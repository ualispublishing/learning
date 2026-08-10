# Active Flashcard Review Scope

The external periodic-review app consumes flashcards from the repository's `subjects/` tree.

## Rule
- `subjects/**/knowledge.json` and `subjects/**/practice.json` = active review material.
- `archive/flashcards/**` = preserved but excluded from active periodic review.

When the user pivots subjects, do not delete old cards. Move paused decks from `subjects/` to `archive/flashcards/<subject>/...` while preserving the original hierarchy and JSON unchanged.

When a paused subject is resumed, move the desired canonical decks back into `subjects/<subject>/...` and archive any subject that should no longer appear in the external review app.

Only put cards into the active `subjects/` tree when the learner has reached, is currently learning, or should now be reviewing that material. Avoid preloading large future decks because it weakens spaced repetition and causes out-of-sequence reviews.

For Arabic, newly completed lessons should add/deepen cards under `subjects/arabic/` using `docs/ARABIC_FLASHCARD_STANDARD.md` and the canonical layered schema. Review variants should reference canonical card IDs rather than duplicate the knowledge record.
