# Agent Handoff — Graded Reading Curriculum

**Purpose:** resume the Arabic/French/Urdu graded-reading project from live repository state without replaying old chat history or restarting completed phases.

## 1. Read order and precedence

Read `reading/STATUS.json`, then this handoff, generation policy, ten-question standard, schema, durable reading standard, roadmap, and `reading/TASKS.md`.

Current-state precedence:

**live canonical JSONL > fresh audit artifacts > STATUS > handoff/current policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## 2. Arabic — CLOSED / APPROVED

Arabic A1–C2 is complete and formally approved: 360 canonical passages, 3,600 questions, 3,600 linked answers, final Pass 12 `PASS`, formal final approval `true`, and zero current hard regressions/final-approval blockers.

Final evidence: `reading/audit/final_arabic_pass12_adversarial_gate_falsification.json`.

**Do not reopen Arabic unless canonical Arabic data is deliberately changed.**

## 3. French A1 — GENERATED / INTEGRITY PASS

French A1 is complete at 60 passages / 600 questions / 600 answers.

- canonical file: `reading/french/a1/passages.jsonl`;
- accepted blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`;
- generation-integrity closeout: `PASS` at `reading/audit/french_a1_generation_integrity.json`;
- 100 deliberate targets;
- all Unit P06 checkpoints have zero deliberately new targets.

A1 is closed to routine regeneration but has not yet gone through the final language-wide French multi-pass approval audit.

## 4. French A2 — GENERATED / INTEGRITY PASS

French A2 is complete at 60 passages / 600 questions / 600 answers.

- canonical file: `reading/french/a2/passages.jsonl`;
- accepted blob: `d0a80b8866071f426019aa0ad143e1d270dba4de`;
- canonical completion commit: `b529f730e743e3a3b077750f31be31632b8b9afc`;
- generation-integrity closeout: `PASS` at `reading/audit/french_a2_generation_integrity.json`;
- 100 unique deliberate A2 targets;
- zero A1↔A2 deliberate-target collisions by validated source ID or visible form;
- all 10 Unit P06 checkpoints have zero deliberately new targets.

Important later-unit target history:

- Unit 06: `voyage`, `train`, `route`, `départ`, `hôtel`, `chambre`, `retour`, `visite`, `plan`, `avion`.
- Unit 07: `tenter`, `tranquille`, `déjeuner`, `partager`, `vue`, `avancer`, `marché`, `poste`, `intérêt`, `mur`.
- Unit 08: `étrange`, `répéter`, `appartenir`, `signe`, `plusieurs`, `compagnie`, `douter`, `test`, `but`, `parole`.
- Unit 09: `excuse`, `surprise`, `bruit`, `fonctionner`, `moitié`, `rater`, `cerveau`, `respirer`, `chacun`, `pourtant`.
- Unit 10: `habiter`, `milieu`, `cuisine`, `fenêtre`, `vidéo`, `caméra`, `retenir`, `image`, `proposer`, `gérer`.

Guard history worth preserving:

- Unit 04 failed closed on invisible exact `perdre`; repaired naturally without weakening the guard.
- Unit 06 rejected duplicate candidate `place`; replaced with fresh `visite`.
- Unit 07 rejected duplicate candidate `gauche`; replaced with fresh `tenter`.
- Unit 08 failed closed on checkpoint exact-form `douter`; repaired with an exact infinitive occurrence.
- Unit 09 failed closed on an invalid grammar-role enum; metadata role was corrected to schema-approved `review`, lexical content unchanged.
- Unit 10 passed first run.

Do not broadly regenerate A2. The final expensive French multi-pass approval audit remains deferred until French A1–C2 generation is complete.

## 5. French B1 — IMMEDIATE FRONTIER

No canonical B1 passages are accepted yet. Start with **B1 Unit 01 / sequences 1–6 as a calibration unit**.

B1 production profile from the durable standard/roadmap:

- standard length band: **220–350 words**;
- new lexical planning range: **3–6 types per standard passage**, a ceiling/range rather than a quota;
- connected narratives/explanations and clearer paragraph structure;
- paragraph-level main ideas and multi-sentence inference;
- motives, decisions, consequences and summaries;
- grammar review increasingly embedded rather than announced;
- move due vocabulary across related but non-identical topics/genres;
- 10 questions + 10 linked answers per canonical passage under the project-wide ten-question override;
- P06 checkpoint has zero deliberately new lexical targets and should be high-coverage/timed-reading friendly.

### B1 Unit 01 guard requirements

1. verify live `main`, confirm `reading/french/b1/passages.jsonl` state, and ensure no parallel writer has claimed Unit 01;
2. check every proposed new B1 target against **all deliberate French A1 + A2 new targets** before canonical write;
3. preserve validated `french_top1000.csv` source rank/ID identity and exact source-state locks;
4. make every deliberate running-text/summary review exactly visible;
5. validate schema, 220–350 word band, immutable IDs/sequences, local question-target declarations and one-to-one answer linkage;
6. keep contextual introductions inferable rather than dictionary-like;
7. include B1-appropriate question demand: multi-sentence inference, motive/reason, summary and grammar-in-context where natural;
8. keep P06 zero-new; fail closed on any collision or drift;
9. treat this first B1 unit as calibration: inspect the generated unit before scaling later B1 units.

## 6. Immediate next action

**Generate and validate French B1 Unit 01 / sequences 1–6 as one guarded calibration batch, fresh against all completed A1+A2 deliberate targets.**

## 7. Urdu — QUEUED

Urdu remains unchanged at six A1 calibration passages. Keep it paused while French is active unless explicitly reprioritized.

## 8. Throughput / parallel-agent rules

- use coherent six-passage unit batches, not passage-by-passage workflows;
- verify live main before each write batch;
- prefer non-overlapping units/files across chats;
- source-state assertions are required for large mutations;
- serialize workflows writing the same canonical artifact;
- fix failed guards rather than weakening them;
- do not rely on recursive `GITHUB_TOKEN` workflow triggers;
- update STATUS/TASKS/handoff at meaningful milestones, not after every passage.

## 9. Core pedagogical non-negotiables

- canonical data: `reading/<language>/<level>/passages.jsonl`;
- passage → all questions → answers/reveal;
- 10 questions / 10 linked answers per canonical passage;
- infer → verify → transfer plus spaced review;
- root validated lexical CSV remains read-only curriculum input;
- frequency rank is not a CEFR label;
- final approval is fail-closed and cannot be obtained by editing status fields.
