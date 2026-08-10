# Arabic Learning Protocol — MSA to C2

This file is mandatory reading for agents working on the Arabic track.

## Goal
Build the user from their current Arabic foundation to functional CEFR C2 mastery, with Modern Standard Arabic (MSA) as the core. The system is audio-first, but not audio-only.

## Active-track commands
When Arabic is active:
- `complete` = mark the current lesson complete, process its learning content, generate/deepen cards, store sources, and advance to the next item.
- `finished` = same as `complete`.
- `what's next` = read repo state and return the exact next lesson.
Never infer completion from chat memory when repo state is available.

## Media-source priority
The user prefers YouTube or other directly consumable public media rather than provider lesson pages.

When resolving the next lesson, use this order:
1. verified YouTube video from a high-quality educator/institution;
2. free public podcast/audio/video lesson;
3. university/open educational resource with audio;
4. provider lesson page only as a transcript/reference or when no suitable public-media equivalent exists.

Do not sacrifice curriculum coverage merely to use YouTube. If a replacement video covers only part of a planned lesson, preserve the uncovered concept and schedule another public source later. Record the resolved media in `playlists/audio/arabic/msa-to-c2/resolved_media.json`.

Prefer audio-capable videos. Search across multiple teachers/sources rather than keeping the track tied to one provider. This also supports spaced reinforcement through different voices and explanations.

## Variants
Keep these distinct:
1. MSA — primary backbone for formal speech, media, reading, writing, cross-region communication.
2. Conversational dialect — add as a parallel branch after a stable A2/B1 MSA base. Do not silently substitute dialect content for MSA.
3. Quranic/Classical Arabic — light exposure may begin early because it supports the user's interests, but systematic grammar/lexicon becomes a parallel branch from A2/B1 onward.

Every lesson/card/source must record variety: `msa`, `classical`, `quranic`, or a named dialect.

## Audio-first standard
Target roughly 70–85% of consumption time as audio-capable material.
Each media item records `visual_dependency`: none/helpful/periodic/high.
For an audio lesson:
1. first pass — listen without transcript;
2. second pass — listen and shadow/repeat;
3. third pass only if needed — inspect Arabic transcript and grammar;
4. final pass — listen again without English.

At B1+, authentic listening must grow steadily. At C1/C2, learner-targeted English explanations become supplemental rather than the core.

## CEFR advancement
Do not equate playlist completion with CEFR mastery. A level is passed only when the learner can demonstrate reception, production, interaction, and mediation consistent with CEFR descriptors.

### A1
Understand and use highly frequent expressions, identify basic personal information, produce short rehearsed exchanges.

### A2
Handle routine exchanges, describe immediate environment and past/routine events in simple connected language.

### B1
Understand main points of clear standard Arabic, narrate experiences, explain simple reasons, follow ordinary news/topics with support.

### B2
Follow extended standard discourse, interact with reasonable fluency, discuss abstract topics, produce clear detailed explanations.

### C1
Understand demanding extended discourse and implicit meaning, use Arabic flexibly for academic/professional/social purposes, produce well-structured extended speech and writing.

### C2
Understand virtually all forms of speech/text with minimal strain, including specialized and implicit content; synthesize and reformulate sources; express subtle distinctions spontaneously, precisely, and appropriately across registers.

## Completion processing
For every completed lesson:
1. Verify the exact media actually completed.
2. Extract main ideas.
3. Search existing Arabic cards for semantic overlap.
4. Add only high-utility new vocabulary, grammar, phrase, pronunciation, or listening distinctions.
5. Deepen existing cards when the concept already exists.
6. Store source ID(s).
7. Update playlist/progress item to completed.
8. Resolve the next lesson to a verified YouTube/public-media URL using the media-source priority above.
9. Preserve any curriculum concepts not covered by the replacement media.
10. Update `playlists/audio/arabic/msa-to-c2/resolved_media.json`.
11. Update `progress/tracks/arabic-msa-to-c2.json`.
12. Update `progress/current.json`.
13. Update `NEXT.md`.
14. Keep paused MATS progress untouched.

## Arabic flashcards
Use `docs/ARABIC_FLASHCARD_STANDARD.md`. Do not dump every lesson word into cards. Prefer high-frequency, generative language.

## Roadmap
Canonical long-range path:
`playlists/audio/arabic/msa-to-c2/roadmap.json`

Current stage playlist:
`playlists/audio/arabic/msa-to-c2/a1-foundations/playlist.json`
