"""arXiv API client. lookup by ID, get canonical metadata."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx

ARXIV_API = "https://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


@dataclass
class ArxivMatch:
    arxiv_id: str
    title: str
    authors: list[str]
    year: int | None


class ArxivError(Exception):
    pass


async def lookup(arxiv_id: str, client: httpx.AsyncClient) -> ArxivMatch | None:
    """look up an arXiv ID. returns None if not found."""
    resp = await client.get(
        ARXIV_API,
        params={"id_list": arxiv_id, "max_results": 1},
        follow_redirects=True,
    )
    if resp.status_code != 200:
        raise ArxivError(f"arXiv API returned {resp.status_code}")

    return _parse_atom(resp.text, arxiv_id)


def _parse_atom(xml_text: str, requested_id: str) -> ArxivMatch | None:
    root = ET.fromstring(xml_text)
    entries = root.findall(f"{ATOM_NS}entry")
    if not entries:
        return None

    entry = entries[0]

    title_el = entry.find(f"{ATOM_NS}title")
    title = (title_el.text or "").strip() if title_el is not None else ""
    if title.lower() == "error":
        return None

    # canonical id from <id> URL
    id_el = entry.find(f"{ATOM_NS}id")
    canonical_id = requested_id
    if id_el is not None and id_el.text:
        url = id_el.text.strip()
        if "/abs/" in url:
            canonical_id = url.split("/abs/")[-1].split("v")[0]

    authors = []
    for author in entry.findall(f"{ATOM_NS}author"):
        name_el = author.find(f"{ATOM_NS}name")
        if name_el is not None and name_el.text:
            authors.append(name_el.text.strip())

    year: int | None = None
    published = entry.find(f"{ATOM_NS}published")
    if published is not None and published.text and len(published.text) >= 4:
        try:
            year = int(published.text[:4])
        except ValueError:
            pass

    return ArxivMatch(
        arxiv_id=canonical_id,
        title=title,
        authors=authors,
        year=year,
    )
