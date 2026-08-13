# Reading Passage Production Standard — Arabic, French, Urdu

This is the mandatory production contract for the graded reading curriculum under `reading/`.

Research rationale: `docs/READING_PASSAGE_RESEARCH.md`  
Research registry: `sources/reading-acquisition.json`  
Existing spaced-review rules: `docs/SPACED_REINFORCEMENT_STANDARD.md`

## 1. Non-negotiable goals

Every passage must serve at least three of these functions, and most should serve more:

- meaningful reading comprehension;
- reading fluency;
- contextual vocabulary acquisition;
- retrieval of previously learned vocabulary;
- grammar reinforcement in context;
- interleaving / discrimination;
- discourse and cohesion development;
- inference;
- register / style development;
- cumulative synthesis.

Do not create filler text solely to hit a passage count.

## 2. Canonical file format

Canonical production format is **JSONL**, one passage object per line, grouped by language and CEFR level:

`reading/<language>/<level>/passages.jsonl`

Examples:

- `reading/arabic/a1/passages.jsonl`
- `reading/french/b2/passages.jsonl`
- `reading/urdu/c2/passages.jsonl`

A plain-text or app-specific export may be generated later, but JSONL is the source of truth because it supports incremental appends, validation, ledgers, and streaming ingestion.

## 3. Passage ID

IDs are immutable:

`<lang>-<level>-u<unit>-p<passage>`

Examples:

- `ar-a1-u01-p01`
- `fr-b2-u04-p03`
- `ur-c1-u10-p06`

Do not reuse an ID after a passage has been published. A replacement gets a revision field or a new ID.

## 4. Required passage object

Each JSON object must contain:

- `id`
- `language`: `ar`, `fr`, or `ur`
- `cefr`: `A1`–`C2`
- `unit`
- `sequence`
- `revision`
- `title`
- `passage_type`
- `genre`
- `domains`
- `topics`
- `text`
- `word_count`
- `sentence_count`
- `estimated_known_token_coverage`
- `new_lexical_targets`
- `review_lexical_targets`
- `grammar_targets`
- `discourse_targets`
- `questions`
- `answer_key`
- `speed_training`
- `quality`

Optional but recommended:

- `source_facts` for fact-checked informational content;
- `cultural_notes_internal`;
- `paired_text_group`;
- `prerequisites`;
- `difficulty_notes_internal`;
- `reader_tags`.

## 5. Passage types

Allowed values:

- `instructional` — introduces a controlled amount of new language;
- `reinforcement` — primarily reuses due material;
- `transfer` — places known material in a meaningfully different context;
- `interleaved` — mixes confusable/related targets;
- `fluency` — high coverage, timed-reading friendly, little or no new material;
- `stretch` — intentionally harder but still supported;
- `checkpoint` — cumulative comprehension + retrieval;
- `paired` — one member of a compare/contrast text pair.

## 6. Level length targets

Calibration bands, not hard laws:

| Level | Standard | Extended |
|---|---:|---:|
| A1 | 90–140 words | 160–220 |
| A2 | 140–220 | 250–350 |
| B1 | 220–350 | 400–550 |
| B2 | 350–550 | 600–900 |
| C1 | 500–800 | 900–1,400 |
| C2 | 700–1,200 | 1,300–2,200 |

The level is determined by the whole difficulty profile, not length alone.

## 7. Lexical-load rules

### Coverage bands

- `fluency`: target ~98.5–99.5% known tokens;
- normal `instructional`: target ~97–98.5%;
- `stretch`: target ~95–97.5%;
- routine passages below ~95% should fail review unless deliberately supported and justified.

### New lexical types per standard passage

Initial target ranges:

- A1: 1–3;
- A2: 2–4;
- B1: 3–6;
- B2: 4–8;
- C1: 6–10;
- C2: 8–14.

These are maximum planning bands, not quotas. Use fewer when the grammar/discourse load is high.

### Known-vocabulary ledger

Known coverage is calculated from:

1. validated root language CSVs;
2. lexical items introduced in prior passages;
3. evidence from the exposure ledger that an introduced item has received adequate successful reinforcement.

Do not mark every previously seen word as fully known forever.

## 8. Contextual introduction standard

Every deliberate new word must include `context_strategy` with one or more of:

- `contrast`
- `cause_consequence`
- `behavior_interpretation`
- `example_instance`
- `restatement`
- `parallel_structure`
- `category_relation`
- `scenario_resolution`
- `morphological_support`

### Quality requirement

At A1–B1, the surrounding context should make the intended sense the overwhelmingly reasonable inference.

Do not write disguised dictionary definitions into the prose when a natural scenario can do the work.

Example principle:

Instead of: “The path was narrow, meaning not wide.”

Use: “Two people could not walk side by side on the path. It was so narrow that they had to walk one behind the other.”

The second version supplies observable consequences rather than translation-like exposition.

## 9. Infer → verify → transfer sequence

When a passage deliberately introduces a new lexical item:

1. learner encounters it in informative context;
2. one question asks for meaning/function from context;
3. the answer key verifies the intended sense;
4. a later question or passage uses it again in a new context;
5. at least one later exposure requires retrieval rather than recognition.

Never leave a deliberate inference target unverified.

## 10. Spaced lexical lifecycle

Default planned exposures for important new items:

- R0: introduction passage, 1–2 textual encounters;
- R1: +1–2 passages;
- R2: +4–6 passages;
- R3: +10–14 passages;
- R4: +25–35 passages;
- R5: next-level bridge or later cumulative checkpoint.

Each important target should normally receive **at least six meaningful contacts** across text and retrieval tasks before being considered stable curriculum knowledge.

Intervals are heuristics. If future reader telemetry shows failure, schedule sooner; repeated easy success can lengthen intervals.

## 11. Context-diversity progression

### A1–A2
Use narrow reading first. Reuse related settings, characters, objects, and discourse frames so new lexical items are encountered with manageable cognitive load.

### B1
Begin moving due vocabulary across related but non-identical topics and genres.

### B2
Regularly vary topic, genre, speaker perspective, and semantic environment.

### C1–C2
Use broad contextual diversity: academic, public, professional, literary, technical, journalistic, argumentative, and culturally varied contexts.

Do not mistake random topic switching for good interleaving. Variation should be scheduled after initial understanding.

## 12. Grammar spiral

Each passage may have 0–2 **new** grammar targets but should reuse several previously encountered structures.

- A1: mostly supported patterns, explicit word order, highly recoverable references;
- A2: add common subordinate structures and mix established forms;
- B1: grammar review becomes embedded rather than announced;
- B2: systematically contrast structures with similar functions;
- C1/C2: reinforce grammar through discourse, register, rhythm, and meaning rather than worksheet-like labeling.

A grammar target must not make the passage unnatural merely to increase occurrences.

## 13. Interleaving rules

Interleave across:

- old/new vocabulary;
- grammar;
- topic;
- genre;
- question type;
- register;
- literal/inferential comprehension;
- recognition/production.

Do not introduce several highly confusable new forms simultaneously at very low proficiency unless explicit contrast is the pedagogical target.

## 14. Passage unit pattern

Default level structure: **10 units × 6 passages = 60 passages per CEFR level**.

Within each unit:

1. P1 — contextual introduction;
2. P2 — reinforcement + small new load;
3. P3 — interleaved contrast / near transfer;
4. P4 — new setting or genre;
5. P5 — cumulative integration;
6. P6 — fluency/checkpoint.

Across six CEFR levels:

- 360 passages per language;
- 1,080 passages total across Arabic, French, Urdu.

This target may be recalibrated after learner data.

## 15. Question contract

Questions appear **after the passage**. Answers appear only after **all** questions.

Do not reveal answers inline.

Each question has:

- `id`
- `type`
- `prompt`
- `target_ids`
- `answer_id`
- optional `options` for multiple choice;
- optional `skill`;
- optional `difficulty`.

Each answer has:

- `id`
- `question_id`
- `answer`
- `explanation`
- optional `evidence_span`;
- optional `acceptable_variants`.

### Question taxonomy

- `gist`
- `literal_detail`
- `sequence`
- `cause_effect`
- `reference_resolution`
- `vocabulary_in_context`
- `cloze_transfer`
- `grammar_in_context`
- `paraphrase`
- `inference`
- `motive`
- `main_claim`
- `argument_relation`
- `stance`
- `tone`
- `rhetorical_function`
- `assumption`
- `ambiguity_resolution`
- `summary`
- `synthesis`
- `cross_text_synthesis`
- `register_style`

## 16. Question progression

### A1 — usually 4–5
At least: gist, literal/sequence, vocabulary inference when a new word exists, transfer cloze.

### A2 — usually 5–6
Add cause/effect, reference resolution, simple paraphrase.

### B1 — usually 5–7
Add multi-sentence inference, motive/reason, summary, grammar-in-context.

### B2 — usually 6–8
Add stance, paragraph relation, cohesion, abstract vocabulary nuance.

### C1 — usually 7–9
Add implicit meaning, rhetorical purpose, assumptions, evidence evaluation, synthesis.

### C2 — usually 8–10
Add fine semantic distinctions, competing interpretations, tone/irony when appropriate, argument reconstruction, ambiguity, register/style, and cross-text synthesis.

## 17. Cloze rules

Cloze is a **retrieval/transfer task**, not simply deleting a word from the passage and asking the learner to remember its location.

Preferred cloze:

- uses the target in a new sentence or scenario;
- supplies enough semantic/grammatical constraint for one clearly best answer;
- may contrast confusable forms at B1+;
- may test collocation or discourse connector at B2+;
- must have a verified answer and acceptable variants.

Do not create ambiguous cloze items solely because multiple answers are grammatical.

## 18. Reading-speed contract

`speed_training` object:

- `timed`: boolean;
- `benchmark_eligible`: boolean;
- `comprehension_gate`: default 0.80;
- `new_word_policy`: `none`, `minimal`, or `controlled`;
- `notes`.

For a `fluency` passage:

- no dictionary use during the first timed read;
- new vocabulary should be zero or minimal;
- comprehension questions are answered after timing;
- if comprehension <80%, the reading time is retained diagnostically but does not count as a speed-progression success.

Do not train speed by suppressing normal comprehension behaviors.

## 19. Complexity profile

Store or compute these diagnostics where tooling allows:

- tokens / words;
- sentences;
- known-token coverage;
- new lexical types;
- target recurrence counts;
- sentence-length distribution;
- clauses per sentence;
- subordination / coordination counts;
- connective diversity;
- reference-chain distance;
- lexical diversity;
- multiword-expression count;
- morphology indicators;
- discourse/inference demand.

Never assign level from a single readability formula.

## 20. Content domains and genres

Over every level, balance CEFR-style domains:

- personal;
- public;
- educational;
- professional.

By C2, the learner should encounter original generated examples of:

- narrative;
- biography;
- practical information;
- news/reporting;
- explanation;
- popular science;
- history/culture;
- argument/counterargument;
- professional reports/memos;
- academic-style exposition;
- criticism/reviews;
- literary-style prose;
- paired conflicting viewpoints.

All passages must be original. Facts in informational passages must be checked and source-noted internally when material accuracy matters.

## 21. Language-specific production rules

### Arabic

- default variety: Modern Standard Arabic;
- label any non-MSA item explicitly;
- A1/A2 may use supportive tashkeel;
- gradually reduce nonessential tashkeel;
- do not count Arabic orthographic tokens as equivalent difficulty units to French words;
- include verified phrase-bank chunks where level-appropriate;
- Quranic/Classical material stays separately tagged if introduced later.

### French

- contemporary standard French;
- natural contraction/elision/pronouns;
- no translated-English syntax;
- modern learner senses first;
- archaic/literary usages only when intentionally teaching that register.

### Urdu

- contemporary standard Urdu;
- Unicode Urdu script, no Roman Urdu in canonical passage text;
- interpret speed cautiously at early levels because decoding load is affected by Urdu orthography;
- reject Hindi-only/archaic/dictionary-noise meanings unless explicitly labeled;
- gradually expand formal and literary Perso-Arabic vocabulary at C1/C2.

## 22. Lexical sourcing beyond the 3,000-word base

Before a beyond-base word becomes a deliberate C1/C2 target:

1. confirm it is a legitimate contemporary lexical item;
2. verify the intended sense with at least two reliable lexical/corpus signals where practical;
3. record lemma, form, part of speech, register, and source evidence in the language lexical ledger;
4. create its first contextual-introduction passage;
5. schedule R1–R5.

Do not repeat the earlier mistake of accepting an obscure dictionary sense merely because it exists.

## 23. Quality gates for every passage

A passage cannot be marked `approved` unless all applicable checks pass:

### Language
- natural grammar;
- correct spelling/orthography;
- target-language script clean;
- no accidental machine artifacts;
- appropriate modern register;
- no unintended dialect/archaic contamination.

### Pedagogy
- level-appropriate load;
- target coverage band;
- every new target has useful context;
- no excessive new targets;
- due review items are actually recycled;
- questions span more than literal copying;
- answer key is correct;
- cloze has a uniquely defensible answer or explicit accepted variants.

### Comprehension
- question answer is supported by text or clearly labeled transfer reasoning;
- no hidden external knowledge required at A1–B1;
- advanced external/world knowledge demands are labeled;
- inference difficulty is intentional.

### Content
- passage is original;
- factual claims are checked where needed;
- names/scenarios do not inadvertently encode stereotypes;
- topic mix is broad over the curriculum.

### Data
- valid JSON;
- unique immutable ID;
- word/sentence counts updated;
- target IDs exist in ledgers;
- exposure schedule updated;
- status recorded.

## 24. Passage status lifecycle

- `draft`
- `linguistic_review`
- `pedagogical_review`
- `calibrated`
- `approved`
- `retired`

Only `approved` passages are considered publication-ready.

## 25. Calibration before scale

Do not mass-generate the 1,080-passage target immediately.

Required order:

1. create A1 Unit 1 (6 passages) for Arabic;
2. create parallel A1 calibration units for French and Urdu;
3. inspect lexical coverage, inferability, question quality, and length;
4. refine standard if needed;
5. create one A2 calibration unit/language;
6. create one B1 calibration unit/language;
7. only then begin large batches;
8. calibrate B2/C1/C2 before scaling those levels.

## 26. Human handoff

Before any chat/session ends or becomes too large, update:

- `reading/STATUS.json`
- `reading/ROADMAP.md` if plan changed;
- `reading/AGENT_HANDOFF.md` with current state, decisions, blockers, exact next action.

A new agent must be able to continue by reading those files plus this standard, without relying on conversation memory.
