# LANG-WB v1.0 — Final Native-Speaker Review Packet

## Purpose

This packet defines the final independent linguistic certification step for the Arabic, French, and Urdu v1.0 production-candidate workbooks.

Automated, structural, provenance, pronunciation, rendering, reproducibility, and row-adjudication gates are separate evidence. They do not replace full learner-facing review by a qualified native or near-native expert.

For a concise participation walkthrough, see [`REVIEWER_ONBOARDING.md`](REVIEWER_ONBOARDING.md).

## Exact candidate being reviewed

Review the exact current master workbook for the assigned language:

- Arabic: [`completed/languages/workbooks/v1.0/arabic/00_arabic_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/arabic/00_arabic_complete_master.pdf)
- French: [`completed/languages/workbooks/v1.0/french/00_french_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/french/00_french_complete_master.pdf)
- Urdu: [`completed/languages/workbooks/v1.0/urdu/00_urdu_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/urdu/00_urdu_complete_master.pdf)

Release manifest: [`completed/languages/workbooks/v1.0/RELEASE_MANIFEST.json`](../../../completed/languages/workbooks/v1.0/RELEASE_MANIFEST.json).

**Do not copy candidate hashes from this document or from an older review.** Candidate-specific hashes intentionally are not hardcoded here. Generate or use the current [`native-review-ledgers/CANDIDATE_BINDINGS.json`](native-review-ledgers/CANDIDATE_BINDINGS.json) and copy the exact master-workbook Git blob SHA, release-manifest Git blob SHA, and sentence-decision SHA-256 from that file into the sign-off record.

The current sentence-decision SHA-256 binds a deterministic `*_resolved_sentence_decisions.json` snapshot generated from the exact 1,000-row row-by-row sentence adjudications and the exact current learner-facing sentence companion CSV. The older `curation/language-workbooks/v1.0/*_sentence_row_decisions.json` files remain historical provenance; they are **not** the authority for a changed current candidate.

The production build must fail closed if the resolved adjudications, learner-facing sentence CSV, generated decision snapshot, QA metadata, or manifest binding disagree.

## Structured reviewer worksheets

Generate current-candidate worksheets with:

```bash
python scripts/build_lang_wb_native_review_ledgers.py
```

Instructions are in [`native-review-ledgers/README.md`](native-review-ledgers/README.md). The generator creates one 2,000-item worksheet per language: 1,000 vocabulary rows plus 1,000 sentence rows. It also creates `CANDIDATE_BINDINGS.json`.

The generator performs no linguistic adjudication and cannot create a PASS. It first validates the current candidate decision snapshot against the exact row-by-row adjudications and learner-facing sentence bank. All reviewer fields remain blank.

Validate a completed worksheet with:

```bash
python scripts/validate_lang_wb_native_review_ledger.py <arabic|french|urdu>
```

The validator rejects source/binding drift and malformed review metadata; it returns success only when all 2,000 structured items are explicitly PASS. This remains a structured-row preflight, not final certification.

If the reviewer records FAIL/HOLD items, project only those explicit decisions into a remediation queue with:

```bash
python scripts/extract_lang_wb_native_review_actions.py <arabic|french|urdu>
```

The extractor performs no linguistic inference and does not alter reviewer decisions.

## Required review scope

Review the complete learner-facing master workbook, not a sample. Check every vocabulary item, translation, example, sentence pair, prompt, answer, explanation, heading, pronunciation statement, and other instructional text that could affect a learner.

At minimum, adjudicate the correctness dimensions in [`CORRECTNESS_STANDARD.md`](CORRECTNESS_STANDARD.md):

1. semantic accuracy and translation fidelity;
2. grammar and morphology;
3. spelling and orthography;
4. naturalness, idiomaticity, and register;
5. learner/progression appropriateness;
6. prompt-answer consistency;
7. duplicate, filler, malformed, or misleading material;
8. Arabic/Urdu script hygiene and punctuation where applicable;
9. French accents, agreement, conjugation, contractions, and idiomatic usage;
10. misleading cultural, factual, or pedagogical framing.

## Review outcome rules

- **PASS**: full-content review of the exact bound candidate is complete and no known learner-facing linguistic defect or unresolved hold remains.
- **FAIL**: one or more defects remain. Record language, section/page or rank, current text, defect type, explanation, and a proposed correction where possible.
- **HOLD**: one or more items cannot be confidently adjudicated. Keep the uncertainty explicit; do not convert it to approval.
- Sampling, automated/model review, deterministic checks, or previous editorial passes are supporting evidence only and do not satisfy this final human gate.

## Reviewer qualifications

Record the reviewer's language competence and relevant editing, teaching, or linguistic experience. Native-speaker status is preferred. Near-native expert review is acceptable only when the reviewer explicitly states the basis for competence. A reviewer must be able to judge grammar, idiom, register, and pedagogical naturalness independently.

## Defect loop

If a reviewer reports a defect:

1. record it in a versioned correction record;
2. update the current authoritative source/adjudication data rather than patching only a PDF;
3. preserve older curation/review records as immutable history rather than rewriting prior approvals;
4. rebuild the affected workbook;
5. rerun automated, rendered-output, and candidate-decision-binding gates;
6. generate new decision snapshots, manifest bindings, and artifact identifiers;
7. invalidate any sign-off bound to a superseded candidate; and
8. repeat human review as required for the changed candidate.

## Recording sign-offs

Use [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json) as the canonical schema and store completed records under [`native-signoffs/`](native-signoffs/). Sign-offs are immutable historical records: if the candidate changes or a later reviewer reaches a different outcome, add a new record rather than rewriting the old one.

Use exact current values from `native-review-ledgers/CANDIDATE_BINDINGS.json`. The template intentionally uses placeholders so candidate-specific hashes cannot become stale in the template.

`review_completed_utc` must be the real timezone-aware completion time. Reviews dated before the candidate existed, materially future-dated timestamps, and ambiguous ties for the latest current-candidate review are rejected fail-closed.

The latest **unambiguous** structurally valid review bound to the current candidate controls. A newer FAIL or HOLD therefore overrides an older PASS for that same candidate. A record bound to a superseded candidate does not control the current candidate.

## Sign-off validation versus final promotion

Validate each newly submitted human record independently with:

```bash
python scripts/validate_lang_wb_native_signoff.py path/to/signoff.json
```

GitHub Actions also checks sign-off submissions through [`.github/workflows/language-workbook-final-human-promotion.yml`](../../../.github/workflows/language-workbook-final-human-promotion.yml).

Candidate/master/manifest binding status is evaluated separately by [`.github/workflows/language-workbook-signoff-binding-status.yml`](../../../.github/workflows/language-workbook-signoff-binding-status.yml). A binding mismatch is a real hold and must not be bypassed merely because older automated or human evidence passed.

The final all-language gate remains:

```bash
python scripts/workbook_final_human_promotion_gate.py
```

It recomputes current master-workbook Git blob hashes, reads the current candidate decision hashes from the release manifest, verifies manifest binding, checks reviewer qualification/scope/outcome/timestamps, and selects the latest unambiguous current-candidate review for each language.

The command exits non-zero until Arabic, French, and Urdu all have valid latest PASS records. Synthetic CI fixtures are test evidence only and never constitute human certification.

## Exact-commit release snapshot after human PASS

After the three-language human gate passes, build the final content-addressed release evidence with:

```bash
python scripts/build_lang_wb_final_release_snapshot.py \
  --output audit/language-workbooks/v1.0/FINAL_RELEASE_SNAPSHOT.json
```

The equivalent manual workflow is [`.github/workflows/language-workbook-final-release-snapshot.yml`](../../../.github/workflows/language-workbook-final-release-snapshot.yml).

This step reruns production-candidate and human-promotion gates and records the exact repository commit together with release-tree, master-workbook, manifest, evidence, decision, and sign-off bindings.

A successful snapshot applies only to the exact recorded commit. Later commits do not inherit release eligibility automatically.

## Promotion rule

LANG-WB v1.0 may be promoted beyond `production_candidate` only when:

- Arabic, French, and Urdu each have a completed latest PASS sign-off;
- all three sign-offs bind to the exact current master, current candidate sentence-decision snapshot, and current release manifest;
- no known learner-facing defect or unresolved hold remains;
- the current candidate decision snapshots validate against all 3,000 resolved row-by-row adjudications and learner-facing sentence rows;
- `python scripts/workbook_final_human_promotion_gate.py` returns PASS;
- post-sign-off release/integrity checks still pass; and
- `python scripts/build_lang_wb_final_release_snapshot.py` succeeds for the exact commit being released.

Until then, the release remains `production_candidate`.
