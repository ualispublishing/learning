# LANG-A1C2 Active Tasks

Updated: 2026-08-29

This file is an **active queue only**. Completed timelines belong in Git history and `reading/audit/`. Current truth starts with `PROJECT_TRACKS.json`, `reading/CONTINUATION.json`, and live canonical data.

## P0 — state integrity

- [ ] Confirm `PROJECT_TRACKS.json` routes this session to `LANG-A1C2`, not `LANG-WB`.
- [ ] Run `python reading/tools/validate_continuation_state.py` before resuming generation after a new chat/session.
- [ ] If `reading/STATE_MANIFEST.json` differs from tracked live-state bytes, stop and reconcile/refresh it before continuing.
- [ ] If canonical counts or the pinned Urdu A1 blob differ from continuation/status state, reconcile before writing new passages.
- [ ] Keep production state and educator-release state separate; never infer release readiness from generation-complete or historical approval labels.

## P1 — active production: Urdu C2

Canonical production frontier: **Urdu C2, Unit 7, sequence 37**.

- [ ] Read `reading/planning/ACTIVE_GENERATION_PLAN.json` and the exact C2 entry in `reading/planning/topic_genre_matrix.json`.
- [ ] Generate Urdu C2 in guarded unit or large bounded batches under the generation-first policy.
- [ ] Preserve 6 passages per unit and the active 10-question/10-answer contract unless a documented pedagogical exception is necessary.
- [ ] Write independent natural contemporary Urdu; do not translate Arabic/French passage-by-passage.
- [ ] Independently learner-check every deliberately taught lexical sense before assessing that sense in a question.
- [ ] Fix obvious severe defects immediately, but do not interrupt ordinary generation with repeated whole-corpus release audits.
- [ ] After each canonical batch, update the live production state files in the same work unit.

Current production totals:

- Arabic: 360/360 generated.
- French: 360/360 generated.
- Urdu: 336/360 generated; A1-C1 complete, C2 in progress.
- Project: 1056/1080 generated.

## P1 — release/verification workstreams

These run independently of ordinary generation unless a concrete blocker requires otherwise.

### Arabic

- [ ] Resolve and revalidate the open educator-release defect classes listed in `reading/RELEASE_STATUS.json`.
- [ ] Complete fresh semantic, native/professional, educator, adversarial, and hash-bound release evidence required by the assurance profile.

### French

- [ ] Substantively revalidate the record-level evidence behind the post-repair Gate A failure.
- [ ] Do **not** bulk-promote `draft`/`pending` metadata just to remove the 2,160 findings.
- [ ] Rerun Gate A only after real evidence is recorded, then continue the independent semantic/release gates.

### Urdu A1

- [ ] Preserve the exact integrity-passing baseline at blob `ec0970dc1916ce523dd3320d2f4dca4c7f8bc677` unless a concrete defect requires a canonical change.
- [ ] Treat `reading/audit/urdu_a1_final_integrity_2026-08-23.json` as structural/integrity evidence only (`quality_promotion: false`).
- [ ] Add semantic naturalness, pedagogy, answer-key, lexical/CEFR, and independent review evidence at the designated review milestone.

## State-update checklist

After production changes:

- [ ] `reading/CONTINUATION.json`
- [ ] `reading/STATUS.json`
- [ ] `reading/planning/ACTIVE_GENERATION_PLAN.json` when frontier changes
- [ ] this file
- [ ] `reading/AGENT_HANDOFF_V2.md` when its live snapshot/frontier would otherwise become stale

After release-evidence changes:

- [ ] `reading/VERIFICATION_TASKS.md`
- [ ] `reading/RELEASE_STATUS.json`
- [ ] `reading/CONTINUATION.json` whenever its cached release summary changes

After all tracked live-state edits:

- [ ] run `python reading/tools/refresh_state_manifest.py` last;
- [ ] run `python reading/tools/validate_continuation_state.py` against the refreshed bundle when execution is available.

## Definition of a clean handoff

A work session ends with:

- project route confirmed;
- live canonical state verified;
- state manifest refreshed for the exact live-state bundle;
- affected checks run and recorded;
- no hidden source/hash drift;
- blockers separated into content vs tooling/evidence problems;
- exactly one current production frontier;
- exactly one explicit next production action;
- no historical `IMMEDIATE NEXT` sections left in this file.
