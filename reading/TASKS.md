# Reading Curriculum Task List

This is the **active operational queue**. Historical calibration/review work belongs in git history and audit artifacts; do not infer current state from old unchecked items.

## Arabic — COMPLETE / APPROVED

- [x] A1–C2: 360 passages / 3,600 questions / 3,600 linked answers.
- [x] Final Arabic review through Pass 12 = `PASS`; formal final approval = `true`.
- [x] Zero current final-approval blockers.

Do not reopen Arabic unless canonical Arabic content is deliberately changed.

## French — ACTIVE

### A1 — GENERATED / GENERATION-INTEGRITY PASS

- [x] Units 01–10 / sequences 1–60 generated.
- [x] 60 passages / 600 questions / 600 linked answers.
- [x] 100 deliberate lexical targets.
- [x] Every Unit P06 checkpoint has zero deliberately new lexical targets.
- [x] Generation-integrity artifact: `reading/audit/french_a1_generation_integrity.json` = `PASS`.
- [x] Canonical blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`.

### A2 — GENERATED / GENERATION-INTEGRITY PASS

- [x] Units 01–10 / sequences 1–60 generated.
- [x] 60 passages / 600 questions / 600 linked answers.
- [x] 100 unique deliberate lexical targets; zero A1↔A2 deliberate-target collisions.
- [x] Every Unit P06 checkpoint has zero deliberately new lexical targets.
- [x] Generation-integrity artifact: `reading/audit/french_a2_generation_integrity.json` = `PASS`.
- [x] Canonical blob: `d0a80b8866071f426019aa0ad143e1d270dba4de`.

A1 and A2 have not yet gone through the final language-wide multi-pass French approval audit; do not broadly regenerate them.

### B1 — ACTIVE

#### Unit 01 — ACCEPTED CALIBRATION

- [x] Sequences 1–6 generated and guarded.
- [x] 6 passages / 60 questions / 60 linked answers.
- [x] 15 fresh deliberate targets, three each in P01–P05; P06 has zero new targets.
- [x] All passage lengths in B1 220–350 band: 246, 254, 250, 250, 276, 271.
- [x] Post-calibration precision review = `PASS`: `reading/audit/french_b1_unit01_calibration_review.json`.
- [x] Accepted canonical B1 blob after calibration repair: `beed8c8337be567325a4b329b79c7d070511f3b1`.
- [x] Calibration commit: `ccdf4743c5b359c085387dd66653f01d368e5c07`.
- [x] Root lexical CSV remained unchanged; `impliquer` was tightened to the directly supported entail/consequence sense rather than adding a sense override.

Unit 01 targets: `poursuivre`, `époque`, `trace`, `convaincre`, `position`, `impliquer`, `machine`, `code`, `recommencer`, `étranger`, `peuple`, `futur`, `regretter`, `profiter`, `ennui`.

#### Unit 02 — IMMEDIATE NEXT

- [ ] Generate sequences 7–12 as one guarded batch against B1 blob `beed8c8337be567325a4b329b79c7d070511f3b1`.
- [ ] Use the calibrated default of 3 new deliberate lexical types in each P01–P05; P06 zero new.
- [ ] Check every new target against all deliberate A1+A2+B1 Unit01 targets before canonical write.
- [ ] Keep every passage in the B1 220–350-word band.
- [ ] Use 10 questions + 10 linked answers per passage.
- [ ] Make deliberate reviews exactly visible; naturally distribute Unit01 reviews across P01–P05.
- [ ] Preserve B1 demand: paragraph-level main ideas, multi-sentence inference, motive/reason, summary, grammar-in-context, and transfer across related but non-identical genres.
- [ ] Fail closed on source/blob drift, source identity, cross-level duplication, schema/linkage errors, exact review visibility, word band, or sequence collision.

Remaining French after accepted B1 Unit01:

- [ ] B1: 54 passages.
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

Production policy:

- generation-first; full multi-pass French audit remains deferred until completed French A1–C2 generation;
- standard bands: B1 220–350, B2 350–550, C1 500–800, C2 700–1,200 words;
- root validated lexical CSV remains read-only;
- fix failed guards rather than weakening them.

## Urdu — QUEUED

- [x] A1 sequences 1–6 exist in `reading/urdu/a1/passages.jsonl`.
- [ ] A1 sequences 7–60.
- [ ] A2–C2: 60 passages each.

Keep Urdu unchanged while French is active unless explicitly reprioritized.

## Throughput rules

- Work in coherent unit/batch scopes, not passage-by-passage workflows.
- One live-state/collision check + one guarded script + one relevant validation run per batch.
- Full multi-pass audit is a final-stage operation, not a per-generation-batch tax.
- Fail closed on source drift or invariant failure, then repair the same batch rather than weakening the guard.
- Serialize writers to the same canonical/audit artifact.

## Immediate next task

**Generate French B1 Unit 02 / sequences 7–12 against canonical B1 blob `beed8c8337be567325a4b329b79c7d070511f3b1`. Keep Arabic sealed.**
