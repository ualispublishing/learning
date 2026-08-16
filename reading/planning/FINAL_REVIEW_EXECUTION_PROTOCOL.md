# Final Review Execution Protocol — Graded Reading

## Purpose

This file governs the **current final-review phase** of the graded-reading project. It exists to prevent stale calibration instructions, duplicated audit work, and one-passage-at-a-time workflow churn from slowing final review.

For current-state questions, use this precedence order:

1. live canonical JSONL on `main`;
2. freshly regenerated audit artifacts produced from that live JSONL;
3. `reading/STATUS.json`;
4. this execution protocol and `GENERATION_FIRST_FINAL_AUDIT_POLICY.md`;
5. `TEN_QUESTION_STANDARD.md` and the canonical schema;
6. durable pedagogical standards / roadmap;
7. historical calibration instructions and old audit artifacts.

If an older document conflicts with a later final-review policy only on **order of operations**, the later final-review policy wins. Quality criteria are not weakened.

## Current phase

Arabic A1–C2 generation is complete: 360 canonical passages, 60 at each CEFR level. Arabic is in final multi-pass review. French and Urdu are paused while Arabic final review closes.

Do not restart Arabic generation or calibration units. Do not infer current status from old chat memory or historical checklist text.

## Fast-path operating model

Final review should run in **large, evidence-bounded batches**, not one passage or one workflow per edge case.

For each remediation class:

1. Fetch/check live `main` once.
2. Build one compact snapshot or diagnostic worklist for the whole affected set.
3. Review/classify the whole set before writing.
4. Write one guarded remediation script for the batch.
5. Fail closed on source drift, unexpected schema, target/exposure drift, answer linkage drift, or level-band violations.
6. Run only the audits materially affected by the change.
7. Commit canonical changes and refreshed affected audit artifacts together when practical.
8. Update `STATUS.json` / handoff state once per completed batch, not once per passage.

Do not create a new workflow for every individual exception. A failed guard should normally improve the same batch script and rerun it, unless the failure proves the passage needs separate human adjudication.

## Audit invalidation matrix

Use the narrowest correct rerun set:

- **question type/prompt/answer changes only:** rerun Pass 03 and Pass 04; rerun script/data-integrity gates only if their checked fields are affected. Do not rerun prose naturalness or CEFR length merely because questions changed.
- **passage prose changes:** rerun word-count/CEFR diagnostics, script hygiene, answer/evidence alignment where relevant, and targeted naturalness re-review for changed prose.
- **lexical target metadata/exposure changes:** rerun lexical exposure/source gates plus any question/evidence gates touching those targets.
- **schema/ID/order changes:** rerun data-integrity gates.
- **final approval attempt:** regenerate all final gate artifacts sequentially from current canonical data, then run Pass 12 last.

## Concurrency / collision rules

Multiple Arabic chats or agents may operate in parallel.

- Before taking a write batch, verify the live `main` head and affected records.
- Prefer non-overlapping levels/units/files between agents.
- Every large remediation script must assert the source state it expects before writing.
- Before pushing from Actions, fetch/rebase `origin/main`; a conflict or failed source assertion is a stop condition, not permission to overwrite.
- Do not run multiple workflows that independently push the same audit artifact at the same time. Final audit regeneration is sequential.
- GitHub Actions commits made with `GITHUB_TOKEN` may not recursively trigger downstream workflows. Explicitly run the required dependent audit in the same workflow or use a deliberate dispatch/trigger.

## Status and artifact freshness

Persisted audit JSON is evidence only for the corpus state from which it was generated. If canonical fields covered by an audit changed afterward, regenerate that audit before relying on its status.

`estimated_known_token_coverage = 0` in the current Arabic corpus is an **unmeasured placeholder**, not a measured 0% coverage result. Pass 07 records this as `UNMEASURED_NOT_FAILURE`; do not convert it into a failure or fabricate percentages.

Pass 11 uses `COMPLETE` for the finished manual naturalness review. Final-gate logic must accept the documented completion state rather than requiring a fictitious `PASS` string.

## Question-review rules

`TEN_QUESTION_STANDARD.md` is the active distribution contract. Canonical passages contain 10 questions and 10 linked answers.

Question roles may overlap only when semantics and metadata genuinely support both roles. Do not relabel questions merely to satisfy a counter. When remediation is needed, preserve a target's independent lexical assessment if one of its redundant lexical questions is repurposed for grammar/form retrieval.

The schema's question-type enum is authoritative for allowed type names. If an older prose standard lists a smaller taxonomy, the schema and Ten-Question Standard control current canonical data.

## Final approval

Final approval is fail-closed.

- No final approval while a substantive required audit remains unresolved.
- Do not hand-edit audit status fields to green.
- Pass 12 runs last and must derive blockers from live/fresh upstream artifacts.
- Pass 12 must include answer/evidence alignment (Pass 04) and must accept Pass 11 `COMPLETE` as completion.
- If Pass 12 is stale relative to upstream remediation, its old blocker prose is historical evidence, not current truth.

## Current Arabic frontier (2026-08-16)

At the time this protocol was added:

- Pass 03: `REVIEW_REQUIRED`, 8 residual A2 lexical-composition flags after the large grammar-distribution remediation.
- Pass 04: `REVIEW_REQUIRED`, 52 conservative diagnostic flags; many are expected false-positive candidates from duplicate grammatical-category answers or surface-overlap heuristics and require classifier/adjudication review before content edits.
- Pass 07: `PASS`, 0 actionable flags; lexical coverage remains unmeasured for 360 passages.
- Pass 11: `COMPLETE`, 360/360 passages covered by manual naturalness review evidence.
- Pass 12: persisted artifact is stale and remains blocked; do not use its old Pass 07/Pass 11 blocker text as current state.

Immediate sequence:

1. clear the eight genuine residual A2 Pass 03 lexical-composition cases with scheduled review vocabulary only;
2. repair/adjudicate Pass 04 diagnostics so false positives are not mistaken for answer defects, then remediate any genuine answer/evidence issues;
3. refresh all affected machine gates sequentially;
4. repair Pass 12 dependency logic and rerun it last;
5. set final approval only if the fresh adversarial gate passes.
