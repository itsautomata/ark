"""pipeline orchestration. layer 0: Verifier only."""

from __future__ import annotations

from ark.agents.verifier import verify
from ark.models import IntegrityReport, Paper


async def run(paper: Paper) -> IntegrityReport:
    """run the full pipeline on a paper. layer 0: verifier only."""
    verdicts = await verify(paper.references)
    return IntegrityReport(paper=paper, verdicts=verdicts)
