# Scoped agent instructions — LANG-A1C2

These instructions apply to the `reading/` tree.

## Project identity

Project ID: **LANG-A1C2**

Scope: Arabic, French, and Urdu A1-C2 graded-reading generation, verification, and release evidence.

Never silently switch this work into:

- the language-workbook project under `completed/languages/workbooks/v1.0/`, `audit/language-workbooks/v1.0/`, or `curation/language-workbooks/v1.0/`;
- the separate `progress/` language-study track.

If a user starts a new chat with `LANG-A1C2`, this is the project they mean unless they explicitly redefine the label.

## Mandatory resume order

1. `reading/CONTINUATION.json`
2. live canonical `reading/<language>/<level>/passages.jsonl` relevant to the task
3. `reading/RELEASE_STATUS.json` for educator/publication claims
4. `reading/STATUS.json` for production counts/frontier
5. `reading/AGENT_HANDOFF_V2.md`
6. `reading/planning/ACTIVE_GENERATION_PLAN.json`
7. `reading/TASKS.md` / `reading/VERIFICATION_TASKS.md`
8. durable policies, schema, research standards, and roadmap as needed

`reading/AGENT_HANDOFF.md` is a legacy redirect only.

## Fail-closed continuity rules

- Run `python reading/tools/validate_continuation_state.py` before trusting a stored frontier in a fresh working session when execution is available.
- If canonical data, pinned hashes, audit evidence, or live state disagree, stop progression and reconcile the state first.
- Production completion and educator/publication release are separate states.
- Never infer release readiness from historical `APPROVED`, `SEALED`, `PASS`, `FINAL_APPROVED`, or generation-complete labels.
- Audit evidence is valid only for the canonical bytes/fields it examined.
- A zero-step/skipped check is not a green gate.
- Machine integrity does not replace linguistic, pedagogical, native/professional, or educator review when required.

## State-writing rules

Keep live state compact. Do not append long historical timelines or multiple competing `IMMEDIATE NEXT` sections.

After a production frontier/count change, update together:

- `reading/CONTINUATION.json`
- `reading/STATUS.json`
- `reading/planning/ACTIVE_GENERATION_PLAN.json` if frontier changed
- `reading/TASKS.md`

After release/verification evidence changes, update as applicable:

- `reading/VERIFICATION_TASKS.md`
- `reading/RELEASE_STATUS.json`
- `reading/CONTINUATION.json` if its live summary/frontier changes

Detailed completed work belongs in `reading/audit/` and Git history.

## Current frontier lookup

Do not encode a dated current frontier in this instruction file. Resolve it from `reading/CONTINUATION.json` and verify it against live canonical data.
