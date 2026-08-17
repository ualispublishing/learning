# Agent Handoff — Graded Reading Curriculum

**Purpose:** resume the Arabic/French/Urdu graded-reading project from live repository state without replaying old chat history or restarting completed phases.

## 1. Precedence

Read `reading/STATUS.json`, then this handoff, generation policy, ten-question standard, schema, durable reading standard, roadmap, and `reading/TASKS.md`.

**live canonical JSONL > fresh audit artifacts > STATUS > handoff/current policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## 2. Arabic — CLOSED / APPROVED

Arabic A1–C2 is complete and formally approved: 360 canonical passages, 3,600 questions, 3,600 linked answers, final Pass 12 `PASS`, formal final approval `true`, zero current blockers.

**Do not reopen Arabic unless canonical Arabic data is deliberately changed.**

## 3. French A1 + A2 — GENERATED / INTEGRITY PASS

- A1: 60 passages / 600 Q / 600 A; blob `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`; integrity `PASS` at `reading/audit/french_a1_generation_integrity.json`.
- A2: 60 passages / 600 Q / 600 A; blob `d0a80b8866071f426019aa0ad143e1d270dba4de`; integrity `PASS` at `reading/audit/french_a2_generation_integrity.json`; 100 unique deliberate A2 targets and zero A1↔A2 deliberate-target collisions.

Do not broadly regenerate A1/A2. Final expensive French language-wide multi-pass approval remains deferred until A1–C2 generation is complete.

## 4. French B1 production profile

Canonical file: `reading/french/b1/passages.jsonl`.

- standard band: **220–350 words**;
- calibrated default deliberate load: **3 fresh new lexical types in P01–P05**; durable planning range remains 3–6, so 3 is a current default rather than a permanent hard quota;
- 10 questions + 10 linked answers per passage;
- P06 zero deliberately new targets, high-known-vocabulary/timed-reading friendly where appropriate;
- connected multi-paragraph narratives/explanations;
- paragraph-level main ideas, multi-sentence inference, motives/consequences, summaries, grammar-in-context;
- transfer older vocabulary across related but non-identical domains/genres;
- root validated `french_top1000.csv` is read-only curriculum input;
- every new target must be fresh against **all** prior deliberate French targets and preserve validated source rank/ID/intended-sense discipline;
- every deliberate running-text/summary review must be exact-form visible.

## 5. B1 Units 01–03 — CANONICAL

### Unit 01 — accepted calibration

Sequences 1–6, 6 passages / 60 Q / 60 A, 15 fresh targets, P06 zero new.

Accepted post-calibration blob: `beed8c8337be567325a4b329b79c7d070511f3b1`.
Calibration audit: `reading/audit/french_b1_unit01_calibration_review.json` = `PASS`.

Targets:
`poursuivre`, `époque`, `trace`, `convaincre`, `position`, `impliquer`, `machine`, `code`, `recommencer`, `étranger`, `peuple`, `futur`, `regretter`, `profiter`, `ennui`.

Important calibration history:
- initial path bug corrected before canonical write;
- P01 expanded from 215 into unchanged B1 band;
- exact review `proposer` repaired naturally;
- post-calibration review reframed `impliquer` to the directly root-supported entail/consequence sense rather than mutating the root CSV or adding an override;
- minor `peuple`/`ennui` phrasing polished.

### Unit 02 — complete

Sequences 7–12, 6 passages / 60 Q / 60 A, 15 fresh targets, P06 zero new.

Targets:
`apparemment`, `détail`, `honnête`, `ordinateur`, `installer`, `remplir`, `planète`, `attirer`, `durer`, `coûter`, `respecter`, `inutile`, `admettre`, `mensonge`, `conversation`.

Guard history:
- source generator had one bracket typo; failed before canonical mutation and was narrowly repaired;
- checkpoint accidentally tagged prior-unit `impliquer` without declaring it; stale target tag was removed, rather than expanding P06 declarations.

### Unit 03 — complete / current frontier

Sequences 13–18, 6 passages / 60 Q / 60 A, 15 fresh targets, P06 zero new.

Current B1 blob: `8dfb17e274d33227c356b16bad00624f3779342f`.
Canonical completion commit: `551d44b649486495ce47fcfdc0d5569c8bc61c2f`.

Targets:
`zone`, `séparer`, `morceau`, `causer`, `rapide`, `agir`, `espoir`, `oser`, `liberté`, `nourriture`, `accompagner`, `sonner`, `art`, `paix`, `rôle`.

Guard history:
- candidate `existence` failed closed because it is absent from the validated lexical deck;
- replaced with fresh, source-backed `rôle` rank 932, used in its supported function/role sense;
- P02 and P06 were initially below 220 words and were expanded naturally; B1 threshold unchanged;
- final generator + independent checks + canonical commit passed.

## 6. IMMEDIATE FRONTIER — B1 Unit 04

Generate **French B1 Unit 04 / sequences 19–24** as one guarded batch.

Required B1 source lock:

`reading/french/b1/passages.jsonl` blob = `8dfb17e274d33227c356b16bad00624f3779342f`.

Unit 04 guard requirements:

1. verify live main and exact Unit03 blob before write;
2. check every proposed target against all deliberate French A1 + A2 + B1 Units01–03 targets;
3. use validated source rank/ID and avoid unsupported sense extensions;
4. default to 3 new targets each P01–P05; P06 zero new;
5. naturally review Unit03 targets across P01–P05, exact-form visible;
6. validate schema, 220–350 word band, immutable IDs/sequences, local target declarations and one-to-one answer linkage;
7. preserve B1 inference/motive/summary/grammar-in-context demand and cross-domain transfer;
8. fail closed on collision/drift/invariant failure and repair rather than weakening guards.

## 7. Urdu — QUEUED

Urdu remains unchanged at six A1 calibration passages. Keep it paused while French is active unless explicitly reprioritized.

## 8. Throughput / parallel-agent rules

- coherent six-passage units, not passage-by-passage workflows;
- verify live main before each write batch;
- source-state assertions for large mutations;
- serialize workflows writing the same canonical artifact;
- fix failed guards rather than weakening them;
- do not rely on recursive `GITHUB_TOKEN` workflow triggers;
- update STATUS/TASKS/handoff at meaningful milestones.

## 9. Core pedagogical non-negotiables

- canonical data: `reading/<language>/<level>/passages.jsonl`;
- passage → all questions → answers/reveal;
- 10 questions / 10 linked answers per canonical passage;
- infer → verify → transfer plus spaced review;
- root lexical CSV remains read-only;
- frequency rank is not a CEFR label;
- final approval is fail-closed and cannot be obtained by editing status fields.
