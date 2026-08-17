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
- [x] Generation-integrity artifact: `reading/audit/french_a1_generation_integrity.json` = `PASS`.
- [x] Canonical blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`.

### A2 — GENERATED / GENERATION-INTEGRITY PASS

- [x] Units 01–10 / sequences 1–60 generated.
- [x] 60 passages / 600 questions / 600 linked answers.
- [x] 100 unique deliberate targets; zero A1↔A2 deliberate-target collisions.
- [x] Generation-integrity artifact: `reading/audit/french_a2_generation_integrity.json` = `PASS`.
- [x] Canonical blob: `d0a80b8866071f426019aa0ad143e1d270dba4de`.

A1 and A2 remain closed to broad regeneration until the final French language-wide audit.

### B1 — ACTIVE

#### Unit 01 — ACCEPTED CALIBRATION

- [x] Sequences 1–6; 6 passages / 60 Q / 60 A.
- [x] 15 fresh targets, 3 in P01–P05; P06 zero new.
- [x] Post-calibration precision review PASS: `reading/audit/french_b1_unit01_calibration_review.json`.
- [x] Accepted calibration blob: `beed8c8337be567325a4b329b79c7d070511f3b1`.

Targets: `poursuivre`, `époque`, `trace`, `convaincre`, `position`, `impliquer`, `machine`, `code`, `recommencer`, `étranger`, `peuple`, `futur`, `regretter`, `profiter`, `ennui`.

#### Unit 02 — COMPLETE

- [x] Sequences 7–12; 6 passages / 60 Q / 60 A.
- [x] 15 fresh targets; P06 zero new.
- [x] Generator bracket typo failed before canonical mutation and was narrowly repaired.
- [x] Checkpoint stale prior-unit target tag was removed rather than expanding P06’s declarations.

Targets: `apparemment`, `détail`, `honnête`, `ordinateur`, `installer`, `remplir`, `planète`, `attirer`, `durer`, `coûter`, `respecter`, `inutile`, `admettre`, `mensonge`, `conversation`.

#### Unit 03 — COMPLETE

- [x] Sequences 13–18; 6 passages / 60 Q / 60 A.
- [x] 15 fresh targets; P06 zero new.
- [x] Candidate `existence` failed closed because it is absent from the validated deck; replaced by fresh source-backed `rôle` (rank 932).
- [x] P02/P06 were expanded naturally to satisfy the unchanged 220–350 B1 word band.
- [x] Canonical completion commit: `551d44b649486495ce47fcfdc0d5569c8bc61c2f`.
- [x] Current B1 blob: `8dfb17e274d33227c356b16bad00624f3779342f`.

Targets: `zone`, `séparer`, `morceau`, `causer`, `rapide`, `agir`, `espoir`, `oser`, `liberté`, `nourriture`, `accompagner`, `sonner`, `art`, `paix`, `rôle`.

#### Unit 04 — IMMEDIATE NEXT

- [ ] Generate sequences 19–24 against B1 blob `8dfb17e274d33227c356b16bad00624f3779342f`.
- [ ] Use calibrated default: 3 fresh deliberate lexical targets in each P01–P05; P06 zero new.
- [ ] Check every new target against all deliberate French A1+A2+B1 Units01–03 targets before canonical write.
- [ ] Naturally review Unit03 targets across P01–P05 with exact visible forms.
- [ ] Keep every passage in the 220–350-word B1 band.
- [ ] Use 10 questions + 10 linked answers per passage.
- [ ] Preserve paragraph-level inference, motive/reason, summary, grammar-in-context, and cross-domain transfer.
- [ ] Fail closed on blob/source drift, source identity, duplication, schema/linkage, review visibility, word band, or sequence collision.

Remaining French after Unit03:

- [ ] B1: 42 passages.
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

Production policy:

- generation-first; final multi-pass French audit remains deferred until A1–C2 generation is complete;
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
- Verify live canonical/source locks before each batch.
- Full multi-pass audit is a final-stage operation, not a per-generation-batch tax.
- Fail closed and repair the same batch instead of weakening invariants.
- Serialize writers to the same canonical artifact.

## Immediate next task

**Generate French B1 Unit 04 / sequences 19–24 against canonical B1 blob `8dfb17e274d33227c356b16bad00624f3779342f`. Keep Arabic sealed.**
