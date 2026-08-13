# Lexical Coverage Policy — Graded Reading Curriculum

This policy supersedes any interpretation that `rank <= 500` is itself an A1 vocabulary syllabus or that membership in the validated top-3,000 decks proves learner mastery.

## Why this file exists

The first multilingual A1 coverage audit was intentionally strict. It lemmatized all 18 calibration passages and compared tokens with the ranked reading lexicons. The audit was useful, but it exposed two problems with the original planning shorthand:

1. **Frequency rank is not a CEFR curriculum.** Common beginner theme words such as room, window, market, chair, park, read, walk, etc. may rank above 500 or even fall outside a 3,000-item frequency list.
2. **Morphological analyzers and surface inventories do not align perfectly.** Arabic clitics and inflection, Urdu lemma spelling/inflection, French contractions/function words, and names can create false “unknown” matches.

Therefore a raw `rank <= 500` coverage percentage is diagnostic only. It must not be used as the publication gate.

## Five lexical categories

Every running token in a passage should ultimately fall into one of these categories.

### 1. Frequency-backbone item

A verified item from the canonical ranked language datasets. Rank remains useful for prioritization and recycling, but does not assign CEFR level by itself.

### 2. Grammar/function support

A function word, clitic, contraction, grammatical particle, inflected form, or predictable morphological realization of material already in the curriculum.

Examples include Arabic bound conjunction/preposition particles, French contractions and common function forms, and predictable Urdu inflection/auxiliary forms.

These must be recognized by the coverage tooling rather than counted as uncontrolled vocabulary merely because a surface form is absent from the ranked list.

### 3. Verified pedagogical support item

A concrete or thematic word needed for natural beginner reading but missing from the ranked backbone.

Requirements:
- independently verify contemporary meaning and register;
- assign a stable reading-lexicon ID;
- record language, lemma, sense, POS, source/provenance, intended level/unit, and first exposure;
- do not add a word merely to make a coverage percentage look better;
- keep the number of new support items small enough that the passage remains highly comprehensible.

Support items may receive lighter recycling than a deliberate target, but important/recurrent items should graduate into the normal R1–R5 lifecycle.

### 4. Deliberate inference/retrieval target

A word or chunk intentionally taught by the passage.

At early levels it must appear in a high-constraint context. It is then verified through a question/answer or other retrieval task and deliberately recycled later.

A1 standard planning target remains roughly **1–3 deliberate targets per standard passage**. This is separate from a very small number of pedagogical support items.

### 5. Uncontrolled unknown

A token that is neither already supported nor intentionally introduced.

This is the category the quality gate should minimize. Repeated uncontrolled unknowns are a passage-design defect, even if the prose sounds natural to a native speaker.

## Coverage metrics

Future audits should report several metrics rather than one misleading number:

- `ranked_inventory_coverage`: token coverage attributable to the validated ranked backbone after morphology/function normalization;
- `supported_coverage`: backbone + grammar/function support + verified pedagogical support + properly controlled deliberate targets;
- `uncontrolled_unknown_token_rate`;
- `uncontrolled_unknown_type_count`;
- rank-band distribution as descriptive information only;
- target/support type counts;
- actual learner-known coverage when reader telemetry/mastery evidence becomes available.

## Planning versus actual learner knowledge

`Supported` means the curriculum has made the item reasonably available, not that the individual learner has mastered it.

Actual learner-known coverage should eventually incorporate:
- flashcard/retrieval success;
- earlier passage performance;
- failed inference/cloze questions;
- reader difficult-word reports;
- recency/spacing state.

Until telemetry exists, speed benchmarks are **provisional planning benchmarks**. Faster WPM must never be interpreted as progress if comprehension is poor.

## Initial calibration gates

For A1 calibration, use these as design checks:

- every deliberate target is learner-checked for the intended contemporary sense;
- every outside-backbone content word is either a verified support item or an explicitly controlled target;
- uncontrolled unknown token rate should be approximately zero after final calibration;
- target/support density must still preserve the research-based high-comprehensibility principle;
- P6 fluency/checkpoint has no deliberately new target and should contain only well-supported material;
- the old `rank <= 500 >= 97%` rule is **retired as a gate**.

The broader research-informed 97–98.5% instructional and 98.5–99.5% fluency ideas remain useful when *known/supported vocabulary is measured correctly*. They should not be computed by equating one arbitrary rank cutoff with knowledge.

## Language-specific normalization

### Arabic

- evaluate original orthographic tokens as well as analyzer subwords;
- handle bound `و`, `ف`, `ب`, `ك`, `ل`, `س` and the definite article appropriately;
- use morphology/lemma matches where reliable;
- do not let a tokenizer's mistaken split of a name or lexical initial letter become an “unknown-word” penalty;
- MSA remains default.

### French

- normalize apostrophes and contractions;
- treat common grammatical forms such as `ne`, `à`, `y`, `où`, etc. through grammar/function support when the ranked inventory misses them;
- lemmatize inflected verbs/adjectives before matching;
- contemporary standard French remains default.

### Urdu

- match surface and lemma forms;
- normalize predictable analyzer spelling variants where safe;
- use a verified support lexicon for common concrete words missing from the frequency backbone;
- Urdu script is canonical; Roman Urdu is not a coverage substitute.

## Calibration implication

Do **not** mass-rewrite the 18 A1 drafts solely to maximize a flawed rank-500 score. Instead:

1. improve normalization;
2. identify genuine outside-backbone content words;
3. decide whether each is necessary support, a deliberate target, or unnecessary complexity;
4. simplify/rewrite passages with too many genuine new items;
5. rerun the audit;
6. approve only after uncontrolled unknowns and target load are within policy.
