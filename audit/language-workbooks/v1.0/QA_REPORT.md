# Language Workbooks v1.0 - automated QA

Automated release gates passed for the generated production candidate. Natural language quality takes priority over artificial surface-form uniqueness. Independent native-speaker editorial certification remains the final step before an absolute commercial correctness claim.

> **Editorial blocker (2026-08-23):** manual linguistic screening of the Urdu sentence bank found learner-facing grammar, spelling, idiomaticity, and translation-equivalence defects despite the automated PASS. Urdu sentence rows 1-500 have now been screened (50%); the release must not be described as linguistically certified or error-free. Detailed findings are recorded in `urdu_sentence_editorial_audit.json` and `urdu_sentence_editorial_audit_251_500.json`. The same target-language validation gap exists in the sentence-selection method used for Arabic and French, so their sentence banks also require linguistic/editorial screening before an absolute correctness claim.

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
- Manual sentence audit coverage: 500/1000 (50%).
- Linguistic/editorial release status: BLOCKED pending correction, full-bank screening, regeneration, and independent review.

