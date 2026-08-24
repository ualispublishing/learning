# LANG-A1C2 — Tomorrow Start Guide

Ready from: **2026-08-24**  
Timezone: **America/Toronto**

This guide is only for the Arabic/French/Urdu **A1-C2 graded-reading project under `reading/`**. Do not switch into the language-workbook (`LANG-WB`) or `progress/` tracks.

## Start phrase

Use:

`LANG-A1C2 — CONTINUE`

Then read, in order:

1. `PROJECT_TRACKS.json`
2. `reading/AGENTS.md`
3. `reading/CONTINUATION.json`
4. `reading/STATE_MANIFEST.json`
5. live `reading/urdu/a2/passages.jsonl`
6. `reading/STATUS.json`
7. `reading/planning/ACTIVE_GENERATION_PLAN.json`
8. `reading/planning/WEEK_READY_2026-08-24.json`
9. `reading/audit/week_ready_2026-08-24.json`
10. `reading/TASKS.md`

Run:

`python reading/tools/validate_continuation_state.py`

and:

`python reading/tools/validate_week_ready_queue.py`

before writing new canonical passages when execution is available.

## Baseline is already closed

Urdu A2 Unit 1 is **integrated on `main`**. Do not regenerate or reopen it merely because the historical source branch or closed PR still exists.

Current intended production baseline:

- project: **786/1080** generated;
- Urdu: **66/360** generated;
- Urdu A2: **6/60** generated;
- active frontier: **Urdu A2 Unit 2 / sequence 7**.

Unit 1 evidence on `main` includes:

- `reading/audit/urdu_a2_u01_lexical_sense_check_2026-08-23.json`;
- `reading/audit/urdu_a2_u01_quality_pass_2026-08-23.json` with `PASS_AFTER_BOUNDED_REMEDIATION`;
- repaired Unit 1 corpus result blob `e5bb0fb6fb642a37ba4f69537f960cbb324fd365`;
- 6 passages / 60 questions / 60 answers;
- unchanged deliberate target identities;
- zero deliberate new lexical targets in the Unit 1 fluency passage;
- refreshed `reading/STATE_MANIFEST.json` bound to project=786 / Urdu=66.

Historical draft PR #58 was closed as superseded after the vetted files were replayed cleanly onto the then-current `main`. Do not merge or revive it.

## Seven ready sessions

`reading/planning/WEEK_READY_2026-08-24.json` pre-stages seven sessions:

1. **Unit 2** — plans, invitations, and changes — sequences **7-12**
2. **Unit 3** — past events and memories — **13-18**
3. **Unit 4** — shopping, comparison, and problems — **19-24**
4. **Unit 5** — hobbies and learning skills — **25-30**
5. **Unit 6** — transport and travel — **31-36**
6. **Unit 7** — community events and simple news — **37-42**
7. **Unit 8** — nature and environment — **43-48**

The queue has a hash-bound PASS artifact at `reading/audit/week_ready_2026-08-24.json`. That artifact must match this guide, the week queue, validator, and A2 roadmap; if any of those files change, regenerate the audit rather than relying on the old PASS.

If all seven sessions complete successfully, expected state is:

- project: **828/1080** generated;
- Urdu: **108/360** generated;
- Urdu A2: **48/60** generated;
- remaining project generation: **252** passages;
- next frontier: **Urdu A2 Unit 9 / sequence 49**.

## Per-session operating pattern

Each session is one complete six-passage unit:

- P1 instructional;
- P2 reinforcement;
- P3 interleaved;
- P4 transfer;
- P5 integration;
- P6 fluency/checkpoint.

Use the A2 standard band of **140-220 words** as the normal target, not a hard law. Keep new vocabulary controlled, sense-verified, inferable, and naturally collocated. P5 should be cumulative; P6 should normally introduce no deliberate new lexical target. Every passage gets exactly **10 linked questions and 10 answers** under the current Ten-Question Standard, with operational A2 grammar rather than unnecessary formal metalanguage.

## Important lexical scheduling note

`reading/ledgers/urdu_lexical_exposure.jsonl` currently has stale `introduced_in` state and must **not** be treated as authoritative scheduling truth until rebuilt from canonical passages.

For each new unit:

1. derive candidate targets from `reading/lexicons/urdu.jsonl`;
2. subtract every target ID already introduced in live Urdu A1/A2 canonical passages;
3. verify the exact learner-facing sense before generation;
4. reject ambiguous/noisy senses or unnatural collocations rather than forcing an occurrence;
5. schedule deliberate review in later passages using the canonical passage history as the reliable source.

## State transaction order

After each unit:

1. update canonical Urdu A2 JSONL;
2. run a bounded reader-first quality pass and preserve evidence;
3. update `reading/STATUS.json`, `reading/CONTINUATION.json`, and `reading/TASKS.md` as required;
4. run `python reading/tools/extract_active_generation_plan.py`;
5. run `python reading/tools/refresh_state_manifest.py`;
6. run `python reading/tools/validate_continuation_state.py`;
7. integrate through a current-main-safe transaction; never overwrite concurrent unrelated work with an older branch tree.

Generation/integrity success never changes educator/publication readiness by itself. `reading/RELEASE_STATUS.json` changes only when release evidence itself changes.

## Exact first action tomorrow

Execute **Session 1 / Urdu A2 Unit 2**, sequences **7-12**, theme **“plans, invitations, and changes”**, using the exact genres in `reading/planning/topic_genre_matrix.json` and the shared contract in `reading/planning/WEEK_READY_2026-08-24.json`.
