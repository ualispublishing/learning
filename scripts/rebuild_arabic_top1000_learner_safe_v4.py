#!/usr/bin/env python3
"""Final learner-semantic lock plus externally verified Arabic corrections."""
import rebuild_arabic_top1000_learner_safe_v3 as v3

# Preserve rank/order while normalizing learner-facing forms where independent
# lexical evidence and the published POS/vocalization show the source extraction
# or form-sense pairing is unsafe.
v3.v2.final.FINAL_REPAIRS.update({
    209: "نسوة",
    292: "ألا",
    296: "لاعب",
    353: "هؤلاء",
    389: "إسلامي",
    479: "سلام",
    489: "مساء",
    724: "أهلا",
    766: "سلامة",
})

v3.v2.MANUAL.update({
    33: "want; desire; intend",
    209: "women; group of women",
    270: "type; kind; form",
    292: "attention/emphasis particle; also unvocalized form of أَلَّا 'that not'",
    296: "player; sport/game player",
    336: "as for; whereas; as regards (أَمَّا)",
    353: "these",
    389: "Islamic",
    403: "family; people; inhabitants; people of",
    423: "opposite; counterpart; in exchange for; versus",
    479: "peace; greeting; salutation",
    489: "evening; in the evening",
    500: "speech; statement; remark; talk; saying",
    506: "control; regulation; adjustment; controlled; adjusted",
    550: "results; consequences",
    643: "harm; hardship; might; strength; often in لا بأس = no problem/not bad",
    646: "judgment; ruling; judiciary; judicial authority; fulfillment/performance",
    660: "success",
    724: "welcome!; hello! (أهلًا)",
    732: "is truthful; tells the truth; proves true",
    766: "safety; soundness; well-being",
    770: "faster; fastest; hasten; hurry",
    785: "petroleum; oil",
    793: "lower; lowest; underneath",
    798: "sleep",
    852: "medical treatment; therapy; processing",
    943: "kisses; is kissing (يُقَبِّل)",
    999: "interview; meeting; encounter; confrontation",
})

v3.v2.POS_OVERRIDE.update({
    33: "verb",
    209: "collective noun / plural noun",
    270: "noun",
    292: "particle",
    296: "noun / active participle",
    336: "particle",
    353: "demonstrative pronoun",
    389: "adjective",
    403: "noun",
    423: "noun / relational expression",
    479: "noun",
    489: "adverb / noun used adverbially",
    500: "noun",
    506: "noun / verb",
    550: "noun",
    643: "noun",
    646: "noun / verbal noun",
    660: "noun",
    724: "greeting expression / noun used adverbially",
    732: "verb",
    766: "noun",
    770: "comparative adjective / verb",
    785: "noun",
    793: "adjective / adverb",
    798: "noun",
    852: "noun",
    943: "verb",
    999: "noun / verbal noun",
})

if __name__ == "__main__":
    v3.v2.main()
