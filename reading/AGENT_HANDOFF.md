# Agent Handoff — Graded Reading Curriculum

**Purpose:** resume the Arabic/French/Urdu graded-reading project from live repository state without replaying old chat history or restarting completed phases.

## 1. Precedence

Read `reading/STATUS.json`, then this handoff, generation policy, ten-question standard, schema, durable reading standard, roadmap/topic matrix, and `reading/TASKS.md`.

**live canonical JSONL > fresh audit artifacts > STATUS > handoff/current policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## 2. Arabic — CLOSED / APPROVED

Arabic A1–C2 is complete and formally approved: 360 canonical passages, 3,600 questions, 3,600 linked answers, final Pass 12 `PASS`, formal final approval `true`, zero current blockers.

**Do not reopen Arabic unless canonical Arabic data is deliberately changed.**

## 3. French A1–B1 — GENERATED / GENERATION-INTEGRITY PASS

Do not broadly regenerate these levels. Their final expensive language-wide French approval audit remains deferred until French A1–C2 generation is complete.

- A1: 60 passages / 600 Q / 600 A; blob `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`; `reading/audit/french_a1_generation_integrity.json` = PASS.
- A2: 60 passages / 600 Q / 600 A; blob `d0a80b8866071f426019aa0ad143e1d270dba4de`; 100 unique deliberate targets; zero A1↔A2 collisions; integrity PASS.
- B1: 60 passages / 600 Q / 600 A; blob `4a2cd9ff30c3cea58caf20fca2822b06200622ca`; 150 unique deliberate targets; zero A1/A2↔B1 collisions; all 10 P06 checkpoints zero new; integrity artifact `reading/audit/french_b1_generation_integrity.json` = PASS.
- B1 integrity artifact commit: `512dc86bf64dc14df7ffa3a77f323971bf320544`.

B1 integrity specifically revalidated schema, 220–350 band, stored word counts, 600 Q/A linkage, local target declarations, source rank/ID identity, stored new-target exposures, exact running-text/summary review visibility, target uniqueness, cross-level collisions, and checkpoint invariants.

## 4. French B2 durable profile

Canonical target path: `reading/french/b2/passages.jsonl`.

Before first write, verify that no B2 canonical file/frontier already exists.

Durable standards:
- standard length band: **350–550 words**;
- initial new lexical planning range: **4–8 types per standard passage**; use fewer when discourse/grammar load is high;
- 10 questions + 10 linked answers per passage remains the project contract;
- P06 checkpoint: zero deliberately new lexical targets, high coverage/timed-friendly where appropriate;
- regular variation in topic, genre, speaker perspective and semantic environment;
- stronger B2 demand: concrete + abstract topics, argument/counterargument, author stance, denser cohesion/reference, supported technical discussion, paired viewpoints, and abstract vocabulary nuance;
- grammar should systematically contrast structures with similar functions rather than merely lengthen B1 prose;
- root validated `french_top1000.csv` remains read-only curriculum input;
- new targets must be fresh against **all** prior deliberate French A1+A2+B1 targets and preserve source rank/ID/intended-sense discipline;
- deliberate running-text/summary reviews must be exact-form visible;
- fail closed on source identity/freshness, schema/linkage, word band, review visibility, or ID/sequence collision.

## 5. IMMEDIATE FRONTIER — B2 Unit 01 calibration

Roadmap source: `reading/planning/topic_genre_matrix.json`.

Unit 01 theme: **science and society**.
Genres: **popular science, analysis, paired viewpoints**.

Required approach:
1. verify live main and confirm `reading/french/b2/passages.jsonl` is absent/empty before the first canonical creation;
2. treat Unit 01 as a new-level calibration, not a scaled production batch;
3. use a conservative starting load inside the 4–8 durable planning range — **4 fresh targets per P01–P05 is the current calibration default**, subject to post-calibration inspection; P06 zero new;
4. check all 20 proposed B2 targets against every deliberate French A1+A2+B1 target before canonical write;
5. use contemporary standard French and modern learner senses from the validated lexical source;
6. deliberately bridge selected B1 vocabulary into new science/society contexts with exact visible review forms, but do not make B2 merely longer B1;
7. include argument relation, counterargument, stance, cohesion/reference, multi-sentence inference, abstract vocabulary nuance, summary and synthesis across the six passages;
8. include at least one meaningful paired-viewpoint structure in the unit, with `paired_text_group` when schema-compatible;
9. keep every standard passage in 350–550 words and 10 Q/A linkage exact;
10. after Unit 01 mechanically passes, run a stricter post-calibration review before accepting its load/style as the B2 production template;
11. fix failed guards rather than weakening them.

## 6. B2 Unit 01 suggested structure from durable cycle + roadmap

- P01 instructional popular-science explanation introducing four inferable targets in a science/society problem.
- P02 reinforcement/analysis, four fresh targets, with early P01 retrieval.
- P03 paired viewpoint A, four fresh targets, argument/stance focus.
- P04 paired viewpoint B/counterargument, four fresh targets, same `paired_text_group`, materially different reasoning rather than repetition.
- P05 integration, four fresh targets, reconcile evidence/trade-offs across viewpoints.
- P06 fluency/checkpoint, zero new targets, high-coverage synthesis and B2 stance/argument questions.

## 7. Urdu — QUEUED

Urdu remains unchanged at six A1 calibration passages. Keep it paused while French is active unless explicitly reprioritized.

## 8. Parallel/throughput rules

- coherent six-passage unit scopes;
- calibrate each new CEFR level before scaling;
- verify live main before each write batch;
- source-state assertions for large mutations;
- serialize workflows writing the same canonical artifact;
- do not rely on recursive `GITHUB_TOKEN` workflow triggers;
- update STATUS/TASKS/handoff at meaningful milestones;
- final language-wide French multi-pass audit remains deferred until A1–C2 generation is complete.

## 9. Core non-negotiables

- canonical data: `reading/<language>/<level>/passages.jsonl`;
- passage → all questions → answers/reveal;
- 10 questions / 10 linked answers per canonical passage;
- infer → verify → transfer plus spaced review;
- validated root lexical CSV remains read-only;
- frequency rank is not a CEFR label;
- final approval is fail-closed and cannot be obtained by editing status fields.
