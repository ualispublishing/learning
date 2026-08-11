# Arabic Learning Protocol — MSA to C2

This file is mandatory reading for agents working on the Arabic track.

## Goal
Build from the current Arabic foundation toward functional CEFR C2 mastery, with Modern Standard Arabic (MSA) as the core. The system is audio-first, flashcard-integrated, spaced, source-diverse, and checkpoint-based.

## ArabicPod exclusion
ArabicPod101 is excluded from the current repository learning scheme.

Do **not** use ArabicPod101 websites, lessons, audio, transcripts, playlists, source IDs, or derived lesson metadata in active curriculum, progress, sources, or flashcard provenance unless the user explicitly reverses this instruction later.

Previously learned concepts remain learned; remove provider provenance rather than deleting the knowledge itself.

## Active audio-first course
Primary course:
`playlists/audio/arabic/courses/alifbee-msa-audio/playlist.json`

Use the curated **AlifBee MSA audio-first path** as the current beginner listening spine. AlifBee's podcast is directly playable, beginner-oriented, English-supported, and explicitly teaches Modern Standard Arabic.

Current next item is stored in `progress/current.json` and `NEXT.md`.

### Secondary audio/grammar sources
Use these when the primary podcast has a curriculum gap or a concept needs another representation:
- LQToronto / Madina Arabic English audio lessons — grammar-depth clinic;
- Michigan State University Elementary Arabic OER — structured MSA grammar/output validation;
- University of Wisconsin MSA materials — listening/retrieval reinforcement, including recorded flashcard activities only as reinforcement;
- DLI GLOSS Arabic-MSA — graded listening/reading after the beginner foundation;
- ANU Marhaba — multimedia structured MSA reference.

The researched free/open intensive plan remains at:
`playlists/audio/arabic/courses/free-intensive-20-week/`

It is secondary curriculum scaffolding, not the automatic next queue.

### Deferred/optional
Keep these outside the automatic sequence:
- `playlists/audio/arabic/deferred/gateway-to-arabic-book-2/playlist.json`
- `playlists/audio/arabic/deferred/al-jazeera-immersion/playlist.json`

Al Jazeera remains a later Arabic-first immersion option and its media must be reverified before reuse.

## Active commands
- `complete` / `finished`: verify the exact current audio item, mark it complete, extract/deepen useful cards, update audio-review scripts and spaced review, then advance to the next appropriate audio lesson.
- `what's next`: read repo state and return the exact current audio lesson.

Do not restart mastered concepts except as intentionally spaced reinforcement.

## Audio-first lesson protocol
1. Listen once for the overall meaning.
2. Replay and shadow the Arabic.
3. Pause before explanations when useful and retrieve meaning yourself.
4. Use English support/transcripts only to clarify gaps.
5. Produce the key language aloud.
6. Finish with another less-supported listen.

Primary `next` items should be comfortable, continuous audio/podcast/video lessons—not flashcard webpages.

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
For every completed lesson/media item:
1. Read `progress/current.json`, the active AlifBee playlist, track progress and review queue.
2. Verify the live audio episode/source.
3. Extract only main/high-utility concepts.
4. Search existing cards for overlap and deepen rather than duplicate.
5. Add new cards only when high-frequency, generative, or essential.
6. Keep Arabic-only fronts and complete eight-layer backs.
7. Create/update pleasant audio-review scripts for changed/new cards.
8. Record only sources genuinely used; do not restore excluded source IDs.
9. Update exposure counts and spaced-review due state.
10. Advance to the next audio-first item, resolving exact URLs live when needed.
11. Update playlist, `resolved_media.json`, track progress, `progress/current.json`, review queue and `NEXT.md`.
12. Keep paused MATS progress untouched.

## Variety policy
MSA remains the backbone. When a source mixes MSA and dialects, extract MSA into the core deck and label dialect forms separately. Dialect and Quranic/Classical branches remain distinct.

## Long-term progression
The AlifBee podcast is the current audio spine, not by itself the entire C2 curriculum. Use deeper grammar, graded listening, authentic MSA, Quranic/Classical material, and later dialect branches as proficiency grows.

CEFR advancement is checkpoint-based; playlist completion alone does not prove mastery.
