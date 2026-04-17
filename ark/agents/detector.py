"""Detector agent. scores claims for rhetorical inflation."""

from __future__ import annotations

import json
import re

from ark.llm.ollama import generate
from ark.models import Claim, InflationScore

SCORE_PROMPT = """you are a scientific integrity reviewer. your job is to score how much a claim's rhetoric exceeds what the evidence supports.

the claim:
"{claim_text}"

this claim appears in the {section} section of a research paper.

rules:
- score from 0.0 (conservative, well-supported) to 1.0 (highly inflated, rhetoric far exceeds evidence).
- explain your score in one sentence. be specific about what is inflated.
- rewrite the claim conservatively (matching only what the text actually demonstrates).
- if you cannot assess the claim, set score to -1 and explain why.
- base your assessment on: does the claim use absolute language ("achieves state-of-the-art") when the evidence is relative? does it generalize beyond what was tested? does it claim novelty without acknowledging prior work?

output format (JSON):
{{
  "score": 0.0 to 1.0,
  "reasoning": "one sentence explaining the score",
  "conservative_rewrite": "the claim rewritten honestly"
}}

output ONLY the JSON. no explanation, no markdown fences."""


async def score_claims(
    claims: list[Claim], model: str = "gemma4:e4b"
) -> list[InflationScore]:
    """score each claim for rhetorical inflation."""
    scores: list[InflationScore] = []

    for claim in claims:
        score = await _score_one(claim, model)
        if score:
            scores.append(score)

    return scores


async def _score_one(claim: Claim, model: str) -> InflationScore | None:
    """score one claim."""
    prompt = SCORE_PROMPT.format(
        claim_text=claim.text,
        section=claim.section or "unknown",
    )

    response = await generate(prompt, model=model, temperature=0.1)
    return _parse_response(response, claim)


def _parse_response(response: str, claim: Claim) -> InflationScore | None:
    """parse Gemma's JSON response into an InflationScore."""
    response = response.strip()
    if response.startswith("```"):
        response = re.sub(r"^```\w*\n?", "", response)
        response = re.sub(r"\n?```$", "", response)
        response = response.strip()

    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return None
        else:
            return None

    if not isinstance(data, dict):
        return None

    score = data.get("score")
    if score is None:
        return None

    return InflationScore(
        claim=claim,
        score=float(score),
        conservative_rewrite=data.get("conservative_rewrite", ""),
        reasoning=data.get("reasoning", ""),
    )
