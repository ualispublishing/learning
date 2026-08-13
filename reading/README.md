# Graded Reading Curriculum

This directory is the source of truth for a new Arabic, French, and Urdu reading curriculum designed to build comprehension and reading fluency from A1 through C2.

## Core design

The curriculum combines:

- high-comprehensibility graded reading;
- controlled contextual introduction of new vocabulary;
- infer → verify → transfer learning;
- cloze retrieval in new contexts;
- spaced lexical and grammar reinforcement;
- interleaving;
- narrow reading at lower proficiency and broader contextual diversity later;
- timed fluency passages with comprehension gates;
- progressively deeper inference, cohesion, argument, tone, and synthesis tasks.

## Mandatory files

Read these before producing passages:

1. `../docs/READING_PASSAGE_RESEARCH.md` — evidence and design reasoning.
2. `../docs/READING_PASSAGE_STANDARD.md` — mandatory production contract.
3. `ROADMAP.md` — game plan and production phases.
4. `TASKS.md` — actionable checklist.
5. `STATUS.json` — machine-readable current state.
6. `AGENT_HANDOFF.md` — full continuity/handoff instructions.
7. `schema/passage.schema.json` — canonical record shape.

## Target scale

Initial target:

- Arabic: 360 passages;
- French: 360 passages;
- Urdu: 360 passages;
- total: 1,080 passages.

Each language has 60 passages at each CEFR level A1, A2, B1, B2, C1, C2. The count is a production target, not a reason to retain weak material.

## Canonical data layout

```text
reading/
  arabic/
    a1/passages.jsonl
    a2/passages.jsonl
    b1/passages.jsonl
    b2/passages.jsonl
    c1/passages.jsonl
    c2/passages.jsonl
  french/
    ...
  urdu/
    ...
  ledgers/
    arabic_lexical_exposure.jsonl
    french_lexical_exposure.jsonl
    urdu_lexical_exposure.jsonl
  schema/
    passage.schema.json
```

Directories/files are created as production reaches them; do not preload empty passage files unnecessarily.

## Relationship to existing language CSVs

The validated root CSVs remain the initial lexical foundation:

- Arabic: `../arabic_top1000.csv`, `../arabic_top3000.csv`, `../arabic_phrase_bank.csv`;
- French: `../french_top1000.csv`, `../french_top3000.csv`;
- Urdu: `../urdu_top1000.csv`, `../urdu_top3000.csv`.

The continuation `*_top3000.csv` files contain ranks 1001–3000. Combined with the top-1,000 deck, each language has a validated 3,000-item base.

These inventories are **not** assumed to be the complete vocabulary required for C2. C1/C2 production must introduce additional verified contemporary vocabulary and track it in the reading ledgers.

## Reader-facing rendering order

A reader should normally display:

1. title;
2. passage;
3. all questions;
4. answer key only after the learner submits or explicitly reveals it.

The canonical JSONL contains answers for portability, but the UI should not show them before retrieval.

## Current state

This project is in research/specification and calibration setup. See `STATUS.json` for the exact next action.
