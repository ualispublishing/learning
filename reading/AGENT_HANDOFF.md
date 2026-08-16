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

French A1 generation is complete at **60/60 canonical passages**:

- Unit 01 / sequences 1–6: original calibration cycle preserved;
- Units 02–10 / sequences 7–60: generated in guarded six-passage batches;
- 600 questions and 600 linked answers;
- every Unit P06 checkpoint has zero deliberately new lexical targets;
- live A1 canonical file: `reading/french/a1/passages.jsonl`;
- latest accepted A1 sequence: `fr-a1-u10-p06`, sequence 60;
- latest A1 canonical blob at the completion milestone: `b6c15291b7871e196cac8f7b5920923f2a3a95a9`.

A1 generation is **closed to routine regeneration**. It is generated, not yet the final audited/approved French language corpus. Under the generation-first policy, continue French through A2–C2 before the expensive multi-pass final French audit unless the governing policy is explicitly changed.

The A1 batch guards established and retained the following failure-closed behavior:

- exact canonical source-blob collision guards;
- sequence and ID continuity;
- canonical JSON schema validation;
- A1 90–140-word planning band;
- exactly 10 questions and 10 one-to-one linked answers per passage;
- all question target IDs locally declared as new/review vocabulary;
- source-rank identity against `french_top1000.csv`;
- no reintroduction of already scheduled lexical IDs;
- visible exact-form checks for deliberate running-text/summary reviews;
- Unit P06 zero deliberately new lexical targets.

Important A1 failure modes already encountered and resolved without weakening guards:

- Unit 06: a declared `enfant` review appeared only as plural `enfants`; exact-form visibility correctly blocked the write until a natural singular occurrence was added.
- Unit 07: a surface/lemma mismatch involving `droite`/`droit` was resolved against the validated lexical source before canonical commit.
- Unit 10: `pluie` and `manteau` were not direct validated `french_top1000.csv` targets; the source guard blocked the first run. The successful retry used validated `ciel` and `sac` instead, while preserving the rest of the guarded target cycle. The retry workflow passed and the canonical sequence 60 commit landed.

Do not translate Arabic passages into French. French scenarios, collocations, grammar progression, and lexical scheduling must remain independently designed and natural.

### French A2 — NEXT FRONTIER

The immediate production frontier is **A2 Unit 01 / sequences 1–6**.

Before writing A2:

1. verify live `main` again;
2. determine whether `reading/french/a2/passages.jsonl` already exists and treat its live contents as authoritative;
3. confirm A2 planning constraints from the roadmap and durable reading standards rather than copying the A1 word band blindly;
4. preserve the ten-question contract and P06 zero-new-target checkpoint pattern;
5. use validated French lexical sources and explicit A1→A2 bridge/review scheduling where pedagogically useful;
6. encode the exact A2 starting state in the generator so parallel work fails closed on drift;
7. generate a complete six-passage Unit 01 batch, not passage-by-passage.

A2 progression should follow the roadmap focus: routine problems and solutions, short stories/practical information, pronoun/reference chains, common subordinate clauses, more flexible tense/aspect, simple motives/cause-effect, and more cloze transfer.

### Urdu — QUEUED

Urdu remains unchanged:

- six A1 calibration passages exist;
- A2–C2 canonical corpus does not yet exist.

Keep Urdu unchanged while French is active unless the user explicitly reprioritizes it.

## 4. Immediate next action

**Verify the live French A2 starting state and generate French A2 Unit 01 / sequences 1–6 as one guarded batch. Do not reopen French A1 or Arabic.**

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
