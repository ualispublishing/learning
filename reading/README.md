# Graded Reading Curriculum — LANG-A1C2

This directory is the source of truth for the Arabic, French, and Urdu A1-C2 graded-reading project.

## Scope

`LANG-A1C2` means the graded-reading curriculum under `reading/` only. It is separate from:

- the language-workbook project under `completed/languages/workbooks/v1.0/`, `audit/language-workbooks/v1.0/`, and `curation/language-workbooks/v1.0/`;
- the separate language-study/progress track under `progress/`.

`reading/AGENT_HANDOFF.md` is legacy history and must not drive current work.

## Start / resume order

1. `CONTINUATION.json` — compact authoritative live resume state and scope guard.
2. Verify the live canonical JSONL for any language/level you will touch.
3. `RELEASE_STATUS.json` — educator/publication readiness only.
4. `STATUS.json` — production counts and frontier only.
5. `AGENT_HANDOFF_V2.md` — human operating contract.
6. `planning/ACTIVE_GENERATION_PLAN.json` — exact current generation target.
7. `TASKS.md` and `VERIFICATION_TASKS.md` — active queues only.
8. `planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md` and `planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md`.
9. `planning/TEN_QUESTION_STANDARD.md` and `schema/passage.schema.json`.
10. durable standards and `ROADMAP.md`.

Truth precedence:

**live canonical JSONL > fresh hash-bound audit evidence > CONTINUATION > RELEASE_STATUS for release claims > STATUS for production state > handoff/active queues > durable policy/schema/roadmap > historical artifacts.**

If those disagree, fail closed and reconcile the live files/evidence first.

## Current operating state — 2026-08-23

Production target: 1,080 passages total, 360 per language, 60 per CEFR level A1-C2.

- **Arabic:** 360/360 generated; A1-C2 generation complete. Educator/publication release is not currently cleared by `RELEASE_STATUS.json`.
- **French:** 360/360 generated; A1-C2 generation complete. Release is `REOPEN_REQUIRED`; the latest post-repair deterministic Gate A remains failed pending substantive evidence revalidation.
- **Urdu:** 60/360 generated; A1 generation complete, A2 is next. The exact A1 integrity audit reports 60 passages, 600 questions, 600 answers, 0 hard errors, and 0 warnings for the pinned corpus, but explicitly does **not** promote quality/release status.
- **Project generated:** 780/1080 passages.

Current production frontier: **Urdu A2, Unit 1, sequence 1**.

Run `python reading/tools/validate_continuation_state.py` before trusting stored counts/frontiers in a fresh session.

## Core architecture

Each language uses 60 passages per CEFR level; each level uses 10 units x 6 passages. The six-passage unit cycle is:

1. introduce;
2. reinforce;
3. interleave;
4. transfer;
5. integrate/checkpoint;
6. fluency/checkpoint.

Canonical data is JSONL at `reading/<language>/<level>/passages.jsonl`. App-specific exports are derived outputs.

Canonical passages use 10 questions with 10 linked answers under `planning/TEN_QUESTION_STANDARD.md` unless a documented pedagogical exception is necessary.

## Production model

Follow `planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md`:

- write natural, high-quality language from the start;
- generate in guarded unit or large bounded batches rather than one workflow per passage;
- fix obvious severe defects immediately;
- defer repeated formal release-audit bookkeeping to designated final review phases;
- keep generation state separate from educator/publication release state.

Arabic, French, and Urdu passages must be independently natural and pedagogically designed rather than translations of one another.

## Verification / release model

Use `planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md`, `planning/EDUCATOR_RELEASE_VERIFICATION_PROTOCOL.md`, and `planning/HIGHEST_ASSURANCE_RELEASE_PROFILE.md` for final verification.

No agent should claim literal 100% correctness. Release claims require fresh evidence bound to the reviewed canonical corpus, with no known unresolved defects under the applicable assurance profile.

## Existing lexical foundations

Validated root CSVs are lexical foundations, not CEFR labels:

- Arabic: `../arabic_top1000.csv`, `../arabic_top3000.csv`, `../arabic_phrase_bank.csv`;
- French: `../french_top1000.csv`, `../french_top3000.csv`;
- Urdu: `../urdu_top1000.csv`, `../urdu_top3000.csv`.

Do not mutate validated root CSVs merely to simplify passage production. Use derived ledgers/overrides where necessary. Frequency rank is not itself a CEFR label.

## Handoff hygiene

Live state files must remain compact. Do not append dated historical timelines or multiple contradictory `IMMEDIATE NEXT` sections. Completed work belongs in Git history and `reading/audit/`; live files should preserve only verified current state, blockers, and exact next actions.
