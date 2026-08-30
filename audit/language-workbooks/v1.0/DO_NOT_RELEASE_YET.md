# Production candidate — final linguistic sign-off pending

The v1.0 Arabic, French, and Urdu workbook set has passed the automated corpus, vocabulary, pronunciation, structural, rendering, reproducibility, publication, and rendered-output QA gates and is suitable for production-candidate review.

Do not describe the set as 100% linguistically certified or as having completed native-speaker sign-off until that human review is actually completed. This hold is limited to final independent linguistic certification rather than unresolved automated QA or build defects.

## Remaining release gate

Complete independent full-content linguistic review for all three languages using:

- [`REVIEWER_ONBOARDING.md`](REVIEWER_ONBOARDING.md) — practical reviewer start-to-finish instructions;
- [`FINAL_NATIVE_REVIEW_PACKET.md`](FINAL_NATIVE_REVIEW_PACKET.md) — exact artifact bindings, review scope, defect loop, and promotion rule;
- [`native-review-ledgers/README.md`](native-review-ledgers/README.md) — structured 2,000-item vocabulary/sentence worksheet workflow;
- [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json) — canonical immutable sign-off schema;
- [`native-signoffs/`](native-signoffs/) — immutable submitted human review records;
- [issue #106](https://github.com/ualispublishing/learning/issues/106) — Arabic/French/Urdu review tracker.

A PASS is valid only for the exact candidate identifiers recorded in the sign-off. If learner-facing content changes afterward, the superseded sign-off must not be carried forward automatically.

The overall release remains `production_candidate` until Arabic, French, and Urdu each have a valid latest PASS record and `python scripts/workbook_final_human_promotion_gate.py` passes.
