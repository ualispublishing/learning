# Agent Handoff — Graded Reading Curriculum

**Purpose:** resume the Arabic/French/Urdu graded-reading project from live repository state without replaying old chat history or restarting completed phases.

## 1. Precedence

Read `reading/STATUS.json`, then this handoff, generation policy, ten-question standard, schema, durable reading standard, roadmap/topic matrix, and `reading/TASKS.md`.

**live canonical JSONL > fresh audit artifacts > STATUS > handoff/current policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## 2. Arabic — CLOSED / APPROVED

Arabic A1–C2 is complete and formally approved: 360 canonical passages, 3,600 questions, 3,600 linked answers, final Pass 12 `PASS`, formal final approval `true`, zero current blockers.

**Do not reopen Arabic unless canonical Arabic data is deliberately changed.**

## 3. French A1–B1 — GENERATED / GENERATION-INTEGRITY PASS

Do not broadly regenerate these levels. Final expensive language-wide French approval remains deferred until French A1–C2 generation is complete.

- A1: 60 passages / 600 Q / 600 A; blob `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`; integrity PASS.
- A2: 60 passages / 600 Q / 600 A; blob `d0a80b8866071f426019aa0ad143e1d270dba4de`; 100 unique targets; zero A1↔A2 collisions; integrity PASS.
- B1: 60 passages / 600 Q / 600 A; blob `4a2cd9ff30c3cea58caf20fca2822b06200622ca`; 150 unique targets; zero earlier-level collisions; integrity PASS at `reading/audit/french_b1_generation_integrity.json`.

## 4. French B2 — ACCEPTED PRODUCTION PROFILE

Canonical file: `reading/french/b2/passages.jsonl`.

Durable standards:
- standard length band **350–550 words**;
- durable lexical planning range **4–8 new types per standard passage**;
- after Unit 01 post-calibration review, **accepted default = 4 fresh targets per P01–P05**, not a hard quota; P06 zero new;
- 10 questions + 10 linked answers per passage;
- regular topic/genre/perspective/semantic variation;
- stronger B2 demand: argument/counterargument, author position and scope, denser cohesion/reference, technical discussion with support, paired viewpoints, abstract vocabulary nuance, cross-text synthesis;
- validated root lexical CSV is read-only;
- all new targets fresh against every prior deliberate French target, source-backed with exact rank/ID/intended sense;
- deliberate running-text/summary reviews exact-form visible;
- fail closed on blob/source drift, collisions, schema/linkage, word band, review visibility, or IDs/sequences.

## 5. B2 Unit 01 — ACCEPTED CALIBRATION

Theme: **science and society**. Sequences 1–6.

- 6 passages / 60 questions / 60 linked answers;
- 20 fresh targets, 4 in each P01–P05; P06 zero new;
- accepted canonical blob `1ba43c900ad64ff9359264e743470138ce25a9c5`;
- all passages 350–550 words; standard passage mean 387.2;
- P03/P04 paired viewpoint group `fr-b2-u01-citizen-science-access`, materially distinct;
- post-calibration artifact `reading/audit/french_b2_unit01_calibration_review.json` = PASS;
- calibration artifact commit `a784e4594b1bb487c51c882cf8b704c99331cd96`;
- language review PASS after narrow repair of P03/P04 phrasing and learner-facing `stance` → standard `position`;
- pedagogical review PASS for argument/counterargument, author position/scope, denser cohesion/reference, paired viewpoint transfer, abstract nuance and cross-text synthesis.

Unit 01 targets:
`supposer`, `cause`, `effet`, `preuve`, `sécurité`, `protéger`, `suffire`, `moyen`, `public`, `apporter`, `libre`, `accepter`, `tromper`, `certain`, `général`, `ressembler`, `apprécier`, `ainsi`, `valoir`, `intéresser`.

Guard history:
1. pre-generation read-only probe confirmed the 20-word pool was source-backed and fresh across all 350 prior deliberate French targets;
2. P04 exact target `général` initially appeared only as `générale`; repaired with `portrait général`;
3. a P05 assessment incorrectly tagged prior-passage target `apporter`; stale tag removed rather than broadening local declarations;
4. P02 B1 bridge reviews `dangereux`/`risquer` were only inflected; natural exact forms added;
5. P06 exact `général` repaired;
6. post-calibration language review replaced learner-facing Anglicism `stance` and polished two paired-viewpoint phrases.

## 6. B2 Unit 02 — COMPLETE / CURRENT LOCK

Theme used: **decision under uncertainty**. Sequences 7–12.

- 6 passages / 60 questions / 60 answers;
- 20 fresh deliberate targets, four in P01–P05; P06 zero new;
- canonical B2 blob after Unit02: `ff94113359f90b68032b2e2f92aaa1bf2b3ea923`;
- frontier lock artifact: `reading/audit/french_b2_unit02_frontier_lock.json` = PASS;
- Unit02 targets: `promettre`, `décider`, `attendre`, `confiance`, `grave`, `calmer`, `choisir`, `problème`, `maintenir`, `simplement`, `secret`, `surtout`, `ordre`, `lieu`, `doute`, `préférer`, `ramener`, `pareil`, `lumière`, `pousser`.

Guard repairs preserved rather than weakened freshness, local-linkage and exact-form checks.

## 7. B2 Unit 03 — COMPLETE / CURRENT LOCK

Theme: **ethics and competing values**. Genres: argument / case / response. Sequences 13–18.

- 6 passages / 60 questions / 60 answers;
- 20 fresh deliberate targets, four in P01–P05; P06 zero new;
- canonical B2 blob after Unit03: `e97d0929a5ea7aa09a7306a82f9159194ff954da`;
- frontier lock: `reading/audit/french_b2_unit03_frontier_lock.json` = PASS;
- Unit03 targets: `juste`, `chance`, `groupe`, `réussir`, `permettre`, `refuser`, `accord`, `obliger`, `vérité`, `vrai`, `faux`, `mentir`, `victime`, `dommage`, `aider`, `difficile`, `garder`, `donner`, `loi`, `guerre`.

## 8. B2 Unit 04 — COMPLETE / CURRENT LOCK

Theme: **cities and design**. Genres: report / proposal / critique. Sequences 19–24.

- 6 passages / 60 questions / 60 answers;
- 20 fresh targets, four in P01–P05; P06 zero new;
- canonical B2 blob `125d8c87641ee5a0fbd958a415ede82f95c40eff`;
- frontier lock `reading/audit/french_b2_unit04_frontier_lock.json` = PASS;
- Unit04 targets: `coin`, `côté`, `arbre`, `air`, `voiture`, `proche`, `besoin`, `simple`, `construire`, `ouvrir`, `fermer`, `utiliser`, `haut`, `bas`, `monter`, `descendre`, `entrer`, `sortir`, `servir`, `nouveau`.

## 9. B2 Unit 05 — COMPLETE / CURRENT LOCK

Theme: **climate and uncertainty**. Genres: evidence summary / news analysis / argument. Sequences 25–30.

- 6 passages / 60 questions / 60 answers;
- 20 fresh targets, four in P01–P05; P06 zero new;
- canonical B2 blob `bada023bdbbe9830ec324ed5924862d5b153e214`;
- frontier lock `reading/audit/french_b2_unit05_frontier_lock.json` = PASS;
- Unit05 targets: `été`, `année`, `mois`, `nuit`, `passé`, `long`, `changer`, `continuer`, `rester`, `devenir`, `compter`, `montrer`, `croire`, `penser`, `sembler`, `comprendre`, `préparer`, `action`, `mer`, `terre`.

Guard history: repaired one non-local assessment tag, exact-form visibility (`proche`, `long`), two learner-facing participle/adjective issues, checkpoint length, and exact checkpoint review `long`; guards were preserved rather than weakened.

## 10. B2 Unit 06 — COMPLETE / CURRENT LOCK

Theme: **digital life and privacy**. Genres: analysis / policy-style summary / paired opinions. Sequences 31–36.

- 6 passages / 60 questions / 60 answers;
- 20 fresh targets, four in P01–P05; P06 zero new;
- P03/P04 paired group `fr-b2-u06-data-control-opinions`;
- canonical B2 blob `939ec4d433c8b5a8893093eca6f8e8a90ff2c1d4`;
- frontier lock `reading/audit/french_b2_unit06_frontier_lock.json` = PASS;
- Unit06 targets: `téléphone`, `compte`, `message`, `adresse`, `photo`, `nom`, `visage`, `voix`, `contrôler`, `suivre`, `connaître`, `cacher`, `client`, `bureau`, `demander`, `répondre`, `vendre`, `chercher`, `trouver`, `monde`.

Guard history: checkpoint retained three stale Unit05 target tags; they were remapped to locally declared Unit06 concepts before canonicalization. No guard was weakened.

## 11. B2 Unit 07 — COMPLETE / CURRENT LOCK

Theme: **arts and interpretation**. Genres: review / profile / critical comparison. Sequences 37–42.

- 6 passages / 60 questions / 60 answers;
- 20 fresh targets, four in P01–P05; P06 zero new;
- canonical B2 blob `5ff899452326f679b7c16b0ff33d8f38fa99719a`;
- frontier lock `reading/audit/french_b2_unit07_frontier_lock.json` = PASS;
- Unit07 targets: `film`, `musique`, `chanson`, `jouer`, `histoire`, `lire`, `écrire`, `mot`, `ton`, `sens`, `sujet`, `imaginer`, `avis`, `aimer`, `beau`, `drôle`, `vie`, `présent`, `société`, `politique`.

Guard history: repaired one stale checkpoint tag, brought P03 into the B2 word band with substantive counterevidence logic, and exposed exact checkpoint lemma `beau`; no guard was weakened.

## 12. IMMEDIATE FRONTIER — B2 Unit 08

Canonical theme: **history and explanation**. Genres: **historical account / causal analysis / source comparison**. Generate sequences **43–48** against exact blob `5ff899452326f679b7c16b0ff33d8f38fa99719a`. Require the Unit07 lock; use four fresh targets by default in P01–P05 and zero new in P06; preserve source freshness/rank identity, exact reviews, 350–550 words, 10 linked Q/A, and B2 historical reasoning about chronology, causal chains, competing explanations, source perspective/comparison, counterargument, position and synthesis. Fail closed and repair rather than weakening guards.

## 13. Urdu — QUEUED

Urdu remains unchanged at six A1 calibration passages. Keep it paused while French is active unless explicitly reprioritized.

## 14. Throughput / parallel rules

- coherent six-passage units;
- verify live main before each write batch;
- source-state assertions required;
- serialize workflows writing the same canonical artifact;
- fix failed guards rather than weakening them;
- do not rely on recursive `GITHUB_TOKEN` workflow triggers;
- update STATUS/TASKS/handoff at meaningful milestones;
- final French multi-pass approval audit remains deferred until A1–C2 generation is complete.

## 15. Core non-negotiables

- canonical data: `reading/<language>/<level>/passages.jsonl`;
- passage → all questions → answers/reveal;
- 10 questions / 10 linked answers per passage;
- infer → verify → transfer plus spaced review;
- validated root lexical CSV remains read-only;
- frequency rank is not a CEFR label;
- final approval is fail-closed and cannot be obtained by editing status fields.


## French B2 — COMPLETE / GENERATION-INTEGRITY PASS

- Canonical B2 blob `38976211f13329ba3e2b0b9dbd6868699023d05d`.
- 60 passages / 600 questions / 600 answers.
- 200 unique B2 deliberate targets; zero prior-level collisions.
- checkpoints 6,12,18,24,30,36,42,48,54,60 are zero-new.
- artifact `reading/audit/french_b2_generation_integrity.json` = PASS.
- This is a generation seal, not the deferred final whole-French multi-pass audit.

### Immediate frontier — French C1 Unit 01 calibration

Read the canonical C1 passage standard and topic/genre matrix first. Derive the exact word band and production constraints; run an exhaustive freshness probe against all A1–B2 deliberate targets; choose a conservative calibration lexical load rather than copying B2 by assumption; generate sequences 1–6 with P06 zero-new and 10 linked Q/A; then run a strict post-calibration language/pedagogy/integrity review before setting the C1 production default.


## French C1 Unit 01 — CALIBRATION PASS / CURRENT LOCK

- Canonical C1 blob `6ca488f81788cefa49ef2e303bf6966cb4862a4c`.
- 6 passages / 60 questions / 60 answers.
- C1 word band `500–800`.
- 20 fresh Unit01 targets; P06 zero-new.
- strict review `reading/audit/french_c1_unit01_calibration_review.json` = PASS.
- frontier lock `reading/audit/french_c1_unit01_frontier_lock.json` = PASS.
- accepted conservative C1 default: `4` new targets per standard passage, not a hard quota.

### Immediate frontier — French C1 Unit 02

Theme: **professional judgment**. Genres: **["briefing", "case analysis", "recommendation"]**. Generate sequences 7–12 against exact C1 blob `6ca488f81788cefa49ef2e303bf6966cb4862a4c`. Use the calibrated default `4` fresh targets per P01–P05 unless canonical policy/discourse load supports more; P06 zero-new. Preserve `500–800` words, 10 linked Q/A, source identity/exposures, exact reviews, competing perspectives, scope, source-method critique, normative bridge, counterargument and revision conditions. Fail closed.


## French C1 Unit 02 — COMPLETE / CURRENT LOCK

- Canonical C1 blob `3dd6fc869920ed96cff6861d7498afe59e433947`.
- 12 total C1 passages / 120 questions / 120 answers.
- Unit02 strict review and frontier lock PASS.
- calibrated default remains `4` new targets per standard passage, not a hard quota.

### Immediate frontier — French C1 Unit 03
Theme: **institutions and incentives**. Genres: **["analysis", "commentary", "policy note"]**. Generate sequences 13–18 against `3dd6fc869920ed96cff6861d7498afe59e433947` with `500–800` words, 10 linked Q/A, exact source/review guards, P06 zero-new and full C1 reasoning requirements.


## French C1 Unit 03 — COMPLETE / CURRENT LOCK

- Canonical C1 blob `826de7eb5a241ca1c95d54281696abd65dbc22a4`; 18 C1 passages / 180 Q / 180 A.
- Unit03 strict review and frontier lock PASS.
- calibrated default remains `4`, not a hard quota.

### Immediate frontier — French C1 Unit 04
Theme: **language, identity, and society**. Genres: **["essay", "analysis", "paired viewpoints"]**. Generate sequences 19–24 against `826de7eb5a241ca1c95d54281696abd65dbc22a4` with `500–800` words, 10 linked Q/A, exact source/review guards and C1 reasoning requirements.


## French C1 Unit 04 — COMPLETE / CURRENT LOCK

- Canonical C1 blob `3631f63f3a6c0dc8a2640a6d43d8ef05df5dd9ef`; 24 C1 passages / 240 Q / 240 A.
- Unit04 strict review and frontier lock PASS.
- calibrated default remains `4`, not a hard quota.

### Immediate frontier — French C1 Unit 05
Theme: **scientific uncertainty and communication**. Genres: **["research summary", "journalistic analysis", "critique"]**. Generate sequences 25–30 against `3631f63f3a6c0dc8a2640a6d43d8ef05df5dd9ef` with `500–800` words, 10 linked Q/A, exact source/review guards and C1 reasoning requirements.


## French C1 Unit 05 — COMPLETE / CURRENT LOCK

- Canonical C1 blob `26c09727e67f88bc5fcaf17440ce145df48b4d4b`; 30 C1 passages / 300 Q / 300 A.
- Unit05 strict review and frontier lock PASS.
- calibrated default remains `4`, not a hard quota.

### Immediate frontier — French C1 Unit 06
Theme: **law, rights, and interpretation**. Genres: **["case-style explanation", "argument", "commentary"]**. Generate sequences 31–36 against `26c09727e67f88bc5fcaf17440ce145df48b4d4b` with `500–800` words, 10 linked Q/A, exact source/review guards and C1 reasoning requirements.


## French C1 Unit 06 — COMPLETE / CURRENT LOCK

- Canonical C1 blob `c3aee049cf6bdbdadf6639d132fcfc061481a3c9`; 36 C1 passages / 360 Q / 360 A.
- Unit06 strict review and frontier lock PASS.
- calibrated default remains `4`, not a hard quota.

### Immediate frontier — French C1 Unit 07
Theme: **literature and cultural criticism**. Genres: **["critical essay", "review", "close-reading style prose"]**. Generate sequences 37–42 against `c3aee049cf6bdbdadf6639d132fcfc061481a3c9` with `500–800` words, 10 linked Q/A, exact source/review guards and C1 reasoning requirements.


## French C1 Unit 07 — COMPLETE / CURRENT LOCK

- Canonical C1 blob `2a5671b611d15547af51c99e19242460757ee7c6`; 42 C1 passages / 420 Q / 420 A.
- Unit07 strict review and frontier lock PASS.
- calibrated default remains `4`, not a hard quota.

### Immediate frontier — French C1 Unit 08
Theme: **economics, risk, and forecasting**. Genres: **["analysis", "briefing", "scenario comparison"]**. Generate sequences 43–48 against `2a5671b611d15547af51c99e19242460757ee7c6` with `500–800` words, 10 linked Q/A, exact source/review guards and C1 reasoning requirements.


## French C1 Unit 08 — COMPLETE / CURRENT LOCK

- Canonical C1 blob `db848d9447849c178e6dae39f4474c905b974503`; 48 C1 passages / 480 Q / 480 A.
- Unit08 strict review and frontier lock PASS.
- calibrated default remains `4`, not a hard quota.

### Immediate frontier — French C1 Unit 09
Theme: **history, memory, and narrative**. Genres: **["historiographical essay", "source comparison", "reflection"]**. Generate sequences 49–54 against `db848d9447849c178e6dae39f4474c905b974503` with `500–800` words, 10 linked Q/A, exact source/review guards and C1 reasoning requirements.


## French C1 Unit 09 — COMPLETE / CURRENT LOCK

- Canonical C1 blob `76e43c57fdbd2f8e30c90263451ae2c23f50af55`; 54 C1 passages / 540 Q / 540 A.
- Unit09 strict review and frontier lock PASS.
- calibrated default remains `4`, not a hard quota.

### Immediate frontier — French C1 Unit 10
Theme: **C1 synthesis**. Genres: **["multi-section essay", "paired perspectives", "checkpoint"]**. Generate sequences 55–60 against `76e43c57fdbd2f8e30c90263451ae2c23f50af55` with `500–800` words, 10 linked Q/A, exact source/review guards and C1 reasoning requirements.


## French C1 — COMPLETE / GENERATION INTEGRITY LOCK
- 60 C1 passages / 600 Q / 600 A; canonical blob `6f5bd912dfb550c064b54c8f7de4027bebf3786d`.
- Full C1 generation-integrity artifact PASS with 200 unique new targets and ten zero-new checkpoints.
- This is not final French approval; final language-wide review waits for C2.

### Immediate frontier — French C2 Unit 01
Resolve C2 standards and exact matrix node from canonical policy, then calibrate against the sealed C1 blob. Prefer validated top-3000 continuation over leftover top-1000 grammar/interjection tokens.


### French C2 Unit 02 frontier
- Unit 01 sealed; canonical C2 blob `3ad7e1ec6219ac4d2d41b283f976beb219836ad1`.
- Next canonical matrix theme: **law and competing interpretations**; genres: dense analysis, case commentary, position comparison.
- Fresh rank-1001+ continuation terms: 1974.
- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.


### French C2 Unit 03 frontier
- Unit 02 sealed; canonical C2 blob `58ce1ad95c3ba4e738df93057d7b9a3867cbf4fe`.
- Next canonical matrix theme: **science, models, and epistemic limits**; genres: advanced synthesis, critique, research commentary.
- Fresh rank-1001+ continuation terms: 1949.
- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.


### French C2 Unit 04 frontier
- Unit 03 sealed; canonical C2 blob `21be6a87ceb638cb304fa341641f43825bf6d561`.
- Next canonical matrix theme: **economics and complex systems**; genres: analytical essay, scenario analysis, commentary.
- Fresh rank-1001+ continuation terms: 1924.
- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.


### French C2 Unit 05 frontier
- Unit 04 sealed; canonical C2 blob `b22101b5c1d1f6f9a60f95e1813a5ba53dfeeb60`.
- Next canonical matrix theme: **literary style and rhetoric**; genres: literary prose, critical analysis, rhetorical commentary.
- Fresh rank-1001+ continuation terms: 1899.
- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.


### French C2 Unit 06 frontier
- Unit 05 sealed; canonical C2 blob `7eeb53f2535cb72b420e120f4481e93ce6e7f0af`.
- Next canonical matrix theme: **political and institutional argument without partisan advocacy**; genres: comparative analysis, policy critique, argument reconstruction.
- Fresh rank-1001+ continuation terms: 1874.
- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.


### French C2 Unit 07 frontier
- Unit 06 sealed; canonical C2 blob `9fd04c6ad99c65b5691cea84bb29d1f2c39dcff2`.
- Next canonical matrix theme: **culture, translation, and interpretation**; genres: essay, comparative criticism, reflection.
- Fresh rank-1001+ continuation terms: 1849.
- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.


### French C2 Unit 08 frontier
- Unit 07 sealed; canonical C2 blob `5c543adbd136845d5bc181c9d0ce798de1ac0877`.
- Next canonical matrix theme: **history and contested explanation**; genres: historiographical comparison, source critique, synthesis.
- Fresh rank-1001+ continuation terms: 1824.
- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.


### French C2 Unit 09 frontier
- Unit 08 sealed; canonical C2 blob `8760174e524ab2da8652ad7ecb9130787f572a13`.
- Next canonical matrix theme: **technology, ethics, and future uncertainty**; genres: advanced analysis, scenario argument, critique.
- Fresh rank-1001+ continuation terms: 1799.
- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.
