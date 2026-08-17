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

- [x] Unit 01 / sequences 1–6 — accepted calibration; 15 fresh targets; P06 zero new; post-calibration audit PASS.
- [x] Unit 02 / sequences 7–12 — complete; 15 fresh targets; P06 zero new.
- [x] Unit 03 / sequences 13–18 — complete; 15 fresh targets; P06 zero new.
- [x] Unit 04 / sequences 19–24 — complete; 15 fresh targets; P06 zero new.
- [x] Unit 05 / sequences 25–30 — complete; 15 fresh targets; P06 zero new.
- [x] Current B1: 30 passages / 300 questions / 300 linked answers.
- [x] Current B1 blob: `dfd2b675884c9481906ce6b5bbba263f6c95b063`.
- [x] Current B1 canonical commit: `52d6156746db740f7926ae58a61756ef401a7587`.

Unit 04 targets: `probablement`, `prouver`, `sérieux`, `scène`, `spécial`, `créer`, `rejoindre`, `ligne`, `bout`, `normal`, `système`, `prévenir`, `relation`, `reconnaître`, `plutôt`.

Unit 05 targets: `clair`, `reprendre`, `déranger`, `empêcher`, `récupérer`, `sinon`, `ancien`, `vivant`, `honneur`, `inviter`, `remercier`, `mériter`, `liste`, `réaliser`, `arranger`.

Recent guard history:
- Unit 04 rejected prior deliberate `recherche`, `voix`, `présent`; fresh replacements were `sérieux`, `spécial`, `plutôt`.
- Unit 04 also repaired invalid domain `cultural`, short passage/checkpoint lengths, and exact checkpoint review `sérieux` without weakening guards.
- Unit 05 rejected prior deliberate `prix` and replaced it with fresh `liste`.
- Unit 05 exact-form `mériter`, review `normal`, and checkpoint `clair`/`mériter` mismatches were repaired naturally before canonical write.

#### Unit 06 — IMMEDIATE NEXT

- [ ] Generate sequences 31–36 against B1 blob `dfd2b675884c9481906ce6b5bbba263f6c95b063`.
- [ ] Use calibrated default: 3 fresh deliberate lexical targets in each P01–P05; P06 zero new.
- [ ] Check every new target against all deliberate French A1+A2+B1 Units01–05 targets before canonical write.
- [ ] Naturally review Unit05 targets across P01–P05 with exact visible forms.
- [ ] Keep every passage in the 220–350-word B1 band.
- [ ] Use 10 questions + 10 linked answers per passage.
- [ ] Preserve paragraph-level inference, motive/reason, summary, grammar-in-context, and cross-domain transfer.
- [ ] Fail closed on blob/source drift, source identity, duplication, schema/linkage, review visibility, word band, or sequence collision.

Remaining after Unit05:
- [ ] B1: 30 passages.
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

**Generate French B1 Unit 06 / sequences 31–36 against canonical B1 blob `dfd2b675884c9481906ce6b5bbba263f6c95b063`. Keep Arabic sealed.**
