# Arabic

Primary goal: Modern Standard Arabic (MSA) to CEFR C2 with strong listening, speaking, reading, writing, interaction, and mediation.

## Active review scope

The external periodic-review app reads the repository's `subjects/` tree. Arabic is the current active review subject. Paused subject decks are preserved under `archive/flashcards/` instead of remaining here.

See `docs/ACTIVE_REVIEW_SCOPE.md`.

## Arabic card display contract

For every active Arabic knowledge card:

- `front` MUST be Arabic script only. Do not put an English question, translation, transliteration, hint, or definition on the front.
- Use vocalized Arabic at A1/A2 when it materially helps pronunciation; progressively reduce nonessential tashkeel later.
- The reverse side contains the complete learning payload: English/Urdu/French translations when applicable, Arabic and English definitions, root/pattern when useful, synonyms, Arabic/English examples, grammatical/register notes, prerequisites, tags, source IDs, and all eight layered fields.
- The eight required layers remain: `direct_answer`, `concept_expansion`, `worked_or_physical_example`, `boundaries_and_misconceptions`, `connections_and_memory`, `transfer_prompt`, `mastery_evidence`, and `sources`.
- Multiple retrieval representations (audio recognition, cloze, production, discrimination) should reference the same canonical card rather than weakening the Arabic-only knowledge-card front.

This contract applies automatically to cards generated when the user says `complete` or `finished`.

## Canonical subject structure

Arabic knowledge should grow under the smallest meaningful hierarchy, including:
- `a1-foundations/` while the beginner sequence is active;
- `phonology-pronunciation/`;
- `core-grammar/`;
- `morphology/`;
- `vocabulary/`;
- `listening/`;
- `speaking/`;
- `reading/`;
- `writing/`;
- `discourse-register/`;
- `quranic-classical/`;
- `dialects/<dialect>/`.

Do not organize Arabic knowledge by YouTube channel/provider. Providers belong in `sources/` and `playlists/`.

Only activate cards that have been reached or are pedagogically due. Do not preload large future vocabulary lists into the app-facing review scope.

See root `ARABIC.md`, `docs/ARABIC_FLASHCARD_STANDARD.md`, and `docs/SPACED_REINFORCEMENT_STANDARD.md`.
