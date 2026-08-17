# Reading Curriculum Task List

This is the **active operational queue**. Historical calibration/review work belongs in git history and audit artifacts; do not infer current state from old unchecked items.

## Arabic — COMPLETE / APPROVED

- [x] A1–C2: 360 passages / 3,600 questions / 3,600 linked answers.
- [x] Final Arabic review through Pass 12 = `PASS`; formal final approval = `true`.
- [x] Zero current final-approval blockers.

Do not reopen Arabic unless canonical Arabic content is deliberately changed.

## French — ACTIVE

### A1 — GENERATED / GENERATION-INTEGRITY PASS
- [x] 60 passages / 600 Q / 600 A; blob `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`.

### A2 — GENERATED / GENERATION-INTEGRITY PASS
- [x] 60 passages / 600 Q / 600 A; blob `d0a80b8866071f426019aa0ad143e1d270dba4de`.
- [x] 100 unique deliberate targets; zero A1↔A2 collisions.

### B1 — GENERATED / GENERATION-INTEGRITY PASS
- [x] 60 passages / 600 Q / 600 A; 150 unique deliberate targets.
- [x] Blob `4a2cd9ff30c3cea58caf20fca2822b06200622ca`.
- [x] `reading/audit/french_b1_generation_integrity.json` = PASS.

A1–B1 are generated/integrity-pass but not final language-wide French approved. Do not broadly regenerate them.

### B2 — ACTIVE

Durable profile:
- 350–550 words;
- 4–8 new lexical types per standard passage is the durable range;
- **accepted production default = 4** after Unit 01 calibration; this is not a hard quota;
- 10 questions + 10 linked answers;
- P06 zero new;
- regular genre/perspective variation, argument/counterargument, author position and scope, denser cohesion/reference, technical support, paired viewpoints, abstract vocabulary nuance;
- all new targets fresh against every prior deliberate French target and source-backed by validated rank/ID;
- exact visible deliberate reviews; fail closed on every structural or linguistic invariant.

#### Unit 01 — ACCEPTED CALIBRATION
- [x] Sequences 1–6 canonical.
- [x] 6 passages / 60 Q / 60 A.
- [x] 20 fresh targets, exactly 4 in P01–P05; P06 zero new.
- [x] All passages 350–550 words; standard-passage mean 387.2.
- [x] P03/P04 paired viewpoints materially distinct.
- [x] B2 question inventory includes main claim, argument relation, stance/author position, assumption, inference, reference resolution, cross-text synthesis, synthesis, and summary.
- [x] Narrow language repair completed: standardized P03/P04 phrasing and replaced learner-facing `stance` Anglicism with `position`.
- [x] Post-calibration review `reading/audit/french_b2_unit01_calibration_review.json` = PASS.
- [x] Accepted B2 blob `1ba43c900ad64ff9359264e743470138ce25a9c5`.
- [x] Calibration audit commit `a784e4594b1bb487c51c882cf8b704c99331cd96`.

Unit 01 targets: `supposer`, `cause`, `effet`, `preuve`, `sécurité`, `protéger`, `suffire`, `moyen`, `public`, `apporter`, `libre`, `accepter`, `tromper`, `certain`, `général`, `ressembler`, `apprécier`, `ainsi`, `valoir`, `intéresser`.

#### Unit 02 — COMPLETE
- [x] Sequences 7–12 canonical.
- [x] 6 passages / 60 Q / 60 A.
- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.
- [x] Theme used: `decision under uncertainty`.
- [x] Canonical B2 blob after Unit02: `ff94113359f90b68032b2e2f92aaa1bf2b3ea923`.
- [x] Frontier lock `reading/audit/french_b2_unit02_frontier_lock.json` = PASS.

Unit 02 targets: `promettre`, `décider`, `attendre`, `confiance`, `grave`, `calmer`, `choisir`, `problème`, `maintenir`, `simplement`, `secret`, `surtout`, `ordre`, `lieu`, `doute`, `préférer`, `ramener`, `pareil`, `lumière`, `pousser`.

#### Unit 03 — COMPLETE
- [x] Sequences 13–18 canonical.
- [x] 6 passages / 60 Q / 60 A.
- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.
- [x] Theme: `ethics and competing values`; genres: argument / case / response.
- [x] Canonical B2 blob after Unit03: `e97d0929a5ea7aa09a7306a82f9159194ff954da`.
- [x] Frontier lock `reading/audit/french_b2_unit03_frontier_lock.json` = PASS.

Unit 03 targets: `juste`, `chance`, `groupe`, `réussir`, `permettre`, `refuser`, `accord`, `obliger`, `vérité`, `vrai`, `faux`, `mentir`, `victime`, `dommage`, `aider`, `difficile`, `garder`, `donner`, `loi`, `guerre`.

#### Unit 04 — COMPLETE
- [x] Sequences 19–24 canonical.
- [x] 6 passages / 60 Q / 60 A.
- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.
- [x] Theme: `cities and design`; genres: report / proposal / critique.
- [x] Canonical B2 blob after Unit04: `125d8c87641ee5a0fbd958a415ede82f95c40eff`.
- [x] Frontier lock `reading/audit/french_b2_unit04_frontier_lock.json` = PASS.

Unit 04 targets: `coin`, `côté`, `arbre`, `air`, `voiture`, `proche`, `besoin`, `simple`, `construire`, `ouvrir`, `fermer`, `utiliser`, `haut`, `bas`, `monter`, `descendre`, `entrer`, `sortir`, `servir`, `nouveau`.

#### Unit 05 — IMMEDIATE NEXT
Canonical topic-matrix theme: **climate and uncertainty**. Genres: **evidence summary / news analysis / argument**.

- [ ] Generate sequences 25–30 against locked B2 blob `125d8c87641ee5a0fbd958a415ede82f95c40eff`.
- [ ] Accepted default 4 fresh targets per P01–P05; P06 zero new.
- [ ] Check every candidate against all prior deliberate French A1–B2 targets.
- [ ] Preserve 350–550 words, 10 linked Q/A, source identity, exact reviews and local target declarations.
- [ ] Require evidence-strength, uncertainty, competing explanations, probability/limitations, counterargument, author position and synthesis.
- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.

Remaining after Unit04:
- [ ] B2: 36 passages.
- [ ] C1: 60 passages.
- [ ] C2: 60 passages.

## Urdu — QUEUED
- [x] A1 sequences 1–6 exist.
- [ ] A1 sequences 7–60.
- [ ] A2–C2: 60 passages each.

Keep Urdu unchanged while French is active unless explicitly reprioritized.

## Throughput rules
- coherent six-passage units;
- accepted B2 calibration may now scale with the same guard profile;
- verify live canonical/source locks before every batch;
- final multi-pass French audit stays deferred until A1–C2 generation is complete;
- fix failed guards rather than weakening them;
- serialize writers to the same canonical artifact.

## Immediate next task

**Generate French B2 Unit 05 / sequences 25–30 for `climate and uncertainty` against blob `125d8c87641ee5a0fbd958a415ede82f95c40eff`. Keep Arabic sealed.**
