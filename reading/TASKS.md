# LANG-A1C2 Active Tasks

Updated: 2026-08-30

This file is an **active queue only**. Completed timelines belong in Git history and `reading/audit/`. Current truth starts with `PROJECT_TRACKS.json`, `reading/CONTINUATION.json`, and live canonical data.

## P0 — state integrity

- [ ] Confirm `PROJECT_TRACKS.json` routes this session to `LANG-A1C2`, not `LANG-WB`.
- [ ] Run `python reading/tools/validate_continuation_state.py` before resuming generation after a new chat/session.
- [ ] If `reading/STATE_MANIFEST.json` differs from tracked live-state bytes, stop and reconcile/refresh it before continuing.
- [ ] If canonical counts or the pinned Urdu A1 blob differ from continuation/status state, reconcile before writing new passages.
- [ ] Keep production state and educator-release state separate; never infer release readiness from generation-complete or historical approval labels.

## P1 — canonical generation complete

There is **no active production frontier**. Arabic, French, and Urdu A1-C2 canonical generation is complete at **1080/1080**.

- [x] Arabic: 360/360 generated.
- [x] French: 360/360 generated.
- [x] Urdu: 360/360 generated; A1-C2 complete.
- [x] Project: 1080/1080 generated.
- [ ] Do not reopen canonical generation unless fresh evidence identifies a concrete defect requiring bounded repair.
- [ ] Keep all educator/publication release claims under the independent release/verification workstreams below.

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
- no active production frontier after generation completion;
- exactly one explicit next verification/release action;
- no historical `IMMEDIATE NEXT` sections left in this file.
