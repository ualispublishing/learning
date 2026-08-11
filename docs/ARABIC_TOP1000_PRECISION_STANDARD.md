# Arabic Top 1000 Precision Standard

## Purpose

`arabic_top1000.csv` is a ranked Modern Standard Arabic lexical deck. Precision takes priority over metadata completeness: an uncertain field is omitted rather than guessed.

## Inventory authority

The ranking is based on Table 4 of:

> Almoataz B. Al-Said (2023), “A New List of Common Words in Modern Standard Arabic,” *Miscelánea de Estudios Árabes y Hebraicos. Sección Árabe-Islam* 72, 287–351. DOI: 10.30827/meaharabe.v72.23634.

The paper reports a 1,000-item undiacritized MSA common-word inventory, subcategorized into 1,250 vocalized forms. The published rank is the only authority for deck ordering.

## Morphological validation

CALIMA-MSA r13 through CAMeL Tools is used as an independent MSA morphology layer for:

- lexical/grammatical analysis;
- lemma validation;
- English lexical gloss validation;
- derivational-root validation.

CAMeL frequency data may help repair PDF text-extraction artifacts, but it must never reorder the published Al-Said inventory.

## Front contract

Every `Front` must:

1. contain Arabic script only;
2. contain no English, French, Urdu, transliteration, hint, definition, rank, or grammatical explanation;
3. represent exactly one reconciled published rank;
4. be a single lexical form, not an unrelated multiword phrase.

## Back contract

A precision-grade back contains only supportable fields:

- published rank;
- meaning / grammatical sense(s);
- part of speech;
- lemma when it differs usefully from the surface form;
- derivational root only when morphologically justified;
- source attribution.

Homographs must be separated into explicit sense blocks rather than blended into one vague definition.

## Root policy

Do not manufacture roots from the visible letters of a word.

- Prepositions, conjunctions, pronouns, particles and similar closed-class items receive no productive lexical root.
- A content-word root is emitted only when a compatible CALIMA-MSA lexical analysis supports a three- or four-radical root.
- If compatible analyses disagree materially, the root is omitted rather than guessed.
- A multiword expression never receives one synthetic “whole-phrase root.”

## Translation / enrichment policy

The original uploaded deck contained English, French and Urdu translations plus generated examples, synonyms and etymological claims. These fields are not retained merely to preserve density.

- English meanings in the precision core must be tied to compatible MSA lexical analyses.
- French or Urdu may be added only when independently verified against a suitable bilingual lexicographic source for the exact sense.
- Examples, synonyms and etymologies may be added only when source-grounded and sense-specific.
- Missing enrichment is preferable to plausible-looking but unverified enrichment.

## Legacy material

The original uploaded CSV is preserved verbatim under `archive/wordlists/arabic_top1000_uploaded_2026-08-11.csv`.

Its multiword material is preserved separately in `arabic_phrase_bank.csv`; phrase-bank membership does not make an item part of the 1,000-word lexical core.

## Acceptance checks

A replacement `arabic_top1000.csv` must pass all of the following before promotion:

- exactly 1,000 data rows;
- exactly 1,000 reconciled rank records;
- Arabic-only fronts;
- no unresolved PDF extraction artifacts;
- no duplicate fronts unless the published source demonstrably requires separate rank records and the ambiguity is explicitly reviewed;
- at least one paper-POS-compatible MSA analysis per card;
- no invented roots;
- no synthetic phrase roots;
- no `AR: (self)` or similar generation artifacts;
- no unsourced synonym/example/etymology filler.
