# Language Workbooks v1.0

Production-candidate workbooks for Arabic, French, and Urdu. Each language includes one complete master PDF, 13 split PDFs, a 1,000-entry vocabulary companion CSV, and a 1,000-sentence companion CSV.

## Start here

Use this page as the single entry point for the LANG-WB v1.0 materials.

| Language | Complete workbook | All language files |
|---|---|---|
| Arabic | [`00_arabic_complete_master.pdf`](arabic/00_arabic_complete_master.pdf) | [`arabic/`](arabic/) |
| French | [`00_french_complete_master.pdf`](french/00_french_complete_master.pdf) | [`french/`](french/) |
| Urdu | [`00_urdu_complete_master.pdf`](urdu/00_urdu_complete_master.pdf) | [`urdu/`](urdu/) |

Each language folder contains the master workbook, Foundations, the split vocabulary and sentence PDFs, and the companion CSV files.

For release state and verification material:

- [`RELEASE_MANIFEST.json`](RELEASE_MANIFEST.json) — current v1.0 production-candidate state and source/provenance summary.
- [`audit/language-workbooks/v1.0/`](../../../../audit/language-workbooks/v1.0/) — QA, integrity, render, pronunciation, visual-audit, human-sign-off, and exact-commit release-gate evidence.
- [`curation/language-workbooks/v1.0/`](../../../../curation/language-workbooks/v1.0/) — source-locked row decisions, approvals, overrides, and review-state records.
- [`FINAL_NATIVE_REVIEW_PACKET.md`](../../../../audit/language-workbooks/v1.0/FINAL_NATIVE_REVIEW_PACKET.md) — exact remaining human linguistic sign-off procedure and final release-snapshot step.
- [`REVIEWER_ONBOARDING.md`](../../../../audit/language-workbooks/v1.0/REVIEWER_ONBOARDING.md) — concise public instructions for a qualified Arabic, French, or Urdu native/near-native reviewer.
- [`native-review-ledgers/`](../../../../audit/language-workbooks/v1.0/native-review-ledgers/) — structured reviewer-worksheet instructions; generate current 2,000-item worksheets with `python scripts/build_lang_wb_native_review_ledgers.py`.
- [Final native-speaker sign-off tracker — issue #106](https://github.com/ualispublishing/learning/issues/106) — Arabic/French/Urdu completion checklist.
- [Final release snapshot workflow](../../../../.github/workflows/language-workbook-final-release-snapshot.yml) — after all three genuine human PASS records exist, build content-addressed evidence for the exact commit being released.

Vocabulary comes from the repository's audited top-1,000 learner decks. Arabic and French sentence pairs originate from the ManyThings bilingual exports of the Tatoeba Project and retain supplied sentence-level attribution under CC BY 2.0 France. Urdu v1.0 uses UALIS Publishing original controlled learner sentences; those rows retain UALIS source provenance and are not represented as third-party Tatoeba quotations.

The v1.0 production sentence corpus is fixed by a versioned 1,000-row source-locked decision ledger per language. KEEP rows remain exact. Approved corrections preserve the source provenance and are explicitly marked as editorial adaptations.

Each language includes a source-backed pronunciation quick-start in Foundations using broad IPA and articulatory guidance. Sentence drills remain in normal target-language spelling rather than introducing ad-hoc romanization.

The production build checks row counts, target/English uniqueness, all-row source provenance, applicable external-license attribution, pronunciation-guide integrity, PDF structure, and exact production-to-decision alignment. Independent native-speaker certification remains separate from these automated and editorial controls; no absolute error-free claim is made.

The repository's moving `main` branch is not itself the final release identity. Once the remaining human gate is complete, release eligibility is bound to the exact commit and file hashes emitted by `scripts/build_lang_wb_final_release_snapshot.py`; later learner-facing changes require fresh applicable evidence rather than inheriting the earlier release state automatically.
