# ark

scientific integrity tool. takes a research paper, tells you what holds up.
catches hallucinated citations, flags inflated claims, finds counter-evidence.
runs on open models, local-first.

---

## the problem

LLMs are reshaping how research is written. two failure modes are surfacing at scale:

| failure | how bad |
|---|---|
| citations that do not exist or misrepresent their source | 17% phantom rate in AI survey papers ([Ilter 2026](https://arxiv.org/abs/2601.17431)), 39% error rate in biomedicine ([Sarol et al. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11231046/)) |
| LLM-inflated rhetoric rewarded over substance | rhetorical intensity predicts citations, not quality ([Qiu et al. 2025](https://arxiv.org/abs/2512.19908)) |

AI detectors are not the answer. they have a big false positive rate. and the problem is not who wrote it. the problem is whether it is true.

---

## what ark does

ark does not detect AI. it checks integrity: the claims, the citations, the evidence.

it produces a report on two things:

**A. citation hallucination.** does this reference exist? does it match its claimed metadata? does it say what the paper claims it does? binary, verifiable.

**B. rhetorical inflation.** is the claim stronger than the evidence supports? continuous, measurable.

---

## how it works

built in layers. each layer is independently demoable.

### layer 0 (current): citation verification

takes a paper (for now, a python fixture structured as claims + references).
1. queries arxiv for canonical metadata
2. compares cited title to resolved title (token similarity)
3. compares cited authors to resolved authors (surname overlap)
4. outputs verdict: `confirmed`, `not_found`, `metadata_mismatch`, or `unverifiable`

catches arxiv ID hijacks (the most common hallucination pattern): when a citation claims arxiv:X is paper P, but arxiv:X actually points to something unrelated.

---

## install

requires python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --python 3.12
```

install globally so `ark` works from anywhere:

```bash
uv tool install -e .
```

---

## run

the included fixture is FLAIRR-TS, a real EMNLP 2025 paper with a documented hallucinated citation (source: [HalluCitation Matters](https://arxiv.org/abs/2601.18724)).

```bash
uv run ark flairr_ts
```

or globally:

```bash
ark flairr_ts
```

expected output: 18 references scanned, 9 confirmed, 4 `metadata_mismatch` (including the documented TEMPO fake), 5 `unverifiable` (no arxiv ID). `PASS: 1/1 expectations met`.

---

## adding a paper

before PDF fetching and parsing are wired in, papers are defined directly as python fixtures. each fixture declares a `Paper` with its references and optional `EXPECTED_VERDICTS` for validation.

```python
from ark.models import Paper, Reference

PAPER = Paper(
    title="your paper",
    authors=["author one", "author two"],
    year=2025,
    references=[
        Reference(
            raw="full citation text",
            title="cited title",
            authors=["cited author"],
            year=2024,
            arxiv_id="2401.12345",
        ),
    ],
)

EXPECTED_VERDICTS = {
    0: "metadata_mismatch",  # if you know this citation is fake
}
```

save as `tests/fixtures/<name>.py` and run:

```bash
uv run ark <name>
```

---

## what ark is not

- not an AI detector. AI detection has a 61% false positive rate on non-native English. ark checks truth, not authorship.
- not a replacement for peer review. ark is a microscope, not a judge. LLM-as-judge agrees with human experts 60-68% of the time. ark surfaces signals, you decide.
- not a tool for paywalled content (yet). ~50% of papers are gated. ark verifies existence for 100%, verifies content for ~50%, and reports the gap honestly.

---

## status

layer 0 working. confirmed catch on documented hallucinations and fake demo data.