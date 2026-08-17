# Agent Handoff — Graded Reading Curriculum

**Purpose:** resume the Arabic/French/Urdu graded-reading project from live repository state without replaying old chat history or restarting completed phases.

## 1. Precedence

Read `reading/STATUS.json`, then this handoff, generation policy, ten-question standard, schema, durable reading standard, roadmap, and `reading/TASKS.md`.

**live canonical JSONL > fresh audit artifacts > STATUS > handoff/current policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## 2. Arabic — CLOSED / APPROVED

Arabic A1–C2 is complete and formally approved: 360 canonical passages, 3,600 questions, 3,600 linked answers, final Pass 12 `PASS`, formal final approval `true`, zero current blockers.

**Do not reopen Arabic unless canonical Arabic data is deliberately changed.**

## 3. French A1 + A2 — GENERATED / INTEGRITY PASS

- A1: 60 passages / 600 Q / 600 A; blob `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`; integrity `PASS`.
- A2: 60 passages / 600 Q / 600 A; blob `d0a80b8866071f426019aa0ad143e1d270dba4de`; integrity `PASS`; 100 unique deliberate A2 targets and zero A1↔A2 deliberate-target collisions.

Do not broadly regenerate A1/A2. Final expensive French language-wide multi-pass approval remains deferred until A1–C2 generation is complete.

## 4. French B1 production profile

Canonical file: `reading/french/b1/passages.jsonl`.

- standard band: **220–350 words**;
- calibrated default: **3 fresh new lexical types in P01–P05**;
- 10 questions + 10 linked answers per passage;
- P06 zero deliberately new targets;
- connected multi-paragraph narratives/explanations with paragraph-level main ideas, multi-sentence inference, motives/consequences, summaries and grammar-in-context;
- transfer older vocabulary across related but non-identical domains/genres;
- root validated `french_top1000.csv` is read-only curriculum input;
- every new target must be fresh against **all** prior deliberate French targets and preserve source rank/ID/intended-sense discipline;
- every deliberate running-text/summary review must be exact-form visible;
- fail closed on blob/source drift, duplication, schema/linkage, exact review visibility, word band or sequence collisions.

## 5. French B1 Units 01–05 — CANONICAL

B1 is currently **30/60 passages**, 300 questions, 300 linked answers.

Current B1 blob: `dfd2b675884c9481906ce6b5bbba263f6c95b063`.
Current canonical commit: `52d6156746db740f7926ae58a61756ef401a7587`.

### Unit 01 — accepted calibration
Sequences 1–6. Calibration audit `reading/audit/french_b1_unit01_calibration_review.json` = `PASS`. Accepted repaired calibration blob `beed8c8337be567325a4b329b79c7d070511f3b1`.

Targets: `poursuivre`, `époque`, `trace`, `convaincre`, `position`, `impliquer`, `machine`, `code`, `recommencer`, `étranger`, `peuple`, `futur`, `regretter`, `profiter`, `ennui`.

### Unit 02 — complete
Sequences 7–12.
Targets: `apparemment`, `détail`, `honnête`, `ordinateur`, `installer`, `remplir`, `planète`, `attirer`, `durer`, `coûter`, `respecter`, `inutile`, `admettre`, `mensonge`, `conversation`.

### Unit 03 — complete
Sequences 13–18.
Targets: `zone`, `séparer`, `morceau`, `causer`, `rapide`, `agir`, `espoir`, `oser`, `liberté`, `nourriture`, `accompagner`, `sonner`, `art`, `paix`, `rôle`.

### Unit 04 — complete
Sequences 19–24.
Targets: `probablement`, `prouver`, `sérieux`, `scène`, `spécial`, `créer`, `rejoindre`, `ligne`, `bout`, `normal`, `système`, `prévenir`, `relation`, `reconnaître`, `plutôt`.

Guard history: prior deliberate `recherche`, `voix`, `présent` were rejected; fresh replacements were `sérieux`, `spécial`, `plutôt`. Invalid domain `cultural`, short word-band cases, and exact checkpoint `sérieux` visibility were repaired before canonical mutation.

### Unit 05 — complete / current frontier
Sequences 25–30.
Targets: `clair`, `reprendre`, `déranger`, `empêcher`, `récupérer`, `sinon`, `ancien`, `vivant`, `honneur`, `inviter`, `remercier`, `mériter`, `liste`, `réaliser`, `arranger`.

Guard history: prior deliberate `prix` was rejected and replaced by fresh source-backed `liste` rank 646. Exact-form `mériter`, Unit04 review `normal`, and P06 summary `clair`/`mériter` visibility were repaired naturally. Final generator, independent checks and canonical commit passed. P06 word count 252 and zero new targets.

## 6. IMMEDIATE FRONTIER — B1 Unit 06

Generate **French B1 Unit 06 / sequences 31–36** as one guarded batch.

Required B1 source lock:
`reading/french/b1/passages.jsonl` blob = `dfd2b675884c9481906ce6b5bbba263f6c95b063`.

Unit 06 requirements:
1. verify live main and exact Unit05 blob before write;
2. check every proposed target against all deliberate French A1 + A2 + B1 Units01–05 targets;
3. preserve validated source rank/ID and intended-sense discipline;
4. default to 3 new targets each P01–P05; P06 zero new;
5. naturally review Unit05 target triplets across P01–P05, exact-form visible;
6. validate schema, 220–350 word band, immutable IDs/sequences, local target declarations and one-to-one answer linkage;
7. preserve B1 inference/motive/summary/grammar-in-context demand and cross-domain transfer;
8. fail closed and repair rather than weakening guards.

Unit05 review triplets for Unit06:
- P01: `clair`, `reprendre`, `déranger`
- P02: `empêcher`, `récupérer`, `sinon`
- P03: `ancien`, `vivant`, `honneur`
- P04: `inviter`, `remercier`, `mériter`
- P05: `liste`, `réaliser`, `arranger`

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
