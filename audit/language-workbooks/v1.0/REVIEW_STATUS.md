# Review status

Current as of 2026-08-29.

## Production-candidate QA

Automated, deterministic, editorial, reproducibility, and rendered-output review is complete for the LANG-WB v1.0 production candidate.

Passed evidence includes:

- canonical vocabulary integrity before and after repair application;
- complete 3,000-sentence source-locked corpus selection and audit with zero unresolved sentence rows;
- fail-closed automated/editorial row-level review and approved correction tracking;
- Arabic, French, and Urdu pronunciation-foundations QA;
- fresh rendering of all 42 PDFs;
- qpdf, pdfinfo, and Poppler render preflight for all 42 PDFs;
- final release-manifest and cross-gate audit;
- final rendered-PDF visual audit, including representative master-page sampling and targeted checks for every exceptional repair/display normalization;
- clean self-publication of the rebuilt outputs;
- source-bound native-review worksheet generation and validation CI;
- synthetic CI coverage for reviewer-ledger PASS/HOLD/FAIL/source-drift states and final human-promotion precedence/binding edge cases.

The generated manifest remains `production_candidate`.

## Independent human linguistic gate

Independent full-content human linguistic certification is **not complete**. No automated/editorial decision, language-model review, deterministic check, or visual sampling is represented as a substitute for that final human gate.

The current `native-signoffs/` directory contains no committed human sign-off JSON records. Arabic, French, and Urdu therefore remain pending independent full-master review.

Reviewers should start with:

- [`REVIEWER_ONBOARDING.md`](REVIEWER_ONBOARDING.md) — practical one-language reviewer workflow;
- [`FINAL_NATIVE_REVIEW_PACKET.md`](FINAL_NATIVE_REVIEW_PACKET.md) — canonical scope, artifact binding, defect loop, and promotion rules;
- [`native-review-ledgers/README.md`](native-review-ledgers/README.md) — 2,000 structured row worksheet workflow;
- [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json) — immutable human sign-off schema;
- [issue #106](https://github.com/ualispublishing/learning/issues/106) — Arabic/French/Urdu completion tracker.

Promotion beyond `production_candidate` is allowed only after all three languages have valid latest PASS records bound to the exact current candidate and the final human-promotion gate passes.

## Quality boundary

The existing automated/editorial/render evidence is strong production-candidate QA. It is not an absolute error-free guarantee and must not be described as completed independent native-speaker certification.
