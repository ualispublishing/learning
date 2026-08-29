# LANG-WB v1.0 native-review ledgers

This directory is the output location for structured human-review worksheets generated from the current Arabic, French, and Urdu production-candidate companion CSVs.

Generate them with:

```bash
python scripts/build_lang_wb_native_review_ledgers.py
```

The generator produces:

- `arabic_native_review_ledger.csv`
- `french_native_review_ledger.csv`
- `urdu_native_review_ledger.csv`
- `CANDIDATE_BINDINGS.json`

Each language ledger contains exactly 2,000 structured learner items: 1,000 vocabulary rows followed by 1,000 sentence rows. Source text, English, POS/level, and sentence attribution are copied from the production-candidate companion CSVs. The reviewer columns are intentionally blank:

- `review_outcome` — reviewer enters `PASS`, `FAIL`, or `HOLD` per item;
- `defect_type` — concise classification when an item is not PASS;
- `reviewer_notes` — explanation/evidence;
- `proposed_correction` — correction when appropriate.

## Important limitation

These worksheets are an ergonomic aid, **not** the final certification artifact. They do not contain every learner-facing item in the rendered workbook. A qualified reviewer must also inspect the complete current master PDF, including Foundations, pronunciation guidance, headings, instructions, and any other learner-facing text or presentation that can affect correctness.

The final release gate remains [`../FINAL_NATIVE_REVIEW_PACKET.md`](../FINAL_NATIVE_REVIEW_PACKET.md) plus an immutable sign-off derived from [`../FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](../FINAL_NATIVE_SIGNOFF_TEMPLATE.json). No generated ledger row is pre-approved, and generating a worksheet does not alter release status.

`CANDIDATE_BINDINGS.json` records the current master-workbook Git blob SHA, release-manifest Git blob SHA, source companion-CSV Git blob SHAs, and sentence-decision SHA-256 so a reviewer can confirm that their worksheet belongs to the exact candidate being certified.
