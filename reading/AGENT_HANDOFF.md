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
- accepted A1 blob: `0493a2fa13e51b5997db05e91cdea4d8dc5e647b`;
- generation-integrity closeout = `PASS`;
- 100 deliberate A1 targets;
- all A1 Unit P06 checkpoints have zero deliberately new targets.

A1 is closed to routine regeneration but has not yet gone through the final language-wide French multi-pass approval audit. Continue generation-first through A2–C2 first unless governing policy changes.

## 4. French A2 — ACTIVE

Canonical file: `reading/french/a2/passages.jsonl`.

Current accepted frontier:

- Units 01–05 / sequences 1–30: complete;
- total A2 passages: 30;
- total A2 questions/answers: 300 / 300;
- latest sequence: `fr-a2-u05-p06`, sequence 30;
- current canonical A2 blob: `236c94a3493c83e0e55c56fc3cd34e52ec258cae`;
- latest canonical A2 commit: `eab60b077540974428f1f634630a503aa59857fc`;
- every completed A2 Unit P06 has zero deliberately new lexical targets.

A2 planning band remains **140–220 words** for standard passages, with controlled lexical load, more reference chains, subordinate clauses, motives/cause-effect, tense/aspect flexibility, and transfer questions.

### A2 target history

Unit 01:
`retard`, `conseil`, `erreur`, `expliquer`, `essayer`, `possible`, `réparer`, `éviter`, `rendez-vous`, `découvrir`.

Unit 02:
`raison`, `résultat`, `décision`, `information`, `important`, `différent`, `habitude`, `expérience`, `choix`, `idée`.

Unit 03:
`oublier`, `clé`, `perdre`, `retrouver`, `recevoir`, `envoyer`, `vérifier`, `payer`, `numéro`, `carte`.

Unit 04:
`projet`, `équipe`, `réunion`, `responsable`, `programme`, `dossier`, `demande`, `réponse`, `service`, `contact`.

Unit 05:
`médecin`, `patient`, `douleur`, `santé`, `hôpital`, `accident`, `soin`, `urgence`, `risque`, `danger`.

### Guard history and durable rules

From Unit 03 onward, every A2 generator checks proposed new targets against **A1 plus all prior A2 deliberate targets** before canonical write. Every batch also enforces exact source-blob lock, validated `french_top1000.csv` rank/ID identity, A2 word band, 10 one-to-one Q/A per passage, local question-target declaration, exact-form visibility for deliberate running-text/summary reviews, sequence/ID continuity, exactly ten new targets across P01–P05, zero-new P06, and independent post-generation checks before commit.

Unit 04 first run correctly failed closed because the review target `perdre` appeared only as the inflected form `perdu`. A natural exact infinitive occurrence was added; the retry passed without weakening the visibility guard.

Unit 05 used general, non-diagnostic health/safety language and passed all guards on its first workflow run.

Do not translate Arabic passages into French; keep French scenarios and collocations independently natural.

## 5. Immediate next action

**Generate French A2 Unit 06 / sequences 31–36 as one guarded six-passage batch against exact canonical A2 blob `236c94a3493c83e0e55c56fc3cd34e52ec258cae`.**

Requirements:

1. verify live `main` and ensure no parallel agent has claimed Unit 06;
2. review Unit-05 targets one pair per P01–P05 where natural: `médecin/patient`, `douleur/santé`, `hôpital/accident`, `soin/urgence`, `risque/danger`;
3. choose ten source-backed new targets and reject anything already deliberate in A1 or A2 Units 01–05;
4. keep standard passages in the 140–220 band;
5. preserve exact local target declarations and one-to-one answer linkage;
6. make deliberate running-text reviews exactly visible;
7. keep P06 zero-new and timed-reading friendly;
8. lock the generator to the exact 30-passage source state so parallel work fails closed on drift.

## 6. Urdu — QUEUED

Urdu remains unchanged at six A1 calibration passages. Keep it paused while French is active unless explicitly reprioritized.

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
