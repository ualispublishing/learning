# Agent Handoff — Graded Reading Curriculum

**Purpose:** let a new agent resume the Arabic/French/Urdu graded-reading project from repository state without reconstructing old chat history or restarting completed phases.

## 1. Read this order before acting

1. `reading/STATUS.json` — exact current phase and actionable queue.
2. `reading/AGENT_HANDOFF.md` — this concise continuity contract.
3. `reading/planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md` — current batching, freshness, concurrency, and final-gate rules.
4. `reading/planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md` — current order-of-operations policy.
5. `reading/planning/TEN_QUESTION_STANDARD.md` — active ten-question distribution contract.
6. `reading/schema/passage.schema.json` — authoritative canonical schema/type enum.
7. `docs/READING_PASSAGE_STANDARD.md` — durable passage-quality standard.
8. `reading/ROADMAP.md` — durable curriculum architecture.
9. `reading/TASKS.md` — active operational queue.
10. lexical/source ledgers only when the task actually concerns lexical identity, coverage, or exposure.

### Precedence

For current-state conflicts, use:

**live canonical JSONL > fresh audit artifacts > STATUS > final-review execution/policy docs > Ten-Question Standard + schema > durable standards/roadmap > historical calibration instructions/artifacts.**

Later final-review policy supersedes older calibration text only on **workflow ordering**. It does not weaken quality criteria.

## 2. Current state — 2026-08-16

Arabic A1–C2 generation is complete:

- 360 canonical Arabic passages;
- 60 passages at each A1, A2, B1, B2, C1, C2;
- 10 questions and 10 linked answers per passage;
- Arabic is in the closing final-review phase;
- French and Urdu are paused until Arabic final review closes;
- final Arabic approval remains **false** until fresh Pass 12 succeeds.

Do **not** restart Arabic generation, A1 calibration, or early unit production.

Current important audit state:

- Pass 03 — `REVIEW_REQUIRED`: 8 residual A2 lexical-composition flags only.
- Pass 04 — `REVIEW_REQUIRED`: 52 conservative diagnostic flags; many are likely classifier false positives and must be adjudicated before content changes.
- Pass 07 — `PASS`: 0 actionable flags; all 360 length-band checks are clean. Coverage is still unmeasured, not a measured failure.
- Pass 11 — `COMPLETE`: 360/360 passages covered by manual naturalness review evidence.
- Pass 12 — persisted artifact is stale and blocked; its old Pass 07/Pass 11 blocker prose is not current truth.

Exact current details belong in `reading/STATUS.json`, not in chat memory.

## 3. Immediate Arabic work queue

1. Clear the eight residual A2 Pass 03 lexical-composition cases using already scheduled review vocabulary only.
2. Adjudicate Pass 04's diagnostics before editing answers or passages.
3. Repair only genuine Pass 04 answer/evidence defects in one guarded batch.
4. Regenerate final audit artifacts sequentially from the current corpus.
5. Repair Pass 12 dependency logic so it:
   - includes Pass 04;
   - accepts Pass 11 `COMPLETE` as completion;
   - derives blocker text from current upstream artifacts rather than hard-coded historical reasons.
6. Run Pass 12 last.
7. Grant final approval only if fresh Pass 12 genuinely returns `PASS`.

Do not invent Pass 13 merely because Pass 12 needed repair/re-execution.

## 4. Speed / execution contract

The final review should be fast **without weakening safeguards**.

Use one large evidence-bounded batch per defect class:

- one live-head/collision check;
- one compact snapshot/worklist;
- review/classify the whole set;
- one guarded mutation script;
- one workflow execution for that batch;
- rerun only audits materially affected by those fields;
- one status/handoff update at the end of the completed batch.

Do not create a separate workflow for every passage or every small edge case. If a guard exposes a new metadata pattern, update the same batch script and rerun unless human passage-specific adjudication is actually required.

Question-only changes normally require Pass 03 + Pass 04, not Pass 07 or another full prose naturalness read. Prose changes require targeted prose/length/script/evidence revalidation. Lexical metadata changes require the lexical/source/exposure gates.

The full gate suite is regenerated once at the final approval attempt.

## 5. Parallel-agent safety

Multiple Arabic agents/chats may work at once.

Before any write batch:

- verify live `main` and the affected records;
- prefer non-overlapping levels/units/files;
- encode expected source state in the remediation script;
- fail closed on source drift;
- fetch/rebase before Actions pushes;
- never overwrite a conflict merely to finish the batch.

Serialize workflows that write the same audit artifact. GitHub Actions `GITHUB_TOKEN` bot commits may not recursively trigger dependent workflows, so explicitly run required dependent audits in the same workflow or via deliberate dispatch.

## 6. Core pedagogical non-negotiables

- Canonical data is `reading/<language>/<level>/passages.jsonl`.
- Reader order is passage → all questions → answers/reveal.
- Arabic default is natural contemporary MSA; do not silently introduce dialect.
- Vocabulary follows infer → verify → transfer and spaced reinforcement.
- Root validated CSVs are foundations and must not be mutated merely to make passages easier.
- Frequency rank is not a CEFR label.
- 3,000 validated items are not a complete C2 lexicon.
- Reading-speed gains count only with adequate comprehension.
- Passage difficulty is multidimensional; word count is a planning band, not a CEFR classifier.
- Questions are learning tasks, not merely recall checks.
- Only high-confidence naturalness/grammar/idiom defects are repaired during manual linguistic review; stylistic preference alone is not a defect.
- Final approval is fail-closed and cannot be obtained by hand-editing audit statuses.

## 7. Coverage note

The current Arabic canonical field `estimated_known_token_coverage` is unmeasured. Existing zeros are placeholders. Pass 07 correctly records 360 passages as `UNMEASURED_NOT_FAILURE`.

Do not fabricate coverage percentages and do not interpret zero as 0% learner knowledge. A future coverage implementation must calculate from a defensible curriculum-known ledger and documented morphology/token policy.

## 8. Question contract note

`TEN_QUESTION_STANDARD.md` and the schema are authoritative for the current ten-question corpus. Some older prose in `READING_PASSAGE_STANDARD.md` predates the ten-question expansion and lists fewer question types / lower question counts. Treat that older text as historical where it conflicts with the active Ten-Question Standard or schema.

Role overlap is allowed only when semantics and metadata genuinely support it. Do not relabel unrelated questions to satisfy numeric gates.

## 9. End-of-session procedure

Before ending a substantial reading-project session:

1. update `reading/STATUS.json` with the exact live state;
2. update `reading/TASKS.md` if the operational queue changed;
3. update this handoff only when a new durable decision, failure mode, precedence rule, or exception needs to survive;
4. keep historical details in audit artifacts / git history rather than bloating this handoff;
5. leave one exact immediate next action.

The handoff should stay concise. Durable pedagogy belongs in standards/roadmap; exact state belongs in `STATUS.json`; audit evidence belongs in `reading/audit/`.
