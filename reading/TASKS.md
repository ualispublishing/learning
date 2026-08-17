# Reading Curriculum Task List

This is the **active operational queue**. Historical calibration/review work belongs in git history and audit artifacts; do not infer current state from old unchecked items.

## Arabic — COMPLETE / APPROVED

- [x] A1–C2: 360 passages / 3,600 questions / 3,600 linked answers.
- [x] Final Arabic review through Pass 12 = `PASS`; formal final approval = `true`.
- [x] Zero current final-approval blockers.

Do not reopen Arabic unless canonical Arabic content is deliberately changed.

## French — ACTIVE

### A1 — GENERATED / GENERATION-INTEGRITY PASS
- [x] 60 passages / 600 Q / 600 A.
- [x] Blob `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`.
- [x] `reading/audit/french_a1_generation_integrity.json` = PASS.

### A2 — GENERATED / GENERATION-INTEGRITY PASS
- [x] 60 passages / 600 Q / 600 A.
- [x] 100 unique deliberate targets; zero A1↔A2 collisions.
- [x] Blob `d0a80b8866071f426019aa0ad143e1d270dba4de`.
- [x] `reading/audit/french_a2_generation_integrity.json` = PASS.

### B1 — GENERATED / GENERATION-INTEGRITY PASS
- [x] Units 01–10 / sequences 1–60 complete.
- [x] 60 passages / 600 questions / 600 linked answers.
- [x] 150 unique deliberate new targets.
- [x] Zero A1/A2↔B1 target collisions by source ID or visible form.
- [x] Every unit P06 checkpoint has zero new targets.
- [x] Every passage in the 220–350 standard band and stored word counts exact.
- [x] Schema, local target declarations, answer linkage, source identity/exposure counts, and exact deliberate review visibility all PASS.
- [x] Canonical blob `4a2cd9ff30c3cea58caf20fca2822b06200622ca`.
- [x] Generation-integrity artifact `reading/audit/french_b1_generation_integrity.json` = PASS.
- [x] Integrity artifact commit `512dc86bf64dc14df7ffa3a77f323971bf320544`.

A1–B1 are generated/integrity-pass but have **not** yet received the final language-wide French approval audit. Do not broadly regenerate them.

### B2 — CALIBRATION / IMMEDIATE NEXT

Durable B2 profile:
- standard passage band: **350–550 words**;
- initial planning range: **4–8 new lexical types per standard passage**; use fewer when discourse/grammar load is high;
- regular variation in topic, genre, speaker perspective, and semantic environment;
- argument/counterargument, author stance, denser cohesion/reference, supported technical discussion, paired viewpoints, and abstract vocabulary nuance;
- 10 questions + 10 linked answers remains the project contract;
- P06 checkpoint should have zero deliberately new targets and be timed/high-coverage where appropriate.

#### Unit 01 — science and society
Roadmap genres: `popular science`, `analysis`, `paired viewpoints`.

- [ ] Verify no existing `reading/french/b2/passages.jsonl` canonical frontier before first write.
- [ ] Calibrate Unit 01 / sequences 1–6 before scaling B2.
- [ ] Choose a conservative load inside the 4–8 range (default candidate: 4 fresh targets per P01–P05) and inspect the resulting discourse density before treating it as the B2 production default.
- [ ] Check every proposed target against all deliberate French A1+A2+B1 targets before canonical creation.
- [ ] Use validated source rank/ID identity and exact target-form exposure; root CSV remains read-only.
- [ ] Use exact visible B1 bridge reviews where deliberately declared.
- [ ] Include stance, argument relation/counterargument, paragraph cohesion, inference, abstract vocabulary nuance, summary, and transfer questions where natural.
- [ ] Fail closed on source identity/freshness, schema/linkage, 350–550 word band, exact review visibility, or sequence/ID collision.
- [ ] After Unit 01 generation, run a stricter post-calibration review before scaling B2 Units 02–10.

Remaining French generation:
- [ ] B2: 60 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

Production policy:
- generation-first; final French multi-pass approval audit remains deferred until French A1–C2 generation is complete;
- root validated lexical CSV remains read-only;
- fix failed guards rather than weakening them.

## Urdu — QUEUED
- [x] A1 sequences 1–6 exist.
- [ ] A1 sequences 7–60.
- [ ] A2–C2: 60 passages each.

Keep Urdu unchanged while French is active unless explicitly reprioritized.

## Throughput rules
- Work in coherent six-passage unit scopes.
- Calibrate each new CEFR level before scaling it.
- Verify live canonical/source locks before each write batch.
- Full multi-pass audit is a final-stage operation, not a per-unit tax.
- Fail closed and repair the same batch instead of weakening invariants.
- Serialize writers to the same canonical artifact.

## Immediate next task

**Calibrate French B2 Unit 01 / sequences 1–6 for `science and society`, using the 350–550 word band and fresh all-prior-French lexical guards. Keep Arabic sealed.**
