# LANG-WB v1.0 — Native / Near-Native Reviewer Onboarding

Thank you for considering an independent linguistic review of the Arabic, French, or Urdu LANG-WB v1.0 workbook.

The current release is a **production candidate**, not a claimed human-certified final release. Automated corpus, provenance, structural, pronunciation, rendering, reproducibility, and editorial checks have already been run separately. The purpose of this review is the remaining human linguistic gate: an independent, full learner-facing review by someone who can confidently judge grammar, meaning, idiom, register, and pedagogical naturalness in the language being reviewed.

You may review **one language only**. Arabic, French, and Urdu are certified independently.

## Fastest start: use a self-contained reviewer bundle

A reviewer does not need to assemble the workbook, worksheet, candidate hashes, sign-off draft, and instructions manually.

GitHub Actions provides [`LANG-WB reviewer packages`](../../../.github/workflows/language-workbook-reviewer-package.yml). Run the workflow to generate separate Arabic, French, and Urdu artifacts. Each artifact contains a self-contained ZIP for one language with the complete master PDF, exact vocabulary/sentence companion CSVs, blank 2,000-item review ledger, current candidate binding, release manifest, intentionally incomplete sign-off draft, canonical sign-off template, review documents, PR checklist, bundle manifest, and SHA-256 checksums.

A normal Git checkout can build the same package locally with one command:

```bash
python scripts/build_lang_wb_reviewer_bundle.py arabic --output-root ~/Desktop
# or: french / urdu
```

### If the Actions artifact is not available to you

GitHub's browser artifact download can require a signed-in account with repository read access. The language-specific review issue provides an **exact public source-archive URL and exact commit SHA** for the currently verified reviewer package.

Download that exact archive, extract it, open the extracted repository directory, and run:

```bash
python scripts/build_lang_wb_reviewer_bundle.py arabic \
  --repository-commit-sha <EXACT_COMMIT_FROM_THE_LANGUAGE_ISSUE> \
  --output-root ~/Desktop
# or: french / urdu
```

A GitHub source archive does not contain `.git` metadata. The bundle builder therefore **fails closed** when neither Git metadata nor an explicit exact commit is available. If `.git` is present and you also supply `--repository-commit-sha`, the explicit value must match the checkout's actual HEAD. This prevents an archive-built bundle from carrying a missing or misleading repository-commit binding.

Do not use a moving `main` source archive as a substitute for the exact verified commit in the language issue. If the candidate or reviewer-package inputs change, use the newly verified commit/package instead.

The generated draft contains **no human outcome, reviewer identity/qualification, or completed scope attestations**. It is deliberately invalid as a sign-off until a qualified reviewer completes the required review and fills the human-only fields truthfully.

Language-specific work trackers:

- Arabic: [issue #114](https://github.com/ualispublishing/learning/issues/114)
- French: [issue #115](https://github.com/ualispublishing/learning/issues/115)
- Urdu: [issue #116](https://github.com/ualispublishing/learning/issues/116)

Parent release tracker: [issue #106](https://github.com/ualispublishing/learning/issues/106).

## 1. Confirm that you are an appropriate reviewer

A reviewer should be either:

- a native speaker with sufficient literacy to judge instructional language carefully; or
- a near-native expert who can state a credible qualification basis, such as advanced language study, teaching, translation, editing, linguistics, or sustained professional use.

You do not need to publish unnecessary personal information. The sign-off schema allows a name **or reviewer identifier**, plus a concise competence/qualification basis.

Do not certify a language if you cannot independently judge grammar, morphology, spelling, idiom, register, translation fidelity, and learner appropriateness.

## 2. Read the canonical review rules

Start with:

- [`FINAL_NATIVE_REVIEW_PACKET.md`](FINAL_NATIVE_REVIEW_PACKET.md)
- [`CORRECTNESS_STANDARD.md`](CORRECTNESS_STANDARD.md)
- [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json)

The final review is **not a sample**. PASS requires review of the complete learner-facing current master workbook.

## 3. Review the exact current candidate

Current master workbooks are under:

- Arabic: [`../../../completed/languages/workbooks/v1.0/arabic/00_arabic_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/arabic/00_arabic_complete_master.pdf)
- French: [`../../../completed/languages/workbooks/v1.0/french/00_french_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/french/00_french_complete_master.pdf)
- Urdu: [`../../../completed/languages/workbooks/v1.0/urdu/00_urdu_complete_master.pdf`](../../../completed/languages/workbooks/v1.0/urdu/00_urdu_complete_master.pdf)

Do not change the master PDF, release manifest, companion CSVs, or decision ledgers in the same change that records your sign-off. A candidate change invalidates the artifact hashes and requires fresh binding/review.

## 4. Use the structured worksheet for the 2,000 row-based items

If you are not using the self-contained bundle, generate the current worksheets from the repository root:

```bash
python scripts/build_lang_wb_native_review_ledgers.py
```

This creates a 2,000-item worksheet for each language: 1,000 vocabulary rows plus 1,000 sentence rows. Reviewer fields are blank by design. Instructions are in [`native-review-ledgers/README.md`](native-review-ledgers/README.md).

For every structured row, record `PASS`, `FAIL`, or `HOLD` yourself. The tooling never fills this decision for you.

The worksheet does **not** replace review of the full PDF. Foundations, pronunciation guidance, headings, instructions, and other learner-facing material must also be checked in the rendered master.

## 5. Validate your completed worksheet

Run the validator for the language you reviewed:

```bash
python scripts/validate_lang_wb_native_review_ledger.py arabic
# or: french / urdu
```

A structured worksheet returns:

- exit `0` only if all 2,000 rows are explicitly PASS and still match the current candidate;
- exit `2` if review is incomplete or contains explicit FAIL/HOLD items;
- exit `1` for malformed data, source drift, or invalid review metadata.

If you recorded FAIL/HOLD items, generate a compact remediation projection with:

```bash
python scripts/extract_lang_wb_native_review_actions.py <language>
```

This copies only your explicit action items; it does not reinterpret them.

## 6. If you find a defect or uncertainty

Do **not** convert uncertainty into PASS.

Use FAIL for a defect you can identify, or HOLD when an item needs further adjudication. Include enough detail to reproduce the concern. The project can then repair the source-locked data, rebuild the workbook, rerun automated/render gates, and provide a newly bound candidate for review.

A reviewer is not required to implement the source repair personally.

## 7. Prepare and complete your immutable sign-off

If you are not using the bundle's already bound incomplete draft, generate one with:

```bash
python scripts/prepare_lang_wb_native_signoff_draft.py arabic
# or: french / urdu
```

The draft is written under `native-review-ledgers/` by default. It fills only deterministic candidate bindings. Its review outcome and completion time are blank, reviewer qualification fields are blank, and every scope attestation is `false`; an untouched draft is therefore deliberately rejected by the human sign-off validator and cannot certify anything.

After you complete the required review, use that draft or [`FINAL_NATIVE_SIGNOFF_TEMPLATE.json`](FINAL_NATIVE_SIGNOFF_TEMPLATE.json) to create a **new** file under [`native-signoffs/`](native-signoffs/). The filename must begin with the language declared inside the JSON: `arabic_`, `french_`, or `urdu_`. The required convention is documented in [`native-signoffs/README.md`](native-signoffs/README.md), and CI rejects a filename/language mismatch.

If you prepare the record manually, use current candidate identifiers from the generated:

`native-review-ledgers/CANDIDATE_BINDINGS.json`

Do not copy hashes from an older sign-off.

For PASS:

- all required scope attestations must truthfully be `true`;
- `defects` must be empty;
- `holds` must be empty;
- the completion timestamp must be the real timezone-aware review completion time;
- the attestation must remain accurate.

FAIL/HOLD records are also useful review evidence and are retained rather than erased after later remediation.

Once a sign-off record is committed, it is immutable. CI rejects later modification, rename, or deletion; a later review result must be stored as a new record.

## 8. Submit the sign-off without changing the candidate

Prefer a focused pull request that **adds** the new immutable sign-off record and, when useful, reviewer-authored remediation evidence. Avoid changing the workbook candidate in that same PR.

Use [`.github/PULL_REQUEST_TEMPLATE/lang-wb-native-signoff.md`](../../../.github/PULL_REQUEST_TEMPLATE/lang-wb-native-signoff.md) as the submission checklist.

### If you do not use GitHub

You may return the completed worksheet and your completed sign-off JSON to the project maintainer through an agreed transfer channel. Include the final sign-off file as you authored it and, when practical, its SHA-256 checksum so the maintainer can verify that the repository copy is unchanged.

A maintainer may add that **reviewer-authored record unchanged** to `native-signoffs/` and run the same validators/CI. The GitHub account that commits the file is not the reviewer identity; the reviewer's `name_or_identifier`, qualification basis, outcome, timestamp, exact candidate binding, scope attestations, defects/holds, and attestation inside the JSON remain authoritative.

The maintainer must **not** fill, reinterpret, upgrade, or convert any human-only field on the reviewer's behalf. In particular, a maintainer must never convert FAIL/HOLD/uncertainty into PASS. If the returned record is incomplete, malformed, stale, or fails validation, it must be returned for reviewer correction or retained as non-PASS rather than silently repaired into a certification.

CI validates added sign-off records on pull requests before merge and again on pushes. A valid Arabic sign-off does **not** fail merely because French and Urdu are still pending. The overall release remains on HOLD until all three languages have valid latest PASS records bound to the same current candidate.

You can validate your individual record locally with:

```bash
python scripts/validate_lang_wb_native_signoff.py audit/language-workbooks/v1.0/native-signoffs/<file>.json
```

The final all-language check is:

```bash
python scripts/workbook_final_human_promotion_gate.py
```

## 9. What PASS does and does not mean

A human PASS means the qualified reviewer completed the stated full-content review of the exact bound candidate and, in their independent judgment, no known learner-facing linguistic defect or unresolved hold remains.

It is evidence of careful human certification, not a claim of metaphysical or mathematical impossibility of error. The repository deliberately distinguishes this human judgment from automated QA and avoids claiming that automation alone proves perfect linguistic correctness.

Progress for the three language reviews is tracked in [issue #106](https://github.com/ualispublishing/learning/issues/106).
