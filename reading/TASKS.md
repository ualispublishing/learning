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

- [x] Parse each language's validated top-1,000 + ranks 1001–3000 into a normalized reading lexicon.
- [x] Keep original validated CSVs unchanged; build derived ledgers only.
- [x] Arabic: create a separate 665-row phrase exposure ledger with stable `ar-pNNN` IDs and explicit-review-only A1 eligibility.
- [ ] Arabic: continue pedagogical A1 review beyond the current 26 targeted phrase candidates; do not infer level from phrase-bank order.
- [x] Add normalized form/match-form/POS/rank/meaning fields for ranked reading selection.
- [x] Create `reading/ledgers/arabic_lexical_exposure.jsonl`.
- [x] Create `reading/ledgers/french_lexical_exposure.jsonl`.
- [x] Create `reading/ledgers/urdu_lexical_exposure.jsonl`.
- [x] Define initial known-core planning bands for A1/A2/B1/B2 as coverage heuristics, not CEFR declarations.
- [ ] Define beyond-3,000 verification workflow for C1/C2.
- [x] Create grammar/discourse target inventories per language and level (`reading/planning/grammar_discourse_inventory.json`).
- [x] Create topic/genre/domain matrix so the curriculum does not overuse one theme (`reading/planning/topic_genre_matrix.json`).
- [x] Establish semantic-safety rule: frequency rank may seed selection, but every deliberately taught sense must be learner-checked rather than inherited blindly from a source Back field.
- [x] Record currently known source-gloss issues in `reading/overrides/source_lexicon_issues.json`.
- [ ] Repair or formally supersede the confirmed French/Urdu learner-gloss defects in the canonical source decks.

## Phase 2 — Calibration batch: A1

### Arabic
- [x] Plan Unit 01 lexical targets and review targets.
- [x] Draft `ar-a1-u01-p01` through `p06` in canonical JSONL.
- [x] First-pass MSA naturalness review.
- [x] First-pass contextual inference review.
- [x] First-pass question/answer correctness review.
- [x] Measure lexical coverage and new-word load against the derived learner path using the documented supported-control definition.
- [x] Validate all six records against the canonical JSON Schema and ten-question contract.
- [x] Deep manual inspection of all six after measured coverage; supported-control audit is 6/6 PASS with zero uncontrolled tokens.
- [ ] Persist final supported-coverage/approval fields in all six canonical passage records; P6 benchmark eligibility must remain false until this write is complete.

### French
- [x] Plan Unit 01 lexical targets and review targets.
- [x] Draft `fr-a1-u01-p01` through `p06` in `reading/french/a1/CALIBRATION_UNIT_01.md`.
- [x] First-pass contemporary natural-French/contraction review.
- [x] First-pass question/answer review.
- [x] Block known bad source glosses from passage teaching and use corrected ordinary senses for `pouvoir` and other affected entries.
- [ ] Convert the six staged passages to canonical JSONL.
- [ ] Measure lexical coverage and new-word load.
- [ ] Deep manual inspection of all six after measured coverage is available.

### Urdu
- [x] Plan Unit 01 lexical targets and review targets.
- [x] Draft `ur-a1-u01-p01` through `p06` under `reading/urdu/a1/calibration/`.
- [x] First-pass contemporary Urdu/script review.
- [x] First-pass question/answer review.
- [x] Block the confirmed bad `ہم` and `اب` source glosses and teach the corrected senses `we/us` and `now`.
- [ ] Convert the six staged passages to canonical JSONL.
- [ ] Measure lexical coverage and new-word load.
- [ ] Deep manual inspection of all six after measured coverage is available.

### Cross-language calibration
- [ ] Compare A1 difficulty across languages without forcing identical token counts.
- [ ] Verify every new target is inferable rather than merely translated by context.
- [ ] Verify every P6 functions as a true high-coverage fluency/checkpoint passage.
- [ ] Check that question difficulty is comparable by function, not by literal translation.
- [ ] Adjust the standard if calibration exposes a systematic issue.
- [ ] Approve or rewrite each of the 18 passages individually. **Do not count drafts as approved.**

## Phase 3 — Calibration batch: A2 and B1

Do not begin until the complete 18-passage A1 calibration gate passes.

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

**Do not generate Unit 02 yet.** Arabic Unit 01 has completed schema, supported-control, deep-review, and exposure-ledger gates; the immediate Arabic blocker is to persist those PASS results into the six canonical passage coverage/status fields and verify the resulting records. Continue conservative Arabic phrase A1 review in parallel without treating phrase-bank order as level. After Arabic canonical approval is synchronized, normalize French and Urdu to canonical JSONL, measure coverage, deep-review them, and then complete the cross-language A1 calibration gate.
