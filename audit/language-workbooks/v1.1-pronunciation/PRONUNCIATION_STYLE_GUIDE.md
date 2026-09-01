# Pronunciation audit style guide

This guide fixes the conventions used by the v1.1 row-by-row pronunciation audit. The machine-generated IPA and learner hints are candidates only; this document governs human adjudication.

## General rules

1. Audit the target text and its intended English sense together. Pronunciation is sense-dependent when an unvocalized spelling has more than one standard reading.
2. `ipa` is a broad phonemic transcription suitable for learners, not a narrow phonetic transcription of one speaker.
3. Do not invent a single reading when the workbook entry intentionally covers two distinct standard readings. List the readings in the same semantic order as the English gloss, separated by ` / `.
4. The learner hint must preserve contrasts that matter in the target language. It is not permitted to replace a difficult sound with a misleading English sound merely to look familiar.
5. Do not add contextual variants that are irrelevant to the workbook meaning. Conversely, sentence pronunciation must reflect the actual sentence context rather than an isolated-word default.
6. `PASS` means both the IPA and learner hint candidates already meet these conventions. If either field changes, use `REPAIR` and record the reason.
7. `HOLD` is reserved for a genuinely unresolved linguistic ambiguity. `PENDING` and `HOLD` block release finalization.

## Arabic

Target standard: careful Modern Standard Arabic (MSA).

### IPA

- Use broad MSA phonemes: /ʔ b t θ d ð r z s ʃ sˤ dˤ tˤ ðˤ ʕ ɣ f q k l m n h w j/ and /a i u aː iː uː aj aw/ as applicable.
- Preserve /ʕ/ and /ʔ/; do not silently delete ʿayn or hamza.
- Use the pause/citation form where case or mood endings are context-dependent. Keep lexical endings that are part of the word itself, e.g. /kaːna/, /qaːla/, /maʕa/.
- For an unvocalized homograph whose workbook gloss deliberately spans different readings, include each relevant MSA reading, e.g. `أن` → /ʔan/ / /ʔanna/, `من` → /min/ / /man/.
- Do not accept eSpeak's vowel omission on Arabic consonantal spellings when it produces a non-MSA lexical form.

### Learner hint

Use a consistent readable transliteration rather than an English respelling:

- long vowels: `ā ī ū`
- hamza: `ʾ`
- ʿayn: `ʿ`
- ث `th`, ذ `dh`, ش `sh`, خ `kh`, غ `gh`
- emphatics: `ṣ ḍ ṭ ẓ`
- ح `ḥ`, ق `q`
- /j/ is written `y`

Examples: `في` → `fī`; `على` → `ʿalā`; `شيء` → `shayʾ`.

## French

Target standard: neutral educated Metropolitan/Hexagonal French suitable for general learners.

### IPA

- Use broad standard French IPA.
- Preserve phonemic contrasts needed to distinguish the audited word or sentence; do not force marginal speaker-specific contrasts where both realizations are standard.
- For isolated vocabulary, do not manufacture liaison. For sentences, include liaison only where it is obligatory or clearly part of neutral careful pronunciation.
- Treat schwa and optional consonant realization contextually; do not present an optional colloquial deletion as the sole careful form.

### Learner hint

- Use a stable, readable cue system, not ordinary French spelling copied into the hint field.
- Preserve front rounded vowels, nasal vowels, and French `r` distinctions through the pronunciation key rather than mapping them to misleading English vowels/consonants.
- Prefer syllable boundaries or hyphens where they materially improve readability.

## Urdu

Target standard: neutral educated Standard Urdu.

### IPA

- Preserve aspiration, retroflexion, vowel length, nasalization, and breathy/voiced distinctions where phonemic.
- Restore short vowels that are absent from ordinary Urdu orthography when required by the standard lexical reading.
- Audit Perso-Arabic spellings by the intended Urdu word and workbook meaning, not by an Arabic or Persian default pronunciation.
- When a spelling genuinely has more than one standard Urdu reading matching different included senses, list the relevant readings in semantic order.

### Learner hint

Use a consistent transliteration that makes Urdu contrasts visible. At minimum, distinguish:

- long vowels `ā ī ū`
- retroflexes `ṭ ḍ ṛ`
- aspiration with `h` digraphs (`kh`, `gh`, `chh`, `jh`, `ṭh`, `ḍh`, `th`, `dh`, `ph`, `bh`) where applicable
- nasalized vowels with `̃` when necessary
- Urdu/Perso-Arabic consonants whose merger would misteach the word should remain distinguishable in the key.

## Release gate

No pronunciation-enhanced workbook may be built from `candidates/`. Only the six files produced by `scripts/finalize_language_workbook_pronunciation.py` after all 6,000 rows are `PASS` or fully specified `REPAIR` may enter the v1.1 PDF build.
