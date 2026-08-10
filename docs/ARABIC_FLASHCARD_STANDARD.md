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
