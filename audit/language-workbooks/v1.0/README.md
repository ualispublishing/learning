# LANG-WB v1.0 audit and release evidence

This directory is the canonical audit/release-evidence hub for the Arabic, French, and Urdu LANG-WB v1.0 workbooks.

## Current release state

- Release: `v1.0`
- Status: `production_candidate`
- Automated/deterministic, source-locked editorial, pronunciation, structural/render, reproducibility, publication, and final rendered-output QA: **PASS**
- Unresolved sentence rows: **0**
- Remaining gate: independent full-content human linguistic review for Arabic, French, and Urdu

The current candidate must not be described as independently native-speaker certified until all three languages have valid latest PASS sign-offs and the final human promotion gate passes.

## Start here

For current status and release boundaries:

- [`REVIEW_STATUS.md`](REVIEW_STATUS.md) — concise current QA/human-review status.
- [`DO_NOT_RELEASE_YET.md`](DO_NOT_RELEASE_YET.md) — explicit production-candidate hold and remaining release gate.
- [`LINGUISTIC_GATE.md`](LINGUISTIC_GATE.md) — final linguistic completion rules and automated enforcement.
- [`CORRECTNESS_STANDARD.md`](CORRECTNESS_STANDARD.md) — learner-facing correctness dimensions.
- [`QA_REPORT.md`](QA_REPORT.md) — current source/corpus/pronunciation/PDF QA summary.
- [`final_visual_audit_20260829.json`](final_visual_audit_20260829.json) — final rendered-output visual QA evidence.

## Independent human review

A qualified Arabic, French, or Urdu reviewer should use:

- [`REVIEWER_ONBOARDING.md`](REVIEWER_ONBOARDING.md) — practical start-to-finish instructions.
- [`FINAL_NATIVE_REVIEW_PACKET.md`](FINAL_NATIVE_REVIEW_PACKET.md) — canonical full-content review scope, artifact binding, and defect loop.
- [`native-review-ledgers/README.md`](native-review-ledgers/README.md) — generated 2,000-item structured worksheet workflow.
- [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json) — immutable sign-off schema.
- [`native-signoffs/`](native-signoffs/) — submitted immutable human review records.
- [issue #106](https://github.com/ualispublishing/learning/issues/106) — Arabic/French/Urdu human-review tracker.

Relevant preparation and validation commands:

```bash
python scripts/build_lang_wb_native_review_ledgers.py
python scripts/validate_lang_wb_native_review_ledger.py <language>
python scripts/prepare_lang_wb_native_signoff_draft.py <language>
python scripts/validate_lang_wb_native_signoff.py <signoff.json>
python scripts/validate_lang_wb_signoff_diff.py <base-ref> <head-ref>
python scripts/workbook_final_human_promotion_gate.py
python scripts/validate_lang_wb_expected_human_hold.py
```

`prepare_lang_wb_native_signoff_draft.py` fills only deterministic current-candidate bindings. Human outcome/time/qualification fields remain incomplete and all scope attestations remain false; an untouched generated draft is deliberately invalid as a human sign-off.

The enforcement chain checks worksheet/sign-off structure, source and artifact binding, filename discoverability, timestamps, latest-review precedence, append-only sign-off history, all-language promotion conditions, and whether a release HOLD is genuinely the expected pending-human-review state. Relevant pull requests are checked before merge, and the same safeguards run again on pushes.

Synthetic CI self-tests verify these controls without adding synthetic human certification to repository history. Automation does not make the human linguistic judgment.

## Exact-commit final release snapshot

After Arabic, French, and Urdu all have valid latest current-candidate PASS sign-offs, create the final release attestation with:

```bash
python scripts/build_lang_wb_final_release_snapshot.py \
  --output audit/language-workbooks/v1.0/FINAL_RELEASE_SNAPSHOT.json
```

The same gate can be run through [`.github/workflows/language-workbook-final-release-snapshot.yml`](../../../.github/workflows/language-workbook-final-release-snapshot.yml). It reruns the established production-candidate release audit and final-human gate, verifies source-locked integrity and final visual-audit applicability, requires clean tracked release/sign-off inputs, and hashes the complete tracked v1.0 release tree. The resulting attestation identifies the exact repository commit, master PDFs, release manifest, human sign-offs, gate evidence, and canonical release-tree SHA-256.

The repository's moving `main` branch is currently not protected by required status checks. Therefore final release evidence must be interpreted against the **exact commit recorded in the snapshot**, not merely against whatever commit later becomes `main`. The snapshot is content-addressed specifically to remove that moving-branch ambiguity; it does not claim that `main` itself is immutable.

Drift handling is deliberately scoped to learner-facing release integrity:

- PDF changes after the recorded visual-audit production commit invalidate the visual-audit binding;
- release CSV or `RELEASE_MANIFEST.json` changes after the source-locked production commit invalidate source/integrity evidence;
- source-locked curation changes invalidate the integrity evidence;
- documentation-only changes such as the workbook hub README do not falsely invalidate learner-facing output evidence.

The snapshot implementation is exercised by [`.github/workflows/language-workbook-final-release-snapshot-selftest.yml`](../../../.github/workflows/language-workbook-final-release-snapshot-selftest.yml). Live run `33317311123` passed on 2026-08-30, demonstrating that an exact-commit snapshot succeeds with three synthetic current-candidate PASS fixtures, while learner CSV drift and a missing language PASS are rejected. The fixtures exist only in the runner workspace and are not human certification records.

No `FINAL_RELEASE_SNAPSHOT.json` should be created or treated as release authorization while genuine independent human sign-offs are still missing.

## Editorial/source-locked audit evidence

- [`AUDIT_SCOPE.md`](AUDIT_SCOPE.md) — learner-facing content covered by the audit program.
- [`AUDIT_METHOD.md`](AUDIT_METHOD.md) — source-locked editorial row-review method and its distinction from final human review.
- `curation/language-workbooks/v1.0/` — source-locked decisions, approvals, overrides, and review-state records outside this audit directory.

## Historical records

Files with explicit earlier dates or build-trigger timestamps, such as `ACTIVE_AUDIT_NOTE_2026-08-23.md`, `PROGRESS_2026-08-23.md`, and `BUILD_TRIGGER.md`, are retained as historical audit/build evidence. They should not be treated as the current release-status source when they conflict with the current files listed above.

For the workbook materials themselves, use [`completed/languages/workbooks/v1.0/`](../../../completed/languages/workbooks/v1.0/).
