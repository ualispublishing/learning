# Language workbooks v1.1 pronunciation audit

Status: **NOT RELEASED**

This directory is an audit workspace for a pronunciation-enhanced companion release. It is deliberately separate from `completed/languages/workbooks/v1.0` so the validated original workbook release is not overwritten.

## Source binding

Pronunciation candidates must be generated only after:

```bash
python scripts/apply_language_workbook_linguistic_repairs.py --write
```

passes all original 6,000 row-level linguistic gates in an isolated runner. The pronunciation generator then records SHA-256 hashes of the repaired Arabic, French, and Urdu vocabulary and sentence sources in `candidate_manifest.json`.

The runner restores the checked-in v1.0 inputs before committing anything. Only this v1.1 pronunciation audit directory is committed by the candidate workflow.

## Candidate generation

`python scripts/generate_language_workbook_pronunciation_candidates.py`

creates six candidate files:

- Arabic vocabulary — 1,000 rows
- Arabic sentences — 1,000 rows
- French vocabulary — 1,000 rows
- French sentences — 1,000 rows
- Urdu vocabulary — 1,000 rows
- Urdu sentences — 1,000 rows

Each row receives:

- a machine IPA candidate from eSpeak NG through `phonemizer`;
- a learner-oriented Latin hint candidate derived from that IPA;
- the exact source hash used for generation.

These are **candidates, not certified pronunciations**.

## Mandatory row-by-row pronunciation audit

The generator initializes permanent 50-row ledgers under `row_by_row/`. Every one of the 6,000 rows begins as `PENDING` and must be adjudicated individually.

Allowed final statuses:

- `PASS` — IPA and learner hint are both acceptable for the intended standard/register.
- `REPAIR` — at least one pronunciation field needs an exact correction; record the issue and proposed replacement.
- `HOLD` — pronunciation or register remains genuinely ambiguous and requires later adjudication.

`PENDING` and `HOLD` block finalization.

Review must consider, as applicable:

- phoneme identity and vowel quality;
- stress and syllable structure;
- Arabic MSA short-vowel inference and hamza/ʿayn/pharyngeal distinctions;
- French liaison, schwa, nasal vowels, mute letters, and register-appropriate realization;
- Urdu short vowels, aspiration, retroflexion, vowel length, nasalization, and standard pronunciation;
- whether the learner hint is actually readable and does not teach a misleading English approximation;
- target-word/sentence sense and grammatical context when pronunciation is ambiguous without it.

## Fail-closed finalization

After all 6,000 pronunciation rows are adjudicated:

```bash
python scripts/finalize_language_workbook_pronunciation.py
```

will refuse to produce final sidecars if:

- any rank is missing or duplicated;
- any row remains `PENDING` or `HOLD`;
- a ledger has drifted from its original pronunciation candidate;
- a `REPAIR` has no issue note or no proposed correction;
- a `PASS` contains an unexplained proposed change;
- any final pronunciation field is blank.

Only after that gate passes should the pronunciation-enhanced PDFs be built and placed beside, never over, the original v1.0 release.
