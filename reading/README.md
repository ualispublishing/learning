# Graded Reading Curriculum

This directory is the source of truth for the Arabic, French, and Urdu A1–C2 graded-reading curriculum.

## Current operating state

As of 2026-08-16:

- Arabic A1–C2 generation is complete: 360 canonical passages, 60 per CEFR level.
- Arabic is in the closing final multi-pass review phase.
- French and Urdu are paused until Arabic final review closes.
- Arabic final approval remains false until a fresh Pass 12 adversarial gate succeeds.

Do not restart Arabic calibration or generation from older checklist text.

## Read order

For current work, read:

1. `STATUS.json` — exact current state and next actions.
2. `AGENT_HANDOFF.md` — concise continuity rules.
3. `planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md` — batching, artifact freshness, concurrency, and final-gate rules.
4. `planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md` — current workflow-order policy.
5. `planning/TEN_QUESTION_STANDARD.md` — active ten-question contract.
6. `schema/passage.schema.json` — authoritative canonical schema and question-type enum.
7. `../docs/READING_PASSAGE_STANDARD.md` — durable passage-quality contract.
8. `ROADMAP.md` — curriculum architecture.
9. `TASKS.md` — active operational queue.

### Precedence for conflicts

Use:

**live canonical JSONL > fresh audit artifacts > STATUS > current final-review policy/protocol > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

Later generation-first/final-review policy changes the order of operations, not the underlying quality criteria.

## Core design

The curriculum combines:

- graded reading with level-appropriate support;
- contextual vocabulary introduction;
- infer → verify → transfer learning;
- cloze and retrieval in new contexts;
- spaced lexical and grammar reinforcement;
- interleaving;
- narrow reading at lower proficiency and broader contextual diversity later;
- timed fluency passages with comprehension gates;
- progressively deeper inference, cohesion, argument, tone, register, and synthesis tasks.

## Target scale

Initial project target:

- Arabic: 360 passages;
- French: 360 passages;
- Urdu: 360 passages;
- total: 1,080 passages.

Each language uses 60 passages at each CEFR level A1, A2, B1, B2, C1, C2. Counts are production targets, not permission to retain weak material.

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
    ...
  audit/
    ...
  schema/
    passage.schema.json
```

Canonical data is JSONL. App-specific JSON/CSV/text exports are derived outputs.

## Existing language inventories

Validated root CSVs are lexical foundations, not CEFR labels:

- Arabic: `../arabic_top1000.csv`, `../arabic_top3000.csv`, `../arabic_phrase_bank.csv`;
- French: `../french_top1000.csv`, `../french_top3000.csv`;
- Urdu: `../urdu_top1000.csv`, `../urdu_top3000.csv`.

Do not mutate validated root CSVs merely to simplify reading-corpus work. Build derived ledgers/overrides instead. The 3,000-item base is not a complete C2 lexicon.

## Question and rendering contract

Current canonical passages use 10 questions with 10 linked answers under `planning/TEN_QUESTION_STANDARD.md`.

Reader-facing order is:

1. title;
2. passage;
3. all questions;
4. answers only after submission/reveal.

The schema is authoritative for allowed question type names. Some older prose standards predate the expanded ten-question taxonomy; where they conflict, use the Ten-Question Standard and schema.

## Arabic coverage note

Current Arabic `estimated_known_token_coverage` zeros are unmeasured placeholders. They are not measured 0% results. Pass 07 records the current state as `UNMEASURED_NOT_FAILURE` and has zero actionable CEFR/length flags.

Do not fabricate coverage percentages merely to make an audit green.

## Final-review execution

Use large guarded batches rather than passage-by-passage workflow churn. Rerun only audits affected by the fields changed; regenerate the full final gate suite once at final approval. See `planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md`.
