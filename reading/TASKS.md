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

### A1 — GENERATED / CLOSED TO ROUTINE REGENERATION

- [x] Unit 01 / sequences 1–6 preserved from calibration.
- [x] Unit 02 / sequences 7–12 generated as one guarded batch.
- [x] Unit 03 / sequences 13–18 generated as one guarded batch.
- [x] Unit 04 / sequences 19–24 generated as one guarded batch.
- [x] Unit 05 / sequences 25–30 generated as one guarded batch.
- [x] Unit 06 / sequences 31–36 generated as one guarded batch; exact-form review failure repaired without weakening the visibility guard.
- [x] Unit 07 / sequences 37–42 generated as one guarded batch; validated lemma/surface-form issue resolved before canonical write.
- [x] Unit 08 / sequences 43–48 generated as one guarded batch.
- [x] Unit 09 / sequences 49–54 generated as one guarded batch.
- [x] Unit 10 / sequences 55–60 generated as one guarded batch; unsupported `pluie`/`manteau` targets were rejected by the source guard and replaced by validated `ciel`/`sac` before the successful retry.

French A1 generated totals:

- 60 canonical passages;
- 600 questions;
- 600 linked answers;
- 10 complete six-passage units;
- each Unit P06 checkpoint has zero deliberately new lexical targets;
- generated passages preserve source-rank identity, local target declaration, question-answer linkage, sequence/ID continuity, and collision guards;
- A1 generated units use the 90–140-word planning band;
- A1 is generated but **not yet the final audited/approved French language corpus**; the expensive multi-pass review remains deferred under generation-first policy.

### A2 — NEXT

- [ ] Verify live `main`, whether `reading/french/a2/passages.jsonl` exists, and the exact A2 starting state.
- [ ] Confirm A2 planning constraints from the roadmap/standards before writing.
- [ ] Generate A2 Unit 01 / sequences 1–6 as one guarded batch.
- [ ] Use natural contemporary French and independently designed A2 scenarios; do not translate Arabic passages or recycle A1 passages mechanically.
- [ ] Schedule bridge/review material from A1 where pedagogically useful while keeping all question target IDs locally declared.
- [ ] Keep Unit P06 zero-new-target and timed-reading friendly.
- [ ] Continue A2 in coherent guarded unit batches to 60 passages.

Remaining French levels:

- [ ] A2: 60 passages.
- [ ] B1: 60 passages.
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

Production policy:

- generation-first, full multi-pass audit at completed French corpus milestone;
- lightweight structural/source/linkage validation during generation;
- fail closed on lexical-source drift, canonical blob drift, schema failure, linkage failure, invisible deliberate review, or sequence collision;
- do not mutate the root validated lexical CSV merely to simplify passage production.

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

**Begin French A2 Unit 01 / sequences 1–6 from the verified live A2 starting state. Do not reopen or regenerate French A1.**
