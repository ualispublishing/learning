# Reading Curriculum Task List

This checklist is the operational work queue for the Arabic, French, and Urdu A1–C2 reading project.

## Phase 0 — Research and specification

- [x] Review existing spaced-reinforcement standard.
- [x] Review existing Arabic flashcard standard and validated language CSV role.
- [x] Research lexical coverage and reading comprehension.
- [x] Research contextual vocabulary inference and verification.
- [x] Research repeated encounters / contextual diversity.
- [x] Research retrieval practice, cloze, spacing, and interleaving.
- [x] Research reading-rate / fluency training and passage-length evidence.
- [x] Research CEFR progression and reading task complexity.
- [x] Record Arabic/Urdu script/readability considerations.
- [x] Create `sources/reading-acquisition.json`.
- [x] Create `docs/READING_PASSAGE_RESEARCH.md`.
- [x] Create `docs/READING_PASSAGE_STANDARD.md`.
- [x] Create this task list, roadmap, status file, schema, and handoff.

## Phase 1 — Build lexical and curriculum ledgers

- [ ] Parse each language's validated top-1,000 + ranks 1001–3000 into a normalized reading lexicon.
- [ ] Keep original validated CSVs unchanged; build derived ledgers only.
- [ ] Arabic: add level-appropriate phrase-bank chunks as separate multiword targets.
- [ ] Add normalized lemma/form/POS/rank/meaning fields for reading selection.
- [ ] Create `reading/ledgers/arabic_lexical_exposure.jsonl`.
- [ ] Create `reading/ledgers/french_lexical_exposure.jsonl`.
- [ ] Create `reading/ledgers/urdu_lexical_exposure.jsonl`.
- [ ] Define initial known-core bands for A1/A2/B1/B2 as coverage heuristics, not CEFR declarations.
- [ ] Define beyond-3,000 verification workflow for C1/C2.
- [ ] Create grammar/discourse target inventories per language and level.
- [ ] Create topic/genre/domain matrix so the curriculum does not overuse one theme.

## Phase 2 — Calibration batch: A1

### Arabic
- [ ] Plan Unit 01 lexical targets and review targets.
- [ ] Draft `ar-a1-u01-p01` through `p06`.
- [ ] Check MSA naturalness and tashkeel policy.
- [ ] Validate contextual inference targets.
- [ ] Validate question/answer correctness.
- [ ] Validate lexical coverage and new-word load.
- [ ] Validate JSONL/schema.
- [ ] Manually inspect all six passages.

### French
- [ ] Plan Unit 01 lexical targets and review targets.
- [ ] Draft `fr-a1-u01-p01` through `p06`.
- [ ] Check contemporary natural French and contraction/elision.
- [ ] Run all passage/question/coverage/schema checks.
- [ ] Manually inspect all six passages.

### Urdu
- [ ] Plan Unit 01 lexical targets and review targets.
- [ ] Draft `ur-a1-u01-p01` through `p06`.
- [ ] Check contemporary Urdu, Unicode/Nastaliq rendering, and early decoding load.
- [ ] Run all passage/question/coverage/schema checks.
- [ ] Manually inspect all six passages.

### Cross-language calibration
- [ ] Compare A1 difficulty across languages without forcing identical token counts.
- [ ] Verify that new words are inferable rather than merely translated by context.
- [ ] Verify that P6 functions as a true high-coverage fluency/checkpoint passage.
- [ ] Adjust standard if calibration exposes a systematic issue.

## Phase 3 — Calibration batch: A2 and B1

- [ ] Produce one six-passage A2 unit in Arabic.
- [ ] Produce one six-passage A2 unit in French.
- [ ] Produce one six-passage A2 unit in Urdu.
- [ ] Validate greater interleaving and reference chains.
- [ ] Produce one six-passage B1 unit in each language.
- [ ] Validate multi-sentence inference, summaries, motive/reason questions, and wider context reuse.
- [ ] Confirm passage-length bands against actual reader timing/comprehension if telemetry is available.

## Phase 4 — Scale A1–B1

For each language:

- [ ] Complete A1 Units 02–10.
- [ ] Complete A2 Units 02–10.
- [ ] Complete B1 Units 02–10.
- [ ] Maintain R1–R5 exposure scheduling in lexical ledger.
- [ ] Ensure every important introduced item receives ~6 meaningful contacts.
- [ ] Maintain genre/topic/domain balance.
- [ ] Run batch audits after every unit.
- [ ] Run cumulative audit at each CEFR-level completion.

## Phase 5 — B2 calibration and scale

- [ ] Produce B2 Unit 01 in each language.
- [ ] Add more abstract topics, arguments, stance, cohesion, and technical-but-accessible prose.
- [ ] Validate use of the full 3,000-item core without assuming all words are mastered.
- [ ] Increase contextual diversity for due vocabulary.
- [ ] Begin paired viewpoints where appropriate.
- [ ] Complete B2 Units 02–10 after calibration.

## Phase 6 — Build advanced lexical inventories for C1/C2

- [ ] Select candidate beyond-3,000 vocabulary from reliable frequency/corpus resources for Arabic.
- [ ] Independently verify contemporary sense/register before learner use.
- [ ] Repeat for French.
- [ ] Repeat for Urdu.
- [ ] Add academic/professional vocabulary.
- [ ] Add literary/journalistic register vocabulary.
- [ ] Add high-value idioms, collocations, discourse markers, and near-synonym contrasts.
- [ ] Record all new advanced lexical items in ledgers with provenance.

## Phase 7 — C1 calibration and scale

- [ ] Produce C1 Unit 01 in each language.
- [ ] Validate demanding longer texts and implicit meaning.
- [ ] Add rhetorical function, assumptions, evidence evaluation, and synthesis questions.
- [ ] Add professional/academic/news/literary-style genre variation.
- [ ] Complete C1 Units 02–10 after calibration.

## Phase 8 — C2 calibration and scale

- [ ] Produce C2 Unit 01 in each language.
- [ ] Validate fine shades of meaning, ambiguity, stance, style, argument reconstruction, and synthesis.
- [ ] Add controlled irony/allusion only where culturally and linguistically natural.
- [ ] Add paired or linked texts with competing perspectives.
- [ ] Complete C2 Units 02–10 after calibration.

## Phase 9 — Reader integration exports

- [ ] Confirm reader's preferred import contract if not already known.
- [ ] Keep JSONL canonical regardless of export format.
- [ ] Create plain-text/JSON/CSV export adapter as required.
- [ ] Ensure rendering order is passage → questions → answers.
- [ ] Ensure answers are hidden until retrieval/reveal in reader UI.
- [ ] Add fields for reading time, WPM, comprehension score, difficult-word reports if reader supports them.

## Phase 10 — Adaptive refinement from telemetry

If reader telemetry becomes available:

- [ ] Record time and comprehension per passage.
- [ ] Do not count speed gains when comprehension <80% project gate.
- [ ] Track which lexical inference/cloze questions fail.
- [ ] Shorten reinforcement interval for failed targets.
- [ ] Increase interval after repeated successful retrieval.
- [ ] Detect passages that are mis-leveled from performance data.
- [ ] Recalibrate passage lengths and coverage bands if evidence warrants.

## Phase 11 — Final publication audit

For every language/level:

- [ ] Required passage count complete or documented exception.
- [ ] No duplicate IDs.
- [ ] All records schema-valid.
- [ ] All passage text language/script-clean.
- [ ] All questions have correct answer keys.
- [ ] All deliberate inference targets are verified.
- [ ] Lexical exposure schedules have no stranded important targets.
- [ ] No accidental dialect/archaic/dictionary-noise senses.
- [ ] No copied copyrighted passages.
- [ ] Factual passages checked.
- [ ] CEFR difficulty reviewed multidimensionally.
- [ ] Speed passages meet high-coverage policy.
- [ ] Topic/genre/domain distribution audited.
- [ ] Final handoff/status updated.

## Immediate next task

Build the normalized lexical/curriculum ledgers, then produce **A1 Unit 01 (six passages) for Arabic, French, and Urdu** as the calibration batch. Do not mass-generate later levels before inspecting those 18 passages.
