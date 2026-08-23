# Language Workbooks v1.0 - automated QA

Automated release gates passed for the generated production candidate. Natural language quality takes priority over artificial surface-form uniqueness. Independent native-speaker editorial certification remains the final step before an absolute commercial correctness claim.

> **Editorial blocker (2026-08-23):** a complete first-pass linguistic/editorial screening of all 1,000 Urdu sentence-bank rows found learner-facing grammar, spelling, idiomaticity, and translation-equivalence defects despite the automated PASS. The Urdu sentence bank is therefore blocked for learner/publication release until the curated repair layer is applied, all Urdu artifacts are regenerated together, regression QA passes, and independent native/editorial review is completed. Detailed findings are recorded across `urdu_sentence_editorial_audit.json`, `urdu_sentence_editorial_audit_251_500.json`, `urdu_sentence_editorial_audit_501_750.json`, and `urdu_sentence_editorial_audit_751_1000.json`. The same target-language validation gap exists in the sentence-selection method used for Arabic and French, so their sentence banks also require linguistic/editorial screening before an absolute correctness claim.

## Arabic
- Vocabulary: 1000 audited entries; 999 normalized surface forms.
- Sentences: 1000 rows; 1000 unique target strings; 838 unique English strings.
- Licensed attribution retained: 1000/1000 rows.
- Sentence candidates after hard filters: 12067.
- PDFs: 14 (1 master + 13 tablet segments).
- Automated structural status: PASS.
- Linguistic/editorial release status: NOT YET CERTIFIED.

## French
- Vocabulary: 1000 audited entries; 1000 normalized surface forms.
- Sentences: 1000 rows; 1000 unique target strings; 561 unique English strings.
- Licensed attribution retained: 1000/1000 rows.
- Sentence candidates after hard filters: 212238.
- PDFs: 14 (1 master + 13 tablet segments).
- Automated structural status: PASS.
- Linguistic/editorial release status: NOT YET CERTIFIED.

## Urdu
- Vocabulary: 1000 audited entries; 1000 normalized surface forms.
- Sentences: 1000 rows; 1000 unique target strings; 794 unique English strings.
- Licensed attribution retained: 1000/1000 rows.
- Sentence candidates after hard filters: 1137.
- PDFs: 14 (1 master + 13 tablet segments).
- Automated structural status: PASS.
- Manual sentence first-pass audit coverage: 1000/1000 (100%).
- Linguistic/editorial release status: BLOCKED pending correction, regeneration, regression verification, and independent review.

