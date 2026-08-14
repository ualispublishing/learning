# Arabic-First Reading + Flashcard Verification Pipeline

Arabic is the active language. French and Urdu remain paused for new curriculum expansion until the Arabic A1 calibration workflow is canonically closed and the complete 18-passage A1 cross-language calibration is ready to proceed.

## Current Arabic evidence state

The Arabic vocabulary re-audit is complete for the validated learner backbone:

- ranks 1–100: educator-cleared;
- ranks 101–500: educator-cleared under the stricter second-pass standard;
- ranks 501–1000: `EDUCATOR_CLEARED_SOURCE_TIGHT`, full-block manual review complete, zero unresolved ranks;
- ranks 1001–3000: `EDUCATOR_CLEARED_MODERN_SENSE`, zero block/review rows and live attestation PASS;
- Arabic phrase bank: 665/665 semantic/example-fidelity rows cleared, with zero unresolved rows after manual adjudication of heuristic false positives.

Canonical evidence includes:

- `audit/arabic_top100_educator_review.json`
- `audit/arabic_101_500_educator_review.json`
- `audit/arabic_501_1000_educator_review.json`
- `audit/arabic_top3000_v2_promotion_gate_summary.json`
- `audit/arabic_phrase_bank_audit_summary.json`
- `audit/live_csv_attestation.json`

The ranked 1–3000 backbone is therefore frozen for ordinary curriculum use unless a reader passage exposes a genuinely new, independently confirmed defect. Do not restart obsolete heuristic review queues merely because older audit artifacts contain historical flags.

## Two linked tracks

### Track A — graded reading

Build and approve Arabic passages level by level from A1 upward. The educator-cleared flashcard corpus is the frequency backbone, but vocabulary is selected according to actual learner difficulty, communicative usefulness, morphology, concreteness/abstractness, register, and passage context.

Frequency rank is **not** treated as a CEFR level by itself.

Working eligibility guidance, subject to individual-word review:

- **A1:** overwhelmingly high-frequency concrete/function vocabulary; very small verified support layer; transparent morphology and syntax.
- **A2:** broader everyday vocabulary, routine actions, time/location, common descriptions, more inflection and basic derivation.
- **B1:** wider top-frequency corpus, common abstract meanings, narrative/expository vocabulary, productive word families and collocations.
- **B2:** the full verified top-3000 backbone may be drawn on when context supports it; abstract, academic/news and polysemous senses still require passage-specific sense verification.
- **C1:** the full verified backbone plus independently verified beyond-base vocabulary, idiomatic/collocational precision, register and stylistic distinctions.
- **C2:** not constrained by the flashcard corpus; use it as known/review material while independently verifying advanced lexical, idiomatic, rhetorical and stylistic content.

These are curriculum heuristics, not claims that rank N equals CEFR level X.

### Track B — reader-driven regression checking

The reader remains a second verification surface for the Arabic flashcards even though the base audit is complete.

A card deliberately used in a passage is checked in context for:

1. exact Arabic surface form;
2. intended contemporary MSA sense;
3. English learner gloss;
4. grammatical category / part of speech;
5. homograph and vocalization handling;
6. register and dialect risk;
7. morphology/root relationship where relevant;
8. whether multiple senses are bundled in a learner-confusing way;
9. whether the example passage actually instantiates the stated sense;
10. whether a concise educator-facing explanation remains accurate.

These checks are regression protection and passage-sense validation; they do **not** reopen the whole cleared rank block unless new evidence warrants it.

## Audit order going forward

For new Arabic reading work:

1. verify every deliberate passage target/support item in its exact reader-used sense;
2. reuse the educator-cleared ranks 1–3000 without repeating completed whole-block audits;
3. treat phrase-bank chunks as separate multiword curriculum targets with their own exposure history;
4. independently verify any beyond-3000 item before learner use;
5. for B2–C2, add register/polysemy/collocation review where the passage demands finer sense distinctions;
6. if a passage uncovers a genuine defect in a cleared card, repair that card with rank/front regression guards and record the exception explicitly.

## Educator-readiness terminology

For Arabic as of 2026-08-13:

- the validated ranked vocabulary backbone, ranks 1–3000, is educator-cleared under the recorded source-aware second-pass evidence;
- the 665-row Arabic phrase bank is educator semantically cleared;
- this clearance does **not** imply that a learner has mastered any item;
- frequency rank does **not** imply CEFR level;
- reader passage approval remains separate and still requires linguistic, pedagogical, semantic-target, supported-coverage, schema, exposure-spacing, and fluency checks;
- beyond-base vocabulary remains unapproved until independently verified.

## Passage-question policy

All Arabic passages use the 10-question standard in `reading/planning/TEN_QUESTION_STANDARD.md`.

Questions are deliberately used to surface regressions. A vocabulary or grammar question that reveals a newly confirmed misleading card blocks the passage and opens a targeted repair; it does not by itself invalidate the already-cleared surrounding rank block.

## Current A1 Unit-01 gate

For `ar-a1-u01-p01` through `p06`:

- 6/6 records validate against the canonical JSON Schema;
- 60/60 questions and 60/60 linked answers pass the structural gate;
- canonical passage records currently record linguistic, pedagogical, and answer-key checks as PASS;
- `reading/audit/arabic_a1_supported_coverage.json` records the supported-control gate as PASS with zero uncontrolled tokens under the documented curriculum-control definition;
- `reading/ledgers/arabic_unit01_exposure_summary.json` records all ten deliberate Unit-01 lexical targets without assuming learner success/mastery;
- canonical passage `coverage_check` / final approval status persistence remains the last Arabic Unit-01 bookkeeping gate.

Do not generate Arabic Unit 02 until the canonical Unit-01 approval state is closed and the broader A1 calibration policy permits scaling.
