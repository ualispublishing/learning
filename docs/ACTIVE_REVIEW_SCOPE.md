# Active Flashcard Review Scope

The external periodic-review app currently depends on a legacy MATS deck location. Until the user updates that app, the repository must preserve a compatibility mirror at the exact legacy path.

## Current compatibility contract

Canonical Arabic deck:
`subjects/arabic/a1-foundations/greetings/knowledge.json`

Temporary app-facing compatibility path:
`subjects/mats/mechanics-of-materials/stress-and-strain/knowledge.json`

The compatibility file must mirror the currently active Arabic review deck byte-for-byte whenever the Arabic deck changes. The path remains named `mats/...` only because the external app has not yet been updated. Do not interpret the path as the deck's semantic subject; the JSON metadata remains Arabic.

When the user says `complete` or `finished`, after adding/deepening Arabic cards, update both the canonical Arabic deck and this compatibility path in the same workflow.

## Archived material

Paused MATS cards are preserved under `archive/flashcards/mats/...`, but their files use the `.archive` extension rather than `.json` so a naive flashcard importer does not discover them as active decks.

Current archived files:
- `archive/flashcards/mats/mechanics-of-materials/stress-and-strain/knowledge.archive`
- `archive/flashcards/mats/mechanics-of-materials/youngs-modulus/knowledge.archive`

Do not delete these cards. They remain available for restoring the MATS track later.

## Canonical organization

- `subjects/arabic/**/knowledge.json` and `practice.json` = canonical Arabic knowledge/practice data.
- `archive/flashcards/**` = preserved inactive subject material.
- The legacy MATS-path mirror is temporary compatibility infrastructure only.

Only activate cards the learner has reached or that are pedagogically due. Avoid preloading future vocabulary merely to increase deck size.

For Arabic, use `docs/ARABIC_FLASHCARD_STANDARD.md`, Arabic-script-only fronts, and the canonical eight-layer back. Review variants should reference canonical card IDs rather than duplicate the knowledge record.

## Removal condition

Do not remove the legacy MATS-path mirror until the user explicitly says their flashcard app has been updated to read the canonical Arabic location. At that point, remove the compatibility copy and leave only the correctly categorized Arabic deck.
