# Research Basis — Graded Reading Passages A1 to C2

This document records the evidence and design reasoning behind the Arabic, French, and Urdu reading-passages project. It is intentionally separate from the production standard so future agents can distinguish **research findings** from **project heuristics**.

Primary source registry: `sources/reading-acquisition.json`.

## 1. What the curriculum is trying to optimize

The passages are not simply CEFR-themed texts. They must jointly improve:

1. comprehension;
2. reading fluency / speed without sacrificing comprehension;
3. vocabulary growth through contextual inference and later verification;
4. automatic retrieval of previously learned vocabulary and grammar;
5. sensitivity to morphology, collocation, cohesion, register, and discourse;
6. increasingly deep inference, argument reconstruction, and implicit-meaning processing;
7. transfer across topics and genres;
8. durable retention through spacing, retrieval, and interleaving.

The design therefore needs both **easy/high-coverage reading** and **controlled challenge**. A passage that contains many impressive unknown words may look advanced but can be poor instruction if lexical decoding consumes the learner's attention.

## 2. CEFR progression is functional, not a word-count formula

The Council of Europe describes a progression from familiar concrete language at A1/A2, through connected familiar text at B1 and complex concrete/abstract text at B2, to demanding longer texts with implicit meaning at C1 and near-unrestricted comprehension and argument reconstruction at C2.

Important implication: CEFR level cannot be assigned from sentence length or vocabulary rank alone. Passage difficulty is produced by the interaction of:

- lexical familiarity;
- morphology;
- syntax and clause embedding;
- cohesion and reference chains;
- discourse organization;
- genre conventions;
- topic/background knowledge;
- inferential distance;
- figurative/idiomatic language;
- register;
- question/task demands.

For this project, CEFR labels are curriculum targets, not claims of official Council of Europe certification.

## 3. Lexical coverage

Hu & Nation (2000), Schmitt, Jiang & Grabe (2011), later replications, and subsequent work show a strong relationship between the percentage of known running words and comprehension. The literature frequently discusses approximately 95% as a lower/minimal region and approximately 98% as a much safer target for unassisted/detailed reading, while later work cautions that the relationship is continuous rather than a single magical threshold.

### Project interpretation

Use coverage as a **load-control tool**, not an exam score:

- **fluency passages:** aim for about 98.5–99.5% known running-token coverage;
- **ordinary instructional passages:** aim for about 97–98.5%, with unknown items deliberately made inferable;
- **stretch passages:** about 95–97.5%, used periodically and not as the main speed benchmark;
- below about 95% should normally be diagnostic or deliberately supported, not routine independent reading.

These bands are project heuristics informed by the research, not universal laws.

Coverage must be calculated against the learner-path ledger: validated base vocabulary + vocabulary already introduced and successfully recycled in earlier passages. A word that appeared once three months earlier should not automatically be treated as fully known.

## 4. The existing 3,000-word decks are a foundation, not C2

The verified Arabic, French, and Urdu 3,000-word inventories are an unusually useful lexical spine for the early and intermediate curriculum, but **3,000 lexical items cannot be treated as a complete C2 lexicon**.

Use the existing decks as controlled known-vocabulary inventories:

- A1: draw mainly from the highest-frequency core;
- A2: broaden through the top-1,000 inventory;
- B1: expand through roughly the first 1,500–2,000 high-frequency items;
- B2: increasingly exploit the full validated 3,000-item base;
- C1/C2: continue recycling those items but deliberately introduce and verify vocabulary beyond the current 3,000, including academic, professional, literary, abstract, idiomatic, and register-sensitive vocabulary.

Rank is not synonymous with CEFR level; the bands above are load-management defaults, not a declaration that rank 501 is inherently A2, etc.

## 5. Learning new words from context: infer, then verify

Research on contextual word learning shows that readers can learn vocabulary while reading, but semantic knowledge develops gradually and can remain incomplete after several encounters. Elgort, Beliaeva & Boers found benefits when readers first attempted a contextual inference and then received the correct meaning.

### Project implementation

A newly introduced word should normally be placed in a **high-constraint natural context**. The sentence or surrounding sentences should allow a strong hypothesis without writing a dictionary definition into the passage.

Preferred clue structures include:

1. **contrast / antonym:** the new word is contrasted with an already known state;
2. **cause → consequence:** observable effects make the property/action inferable;
3. **behavior → interpretation:** what a person/object does reveals the meaning;
4. **example / instance:** concrete members reveal an abstract category;
5. **restatement / paraphrase:** the idea is expressed again naturally in known words;
6. **parallel structure:** a familiar relation constrains the new item;
7. **part-whole / category relation:** known surrounding concepts narrow the semantic field;
8. **scenario resolution:** events before and after the word make only a small set of meanings plausible.

Avoid artificial textbook sentences whose only purpose is to encode an English gloss.

Bad pattern:
> The task was complex, which means difficult.

Better pattern:
> At first the repair looked simple. Then they discovered three broken wires, a leaking pipe, and a damaged motor; the job had become complex.

The reader infers the meaning from the accumulation of interacting problems. The answer key then verifies the intended sense.

### Error protection

Because incorrect inferences can occur:

- every deliberate inference target must eventually be verified in the answer key;
- ambiguous clueing is a quality failure at A1–B1;
- at B2+ controlled ambiguity may be used only when resolving ambiguity is itself the target skill;
- do not require the learner to consult a dictionary before making the first inference unless the passage is explicitly a reference-reading task.

## 6. Repetition is necessary, but identical repetition is not enough

Waring & Takaki and later contextual-learning studies show that incidental learning from a single encounter is weak. A recent contextual-diversity study used six encounters per target word and found that variation across genres/topics can improve delayed recognition for learners with stronger prior vocabulary, while lower-vocabulary learners can benefit more from thematically coherent/narrow reading first.

### Project implementation

Each deliberate new lexical target should receive a minimum planned lifecycle of approximately six meaningful contacts:

- **R0 — introduction:** 1–2 natural encounters in the introducing passage;
- **R1 — near retrieval:** 1–2 passages later;
- **R2 — short spacing:** roughly 4–6 passages later;
- **R3 — medium spacing:** roughly 10–14 passages later;
- **R4 — long spacing:** roughly 25–35 passages later;
- **R5 — bridge:** at the next CEFR stage or later cumulative checkpoint.

Not every contact must be the word printed in running text. Some should be retrieval:

- meaning-from-context question;
- cloze in a new sentence;
- synonym/contrast choice;
- reference to a previous event;
- paraphrase;
- production or summary prompt.

For A1/A2, early re-encounters should often remain within related topics and similar discourse frames. Context diversity should increase gradually at B1/B2 and become broad at C1/C2.

## 7. Spacing and retrieval

The repository already uses `docs/SPACED_REINFORCEMENT_STANDARD.md`. L2 vocabulary experiments also show benefits from retrieval opportunities and distributed practice, including fill-in-the-blank practice.

### Project implementation

Questions must do more than test whether the passage was read. They are retrieval events.

A typical passage should include a mixture of:

- gist recall;
- literal detail recall;
- sequence / cause-effect reconstruction;
- reference resolution;
- inference;
- vocabulary-in-context inference;
- cloze in a **new** sentence;
- paraphrase;
- short summary / synthesis;
- at advanced levels, stance, tone, rhetorical function, assumption, ambiguity, and cross-text synthesis.

Answers must appear after the full question set so the learner has a genuine retrieval interval.

## 8. Interleaving

Nakata & Suzuki found delayed benefits from interleaving L2 grammar practice, though difficulty during training increased and the broader literature shows that interleaving effects depend on task and prior knowledge.

### Project implementation

Do not make every passage a clean block of one tense or structure forever.

Use **supported introduction → increasing interleaving**:

- A1: introduce one main new pattern while maintaining familiar old patterns;
- A2: mix two or more already learned patterns inside the same narrative or task;
- B1+: old grammar should normally reappear without being announced as review;
- B2+: contrast confusable structures/register choices in meaningful contexts;
- C1/C2: grammar is primarily reinforced through authentic discourse demands rather than isolated labeling.

The same principle applies to vocabulary, topics, genres, and question types.

## 9. Reading speed / fluency

Beglar, Hunt & Kite found that substantial simplified pleasure reading improved L2 reading rate without corresponding loss of comprehension. A 2022 timed/repeated-reading study used passages of about 350 words followed by five comprehension questions and found fluency-building benefits over a semester.

There is **no single research-backed optimal passage length for every CEFR level and language**. Length must be long enough to produce stable timed-reading data but short enough that beginning learners can sustain comprehension.

### Project passage-length bands

These are initial calibration bands, to be revised from actual reader data:

| CEFR | Standard passage | Periodic extended passage | Main purpose |
|---|---:|---:|---|
| A1 | 90–140 words | 160–220 | decoding → short connected meaning |
| A2 | 140–220 | 250–350 | connected everyday text |
| B1 | 220–350 | 400–550 | sustained familiar narrative/exposition |
| B2 | 350–550 | 600–900 | complex concrete + abstract argument |
| C1 | 500–800 | 900–1,400 | demanding longer text, implicit meaning |
| C2 | 700–1,200 | 1,300–2,200 | dense authentic-style discourse and synthesis |

Do not enforce these as hard limits. A short legal notice can be C1; a long simple story can be A2. The bands are for curriculum pacing and speed measurement.

### Speed passages

A designated `fluency` passage should:

- use a very high known-token coverage;
- contain few or no brand-new lexical targets;
- use grammar already encountered;
- be read once without pausing for definitions;
- be followed by comprehension questions;
- count toward speed progression only when comprehension clears the project gate.

Initial project gate: **80% comprehension**. This is an operational heuristic, not a scientific threshold. If comprehension falls below the gate, the result is treated as difficulty data rather than evidence that the learner should read faster.

## 10. Complexity must be multidimensional

Arabic L2 readability work and broader L2 readability research show that lexical, morphological, syntactic, semantic, and cohesion variables matter. Sentence length alone is inadequate.

Track at minimum:

- word count;
- known-token coverage;
- number of new lexical types;
- mean / median sentence length (diagnostic only);
- clause count and subordination;
- morphology load;
- pronoun/reference distance;
- connective diversity;
- lexical diversity;
- idiom / multiword-expression load;
- discourse type;
- inference depth;
- topic familiarity;
- question difficulty.

### Approximate syntactic progression

- **A1:** mostly one-clause sentences; very short coordination; explicit referents.
- **A2:** one–two clauses; common coordination/subordination; simple pronoun chains.
- **B1:** varied simple/compound/complex sentences; reasons, conditions, relative clauses, reported events.
- **B2:** routine multi-clause syntax; abstract noun phrases; denser reference and discourse connectors.
- **C1:** flexible sentence architecture; embedding, nominalization, rhetorical cohesion, implicit links.
- **C2:** natural unrestricted syntax, including deliberate complexity, ellipsis, stylistic variation, and long-distance dependencies where genre-appropriate.

## 11. Language-specific constraints

### Arabic

- Modern Standard Arabic is the default.
- Do not silently mix dialect into MSA passages.
- A1/A2 may use helpful tashkeel; gradually reduce nonessential diacritics as decoding improves.
- Because Arabic morphology can pack information into orthographic words, raw word count and average sentence length must not be compared mechanically with French.
- C1/C2 should include formal journalistic, academic, essayistic, professional, and literary-style MSA. Quranic/Classical Arabic remains a separately labeled branch unless explicitly integrated later.

### French

- Use contemporary standard French as the default.
- Preserve natural contractions, pronouns, agreement, and discourse markers rather than writing translated-English French.
- Avoid archaic senses unless a passage intentionally teaches historical/literary register.
- FLELex and French CEFR reference-level resources may be used as secondary lexical-complexity checks.

### Urdu

- Use contemporary standard Urdu in clean Unicode suitable for Nastaliq rendering.
- Do not replace Urdu script with Roman Urdu.
- Urdu's deep/cursive orthography and normal omission of many vowel diacritics can slow decoding independently of linguistic comprehension; early speed data must therefore be interpreted cautiously.
- Avoid Hindi-only, archaic, or dictionary-noise senses unless deliberately labeled.
- C1/C2 should broaden into formal Perso-Arabic vocabulary, professional prose, essays, journalism, and literary-style Urdu while preserving natural contemporary usage.

## 12. Question progression by level

Suggested default counts:

- A1: 4–5 questions;
- A2: 5–6;
- B1: 5–7;
- B2: 6–8;
- C1: 7–9;
- C2: 8–10.

The count matters less than skill coverage.

### A1
Gist, literal detail, sequence, one inferable-word item, one simple transfer cloze.

### A2
Add cause/effect, reference resolution, simple paraphrase.

### B1
Add multi-sentence inference, reasons/motives, summary, grammar-in-context.

### B2
Add author position, cohesion, contrast, argument relation, vocabulary nuance.

### C1
Add implicit meaning, rhetorical purpose, assumption, paragraph function, evidence evaluation, synthesis.

### C2
Add tone/irony where culturally appropriate, fine semantic distinctions, ambiguity, allusion, argument reconstruction, competing interpretations, cross-text synthesis, and register/style analysis.

## 13. Genre and domain progression

Use all major CEFR domains over time: personal, public, educational, and professional.

Early levels should reuse topics enough to create lexical security. Later levels should diversify aggressively.

Genres should eventually include:

- narrative;
- dialogue represented as prose where appropriate;
- description;
- practical instructions;
- messages/notices;
- biography;
- explanation;
- news-style report;
- compare/contrast;
- problem/solution;
- opinion essay;
- argument/counterargument;
- science/popular science;
- history/culture;
- professional memo/report;
- academic-style exposition;
- criticism/review;
- literary-style prose;
- paired texts with conflicting viewpoints.

All generated passages must be original. Do not paste copyrighted reading passages into the dataset.

## 14. Initial production scale

Target **60 passages per CEFR level per language**:

- 6 levels × 60 = 360 passages per language;
- 3 languages = 1,080 passages total.

Each level is organized as 10 units × 6 passages:

1. contextual introduction;
2. reinforcement + small amount of new material;
3. interleaved contrast/transfer;
4. new context;
5. cumulative integration;
6. timed fluency/checkpoint.

This is large enough to support multiple spaced encounters without making the curriculum endless. Counts can be changed if real reader performance indicates a better distribution.

## 15. Calibration requirement

Before producing hundreds of passages, generate a six-passage A1 calibration unit in **each language**, run all lexical/structural audits, and inspect it manually. Then create an A2 and B1 calibration unit before scaling production.

The project should be data-driven after launch: actual comprehension, reading time, difficult words, and question errors should be able to adjust future passage difficulty.

## 16. Research limitations

- Most controlled L2 reading research is in English and may not transfer perfectly to Arabic, French, or Urdu.
- CEFR is language-general; it does not provide a universal word-count or sentence-length formula.
- Frequency rank is not proficiency level.
- Lexical coverage is highly useful but not sufficient: background knowledge, morphology, genre, syntax, and inference demands matter.
- Repetition counts are probabilistic learning opportunities, not guarantees of acquisition.
- Reading speed is meaningful only together with comprehension.

For production rules, see `docs/READING_PASSAGE_STANDARD.md`.
