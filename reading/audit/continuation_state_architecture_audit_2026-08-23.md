# LANG-A1C2 continuation/state architecture audit — 2026-08-23

## Scope

Audited the live continuation/status architecture for the Arabic/French/Urdu A1-C2 graded-reading project, with the goal of making max-length chat replacement safe, compact, auditable, and resistant to cross-project drift.

Primary files reviewed:

- `reading/README.md`
- `reading/STATUS.json`
- `reading/RELEASE_STATUS.json`
- `reading/AGENT_HANDOFF.md`
- `reading/AGENT_HANDOFF_V2.md`
- `reading/TASKS.md`
- `reading/VERIFICATION_TASKS.md`
- `reading/planning/ACTIVE_GENERATION_PLAN.json`
- `reading/planning/C2_GENERATION_STATE.json`
- `reading/planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md`
- `reading/planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md`
- `reading/planning/topic_genre_matrix.json`
- current Urdu A1 canonical corpus and final integrity evidence

## Evidence reconciliation

Live Urdu A1 canonical data is complete at 60 passages. The canonical `reading/urdu/a1/passages.jsonl` Git blob is:

`ec0970dc1916ce523dd3320d2f4dca4c7f8bc677`

`reading/audit/urdu_a1_final_integrity_2026-08-23.json` is bound to that exact blob and records:

- 60 passages;
- 600 questions;
- 600 answers;
- 130 cloze questions, all reconstructing;
- 0 hard errors;
- 0 warnings;
- `quality_promotion: false`.

This proves a clean deterministic/integrity baseline for the pinned corpus. It does **not** prove educator/publication readiness.

Reconciled production totals:

- Arabic: 360/360 generated;
- French: 360/360 generated;
- Urdu: 60/360 generated;
- total: 780/1080 generated;
- next production level: Urdu A2.

## Findings

### F1 — critical: live Urdu state was stale

Several live-state files still described only Urdu A1 sequences 1-30 / Units 01-05 as canonical even though the live corpus had reached 60/60 passages and had a completed exact-corpus integrity audit.

Risk: a new chat could regenerate already-completed A1 material, overwrite the wrong frontier, or waste work auditing a superseded staging boundary.

Resolution: production state was reconciled to the exact 60-passage corpus and pinned blob.

### F2 — high: historical timelines were mixed into current state

`STATUS.json`, `TASKS.md`, and handoff material accumulated long completed histories and multiple old next-action sections.

Risk: later text could be mistaken for current truth, especially after chat truncation.

Resolution: live files were rewritten as compact current-state/active-queue documents. Historical detail now belongs in Git history and `reading/audit/`.

### F3 — high: generation and release concepts could be conflated

Historical `APPROVED`, `SEALED`, and internal PASS wording coexisted with stricter later educator-release evidence showing unresolved gates.

Risk: generation completion or an internal pass could be incorrectly reported as teacher/publication readiness.

Resolution: `STATUS.json` is explicitly production-only; `RELEASE_STATUS.json` is explicitly release-evidence-only. `CONTINUATION.json` requires the two states to remain separate.

A first redesign still mirrored live canonical passage counts into `RELEASE_STATUS.json`. That would have forced release state to change after every generation batch even when no release evidence changed. This coupling was removed. Release status now records the **scope of the cited evidence**, while `STATUS.json` owns live production counts.

### F4 — high: durable policy carried dated frontier state

`FINAL_REVIEW_EXECUTION_PROTOCOL.md` embedded a 2026-08-16 Arabic-only current phase and immediate sequence, even after French and Urdu work had advanced far beyond it.

Risk: a durable protocol could resurrect an obsolete language frontier.

Resolution: the protocol is now state-independent and explicitly forbids dated current-frontier content. Current state is delegated to continuation/status files.

### F5 — high: legacy handoff remained a large alternative source

`reading/AGENT_HANDOFF.md` contained substantial stale continuation material despite being declared legacy elsewhere.

Risk: old links or agents could still resume from it.

Resolution: the legacy file is now a short redirect to the authoritative continuation stack; its history remains recoverable from Git.

### F6 — high: active generation plan was stale

`reading/planning/ACTIVE_GENERATION_PLAN.json` still selected A1 after Urdu A1 had completed.

Resolution: active production is now Urdu A2, Unit 1, sequence 1, using the A2 roadmap lookup instead of duplicating the whole roadmap inside the derived plan.

### F7 — high: no fail-closed continuation freshness gate

The repository had conventions for updating state but no single check that canonical counts/frontier/hash anchors still matched continuation/status files.

Resolution: added `reading/tools/validate_continuation_state.py` and `.github/workflows/validate-language-a1c2-continuation.yml`.

The validator checks:

- project identity;
- canonical JSONL validity/counts by language against production state (`STATUS` and `CONTINUATION`);
- total generated count;
- active-frontier agreement among `CONTINUATION`, `STATUS`, and `ACTIVE_GENERATION_PLAN`;
- `RELEASE_STATUS` remains release-evidence-only rather than a live production mirror;
- exact Urdu A1 Git blob binding across production and release evidence;
- exact integrity-artifact blob binding;
- Urdu A1 integrity counts/errors/warnings/cloze gate;
- `quality_promotion: false` preservation;
- production/release separation;
- `PROJECT_TRACKS.json` routing and workbook/progress scope exclusions.

Any mismatch exits non-zero.

### F8 — high: README was an obsolete resume entry point

The old README still said French had six passages and Urdu was queued, and directed readers to the legacy handoff.

Resolution: README now identifies `LANG-A1C2`, gives the authoritative resume order, reconciled 780/1080 production state, release-state separation, and current Urdu A2 frontier.

### F9 — medium/high: cross-chat project identity was implicit

Both the graded-reading project and workbook project are language projects, making generic prompts such as “proceed with the language chats” vulnerable to cross-project continuation after context loss.

Resolution:

- added scoped `reading/AGENTS.md` with project ID `LANG-A1C2` and hard exclusions;
- added root `PROJECT_TRACKS.json` routing `LANG-A1C2` vs `LANG-WB`;
- canonical new-chat prefixes are `LANG-A1C2 — CONTINUE` and `LANG-WB — CONTINUE`.

### F10 — medium: specialized historical state could still advertise an obsolete next phase

`reading/planning/C2_GENERATION_STATE.json` was a valid French C2 completion snapshot but still exposed `next_phase: whole-French final audit` as though it were a live instruction.

Risk: a new agent searching for state-like files could mistake a historical French C2 milestone for the project frontier.

Resolution: the file is retained for traceability but is now explicitly `HISTORICAL_FRENCH_C2_GENERATION_SNAPSHOT`, sets `authoritative_for_current_frontier: false`, and points to `CONTINUATION`, `STATUS`, and `RELEASE_STATUS` for current truth.

## New continuation architecture

### Repository project router

`PROJECT_TRACKS.json`

Routes the two similarly named language projects before their internal continuation files are read:

- `LANG-A1C2` -> `reading/`;
- `LANG-WB` -> workbook generation/audit/curation roots.

Each route explicitly excludes the other project's root(s).

### Machine-readable live state

`reading/CONTINUATION.json`

Contains only:

- project/scope guard;
- authoritative read order;
- truth precedence;
- update contract;
- production snapshot;
- release summary pointers;
- current production frontier;
- parallel verification lanes;
- exact resume checks/next actions.

### Production status

`reading/STATUS.json`

Contains live production counts/frontier only. It cannot authorize educator-release claims.

### Release status

`reading/RELEASE_STATUS.json`

Contains release decisions, evidence scopes, evidence pointers, blockers, and assurance rules only. Evidence-scope counts describe the corpus actually reviewed; they are not live generation counters. Detailed history stays in audit artifacts/Git.

### Human handoff

`reading/AGENT_HANDOFF_V2.md`

Explains the operating cycle, state update contract, freshness rules, and one exact current production frontier.

### Active queues

- `reading/TASKS.md` — active production/release work only.
- `reading/VERIFICATION_TASKS.md` — active verification gates only.

No append-only historical `IMMEDIATE NEXT` sections.

### Scoped routing

- `reading/AGENTS.md` — hard scope rules for this tree.
- `PROJECT_TRACKS.json` — repository-level routing between `LANG-A1C2` and `LANG-WB`.

## Current exact resume state after audit

Project: `LANG-A1C2`

Production:

- Arabic A1-C2: generation complete, 360 passages.
- French A1-C2: generation complete, 360 passages.
- Urdu A1: generation complete, 60 passages.
- Urdu A2: next production level, Unit 1 / sequence 1.
- total generated: 780/1080.

Release:

- Arabic: not educator/publication ready under current release gates.
- French: `REOPEN_REQUIRED`; latest post-repair Gate A remains failed pending substantive evidence revalidation.
- Urdu: A1 deterministic/integrity baseline passes for the pinned corpus, but `quality_promotion` is false; broader release evidence is not recorded as complete.

## New-chat protocol

For this project, start a replacement chat with:

`LANG-A1C2 — CONTINUE`

Then read `PROJECT_TRACKS.json`, `reading/AGENTS.md`, and `reading/CONTINUATION.json` before doing work.

For the separate workbook project, use:

`LANG-WB — CONTINUE`

Do not infer one from the other based on generic words such as “language”, “Arabic”, “French”, “Urdu”, or “workbook”.

## Residual limitations

- The connected GitHub interface used for this audit can write/read repository files, but a repository-side CI run of the newly added validation workflow has not been observed in this session.
- Direct network access from the execution runtime to GitHub was unavailable for cloning/executing the repository locally in this session.
- These are tooling-observation limitations, not evidence that the validator passed or failed. The validator and workflow are committed; an observed Actions run should be treated as the machine confirmation.
- Durable roadmap/history files may still mention older lifecycle terminology, but they are deliberately lower precedence than the new continuation stack, and the legacy handoff they reference now redirects to current state.

## Audit result

**Architecture materially improved and stale live-state contradictions corrected.**

The project now has a single explicit identity, compact current-state object, genuinely separated production/release truth, one production frontier, active-only queues, legacy redirect, scope routing, historical-snapshot labeling, and a fail-closed consistency validator.
