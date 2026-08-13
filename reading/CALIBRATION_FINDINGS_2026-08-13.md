# A1 Calibration Findings — 2026-08-13

## State

- Arabic A1 Unit 01: 6 drafts in canonical JSONL.
- French A1 Unit 01: 6 drafts converted to canonical JSONL.
- Urdu A1 Unit 01: 6 drafts converted to canonical JSONL.
- Total drafts: **18**.
- Approved passages: **0**.

Do not start A1 Unit 02 or A2 work until these 18 pass the final calibration gates.

## Infrastructure now complete

- 3,000-entry derived reading lexicon for each language;
- 3,000-row exposure ledger for each language, with zero assumed mastery;
- grammar/discourse inventory;
- topic/genre/domain matrix;
- canonical A1 JSONL conversion for all three languages;
- multilingual tokenization/lemmatization audit infrastructure;
- source-gloss repair evidence;
- revised lexical-coverage policy.

## Source-data lesson

Passage planning exposed real high-frequency gloss defects that earlier generic audits had missed. Confirmed French and Urdu entries were repaired in the canonical root decks, then the publication-readiness and live-integrity audits were rerun.

Permanent rule: **frequency rank may seed passage selection, but every deliberately taught sense must be independently learner-checked.**

See:
- `reading/overrides/source_lexicon_issues.json`
- `audit/confirmed_language_gloss_repairs.json`
- `audit/confirmed_french_gloss_refinement.json`

## First coverage audit: useful failure

The first audit used an experimental A1 planning gate of `rank <= 500` plus 97% coverage for ordinary passages and 98.5% for P6 fluency passages. All 18 drafts required review under that model.

That result is retained as evidence, but the model is now retired as a publication gate.

### Why the model was too crude

1. Arabic tokenization splits common clitics and can split lexical initial letters, creating false unknowns.
2. French exact ranked data misses some extremely common grammatical surface forms.
3. Urdu frequency coverage omits many normal concrete beginner theme words, and analyzer lemmas do not always match source forms.
4. Rank <=500 excludes many perfectly ordinary beginner concepts. Frequency rank is not a CEFR vocabulary syllabus.
5. Proper names, numbers, predictable inflections, and grammar morphemes should not be treated like uncontrolled lexical unknowns.

## Real passage-design finding

The audit also found genuine lexical load, not only analyzer artifacts. Some drafts use too many theme/content words that are not yet supported by the reading path.

Every such item must be classified as one of:

1. ranked frequency-backbone / morphological match;
2. grammar/function support;
3. verified pedagogical support item;
4. deliberate inference/retrieval target; or
5. unnecessary complexity to simplify/remove.

Do not simply declare an unmatched word “known” to improve a percentage.

## Manual language-review notes

### Arabic
- P2 contains a slightly narrator-like use of `هنا`; rewrite it as naturally deictic speech/thought or remove the awkward deixis.
- Some Arabic analyzer outputs are segmentation/lemma artifacts; do not rewrite natural MSA merely to satisfy analyzer mistakes.

### French
- Overall first-pass naturalness is stronger than the rank-500 score suggests.
- P2 deliberately repeats `quand / alors`; retain the retrieval pattern but avoid mechanical prose.
- P4/P5 contain several theme nouns that need support classification or simplification.

### Urdu
- P2 should be simplified around the coordinated object/verb phrase involving `دو کاپیاں اور ایک قلم` so there is no avoidable agreement ambiguity at A1.
- The passages intentionally use the corrected `ہم = we/us` and `اب = now` senses.
- Common concrete words missing from the ranked backbone must enter through a verified support process, not a silent assumption.

## Methodology change

See `reading/planning/LEXICAL_COVERAGE_POLICY.md`.

The new model separates:
- ranked frequency backbone;
- grammar/function support;
- verified pedagogical support vocabulary;
- deliberate inference targets;
- uncontrolled unknowns;
- actual learner-known coverage when telemetry exists.

The research-informed high-coverage principle remains. What changed is how support/knowledge is measured.

## Next exact work

1. Build coverage audit v2 with language-specific normalization and original-token morphology matching.
2. Produce genuine outside-backbone candidate lists after analyzer artifacts are removed.
3. Build the first verified A1 pedagogical-support lexicons.
4. Simplify/rewrite passages whose genuine new-word burden is too high.
5. Apply the Arabic P2 and Urdu P2 language refinements above.
6. Re-run question/answer and contextual-inference audits.
7. Verify every P6 contains only well-supported material before enabling speed benchmarking.
8. Approve passages individually; approved count remains zero until all gates pass.
