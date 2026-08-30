# Linguistic gate

Final LANG-WB v1.0 completion requires zero known learner-facing linguistic defects after independent full-content human review of the exact current candidate. Unknowns are held, not silently accepted.

## Required human evidence

Arabic, French, and Urdu are reviewed independently. Each language must have a valid latest human PASS record that:

- is submitted under [`native-signoffs/`](native-signoffs/) using [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json);
- binds to the exact current master-workbook Git blob, sentence-decision SHA-256, and release-manifest Git blob;
- records a real timezone-aware completion timestamp;
- records reviewer competence/qualification information;
- truthfully attests full learner-facing master-workbook review;
- contains no unresolved defects or holds for PASS.

A newer current-candidate FAIL or HOLD overrides an older PASS. Stale-candidate records do not certify a changed candidate. Future-dated or ambiguous latest timestamps fail closed.

## Reviewer workflow

Use:

1. [`REVIEWER_ONBOARDING.md`](REVIEWER_ONBOARDING.md)
2. [`FINAL_NATIVE_REVIEW_PACKET.md`](FINAL_NATIVE_REVIEW_PACKET.md)
3. [`native-review-ledgers/README.md`](native-review-ledgers/README.md)
4. [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json)

The structured ledgers cover 1,000 vocabulary rows and 1,000 sentence rows per language, but they do not replace review of Foundations, pronunciation guidance, headings, instructions, or other learner-facing material in the rendered master PDF.

## Automated enforcement

- `python scripts/validate_lang_wb_native_review_ledger.py <language>` validates a completed 2,000-row reviewer worksheet against current sources.
- `python scripts/validate_lang_wb_native_signoff.py <signoff.json>` validates one submitted human sign-off independently.
- `python scripts/workbook_final_human_promotion_gate.py` requires valid latest PASS records for all three languages before overall promotion.

Automation validates structure, binding, precedence, and completeness claims. It does not make the linguistic judgment itself.
