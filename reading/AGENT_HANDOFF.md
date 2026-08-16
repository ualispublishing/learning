# Agent Handoff — Graded Reading Curriculum

**Purpose:** resume the Arabic/French/Urdu graded-reading project from live repository state without replaying old chat history or restarting completed phases.

## 1. Read order and precedence

Read `reading/STATUS.json`, then this handoff, generation policy, ten-question standard, schema, durable reading standard, roadmap, and `reading/TASKS.md`.

Current-state precedence:

**live canonical JSONL > fresh audit artifacts > STATUS > handoff/current policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## 2. Arabic — CLOSED / APPROVED

Arabic A1–C2 is complete and formally approved:

- 360 canonical passages;
- 3,600 questions and 3,600 linked answers;
- final Pass 12 = `PASS`;
- formal final approval = `true`;
- zero current hard regressions/final-approval blockers.

Final evidence: `reading/audit/final_arabic_pass12_adversarial_gate_falsification.json`.

**Do not reopen Arabic generation/recalibration/review unless canonical Arabic data is deliberately changed.**

## 3. French A1 — GENERATED / INTEGRITY PASS

French A1 is complete at 60 passages / 600 questions / 600 answers.

- canonical file: `reading/french/a1/passages.jsonl`;
- current accepted A1 blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`;
- generation-integrity closeout = `PASS`;
- 100 deliberate A1 targets;
- four verified sense overrides plus documented morphology/polysemy exceptions;
- all A1 Unit P06 checkpoints have zero deliberately new targets.

A1 is closed to routine regeneration but has not yet gone through the final language-wide French multi-pass approval audit. Continue generation-first through A2–C2 first unless governing policy changes.

## 4. French A2 — ACTIVE

Canonical A2 file: `reading/french/a2/passages.jsonl`.

Current accepted frontier:

- Unit 01 / sequences 1–6: complete;
- Unit 02 / sequences 7–12: complete;
- Unit 03 / sequences 13–18: complete;
- total A2 passages: 18;
- total A2 questions/answers: 180 / 180;
- latest sequence: `fr-a2-u03-p06`, sequence 18;
- current canonical A2 blob: `488fa3f0638df94624900a155d9f2ed22dbe09a6`;
- every completed A2 Unit P06 has zero deliberately new lexical targets.

A2 planning band remains **140–220 words** for standard passages, with controlled lexical load, more reference chains, subordinate clauses, motives/cause-effect, tense/aspect flexibility, and transfer questions.

### A2 target history

Unit 01:
`retard`, `conseil`, `erreur`, `expliquer`, `essayer`, `possible`, `réparer`, `éviter`, `rendez-vous`, `découvrir`.

Unit 02:
`raison`, `résultat`, `décision`, `information`, `important`, `différent`, `habitude`, `expérience`, `choix`, `idée`.

Unit 03:
`oublier`, `clé`, `perdre`, `retrouver`, `recevoir`, `envoyer`, `vérifier`, `payer`, `numéro`, `carte`.

### Guard history and durable rule

Unit 01 established the A1→A2 bridge and exposed several useful fail-closed cases: stale A1 blob, exact review visibility, source-sense mismatch, and exact infinitive visibility. Those were repaired without weakening guards.

Unit 02 initially checked freshness only against prior A2. A post-generation cross-level audit confirmed its ten targets happened not to collide with any A1 deliberate target. **Do not repeat that narrow guard.**

From Unit 03 onward, every A2 generator must check proposed new targets against **A1 plus all prior A2 deliberate targets** before any canonical write.

Unit 03 generator/workflow enforced and passed:

- exact source-blob lock;
- A1+A2 target freshness;
- validated `french_top1000.csv` rank/ID identity;
- A2 140–220 word band;
- 10 questions and 10 one-to-one answers per passage;
- all question target IDs locally declared;
- exact-form visibility for deliberate running-text/summary reviews;
- sequence/ID continuity;
- exactly ten new targets across P01–P05;
- zero-new P06 checkpoint;
- independent post-generation checks before canonical commit.

Do not translate Arabic passages into French; keep French scenarios and collocations independently natural.

## 5. Immediate next action

**Generate French A2 Unit 04 / sequences 19–24 as one guarded six-passage batch against exact canonical A2 blob `488fa3f0638df94624900a155d9f2ed22dbe09a6`.**

Requirements for Unit 04:

1. verify live `main` and that no parallel agent has already claimed Unit 04;
2. review Unit-03 targets one pair per P01–P05 where natural;
3. choose ten source-backed new targets and reject any target already deliberate in A1 or A2 Units 01–03;
4. keep all standard passages in the 140–220 band;
5. keep every question target locally declared and all answer links one-to-one;
6. make all deliberate running-text reviews exactly visible;
7. keep P06 zero-new and timed-reading friendly;
8. encode the exact 18-passage source state so parallel work fails closed on drift.

## 6. Urdu — QUEUED

Urdu remains unchanged at six A1 calibration passages. Keep it paused while French is active unless the user explicitly reprioritizes it.

## 7. Throughput / parallel-agent rules

- use coherent six-passage unit batches, not passage-by-passage workflows;
- verify live main before each write batch;
- prefer non-overlapping units/files across chats;
- source-state assertions are required for large mutations;
- serialize workflows writing the same canonical artifact;
- fix failed guards rather than weakening them;
- do not rely on recursive `GITHUB_TOKEN` workflow triggers;
- update STATUS/TASKS/handoff at meaningful milestones, not after every passage.

## 8. Core pedagogical non-negotiables

- canonical data: `reading/<language>/<level>/passages.jsonl`;
- passage → all questions → answers/reveal;
- 10 questions / 10 linked answers per canonical passage;
- infer → verify → transfer plus spaced review;
- root validated lexical CSV remains read-only curriculum input;
- frequency rank is not a CEFR label;
- final approval is fail-closed and cannot be obtained by editing status fields.
