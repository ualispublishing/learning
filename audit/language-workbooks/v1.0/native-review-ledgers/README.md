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

## Validate a completed worksheet

Before creating a final language sign-off, run the source-bound preflight for that language:

```bash
python scripts/validate_lang_wb_native_review_ledger.py arabic
python scripts/validate_lang_wb_native_review_ledger.py french
python scripts/validate_lang_wb_native_review_ledger.py urdu
```

You may also provide an explicit ledger path as the second argument.

The validator checks that all 2,000 immutable source fields still match the current production candidate and that every review outcome is well formed. Its exit states are deliberately fail-closed:

- exit `0`: every structured row is explicitly `PASS` and source-bound;
- exit `2`: the ledger is source-valid but is incomplete or contains at least one `FAIL`/`HOLD`;
- exit `1`: malformed worksheet, source drift, invalid review metadata, or another validation error.

For `FAIL`, `defect_type` and `reviewer_notes` are required. For `HOLD`, `reviewer_notes` are required. A `PASS` row cannot simultaneously carry a defect classification or proposed correction. The validator writes a sibling `*_validation.json` report with counts and current candidate bindings.

## Extract reviewer-recorded remediation items

To turn explicit human `FAIL`/`HOLD` decisions into a compact correction queue without reinterpreting them, run:

```bash
python scripts/extract_lang_wb_native_review_actions.py arabic
python scripts/extract_lang_wb_native_review_actions.py french
python scripts/extract_lang_wb_native_review_actions.py urdu
```

The extractor first verifies that the worksheet still matches the current production candidate and that its review metadata is valid. It then writes a sibling `*_actions.json` containing only rows the human reviewer explicitly marked `FAIL` or `HOLD`, preserving the reviewer notes, defect type, proposed correction, source text, rank, and attribution. Unreviewed or PASS rows are not turned into action items, and the extractor performs no linguistic inference or status mutation.

Use these action files to drive the defect loop in the final review packet: repair the source-locked data, rebuild, rerun automated/render gates, regenerate candidate bindings, and re-review the changed candidate as required.

## Important limitation

These worksheets are an ergonomic aid, **not** the final certification artifact. They do not contain every learner-facing item in the rendered workbook. A qualified reviewer must also inspect the complete current master PDF, including Foundations, pronunciation guidance, headings, instructions, and any other learner-facing text or presentation that can affect correctness.

Even a structured-ledger exit `0` is only a preflight. The final release gate remains [`../FINAL_NATIVE_REVIEW_PACKET.md`](../FINAL_NATIVE_REVIEW_PACKET.md) plus an immutable sign-off derived from [`../FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](../FINAL_NATIVE_SIGNOFF_TEMPLATE.json). No generated ledger row is pre-approved, and generating, validating, or projecting a worksheet does not alter release status.

`CANDIDATE_BINDINGS.json` records the current master-workbook Git blob SHA, release-manifest Git blob SHA, source companion-CSV Git blob SHAs, and sentence-decision SHA-256 so a reviewer can confirm that their worksheet belongs to the exact candidate being certified.
