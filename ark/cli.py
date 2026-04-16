"""ark CLI."""

from __future__ import annotations

import asyncio
import importlib

import typer
from rich.console import Console
from rich.table import Table

from ark.models import IntegrityReport
from ark.pipeline import run

app = typer.Typer(
    name="ark",
    help="scientific integrity tool. catches hallucinated citations and inflated claims.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


@app.command()
def verify_fixture(
    name: str = typer.Argument(help="fixture module name (e.g. flairr_ts)"),
) -> None:
    """run the pipeline on a test fixture.

    loads tests.fixtures.<name>, runs the pipeline, prints the report.
    """
    try:
        module = importlib.import_module(f"tests.fixtures.{name}")
    except ImportError as e:
        console.print(f"[red]fixture not found:[/red] {e}")
        raise typer.Exit(code=1)

    paper = module.PAPER
    expected = getattr(module, "EXPECTED_VERDICTS", {})

    console.print(f"[bold]{paper.title}[/bold]")
    if paper.authors:
        console.print(f"authors: {', '.join(paper.authors[:3])}")
    console.print(f"references: {len(paper.references)}\n")

    with console.status("verifying references..."):
        report = asyncio.run(run(paper))

    _print_report(report, expected)


def _print_report(report: IntegrityReport, expected: dict[int, str] | None = None) -> None:
    expected = expected or {}

    # summary
    counts = report.counts
    console.print("[bold]summary[/bold]")
    for verdict in ["confirmed", "not_found", "metadata_mismatch", "unverifiable", "error"]:
        n = counts.get(verdict, 0)
        if n:
            color = {
                "confirmed": "green",
                "not_found": "red",
                "metadata_mismatch": "yellow",
                "unverifiable": "dim",
                "error": "magenta",
            }.get(verdict, "white")
            console.print(f"  [{color}]{verdict}:[/{color}] {n}")
    console.print()

    # per-ref table
    table = Table(show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("verdict", width=20)
    table.add_column("cited", max_width=35, overflow="fold")
    table.add_column("resolved", max_width=35, overflow="fold")
    table.add_column("notes", max_width=30, overflow="fold")
    if expected:
        table.add_column("expected", width=12)

    for i, v in enumerate(report.verdicts):
        verdict_color = {
            "confirmed": "green",
            "not_found": "red",
            "metadata_mismatch": "yellow",
            "unverifiable": "dim",
            "error": "magenta",
        }.get(v.verdict, "white")

        cited = _fmt_side(
            v.reference.title,
            v.reference.authors,
            v.reference.year,
            v.reference.arxiv_id,
        )
        resolved = _fmt_side(
            v.resolved_title,
            v.resolved_authors,
            v.resolved_year,
            v.resolved_arxiv_id,
        )

        row = [
            str(i + 1),
            f"[{verdict_color}]{v.verdict}[/{verdict_color}]",
            cited,
            resolved,
            v.notes or "[dim]—[/dim]",
        ]

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

    # pass/fail summary against expectations
    if expected:
        hits = sum(1 for i, v in enumerate(report.verdicts) if expected.get(i) == v.verdict)
        total = len(expected)
        status = "[green]PASS[/green]" if hits == total else "[red]FAIL[/red]"
        console.print(f"\n{status}: {hits}/{total} expectations met")


def _fmt_side(title: str | None, authors: list[str], year: int | None, arxiv_id: str | None) -> str:
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


def main():
    app()


if __name__ == "__main__":
    main()
