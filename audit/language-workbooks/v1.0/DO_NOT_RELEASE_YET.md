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

## Final release authorization

Passing the three-language human gate is necessary but not by itself the final release artifact. After all three genuine current-candidate PASS records exist, run:

```bash
python scripts/build_lang_wb_final_release_snapshot.py \
  --output audit/language-workbooks/v1.0/FINAL_RELEASE_SNAPSHOT.json
```

or manually dispatch [`.github/workflows/language-workbook-final-release-snapshot.yml`](../../../.github/workflows/language-workbook-final-release-snapshot.yml).

That final snapshot reruns the production and human gates, verifies that the final visual audit and source-locked integrity evidence still apply, requires clean tracked release/sign-off inputs, and binds the release to an exact Git commit plus file hashes. Because the repository's moving `main` branch is currently unprotected, release eligibility must be attached to the exact snapshot commit rather than to the phrase "latest main."

Do not remove this hold or promote beyond `production_candidate` unless the final snapshot itself succeeds for the exact candidate being released. A later learner-facing PDF/CSV/manifest or source-locked curation change requires fresh applicable evidence and, where candidate bindings change, fresh human sign-off.
