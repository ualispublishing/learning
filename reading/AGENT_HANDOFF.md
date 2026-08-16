# Agent Handoff — Graded Reading Curriculum

**Purpose:** resume the Arabic/French/Urdu graded-reading project from live repository state without replaying old chat history or restarting completed phases.

## 1. Read order

1. `reading/STATUS.json` — exact current state and active language.
2. `reading/AGENT_HANDOFF.md` — this continuity contract.
3. `reading/planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md` — production order.
4. `reading/planning/TEN_QUESTION_STANDARD.md` — ten-question contract.
5. `reading/schema/passage.schema.json` — canonical schema/type enum.
6. `docs/READING_PASSAGE_STANDARD.md` — durable quality standard.
7. `reading/ROADMAP.md` — curriculum architecture.
8. `reading/TASKS.md` — operational queue.
9. `reading/planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md` — final-review batching/freshness rules when a language reaches final audit.

Current-state precedence:

**live canonical JSONL > fresh audit artifacts > STATUS > handoff/current policy > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

## 2. Arabic is closed and approved

Arabic A1–C2 is complete and formally approved:

- 360 canonical passages;
- 60 at each A1/A2/B1/B2/C1/C2;
- 3,600 questions and 3,600 linked answers;
- Passes 01–09 `PASS`;
- Pass 10 `PASS_WITH_SOURCE_ADJUDICATION`;
- Pass 11 `COMPLETE`, 360/360 manual naturalness review;
- Pass 12 `PASS`, `final_approval=true`;
- zero hard regressions or final-approval blockers.

Final evidence:
`reading/audit/final_arabic_pass12_adversarial_gate_falsification.json`

**Do not reopen Arabic generation/recalibration/review unless canonical Arabic data is deliberately changed.**

Arabic known-token coverage remains intentionally unmeasured; existing zero values are placeholders, not measured 0%.

## 3. Current production state

### French — ACTIVE

Live French A1 state is now **24/60 canonical passages**:

- Unit 01 / sequences 1–6: original calibration cycle preserved;
- Unit 02 / sequences 7–12: generated and validated;
- Unit 03 / sequences 13–18: generated and validated;
- Unit 04 / sequences 19–24: generated and validated;
- next frontier: **Unit 05 / sequences 25–30**.

Current French A1 totals:

- 24 passages;
- 240 questions;
- 240 linked answers.

Units 02–04 were generated as full six-passage guarded batches, not passage-by-passage. Each batch enforced:

- an exact canonical source-blob collision guard;
- sequence and ID continuity;
- canonical JSON schema validation;
- A1 90–140-word planning band;
- exactly 10 questions and 10 one-to-one linked answers per passage;
- all question target IDs locally declared as new/review vocabulary;
- source-rank identity against `french_top1000.csv`;
- no reintroduction of already scheduled lexical IDs;
- Unit P06 zero deliberately new lexical targets.

Do not regenerate Units 01–04. Verify live `main` before taking Unit 05.

French remains generation-first: perform lightweight structural/source/linkage checks during generation and reserve the expensive multi-pass linguistic/pedagogical final audit for the completed generated corpus.

Do not translate Arabic passages into French. French scenarios, collocations, grammar progression, and lexical scheduling must remain independently designed and natural.

### Urdu — QUEUED

Urdu remains unchanged:

- six A1 calibration passages exist;
- A2–C2 canonical corpus does not yet exist.

Keep Urdu unchanged while French is active unless the user explicitly reprioritizes it.

## 4. Immediate next action

**Generate French A1 Unit 05 as sequences 25–30 from the live 24-passage corpus.**

Before writing:

1. verify live `main` and the French A1 canonical blob;
2. select new lexical targets from the validated French source while excluding already scheduled target IDs;
3. explicitly schedule spaced review from earlier units;
4. generate P01–P05 with controlled new targets and P06 as a zero-new-target checkpoint;
5. run the same schema/source/linkage/word-band/collision guards;
6. commit the entire unit as one batch.

## 5. Speed / unthrottled execution contract

Use large evidence-bounded batches rather than micro-workflows:

- one live-head/collision check per batch;
- one compact source/worklist read;
- one guarded mutation script per coherent batch;
- one workflow run for that batch;
- rerun only checks materially affected by the write;
- update STATUS/TASKS/handoff at meaningful milestones, not per passage.

A failed guard should normally improve the same batch script and rerun it. Create a separate workflow only when the failure proves a genuinely different human-adjudication problem.

This removes self-imposed throttling without removing quality controls.

## 6. Parallel-agent safety

Multiple agents/chats may work in the repo.

- verify live `main` before each write batch;
- prefer non-overlapping languages/levels/units/files;
- encode expected source state in large mutation scripts;
- fail closed on source drift;
- fetch/rebase before Actions pushes;
- serialize workflows that write the same canonical/audit artifact;
- do not rely on recursive `GITHUB_TOKEN` workflow triggers.

## 7. Core pedagogical non-negotiables

- Canonical data: `reading/<language>/<level>/passages.jsonl`.
- Reader order: passage → all questions → answers/reveal.
- Ten questions / ten linked answers per canonical passage.
- Vocabulary uses infer → verify → transfer plus spaced review.
- Root validated CSVs are lexical foundations and are not mutated merely to simplify passage production.
- Frequency rank is not a CEFR label.
- Passage difficulty is multidimensional; word bands are planning bands, not sole CEFR classifiers.
- Questions are learning tasks, not just recall checks.
- Final approval for each language is fail-closed and cannot be achieved by hand-editing status fields.

## 8. End-of-session procedure

Before ending a substantial session:

1. synchronize `reading/STATUS.json` with live canonical state;
2. update `reading/TASKS.md` if the operational queue changed;
3. update this handoff only for durable phase/precedence/failure-mode changes;
4. leave detailed audit history in `reading/audit/` and git history instead of bloating this file;
5. leave one exact immediate next action.
