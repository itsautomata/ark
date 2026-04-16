"""Verifier agent. checks if cited references actually exist and match claimed metadata."""

from __future__ import annotations

import asyncio

import httpx

from ark.models import Reference, Verdict
from ark.verify.arxiv import ArxivError, lookup as arxiv_lookup
from ark.verify.similarity import author_overlap, title_similarity

# arXiv is strict, 1 req per 3 seconds recommended. we do 1 per 3.5 to be safe.
_ARXIV_DELAY = 3.5
_TITLE_SIM_THRESHOLD = 0.85
_AUTHOR_OVERLAP_THRESHOLD = 0.3


async def verify(references: list[Reference]) -> list[Verdict]:
    """verify a list of references. layer 0: arxiv lookup + similarity check."""
    _arxiv_lock = asyncio.Lock()

    async with httpx.AsyncClient(timeout=30.0) as client:
        async def _one(ref: Reference) -> Verdict:
            return await _verify_reference(ref, client, _arxiv_lock)

        return await asyncio.gather(*[_one(r) for r in references])


async def _verify_reference(
    ref: Reference,
    client: httpx.AsyncClient,
    arxiv_lock: asyncio.Lock,
) -> Verdict:
    """verify one reference. layer 0 path: arxiv lookup if arxiv_id present."""
    if not ref.arxiv_id:
        # layer 0 stops here. layers 1+ add Crossref, PubMed, OpenReview, fuzzy search.
        return Verdict(
            reference=ref,
            verdict="unverifiable",
            depth_reached="none",
            notes="no arxiv ID. layer 0 only handles arxiv-cited references.",
        )

    try:
        # serialize arxiv calls, spread by 3.5s each
        async with arxiv_lock:
            match = await arxiv_lookup(ref.arxiv_id, client)
            await asyncio.sleep(_ARXIV_DELAY)
    except ArxivError as e:
        return Verdict(
            reference=ref,
            verdict="error",
            depth_reached="none",
            notes=str(e),
        )
    except httpx.HTTPError as e:
        return Verdict(
            reference=ref,
            verdict="error",
            depth_reached="none",
            notes=f"{type(e).__name__}: {e or 'no message'}",
        )

    if not match:
        return Verdict(
            reference=ref,
            verdict="not_found",
            depth_reached="none",
            notes=f"arxiv ID {ref.arxiv_id} not found",
        )

    # got a match. check metadata.
    sim = title_similarity(ref.title or "", match.title) if ref.title else None
    overlap = author_overlap(ref.authors, match.authors) if ref.authors and match.authors else None

    notes: list[str] = []
    is_mismatch = False

    if sim is not None and sim < _TITLE_SIM_THRESHOLD:
        is_mismatch = True
        notes.append(f"title similarity {sim:.2f}")

    if overlap is not None and overlap < _AUTHOR_OVERLAP_THRESHOLD:
        is_mismatch = True
        notes.append(f"author overlap {overlap:.2f}")

    return Verdict(
        reference=ref,
        verdict="metadata_mismatch" if is_mismatch else "confirmed",
        depth_reached="metadata",
        resolved_title=match.title,
        resolved_authors=match.authors,
        resolved_year=match.year,
        resolved_arxiv_id=match.arxiv_id,
        title_similarity=sim,
        author_overlap=overlap,
        notes="; ".join(notes),
    )
