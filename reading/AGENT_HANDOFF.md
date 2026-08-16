# Agent Handoff — Graded Reading Curriculum

**Purpose:** resume the Arabic/French/Urdu graded-reading project from live repository state without replaying old chat history or restarting completed phases.

## 1. Read order and precedence

Read `reading/STATUS.json`, then this handoff, generation policy, ten-question standard, schema, durable reading standard, roadmap, and `reading/TASKS.md`.

Current-state precedence:

**live canonical JSONL > fresh audit artifacts > STATUS > handoff/current policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## 2. Arabic — CLOSED / APPROVED

Arabic A1–C2 is complete and formally approved: 360 canonical passages, 3,600 questions, 3,600 linked answers, final Pass 12 `PASS`, formal final approval `true`, and zero current hard regressions/final-approval blockers.

**Do not reopen Arabic unless canonical Arabic data is deliberately changed.**

## 3. French A1 + A2 — GENERATED / GENERATION-INTEGRITY PASS

French A1 and A2 are each complete at 60 passages / 600 questions / 600 answers.

- A1 accepted blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`;
- A1 integrity: `reading/audit/french_a1_generation_integrity.json` = `PASS`;
- A2 accepted blob: `d0a80b8866071f426019aa0ad143e1d270dba4de`;
- A2 integrity: `reading/audit/french_a2_generation_integrity.json` = `PASS`;
- A2 has 100 unique deliberate targets and zero A1↔A2 deliberate-target collisions by validated source ID or visible form;
- every A1/A2 P06 checkpoint has zero deliberately new targets.

Do not broadly regenerate A1/A2. The final expensive French multi-pass approval audit remains deferred until French A1–C2 generation is complete.

## 4. French B1 Unit 01 — ACCEPTED CALIBRATION

Canonical file: `reading/french/b1/passages.jsonl`.

Accepted current frontier:

- sequences 1–6 / Unit 01;
- 6 passages / 60 questions / 60 linked answers;
- 15 fresh deliberate targets, exactly 3 in each P01–P05;
- P06 zero new targets and timed/benchmark eligible;
- word counts: 246, 254, 250, 250, 276, 271;
- accepted B1 blob: `beed8c8337be567325a4b329b79c7d070511f3b1`;
- accepted calibration commit: `ccdf4743c5b359c085387dd66653f01d368e5c07`;
- post-calibration audit: `reading/audit/french_b1_unit01_calibration_review.json` = `PASS`.

Unit 01 targets:

`poursuivre`, `époque`, `trace`, `convaincre`, `position`, `impliquer`, `machine`, `code`, `recommencer`, `étranger`, `peuple`, `futur`, `regretter`, `profiter`, `ennui`.

Calibration guard history:

1. initial workflow path pointed one directory too high; corrected before any canonical write;
2. P01 initially measured 215 words; expanded naturally into the unchanged B1 220–350 band;
3. P05 review `proposer` appeared only conjugated; added a natural exact infinitive occurrence without weakening the review guard;
4. stricter post-calibration review found `impliquer` was being used in a broader participation sense while the validated root gloss directly supports entail/imply; the passage was reframed to teach the consequence/entail sense instead of mutating the root CSV or adding a sense override;
5. minor `peuple` / `ennui` phrasing was polished while preserving target visibility, linkage and B1 length.

Treat Unit 01 as the accepted calibration template for later B1 units.

## 5. French B1 production profile

- standard length band: **220–350 words**;
- calibrated default deliberate load: **3 fresh new lexical types in P01–P05**, still within the durable 3–6 planning range; do not treat 3 as a permanent hard quota if pedagogy later warrants another value;
- connected multi-paragraph narratives/explanations;
- paragraph-level main ideas and multi-sentence inference;
- motives, decisions, consequences, summaries and grammar-in-context;
- move older vocabulary across related but non-identical topics/genres;
- 10 questions + 10 linked answers per canonical passage;
- P06 checkpoint has zero deliberately new lexical targets and should be high-coverage/timed-reading friendly where appropriate;
- root validated lexical CSV is read-only curriculum input.

## 6. IMMEDIATE FRONTIER — B1 Unit 02

Generate **French B1 Unit 02 / sequences 7–12** as one guarded batch.

Required source lock:

`reading/french/b1/passages.jsonl` blob = `beed8c8337be567325a4b329b79c7d070511f3b1`.

Unit 02 guard requirements:

1. verify live main and exact Unit01 blob before write;
2. check every proposed new B1 target against **all deliberate French A1 + A2 + B1 Unit01 targets** before canonical write;
3. preserve validated `french_top1000.csv` source rank/ID identity and intended-sense discipline; avoid unsupported sense extensions when a directly source-supported context is available;
4. default to 3 new targets in each P01–P05; P06 zero new;
5. naturally review Unit01 targets across P01–P05, with every deliberate running-text/summary review exactly visible;
6. validate schema, 220–350 word band, immutable IDs/sequences, local question-target declarations and one-to-one answer linkage;
7. include multi-sentence inference, motive/reason, summary and grammar-in-context where natural;
8. choose related-but-not-identical domains/genres to force transfer rather than copying Unit01’s community-project frame;
9. fail closed on collision, drift or quality invariant failure and repair the batch rather than weakening the guard.

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
