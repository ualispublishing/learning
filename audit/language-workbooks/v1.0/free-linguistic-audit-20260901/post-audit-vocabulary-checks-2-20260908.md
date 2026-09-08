# LANG-WB second vocabulary reference pass — 2026-09-08

This note continues the conservative post-audit review of rows left `UNRESOLVED` by the preserved v1.0 machine linguistic audit.

## Boundary

- Exact candidate: `aa9b5d465839edb2ce520133a01d78ed40634c96`
- Reviewer-aid evidence only; this is **not** native-speaker certification.
- The original `strongest_flags_compact.csv` remains unchanged as historical audit evidence.
- No learner-facing workbook row was changed.
- A row is cleared here only when the **whole candidate gloss/form**, not merely one convenient sense, is supported by the cited reference or transparent morphology.
- Borderline polysemy, register, and idiomaticity remain for human review.

## French — 3 additional whole-row clears

| Rank | Target | Candidate gloss/form | Classification | Reference |
|---:|---|---|---|---|
| 641 | `habitude` | habit; regularly repeated action | `CONFIRMED_VALID_LEXICAL_SENSE` | Académie française: https://www.dictionnaire-academie.fr/article/A9H0004 |
| 665 | `con` | stupid/dumb; idiot/jerk; vulgar anatomical sense | `CONFIRMED_VALID_LEXICAL_SENSE` | Académie française: https://www.dictionnaire-academie.fr/article/A10C1464 |
| 817 | `télé` | TV / telly | `CONFIRMED_VALID_LEXICAL_SENSE` | Larousse: https://www.larousse.fr/dictionnaires/francais/télé/77012 |

These are exact candidate rows from `completed/languages/workbooks/v1.0/french/french_vocabulary_1000.csv`.

## Arabic — 10 additional whole-row clears

| Rank | Target | Candidate gloss/form | Classification | Reference |
|---:|---|---|---|---|
| 7 | `هذا` | this, masculine singular | `CONFIRMED_VALID_DEMONSTRATIVE_FORM` | Wiktionary: https://en.wiktionary.org/wiki/هذا |
| 14 | `ذلك` | that, masculine singular | `CONFIRMED_VALID_DEMONSTRATIVE_FORM` | Wiktionary: https://en.wiktionary.org/wiki/ذلك |
| 25 | `هذه` | this, feminine singular | `CONFIRMED_VALID_DEMONSTRATIVE_FORM` | Wiktionary: https://en.wiktionary.org/wiki/هذه |
| 90 | `تلك` | that, feminine singular | `CONFIRMED_VALID_DEMONSTRATIVE_FORM` | Wiktionary: https://en.wiktionary.org/wiki/تلك |
| 159 | `ثانية` | second; a second (time unit); feminine ordinal second | `CONFIRMED_VALID_POLYSEMY` | Wiktionary: https://en.wiktionary.org/wiki/ثانية |
| 232 | `أيام` | days | `CONFIRMED_VALID_INFLECTED_FORM` | Wiktionary: https://en.wiktionary.org/wiki/أيام |
| 386 | `لما` | when; not yet; for/to what depending on vocalization/segmentation | `CONFIRMED_VALID_UNVOCALIZED_POLYSEMY` | Wiktionary: https://en.wiktionary.org/wiki/لما |
| 617 | `أحيان` | times/occasions; adverbial `أحيانًا` = sometimes | `CONFIRMED_VALID_LEXICAL_AND_ADVERBIAL_FORM` | Cairo Arabic Language Academy root/lexical evidence and Wiktionary: https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-19/الحين ; https://en.wiktionary.org/wiki/أحيانًا |
| 644 | `أشهر` | months; more/most famous depending on vocalization | `CONFIRMED_VALID_UNVOCALIZED_POLYSEMY` | Cairo Arabic Language Academy for plural of `شهر`; Wiktionary for elative `أَشْهَر`: https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-19/الشهر ; https://en.wiktionary.org/wiki/أشهر |
| 977 | `عادة` | habit/custom; adverbial `عادةً` = usually | `CONFIRMED_VALID_LEXICAL_AND_ADVERBIAL_FORM` | Cairo Arabic Language Academy and Wiktionary: https://www.arabicacademy.gov.eg/ar/محرك-البحث/معجم/dic-19/العادة ; https://en.wiktionary.org/wiki/عادة |

These are exact candidate rows from `completed/languages/workbooks/v1.0/arabic/arabic_vocabulary_1000.csv`.

## Urdu — 23 additional whole-row clears

| Rank | Target | Candidate gloss/form | Classification | Reference |
|---:|---|---|---|---|
| 24 | `لئے` | taken; for (in `کے لیے`) | `CONFIRMED_VALID_FORM_AND_COMPOUND_POSTPOSITION` | Rekhta: https://www.rekhtadictionary.com/meaning-of-liye |
| 37 | `تھے` | were, masculine plural/honorific | `CONFIRMED_VALID_AUXILIARY_FORM` | Michigan State University Basic Urdu, past tense of “to be”: https://urdu.lrc.columbia.edu/grammar/verb-to-be/ |
| 54 | `زیادہ` | more/much/a lot; excessive/excessively | `CONFIRMED_VALID_LEXICAL_SENSE` | Rekhta: https://www.rekhtadictionary.com/meaning-of-ziyaada |
| 103 | `استعمال` | use/usage/utilisation/employment | `CONFIRMED_VALID_LEXICAL_SENSE` | Rekhta: https://www.rekhtadictionary.com/meaning-of-istemaal |
| 185 | `بار` | time/turn/occasion/instance/occurrence | `CONFIRMED_VALID_LEXICAL_SENSE` | Rekhta: https://www.rekhtadictionary.com/meaning-of-baar |
| 189 | `نظام` | system/order; institution/foundation/network sense | `CONFIRMED_VALID_POLYSEMY` | Rekhta: https://www.rekhtadictionary.com/meaning-of-nizaam |
| 191 | `کبھی` | ever/sometime/sometimes; never with negation | `CONFIRMED_VALID_CONTEXTUAL_ADVERB` | Rekhta: https://www.rekhtadictionary.com/meaning-of-kabhii |
| 202 | `نئی` | new, feminine | `CONFIRMED_VALID_INFLECTED_FORM` | Rekhta: https://www.rekhtadictionary.com/meaning-of-naii |
| 225 | `پہلی` | first, feminine | `CONFIRMED_VALID_INFLECTED_FORM` | Rekhta: https://www.rekhtadictionary.com/meaning-of-pahlii |
| 240 | `حل` | solution/resolution | `CONFIRMED_VALID_LEXICAL_SENSE` | Rekhta: https://www.rekhtadictionary.com/meaning-of-hal |
| 321 | `دس` | ten | `CONFIRMED_VALID_NUMERAL` | Rekhta: https://www.rekhtadictionary.com/meaning-of-das |
| 334 | `سات` | seven | `CONFIRMED_VALID_NUMERAL` | Rekhta: https://www.rekhtadictionary.com/meaning-of-saat |
| 347 | `واضح` | evident/manifest/clear/apparent; elaborate/detailed sense | `CONFIRMED_VALID_LEXICAL_SENSE` | Rekhta: https://www.rekhtadictionary.com/meaning-of-vaazeh |
| 414 | `دنوں` | days, oblique plural | `CONFIRMED_VALID_INFLECTED_FORM` | Rekhta/standard inflection from `دن`: https://www.rekhtadictionary.com/meaning-of-dinon |
| 579 | `رن` | run, especially cricket/sports | `CONFIRMED_VALID_LOANWORD_SENSE` | Cambridge English–Urdu Dictionary: https://dictionary.cambridge.org/dictionary/english-urdu/run |
| 604 | `کاروبار` | occupation/business/trade | `CONFIRMED_VALID_LEXICAL_SENSE` | Rekhta: https://www.rekhtadictionary.com/meaning-of-kaarobaar |
| 627 | `قوت` | food/sustenance; strength/power/force depending on origin/vocalization | `CONFIRMED_VALID_UNDIACRITIZED_POLYSEMY` | Rekhta: https://www.rekhtadictionary.com/meaning-of-quut ; https://www.rekhtadictionary.com/meaning-of-quvvat |
| 637 | `شہروں` | cities, oblique plural | `CONFIRMED_VALID_INFLECTED_FORM` | Standard inflection of `شہر`; Urdu lexical evidence: https://www.rekhtadictionary.com/meaning-of-shahr |
| 664 | `مجھ` | me, oblique form used before postpositions | `CONFIRMED_VALID_PRONOMINAL_FORM` | Rekhta: https://www.rekhtadictionary.com/meaning-of-mujh |
| 682 | `مسئلے` | problems/issues; singular oblique/vocative depending on context | `CONFIRMED_VALID_INFLECTED_FORM` | Rekhta: https://www.rekhtadictionary.com/meaning-of-masle |
| 759 | `کاشت` | cultivation/agriculture | `CONFIRMED_VALID_LEXICAL_SENSE` | Rekhta: https://www.rekhtadictionary.com/meaning-of-kaasht |
| 795 | `تیسرے` | third, masculine plural/oblique | `CONFIRMED_VALID_INFLECTED_FORM` | Standard inflection of `تیسرا`; Rekhta: https://www.rekhtadictionary.com/meaning-of-tiisraa |
| 818 | `بل` | force/might/power | `CONFIRMED_VALID_LEXICAL_SENSE` | Rekhta: https://www.rekhtadictionary.com/meaning-of-bal |

These are exact candidate rows from `completed/languages/workbooks/v1.0/urdu/urdu_vocabulary_1000.csv`.

## Deliberately left unresolved

The conservative whole-row rule leaves the following examples unresolved rather than stretching a partial reference match:

### French
- `déjà` (#143): ordinary “already/before” is clear, but the candidate also includes discourse senses (“for a start/firstly; again after a question”) that need cleaner whole-row support.
- `salle` (#517): room/hall is clear; standalone “gym” is contextual (`salle de sport`).
- `situation` (#608): `situation (all meanings)` is too broad to certify usefully.
- `cool` (#623): modern adjective uses are clear; the candidate's interjection `cool! great!` should remain human-reviewable.
- `bosser` (#837): informal “to work” is clear; the secondary `emboss/dent` gloss needs better exact support.
- Remaining French sentence rows with pronoun/antecedent or naturalness questions remain for focused review.

### Arabic
- `ما` (#347): exclamative `ما أفعل` analysis is plausible but was not given a sufficiently clean whole-row authority in this pass.
- `ألم` (#536): `أَلَم` = pain is secure; the candidate also encodes the segmented interrogative `أَ + لَمْ` (“did ... not?”), so the unvocalized whole row remains human-reviewable.
- `جاري` (#842): `جارِي` (“my neighbor”) and `جارٍ/جاري` current/ongoing readings are plausible, but a cleaner exact whole-row authority is preferred.
- Seven remaining Arabic sentence-level flags remain focused human-review items.

### Urdu
- `سی` (#70): the feminine resemblance/comparative form is standard, but this pass did not use the weaker web grammar hit as sufficient whole-row authority.
- `طور` (#71): state/condition and manner/way are supported, but the candidate's generic `hill, mount` gloss is broader than the clean exact lexical support found (which points particularly to Mount Sinai in one sense).
- `فیصل` (#495): a common male name in real-world use, but the strongest exact lexical entry retrieved foregrounds adjective/noun meanings rather than cleanly certifying the proper-name gloss used in the candidate.

## Result

This second vocabulary reference pass adds **36** documented whole-row clears:

- French: **3**
- Arabic: **10**
- Urdu: **23**

Combined with the earlier post-audit notes' **99** documented low-priority/false-positive rows, **135 of the original 162 strongest flags** now have a documented machine/reference reason to be deprioritized.

Remaining focused strongest-flag set: **27 rows**

- French: **14**
- Arabic: **10**
- Urdu: **3**

This is prioritization evidence only. It does not alter the preserved original audit result, certify any language, change a human sign-off requirement, or modify learner-facing content.