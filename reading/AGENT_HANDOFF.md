# Agent Handoff — Arabic, French, Urdu Graded Reading Curriculum

**Purpose:** preserve the full project contract across ChatGPT conversations, agent changes, and context-window limits.

If you are a new agent taking over this project, **do not reconstruct the plan from memory or redesign it from scratch**. Read the files below in order and continue from `reading/STATUS.json`.

## 1. Mandatory read order for a new agent

1. `reading/STATUS.json` — exact current state and immediate next action.
2. `reading/AGENT_HANDOFF.md` — this file; non-negotiables and continuity rules.
3. `reading/ROADMAP.md` — game plan from A1 through C2.
4. `reading/TASKS.md` — detailed checklist.
5. `docs/READING_PASSAGE_RESEARCH.md` — research findings and why the design looks this way.
6. `docs/READING_PASSAGE_STANDARD.md` — mandatory passage/data/quality contract.
7. `docs/SPACED_REINFORCEMENT_STANDARD.md` — existing repository spacing/interleaving framework.
8. `sources/reading-acquisition.json` — research/source registry.
9. The validated root language CSVs when doing lexical work.
10. `audit/public_readiness_audit.json` and `audit/live_csv_attestation.json` if verifying the provenance/status of the root language datasets.

Do not begin mass passage generation before completing this read order.

---

## 2. User's non-negotiable request

The user wants a set of **raw reading-passage files for Arabic, French, and Urdu that lead progressively from A1 to C2** and can be plugged into an existing reader.

The existing reader will also train reading speed over time. We only need to build the high-quality source data and later an import/export adapter if the reader requires a different shape.

Every passage must ultimately support:

- meaningful reading comprehension;
- questions after the passage;
- answers **after all questions**, never mixed inline with the passage/questions in reader-facing rendering;
- contextual introduction of new vocabulary;
- cloze retrieval/transfer;
- interleaved practice;
- spaced repetition / recycling;
- retrieval practice;
- cumulative comprehension;
- increasingly sophisticated inference and discourse processing;
- reading-speed development without sacrificing comprehension.

The user explicitly wants **publication-quality language**: passages should be safe to show teachers, fluent speakers, or other learners without obvious linguistic mistakes or awkward machine-generated prose.

Accuracy and naturalness take priority over reaching an arbitrary passage count.

---

## 3. Key pedagogical idea: do not define new words clumsily

The user specifically asked for new words to be made **intuitively inferable from the surrounding language**, not merely translated or defined in a sentence.

Example principle for a hypothetical target equivalent to “complex”:

Avoid:

> The task was complex, which means difficult.

Prefer a scenario that constrains the meaning:

> At first the repair looked simple. Then they discovered three broken wires, a leaking pipe, and a damaged motor; the job had become complex.

The meaning emerges from the interacting complications.

Preferred contextual clue strategies are:

- contrast / antonym;
- cause → consequence;
- behavior → interpretation;
- concrete examples → abstract category;
- natural restatement/paraphrase;
- parallel structure;
- part/whole or category relation;
- scenario resolution;
- morphology when genuinely helpful.

At A1–B1, deliberate lexical targets should be sufficiently constrained that the intended sense is the overwhelmingly reasonable inference. At B2+ controlled ambiguity is acceptable only when resolving it is itself the learning target.

Then use an **infer → verify → transfer** sequence:

1. encounter target in rich context;
2. learner infers meaning/function;
3. later vocabulary-in-context question asks for the inference;
4. answer key verifies the intended sense;
5. a cloze or later passage requires the item in a new context;
6. subsequent R1–R5 exposures continue retrieval.

Never leave a deliberate inference target unverified.

---

## 4. Research-backed design decisions already made

Do not casually change these. If new evidence justifies a change, update the research, standard, roadmap, status, and this handoff together.

### 4.1 Lexical coverage

Coverage is a load-control heuristic, not a magical proficiency threshold.

Initial project bands:

- **fluency passages:** ~98.5–99.5% known running tokens;
- **ordinary instructional passages:** ~97–98.5%;
- **stretch passages:** ~95–97.5%;
- routine passages below ~95% should normally be diagnostic or specially supported.

Known-token coverage must be calculated from the actual curriculum ledger, not from the assumption that every word in a frequency list has been mastered.

### 4.2 Passage length calibration bands

These are project calibration bands, not official CEFR definitions:

| CEFR | Standard passage | Periodic extended passage |
|---|---:|---:|
| A1 | 90–140 words | 160–220 |
| A2 | 140–220 | 250–350 |
| B1 | 220–350 | 400–550 |
| B2 | 350–550 | 600–900 |
| C1 | 500–800 | 900–1,400 |
| C2 | 700–1,200 | 1,300–2,200 |

Difficulty is multidimensional. Do not assign CEFR from word count/sentence length alone.

### 4.3 Planned new lexical targets per standard passage

Initial planning bands:

- A1: 1–3;
- A2: 2–4;
- B1: 3–6;
- B2: 4–8;
- C1: 6–10;
- C2: 8–14.

These are upper planning ranges, not quotas. Use fewer when grammar/discourse load is already high.

### 4.4 Spacing / lexical lifecycle

For important introduced vocabulary, schedule approximately:

- R0: introduction, generally 1–2 natural encounters in the passage;
- R1: +1–2 passages;
- R2: +4–6 passages;
- R3: +10–14 passages;
- R4: +25–35 passages;
- R5: next CEFR bridge or later cumulative checkpoint.

Aim for **at least ~6 meaningful contacts** for important targets across running text and retrieval tasks.

A “contact” can be:

- contextual occurrence;
- vocabulary-in-context inference;
- new-sentence cloze;
- paraphrase;
- synonym/contrast discrimination;
- summary/production;
- later authentic-style encounter.

Do not count six identical repetitions in one paragraph as six useful learning contacts.

### 4.5 Context diversity

- A1/A2: use **narrow reading** first — related topics/settings/frames reduce cognitive load.
- B1: begin moving due vocabulary across related but different settings/genres.
- B2: regularly vary topic, genre, perspective, and semantic environment.
- C1/C2: broad contextual diversity across academic, professional, journalistic, literary, technical, public, and cultural contexts.

Do not randomize everything from the start. Context diversity becomes more useful as lexical knowledge grows.

### 4.6 Interleaving

Use **supported introduction → later interleaving**.

At A1, one main new pattern can be introduced while older material remains familiar. By B1, older grammar/vocabulary should reappear naturally without a “review” label. At C1/C2, most reinforcement is embedded in real discourse.

### 4.7 Reading speed

The reader trains speed, but **speed never outranks comprehension**.

Every six-passage unit normally ends with a high-coverage fluency/checkpoint passage.

Initial project rule:

- benchmark fluency passages are timed;
- no dictionary during first timed read;
- zero/minimal new vocabulary;
- comprehension questions follow timing;
- a result counts as a speed-progression success only if comprehension is at least **80%**.

The 80% threshold is a project heuristic, not a scientific universal. If comprehension is lower, keep the time as diagnostic data but do not reward faster reading.

---

## 5. Scale and curriculum architecture

Initial target:

- **360 Arabic passages**;
- **360 French passages**;
- **360 Urdu passages**;
- **1,080 total**.

Each language:

- A1: 60
- A2: 60
- B1: 60
- B2: 60
- C1: 60
- C2: 60

Each CEFR level uses **10 units × 6 passages**.

Default six-passage unit cycle:

1. P1 — contextual introduction;
2. P2 — reinforcement + small amount of new material;
3. P3 — interleaved contrast / near transfer;
4. P4 — new setting or genre;
5. P5 — cumulative integration;
6. P6 — timed fluency/checkpoint.

Do **not** mass-generate all 1,080 now. The specification explicitly requires staged calibration.

---

## 6. Calibration order

Mandatory before scaling:

1. build normalized lexical/curriculum ledgers;
2. create Arabic A1 Unit 01 (6 passages);
3. create French A1 Unit 01 (6 passages);
4. create Urdu A1 Unit 01 (6 passages);
5. manually and automatically audit all 18;
6. refine the standard if needed;
7. create one A2 calibration unit per language;
8. create one B1 calibration unit per language;
9. only then scale A1–B1;
10. separately calibrate B2, C1, and C2 before scaling each.

Default later batch size is **one unit = six passages for one language**. Larger batches are allowed only when quality tooling is mature, and unit-level audit remains mandatory.

---

## 7. Existing validated language data: how to use it

Canonical root datasets:

### Arabic

- `arabic_top1000.csv`
- `arabic_top3000.csv` — ranks 1001–3000, 2,000 rows
- `arabic_phrase_bank.csv`

### French

- `french_top1000.csv`
- `french_top3000.csv` — ranks 1001–3000

### Urdu

- `urdu_top1000.csv`
- `urdu_top3000.csv` — ranks 1001–3000

These datasets were separately publication-audited before this reading project. **Do not mutate them merely to make passage generation easier.** Build derived normalized reading ledgers instead.

The combined top-1,000 + continuation supplies a validated **3,000-item lexical base per language**.

Critical rule: **3,000 words is not C2.**

Use the existing inventories as a controlled foundation:

- A1: mainly highest-frequency core;
- A2: broaden through the top-1,000;
- B1: roughly the first 1,500–2,000 as a planning resource;
- B2: increasingly exploit the full validated 3,000;
- C1/C2: continue recycling the core while deliberately adding verified contemporary vocabulary beyond the current 3,000.

Frequency rank is **not** a CEFR label.

Before an advanced beyond-base lexical item becomes a learner target:

1. verify it is legitimate contemporary usage;
2. verify the intended sense with reliable lexical/corpus evidence, ideally at least two signals when practical;
3. record lemma/form/POS/register/sense/provenance in the language lexical ledger;
4. introduce it contextually;
5. schedule R1–R5.

Do not accept obscure dictionary senses merely because a dictionary contains them.

---

## 8. Language-specific rules

### Arabic

- Default: **Modern Standard Arabic (MSA)**.
- Do not silently mix dialect into MSA passages.
- A1/A2 may use helpful tashkeel to support pronunciation/decoding.
- Gradually reduce nonessential tashkeel as proficiency rises.
- Arabic morphology makes raw “word count” non-equivalent to French word count; judge difficulty multidimensionally.
- Use verified Arabic phrase-bank chunks where appropriate.
- Quranic/Classical Arabic remains a separately tagged branch if integrated later; do not blur it into ordinary MSA.
- C1/C2 should include formal journalistic, academic, professional, essayistic, and literary-style MSA.

### French

- Contemporary standard French by default.
- Use natural contraction, elision, pronouns, agreement, collocation, and discourse markers.
- Do not write English sentence structures with French words substituted into them.
- Avoid archaic/legacy senses unless a passage deliberately teaches a historical/literary register.
- C1/C2 must include natural abstract, academic, professional, journalistic, and literary-style prose.

### Urdu

- Contemporary standard Urdu in clean Unicode suitable for Nastaliq rendering.
- **No Roman Urdu** in canonical passage text.
- Normal Urdu orthography/diacritic omission can affect early decoding speed independently of linguistic comprehension; interpret speed conservatively at early levels.
- Reject Hindi-only, archaic, or dictionary-noise meanings unless deliberately labeled and pedagogically relevant.
- Expand formal Perso-Arabic vocabulary progressively at advanced levels without making ordinary prose unnaturally ornate.
- C1/C2 should include professional prose, essays, journalism, academic-style exposition, and literary-style Urdu.

---

## 9. Canonical data format

Source of truth: **JSONL**, one passage object per line.

Path:

`reading/<language>/<level>/passages.jsonl`

Examples:

- `reading/arabic/a1/passages.jsonl`
- `reading/french/b2/passages.jsonl`
- `reading/urdu/c2/passages.jsonl`

App-specific JSON/CSV/plain-text exports may be generated later. Do not abandon the canonical JSONL merely because the reader imports a simpler format.

Immutable ID format:

`<lang>-<level>-u<unit>-p<passage>`

Examples:

- `ar-a1-u01-p01`
- `fr-b2-u04-p03`
- `ur-c1-u10-p06`

Schema: `reading/schema/passage.schema.json`.

---

## 10. Reader-facing order

The user wants questions and answers at the end.

Normal rendering order:

1. title;
2. passage text;
3. all questions;
4. answer key after all questions / after reveal or submission.

Do not expose answers inline with questions in the learner UI even though the canonical data object stores the answer key.

---

## 11. Questions are part of learning, not just assessment

Question types should become increasingly inferential over time.

A1 typically includes:

- gist;
- literal detail;
- sequence;
- vocabulary-in-context if a word was introduced;
- a new-context transfer cloze.

A2 adds:

- cause/effect;
- reference resolution;
- simple paraphrase.

B1 adds:

- multi-sentence inference;
- motives/reasons;
- summary;
- grammar in context.

B2 adds:

- stance;
- cohesion;
- argument relationships;
- abstract vocabulary nuance.

C1 adds:

- implicit meaning;
- rhetorical purpose;
- assumptions;
- evidence evaluation;
- synthesis.

C2 adds:

- fine semantic distinction;
- controlled ambiguity;
- tone/irony when culturally natural;
- argument reconstruction;
- competing interpretations;
- register/style;
- cross-text synthesis.

Answers must explain *why* when useful, not just give letters such as “B.”

---

## 12. Cloze rule

Cloze must normally test **transfer**, not location memory.

Bad:

- copy a sentence from the passage and blank the exact target.

Preferred:

- place the target in a new natural sentence or scenario;
- provide strong semantic/grammatical constraint;
- have one clearly best answer or explicitly listed acceptable variants.

At B1+, cloze may distinguish confusable forms, collocations, or discourse connectors.

---

## 13. Complexity progression

Do not use sentence length as the sole measure.

Track/consider:

- lexical coverage;
- number of new types;
- morphology;
- sentence/clause structure;
- subordination;
- reference-chain distance;
- cohesion/connective diversity;
- idiom/multiword expressions;
- topic familiarity;
- discourse organization;
- inference depth;
- register;
- question/task difficulty.

Approximate syntactic progression:

- A1: mostly one clause, short coordination, explicit referents;
- A2: one–two clauses, common subordination, simple pronoun chains;
- B1: varied simple/compound/complex sentences, reasons/conditions/relatives/reported events;
- B2: routine multi-clause syntax, abstract noun phrases, denser reference/cohesion;
- C1: flexible embedding, nominalization, rhetorical cohesion, implicit links;
- C2: natural unrestricted syntax, including stylistic complexity and ellipsis when genre-appropriate.

---

## 14. Topic/genre progression

Cover personal, public, educational, and professional domains over time.

Eventually include:

- narrative;
- dialogue-like prose;
- description;
- practical instructions/notices;
- biography;
- explanation;
- news-style report;
- compare/contrast;
- problem/solution;
- opinion/argument/counterargument;
- science/popular science;
- history/culture;
- professional memo/report;
- academic-style exposition;
- criticism/review;
- literary-style prose;
- paired texts with conflicting viewpoints.

All generated passages must be **original**. Do not paste copyrighted texts into the dataset.

Fact-heavy informational passages must have internal source notes and factual verification when material accuracy matters.

---

## 15. Passage quality gate

A passage is not publication-ready until it passes all applicable checks.

### Linguistic

- grammar correct;
- spelling/orthography correct;
- natural phrasing;
- modern appropriate register;
- correct target sense;
- no accidental machine artifacts;
- no unintended dialect/archaic contamination.

### Pedagogical

- level-appropriate load;
- coverage within intended band;
- deliberate new targets are inferable;
- no excessive unknown vocabulary;
- due review targets actually recur;
- grammar load controlled;
- questions test more than copying;
- cloze unambiguous or variants stated.

### Answer integrity

- every question has an answer;
- answer supported by text or clearly marked transfer reasoning;
- no hidden outside knowledge required at A1–B1;
- deliberate lexical inference verified;
- evidence/explanation correct.

### Data

- valid JSON;
- unique immutable ID;
- target IDs resolve to ledgers;
- word/sentence counts current;
- exposure schedule updated;
- quality status recorded.

Only `approved` passages are public-ready.

Status lifecycle:

`draft` → `linguistic_review` → `pedagogical_review` → `calibrated` → `approved` → `retired`.

---

## 16. Things a future agent MUST NOT do

- **Do not mass-generate hundreds of passages before calibration.**
- Do not call 3,000 words “C2 vocabulary.”
- Do not mutate the already validated root CSVs to fit passage generation.
- Do not introduce rare/archaic senses just because they exist in WordNet/dictionaries.
- Do not hide weak comprehension behind a higher WPM number.
- Do not count speed success below the comprehension gate.
- Do not make passage difficulty simply “more words + longer sentences.”
- Do not copy published/copyrighted reading passages.
- Do not write artificial sentences that openly encode dictionary definitions when a natural contextual clue can teach the word.
- Do not leave inferred target meanings unverified.
- Do not repeat a target six times in one paragraph and call spacing complete.
- Do not interleave so aggressively at A1 that the learner cannot form a stable initial representation.
- Do not silently mix Arabic dialects into MSA.
- Do not use Roman Urdu as canonical text.
- Do not write unnatural translated-English French.
- Do not reveal the answer immediately under each question in reader-facing exports.
- Do not rely on a single readability formula for CEFR assignment.
- Do not mark a passage `approved` merely because a schema validator passes.
- Do not assume a previous chat's memory is enough; the repo files are the source of truth.

---

## 17. Reader telemetry, when available

The user already has a reader that can train speed. If its export/import or telemetry format becomes available, preserve the canonical JSONL and add an adapter.

Useful telemetry fields:

- passage ID;
- reading duration;
- words per minute / characters per minute if appropriate;
- comprehension score;
- question-level errors;
- target-word inference errors;
- cloze errors;
- words learner marked difficult;
- re-read count.

Use telemetry to adapt later passages:

- failed retrieval → shorter next review interval;
- repeated easy success → longer interval;
- low comprehension → lower difficulty / increase support;
- high comprehension + easy reading → cautiously increase complexity;
- passage-specific widespread failure → investigate mis-leveling or bad writing rather than blaming the learner.

---

## 18. Exact current state at project initialization

As of **2026-08-13**:

Completed:

- deep research pass;
- source registry;
- research synthesis;
- mandatory production standard;
- project README;
- detailed task list;
- game plan / roadmap;
- handoff framework.

Not yet completed:

- normalized lexical exposure ledgers;
- grammar/discourse target inventories;
- topic/genre matrix;
- actual passage JSONL files;
- A1 calibration units;
- reader-specific export adapter.

**There are currently zero approved passages. Do not report otherwise.**

---

## 19. Immediate next action

Do this next, without redesigning the project:

1. parse each validated root top-1,000 + ranks 1001–3000 deck into a **derived normalized reading lexicon**;
2. create the three lexical exposure ledgers;
3. include Arabic phrase-bank chunks separately;
4. establish initial A1 lexical/grammar/discourse target pool;
5. build a topic/genre/domain matrix for Unit 01;
6. draft **Arabic A1 Unit 01, six passages**;
7. draft **French A1 Unit 01, six passages**;
8. draft **Urdu A1 Unit 01, six passages**;
9. audit all 18 before scaling.

The calibration set is more important than production speed.

---

## 20. Required end-of-session handoff procedure

Before a future chat/session ends, especially when context size is becoming large:

1. update `reading/STATUS.json` with exact counts, completed artifacts, blockers, last approved IDs, and immediate next action;
2. check off completed items in `reading/TASKS.md`;
3. update `reading/ROADMAP.md` if any design decision actually changed;
4. update **this file** if a new non-negotiable, exception, quality lesson, schema rule, or language-specific decision was discovered;
5. record any known failure patterns and their fixes;
6. never leave the next agent with only “continue” and no exact state.

A new chat should be able to resume correctly from these repository files alone.
