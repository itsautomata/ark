"""ark CLI."""

from __future__ import annotations

import asyncio
import importlib
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

# gold palette
import typer.rich_utils as _ru
_ru.STYLE_OPTION = "bold #D4A017"
_ru.STYLE_SWITCH = "#CD853F"
_ru.STYLE_METAVAR = "#C9A96E"
_ru.STYLE_USAGE = "#D4A017"
_ru.STYLE_USAGE_COMMAND = "bold #D4A017"
_ru.STYLE_COMMANDS_TABLE_FIRST_COLUMN = "bold #D4A017"
_ru.STYLE_COMMANDS_PANEL_BORDER = "#8B6914"
_ru.STYLE_OPTIONS_PANEL_BORDER = "#8B6914"
_ru.STYLE_ERRORS_PANEL_BORDER = "#CD5C5C"

REPORTS_DIR = Path(__file__).parent.parent / "reports"

BANNER = """[#D4A017]
 _______  _______  _
(  ___  )(  ____ )| \\    /\\
| (   ) || (    )||  \\  / /
| (___) || (____)||  (_/ /
|  ___  ||     __)|   _ (
| (   ) || (\\ (   |  ( \\ \\
| )   ( || ) \\ \\__|  /  \\ \\
|/     \\||/   \\__/|_/    \\/
[/#D4A017]
[#C9A96E]scientific integrity tool[/#C9A96E]
"""

app = typer.Typer(
    name="ark",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """scientific integrity tool. catches hallucinated citations and inflated claims."""
    if ctx.invoked_subcommand is None:
        console.print(BANNER)
        console.print(ctx.get_help())
        raise typer.Exit()


def _load_fixture(name: str):
    try:
        return importlib.import_module(f"tests.fixtures.{name}")
    except ImportError as e:
        console.print(f"[red]fixture not found:[/red] {e}")
        raise typer.Exit(code=1)


def _run(coro):
    return asyncio.run(coro)


def _report_dir(name: str) -> Path:
    d = REPORTS_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    return d


# --- ark ref ---

@app.command()
def ref(
    name: str = typer.Argument(help="fixture name (e.g. flairr_ts)"),
) -> None:
    """check if citations exist and match their claimed metadata."""
    from ark.agents.verifier import verify

    module = _load_fixture(name)
    paper = module.PAPER
    expected = getattr(module, "EXPECTED_VERDICTS", {})

    console.print(f"[bold]{paper.title}[/bold]")
    console.print(f"references: {len(paper.references)}\n")

    ref_path = _report_dir(name) / "ref_report.md"
    if ref_path.exists():
        overwrite = typer.confirm(f"{ref_path} already exists. overwrite?", default=False)
        if not overwrite:
            console.print("[dim]keeping existing ref_report.md[/dim]")
            return

    with console.status("verifying references..."):
        verdicts = _run(verify(paper.references))

    # summary
    counts: dict[str, int] = {}
    for v in verdicts:
        counts[v.verdict] = counts.get(v.verdict, 0) + 1

    console.print("[bold]summary[/bold]")
    for verdict_type in ["confirmed", "not_found", "metadata_mismatch", "unverifiable", "error"]:
        n = counts.get(verdict_type, 0)
        if n:
            color = {"confirmed": "green", "not_found": "red", "metadata_mismatch": "yellow",
                     "unverifiable": "dim", "error": "magenta"}.get(verdict_type, "white")
            console.print(f"  [{color}]{verdict_type}:[/{color}] {n}")
    console.print()

    # table
    table = Table(show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("verdict", width=20)
    table.add_column("cited", max_width=35, overflow="fold")
    table.add_column("resolved", max_width=35, overflow="fold")
    table.add_column("notes", max_width=30, overflow="fold")
    if expected:
        table.add_column("expected", width=12)

    for i, v in enumerate(verdicts):
        color = {"confirmed": "green", "not_found": "red", "metadata_mismatch": "yellow",
                 "unverifiable": "dim", "error": "magenta"}.get(v.verdict, "white")

        cited = _fmt_ref(v.reference.title, v.reference.authors, v.reference.year, v.reference.arxiv_id)
        resolved = _fmt_ref(v.resolved_title, v.resolved_authors, v.resolved_year, v.resolved_arxiv_id)

        row = [str(i + 1), f"[{color}]{v.verdict}[/{color}]", cited, resolved, v.notes or "[dim]—[/dim]"]

        if expected:
            exp = expected.get(i)
            if exp is None:
                row.append("[dim]—[/dim]")
            elif exp == v.verdict:
                row.append(f"[green]✓ {exp}[/green]")
            else:
                row.append(f"[red]✗ {exp}[/red]")

        table.add_row(*row)

    console.print(table)

    if expected:
        hits = sum(1 for i, v in enumerate(verdicts) if expected.get(i) == v.verdict)
        total = len(expected)
        status = "[green]PASS[/green]" if hits == total else "[red]FAIL[/red]"
        console.print(f"\n{status}: {hits}/{total} expectations met")

    # save ref_report.md
    report_path = _report_dir(name) / "ref_report.md"
    lines = [f"# ref report: {paper.title}\n"]
    lines.append(f"references: {len(verdicts)}\n")
    for vtype in ["confirmed", "not_found", "metadata_mismatch", "unverifiable", "error"]:
        n = counts.get(vtype, 0)
        if n:
            lines.append(f"- {vtype}: {n}")
    lines.append("\n---\n")
    for i, v in enumerate(verdicts):
        lines.append(f"## {i + 1}. [{v.verdict}]")
        lines.append(f"cited: {v.reference.title or v.reference.raw[:80]}")
        if v.reference.authors:
            lines.append(f"authors: {', '.join(v.reference.authors)}")
        if v.reference.arxiv_id:
            lines.append(f"arxiv: {v.reference.arxiv_id}")
        if v.resolved_title:
            lines.append(f"resolved: {v.resolved_title}")
        if v.resolved_authors:
            lines.append(f"resolved authors: {', '.join(v.resolved_authors)}")
        if v.notes:
            lines.append(f"notes: {v.notes}")
        lines.append("")

    report_path.write_text("\n".join(lines))
    console.print(f"\nsaved to {report_path}")


# --- ark claim ---

@app.command()
def claim(
    name: str = typer.Argument(help="fixture name (e.g. flairr_ts)"),
    model: str = typer.Option("gemma4:e4b", "-m", help="Ollama model to use"),
) -> None:
    """extract verifiable claims from paper text."""
    from ark.agents.scholar import extract_claims

    module = _load_fixture(name)
    paper = module.PAPER

    if not paper.abstract and not paper.sections:
        console.print("[yellow]no text available. add abstract or sections to the fixture.[/yellow]")
        raise typer.Exit(code=1)

    console.print(f"[bold]{paper.title}[/bold]")
    text_sources = []
    if paper.abstract:
        text_sources.append("abstract")
    text_sources.extend(paper.sections.keys())
    console.print(f"text: {', '.join(text_sources)}\n")

    claims_path = _report_dir(name) / "claims.md"
    if claims_path.exists():
        overwrite = typer.confirm(f"{claims_path} already exists. overwrite?", default=False)
        if not overwrite:
            console.print("[dim]keeping existing claims.md[/dim]")
            return

    with console.status("extracting claims via Gemma..."):
        claims = _run(extract_claims(paper, model=model))

    if not claims:
        console.print("[yellow]no claims extracted.[/yellow]")
        return

    console.print(f"[bold]{len(claims)} claims extracted[/bold]\n")

    table = Table(show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("type", width=14)
    table.add_column("claim", max_width=55, overflow="fold")
    table.add_column("refs", width=8)
    table.add_column("section", width=14)

    for i, c in enumerate(claims):
        refs = ", ".join(str(r) for r in c.supporting_refs) if c.supporting_refs else "[dim]—[/dim]"
        table.add_row(str(i + 1), c.claim_type, c.text, refs, c.section)

    console.print(table)

    # save claims.md (user-editable)
    claims_path = _report_dir(name) / "claims.md"
    lines = [f"# claims: {paper.title}\n"]
    lines.append(f"extracted: {len(claims)} claims")
    lines.append("edit this file to correct, remove, or reclassify claims before running `ark inflate`.\n")
    lines.append("---\n")
    for i, c in enumerate(claims):
        refs = ", ".join(str(r) for r in c.supporting_refs) if c.supporting_refs else "none"
        lines.append(f"## {i + 1}.")
        lines.append(f"type: {c.claim_type}")
        lines.append(f"claim: {c.text}")
        lines.append(f"section: {c.section}")
        lines.append(f"refs: {refs}")
        lines.append(f"keep: yes")
        lines.append("")

    claims_path.write_text("\n".join(lines))
    console.print(f"\nsaved to [bold]{claims_path}[/bold]")
    console.print()
    console.print("[dim]next steps:[/dim]")
    console.print(f"[dim]  1. open {claims_path} and review the extracted claims[/dim]")
    console.print("[dim]  2. edit claim text, change types, or set 'keep: no' to remove[/dim]")
    console.print(f"[dim]  3. run 'ark inflate {name}' to score what you approved[/dim]")
    console.print("[dim]  your edits are the source of truth for inflation scoring.[/dim]")


# --- ark inflate ---

@app.command()
def inflate(
    name: str = typer.Argument(help="fixture name (e.g. flairr_ts)"),
    model: str = typer.Option("gemma4:e4b", "-m", help="Ollama model to use"),
) -> None:
    """score claims for rhetorical inflation. reads claims.md if it exists."""
    from ark.agents.detector import score_claims

    claims_path = _report_dir(name) / "claims.md"

    if claims_path.exists():
        # read user-reviewed claims
        claims = _parse_claims_md(claims_path)
        console.print(f"loaded {len(claims)} claims from [bold]{claims_path}[/bold]")
        console.print("[dim]using your edited claims as source of truth.[/dim]\n")
    else:
        # no claims file, extract fresh
        from ark.agents.scholar import extract_claims

        module = _load_fixture(name)
        paper = module.PAPER

        if not paper.abstract and not paper.sections:
            console.print("[yellow]no text available.[/yellow]")
            raise typer.Exit(code=1)

        console.print(f"no claims.md found. extracting fresh...\n")

        with console.status("extracting claims..."):
            claims = _run(extract_claims(paper, model=model))

    if not claims:
        console.print("[yellow]no claims to score.[/yellow]")
        return

    inflate_path = _report_dir(name) / "inflation_report.md"
    if inflate_path.exists():
        overwrite = typer.confirm(f"{inflate_path} already exists. overwrite?", default=False)
        if not overwrite:
            console.print("[dim]keeping existing inflation_report.md[/dim]")
            return

    console.print(f"{len(claims)} claims. scoring inflation...\n")

    with console.status("scoring inflation via Gemma..."):
        scores = _run(score_claims(claims, model=model))

    if not scores:
        console.print("[yellow]no scores produced.[/yellow]")
        return

    table = Table(show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("score", width=6)
    table.add_column("claim", max_width=40, overflow="fold")
    table.add_column("reasoning", max_width=35, overflow="fold")
    table.add_column("conservative rewrite", max_width=35, overflow="fold")

    for i, s in enumerate(scores):
        if s.score < 0:
            score_str = "[dim]n/a[/dim]"
        elif s.score >= 0.7:
            score_str = f"[red]{s.score:.1f}[/red]"
        elif s.score >= 0.4:
            score_str = f"[yellow]{s.score:.1f}[/yellow]"
        else:
            score_str = f"[green]{s.score:.1f}[/green]"

        table.add_row(str(i + 1), score_str, s.claim.text[:80], s.reasoning, s.conservative_rewrite)

    console.print(table)

    # summary
    valid = [s for s in scores if s.score >= 0]
    if valid:
        avg = sum(s.score for s in valid) / len(valid)
        high = sum(1 for s in valid if s.score >= 0.7)
        console.print(f"\naverage inflation: {avg:.2f}")
        if high:
            console.print(f"[red]highly inflated claims: {high}[/red]")

    # save inflation_report.md
    report_path = _report_dir(name) / "inflation_report.md"
    lines = [f"# inflation report: {name}\n"]
    if valid:
        lines.append(f"average inflation: {avg:.2f}")
        lines.append(f"claims scored: {len(valid)}")
        if high:
            lines.append(f"highly inflated (>= 0.7): {high}")
    sections_present = set(c.section for c in claims if c.section)
    lines.append("")
    lines.append(_section_note(sections_present))
    lines.append("\n---\n")
    for i, s in enumerate(scores):
        lines.append(f"## {i + 1}. score: {s.score:.1f}")
        lines.append(f"claim: {s.claim.text}")
        lines.append(f"reasoning: {s.reasoning}")
        lines.append(f"conservative rewrite: {s.conservative_rewrite}")
        lines.append("")

    report_path.write_text("\n".join(lines))
    console.print(f"\nsaved to [bold]{report_path}[/bold]")


# --- helpers ---

SECTION_NOTES = {
    "abstract": "note: abstracts are where authors sell their contribution. moderate inflation is expected and normal.",
    "introduction": "note: introductions frame novelty and motivation. scope claims here tend to be broader than what the results support.",
    "related_work": "note: related work sections attribute claims to other papers. check whether the attributed findings match the cited source.",
}


def _section_note(sections: set[str]) -> str:
    """generate contextual notes based on which sections were analyzed."""
    notes = []
    for s in sorted(sections):
        if s in SECTION_NOTES:
            notes.append(SECTION_NOTES[s])
    if not notes:
        return ""
    return "\n".join(notes)


def _fmt_ref(title: str | None, authors: list[str], year: int | None, arxiv_id: str | None) -> str:
    parts: list[str] = []
    if title:
        parts.append(title)
    else:
        parts.append("[dim]no title[/dim]")
    if authors:
        parts.append(f"[dim]{', '.join(authors)}[/dim]")
    meta: list[str] = []
    if year:
        meta.append(str(year))
    if arxiv_id:
        meta.append(f"[link=https://arxiv.org/abs/{arxiv_id}]arxiv:{arxiv_id}[/link]")
    if meta:
        parts.append(f"[dim]{' · '.join(meta)}[/dim]")
    return "\n".join(parts)


def _parse_claims_md(path: Path) -> list:
    """parse a user-edited claims.md back into Claim objects."""
    import re
    from ark.models import Claim

    text = path.read_text()
    blocks = re.split(r"\n## \d+\.\s+", text)
    claims = []

    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if not lines:
            continue

        fields: dict[str, str] = {}
        for line in lines:
            match = re.match(r"^(type|claim|section|refs|keep):\s*(.*)$", line.strip())
            if match:
                fields[match.group(1)] = match.group(2).strip()

        # skip claims marked as "keep: no"
        if fields.get("keep", "yes").lower() in ("no", "false", "remove", "skip"):
            continue

        claim_text = fields.get("claim", "")
        if not claim_text:
            continue

        refs_str = fields.get("refs", "")
        refs = []
        if refs_str and refs_str != "none":
            for r in refs_str.split(","):
                r = r.strip()
                if r.isdigit():
                    refs.append(int(r))

        claims.append(Claim(
            text=claim_text,
            section=fields.get("section", ""),
            supporting_refs=refs,
            claim_type=fields.get("type", "scope"),
        ))

    return claims


def main():
    app()


if __name__ == "__main__":
    main()
