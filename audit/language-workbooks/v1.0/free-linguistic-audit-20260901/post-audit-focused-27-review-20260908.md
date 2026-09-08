# LANG-WB focused review of final 27 strongest flags — 2026-09-08

This note continues the conservative post-audit review of the v1.0 production candidate originally bound at `aa9b5d465839edb2ce520133a01d78ed40634c96`.

## Boundary

- Reviewer-aid evidence only; this is **not** native-speaker certification.
- The preserved `strongest_flags_compact.csv` remains unchanged.
- No learner-facing workbook row is modified by this note.
- Existing candidate/reviewer-package binding is therefore not changed.
- Rows are classified as `DEPRIORITIZE_VALID`, `CONFIRMED_CORRECTION_CANDIDATE`, or `RETAIN_HUMAN_JUDGMENT`.
- A correction candidate is not applied here because changing learner-facing content would create a materially changed candidate and require a new review/release-binding cycle.

## French — 14 rows

### Deprioritize as valid — 8

1. Vocabulary #143 `déjà` — candidate senses `already, before; for a start, firstly; again (following a question)` are documented French uses. Larousse/CNRTL support the temporal, discourse/start, and reminder-question senses.
   - https://www.larousse.fr/dictionnaires/francais-anglais/deja
   - https://www.cnrtl.fr/definition/d%C3%A9j%C3%A0
   - Classification: `DEPRIORITIZE_VALID`

2. Vocabulary #623 `cool` — informal/anglicism senses include relaxed/fashionable and interjection-like `super/génial` usage.
   - https://fr.wiktionary.org/wiki/cool
   - https://www.larousse.fr/dictionnaires/francais/cool
   - Classification: `DEPRIORITIZE_VALID`

3. Sentence #62 `Vous connaissons-nous ?` / `Do we know you?` — formal inversion is grammatical: object `vous` precedes the verb while interrogative subject `nous` follows it; `nous connaissons` is the correct first-person plural form.
   - https://www.dictionnaire-academie.fr/article/A8V0800
   - https://www.dictionnaire-academie.fr/article/A8N0436
   - Classification: `DEPRIORITIZE_VALID_FORMAL_REGISTER`

4. Sentence #281 `Pouvez-vous parler plus lentement, s'il vous plaît ?` / `Can you speak more slowly, please?` — ordinary grammatical comparative/adverbial construction; no semantic mismatch remains.
   - Dictionnaire de l’Académie française, `lentement` / comparative usage.
   - Classification: `DEPRIORITIZE_VALID`

5. Sentence #539 `Nous savons où il est.` / `We know where it is.` — French masculine `il` can refer to a person **or a masculine thing**, so English `it` is valid when the antecedent is inanimate.
   - https://dictionnaire-academie.fr/article/A8I0078
   - Classification: `DEPRIORITIZE_CONTEXT_VALID`

6. Sentence #688 `Puis-je avoir deux hamburgers et un coca, s'il vous plaît ?` / `Can I have two hamburgers and a Coke, please?` — familiar French `coca` is an abbreviation of Coca-Cola/Coke.
   - Larousse, `coca` / Coca-Cola usage.
   - Classification: `DEPRIORITIZE_VALID`

7. Sentence #747 `Dois-je vous le clarifier ?` / `Do I have to clarify it for you?` — `clarifier` has a figurative transitive sense “make a thought/discourse clear.” The sentence is somewhat formal but semantically and grammatically valid.
   - https://www.dictionnaire-academie.fr/article/A9C2516
   - Classification: `DEPRIORITIZE_VALID_FORMAL_REGISTER`

8. Sentence #769 `Tout ce que tu as à faire, c'est appuyer sur ce bouton.` / `All you have to do is push this button.` — `appuyer sur un bouton` is explicitly standard French for pressing/pushing a button.
   - https://www.dictionnaire-academie.fr/article/A9A2285
   - Classification: `DEPRIORITIZE_VALID`

### Confirmed correction candidates — 2

1. Vocabulary #837 `bosser` — candidate gloss: `to work (informal); emboss/dent`.
   - `bosser` is supported for informal “to work” (and a separate nautical transitive sense), but the physical “emboss/dent / make bumps” meaning belongs to verbs such as `bosseler`/`bossuer`, not ordinary `bosser`.
   - References:
     - Académie française, `bosser`
     - Larousse, `bosser`
     - Larousse, `bosseler` / `bossuer`
   - Classification: `CONFIRMED_CORRECTION_CANDIDATE`
   - Proposed correction direction: narrow the learner gloss to the supported modern sense, e.g. `to work (informal)`, unless a separately sourced specialized sense is intentionally retained.

2. Sentence #599 `Aide-moi avec mon devoir, s’il te plaît.` / `Help me with my homework, please.`
   - The Office québécois de la langue française explicitly identifies `aider quelqu’un avec quelque chose` modeled on English `help somebody with` as a syntactic calque and recommends constructions such as `aider quelqu’un à faire ses devoirs`.
   - Reference: OQLF / Banque de dépannage linguistique, `AVEC : emplois déconseillés calqués sur l’anglais` and `Aider et ses compléments`.
   - Classification: `CONFIRMED_CORRECTION_CANDIDATE`
   - Proposed correction direction: `Aide-moi à faire mes devoirs, s’il te plaît.`

### Retain for human judgment — 4

1. Vocabulary #517 `salle` — `room/hall` is secure, while standalone `gym` is contextual shorthand (`salle de sport`, `salle de gym`) rather than a clean universal lexical sense.
   - Classification: `RETAIN_HUMAN_JUDGMENT`

2. Vocabulary #608 `situation` — candidate `situation (all meanings)` is too broad to certify as a useful learner gloss even though French `situation` has many English-overlapping senses.
   - https://dictionnaire-academie.fr/article/A9S1799
   - Classification: `RETAIN_HUMAN_JUDGMENT_EDITORIAL_SCOPE`

3. Sentence #719 `Peux-tu, s'il te plaît, me dire pourquoi tu l'aimes ?` / `Can you please tell me why you love her?` — elided `l'` can stand for masculine/feminine or thing/person depending on antecedent; isolated row does not independently establish `her`.
   - Classification: `RETAIN_HUMAN_JUDGMENT_CONTEXT`

4. Sentence #869 `Je ne l'aime pas plus que vous.` / `I don't like it any more than you do.` — the comparative reading is defensible, but the isolated pronoun and ellipsis leave enough contextual ambiguity to retain human review.
   - Classification: `RETAIN_HUMAN_JUDGMENT_CONTEXT`

## Arabic — 10 rows

### Deprioritize as valid — 7

1. Vocabulary #347 `ما` — exclamative `ما` in the standard `ما أفعل` pattern supports English `how...! / what a...!`.
   - Standard Arabic exclamative grammar: `ما أفعل`.
   - Classification: `DEPRIORITIZE_VALID_GRAMMATICAL_PATTERN`

2. Vocabulary #536 `ألم` — whole unvocalized row is valid: `أَلَم` = pain, while segmented interrogative `أَ + لَمْ` yields `did ... not?`.
   - Cairo Arabic Language Academy, entries for `الألم`, interrogative hamza, and `لم`.
   - Classification: `DEPRIORITIZE_VALID_UNVOCALIZED_POLYSEMY`

3. Vocabulary #842 `جاري` — context/vocalization supports `current/ongoing`, while `جار` + first-person possessive suffix yields `جاري` = `my neighbor`.
   - Classification: `DEPRIORITIZE_VALID_CONTEXTUAL_POLYSEMY`

4. Sentence #177 `كُلْ ما تريد.` / `Eat whatever you like.` — imperative `كُلْ` + non-human/general relative `ما` + `تريد` gives the intended `eat what/whatever you want/like` meaning.
   - Classification: `DEPRIORITIZE_VALID`

5. Sentence #680 `كم حقيبة ستأخذون في رحلتكم؟` / `How many suitcases are you taking on your trip?` — Arabic `حقيبة` covers bag/case and is used for suitcase/travel-bag meanings; travel context supports the English choice.
   - Cairo Arabic Language Academy: https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-19/حقيبة
   - Cambridge English–Arabic `suitcase`: https://dictionary.cambridge.org/dictionary/english-arabic/suitcase
   - Classification: `DEPRIORITIZE_CONTEXT_VALID`

6. Sentence #685 `أثمّة ما تريد إخباري عنه؟` / `Is there anything that you want to tell me?` — `ثَمّة` is an existential expression meaning `there is/there are`; the rest of the clause transparently asks whether there is something the listener wants to tell the speaker about.
   - Reference grammar / dictionaries for existential `ثَمّة`.
   - Classification: `DEPRIORITIZE_VALID`

7. Sentence #745 `أين هي الوثائق التي كانت على طاولتي؟` / `Where are the documents that were on my desk?` — `الوثائق` is a non-human plural; feminine-singular agreement such as `كانت` is standard Arabic agreement, not a number/gender error.
   - Michigan State University Elementary Arabic II: non-human plurals take feminine-singular agreement.
   - https://openbooks.lib.msu.edu/elemarabicll/chapter/grammar-2/
   - Classification: `DEPRIORITIZE_VALID_NONHUMAN_PLURAL_AGREEMENT`

### Retain for human judgment — 3

1. Sentence #267 `من أينَ تعرف هذا؟` / `How do you know this?` — `من أين تعرف...؟` is attested idiomatically for asking the source/basis of knowledge and can map naturally to English `How do you know...?`, but the literal `from where` → `how` shift is retained for human naturalness judgment.
   - Classification: `RETAIN_HUMAN_JUDGMENT_IDIOMATICITY`

2. Sentence #618 `لا أجد كلمات تكفي لشكرك على مساعدتك.` / `I cannot thank you enough for your assistance.` — semantic intent is strong and idiomatic, but the English is a freer equivalence than the Arabic surface form.
   - Classification: `RETAIN_HUMAN_JUDGMENT_IDIOMATICITY`

3. Sentence #747 `لا يعرف أيٌّ من والديّ الاثنين كيف يسبح.` / `Neither of my two parents knows how to swim.` — meaning is understandable, and `والديّ الاثنين` is attested, but the dual form plus explicit `الاثنين` can feel redundant depending on register. Retain for native naturalness judgment.
   - Classification: `RETAIN_HUMAN_JUDGMENT_NATURALNESS`

## Urdu — 3 rows

### Deprioritize as valid — 3

1. Vocabulary #70 `سی` — Urdu resemblance construction `سا/سی/سے` agrees in gender/number; `سی` is the feminine form used to add `-like / seeming` meaning, e.g. `اچھی سی چائے`.
   - Michigan State University Basic Urdu, `Use of سا With Adjectives`: https://openbooks.lib.msu.edu/urdu/chapter/3-5/
   - Classification: `DEPRIORITIZE_VALID_MORPHOLOGY`

2. Vocabulary #71 `طور` — unvocalized script covers distinct readings: `طور / taur` = manner/way/state/condition and `طور / tur` = hill/mount (including learned/proper-name use).
   - Rekhta Dictionary and Urdu/Wiktionary lexical evidence.
   - Classification: `DEPRIORITIZE_VALID_UNDIACRITIZED_POLYSEMY`

3. Vocabulary #495 `فیصل` — established masculine given name `Faisal`, from Arabic, in Urdu usage.
   - Urdu lexical/proper-name sources.
   - Classification: `DEPRIORITIZE_VALID_PROPER_NAME`

## Result

Focused 27-row outcome:

- `DEPRIORITIZE_VALID`: **18**
  - French: 8
  - Arabic: 7
  - Urdu: 3
- `CONFIRMED_CORRECTION_CANDIDATE`: **2**
  - French vocabulary #837 `bosser`
  - French sentence #599 `Aide-moi avec mon devoir...`
- `RETAIN_HUMAN_JUDGMENT`: **7**
  - French: 4
  - Arabic: 3
  - Urdu: 0

Combined with the prior **135/162** documented low-priority/false-positive strongest flags, this pass brings the documented deprioritized set to **153/162**.

The remaining **9/162** strongest flags are therefore no longer an undifferentiated machine queue:

- **2 confirmed correction candidates** requiring a deliberate candidate revision decision;
- **7 genuine human-judgment rows** requiring native/near-native contextual/naturalness review.

No learner-facing file, PDF, manifest, release state, candidate binding, or reviewer package was changed by this audit note.