# Arabic Audio-First Source Research

## Decision
Use **AlifBee — Complete Arabic Audio Course For Absolute Beginners** as the current free MSA audio spine, curated by prerequisite rather than publication date.

Primary playlist:
`playlists/audio/arabic/courses/alifbee-msa-audio/playlist.json`

## Why AlifBee is active
- The podcast is directly playable and designed for listening while walking, driving, or doing other tasks.
- It explicitly teaches Modern Standard Arabic and is aimed at Arabic learners.
- Episodes include clear pronunciation, English explanations, vocabulary, grammar, and examples.
- It has a large and actively maintained episode library, so the repository can curate by topic and prerequisite.
- It is free to listen to, so the core scheme does not require a purchase.

Main weakness: the podcast publication order is topical rather than a clean CEFR syllabus. Therefore the repo must curate episodes and use secondary sources for grammar/curriculum gaps.

## Strong alternatives researched

### Pimsleur Modern Standard Arabic
**Best pure structured audio option if paid access is acceptable.**

- 3 levels / 90 core lessons.
- Each core lesson is about 30 minutes.
- Hands-free / driving-friendly design.
- Explicit Modern Standard Arabic course.
- Strong prompt-response speaking and spaced recall.

Weaknesses for this repo: paid subscription/purchase; reading and explicit grammar are secondary to oral training.

Official reference:
`https://www.pimsleur.com/learn-arabic-modern-standard/`

### Michel Thomas Foundation Modern Standard Arabic
**Best compact grammar-through-audio course.**

- Roughly 10 hours of audio material.
- English-speaking teacher + native Arabic speaker + two students.
- Builds sentences sequentially through active listening and response.
- Explicitly Modern Standard Arabic.

Weakness: excellent beginner foundation but too short to be the whole long-term course; paid beyond the introductory sample.

Official reference:
`https://michelthomas.com/landing-page/mt-modern-arabic/`

### Mango Languages — Modern Standard Arabic
**Strong structured interactive/audio alternative.**

- MSA course currently lists 3 units, 15 chapters, and 78 lessons.
- Dialogue/listening is central, with grammar/culture support.
- Access may be free through participating libraries/schools, otherwise availability varies.

Weakness: more screen-interactive than a true podcast/hands-free course.

Reference:
`https://mangolanguages.com/`

### DLI Modern Standard Arabic / GLOSS
**Best free large-scale later-stage audio bank.**

- DLI MSA materials include many units and audio files.
- GLOSS provides graded MSA listening/reading exercises and later authentic-style material.

Weakness: government-training materials can feel dated/dry and are not the most pleasant beginner daily listening spine.

References:
`https://gloss.dliflc.edu/`
`https://www.fsi-language-courses.org/arabic/courses/dli-modern-standard-arabic-course/`

## Supporting free sources
- LQToronto / Madina audio: English-supported grammar clinic.
- ANU Marhaba: structured multimedia MSA reference.
- MSU Elementary Arabic I/II: structured grammar, vocabulary, reading/writing and embedded audio.
- Wisconsin MSA resources: alternate-speaker listening and retrieval reinforcement; flashcard-style pages are reinforcement only.

## Operating rule
The primary lesson queue should favor **continuous listenable media**. Written pages, quizzes and flashcard activities can support the course but should not become `next` unless the user explicitly asks for them.

For each completed audio item:
1. extract only high-utility new concepts;
2. deduplicate against existing Arabic cards;
3. keep Arabic-only fronts and full layered backs;
4. update the pleasant audio-review companion;
5. use another source to fill any grammar or progression gap;
6. keep MSA and dialect forms explicitly labeled.
