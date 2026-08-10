# Arabic Learning Protocol — MSA to C2

This file is mandatory reading for agents working on the Arabic track.

## Goal
Build from the current Arabic foundation toward functional CEFR C2 mastery, with Modern Standard Arabic (MSA) as the core. The system is audio-first, source-diverse, checkpoint-based, and flashcard-integrated.

The active few-month program is **not a promise of C2**. It is an intensive, complete beginner-to-independent foundation intended to reach roughly strong A2 / early B1 if the learner passes the checkpoints. Continue from that state toward B2, C1 and C2 based on demonstrated proficiency rather than calendar time.

## Active-track commands
When Arabic is active:
- `complete` = mark the exact current media item complete, process its content into the learning system, update spaced reinforcement, and advance to the next active free item.
- `finished` = same as `complete`.
- `what's next` = read repo state and return the exact next media/lesson.
Never infer completion from chat memory when repo state is available.

## Active course
`playlists/audio/arabic/courses/free-intensive-20-week/`

Files:
- `plan.json` — 20-week intensive curriculum and checkpoints.
- `playlist.json` — ordered media queue; extend/resolve exact URLs as items become due.

### Active free source stack
1. **ANU Press — Marhaba!**: primary 23-lesson MSA curriculum spine with multimedia/audio and four-skill development.
2. **University of Wisconsin–Madison MSA resources**: audio-first retrieval, alternate speakers and targeted reinforcement.
3. **Michigan State University Elementary Arabic I/II OER**: structured vocabulary, grammar, reading, writing, audio and interactive practice.
4. **LQToronto / Madina Books**: parallel English-supported grammar clinic and Quranic/Classical bridge; do not let it replace communicative MSA input/output.
5. **DLI GLOSS Arabic-MSA**: activate after beginner foundations for graded listening/reading transfer toward intermediate and advanced comprehension.

All active sources must remain free/public/open unless the user explicitly asks to add paid material.

## Deferred/optional area
Gateway to Arabic and Al Jazeera are intentionally outside the active course:
- `playlists/audio/arabic/deferred/gateway-to-arabic-book-2/playlist.json`
- `playlists/audio/arabic/deferred/al-jazeera-immersion/playlist.json`
- source metadata: `sources/arabic-deferred.json`

Do not surface either course as `next` unless the user explicitly restores it.

Al Jazeera remains useful later as Arabic-first immersion, but its media must be re-searched and verified before reuse because previously stored media may be unavailable.

### ArabicPod101 exclusion
Do **not** use ArabicPod101 or ArabicPod101-branded websites, YouTube videos, audio, transcripts, playlists, or derived source IDs unless the user explicitly asks to restore that source family.

## MSA vs dialect
MSA is the active backbone.

MSU contains some Egyptian Arabic conversation modules. These must be:
- skipped in the required MSA core, or
- intentionally used as optional dialect exposure with `variety: egyptian`.

Never merge Egyptian forms into MSA cards without labeling them.

## Audio-first standard
Target approximately 75–120 minutes of audio-capable work on full study days within the active intensive plan.

For audio/video lessons:
1. listen before leaning heavily on text when feasible;
2. retrieve what was understood;
3. replay and shadow/repeat;
4. inspect Arabic text and English explanation as needed;
5. produce a response, transformation, summary, or example;
6. finish with another less-supported listen.

Do not make beginner comprehension artificially difficult by hiding all support. English scaffolding should decrease gradually as proficiency rises.

## Daily intensive template
Default full study day:
- 45–60 min core curriculum;
- 30–45 min listening/shadowing;
- 25–35 min spaced flashcards;
- 25–40 min speaking/writing production;
- 20–30 min grammar clinic on selected days.

Study six days per week by default. One lighter day may use only spaced review and passive/graded listening.

## Spaced media reinforcement
Use `docs/SPACED_REINFORCEMENT_STANDARD.md`.

Do not study one topic once and abandon it. Important concepts should recur through:
1. primary explanation;
2. near-transfer;
3. alternate speaker/source;
4. delayed listening/reading encounter;
5. mixed synthesis with newer material.

Early rolling target: roughly 70% new material / 30% reinforcement, moving toward 60/40 as input becomes more authentic.

## Completion processing
For every completed lesson/media item:
1. Read `progress/current.json`, the active course playlist, and review queue.
2. Verify the exact media completed.
3. Extract only the main/high-utility concepts.
4. Search existing Arabic cards for semantic overlap.
5. Add only useful new vocabulary, grammar, phrase, pronunciation, or listening distinctions.
6. Deepen existing cards when a concept already exists.
7. Keep **Arabic-script-only fronts** and complete eight-layer backs.
8. For each active knowledge card added or materially changed, create/update a **pleasant short audio digest** following `docs/ARABIC_FLASHCARD_STANDARD.md`. Keep it TTS-ready, Arabic-first, concise, and under roughly 30 seconds instead of reading the entire layered back aloud.
9. Store/update audio-review companions under `subjects/arabic/audio-review/`; the current combined companion is `subjects/arabic/audio-review/current.json`.
10. Record free/open source IDs.
11. Update concept exposure counts and review due-state.
12. If a spaced reinforcement item is due, select it when pedagogically appropriate.
13. Otherwise advance to the next item in the active free intensive playlist/plan.
14. Update `resolved_media.json`, `progress/tracks/arabic-msa-to-c2.json`, `progress/current.json`, `progress/review_queue.json`, and `NEXT.md`.
15. Keep paused MATS progress untouched.

## Flashcards
Use `docs/ARABIC_FLASHCARD_STANDARD.md`.

Front:
- Arabic script only.

Back:
- English/Urdu/French translation where applicable;
- Arabic definition;
- English definition;
- root/pattern when useful and reliable;
- synonyms where useful;
- Arabic/English example;
- grammar/register/variety metadata;
- prerequisites/tags/source IDs;
- all eight Knowledge Atlas layers.

Audio companion:
- speak the Arabic front first;
- pause for recall;
- give one concise natural meaning/rule;
- add one short Arabic example when useful;
- repeat the Arabic form at A1/A2;
- never read metadata, URLs, layer labels, or the full long backside aloud.

Do not generate a card merely because a word appeared once. Prefer high-frequency, generative, repeatedly useful language.

## Checkpoints
Playlist completion does not equal CEFR mastery.

### A1 exit
Can handle routine personal information and simple exchanges, form basic questions/statements, understand familiar slow/clear MSA, and read/write short vocalized material.

### A2 exit
Can understand the main point of familiar clear MSA, describe self/family/study/routine, narrate simple past events, and write connected short paragraphs.

### B1 bridge
Can follow clear standard speech on familiar subjects and produce connected summaries, descriptions and opinions without heavy scripting.

### B2/C1/C2
Progressively increase DLI GLOSS difficulty and authentic MSA sources. C2 requires near-complete comprehension across registers and precise spontaneous production/synthesis; it is not unlocked by a fixed number of weeks.

## Repository pointers
- Long-range roadmap: `playlists/audio/arabic/msa-to-c2/roadmap.json`
- Active course: `playlists/audio/arabic/courses/free-intensive-20-week/`
- Active source registry: `sources/arabic.json`
- Deferred source registry: `sources/arabic-deferred.json`
- Active progress: `progress/tracks/arabic-msa-to-c2.json`
- Audio flashcard companion: `subjects/arabic/audio-review/current.json`
