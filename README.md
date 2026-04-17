# ark

scientific integrity tool. takes a research paper, tells you what holds up.
catches hallucinated citations, flags inflated claims, finds counter-evidence.
currently using [Gemma 4](https://deepmind.google/models/gemma/gemma-4/) by Google (open source, local-first).

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

three commands. each does one thing.

### `ark ref`: citation verification

checks if cited references actually exist and match their claimed metadata.

1. queries arxiv for canonical metadata
2. compares cited title to resolved title (token similarity)
3. compares cited authors to resolved authors (surname overlap)
4. outputs verdict: `confirmed`, `not_found`, `metadata_mismatch`, or `unverifiable`
5. saves report to `reports/<paper>/ref_report.md`

catches arxiv ID hijacks: when a citation claims arxiv:X is paper P, but arxiv:X actually points to something unrelated.

### `ark claim`: claim extraction

extracts verifiable claims from paper text using Gemma (local LLM).

1. sends abstract (and available sections) to Gemma
2. extracts each claim with its type (attribution, result, scope), section, and linked references
3. saves to `reports/<paper>/claims.md` (user-editable)

the user reviews claims.md, corrects types, edits text, or removes bad extractions by setting `keep: no`. edits are the source of truth for inflation scoring.

### `ark inflate`: inflation scoring

scores each claim for rhetorical inflation using Gemma.

1. reads claims from `reports/<paper>/claims.md` (user-reviewed) or extracts fresh
2. scores each claim from 0.0 (conservative) to 1.0 (highly inflated)
3. provides reasoning and a conservative rewrite for each claim
4. saves to `reports/<paper>/inflation_report.md`

---

## install

two options. pick whichever fits your setup.

### option A: Docker (nothing else needed)

requires only [Docker](https://docs.docker.com/get-docker/).

```bash
git clone <repo-url> ark && cd ark
./ark_docker setup              # builds image, starts ollama, pulls gemma4
./ark_docker ref flairr_ts      # run
./ark_docker status             # check if running
./ark_docker down               # stop when done
```

everything runs inside containers. no local dependencies.

### option B: local install

requires python 3.12+, [uv](https://docs.astral.sh/uv/), and [Ollama](https://ollama.com/).

```bash
git clone <repo-url> ark && cd ark
uv sync --python 3.12
ollama pull gemma4:e4b
```

install globally so `ark` works from anywhere:

```bash
uv tool install -e .
```

after code changes, reinstall:

```bash
uv tool install -e . --reinstall
```

### remote GPU (optional)

if your machine lacks RAM for Gemma, run Ollama on a remote server:

```bash
# on the server
ollama serve && ollama pull gemma4:e4b

# on your machine
export OLLAMA_HOST=http://server-ip:11434
ark claim flairr_ts    # runs locally, Gemma runs remotely
```

---

## run

all examples below use `ark` (local install). for Docker, replace `ark` with `./ark_docker`.

### check citations

```bash
ark ref flairr_ts
```

uses the included FLAIRR-TS fixture, a real EMNLP 2025 paper with a documented hallucinated citation (source: [HalluCitation Matters](https://arxiv.org/abs/2601.18724)).

expected: 18 references scanned, 9 confirmed, 4 `metadata_mismatch` (including the documented TEMPO fake), 5 `unverifiable` (no arxiv ID).

### extract claims

```bash
ark claim flairr_ts
```

extracts claims from the paper's abstract. saves to `reports/flairr_ts/claims.md`. open the file, review, edit, then run inflation scoring.

### score inflation

```bash
ark inflate flairr_ts
```

reads your reviewed claims from `claims.md` and scores each one. saves to `reports/flairr_ts/inflation_report.md`.

---

## the workflow

```
ark ref flairr_ts          → reports/flairr_ts/ref_report.md
ark claim flairr_ts        → reports/flairr_ts/claims.md (editable)
  user reviews claims.md
ark inflate flairr_ts      → reports/flairr_ts/inflation_report.md
```

`ark ref` works standalone (no LLM needed). `ark claim` and `ark inflate` need Ollama running with Gemma.

re-running a command prompts before overwriting existing reports.

---

## adding a paper

papers are defined as python fixtures. each fixture declares a `Paper` with its text and references.

```python
from ark.models import Paper, Reference

PAPER = Paper(
    title="your paper",
    authors=["author one", "author two"],
    year=2025,
    abstract="the paper's abstract text...",
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
ark ref <name>
ark claim <name>
ark inflate <name>
```

---

## what ark is not

- not an AI detector. ark checks truth, not authorship.
- not a replacement for peer review. ark surfaces signals, you decide.
- not a tool for paywalled content (yet). ark verifies existence for 100%, verifies content for ~50%, and reports the gap honestly.

---

## status

layer 0 (citation verification): working. confirmed catch on documented hallucinations.
layer 1 (claim extraction + inflation scoring): working. Gemma e4b extracts claims and scores inflation with reasoning and conservative rewrites.
