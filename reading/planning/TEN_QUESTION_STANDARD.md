# Ten-Question Standard for Graded Reading

Every canonical graded-reading passage should contain **10 questions with 10 linked answers** unless a documented exceptional reason makes ten pedagogically harmful. Ten is the default for A1-C2.

The questions are not limited to literal passage recall. They also reinforce vocabulary, grammar, morphology, discourse, inference, and transfer at the passage's CEFR planning level.

## Core rules

1. Every question has exactly one `answer_id`; every answer points back to exactly one `question_id`.
2. Questions 1-5 normally remain passage-centred. Questions 6-10 may use the passage, its target vocabulary, or level-appropriate grammar independent of the passage.
3. At least one question per deliberate lexical target must test meaning in context or transfer rather than simple copying.
4. Single-word definition / meaning questions are allowed and encouraged when they reinforce a verified flashcard sense.
5. Grammar questions may be independent of the passage when the grammar itself is appropriate to the current CEFR planning level.
6. Cloze questions should normally require retrieval in a new sentence rather than reproducing the passage verbatim.
7. Distractors must be plausible but unambiguously wrong at the target level.
8. Do not test a lexical sense unless that exact sense has passed the language-specific flashcard verification gate.
9. A fluency/checkpoint passage may contain grammar and vocabulary review questions but must not introduce a new lexical target through the questions.
10. Question difficulty must rise through the levels; ten A1 questions should not become ten trivial recall questions, and ten C-level questions should not become ten obscure vocabulary quizzes.

## Default distribution by level

### A1
- 2 literal/gist questions
- 2 passage-linked vocabulary/context questions
- 1 passage-linked sequence/reference/inference question
- 1 single-word meaning/definition retrieval question
- 1 basic grammar/category question
- 1 form/contrast question (pronoun, demonstrative, negation, quantity, tense/aspect, agreement, etc.)
- 1 new-sentence cloze
- 1 simple transfer/production or matching question

Typical answer length: one word to one short sentence.

### A2
- 2 literal/gist
- 1 sequence/reference
- 1 local inference
- 2 vocabulary/collocation
- 2 grammar/form questions
- 1 cloze/transform
- 1 short transfer question

### B1
- 2 comprehension/detail
- 2 inference/reference/cause
- 2 vocabulary/collocation/word-family
- 2 grammar/discourse-form questions
- 1 transfer/transform
- 1 one- or two-sentence summary

### B2
- 2 comprehension/inference
- 2 lexical nuance/collocation/register
- 2 grammar/syntax questions
- 2 cohesion/discourse/rhetorical-function questions
- 1 transfer/reformulation
- 1 synthesis/summary

### C1
- 2 deep inference/implicit stance
- 2 lexical nuance/register/idiom
- 2 syntax/grammar/style
- 2 discourse/rhetoric/pragmatics
- 2 synthesis, reformulation, or critical interpretation

### C2
- 2 subtle inference/allusion/implicature
- 2 lexical precision/idiom/register
- 2 complex syntax/style alternatives
- 2 rhetorical/pragmatic/discourse analysis
- 2 synthesis, transformation, or fine-grained interpretation

## Flashcard linkage

A question that directly teaches a flashcard must record the flashcard/lexicon ID in `target_ids` when the schema supports it. The reader curriculum therefore becomes a second audit surface for the vocabulary decks:

- if a question exposes an ambiguous or unnatural gloss, the flashcard enters the language audit queue;
- if the flashcard is corrected, the reader target/question must use the corrected sense;
- a card is not considered educator-ready merely because it exists in a published CSV;
- cards actually used by the reader receive an additional `reader_verified` evidence state after independent verification.

## CEFR note

CEFR is used here as a **difficulty and communicative-competence planning framework**, not as a universal language-independent word-rank list. Vocabulary selection combines the project's verified frequency backbone, pedagogical support vocabulary, actual passage context, and language-specific review. Level assignment must therefore be treated as a curriculum decision rather than a claim that a particular frequency rank is intrinsically A1, B1, etc.
