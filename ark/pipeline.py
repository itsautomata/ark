"""pipeline orchestration. layer 0: verifier. layer 1: + scholar + detector."""

from __future__ import annotations

from ark.agents.verifier import verify
from ark.llm.ollama import is_available
from ark.models import IntegrityReport, Paper


async def run(paper: Paper) -> IntegrityReport:
    """run the full pipeline on a paper.

    layer 0: verifier only (always runs).
    layer 1: scholar + detector (runs if Ollama is available and paper has text).
    """
    # layer 0: verify citations
    verdicts = await verify(paper.references)

    claims = []
    inflation_scores = []

    # layer 1: extract claims + score inflation (if we have text and a model)
    has_text = bool(paper.abstract or paper.sections)
    gemma_available = await is_available()

    if has_text and gemma_available:
        from ark.agents.scholar import extract_claims
        from ark.agents.detector import score_claims

        claims = await extract_claims(paper)
        if claims:
            inflation_scores = await score_claims(claims)

    return IntegrityReport(
        paper=paper,
        verdicts=verdicts,
        claims=claims,
        inflation_scores=inflation_scores,
    )
