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
- Passes 01–09 fresh `PASS`;
- Pass 10 `PASS_WITH_SOURCE_ADJUDICATION` with six current source adjudications and one historical repaired item;
- Pass 11 `COMPLETE`, 360/360 manual naturalness review;
- Pass 12 `PASS`, `final_approval=true`;
- zero Pass 12 hard regressions or approval blockers;
- direct Pass 12 checks: 360 unique IDs, valid sequences, zero question-answer linkage failures, zero undeclared question-target links, zero word-band failures, zero stored-word-count mismatches, zero Latin-script reader hits, and zero P6 new-target regressions.

Final evidence:
`reading/audit/final_arabic_pass12_adversarial_gate_falsification.json`

**Do not reopen Arabic generation/recalibration/review unless new canonical Arabic data is deliberately changed.** Historical Arabic warnings/checklists do not override the approved current artifact chain.

Arabic coverage remains intentionally unmeasured. Existing zero coverage values are placeholders, not measured 0%; no percentage was fabricated to obtain approval.

## 3. Current production state

### French — ACTIVE

Live repo state:

- `reading/french/a1/passages.jsonl`: 6 canonical A1 calibration passages;
- `reading/french/a1/CALIBRATION_UNIT_01.md` exists;
- no French A2–C2 canonical corpus exists yet.

The six live A1 passages are the starting state. **Do not restart calibration from zero.** Continue A1 from sequence 7 toward 60 using the generation-first policy and current ten-question/schema contract.

### Urdu — QUEUED

Live repo state:

- `reading/urdu/a1/passages.jsonl`: 6 canonical A1 calibration passages;
- `reading/urdu/a1/calibration/` exists;
- no Urdu A2–C2 canonical corpus exists yet.

Keep Urdu unchanged while French is active unless the user explicitly reprioritizes it.

## 4. Immediate next action

**Continue French A1 from the existing six passages.**

Before writing the first new French batch:

1. verify live `main`;
2. read the six current French A1 passages and calibration note;
3. inspect the French validated lexical sources/any French-specific ledgers needed for target identity;
4. establish the continuation schedule from sequence 7 without rewriting sequences 1–6;
5. generate in large unit-sized guarded batches under the ten-question standard;
6. perform structural/source/linkage checks needed for safe generation, but reserve the expensive full multi-pass final audit for the completed generated corpus.

Do not translate Arabic passages into French. French must have natural French scenarios, collocations, grammar progression, and independent lexical scheduling.

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
