# LANG-WB free linguistic audit — 2026-09-01

This directory preserves the machine-only linguistic audit performed against the exact v1.0 workbook candidate.

## Scope

- Candidate commit: `aa9b5d465839edb2ce520133a01d78ed40634c96`
- Structured rows checked: **6000 / 6000**
- Languages: Arabic, French, Urdu
- Rows per language: 1,000 vocabulary + 1,000 sentence rows
- First-pass workflow run: `33527565755`
- Third-adjudication workflow run: `33528985822`

The audit is evidence/triage only. It does **not** constitute native-speaker certification and does not promote the release beyond `production_candidate`.

## First pass

Independent translation families:
- language-specific Marian / OPUS MT
- `facebook/m2m100_418M`

Semantic adjudicator:
- `cross-encoder/nli-MiniLM2-L6-H768`

Aggregate result:
- `CONFIRMED_EQUIVALENT`: 3777
- `MINOR_OR_MODEL_VARIANCE`: 203
- `MEANINGFUL_DIFFERENCE_LIKELY`: 180
- `MODEL_DISAGREEMENT`: 1480
- `NEEDS_ADJUDICATION`: 360

The 180 strongest first-pass flags were sent to a separate third model rather than being auto-corrected.

## Third-model adjudication

Model:
- `Qwen/Qwen2.5-1.5B-Instruct`

Input:
- 180 strongest first-pass flags
- Arabic: 37
- French: 51
- Urdu: 92

Result:
- `CLEARED_VALID_VARIANT`: 18
- `UNRESOLVED`: 162
- machine-safe confirmed content issues: **0**

The third model produced several malformed or linguistically weak rationales, so unresolved rows remain review candidates rather than defects. No workbook row was changed solely because a model disagreed.

Representative false-positive patterns include:
- grammatical annotations such as Arabic/French gender and Urdu oblique forms;
- idiomatic translations;
- words with multiple legitimate senses;
- Urdu homographs such as `کافی` (“coffee” / “enough”);
- French generic `on` and pronoun ambiguity.

## Artifacts

First-pass run artifacts:
- Arabic artifact `9808667265`, digest `sha256:bcecdc3702fb9fabc8f4554a2538db07073ea79cd59fce520d20e41fed79e36e`
- French artifact `9808651726`, digest `sha256:e3cfe4a3e33f68d536f42eafcf2eed450d369701418fe120567ea76d59de2e3c`
- Urdu artifact `9808584400`, digest `sha256:f767885198e15e1ea6b3faa0dbf49224dce635179be09b693d5cfc5738513779`
- aggregate artifact `9808697478`, digest `sha256:e606a4c04cc43a3e7e226ed0f304396078cdb5b687a409b0809d0daca51b8057`

Third-adjudication artifact:
- artifact `9809164732`
- digest `sha256:f4ef001de010c20b7690d1f823bb987cf3b56add6e56bb62ab8c302d935ee71d`

The Actions artifacts expire after 30 days; the durable summary and strongest-flag CSV are stored here.

## Release boundary

This audit materially increases automated confidence but intentionally does **not** create or imply a human/native-speaker PASS. The independent full-content Arabic, French, and Urdu review gates remain the final linguistic release blocker.
