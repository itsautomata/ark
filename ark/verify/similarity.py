"""similarity measures for title and author matching."""

from __future__ import annotations

import re


def title_similarity(a: str, b: str) -> float:
    """Jaccard similarity on tokens, lowercased, stopwords kept."""
    if not a or not b:
        return 0.0
    ta = set(_tokenize(a))
    tb = set(_tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def author_overlap(cited: list[str], resolved: list[str]) -> float:
    """fraction of cited surnames present in resolved set. 1.0 if either is empty."""
    if not cited or not resolved:
        return 1.0
    cited_surnames = {_surname(a) for a in cited if _surname(a)}
    resolved_surnames = {_surname(a) for a in resolved if _surname(a)}
    if not cited_surnames or not resolved_surnames:
        return 1.0
    return len(cited_surnames & resolved_surnames) / len(cited_surnames)


def _tokenize(s: str) -> list[str]:
    return [t for t in re.findall(r"\w+", s.lower()) if len(t) > 2]


def _surname(name: str) -> str:
    """extract surname. last token, skip single-letter initials.
    handles 'Lastname, Firstname' and 'Firstname Lastname'.
    """
    if not name:
        return ""
    name = name.strip().lower()

    if "," in name:
        before = name.split(",", 1)[0].strip()
        tokens = re.findall(r"\w+", before)
        if tokens:
            return tokens[-1]

    tokens = re.findall(r"\w+", name)
    if not tokens:
        return ""
    real = [t for t in tokens if len(t) > 1]
    if real:
        return real[-1]
    return tokens[-1]
