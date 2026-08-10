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

## Media-source policy
Use public/open, directly consumable learning media and rotate sources so the learner hears different speakers and explanations.

Preferred order:
1. verified YouTube video from a high-quality educator/institution;
2. free public video/audio from an educational institution;
3. university/open educational resource with audio;
4. graded authentic MSA media, podcasts, interviews, or documentaries appropriate to the learner's level;
5. interactive reading/writing material when it serves a skill that audio cannot replace.

### Temporarily excluded source family
Do **not** use ArabicPod101 or any ArabicPod101-branded website, YouTube channel, video, audio, transcript, lesson, playlist, or derived source ID anywhere in the active Arabic curriculum, source registry, progress state, review queue, or flashcard citations. This exclusion remains in force until the user explicitly asks to restore that source family.

The first two completed lessons are preserved as concept milestones rather than as provider-specific completions. Public/open sources now validate and reinforce those concepts.

Do not sacrifice curriculum coverage merely to change sources. If one source covers only part of a planned concept cluster, retain the uncovered concept and schedule another public/open source later.

## Variants
Keep these distinct:
1. MSA — primary backbone for formal speech, media, reading, writing, cross-region communication.
2. Conversational dialect — add as a parallel branch after a stable A2/B1 MSA base. Do not silently substitute dialect content for MSA.
3. Quranic/Classical Arabic — light exposure may begin early because it supports the user's interests, but systematic grammar/lexicon becomes a parallel branch from A2/B1 onward.

Every lesson/card/source must record variety: `msa`, `classical`, `quranic`, or a named dialect.

## Audio-first standard
Target roughly 70–85% of consumption time as audio-capable material.
Each media item records `visual_dependency`: none/helpful/periodic/high.
For an audio/video lesson:
1. first pass — listen without transcript/subtitles when feasible;
2. retrieve what was understood;
3. second pass — shadow/repeat;
4. inspect Arabic transcript/visuals only if needed;
5. final pass — listen again without English support.

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
6. Store public/open source ID(s).
7. Update playlist/progress item to completed.
8. Update spaced-reinforcement exposure counts and due reviews.
9. Resolve the next lesson to a verified public/open source using the media-source policy above.
10. Preserve planned concepts not covered by the selected media.
11. Update `playlists/audio/arabic/msa-to-c2/resolved_media.json`.
12. Update `progress/tracks/arabic-msa-to-c2.json`.
13. Update `progress/current.json`.
14. Update `progress/review_queue.json` and `NEXT.md`.
15. Keep paused MATS progress untouched.

## Arabic flashcards
Use `docs/ARABIC_FLASHCARD_STANDARD.md`. Do not dump every lesson word into cards. Prefer high-frequency, generative language. Arabic review-card fronts remain Arabic-script-only; all translations, definitions, examples, metadata, and eight layers belong on the back.

## Roadmap
Canonical long-range path:
`playlists/audio/arabic/msa-to-c2/roadmap.json`

Current stage playlist:
`playlists/audio/arabic/msa-to-c2/a1-foundations/playlist.json`
