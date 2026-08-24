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
9. `reading/TASKS.md`

Run:

`python reading/tools/validate_continuation_state.py`

and:

`python reading/tools/validate_week_ready_queue.py`

before trusting a stored frontier when execution is available.

## Gate A — close/integrate Urdu A2 Unit 1

A reviewed Unit 1 generation branch exists:

`lang-a1c2-urdu-a2-unit01`

Draft integration PR: **#58 — LANG-A1C2: add and polish Urdu A2 Unit 1**.

Its intended post-integration production state is:

- project: **786/1080** generated;
- Urdu: **66/360** generated;
- Urdu A2: **6/60** generated;
- active frontier: **Urdu A2 Unit 2 / sequence 7**.

The branch contains:

- six Unit 1 passages, sequences 1-6;
- exact lexical-sense evidence for the eight deliberate targets;
- a hash-guarded bounded reader-first quality remediation that corrects the identified naturalness/semantic issues and emits `reading/audit/urdu_a2_u01_quality_pass_2026-08-23.json`.

### Morning decision

**Case 1 — Unit 1 is already integrated:** if `main` shows project=786, Urdu=66, and Unit 2 / sequence 7 with `validate_continuation_state.py` green, do **not** reopen or regenerate Unit 1. Go directly to Session 1 below.

**Case 2 — PR #58 is still draft:** verify that `reading/audit/urdu_a2_u01_quality_pass_2026-08-23.json` exists on the PR branch and is bound to the repaired Unit 1 corpus. If it is absent, keep the PR blocked and run/apply the prepared exact remediation before merge. If it is present and checks are clean, merge PR #58 through GitHub's normal merge path and rerun continuation validation on `main`.

Never force `main` to the Unit 1 branch head or reuse the branch's whole tree as `main`; unrelated work is landing in parallel.

## Gate B — seven ready sessions

`reading/planning/WEEK_READY_2026-08-24.json` pre-stages seven sessions:

1. Urdu A2 Unit 2 — plans, invitations, and changes — sequences 7-12
2. Unit 3 — past events and memories — 13-18
3. Unit 4 — shopping, comparison, and problems — 19-24
4. Unit 5 — hobbies and learning skills — 25-30
5. Unit 6 — transport and travel — 31-36
6. Unit 7 — community events and simple news — 37-42
7. Unit 8 — nature and environment — 43-48

If all seven sessions complete successfully, the expected frontier is:

- project: **828/1080** generated;
- Urdu: **108/360** generated;
- Urdu A2: **48/60** generated;
- next: **Urdu A2 Unit 9 / sequence 49**.

When present, `reading/audit/week_ready_2026-08-24.json` is the hash-bound machine evidence for the prepared queue. If that audit is absent, rerun `python reading/tools/write_week_ready_audit.py` after the queue validator passes rather than inferring readiness from this guide alone.

## Per-session operating pattern

Each session is one complete six-passage unit, not six disconnected micro-tasks:

- P1 instructional;
- P2 reinforcement;
- P3 interleaved;
- P4 transfer;
- P5 integration;
- P6 fluency/checkpoint.

Use the A2 standard band of **140-220 words** as the normal target, not a hard law. Keep new vocabulary controlled, sense-verified, inferable, and naturally collocated. P6 should normally have no deliberate new lexical target. Every passage gets exactly 10 linked questions/answers under the current Ten-Question Standard, with operational A2 grammar rather than unnecessary formal metalanguage.

## Important lexical scheduling note

`reading/ledgers/urdu_lexical_exposure.jsonl` currently has stale `introduced_in` state and must **not** be treated as authoritative scheduling truth until rebuilt from canonical passages.

For each new unit, derive candidate targets from `reading/lexicons/urdu.jsonl`, subtract all target IDs already introduced in live Urdu A1/A2 canonical passages, then verify the exact learner-facing sense before generation. Do not teach an ambiguous collocation merely to preserve a target occurrence.

## State transaction order

After each unit:

1. update canonical Urdu A2 JSONL;
2. run the bounded reader-first quality pass and preserve evidence;
3. update `reading/STATUS.json`, `reading/CONTINUATION.json`, and `reading/TASKS.md` as required;
4. run `python reading/tools/extract_active_generation_plan.py`;
5. run `python reading/tools/refresh_state_manifest.py`;
6. run `python reading/tools/validate_continuation_state.py`;
7. integrate via a merge/PR path that preserves concurrent unrelated `main` commits.

Generation/integrity success never changes educator/publication readiness by itself. `reading/RELEASE_STATUS.json` changes only when release evidence itself changes.

## Exact first production action tomorrow

After Gate A is green, execute **Session 1 / Urdu A2 Unit 2**, sequences **7-12**, theme **“plans, invitations, and changes”**, using the exact genres in the A2 roadmap and the shared contract in `WEEK_READY_2026-08-24.json`.
