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
3. PASS is valid only after full learner-facing review with all scope attestations true and no defects or holds remaining.
4. FAIL and HOLD records are retained as review history and must not be deleted merely because a later PASS is obtained.
5. The latest review record bound to the current candidate controls the final promotion gate; a newer FAIL/HOLD overrides an older PASS.

Validate the current release state with:

```bash
python scripts/workbook_final_human_promotion_gate.py
```

The command exits non-zero until Arabic, French, and Urdu each have a valid latest PASS bound to the current production candidate.
