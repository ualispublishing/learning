# LANG-WB broader external-verification weak-source review — 2026-09-09

This reviewer-aid note continues the normal v1.0 book QA track after the original strongest-model flag queue was fully triaged. It does not modify learner-facing content, candidate bindings, release state, or human sign-off requirements.

## Why this pass

The independent external-verification queues are intentionally broad triage tools rather than correctness oracles. Their own policy states that missing source coverage is not proof that an entry is wrong. This pass therefore reviewed the **lowest-support rows first**, because those are the places where external coverage could most plausibly hide a real defect.

Current external-verification summaries:

- Arabic: 1,000 rows; 739 strong; 122 semantic-review; 139 form-only; 261 queued; Kaikki 981/1000; Arabic WordNet 810/1000; CALIMA 997/1000; no source-load problem.
- French: 1,000 rows; 970 strong; 22 semantic-review; 8 form-only; 30 queued; Kaikki 1000/1000; but Lexique4 coverage is **0** because the verifier failed to recognize the actual surface-form column (`1_Mot`).
- Urdu: 1,000 rows; 886 strong; 57 semantic-review; 53 form-only; **4 weak**; 114 queued; Kaikki 949/1000; Urdu UD 967/1000; no source-load problem.

The following classifications are prioritization evidence only; they do not replace full human review.

## Urdu — all 4 `weak` external rows checked

### Rank 503 — `داری`

Current candidate:
- `possession; holding; practice/state; -holding/-keeping (especially in compounds)`
- POS `noun / suffix`

The current row-by-row audit already marks this as an explicit `REPAIR`, correcting an earlier vague POS/definition. Rekhta independently describes Persian-derived `داری` as a suffix conveying having/holding/possessing and ownership/control in compounds.

Reference:
- https://rekhtadictionary.com/meaning-of-daarii-1?lang=ur

Classification: `EXTERNAL_WEAK_FALSE_POSITIVE_ALREADY_REPAIRED`.

### Rank 509 — `کن`

Current candidate:
- `which; whom (plural/oblique interrogative, context-dependent)`
- POS `interrogative pronoun / determiner`

The row-by-row audit already repaired this exact entry. Rekhta's lexical search records `kin` as `What, Which, Who`, and its English-to-Urdu material confirms the interrogative/oblique family (`کس`, `کن`).

References:
- https://www.rekhtadictionary.com/compound-words-containing-kan
- https://www.rekhtadictionary.com/urdu-meaning-of-whom

Classification: `EXTERNAL_WEAK_FALSE_POSITIVE_ALREADY_REPAIRED`.

### Rank 964 — `مری`

Current candidate:
- `died (feminine singular); Murree (place name)`
- POS `verb form / proper noun`

The row-by-row audit already repaired this entry from an unusable generic analysis. Rekhta confirms multiple unvocalized `مری` readings, including dead/expired senses; the feminine perfect `مری` from `مرنا` is standard Urdu morphology. The proper name Murree is the normal Urdu spelling of the Pakistani place name.

Reference:
- https://rekhtadictionary.com/meaning-of-murii?lang=ur

Classification: `EXTERNAL_WEAK_FALSE_POSITIVE_ALREADY_REPAIRED`.

### Rank 980 — `داد`

Current candidate:
- `praise; appreciation; applause; justice/redress (context-dependent)`
- POS `noun`

The row-by-row audit already repaired this exact entry. Rekhta explicitly lists praise/applause/acclamation as well as justice/equity/redress senses.

Reference:
- https://www.rekhtadictionary.com/meaning-of-daad-1?lang=ur

Classification: `EXTERNAL_WEAK_FALSE_POSITIVE_ALREADY_REPAIRED`.

**Urdu weak-result:** `4/4` weak rows checked; **0 new learner defects**. The weak labels came from sparse external-source matching, not from incorrect current learner glosses.

## Arabic — all support-count-2 external rows checked

The Arabic queue has no `weak` confidence class, so this pass reviewed the lowest-support rows visible in the queue: the rows with only two independent support signals.

### Rank 194 — `لذا`

Current candidate: `therefore; thus; for that reason`.

`لذا` is a standard shortened/related connective in the `لهذا/لذلك` family. Wiktionary records `لِهٰذَا` = `therefore` and gives `لِذَا` as an alternative form.

Reference:
- https://en.wiktionary.org/wiki/لهذا

Classification: `LOW_SUPPORT_VALID_CONNECTIVE`.

### Rank 257 — `ما زال`

Current candidate: `still is/was; continues/continued to be`.

This row was already explicitly repaired in the Arabic row-by-row audit to enforce formal MSA spacing (`ما زال`, not fused `مازال`). Lexical grammar for `يزال` records the negative idiom as `still`.

Reference:
- https://en.wiktionary.org/wiki/يزال

Classification: `LOW_SUPPORT_VALID_ALREADY_REPAIRED`.

### Rank 475 — `مشيرا`

Current candidate: `indicating; pointing out; noting (mushiran)`; active participle used adverbially/circumstantially.

`أشار` means to point, point out, indicate, or refer; its active participle is `مُشِير`, and accusative/circumstantial `مُشِيرًا` gives the candidate surface form (normally written without diacritics as `مشيرا`).

Reference:
- https://en.wiktionary.org/wiki/أشار

Classification: `LOW_SUPPORT_VALID_TRANSPARENT_MORPHOLOGY`.

### Rank 619 — `مؤكدا`

Current candidate: `confirming; emphasizing; confirmed; certain; definitely (depending on vocalization/context)` with participial/adverbial POS.

This row was already explicitly repaired by the Arabic row-by-row audit. `أكّد` is independently documented for confirm/corroborate/assert/emphasize; the undiacritized accusative participle can represent active/passive/contextual readings reflected in the learner entry.

Reference:
- https://en.wiktionary.org/wiki/أكد

Classification: `LOW_SUPPORT_VALID_ALREADY_REPAIRED`.

### Rank 747 — `إجراءات`

Current candidate: `procedures; measures; actions`.

The Cairo Arabic Language Academy defines `الإجراء` as an action/measure taken by an official body and explicitly gives plural `إجراءات`; it also uses `إجراءات البحث` for research procedures/mechanisms.

Reference:
- https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-19/الإجراء

Classification: `LOW_SUPPORT_VALID_LEXICAL_FORM`.

### Rank 841 — `يعاني`

Current candidate: `suffers`.

Wiktionary gives `عانى` = suffer/bear/endure and explicitly identifies non-past `يُعَانِي`.

Reference:
- https://en.wiktionary.org/wiki/عانى

Classification: `LOW_SUPPORT_VALID_INFLECTED_VERB`.

### Rank 927 — `وفقا`

Current candidate: `according to; in accordance with (commonly وَفْقًا لِـ)`.

Wiktionary's translation entry for `according to` explicitly gives Arabic `وَفْقًا لِـ`.

Reference:
- https://en.wiktionary.org/wiki/according_to

Classification: `LOW_SUPPORT_VALID_FIXED_EXPRESSION`.

### Rank 952 — `يتمكن`

Current candidate: `manages to; is able to`.

The lexical entry for `تَمَكَّنَ` explicitly gives `to be able to, to be in the position to`, with non-past `يَتَمَكَّنُ`.

Reference:
- https://en.wiktionary.org/wiki/تمكن

Classification: `LOW_SUPPORT_VALID_INFLECTED_VERB`.

### Rank 953 — `جهود`

Current candidate: `efforts`.

`جُهْد` is exertion/effort and its plural is `جهود`; the candidate is straightforward plural morphology.

References:
- https://en.wiktionary.org/wiki/جهد
- https://www.arabicacademy.gov.eg/ar/محرك-البحث/جهد

Classification: `LOW_SUPPORT_VALID_INFLECTED_NOUN`.

**Arabic lowest-support result:** all **9** support-count-2 rows checked; **0 new learner defects**. Two were already repaired by the source-locked row audit; the rest are ordinary lexical/morphological forms whose low score reflects external dictionary/analyzer coverage rather than bad learner content.

## French — queue is currently instrumentation-limited

The French external verifier reports:

- 970/1000 rows with semantic overlap;
- only 30 rows queued;
- Kaikki coverage 1000/1000 and wordfreq attestation 1000/1000;
- **Lexique4 coverage 0/1000** because the verifier does not recognize the actual Lexique4 column names, beginning with `1_Mot`.

Therefore the French 30-row queue should not be interpreted as 30 independent linguistic warnings. Every queued row has lost an intended French-specific support signal because of the loader problem. The appropriate next QA step is to repair the Lexique4 column detection and regenerate the French external-verification summary/queue before spending more editorial time on those 30 rows.

Classification for the French queue at this stage: `REGENERATE_AFTER_VERIFIER_FIX`, not content PASS/FAIL.

## Batch result

Lowest-confidence external-verification layer reviewed:

- Urdu `weak`: **4/4 reviewed, 0 new defects**.
- Arabic support-count-2: **9/9 reviewed, 0 new defects**.
- French: identified a **systemic Lexique4 loader defect** affecting the full 30-row review queue; content adjudication deferred until that verifier is repaired and rerun.

No learner-facing CSV/PDF, release manifest, candidate binding, reviewer package, or human-signoff record was changed by this note.
