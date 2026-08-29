# LANG-A1C2 Agent Handoff

Updated: 2026-08-29

## Scope guard

This handoff is only for the Arabic/French/Urdu A1-C2 graded-reading project under `reading/`.

Do **not** resume the language-workbook project (`completed/languages/workbooks/v1.0/`, `audit/language-workbooks/v1.0/`, `curation/language-workbooks/v1.0/`) or the separate `progress/` language-study track from this handoff.

`reading/AGENT_HANDOFF.md` is legacy history and is not authoritative.

## Start every new session here

1. Read `PROJECT_TRACKS.json` and confirm `LANG-A1C2` routes to `reading/`.
2. Read `reading/AGENTS.md` and `reading/CONTINUATION.json`.
3. Verify the canonical JSONL for the language/level you are about to touch.
4. Read `reading/STATE_MANIFEST.json` and run `python reading/tools/validate_continuation_state.py` when execution is available.
5. Read `reading/RELEASE_STATUS.json` if making any quality/release claim.
6. Read `reading/STATUS.json` for production counts/frontier.
7. Read `reading/planning/ACTIVE_GENERATION_PLAN.json` for the current generation target.
8. Read `reading/TASKS.md` and `reading/VERIFICATION_TASKS.md` for active work only.
9. Apply durable policy/schema/roadmap files as needed.

If stored state, the state manifest, and live canonical files disagree, **fail closed and reconcile first**. Do not continue from chat memory or stale checklist text.

## Current truth snapshot

### Production

- Target: 1,080 passages total; 360 per language; 60 per CEFR level A1-C2.
- Canonical generated total: **1038**.
- Arabic: **360/360**, A1-C2 generation complete.
- French: **360/360**, A1-C2 generation complete.
- Urdu: **318/360**; A1-C1 generation complete and C2 generation in progress.
- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-10 contain sequences 1-60 and A2 generation is complete.
- Urdu A1 canonical path: `reading/urdu/a1/passages.jsonl`.
- Urdu A1 pinned Git blob: `ec0970dc1916ce523dd3320d2f4dca4c7f8bc677`.
- Urdu A1 final integrity evidence: `reading/audit/urdu_a1_final_integrity_2026-08-23.json`.
- That evidence covers 60 passages, 600 questions, and 600 answers with zero hard errors and zero warnings, but explicitly has `quality_promotion: false`.

### Release / educator readiness

Generation state and release state are separate.

- Arabic: educator/publication release **not ready** under the current highest-assurance release gate.
- French: release state **REOPEN_REQUIRED**. The latest post-repair deterministic Gate A remains failed with 2,160 release-evidence findings requiring substantive revalidation.
- Urdu: the cited release evidence establishes an A1 structural/integrity baseline only; it is **not** semantic/educator approval or a language-level release. Consult `reading/STATUS.json` for live generation progress beyond that evidence scope.

Never convert historical `APPROVED`, `SEALED`, `PASS`, or generation-complete wording into an educator-readiness claim. `reading/RELEASE_STATUS.json` controls affirmative release decisions, and fresh contrary evidence invalidates reliance on stale approval evidence.

## Active production frontier

Continue **Urdu C2**, starting from Unit 4 / sequence 19, under:

- `reading/planning/ACTIVE_GENERATION_PLAN.json`
- `reading/planning/topic_genre_matrix.json`
- `reading/planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md`
- `reading/planning/TEN_QUESTION_STANDARD.md`
- `reading/schema/passage.schema.json`

C2 Unit 4 uses the roadmap theme **economics and complex systems** with `analytical essay`, `scenario analysis`, and `commentary` genres.

Generate in guarded unit or large bounded batches. Do not reopen Urdu A1 generation unless fresh evidence identifies a concrete defect.

## Parallel verification lanes

These are separate from the generation frontier:

1. **Arabic release remediation** — resolve/revalidate the known educator-release defect classes and complete fresh semantic/independent review.
2. **French release remediation** — substantively revalidate the 360 records rather than bulk-promoting pending metadata; rerun Gate A only from fresh evidence.
3. **Urdu A1 quality review** — preserve the exact clean integrity baseline while adding semantic/naturalness/pedagogical/answer-key/CEFR evidence. Do not label the level released merely because deterministic integrity passed.

## Operating cycle

For each substantive work unit:

1. verify project route, current canonical state, and relevant hashes/counts;
2. verify the state bundle when execution is available;
3. select the highest-value unfinished item from the active frontier/queue;
4. work in an evidence-bounded batch;
5. run only the checks materially affected by the change, plus any required final gate;
6. fail closed on source drift, schema mismatch, unexpected record selection, stale audit evidence, or state-bundle mismatch;
7. commit canonical changes and directly affected evidence together when practical;
8. update live state immediately;
9. refresh `reading/STATE_MANIFEST.json` after tracked state edits;
10. leave one exact next action, not several historical alternatives.

## State update contract

After a **production** state change, update together:

- `reading/CONTINUATION.json`
- `reading/STATUS.json`
- `reading/planning/ACTIVE_GENERATION_PLAN.json` if the frontier changed
- `reading/TASKS.md`
- `reading/AGENT_HANDOFF_V2.md` when its live snapshot/frontier changes

After a **verification/release** evidence change, update as applicable:

- `reading/VERIFICATION_TASKS.md`
- `reading/RELEASE_STATUS.json`
- `reading/CONTINUATION.json` whenever its cached release summary changes

After those edits, run:

`python reading/tools/refresh_state_manifest.py`

Do not append historical timelines to live state files. Detailed completed work belongs in `reading/audit/` and Git history.

## Freshness rules

- Audit evidence is valid only for the canonical bytes/state it actually examined.
- If a pinned hash/blob no longer matches, the old audit becomes historical evidence until rerun or explicitly revalidated.
- A zero-step or skipped check is not a green gate.
- Tooling/environment blockers must be recorded separately from content defects.
- Machine validity does not replace a reader-first linguistic/pedagogical pass.
- Final approval is fail-closed and must be hash-bound to the reviewed corpus.

## Exact next action

Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu C2 Unit 4 / sequence 19** using the C2 Unit 4 roadmap theme `economics and complex systems`.
