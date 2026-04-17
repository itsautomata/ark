"""Scholar agent. extracts verifiable claims from paper text."""

from __future__ import annotations

import json
import re

from ark.llm.ollama import generate
from ark.models import Claim, Paper

EXTRACT_PROMPT = """you are a scientific claim extractor. your job is to find every verifiable claim in the given text.

rules:
- only extract claims that are ACTUALLY in the text. do not invent claims.
- quote the exact sentence or phrase from the text for each claim.
- a claim is a statement that asserts something is true and could be checked against evidence.
- classify each claim as: "attribution" (paper X shows Y), "result" (we achieve Z), or "scope" (LLMs can do W).
- if a claim references specific authors or citations (e.g. "Zhou et al.", "[14]"), note them.
- if you are unsure whether something is a claim, skip it.
- do NOT extract definitions, background everyone agrees on, or hedged opinions ("future work might...").

output format (JSON array):
[
  {{
    "quote": "the exact sentence from the text",
    "claim_type": "attribution" or "result" or "scope",
    "cited_authors": ["author names mentioned"] or [],
    "section": "abstract" or "introduction" or "related_work"
  }}
]

output ONLY the JSON array. no explanation, no markdown fences.

text to analyze:
---
{text}
---"""


async def extract_claims(paper: Paper, model: str = "gemma4:e4b") -> list[Claim]:
    """extract claims from paper abstract and available sections."""
    all_claims: list[Claim] = []

    # extract from abstract
    if paper.abstract:
        claims = await _extract_from_section(paper.abstract, "abstract", model)
        all_claims.extend(claims)

    # extract from available sections
    for section_name, section_text in paper.sections.items():
        if section_text:
            claims = await _extract_from_section(section_text, section_name, model)
            all_claims.extend(claims)

    # link claims to references by matching cited author names
    _link_claims_to_references(all_claims, paper)

    return all_claims


async def _extract_from_section(
    text: str, section: str, model: str
) -> list[Claim]:
    """extract claims from one section of text."""
    prompt = EXTRACT_PROMPT.format(text=text)
    response = await generate(prompt, model=model, temperature=0.1)

    return _parse_response(response, section)


def _parse_response(response: str, section: str) -> list[Claim]:
    """parse Gemma's JSON response into Claim objects."""
    # strip markdown fences if present
    response = response.strip()
    if response.startswith("```"):
        response = re.sub(r"^```\w*\n?", "", response)
        response = re.sub(r"\n?```$", "", response)
        response = response.strip()

    try:
        items = json.loads(response)
    except json.JSONDecodeError:
        # try to find a JSON array in the response
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            try:
                items = json.loads(match.group())
            except json.JSONDecodeError:
                return []
        else:
            return []

    if not isinstance(items, list):
        return []

    claims = []
    for item in items:
        if not isinstance(item, dict):
            continue
        quote = item.get("quote", "")
        if not quote:
            continue
        claims.append(Claim(
            text=quote,
            section=section,
            claim_type=item.get("claim_type", "scope"),
        ))

    return claims


def _link_claims_to_references(claims: list[Claim], paper: Paper) -> None:
    """link claims to references by matching author surnames in the claim text."""
    for claim in claims:
        text_lower = claim.text.lower()
        for i, ref in enumerate(paper.references):
            for author in ref.authors:
                # extract surname (last token longer than 1 char)
                parts = author.lower().split()
                surname = next((p for p in reversed(parts) if len(p) > 1), None)
                if surname and surname in text_lower:
                    if i not in claim.supporting_refs:
                        claim.supporting_refs.append(i)
                    break
