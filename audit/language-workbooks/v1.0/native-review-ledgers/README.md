# LANG-WB v1.0 native-review ledgers

This directory contains structured human-review worksheets and current-candidate binding artifacts for the Arabic, French, and Urdu v1.0 production candidate.

Generate the worksheets with:

```bash
python scripts/build_lang_wb_native_review_ledgers.py
```

The production build also creates one deterministic sentence-decision snapshot per language:

- `arabic_resolved_sentence_decisions.json`
- `french_resolved_sentence_decisions.json`
- `urdu_resolved_sentence_decisions.json`

Each snapshot is derived from the exact 1,000-row row-by-row sentence adjudication ledgers and must match the exact current learner-facing sentence companion CSV at every rank. If any resolved adjudication and learner-facing row disagree, snapshot generation and the release gate fail closed.

The older `curation/language-workbooks/v1.0/*_sentence_row_decisions.json` files are retained as historical provenance. They are not the binding authority for a changed current candidate.

The worksheet generator produces:

- `arabic_native_review_ledger.csv`
- `french_native_review_ledger.csv`
- `urdu_native_review_ledger.csv`
- `CANDIDATE_BINDINGS.json`

Each language worksheet contains exactly 2,000 structured learner items: 1,000 vocabulary rows followed by 1,000 sentence rows. Source text, English, POS/level, and sentence attribution are copied from the current production-candidate companion CSVs. The reviewer columns are intentionally blank:

- `review_outcome` — reviewer enters `PASS`, `FAIL`, or `HOLD` per item;
- `defect_type` — concise classification when an item is not PASS;
- `reviewer_notes` — explanation/evidence;
- `proposed_correction` — correction when appropriate.

Before writing a worksheet, the generator validates the candidate sentence-decision snapshot against the manifest, current adjudication ledgers, and learner-facing sentence CSV. It performs no linguistic adjudication and cannot create a PASS.

## Validate a completed worksheet

Before creating a final language sign-off, run the source-bound preflight:

```bash
python scripts/validate_lang_wb_native_review_ledger.py arabic
python scripts/validate_lang_wb_native_review_ledger.py french
python scripts/validate_lang_wb_native_review_ledger.py urdu
```

You may provide an explicit ledger path as the second argument.

The validator checks all 2,000 immutable source fields against the current candidate and validates review metadata. Exit states are fail-closed:

- exit `0`: every structured row is explicitly `PASS` and source-bound;
- exit `2`: the ledger is source-valid but incomplete or contains at least one `FAIL`/`HOLD`;
- exit `1`: malformed worksheet, source/binding drift, invalid review metadata, or another validation error.

For `FAIL`, `defect_type` and `reviewer_notes` are required. For `HOLD`, `reviewer_notes` are required. A `PASS` row cannot simultaneously carry a defect classification or proposed correction.

## Extract reviewer-recorded remediation items

To project explicit human `FAIL`/`HOLD` decisions into a compact correction queue without reinterpreting them, run:

```bash
python scripts/extract_lang_wb_native_review_actions.py arabic
python scripts/extract_lang_wb_native_review_actions.py french
python scripts/extract_lang_wb_native_review_actions.py urdu
```

The extractor performs no linguistic inference or status mutation. Use those action files to drive the defect loop: repair authoritative source/adjudication data, rebuild, rerun automated/render/binding gates, regenerate current bindings, and re-review the changed candidate as required.

## Important limitation

These worksheets are an ergonomic aid, **not** final certification. They do not contain every learner-facing item in the rendered workbook. A qualified reviewer must also inspect the complete current master PDF, including Foundations, pronunciation guidance, headings, instructions, and any other learner-facing text or presentation that can affect correctness.

Even a structured-ledger exit `0` is only a preflight. The final release gate remains [`../FINAL_NATIVE_REVIEW_PACKET.md`](../FINAL_NATIVE_REVIEW_PACKET.md) plus an immutable sign-off derived from [`../FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](../FINAL_NATIVE_SIGNOFF_TEMPLATE.json). Generating, validating, or projecting a worksheet does not alter release status.

`CANDIDATE_BINDINGS.json` records the exact current master-workbook Git blob SHA, release-manifest Git blob SHA, source companion-CSV Git blob SHAs, sentence-decision snapshot path/schema/SHA-256, and adjudication status counts so a reviewer can confirm that their worksheet belongs to the exact candidate being certified.
