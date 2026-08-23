# Language Workbooks v1.0

This directory contains the current generated workbook artifacts for Arabic, French, and Urdu: one complete master PDF, 13 split PDFs, a 1,000-entry vocabulary companion CSV, and a 1,000-sentence attributed companion CSV for each language.

> **Release status: EDITORIALLY BLOCKED.** These files are retained as audit/build artifacts and must not currently be represented as linguistically certified, error-free, or learner/publication ready.

Vocabulary comes from the repository's audited top-1,000 learner decks. Sentence pairs were selected from the ManyThings bilingual exports of Tatoeba and retain sentence-level attribution under CC BY 2.0 France.

A complete first-pass linguistic/editorial screen of all 1,000 Urdu sentence rows found substantive grammar, spelling, idiomaticity, register, and bilingual semantic-equivalence defects that were not caught by the original automated structural QA. The detailed Urdu findings are under `audit/language-workbooks/v1.0/`, and the source-locked repair layer is under `curation/language-workbooks/v1.0/`.

Arabic and French sentence banks were produced through the same selection architecture and are therefore not considered linguistically certified until they receive equivalent sentence-level screening.

For regeneration work, use `scripts/build_language_workbooks_curated_v1.py`. The curated wrapper intentionally blocks Urdu regeneration while its curation layer remains incomplete and verifies the exact audited source ZIP hash before any rank-based correction can be applied.

The release continues to favor natural, idiomatic learner language over artificial uniqueness. Genuine homographs may be retained when meaning and grammatical role genuinely differ. Transliteration is omitted from sentence drills rather than introducing inconsistent ad-hoc romanization.

Independent native/editorial review remains required before any absolute correctness claim.
