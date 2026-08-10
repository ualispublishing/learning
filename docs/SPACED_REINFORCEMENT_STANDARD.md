# Spaced Reinforcement Standard

This repository uses spaced retrieval and varied re-exposure at both the flashcard and media-playlist levels.

## Why
Repeated study should not mean replaying the identical explanation immediately. The goal is effortful retrieval followed by a new representation of the same underlying concept. Research on spacing and retrieval practice supports distributed review and active recall over massed restudy; L2 vocabulary research likewise supports spaced, successful retrieval over simple rereading.

## Two reinforcement systems

### 1. Card-level spaced repetition
Each canonical concept can generate multiple retrieval representations without creating duplicate knowledge records:
- definition/meaning recall;
- audio -> meaning recognition;
- English/meaning -> Arabic production;
- Arabic -> sentence production;
- cloze in a new sentence;
- contrast/discrimination with a confusable item;
- morphology/root-family retrieval;
- dictation or transcription;
- translation/reformulation;
- free recall / teach-back.

Representations should point to one canonical concept/card ID.

Default expanding review opportunities after first learning:
- R1: after ~1–2 subsequent learning items;
- R2: after ~4–6 items;
- R3: after ~10–14 items;
- R4: after ~25–35 items;
- R5: at the next CEFR-stage bridge;
- long-term: periodic mixed retrieval thereafter.

These are scheduling heuristics, not rigid laws. Failed retrieval shortens the next interval; effortless repeated success lengthens it.

### 2. Playlist-level spiral reinforcement
A playlist is not strictly linear. Important concepts return later through a different source, speaker, context, or task.

A concept cluster should ideally progress through:
1. **Primary explanation** — clear learner-oriented introduction.
2. **Near transfer** — same concept in a new dialogue/context after a short gap.
3. **Alternate presentation** — different teacher/source/speaker after a medium gap.
4. **Authentic encounter** — native or semi-authentic material using the concept naturally.
5. **Integrated synthesis** — later lesson requires the old concept together with newer material.

Do not place alternate explanations back-to-back unless correcting a misunderstanding.

## Playlist ratios
Default target across a rolling block of 10 media items:
- A1–A2: ~7 new/core items, ~3 reinforcement/transfer items.
- B1–B2: ~6 new/core, ~4 reinforcement/authentic-transfer.
- C1–C2: ~5 new/specialized, ~5 synthesis/transfer/authentic items.

The ratio may change based on performance.

## Retrieval-before-replay rule
Before a reinforcement item, prompt the learner mentally or explicitly to retrieve what they already know. Examples:
- “Before listening, say three greetings and when you would use each.”
- “Predict the masculine/feminine form.”
- “Summarize the earlier lesson in Arabic for 30 seconds.”

Then consume the new representation. This prevents familiarity from being mistaken for mastery.

## Variation dimensions
When selecting a reinforcement item, vary at least one dimension and preferably two:
- different teacher/source;
- different speaker voice;
- different scenario;
- different lexical surface form;
- different register;
- slower learner speech vs natural speed;
- recognition vs production;
- isolated grammar vs authentic use;
- listening vs dialogue shadowing vs dictation vs summary.

For Arabic, preserve the MSA/dialect label. Variety is not permission to mix varieties without warning.

## Interleaving
Do not finish an entire microtopic and abandon it. Mix old grammar/vocabulary into later themes. At B1+, review should increasingly be embedded in authentic topics rather than labeled as a review lesson.

## Media item metadata
Media playlist items may include:
- `role`: `core`, `reinforcement`, `transfer`, `checkpoint`, `authentic`;
- `reinforces`: canonical concept/module IDs;
- `representation`: explanation/dialogue/news/story/grammar/shadowing/dictation/etc.;
- `source_family`;
- `visual_dependency`;
- `retrieval_before`: a short prompt;
- `status`: queued/next/completed/skipped.

## Completion algorithm
When the user says `complete` or `finished`:
1. Process the completed lesson and cards normally.
2. Increment exposure counters for concepts encountered.
3. Check whether any earlier high-value concept is due for R1–R5.
4. If due, prefer inserting or selecting a verified alternate-source reinforcement item before too much new material accumulates.
5. Avoid repeating the same source unless its presentation is meaningfully different.
6. If the learner failed or expressed confusion, prioritize corrective reinforcement sooner.
7. Otherwise advance to the next prerequisite-appropriate item.

## What not to do
- Do not rewatch the same lesson immediately just because it was difficult.
- Do not create duplicate cards for every representation.
- Do not review every concept at identical intervals.
- Do not let review consume so much time that new input stalls.
- Do not confuse easy recognition with productive mastery.

## Evidence basis
See `sources/learning-science.json` for research used to motivate this design.
