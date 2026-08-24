# Graded Reading Curriculum — LANG-A1C2

This directory is the source of truth for the Arabic, French, and Urdu A1-C2 graded-reading project.

## Scope

`LANG-A1C2` means the graded-reading curriculum under `reading/` only. It is separate from:

- the language-workbook project under `completed/languages/workbooks/v1.0/`, `audit/language-workbooks/v1.0/`, and `curation/language-workbooks/v1.0/`;
- the separate language-study/progress track under `progress/`.

`reading/AGENT_HANDOFF.md` is legacy history and must not drive current work.

## Start / resume order

1. `../PROJECT_TRACKS.json` — route `LANG-A1C2` vs `LANG-WB` before reading project state.
2. `AGENTS.md` — scoped fail-closed agent rules for this project.
3. `CONTINUATION.json` — compact live resume state and scope guard.
4. `STATE_MANIFEST.json` — exact-byte lock for the live continuation/status/handoff bundle.
5. Verify the live canonical JSONL for any language/level you will touch.
6. `RELEASE_STATUS.json` — educator/publication release evidence and decisions only.
7. `STATUS.json` — live production counts and frontier only.
8. `planning/ACTIVE_GENERATION_PLAN.json` — exact current generation target.
9. `AGENT_HANDOFF_V2.md` — human operating contract.
10. `TASKS.md` and `VERIFICATION_TASKS.md` — active queues only.
11. durable policies, standards, schema, and `ROADMAP.md` as needed.

## Authority is domain-specific

Do not use one global precedence list for every kind of fact:

- **Project routing/scope:** `PROJECT_TRACKS.json`, `reading/AGENTS.md`, and `CONTINUATION.json` must agree.
- **State-bundle integrity:** `STATE_MANIFEST.json` pins the exact tracked live-state bytes plus an aggregate SHA-256; tracked-file drift means the handoff bundle must be refreshed/reconciled.
- **Production facts:** live canonical JSONL is ground truth. `STATUS.json` and `CONTINUATION.json` must match it; mismatch is a stop condition.
- **Release readiness:** fresh hash-bound evidence can invalidate a release claim. `RELEASE_STATUS.json` is the authoritative affirmative educator/publication decision; stale or conflicting evidence means fail closed, not infer readiness.
- **Active generation frontier:** `CONTINUATION.json`, `STATUS.json`, and `ACTIVE_GENERATION_PLAN.json` must agree.
- **Durable rules:** policies/schema/roadmap constrain work but do not override a newer verified live frontier.
- **History:** Git history, `reading/audit/`, the legacy handoff, and historical snapshots are non-authoritative for the current frontier unless explicitly promoted by the live state stack.

## Current operating state — 2026-08-23

Production target: 1,080 passages total, 360 per language, 60 per CEFR level A1-C2.

- **Arabic:** 360/360 generated; A1-C2 generation complete. Educator/publication release is not currently cleared by `RELEASE_STATUS.json`.
- **French:** 360/360 generated; A1-C2 generation complete. Release is `REOPEN_REQUIRED`; the latest post-repair deterministic Gate A remains failed pending substantive evidence revalidation.
- **Urdu:** 60/360 generated; A1 generation complete, A2 is next. The exact A1 integrity audit reports 60 passages, 600 questions, 600 answers, 0 hard errors, and 0 warnings for the pinned corpus, but explicitly does **not** promote quality/release status.
- **Project generated:** 780/1080 passages.

Current production frontier: **Urdu A2, Unit 1, sequence 1**.

Run `python reading/tools/validate_continuation_state.py` before trusting stored counts/frontiers in a fresh session. After tracked live-state edits, run `python reading/tools/refresh_state_manifest.py` last.

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

Live state files must remain compact. Do not append dated historical timelines or multiple contradictory `IMMEDIATE NEXT` sections. Completed work belongs in Git history and `reading/audit/`; live files should preserve only verified current state, blockers, and exact next actions. Refresh the state manifest after tracked live-state edits so a replacement chat can prove it has one coherent bundle rather than a mixture of revisions.
