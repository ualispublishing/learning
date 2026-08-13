# Arabic-First Reading + Flashcard Verification Pipeline

Arabic is the active language. French and Urdu are paused for new curriculum expansion until the Arabic workflow is calibrated and the Arabic flashcard re-audit reaches a stable educator-review state.

## Two linked tracks

### Track A — graded reading

Build and approve Arabic passages level by level from A1 upward. The validated flashcard corpus is the frequency backbone, but vocabulary is selected according to actual learner difficulty, communicative usefulness, morphology, concreteness/abstractness, register, and passage context.

Frequency rank is **not** treated as a CEFR level by itself.

Working eligibility guidance, subject to individual-word review:

- **A1:** overwhelmingly high-frequency concrete/function vocabulary; very small verified support layer; transparent morphology and syntax.
- **A2:** broader everyday vocabulary, routine actions, time/location, common descriptions, more inflection and basic derivation.
- **B1:** wider top-frequency corpus, common abstract meanings, narrative/expository vocabulary, productive word families and collocations.
- **B2:** the full verified top-3000 backbone may be drawn on when context supports it; abstract, academic/news and polysemous senses require explicit verification.
- **C1:** the full verified backbone plus independently verified beyond-base vocabulary, idiomatic/collocational precision, register and stylistic distinctions.
- **C2:** not constrained by the flashcard corpus; use it as known/review material while independently verifying advanced lexical, idiomatic, rhetorical and stylistic content.

These are curriculum heuristics, not claims that rank N equals CEFR level X.

### Track B — flashcard re-audit

The reader is a second verification surface for the Arabic flashcards.

A card used in a passage is checked for:

1. exact Arabic surface form;
2. intended contemporary MSA sense;
3. English learner gloss;
4. grammatical category / part of speech;
5. homograph and vocalization handling;
6. register and dialect risk;
7. morphology/root relationship where relevant;
8. whether multiple senses are bundled in a learner-confusing way;
9. whether the example passage actually instantiates the stated sense;
10. whether a concise educator-facing explanation would remain accurate.

A card does not become `reader_verified` until those checks pass.

## Audit order

To maximize safety and usefulness, re-audit Arabic in concentric blocks:

1. all cards currently used as A1 targets/review/support;
2. ranks 1-100, because errors there propagate most widely;
3. ranks 101-500;
4. ranks 501-1000;
5. continuation ranks 1001-2000;
6. continuation ranks 2001-3000;
7. any beyond-base word introduced by B2-C2 reading.

Confirmed defects are corrected immediately with rank/front regression guards; uncertain cases remain in an explicit review queue rather than being guessed.

## Educator-readiness terminology

Until this second pass is complete:

- the Arabic CSVs are **working learner datasets with strong prior audit evidence**;
- they are **not to be described as fully educator-ready reference datasets**;
- individual cards may be marked `reader_verified` / `educator_reviewed` as evidence accumulates;
- final educator-readiness requires both whole-deck structural/source checks and the new semantic/grammar audit.

## Passage-question policy

All Arabic passages use the 10-question standard in `reading/planning/TEN_QUESTION_STANDARD.md`.

Questions are deliberately used to surface deck defects. A vocabulary or grammar question that reveals a misleading card causes the card to enter the audit queue before the passage can be approved.
