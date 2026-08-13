# Game Plan — Arabic, French, and Urdu Reading to C2

## Mission

Build a long-form reading curriculum that can plug into the user's existing reader and systematically improve:

- reading comprehension;
- reading speed/fluency;
- contextual vocabulary growth;
- grammar automaticity;
- inference;
- discourse comprehension;
- retention and transfer;
- advanced academic/professional/literary reading.

The curriculum should feel like **good reading**, not like flashcards disguised as paragraphs.

## Final target

Initial production target:

- 360 Arabic passages;
- 360 French passages;
- 360 Urdu passages;
- 1,080 total passages.

Each language: 60 passages per CEFR level A1–C2.

Each level: 10 units × 6 passages.

## Why this architecture

Six passages per unit gives enough room for a deliberate learning cycle:

1. **Introduce** — a small number of new forms in strongly inferable context.
2. **Reinforce** — reuse them soon while adding little new load.
3. **Interleave** — mix old/new/confusable material and require discrimination.
4. **Transfer** — move the language to a new scenario or genre.
5. **Integrate** — cumulative passage requiring several prior skills together.
6. **Fluency/checkpoint** — high lexical coverage, timed-reading friendly, questions after reading.

The same target vocabulary can then recur again at R2/R3/R4/R5 intervals across later units.

## Progression philosophy

### A1 — learn to extract connected meaning

Focus:

- concrete daily life;
- explicit actors and referents;
- highly frequent verbs/function words;
- basic time/place/cause relations;
- very short narratives and descriptions;
- context clues that are almost self-resolving;
- reading without translating every word.

Passages remain narrow in topic so vocabulary can recur safely.

### A2 — build continuity

Focus:

- routine problems and solutions;
- short stories and practical information;
- pronoun/reference chains;
- common subordinate clauses;
- more flexible tense/aspect use;
- simple motives and cause/effect;
- more cloze transfer.

### B1 — sustain a text and infer across sentences

Focus:

- connected narratives/explanations;
- experiences, decisions, plans, consequences;
- paragraph-level main ideas;
- multi-sentence inference;
- summaries;
- wider lexical/grammar interleaving;
- gradual topic diversification.

### B2 — handle complexity and argument

Focus:

- concrete and abstract topics;
- argument/counterargument;
- author stance;
- denser cohesion and reference;
- technical discussion with support;
- broader contextual diversity;
- paired viewpoints;
- full use of the validated 3,000-word base plus controlled additions.

### C1 — read demanding longer prose

Focus:

- implicit meaning;
- professional and academic prose;
- editorials and sophisticated exposition;
- rhetorical function;
- assumptions and evidence;
- dense nominal/abstract language;
- register;
- vocabulary beyond the existing 3,000-word lists, independently verified.

### C2 — reconstruct nuance and discourse

Focus:

- fine shades of meaning;
- competing interpretations;
- stylistic/rhetorical choices;
- ambiguity where intentional;
- irony/allusion when natural;
- literary-style prose;
- sophisticated academic/professional argument;
- cross-text synthesis;
- near-unrestricted syntax and vocabulary with continued support for genuinely rare items.

## Topic plan

Topic progression should spiral rather than reset at every level.

Example domains:

- self, family, relationships;
- home, food, shopping;
- time, weather, transport;
- school, work, skills;
- health and daily decisions;
- nature and environment;
- technology;
- society and institutions;
- science and engineering;
- psychology and behavior;
- finance/economics;
- history and culture;
- arts/music/literature;
- ethics and philosophy;
- public policy and civic life;
- academic/professional communication.

The same domain can return at a higher level with greater lexical, syntactic, inferential, and conceptual depth.

## New-word strategy

The reader should usually understand the **situation first**, then infer the word.

A new word is introduced only when the surrounding context can constrain its meaning naturally. Do not rely on isolated synonym definitions.

Typical pattern:

1. establish familiar scene;
2. create a contrast, consequence, example, or observable behavior;
3. place the new word where the learner can form a strong hypothesis;
4. continue the passage without interrupting flow;
5. ask a vocabulary-in-context question later;
6. verify in answer key;
7. reuse the word in a new cloze/sentence;
8. schedule later contextual encounters.

## Spacing plan

Default lexical schedule after introduction:

- R1: 1–2 passages later;
- R2: 4–6 later;
- R3: 10–14 later;
- R4: 25–35 later;
- R5: next-level bridge / later checkpoint.

Important words should reach roughly six meaningful contacts across text and retrieval.

At low levels, early contexts stay thematically related. At high levels, the same word should migrate across genres/topics.

## Interleaving plan

Do not interleave so aggressively that A1 becomes confusing.

Use:

- initial supported introduction;
- near practice;
- later mixed retrieval;
- increasingly unpredictable natural reuse.

By B1, older grammar/vocabulary should appear without being labeled as review. By C1/C2, most review is simply embedded in meaningful text.

## Fluency / reading-speed plan

Every six-passage unit ends with a fluency/checkpoint passage.

A fluency passage should have:

- very high known-token coverage;
- zero/minimal new vocabulary;
- familiar grammar;
- natural prose;
- comprehension questions after timing.

The reader's WPM result only counts as a speed success when comprehension is at least the project gate (initially 80%).

If comprehension drops, do not push speed upward. Treat it as a difficulty signal.

## Question design plan

Questions become progressively less extractive.

Early:

- main idea;
- who/what/where;
- order of events;
- obvious cause/effect;
- infer a new word;
- cloze transfer.

Middle:

- motives;
- references;
- multi-sentence inferences;
- summary;
- compare/contrast;
- author position;
- cohesion.

Advanced:

- unstated assumptions;
- rhetorical purpose;
- evidence quality;
- ambiguity;
- tone;
- register;
- argument reconstruction;
- competing interpretations;
- synthesis across passages.

## Language-specific tracks

### Arabic

MSA is the default. Early passages may use helpful tashkeel and later remove nonessential diacritics. The validated phrase bank should seed useful chunks. Dialect and Quranic/Classical material remain separately labeled if introduced.

### French

Contemporary standard French, natural syntax, contractions, pronouns, collocations, and register. Avoid legacy/archaic dictionary senses unless deliberately teaching literary/historical usage.

### Urdu

Contemporary standard Urdu in canonical Urdu script. Early reading-speed interpretation must account for script/orthographic load. Avoid Roman Urdu and dictionary-noise senses. Formal/literary Perso-Arabic vocabulary expands gradually at C1/C2.

## Production strategy

### Stage 1 — infrastructure

Build normalized lexical ledgers and exposure tracking from the validated language CSVs.

### Stage 2 — 18-passage A1 calibration

Produce one complete six-passage A1 unit per language. Inspect every line and every question.

### Stage 3 — A2 and B1 calibration

Test whether the system scales as syntax and inference increase.

### Stage 4 — scale A1–B1

Generate in unit-sized batches, auditing after each unit.

### Stage 5 — B2

Calibrate arguments, abstract text, wider genres, and stronger interleaving.

### Stage 6 — advanced lexicon

Build independently verified beyond-3,000 inventories per language.

### Stage 7 — C1/C2

Calibrate first, then scale. Advanced passages should be genuinely sophisticated rather than just longer.

### Stage 8 — reader feedback loop

If reading-time and question telemetry is available, use it to recalibrate future difficulty and review intervals.

## Batch size

Default production batch after calibration: **one unit = six passages for one language**.

Reason:

- small enough for manual inspection;
- large enough to implement introduction/reinforcement/interleaving/fluency as a coherent cycle;
- makes exposure-ledger updates tractable;
- reduces the risk of propagating a bad style decision through hundreds of records.

Once audits are mature, two or three units can be produced in a batch, but quality gates remain unit-level.

## Definition of done for one passage

A passage is not done until:

- language is natural and correct;
- lexical load is measured;
- target words have valid contextual cues;
- questions are correct and varied;
- answers are separated and verified;
- cloze is unambiguous or has accepted variants;
- exposure ledger is updated;
- CEFR/difficulty profile is justified;
- JSON is valid;
- status is `approved`.

## Definition of done for one CEFR level

- 60 approved passages or documented revised target;
- all 10 unit checkpoints complete;
- no stranded introduced lexical targets;
- due R1–R5 reviews completed;
- domain/genre mix audited;
- no unresolved linguistic/pedagogical flags;
- cumulative speed/comprehension profile reviewed if telemetry exists.

## Definition of done for the full project

- Arabic A1–C2 approved;
- French A1–C2 approved;
- Urdu A1–C2 approved;
- 3 language exposure ledgers complete;
- advanced C1/C2 lexical additions source-verified;
- reader export validated;
- final integrity and publication-readiness audit passes;
- `STATUS.json` and `AGENT_HANDOFF.md` describe the final state.
