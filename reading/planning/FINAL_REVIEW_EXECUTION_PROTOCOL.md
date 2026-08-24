# Final Review Execution Protocol — Graded Reading

## Purpose

This is a **durable execution protocol** for final review. It must not carry a dated language frontier. Current state lives in:

1. `reading/CONTINUATION.json`;
2. live canonical JSONL;
3. fresh hash-bound audit evidence;
4. `reading/RELEASE_STATUS.json` for release claims;
5. `reading/STATUS.json` for production state.

If any dated historical section elsewhere conflicts with those sources, the live state/evidence wins. Quality criteria are not weakened.

## Fast-path operating model

Final review should run in **large, evidence-bounded batches**, not one passage or one workflow per edge case.

For each remediation class:

1. verify live `main` and the affected canonical records;
2. build one compact snapshot or diagnostic worklist for the affected set;
3. review/classify the whole set before writing;
4. use one guarded remediation script or one bounded canonical edit set where practical;
5. fail closed on source drift, unexpected schema, target/exposure drift, answer linkage drift, level-band violations, or record-selection mismatch;
6. run only audits materially affected by the change, plus any required final gate;
7. commit canonical changes and refreshed affected evidence together when practical;
8. update continuation/status/release state once per completed batch, not once per passage.

Do not create a new workflow for every individual exception. A failed guard should normally improve the same batch process and rerun it unless the failure proves the passage needs separate human adjudication.

## Audit invalidation matrix

Use the narrowest correct rerun set:

- **question type/prompt/answer changes only:** rerun question-quality/evidence/answer-key gates materially affected by the change; do not rerun prose naturalness or CEFR length merely because questions changed;
- **passage prose changes:** rerun word-count/CEFR diagnostics, script/orthography hygiene, answer/evidence alignment where relevant, and targeted naturalness re-review for changed prose;
- **lexical target metadata/exposure changes:** rerun lexical exposure/source gates plus any question/evidence gates touching those targets;
- **schema/ID/order changes:** rerun data-integrity gates;
- **final approval attempt:** regenerate all required final-gate artifacts sequentially from current canonical data and run the adversarial/final gate last.

## Concurrency / collision rules

Multiple chats or agents may operate in parallel.

- Before taking a write batch, verify the live `main` head and affected records.
- Prefer non-overlapping languages/levels/units/files between agents.
- Every large remediation script must assert the source state it expects before writing.
- Before pushing from Actions, fetch/rebase `origin/main`; a conflict or failed source assertion is a stop condition, not permission to overwrite.
- Do not run multiple workflows that independently push the same audit artifact at the same time. Final audit regeneration should be sequential when artifacts depend on one another.
- GitHub Actions commits made with `GITHUB_TOKEN` may not recursively trigger downstream workflows. Explicitly run required dependent checks in the same workflow or use a deliberate dispatch/trigger.

## Status and artifact freshness

Persisted audit JSON is evidence only for the corpus state from which it was generated. If canonical fields covered by an audit changed afterward, regenerate or explicitly revalidate that audit before relying on its status.

Rules:

- bind final evidence to canonical hashes/blobs where practical;
- treat hash drift as stale evidence, not as permission to reuse an old PASS;
- a zero-step/skipped job is not a green verification gate;
- record tooling/environment failures separately from content defects;
- never hand-edit audit status fields to green;
- do not fabricate lexical coverage percentages where coverage is unmeasured;
- machine-valid structure does not replace semantic reader-first review.

## Question-review rules

`TEN_QUESTION_STANDARD.md` is the active distribution contract. Canonical passages normally contain 10 questions and 10 linked answers.

Question roles may overlap only when semantics and metadata genuinely support both roles. Do not relabel questions merely to satisfy a counter. When remediation is needed, preserve a target's independent lexical assessment if one of its redundant lexical questions is repurposed for grammar/form retrieval.

The schema's question-type enum is authoritative for allowed type names. If an older prose standard lists a smaller taxonomy, the schema and Ten-Question Standard control current canonical data.

## Semantic / educator review rules

A deterministic or structural PASS is necessary evidence where applicable but is not sufficient for educator/publication readiness.

Final semantic review should independently examine, as applicable:

- naturalness and idiomaticity;
- grammar/morphology/agreement/script/punctuation;
- lexical sense and register;
- CEFR and pedagogical suitability;
- inferability and vocabulary load;
- question validity, ambiguity, distractors, and answer correctness;
- evidence alignment and reference resolution;
- spacing/interleaving/exposure quality;
- fluency/checkpoint suitability;
- duplicate/template/topic/genre issues;
- adversarial attempts to falsify prior approvals.

Where the highest-assurance profile requires professional/native/educator or genuinely independent model-family review, deterministic metadata must not be bulk-promoted as a substitute.

## Final approval

Final approval is fail-closed.

- No final approval while a substantive required audit remains unresolved.
- Final evidence must be fresh for the reviewed corpus.
- The final/adversarial gate runs after its required upstream evidence.
- Stale blocker prose or stale PASS prose is historical evidence, not current truth.
- `reading/RELEASE_STATUS.json` is the sole compact source for educator/publication readiness claims.
- Do not claim literal 100% correctness; record the actual assurance achieved and any known limits.

## Current frontier policy

This protocol intentionally contains **no current language, level, date, pass count, or immediate-next sequence**. Those change frequently and belong in `reading/CONTINUATION.json`, `reading/STATUS.json`, `reading/TASKS.md`, and `reading/VERIFICATION_TASKS.md`.

When a new session starts, never resume from a dated frontier embedded in old audit notes or historical commits. Resolve the live frontier from the current state files and canonical data first.
