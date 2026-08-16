# Graded Reading Curriculum

This directory is the source of truth for the Arabic, French, and Urdu A1–C2 graded-reading curriculum.

## Current operating state — 2026-08-16

- **Arabic:** 360/360 passages, formally approved after fresh Pass 12.
- **French:** active; 6 A1 calibration passages exist, 354 passages remain across A1–C2.
- **Urdu:** queued; 6 A1 calibration passages exist, 354 passages remain across A1–C2.

Do not restart Arabic review or French/Urdu calibration from old checklist text. Read `STATUS.json` and `AGENT_HANDOFF.md` first.

## Read order

1. `STATUS.json` — current language, counts, and next action.
2. `AGENT_HANDOFF.md` — concise continuity/throughput rules.
3. `planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md` — production order.
4. `planning/TEN_QUESTION_STANDARD.md` — ten-question contract.
5. `schema/passage.schema.json` — authoritative schema/type enum.
6. `../docs/READING_PASSAGE_STANDARD.md` — durable quality standard.
7. `ROADMAP.md` — curriculum architecture.
8. `TASKS.md` — active operational queue.
9. `planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md` — final-audit batching/freshness rules.

Current-state precedence:

**live canonical JSONL > fresh audit artifacts > STATUS > current handoff/policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## Target scale

- Arabic: 360 passages — **complete/approved**.
- French: 360 passages — 6 currently exist.
- Urdu: 360 passages — 6 currently exist.
- total target: 1,080 passages.

Each language uses 60 passages at each CEFR level A1–C2; each level uses 10 units × 6 passages.

## Core design

The curriculum combines graded reading, contextual vocabulary growth, infer → verify → transfer learning, spaced reinforcement, interleaving, grammar automaticity, fluency with comprehension gates, and progressively deeper inference/discourse/synthesis.

Canonical data is JSONL at `reading/<language>/<level>/passages.jsonl`. App-specific exports are derived outputs.

## Existing lexical inventories

Validated root CSVs are lexical foundations, not CEFR labels:

- Arabic: `../arabic_top1000.csv`, `../arabic_top3000.csv`, `../arabic_phrase_bank.csv`;
- French: `../french_top1000.csv`, `../french_top3000.csv`;
- Urdu: `../urdu_top1000.csv`, `../urdu_top3000.csv`.

Do not mutate validated root CSVs merely to simplify passage production. Build derived ledgers/overrides where necessary. Frequency rank is not a CEFR label, and a 3,000-item base is not a complete C2 lexicon.

## Question / rendering contract

Canonical passages use 10 questions with 10 linked answers under `planning/TEN_QUESTION_STANDARD.md`.

Reader-facing order:

1. title;
2. passage;
3. all questions;
4. answers only after submission/reveal.

The schema is authoritative for allowed question type names. Older prose standards that predate the expanded ten-question taxonomy are historical where they conflict with the active Ten-Question Standard/schema.

## Production throughput

During generation, use **large guarded unit/batch scopes**, not one workflow per passage. Rerun only structural/source/linkage checks affected by the write. Reserve the full expensive multi-pass final review for the completed generated corpus.

At final review, use `planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md`: sequential fresh audit evidence, explicit adjudication where heuristics surface candidates, and Pass 12 last.

## Arabic final evidence

Arabic Pass 12 directly revalidated 360 unique passages, valid level sequences, word bands, stored word counts, question-answer linkage, local question-target declarations, Arabic-script reader content, and P6 zero-new-target policy, with zero hard regressions and zero approval blockers.

Final artifact:
`audit/final_arabic_pass12_adversarial_gate_falsification.json`

Arabic coverage remains unmeasured; existing zeros are placeholders and were not fabricated into a percentage for approval.

## Immediate production frontier

Continue **French A1 from sequence 7**, preserving the six existing calibration passages. French content must be independently natural and pedagogically designed; do not translate the Arabic corpus passage-by-passage.
