# Arabic Learning Protocol — MSA to C2

This file is mandatory reading for agents working on the Arabic track.

## Goal
Build from the current Arabic foundation toward functional CEFR C2 mastery, with Modern Standard Arabic (MSA) as the core. The system is audio-first, flashcard-integrated, spaced, and checkpoint-based.

## Active course
Primary course:
`playlists/audio/arabic/courses/arabicpod101-newbie-season-1/playlist.json`

Use **ArabicPod101 Newbie Season 1** as the active beginner audio sequence. Lessons 1 and 2 are already complete; resume at lesson 3.

The previous ArabicPod101 exclusion is **cancelled**. ArabicPod101 website lessons, audio, transcripts, review tracks, and source IDs may again be used in the active Arabic curriculum and flashcard citations.

### Secondary/free enrichment
Preserve the researched free/open intensive plan at:
`playlists/audio/arabic/courses/free-intensive-20-week/`

It is now secondary enrichment/reference material, not the default `next` sequence. Use ANU, Wisconsin, MSU, LQToronto/Madina and DLI GLOSS when they add useful alternate explanations, spaced reinforcement, output practice or later proficiency material.

### Deferred/optional
Keep these outside the automatic sequence:
- `playlists/audio/arabic/deferred/gateway-to-arabic-book-2/playlist.json`
- `playlists/audio/arabic/deferred/al-jazeera-immersion/playlist.json`

Al Jazeera remains a later Arabic-first immersion option and must be reverified before reuse.

## Active commands
- `complete` / `finished`: verify the exact current ArabicPod101 lesson, mark it complete, extract/deepen useful cards, update audio-review scripts and spaced review, then resolve the next ArabicPod101 lesson from the live lesson library.
- `what's next`: return the exact current ArabicPod101 lesson from repo state.

Do not restart completed lessons unless they are intentionally scheduled as spaced reinforcement.

## Audio-first lesson protocol
1. Listen once for the dialogue/overall meaning.
2. Replay and shadow the Arabic.
3. Pause before translations when useful and retrieve meaning.
4. Use the English explanation/transcript to clarify grammar or vocabulary.
5. Produce the key phrases yourself.
6. Finish with another less-supported listen.

## Flashcards
Use `docs/ARABIC_FLASHCARD_STANDARD.md`.

Canonical visual card:
- Arabic-script-only front.
- Full translations, definitions, grammar/register notes, examples, sources and all eight Knowledge Atlas layers on the back.

Audio companion:
- Arabic front spoken first;
- short retrieval pause;
- concise natural meaning/rule;
- short Arabic example where useful;
- repeat the Arabic form at A1/A2;
- do not read metadata or the full layered back aloud.

Current audio companion:
`subjects/arabic/audio-review/current.json`

## Completion processing
For every completed lesson:
1. Read `progress/current.json`, active ArabicPod101 playlist, track progress and review queue.
2. Verify the live ArabicPod101 page/lesson.
3. Extract only main/high-utility concepts.
4. Search existing cards for overlap and deepen rather than duplicate.
5. Add new cards only when high-frequency, generative, or essential.
6. Keep Arabic-only fronts and full eight-layer backs.
7. Create/update pleasant audio-review scripts for changed/new cards.
8. Record ArabicPod101 source IDs plus alternate sources when genuinely used.
9. Update exposure counts and spaced-review due state.
10. Advance to the next ArabicPod101 lesson, resolving its exact URL live.
11. Update playlist, `resolved_media.json`, track progress, `progress/current.json`, review queue and `NEXT.md`.
12. Keep paused MATS progress untouched.

## Variety policy
MSA remains the backbone. If a lesson contains informal/dialectal language, record that explicitly rather than silently treating it as MSA. Dialect and Quranic/Classical branches remain separate.

## Long-term progression
ArabicPod101 Newbie Season 1 is the current beginner sequence, not the entire C2 curriculum. After foundational material, use broader structured/audio and authentic resources, including the preserved free intensive plan and DLI GLOSS, according to demonstrated proficiency.

CEFR levels are checkpoint-based; playlist completion alone does not prove mastery.
