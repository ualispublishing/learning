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

## 8. IMMEDIATE FRONTIER — B2 Unit 04

Canonical topic-matrix theme: **cities and design**. Genres: **report / proposal / critique**.

Generate sequences **19–24** against exact B2 blob `e97d0929a5ea7aa09a7306a82f9159194ff954da`. Require the Unit03 lock before target selection or append; use the accepted four-target default in P01–P05 and zero new in P06; preserve source freshness/rank identity, exact reviews, 350–550 words, 10 linked Q/A, and B2 report/proposal/critique reasoning with urban-design trade-offs, stakeholders, assumptions, counterargument, position and synthesis. Fail closed and repair rather than weaken guards.

## 9. Urdu — QUEUED

Urdu remains unchanged at six A1 calibration passages. Keep it paused while French is active unless explicitly reprioritized.

## 10. Throughput / parallel rules

- coherent six-passage units;
- verify live main before each write batch;
- source-state assertions required;
- serialize workflows writing the same canonical artifact;
- fix failed guards rather than weakening them;
- do not rely on recursive `GITHUB_TOKEN` workflow triggers;
- update STATUS/TASKS/handoff at meaningful milestones;
- final French multi-pass approval audit remains deferred until A1–C2 generation is complete.

## 11. Core non-negotiables

- canonical data: `reading/<language>/<level>/passages.jsonl`;
- passage → all questions → answers/reveal;
- 10 questions / 10 linked answers per passage;
- infer → verify → transfer plus spaced review;
- validated root lexical CSV remains read-only;
- frequency rank is not a CEFR label;
- final approval is fail-closed and cannot be obtained by editing status fields.
