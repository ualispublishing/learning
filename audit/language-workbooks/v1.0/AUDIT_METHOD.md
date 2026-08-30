# Row-level language workbook audit method

This file describes the source-locked **editorial QA** method used during corpus repair and production-candidate preparation. It is supporting evidence, not the final independent human certification schema.

For each learner-facing row, review target text and English meaning together. Flag only evidence-backed issues.

## Arabic
Check MSA grammaticality, morphology, agreement, word choice, punctuation/script hygiene, translation fidelity, register, and whether the sentence is pedagogically appropriate for the assigned progression band.

## French
Check accents/orthography, agreement, conjugation, contractions/articles, syntax, idiomaticity, translation fidelity, register, and progression level.

## Urdu
Check standard Urdu orthography, agreement, case/postpositions, verb morphology, gender/number, idiomaticity, register, translation fidelity, and progression level. Avoid Roman-script learner-facing leakage.

## Editorial adjudication taxonomy

The production-candidate editorial process used:

- `PASS`: no known issue after the editorial review pass;
- `REPAIR`: a specific defect is identifiable and a correction is justified;
- `HOLD`: meaning or naturalness is uncertain enough that it should not be accepted without further adjudication.

A structural or corpus-quality PASS does not override a `REPAIR` or `HOLD` decision.

## Final independent reviewer taxonomy

The current native/near-native review workflow is separate and uses `PASS`, `FAIL`, and `HOLD` in the generated reviewer ledgers and immutable sign-off records. A final human `PASS` cannot be inferred from an earlier editorial `PASS`.

See [`REVIEWER_ONBOARDING.md`](REVIEWER_ONBOARDING.md), [`FINAL_NATIVE_REVIEW_PACKET.md`](FINAL_NATIVE_REVIEW_PACKET.md), and [`LINGUISTIC_GATE.md`](LINGUISTIC_GATE.md) for the final human gate.
