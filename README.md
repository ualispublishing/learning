# Learning

A structured self-study repository for finished learning datasets, active study tracks, source-curated playlists, flashcards, progress state, and the verification tooling behind them.

The repository is organized so a visitor can quickly distinguish **finished/public-ready material**, **work still being learned**, and **development or audit history**.

## Repository map

| Area | Status | Purpose |
|---|---|---|
| [`completed/`](completed/) | Finished | Human-readable index of completed/public-ready learning assets. |
| Root language CSVs | Finished | Canonical publication-ready Arabic, French, and Urdu datasets. |
| [`in-progress/`](in-progress/) | In progress | Human-readable index of active and paused learning tracks. |
| [`subjects/`](subjects/) | Active learning state | Canonical study systems and flashcards for tracked subjects. |
| [`playlists/`](playlists/) | Active curriculum | Ordered audio/video learning paths. |
| [`progress/`](progress/) | Active state | Machine-readable progress plus the human-readable next lesson. |
| [`sources/`](sources/) | Reference | Curated source metadata used by learning tracks. |
| [`docs/`](docs/) | Standards | Learning protocols, flashcard standards, and repository guidance. |
| [`audit/`](audit/) | Verification only | Quality-control evidence, candidates, review queues, source extractions, and attestations. **Not learner material.** |
| [`archive/`](archive/) | Historical | Superseded decks, quarantined content, paused material, and obsolete development iterations. **Not current learner material.** |
| [`scripts/`](scripts/) + [`.github/workflows/`](.github/workflows/) | Tooling | Active rebuild, audit, and maintenance automation. |

## CISSP Atlas

The current CISSP study system is [`subjects/cissp/2024-outline/study-site/`](subjects/cissp/2024-outline/study-site/). Start with [`TOMORROW_START.md`](subjects/cissp/2024-outline/study-site/TOMORROW_START.md) or the site's 16-question diagnostic rather than reading the repository files sequentially.

**CISSP Atlas v1.2 release scope:** 8 domains, all 62 numbered public objectives, 344 mapped subtopic checks, 33 current AI-security coverage areas, 140 layered retrieval cards, 56 original scenario questions, and 20 primary/reference sources. The machine-readable state is [`RELEASE_STATUS.json`](subjects/cissp/2024-outline/study-site/RELEASE_STATUS.json), and the semantic audit is [`PRECISION_AUDIT.md`](subjects/cissp/2024-outline/study-site/PRECISION_AUDIT.md).

The site is unofficial and independent of ISC2. Its release status means the public-outline mapping, study workflow, and internal consistency have been audited; it does not claim that memorization guarantees a CISSP pass or reproduces the live exam bank.

## Finished language datasets

The canonical learner-facing CSVs remain at the repository root so their existing verification and maintenance tooling stays stable. They are indexed under [`completed/languages/`](completed/languages/).

**Language workbooks:** the Arabic, French, and Urdu LANG-WB v1.0 master PDFs, split PDFs, 1,000-word companion CSVs, 1,000-sentence companion CSVs, release manifest, QA evidence, and curation records are indexed from [`completed/languages/workbooks/v1.0/`](completed/languages/workbooks/v1.0/).

- **Arabic:** `arabic_top1000.csv`, `arabic_top3000.csv`, and `arabic_phrase_bank.csv`.
- **French:** `french_top1000.csv` and `french_top3000.csv`.
- **Urdu:** `urdu_top1000.csv` and `urdu_top3000.csv`.

The `*_top3000.csv` files are the **ranks 1001–3000 continuation** (2,000 rows), not duplicate copies of ranks 1–3000.

These finished datasets are standalone reference/study assets. Their existence does **not** imply that the same material has been mastered in the active spaced-review course.

## Current learning state

See [`in-progress/README.md`](in-progress/README.md) for the human-readable overview. The exact machine-readable state is [`progress/current.json`](progress/current.json), and the next lesson is [`progress/NEXT.md`](progress/NEXT.md).

The active language track is currently the restarted **Arabic MSA audio-first path**. MATS / Efficient Engineer is preserved as a paused track. CISSP Atlas is independently routed through `PROJECT_TRACKS.json` as `CISSP-ATLAS`.

## Quality status

The finished language datasets have passed the repository's publication-readiness and live-integrity checks. The main high-level evidence is:

- [`audit/public_readiness_audit.json`](audit/public_readiness_audit.json)
- [`audit/live_csv_attestation.json`](audit/live_csv_attestation.json)

Audit candidates, rejection files, historical review queues, and archived CSVs are intentionally retained for provenance and should not be presented as finished learning material.
