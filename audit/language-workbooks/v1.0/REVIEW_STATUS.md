# Review status

Current as of 2026-09-10.

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

## Post-audit correction planning

The bounded v2 linguistic repair round was applied on 2026-09-04 by commit `11e1a72b137e5110e4ff610fd4f92fc6e5a4a3bb` / PR #138. That round applied 48 learner-source vocabulary repairs, 2 ledger-only synchronizations, and the associated fail-closed runner/baseline updates, with the established full-corpus/build QA.

Later conservative post-audit review identified three high-confidence French correction candidates that are documented but **not yet applied** to the current production candidate:

- vocabulary rank 608 `situation`: replace the overbroad `situation (all meanings)` gloss with context-bounded learner senses;
- vocabulary rank 837 `bosser`: remove the misleading `emboss/dent` gloss and retain the modern informal `to work` sense;
- sentence rank 599 `Aide-moi avec mon devoir, s’il te plaît.`: replace the English-calque construction with standard `Aide-moi à faire mes devoirs, s’il te plaît.` while preserving the English meaning.

Arabic sentence rank 747 (`والديّ الاثنين`) remains a genuine human naturalness/register judgment and must not be auto-repaired from model/reference evidence alone.

The French external-verification instrumentation issue recorded on 2026-09-09 has since been corrected: the current French summary reports Lexique4 coverage for all 1,000 rows and no source-load problem. The external-verification queue remains a triage aid, not a correctness oracle.

Applying any of the three French correction candidates would create a changed candidate. It must therefore use a new exact incremental vocabulary lock for ranks 608 and 837, the normal sentence repair path for rank 599, an official fail-closed dry-run before any write, and then the established full rebuild, QA, manifest rebinding, and reviewer-package rebinding sequence.

No learner-facing CSV/PDF, release manifest, or human sign-off binding is changed merely by this status update.

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
