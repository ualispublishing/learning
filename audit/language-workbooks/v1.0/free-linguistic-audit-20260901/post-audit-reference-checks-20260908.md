# LANG-WB post-audit reference checks — 2026-09-08

This note records follow-up machine/reference checks against a small subset of rows left `UNRESOLVED` by the preserved 2026-09-01 machine audit.

## Boundary

- Candidate bound by the original audit: `aa9b5d465839edb2ce520133a01d78ed40634c96`
- This is reviewer-aid evidence only.
- This is **not** native-speaker certification and does not satisfy or weaken the independent full-content human review gate.
- The original `strongest_flags_compact.csv` is intentionally left unchanged as a historical record of the original machine adjudication.
- No learner-facing workbook row was changed by these checks.

## Confirmed valid lexical senses

### French vocabulary rank 91 — `temps`

Candidate gloss: `tense; weather; time (in general)`

Follow-up result: **CONFIRMED_VALID_LEXICAL_SENSE**.

Evidence: the Académie française entry for `temps` explicitly covers time generally, grammatical tense, and atmospheric/weather use.

- https://www.dictionnaire-academie.fr/article/A9T0658

### French vocabulary rank 631 — `est`

Candidate gloss: `is (form of être); east; eastern`

Follow-up result: **CONFIRMED_VALID_LEXICAL_SENSE**.

Evidence: the Académie française gives `est` as the third-person singular present form of `être` (`il, elle est`) and separately defines the noun `est` as the east cardinal direction.

- https://www.dictionnaire-academie.fr/article/A9E2986
- https://www.dictionnaire-academie.fr/article/A9E2694

### French vocabulary rank 835 — `parfaire`

Candidate gloss: `to finish, to complete; to make a supplementary payment`

Follow-up result: **CONFIRMED_VALID_LEXICAL_SENSE**.

Evidence: the Académie française defines `parfaire` as bringing something to completion and records the financial sense `parfaire un paiement` as completing what has already been paid to reach the amount due (marked vieill./older usage).

- https://www.dictionnaire-academie.fr/article/A9P0635

## Result

Three additional strongest-flag rows are strongly supported as valid lexical entries. They should be deprioritized for defect hunting while remaining visible to the eventual full-content human reviewer. No production content change is warranted from this batch.
