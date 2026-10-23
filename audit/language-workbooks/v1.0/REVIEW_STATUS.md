# Review status

Current as of 2026-09-14.

## Production-candidate QA

Automated, deterministic, editorial, reproducibility, and rendered-output review is complete for the currently staged LANG-WB v1.0 production candidate.

Passed evidence includes:

- canonical vocabulary integrity before and after repair application;
- complete 3,000-sentence source-locked corpus selection and audit with zero unresolved sentence rows;
- fail-closed automated/editorial row-level review and approved correction tracking across the 6,000 sentence/vocabulary rows;
- fail-closed adjudication-ledger CSV shape validation before repair application;
- Arabic, French, and Urdu pronunciation-foundations QA;
- fresh rendering of all 42 PDFs;
- aggregate rendered-output QA;
- qpdf, pdfinfo, and Poppler render preflight for all 42 PDFs;
- final release-manifest and cross-gate audit;
- targeted manual visual checks for the French pages affected by the current correction round, including sentence ranks 288, 599, and 794 and vocabulary ranks 608 and 837;
- source-bound native-review worksheet generation and validation CI;
- synthetic CI coverage for reviewer-ledger PASS/HOLD/FAIL/source-drift states and final human-promotion precedence/binding edge cases.

The generated manifest remains `production_candidate`.

## Post-audit French correction round

The bounded v2 linguistic repair round was applied on 2026-09-04 by commit `11e1a72b137e5110e4ff610fd4f92fc6e5a4a3bb` / PR #138. That round applied 48 learner-source vocabulary repairs, 2 ledger-only synchronizations, and the associated fail-closed runner/baseline updates, with the established full-corpus/build QA.

A later conservative post-audit review identified three additional high-confidence French corrections. They are now staged on draft PR #140:

- vocabulary rank 608 `situation`: `situation; circumstances; location; job (context-dependent)`;
- vocabulary rank 837 `bosser`: `to work (informal)`;
- sentence rank 599: `Aide-moi à faire mes devoirs, s’il te plaît.` while preserving `Help me with my homework, please.`.

During regeneration, two historical malformed French sentence-ledger CSV rows were also discovered and corrected without changing their intended linguistic decisions:

- rank 288 now preserves the complete target `Pouvez-vous signer ici, s'il vous plaît ?` and English `Can you sign here, please?`;
- rank 794 now preserves the complete English `If you hurry, you can still catch your train.` and remains band C.

The malformed-ledger failure mode is now guarded by `scripts/validate_language_workbook_ledger_csv.py`, wired as workflow Pass 2.4 before adjudication application. The validator accepts the repository's legitimate sentence/vocabulary ledger schema variants while rejecting row/header column-count mismatches caused by malformed quoting or unquoted commas.

Canonical validation run #157 passed the complete workflow from source head `0452e07bf8932c5736453569b187840876a82705`. Its archived learner-facing CSVs were also checked against the post-repair authoritative staging/source data: 1,000 sentence rows and 1,000 vocabulary rows per language, with zero row mismatches.

Controlled writable push run #158 repeated the complete gate sequence successfully and staged the verified generated outputs in commit `d7e1faac368b22a42f12da3cd5bbbbb2ec07be3c`. The temporary draft-branch publish allowance was then removed; commit `91c19d52c10d0157387f6852c79f791161b3d0d8` restored the canonical workflow guard.

Arabic sentence rank 747 (`لا يعرف أيٌّ من والديّ الاثنين كيف يسبح.`) remains a genuine human naturalness/register judgment. Its current learner-facing text was not changed by this correction round and it must not be auto-repaired from model/reference evidence alone.

The French external-verification instrumentation issue recorded on 2026-09-09 has been corrected: the current French summary reports Lexique4 coverage for all 1,000 rows and no source-load problem. The external-verification queue remains a triage aid, not a correctness oracle.

## Independent human linguistic gate

Independent full-content human linguistic certification is **not complete**. No automated/editorial decision, language-model review, deterministic check, workflow pass, or visual sampling is represented as a substitute for that final human gate.

The current `native-signoffs/` directory contains no committed human sign-off JSON records. Arabic, French, and Urdu therefore remain pending independent full-master review.

Reviewers should start with:

- [`REVIEWER_ONBOARDING.md`](REVIEWER_ONBOARDING.md) — practical one-language reviewer workflow;
- [`FINAL_NATIVE_REVIEW_PACKET.md`](FINAL_NATIVE_REVIEW_PACKET.md) — canonical scope, artifact binding, defect loop, and promotion rules;
- [`native-review-ledgers/README.md`](native-review-ledgers/README.md) — 2,000 structured row worksheet workflow;
- [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json) — immutable human sign-off schema;
- [issue #106](https://github.com/ualispublishing/learning/issues/106) — Arabic/French/Urdu completion tracker.

Promotion beyond `production_candidate` is allowed only after all three languages have valid latest PASS records bound to the exact current candidate and the final human-promotion gate passes.

## Quality boundary

The existing automated/editorial/render evidence is strong production-candidate QA. It is not an absolute error-free guarantee and must not be described as completed independent native-speaker certification. PR #140 remains a draft staging/review PR and must not be merged or promoted as a final release solely on the basis of the automated gates above.
