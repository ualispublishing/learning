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

Final Arabic evidence:
`reading/audit/final_arabic_pass12_adversarial_gate_falsification.json`

Do not reopen Arabic unless canonical Arabic content is deliberately changed.

## French — ACTIVE

Current canonical state:

- [x] A1 Unit 01 / sequences 1–6 preserved from calibration.
- [x] A1 Unit 02 / sequences 7–12 generated as one guarded batch.
- [x] A1 Unit 03 / sequences 13–18 generated as one guarded batch.
- [x] A1 Unit 04 / sequences 19–24 generated as one guarded batch.
- [ ] A1 Unit 05 / sequences 25–30.
- [ ] A1 Unit 06 / sequences 31–36.
- [ ] A1 Unit 07 / sequences 37–42.
- [ ] A1 Unit 08 / sequences 43–48.
- [ ] A1 Unit 09 / sequences 49–54.
- [ ] A1 Unit 10 / sequences 55–60.
- [ ] A2: 60 passages.
- [ ] B1: 60 passages.
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

French A1 current totals:

- 24 canonical passages;
- 240 questions;
- 240 linked answers;
- Units 02–04 added 30 validated lexical targets across P01–P05 cycles;
- every generated P06 checkpoint has zero deliberately new lexical targets;
- generated passages are guarded to the A1 90–140-word planning band;
- question target IDs must be locally declared as new/review vocabulary;
- each generator verifies source ranks against `french_top1000.csv` and fails on canonical source-blob drift.

### Next French production batch

- [ ] Verify live `main` and the current French A1 canonical blob.
- [ ] Select Unit 05 targets from the validated French lexical source, excluding already scheduled IDs.
- [ ] Generate sequences 25–30 as one complete unit-sized batch.
- [ ] Keep P30 / Unit 05 P06 zero-new-target.
- [ ] Enforce schema, word band, lexical-source identity, question-answer linkage, local question-target declaration, sequence continuity, and collision guards.
- [ ] Continue in large guarded unit batches to A1=60.

Production policy:

- generation-first, full multi-pass audit at corpus completion;
- lightweight structural/source/linkage validation during generation;
- do not translate Arabic passages into French;
- use natural contemporary French and independent French lexical/grammar progression.

## Urdu — QUEUED

Live starting state:

- [x] A1 sequences 1–6 exist in `reading/urdu/a1/passages.jsonl`.
- [x] `reading/urdu/a1/calibration/` exists.
- [ ] A1 sequences 7–60.
- [ ] A2–C2: 60 passages each.

Keep Urdu unchanged while French is active unless explicitly reprioritized.

## Throughput rules

- Work in coherent unit/batch scopes, not passage-by-passage workflows.
- One collision check + one guarded script + one relevant validation run per batch.
- Rerun only checks affected by the fields changed.
- Full multi-pass audit is a final-stage operation, not a per-generation-batch tax.
- Fail closed on source drift or invariant failure, then fix the same batch script unless the issue truly requires separate adjudication.
- Serialize writers to the same canonical/audit artifact.

## Reader integration / telemetry

After the language corpus work reaches the appropriate stable state:

- [ ] confirm reader import contract;
- [ ] keep JSONL canonical regardless of export format;
- [ ] create adapters as needed;
- [ ] preserve passage → questions → reveal ordering;
- [ ] integrate timing/comprehension telemetry where available;
- [ ] never count speed gains below the comprehension gate.

## Immediate next task

**Generate French A1 Unit 05 as sequences 25–30 from the live 24-passage corpus. Do not regenerate or overwrite sequences 1–24.**
