# Reading Curriculum Task List

This is the **active operational queue**. Historical calibration/review work belongs in git history and audit artifacts; do not infer current state from old unchecked items.

## Arabic — COMPLETE / APPROVED

- [x] A1: 60 passages / 600 questions / 600 answers.
- [x] A2: 60 / 600 / 600.
- [x] B1: 60 / 600 / 600.
- [x] B2: 60 / 600 / 600.
- [x] C1: 60 / 600 / 600.
- [x] C2: 60 / 600 / 600.
- [x] Passes 01–09 freshly `PASS`.
- [x] Pass 10 source adjudication closed (`PASS_WITH_SOURCE_ADJUDICATION`).
- [x] Pass 11 manual naturalness review `COMPLETE`, 360/360.
- [x] Pass 12 `PASS`, zero hard regressions, zero final-approval blockers.
- [x] Arabic formal final approval = `true`.

Do not reopen Arabic unless canonical Arabic content is deliberately changed.

## French — ACTIVE

### A1 — GENERATED / INTEGRITY PASS / CLOSED TO ROUTINE REGENERATION

- [x] Units 01–10 / sequences 1–60 generated.
- [x] 60 passages / 600 questions / 600 linked answers.
- [x] Every Unit P06 checkpoint has zero deliberately new lexical targets.
- [x] Generation-integrity closeout = `PASS` with 100 deliberate targets, four verified sense overrides, documented morphology/polysemy exceptions, and no remaining integrity failures.
- [x] Current A1 canonical blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`.

A1 is still part of the generation-first French corpus and has **not** gone through the final language-wide multi-pass approval audit. Do not broadly regenerate it.

### A2 — ACTIVE

- [x] Verify live A2 start state and A2 140–220-word planning band.
- [x] Unit 01 / sequences 1–6 generated and committed as one guarded batch.
- [x] Unit 01: 60 questions / 60 linked answers / 10 new targets / zero-new P06.
- [x] Unit 01 bridge reviews from A1 are explicitly visible and locally declared.
- [x] Unit 01 source, linkage, word-band, sequence, reader-facing-language, and collision checks passed independently.
- [x] Current A2 canonical blob after Unit 01: `26b18ab417f19597cf12d7d45b8932c5654292fd`.
- [ ] Unit 02 / sequences 7–12: generate as one guarded batch against the live Unit-01 blob.
- [ ] Review Unit-01 targets one pair per P01–P05 where natural; keep P06 zero-new-target.
- [ ] Continue A2 in coherent six-passage guarded batches to 60 passages.

A2 Unit 01 target set:
`retard`, `conseil`, `erreur`, `expliquer`, `essayer`, `possible`, `réparer`, `éviter`, `rendez-vous`, `découvrir`.

Remaining French levels:

- [ ] A2: 54 passages remain after Unit 01.
- [ ] B1: 60 passages.
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

Production policy:

- generation-first, full multi-pass audit at completed French corpus milestone;
- A2 standard passages use the 140–220-word planning band and controlled lexical load;
- lightweight structural/source/linkage validation during generation;
- fail closed on lexical-source drift, canonical blob drift, schema failure, linkage failure, invisible deliberate review, reader-facing contamination, or sequence collision;
- do not mutate the root validated lexical CSV merely to simplify passage production.

## Urdu — QUEUED

- [x] A1 sequences 1–6 exist in `reading/urdu/a1/passages.jsonl`.
- [x] `reading/urdu/a1/calibration/` exists.
- [ ] A1 sequences 7–60.
- [ ] A2–C2: 60 passages each.

Keep Urdu unchanged while French is active unless explicitly reprioritized.

## Throughput rules

- Work in coherent unit/batch scopes, not passage-by-passage workflows.
- One live-state/collision check + one guarded script + one relevant validation run per batch.
- Rerun only checks affected by the fields changed.
- Full multi-pass audit is a final-stage operation, not a per-generation-batch tax.
- Fail closed on source drift or invariant failure, then fix the same batch script unless the issue truly requires separate adjudication.
- Serialize writers to the same canonical/audit artifact.

## Immediate next task

**Generate French A2 Unit 02 / sequences 7–12 against canonical A2 blob `26b18ab417f19597cf12d7d45b8932c5654292fd`. Keep Arabic sealed.**
