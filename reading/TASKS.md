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
- [x] Pass 12 strengthened and run last.
- [x] Pass 12 `PASS`, zero hard regressions, zero final-approval blockers.
- [x] Arabic formal final approval = `true`.
- [x] Final question-target linkage adversarial cleanup: zero undeclared question-target links.

Final Arabic evidence:
`reading/audit/final_arabic_pass12_adversarial_gate_falsification.json`

Do not reopen Arabic unless canonical Arabic content is deliberately changed.

### Arabic coverage note

- [x] Unmeasured zero placeholders are not treated as measured 0%.
- [ ] A real known-token coverage implementation remains optional future infrastructure; build it only from a defensible curriculum-known/morphology model. It is not an unresolved Arabic approval blocker.

## French — ACTIVE

Live starting state:

- [x] A1 sequences 1–6 exist in `reading/french/a1/passages.jsonl`.
- [x] `reading/french/a1/CALIBRATION_UNIT_01.md` exists.
- [ ] A1 sequences 7–60 (54 passages remaining).
- [ ] A2: 60 passages.
- [ ] B1: 60 passages.
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

### First French production batch

- [ ] Verify live `main` before the batch.
- [ ] Read the six existing A1 passages and calibration note; preserve them as the starting state.
- [ ] Inspect French validated lexical sources and any existing French exposure/coverage ledgers required for source identity.
- [ ] Build the continuation schedule from sequence 7; do not restart calibration or overwrite sequences 1–6.
- [ ] Generate the next complete A1 unit-sized batch with 10 questions + 10 linked answers per passage.
- [ ] Guard IDs, sequences, word counts, lexical scheduling, question-answer linkage, and source target identity.
- [ ] Continue in large guarded batches to A1=60.

Production policy:

- generation-first, full audit at corpus completion;
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

**Read the six live French A1 passages + calibration/source context once, then generate French A1 starting at sequence 7 in a large guarded unit batch.**
