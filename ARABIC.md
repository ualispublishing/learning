# Arabic Learning Protocol — MSA to C2

This file is mandatory reading for agents working on the Arabic track.

## Goal
Build the user from their current Arabic foundation to functional CEFR C2 mastery, with Modern Standard Arabic (MSA) as the core. The system is audio-first, but not audio-only.

## Active-track commands
When Arabic is active:
- `complete` = mark the current lesson complete, process its learning content, generate/deepen cards, update spaced reinforcement, and advance to the next item.
- `finished` = same as `complete`.
- `what's next` = read repo state and return the exact next lesson.
Never infer completion from chat memory when repo state is available.

## Course staging
Do not treat all Arabic sources as one flat playlist.

### Course 1 — active beginner foundation
`playlists/audio/arabic/courses/gateway-to-arabic-book-2/playlist.json`

Use **Gateway to Arabic Book 2** as the coherent English-supported MSA foundation. It is designed for learners in a non-Arabic-speaking environment and introduces vocabulary/grammar with short, simple explanations before immersion.

The user already has basic script familiarity, so begin at Book 2 rather than automatically restarting the alphabet. Insert targeted reading/pronunciation repair only when evidence shows it is needed.

### Course 2 — deferred immersion
`playlists/audio/arabic/courses/al-jazeera-immersion/playlist.json`

Al Jazeera Learning Arabic is **not** an introductory source. Treat it as a separate Arabic-first immersion course after Course 1.

Do not surface Al Jazeera as `next`, do not use it for required beginner reinforcement, and do not rely on previously saved Al Jazeera media URLs while Course 1 is active.

Unlock Course 2 only when:
1. Gateway Book 2 foundation is complete; and
2. the learner passes an A1 readiness checkpoint showing they can follow simple fully-Arabic instructions/dialogues without constant English translation.

At activation, re-search and verify every Al Jazeera media item because previously saved media may be missing/unavailable. If the media remains unavailable, substitute another graded Arabic-first MSA source while preserving the immersion-course role.

## Media-source policy
During Course 1, prefer beginner-friendly, directly consumable media with English support:
1. the verified Gateway to Arabic Book 2 YouTube series;
2. free public video/audio from educational institutions;
3. university/open educational resources with audio;
4. simple public YouTube MSA explanations for reinforcement.

Once the immersion gate is passed, gradually increase Arabic-only graded media.

### Temporarily excluded source family
Do **not** use ArabicPod101 or any ArabicPod101-branded website, YouTube channel, video, audio, transcript, lesson, playlist, or derived source ID anywhere in the active Arabic curriculum, source registry, progress state, review queue, or flashcard citations. This exclusion remains in force until the user explicitly asks to restore that source family.

The first two completed lessons are preserved as concept milestones rather than provider-specific completions.

## Variants
Keep these distinct:
1. MSA — primary backbone for formal speech, media, reading, writing, cross-region communication.
2. Conversational dialect — add as a parallel branch after a stable A2/B1 MSA base. Do not silently substitute dialect content for MSA.
3. Quranic/Classical Arabic — light exposure may begin early; systematic grammar/lexicon becomes a parallel branch from A2/B1 onward.

Every lesson/card/source must record variety: `msa`, `classical`, `quranic`, or a named dialect.

## Audio-first standard
Target roughly 70–85% of consumption time as audio-capable material.
Each media item records `visual_dependency`: none/helpful/periodic/high.

For an audio/video lesson:
1. first pass — listen before relying on text when feasible;
2. retrieve what was understood;
3. second pass — shadow/repeat;
4. inspect Arabic text/visuals and English explanation as needed;
5. final pass — listen again with less support.

Do not force blind Arabic-only listening at the beginning when it prevents comprehension. Reduce English scaffolding progressively instead.

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
1. Read `progress/current.json` and the active course file.
2. Verify the exact media actually completed.
3. Extract main ideas.
4. Search existing Arabic cards for semantic overlap.
5. Add only high-utility new vocabulary, grammar, phrase, pronunciation, or listening distinctions.
6. Deepen existing cards when the concept already exists.
7. Keep Arabic-script-only fronts and complete eight-layer backs.
8. Store public/open source IDs.
9. Update active-course progress and spaced-reinforcement exposure counts.
10. Check whether a beginner-appropriate spaced review item is due.
11. Otherwise advance to the next Gateway course video.
12. Do not select Al Jazeera while Course 1 is active.
13. Update `resolved_media.json`, `progress/tracks/arabic-msa-to-c2.json`, `progress/current.json`, `progress/review_queue.json`, and `NEXT.md`.
14. Keep paused MATS progress untouched.

## Arabic flashcards
Use `docs/ARABIC_FLASHCARD_STANDARD.md`. Do not dump every lesson word into cards. Prefer high-frequency, generative language. Arabic review-card fronts remain Arabic-script-only; all translations, definitions, examples, metadata, and eight layers belong on the back.

## Roadmap
Canonical long-range path:
`playlists/audio/arabic/msa-to-c2/roadmap.json`

A1 course manifest:
`playlists/audio/arabic/msa-to-c2/a1-foundations/playlist.json`
