"""data models for ark."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Reference:
    """a reference cited in a paper."""
    raw: str
    title: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    arxiv_id: str | None = None


@dataclass
class Claim:
    """a claim extracted from a paper."""
    text: str
    section: str = ""  # abstract, intro, methods, results, discussion
    supporting_refs: list[int] = field(default_factory=list)  # indices into references
    claim_type: str = "empirical"  # empirical, methodological, theoretical


@dataclass
class Paper:
    """a paper under review."""
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    abstract: str = ""
    sections: dict[str, str] = field(default_factory=dict)  # e.g. {"introduction": "...", "related_work": "..."}
    claims: list[Claim] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)


@dataclass
class InflationScore:
    """result of scoring one claim for rhetorical inflation."""
    claim: Claim
    score: float  # 0.0 conservative, 1.0 highly inflated
    conservative_rewrite: str
    reasoning: str


@dataclass
class Verdict:
    """result of verifying one citation."""
    reference: Reference
    verdict: str  # confirmed, not_found, metadata_mismatch, unverifiable, error
    depth_reached: str = "none"  # none, existence, metadata, context, content
    resolved_title: str | None = None
    resolved_authors: list[str] = field(default_factory=list)
    resolved_year: int | None = None
    resolved_doi: str | None = None
    resolved_arxiv_id: str | None = None
    title_similarity: float | None = None
    author_overlap: float | None = None
    notes: str = ""


@dataclass
class IntegrityReport:
    """structured output for a paper."""
    paper: Paper
    verdicts: list[Verdict]
    claims: list[Claim] = field(default_factory=list)
    inflation_scores: list[InflationScore] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for v in self.verdicts:
            result[v.verdict] = result.get(v.verdict, 0) + 1
        return result
