# LANG-WB v1.0 native sign-offs

Store completed human linguistic review records here as immutable JSON files using the schema in [`../FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](../FINAL_NATIVE_SIGNOFF_TEMPLATE.json).

Recommended filename format:

`<language>_<review-completed-UTC-date>_<reviewer-id>.json`

Examples:

- `arabic_2026-09-02_reviewer-a.json`
- `french_2026-09-03_reviewer-b.json`
- `urdu_2026-09-04_reviewer-c.json`

Rules:

1. Never overwrite or silently edit an earlier sign-off after the reviewed candidate changes; add a new immutable record instead.
2. Every record must bind to the exact master-workbook Git blob SHA, sentence-decision SHA-256, and release-manifest Git blob SHA reviewed.
3. Do not copy candidate hashes from an older sign-off or an old template. Generate the current reviewer bindings with `python scripts/build_lang_wb_native_review_ledgers.py` and use `../native-review-ledgers/CANDIDATE_BINDINGS.json` as the current-candidate binding source.
4. PASS is valid only after full learner-facing review with all scope attestations true and no defects or holds remaining.
5. FAIL and HOLD records are retained as review history and must not be deleted merely because a later PASS is obtained.
6. `review_completed_utc` must be the real timezone-aware completion time of that review. A timestamp before the bound candidate was generated, a materially future-dated timestamp, or an ambiguous tie for the latest current-candidate review is rejected fail-closed.
7. The latest **unambiguous** review record bound to the current candidate controls the final promotion gate; a newer FAIL/HOLD overrides an older PASS.
8. The structured 2,000-row ledger is a review aid and preflight, not the certification itself. The complete rendered master workbook still must be reviewed as described in [`../FINAL_NATIVE_REVIEW_PACKET.md`](../FINAL_NATIVE_REVIEW_PACKET.md).

Validate a completed structured worksheet first with:

```bash
python scripts/validate_lang_wb_native_review_ledger.py <arabic|french|urdu>
```

If the reviewer recorded FAIL/HOLD items, project them without reinterpretation with:

```bash
python scripts/extract_lang_wb_native_review_actions.py <arabic|french|urdu>
```

After the full human review and immutable sign-off record are complete, validate the current release state with:

```bash
python scripts/workbook_final_human_promotion_gate.py
```

The command exits non-zero until Arabic, French, and Urdu each have a valid latest PASS bound to the current production candidate.
