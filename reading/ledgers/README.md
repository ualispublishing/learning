# Reading Exposure Ledgers

This directory will track **curriculum exposure and retrieval history**, not dictionary validity and not assumed learner mastery.

## Core rule

An item being present in `arabic_top1000.csv`, `arabic_top3000.csv`, `french_top1000.csv`, `french_top3000.csv`, `urdu_top1000.csv`, `urdu_top3000.csv`, or `arabic_phrase_bank.csv` means the item is **available for controlled curriculum use**.

It does **not** mean:

- the learner has seen it in the reading curriculum;
- the learner knows it;
- it should count as a known token for passage-coverage calculations;
- its frequency rank is its CEFR level.

## Planned files

- `arabic_lexical_exposure.jsonl`
- `french_lexical_exposure.jsonl`
- `urdu_lexical_exposure.jsonl`

Every lexical/phrase target should have one canonical exposure record.

## Initial record state

Before the item is introduced in an approved passage:

- `curriculum_state`: `not_scheduled`
- `assumed_known`: `false`
- `introduction_passage_id`: `null`
- `successful_meaningful_contacts`: `0`
- `contact_history`: `[]`
- `next_due_stage`: `R0`

## After introduction

The ledger records passage/task contacts, including:

- running-text contextual encounter;
- vocabulary-in-context inference;
- cloze transfer;
- contrast/discrimination;
- paraphrase;
- summary/production;
- later contextual encounter.

Important targets normally progress through R0, R1, R2, R3, R4, and R5 according to `docs/READING_PASSAGE_STANDARD.md`.

## Known-token coverage

Passage coverage must use a curriculum-aware definition of `known` rather than automatically treating the entire 3,000-item inventory as mastered.

The exact mastery/coverage promotion rule will be calibrated with the first passage units and, later, reader telemetry. Until that rule is validated, records should remain conservative.

## Advanced vocabulary

C1/C2 vocabulary beyond the validated 3,000-item base must be added to a derived reading lexicon with verified sense/register/provenance before it gets an exposure-ledger record and becomes a deliberate passage target.
