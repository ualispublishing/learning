# Sentence row-decision compilation

All three 1,000-row sentence banks have completed first-pass row-by-row editorial screening as of 2026-08-23.

The authoritative correction workflow is now:

1. Compile exactly one status for every audited rank using `scripts/compile_sentence_row_decisions_v1.py`.
2. Treat `KEEP` as unchanged only because that rank was inside a completed audit range and no issue was recorded.
3. Treat `CORRECT_PENDING_SECOND_PASS`, `REPLACE_PENDING_SECOND_PASS`, and `NATIVE_REVIEW` as release blockers.
4. Verify each non-KEEP row against its recorded audit finding/recommendation before promotion.
5. Corrections/replacements must come from that row's audit decision; regeneration must not independently invent a different edit.
6. Regenerate learner artifacts only after every row has a resolved, approved state.

This file also intentionally triggers the row-decision compilation workflow after the workflow was installed.
