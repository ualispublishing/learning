# Arabic Flashcard Standard

Arabic cards extend the repository's general layered-card standard with language-specific fields.

## Core principle
Cards must train retrieval and production, not passive recognition alone. Prefer a smaller set of high-utility cards that generalize to many sentences.

## Front/back display contract
For active Arabic review cards:
- `front` must contain Arabic script only.
- No English question, translation, transliteration, definition, hint, or explanatory label belongs on the front.
- Tashkeel is allowed and encouraged at A1/A2 when it helps pronunciation.
- Contrast cards may place two or more Arabic forms on the front, e.g. `أَنْتَ / أَنْتِ` or `كَيْفَ حَالُكُمَا؟ / كَيْفَ حَالُكُمْ؟`.
- All translations, explanations, definitions, roots, grammar/register notes, examples, metadata, and layered learning material belong on the back.

The default retrieval direction is Arabic -> meaning/use. Alternate directions such as meaning -> Arabic production, audio recognition, cloze, dictation, and sentence production are scheduled as review representations rather than replacing the canonical front.

## Audio-review contract
Every active Arabic knowledge card should also have a short TTS-ready/spoken representation. This is an **audio digest**, not a spoken dump of the full eight-layer back.

Store audio representations in a companion audio-review file or in an `audio_review` object when the consuming app supports it.

Recommended fields:
- `spoken_front_ar` — the exact Arabic front, pronounced naturally; Arabic comes first.
- `pause_seconds` — normally 2.5–4 seconds for retrieval before the answer.
- `spoken_answer` — a concise, natural explanation suitable for listening, normally 8–25 seconds.
- `spoken_example_ar` — one short Arabic example where useful.
- `spoken_example_en` — its concise English meaning when useful.
- `repeat_front_after_answer` — normally true at A1/A2.
- `pronunciation_focus` — optional note for sounds/endings worth hearing.
- `tts_ready` — true when punctuation and wording have been edited for natural speech.

### Audio style
Audio review must sound pleasant and purposeful rather than like a database being read aloud:
- Do not read field names, JSON keys, source URLs, tags, IDs, CEFR labels, or all eight layer headings.
- Use one short idea per spoken answer.
- Prefer natural phrasing such as: `مَرْحَبًا. ... Hello, or hi. A general greeting you can use at any time. مَرْحَبًا.`
- For contrast cards, clearly separate forms with a short pause and explain only the distinction being retrieved.
- For grammar cards, state the rule simply, then give one spoken example.
- Keep Arabic pronunciation content in Arabic script; transliteration is not needed in the spoken script.
- At A1/A2, repeat the Arabic form once after the explanation to strengthen the sound-to-form association.
- Avoid long English explanations in audio. The complete layered back remains available visually.

### Preferred audio sequence
1. Speak the Arabic front naturally.
2. Pause for retrieval.
3. Give the concise meaning/rule.
4. Give one short Arabic example when valuable.
5. Repeat the Arabic front or key contrast once.

The audio representation should typically stay under 30 seconds per card.

## Card classes

### 1. Lexeme cards
Use for high-frequency words or words central to the lesson.

Recommended fields:
- `id`
- `front`
- `lemma_ar`
- `vocalized_ar`
- `part_of_speech`
- `variety`
- `cefr_estimate`
- `translations`: `en`, `ur`, `fr` (one concise translation each when available)
- `definition_ar`
- `definition_en`
- `root` when useful and reliable
- `pattern` when useful
- `synonyms_ar` (normally two if genuinely useful)
- `example_ar`
- `example_en`
- `audio_source_id`
- `prerequisites`
- `sources`
- `layers`

Do not force a root/pattern onto loanwords or forms where it adds little value.

### 2. Grammar cards
The front should be the Arabic contrast or Arabic form being retrieved, not an English instruction.
Examples:
- `أَنْتَ / أَنْتِ`
- `ـكَ / ـكِ`
- `كَيْفَ حَالُكُمَا؟ / كَيْفَ حَالُكُمْ؟`

The back should explain the rule, include one clean example, a contrast where valuable, a common error, and a transfer prompt.

### 3. Phrase / chunk cards
Use for expressions best learned as units, especially greetings, discourse markers, collocations, formulaic religious/cultural expressions, and high-frequency frames. Store register and variety.

### 4. Pronunciation/listening cards
Use sparingly for contrasts that repeatedly cause comprehension or production errors. Prefer minimal-pair or listen-and-identify prompts. Record phoneme/feature and an audio source.

### 5. Practice cards
Put sentence transformation, dictation, cloze production, parsing, and extended response tasks in `practice.json`, not `knowledge.json`.

## Layered back
Every knowledge card retains:
1. Direct Answer
2. Concept Expansion
3. Example
4. Boundaries / Misconceptions
5. Connections / Memory
6. Transfer Prompt
7. Mastery Evidence
8. Sources

The audio digest never replaces these layers.

## Selection threshold
Create a card if the item is:
- high frequency;
- grammatically generative;
- essential for future comprehension;
- a recurring collocation/chunk;
- a meaningful pronunciation contrast;
- difficult enough that retrieval practice adds value.

Do not create a card merely because a word appears once.

## Transliteration
Arabic script is canonical. Transliteration may exist as temporary backside pronunciation support at A1/A2, but never as the canonical front.

## Tashkeel
Early cards should preserve enough tashkeel to support correct pronunciation. Gradually reduce nonessential tashkeel at B1+ while retaining it where ambiguity matters.

## MSA vs dialect
Never merge dialect and MSA forms into one answer without labeling them. A card may cross-link equivalent forms, but each form must state its variety/register.

## Vocabulary progression
Prefer:
- A1/A2: concrete high-frequency vocabulary + core verbs + function words + productive sentence frames.
- B1/B2: abstract vocabulary, derivational families, collocations, discourse markers.
- C1/C2: register, nuance, idiom, rhetorical devices, specialized vocabulary, near-synonym distinctions.

## Mastery
A vocabulary card reaches level 4 only when the learner can retrieve the item, use it naturally in a new sentence, recognize it in audio, and distinguish it from close alternatives when relevant.
