# LANG-WB v1.0 — Final Native-Speaker Review Packet

## Purpose

This packet defines the final human linguistic certification step for the Arabic, French, and Urdu v1.0 production-candidate workbooks.

All automated, structural, provenance, pronunciation, rendering, reproducibility, and source-locked row-decision gates are already separate evidence. This review must not be treated as a spot check or as a substitute for those gates. Its purpose is full learner-facing linguistic review by a qualified native or near-native expert.

For a concise participation walkthrough, see [`REVIEWER_ONBOARDING.md`](REVIEWER_ONBOARDING.md).

## Exact candidate being reviewed

Reviewers must review the exact current master workbook for their language and record the bound identifiers below in the sign-off record.

| Language | Master workbook | Git blob SHA | Sentence decision SHA-256 |
|---|---|---|---|
| Arabic | [`completed/languages/workbooks/v1.0/arabic/00_arabic_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/arabic/00_arabic_complete_master.pdf) | `3f7b761bdb5e5740274656c6fab83207ebe08cbf` | `3bf795fdf6c8c53536f8f2d3b6cfc9351d0e337c84cf7b9caf0891ff350d8c89` |
| French | [`completed/languages/workbooks/v1.0/french/00_french_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/french/00_french_complete_master.pdf) | `a1188f892af1cd2775f8fa38342ead69db8e7cc7` | `951f73421c348fba098f8acc1e973055e57a0c5c0e0f1dff90a897a509560506` |
| Urdu | [`completed/languages/workbooks/v1.0/urdu/00_urdu_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/urdu/00_urdu_complete_master.pdf) | `90f9765a028c85d296871c829d25d534b5c29101` | `3dcf44c6c4a6dfdf682565c5e2e6b2df18825ada7628561eb7461872891640d5` |

Release manifest: [`completed/languages/workbooks/v1.0/RELEASE_MANIFEST.json`](../../../completed/languages/workbooks/v1.0/RELEASE_MANIFEST.json).

The table above identifies the current candidate, but reviewers should use freshly generated `CANDIDATE_BINDINGS.json` values when filling a sign-off so stale hashes are never copied from documentation or an older review.

## Structured reviewer worksheets

For faster systematic review of the vocabulary and sentence banks, generate the current-candidate worksheets with:

```bash
python scripts/build_lang_wb_native_review_ledgers.py
```

Instructions are in [`native-review-ledgers/README.md`](native-review-ledgers/README.md). The generator creates one 2,000-item ledger per language: 1,000 vocabulary rows plus 1,000 sentence rows. It also creates `CANDIDATE_BINDINGS.json`, binding the worksheets to the current master-workbook, release-manifest, companion-CSV, and sentence-decision identifiers.

All reviewer fields are intentionally blank. The generator performs no linguistic adjudication and cannot create a PASS. The worksheets cover the structured vocabulary/sentence items only; the reviewer must still inspect the complete rendered master PDF for Foundations, pronunciation guidance, headings, instructions, and every other learner-facing element.

Validate a completed structured worksheet with:

```bash
python scripts/validate_lang_wb_native_review_ledger.py <arabic|french|urdu>
```

The validator rejects source drift and malformed review metadata; it returns success only when all 2,000 structured items are explicitly PASS. This is a structured-row preflight, not final certification.

If the human reviewer records FAIL/HOLD items, project only those explicit decisions into a compact remediation queue with:

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

- **PASS** means the reviewer completed a full-content review of the exact bound candidate and found no known learner-facing linguistic defects remaining.
- **FAIL** means one or more defects remain. Record each defect precisely enough to reproduce it: language, workbook section, page or item/rank, current text, defect type, explanation, and proposed correction where possible.
- **HOLD** means the reviewer cannot confidently adjudicate one or more items. Those items must remain explicit holds; uncertainty must not be converted into approval.
- Sampling, automated language-model review, deterministic checks, or previous editorial passes are supporting evidence only and do not satisfy this final human gate.

## Reviewer qualifications

Record the reviewer's language competence and relevant editing/teaching/linguistic experience. Native-speaker status is preferred; near-native expert review is acceptable only when the reviewer explicitly states the basis for competence. A reviewer should not certify a language they cannot independently judge for grammar, idiom, register, and pedagogical naturalness.

## Defect loop

If a reviewer reports any defect:

1. record it in a versioned correction record;
2. update the source-locked decision/curation data rather than patching only the PDF;
3. rebuild the affected workbook;
4. rerun the automated and rendered-output gates;
5. produce new artifact identifiers/hashes;
6. invalidate any sign-off bound to the superseded artifact;
7. repeat full human review as necessary for the changed candidate.

## Recording sign-offs

Use [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json) as the canonical schema and store completed records under [`native-signoffs/`](native-signoffs/). Sign-offs are immutable historical records: if a candidate changes or a later reviewer reaches a different outcome, add a new record rather than rewriting the old one.

Use current candidate values from `native-review-ledgers/CANDIDATE_BINDINGS.json`; the canonical template intentionally uses placeholders instead of embedding a candidate-specific hash that could later become stale.

`review_completed_utc` must be the real timezone-aware completion time. Reviews dated before the current candidate existed, materially future-dated timestamps, and ambiguous ties for the latest current-candidate review are rejected fail-closed.

The latest **unambiguous** review bound to the current candidate controls. A newer FAIL or HOLD therefore overrides an older PASS for the same candidate. A newer record bound to a superseded/stale candidate does not override a current-candidate review.

## Sign-off submission validation versus final promotion

Each newly submitted human record is validated independently with:

```bash
python scripts/validate_lang_wb_native_signoff.py path/to/signoff.json
```

That per-record validator confirms the current-candidate binding, timestamp, reviewer qualification fields, outcome rules, scope-field shape, and PASS/FAIL/HOLD requirements. A valid Arabic record can therefore be accepted while French and Urdu are still pending.

GitHub Actions runs this per-record check on sign-off submissions via [`.github/workflows/language-workbook-final-human-promotion.yml`](../../../.github/workflows/language-workbook-final-human-promotion.yml). That workflow also evaluates the overall promotion state, but an expected partial-review HOLD does **not** turn a valid single-language submission red.

Candidate/master/manifest changes are evaluated separately by [`.github/workflows/language-workbook-signoff-binding-status.yml`](../../../.github/workflows/language-workbook-signoff-binding-status.yml), where an expected human-review HOLD is likewise reported without treating an otherwise valid production candidate as a failed build.

The final all-language gate remains:

```bash
python scripts/workbook_final_human_promotion_gate.py
```

It independently recomputes current master-workbook Git blob hashes, reads current sentence-decision hashes from the release manifest, verifies release-manifest binding, checks reviewer qualifications and PASS scope attestations, enforces timestamp precedence, requires no PASS defects/holds, and selects the latest unambiguous current-candidate review for each language.

The command exits non-zero until Arabic, French, and Urdu all have valid latest PASS records. Its logic is exercised by a CI-only synthetic self-test in [`.github/workflows/language-workbook-final-human-promotion-selftest.yml`](../../../.github/workflows/language-workbook-final-human-promotion-selftest.yml); synthetic fixtures exist only inside the runner workspace and are never human certification records.

## Exact-commit release snapshot after human PASS

After the three-language human gate passes, build the final content-addressed release evidence with:

```bash
python scripts/build_lang_wb_final_release_snapshot.py \
  --output audit/language-workbooks/v1.0/FINAL_RELEASE_SNAPSHOT.json
```

The equivalent manual workflow is [`.github/workflows/language-workbook-final-release-snapshot.yml`](../../../.github/workflows/language-workbook-final-release-snapshot.yml).

This final step reruns the established production-candidate release audit and human-promotion gate, verifies that source-locked integrity and rendered-output visual evidence still apply, requires clean tracked release/sign-off inputs, and records the exact repository commit together with the release-tree, master-workbook, manifest, evidence, and sign-off hashes.

Because the repository's moving `main` branch is currently unprotected, the release must be identified by the **exact commit recorded in the successful snapshot**. A successful snapshot is not a claim that later `main` commits inherit release eligibility. Learner-facing PDF/CSV/manifest or source-locked curation drift fail-closes the snapshot; documentation-only drift does not falsely invalidate learner-facing evidence.

The snapshot logic has a dedicated synthetic CI self-test at [`.github/workflows/language-workbook-final-release-snapshot-selftest.yml`](../../../.github/workflows/language-workbook-final-release-snapshot-selftest.yml). Live workflow run `33317311123` passed the success path and fail-closed tests for learner CSV drift and a missing language PASS. These synthetic fixtures are ephemeral test data only and do not satisfy any human-review requirement.

## Promotion rule

LANG-WB v1.0 may be promoted beyond `production_candidate` only when:

- Arabic has a completed PASS sign-off;
- French has a completed PASS sign-off;
- Urdu has a completed PASS sign-off;
- all three sign-offs bind to the current candidate artifacts/decision hashes;
- no known learner-facing defect or unresolved hold remains;
- `python scripts/workbook_final_human_promotion_gate.py` returns PASS;
- post-sign-off release/integrity checks still pass; and
- `python scripts/build_lang_wb_final_release_snapshot.py` succeeds, binding the final release evidence to the exact commit being released.
