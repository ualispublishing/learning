# LANG-WB deep review of final 7 human-judgment strongest flags — 2026-09-08

This note continues the conservative post-audit review of the exact v1.0 production candidate originally bound at `aa9b5d465839edb2ce520133a01d78ed40634c96`.

## Boundary

- Reviewer-aid evidence only; this is **not** native-speaker certification.
- The preserved `strongest_flags_compact.csv` remains unchanged as historical machine-audit evidence.
- No row ledger, learner-facing CSV, PDF, manifest, candidate binding, release state, or reviewer package is changed by this note.
- A row is deprioritized only when the whole learner-facing pairing is defensible from authoritative/reference evidence or exact source provenance.
- A correction candidate is recorded but not applied because changing learner-facing content creates a new candidate and triggers the source-locked rebuild/review loop.

## French — 4 previously retained rows

### 1. Vocabulary #517 `salle` — `gym; hall; room (in a house)`

Classification: `DEPRIORITIZE_CONTEXT_VALID`.

Evidence:
- Larousse and the Académie française define `salle` broadly as a room/large room or a room/local assigned to a particular function.
- Standard combinations include `salle de sport`, and contemporary native French commonly ellipses this to `la salle` in fitness context (`aller à la salle`). A Le Monde feature on young gym users uses exactly that ellipsis in its headline and throughout the article.
- Therefore the candidate's `gym` gloss is contextual/elliptical rather than a false lexical meaning. It is less explicit than `salle de sport`, but not strong enough to classify as a learner-facing defect.

References:
- https://www.larousse.fr/dictionnaires/francais/salle/70707
- https://www.dictionnaire-academie.fr/article/A9S0264
- https://www.lemonde.fr/campus/article/2023/05/10/la-fabrique-du-muscle-chez-les-jeunes-s-il-faut-choisir-entre-les-devoirs-et-aller-a-la-salle-je-prefere-m-entrainer_6172716_4401467.html

### 2. Vocabulary #608 `situation` — `situation (all meanings)`

Classification: `CONFIRMED_CORRECTION_CANDIDATE`.

Evidence:
- The learner gloss's parenthetical `all meanings` makes a universal one-to-one equivalence claim that reputable bilingual dictionaries do not support.
- Cambridge and Collins split French `situation` by context, including ordinary `situation/circumstances`, `job`, and `location`, with additional fixed expressions such as marital status.
- The Académie française likewise distinguishes geographic position, state/circumstances, and employment.
- The underlying French word is valid; the defect is the overbroad English learner gloss, which can imply that every English sense of `situation` maps directly back to French and vice versa.

Exact candidate:
```text
608,situation,situation (all meanings),noun
```

Current audited ledger record:
- `audit/language-workbooks/v1.0/row_by_row_vocab/french_0601_0650.csv`
- rank 608 currently has `PASS` with no proposal.

Proposed future correction direction:
```csv
608,REPAIR,"Post-audit reference check: 'situation (all meanings)' overclaims one-to-one equivalence; use explicit context-bounded learner senses.",situation,"situation; circumstances; location; job (context-dependent)",noun
```

References:
- https://www.dictionnaire-academie.fr/article/A9S1799
- https://dictionary.cambridge.org/dictionary/french-english/situation
- https://www.collinsdictionary.com/dictionary/french-english/situation

### 3. Sentence #719 `Peux-tu, s'il te plaît, me dire pourquoi tu l'aimes ?` / `Can you please tell me why you love her?`

Classification: `DEPRIORITIZE_SOURCE_BOUND_CONTEXT_VALID`.

Evidence:
- The exact candidate row is source-paired to Tatoeba English #467303 and French #467358.
- Tatoeba records French #467358 as initially added specifically as a translation of `Could you please tell me why you love her?`.
- The Académie française confirms that direct-object `le` and `la` both elide to written `l'` before a vowel; the elision therefore hides grammatical gender on the surface. `l'` can represent a feminine antecedent, so English `her` is a valid source-bound reading even though the isolated French sentence does not uniquely encode that gender in writing.

References:
- https://tatoeba.org/en/sentences/show/467358
- https://www.dictionnaire-academie.fr/article/A9L0482

### 4. Sentence #869 `Je ne l'aime pas plus que vous.` / `I don't like it any more than you do.`

Classification: `DEPRIORITIZE_VALID_COMPARATIVE_CONTEXT`.

Evidence:
- The Académie française explicitly gives the same negative comparative pattern: `Je ne le connais pas plus que vous ne le connaissez.`
- `l'` can represent an inanimate direct object when its antecedent is a thing; English `it` is therefore a valid contextual reading.
- The omission after `vous` is normal comparative ellipsis in the source pair; the English supplies `do` naturally.
- The candidate's exact Tatoeba attribution is English #3002682 / French #5923323.

References:
- https://www.dictionnaire-academie.fr/article/A6P1598
- https://www.dictionnaire-academie.fr/article/A9L0482

## Arabic — 3 previously retained rows

### 5. Sentence #267 `من أينَ تعرف هذا؟` / `How do you know this?`

Classification: `DEPRIORITIZE_SOURCE_SUPPORTED_IDIOMATIC_EQUIVALENCE`.

Evidence:
- Tatoeba Arabic #1881366 records that the sentence was initially added as a translation of English #436111 `How do you know that?`.
- The construction literally foregrounds source (`From where do you know this?`) but functions naturally as a question about the basis/source of someone's knowledge, which English commonly renders as `How do you know this/that?`.
- Independent modern Arabic usage also attests the exact phrase `من أين تعرف هذا؟` in that epistemic/source sense.

References:
- https://tatoeba.org/en/sentences/show/1881366
- exact bound candidate row: `completed/languages/workbooks/v1.0/arabic/arabic_sentence_bank_1000.csv`, rank 267.

### 6. Sentence #618 `لا أجد كلمات تكفي لشكرك على مساعدتك.` / `I cannot thank you enough for your assistance.`

Classification: `DEPRIORITIZE_IDIOMATIC_EQUIVALENCE`.

Evidence:
- The Arabic surface meaning is approximately `I cannot find words sufficient to thank you for your help`, while the English idiom `I cannot thank you enough` expresses the same insufficiency/intensity of gratitude.
- Modern Arabic gratitude usage independently attests `لا أجد كلمات تكفي...` / `كلمات الشكر لا تكفي...` constructions for precisely this rhetorical meaning.
- The bound sentence bank also preserves a direct bilingual source attribution: English #54434 / Arabic #5419771.
- This is freer than word-for-word translation, but it does not alter the learner-facing communicative meaning.

Exact bound candidate row:
- `completed/languages/workbooks/v1.0/arabic/arabic_sentence_bank_1000.csv`, rank 618.

### 7. Sentence #747 `لا يعرف أيٌّ من والديّ الاثنين كيف يسبح.` / `Neither of my two parents knows how to swim.`

Classification: `RETAIN_HUMAN_JUDGMENT_NATURALNESS`.

Evidence and reason for retaining:
- The semantic structure is clear: under negation, `أيٌّ من والديّ` yields the intended `neither of my parents`, and `كيف يسبح` = `how to swim`.
- `والديّ` is already dual (`my parents`). Adding `الاثنين` explicitly restates the two-ness. The sequence `والديّ الاثنين` is attested in modern Arabic localization, so it cannot safely be called ungrammatical from machine/reference evidence alone.
- However, prescriptive MSA normally has dedicated dual-emphasis mechanisms such as `كلا/كلتا` and often needs no extra numeral after an already dual noun. For a learner workbook whose main register is MSA, whether `والديّ الاثنين` is natural enough or translation-influenced redundancy is a genuine native-editor judgment.
- Do not auto-repair this row from model judgment alone.

Useful references on dual emphasis:
- Arabic grammar discussions of `كلا/كلتا` as semantic emphasis for the dual.
- Exact bound candidate row: `completed/languages/workbooks/v1.0/arabic/arabic_sentence_bank_1000.csv`, rank 747.

## Final strongest-flag disposition after all post-audit follow-up

Original strongest unresolved set after third-model adjudication: **162 rows**.

Current reviewer-aid disposition:

- `DEPRIORITIZE_VALID` / documented false-positive or context-valid: **158**
- `CONFIRMED_CORRECTION_CANDIDATE`: **3**
  1. French vocabulary #837 `bosser` — remove misleading `emboss/dent` gloss.
  2. French sentence #599 `Aide-moi avec mon devoir...` — replace English-calque `aider ... avec` construction.
  3. French vocabulary #608 `situation (all meanings)` — replace universal gloss with explicit context-bounded senses.
- `RETAIN_HUMAN_JUDGMENT`: **1**
  - Arabic sentence #747 `والديّ الاثنين` — MSA naturalness/register judgment.

Arithmetic: `158 + 3 + 1 = 162`.

This classification does **not** revise the production candidate, overwrite the original audit, certify any language, or weaken the required full-content human review gate. The three confirmed correction candidates must be applied only through the established source-locked repair/rebuild process when a deliberate new-candidate revision is authorized.