# LANG-WB sentence-level post-audit checks — 2026-09-08

This note extends the preserved v1.0 machine-audit evidence with a conservative sentence-level follow-up against the exact candidate at `aa9b5d465839edb2ce520133a01d78ed40634c96`.

## Boundary

- Reviewer aid only; not human/native-speaker certification.
- The preserved `strongest_flags_compact.csv` remains unchanged.
- No learner-facing workbook row is changed by this note.
- A sentence is deprioritized only when the exact candidate row, the surrounding controlled pattern where relevant, and a reputable language reference jointly support the flagged translation or construction.
- Pronoun/antecedent ambiguity and genuine naturalness questions remain unresolved.

## Urdu — remaining sentence flags: 10 structurally supported clears

The earlier post-audit note already classified 32 Urdu strongest-sentence flags whose apparent mismatch came from English definite articles. This pass checked the 10 other Urdu sentence flags against the exact controlled sentence bank.

### Demonstrative/adjective template — ranks 763, 778, 798

- `وہ کافی ہے۔` — `That is enough.`
- `وہ تیز ہے۔` — `That is fast.`
- `وہ بہتر ہے۔` — `That is better.`

These rows occur inside explicit parallel `یہ`/`وہ` controlled templates: `یہ ... ہے` = `This is ...`; `وہ ... ہے` = `That is ...`. The adjective senses are independently supported: Rekhta gives `بہتر` as better and standard Urdu `تیز` as fast; `کافی` is the established enough-sense already identified in the original machine-audit README as a known Urdu homograph false-positive pattern.

References:
- https://www.rekhtadictionary.com/meaning-of-behtar?lang=ur
- https://rekhtadictionary.com/urdu-meaning-of-fast
- exact candidate rows 757–800 in `completed/languages/workbooks/v1.0/urdu/urdu_sentence_bank_1000.csv`

Classification: `STRUCTURAL_TEMPLATE_FALSE_POSITIVE`.

### Scheduling/free-time template — ranks 866, 917, 918, 919, 920, 956

- `میں آج شام فارغ ہوں۔` — `I am free this evening.`
- `ہم ہفتے کو فارغ ہیں۔` — `We are free on Saturday.`
- `کیا آپ ہفتے کو فارغ ہیں؟` — `Are you free on Saturday?`
- `کیا ہم ہفتے کو ملیں؟` — `Shall we meet on Saturday?`
- `ہم ہفتے کو بات کر سکتے ہیں۔` — `We can talk on Saturday.`
- `میں چار بجے فارغ ہوں۔` — `I am free at four.`

The candidate contains the same controlled scheduling pattern across mornings/afternoons/evenings, every weekday, and multiple clock times. Rekhta explicitly gives `فارغ` the sense free/at leisure/not busy. The flagged Saturday and four-o'clock rows are structurally identical to their unflagged Monday–Friday/Sunday and other-time neighbors.

Reference:
- https://www.rekhtadictionary.com/meaning-of-faarig?lang=ur
- exact candidate scheduling block in `completed/languages/workbooks/v1.0/urdu/urdu_sentence_bank_1000.csv`

Classification: `STRUCTURAL_TEMPLATE_FALSE_POSITIVE`.

### Rank 997 — `ابھی وقت ہے۔` / `There is still time.`

Rekhta records `ابھی` with senses including `ہنوز، اب تک، اس وقت تک` (still/yet/up to this time), directly supporting the English `still` reading; `وقت` is time.

References:
- https://rekhtadictionary.com/meaning-of-abhii?lang=ur
- https://www.rekhtadictionary.com/urdu-meaning-of-time

Classification: `CONFIRMED_VALID_SENTENCE_EQUIVALENCE`.

**Urdu sentence result:** all 42 Urdu sentence rows that survived the original third-model strongest-flag adjudication now have documented false-positive/low-priority explanations: 32 article-alignment rows from the earlier note + these 10 rows. This does not replace full human review.

## French — 9 sentence flags reference-confirmed

### Rank 13 — `Je t'en prie.` / `You're welcome.`

The Académie française explicitly lists `Je vous en prie` as a conventional response to thanks. The familiar singular `te/t'` variant preserves the same construction.

Reference: https://www.dictionnaire-academie.fr/article/A9P4282

Classification: `CONFIRMED_VALID_SENTENCE_EQUIVALENCE`.

### Ranks 86, 278, 554 — generic `on`

- `Que peut-on faire ?` — `What can you do?`
- `Peut-on y manger quelque chose ?` — `Can you eat something there?`
- `On est ce qu'on mange.` — `You are what you eat.`

The Académie defines `on` as an indefinite human subject and notes that, depending on context, it can correspond to `tu`, `vous`, `je`, `nous`, etc. The English generic `you` is therefore a valid rendering in these source-paired sentences.

References:
- https://www.dictionnaire-academie.fr/article/A9O0421
- https://www.dictionnaire-academie.fr/article/A8O0292

Classification: `GENERIC_PRONOUN_FALSE_POSITIVE`.

### Rank 658 — `Comment oses-tu te montrer ici ?` / `How dare you show your face around here!`

The Académie defines pronominal `se montrer` as appearing/showing oneself and even gives the closely parallel construction `Comment ose-t-il se montrer ?` in an earlier edition. The English idiom `show your face` preserves the meaning rather than adding a new semantic claim.

References:
- https://www.dictionnaire-academie.fr/article/A9M2763
- https://www.dictionnaire-academie.fr/article/A8M1475

Classification: `IDIOMATIC_EQUIVALENCE_FALSE_POSITIVE`.

### Rank 722 — `... se sert d'un tuba ?` / `... use a snorkel?`

Larousse defines the aquatic sense of French `tuba` as the breathing tube used to swim with one's head under water.

Reference: https://www.larousse.fr/dictionnaires/francais/tuba/80115

Classification: `CONFIRMED_VALID_SENTENCE_EQUIVALENCE`.

### Rank 758 — `Un plan ...` / `A map ...`

The Académie defines `plan` as a drawing/representation of a city, district, building, etc., directly supporting `map` in this context.

Reference: https://www.dictionnaire-academie.fr/article/A9P2693

Classification: `CONFIRMED_VALID_SENTENCE_EQUIVALENCE`.

### Rank 774 — `... l'écrire noir sur blanc.` / `... put it in writing.`

The Académie explicitly defines `mettre noir sur blanc` as putting something in writing / stating it in a written document.

Reference: https://dictionnaire-academie.fr/article/A9N0525

Classification: `IDIOMATIC_EQUIVALENCE_FALSE_POSITIVE`.

### Rank 806 — `Je peux te ramener chez toi ...` / `I can give you a lift ...`

The Académie defines `ramener` as taking someone back to the place they came from and gives the example `Montez dans ma voiture : je vous ramène chez vous.` The candidate's English `give you a lift` is a natural rendering of that vehicle-transport sense.

Reference: https://www.dictionnaire-academie.fr/article/A8R0222

Classification: `IDIOMATIC_EQUIVALENCE_FALSE_POSITIVE`.

## Arabic — 5 sentence flags reference/source confirmed

### Rank 30 — `كُل خضراواتك.` / `Eat your vegetables.`

The Cairo Arabic Language Academy records `خَضْراء` for green edible plants/herbs with plural `خضراوات`; the candidate's possessive `خضراواتك` and imperative `كُل` transparently yield `your vegetables` / `eat`.

Reference: https://www.arabicacademy.gov.eg/ar/search_engine/roots/خضر

Classification: `CONFIRMED_VALID_SENTENCE_EQUIVALENCE`.

### Rank 147 — `هل تحب كرة القدم؟` / `Do you like soccer?`

The Cairo Academy explicitly gives `كرة القدم` as `Foot-Ball Soccer` / `soccer = football`.

References:
- https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-327/كرة%20القدم
- https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-217/كرة%20القدم

Classification: `CONFIRMED_VALID_SENTENCE_EQUIVALENCE`.

### Rank 181 — `هذا هو الباقي.` / `Here is your change.`

The exact bilingual source pair in the bound sentence bank maps this phrase to `Here is your change.` Lexically, the Cairo Academy defines the `بقي` family as what remains/is left over and `البقية` as what remains of a thing. In a payment context, `the remainder` is the returned change. No contradictory learner-facing meaning was found.

References:
- https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-19/بقي-أو-بقى
- https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-19/البقية

Classification: `SOURCE_SUPPORTED_IDIOMATIC_EQUIVALENCE`.

### Rank 429 — `ماذا تُسَمّى هذه الوردة؟` / `What do you call this flower?`

The Arabic sentence is passive in form (`What is this flower called?`) while the English uses the ordinary active paraphrase `What do you call this flower?`. The Cairo Academy defines `الاسم` as that by which a thing/person is known and places `سمّى / تسمّى / المسمّى` in the same lexical family. The voice difference does not change the requested naming meaning.

Reference: https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-19/الاسم

Classification: `VOICE_EQUIVALENCE_FALSE_POSITIVE`.

### Rank 452 — `لماذا عصيت أمري؟` / `Why did you disobey my order?`

The Cairo Academy defines `عصى` of a person as leaving obedience and `خالف أمره`—contravening/disobeying his command—almost exactly matching the candidate sentence.

Reference: https://www.arabicacademy.gov.eg/ar/search_engine/roots/عصي

Classification: `CONFIRMED_VALID_SENTENCE_EQUIVALENCE`.

## Rows intentionally not cleared in this sentence pass

Examples retained for human review include:

- French #539 `Nous savons où il est.` / `We know where it is.` — `il` can be masculine-person or masculine-thing dependent on antecedent.
- French #599 `Aide-moi avec mon devoir...` — meaning is understandable, but idiomaticity/register of `aider ... avec` deserves human judgment.
- French #719 `... pourquoi tu l'aimes` / `... why you love her` — `l'` depends on an antecedent not present in the isolated row.
- French #747 `Dois-je vous le clarifier ?` — semantically transparent but stylistic naturalness remains worth human review.
- French #869 `Je ne l'aime pas plus que vous.` — the comparison is defensible, but isolated pronoun/context ambiguity remains.
- Arabic #267 `من أينَ تعرف هذا؟` / `How do you know this?` — plausible idiomatic equivalence, but the `from where` → `how` shift remains worth human review.
- Arabic #618 `لا أجد كلمات تكفي لشكرك...` / `I cannot thank you enough...` — strong idiomatic equivalence, but retained because the English is freer than the Arabic surface form.
- Arabic #680 `كم حقيبة ستأخذون...` / `How many suitcases...` — `حقيبة` can be bag/case and context may matter.
- Arabic #747 `لا يعرف أيٌّ من والديّ الاثنين...` — meaning is clear, but the dual + `الاثنين` combination is a naturalness question best left to a human reviewer.

## Result

This note newly deprioritizes **24** strongest sentence flags:

- Urdu: **10**
- French: **9**
- Arabic: **5**

Combined with the prior post-audit note's **75** documented low-priority/false-positive rows, **99 of the original 162 strongest flags** now have a documented machine/reference reason to be deprioritized.

The remaining strongest-flag set is therefore **63 rows** for focused follow-up/human attention. This arithmetic is a reviewer-aid prioritization only; it does not alter the preserved original audit status, certify any language, or change the release gate.