#!/usr/bin/env python3
"""Final learner-semantic lock plus externally verified Arabic corrections."""
import rebuild_arabic_top1000_learner_safe_v3 as v3

# Preserve rank/order while normalizing learner-facing forms where independent
# lexical evidence shows the source/extracted spelling or form-sense pairing is unsafe.
v3.v2.final.FINAL_REPAIRS.update({
    209: "نسوة",
    292: "ألا",
    353: "هؤلاء",
    389: "إسلامي",
})

v3.v2.MANUAL.update({
    33: "want; desire; intend",
    209: "women; group of women",
    270: "type; kind; form",
    292: "attention/emphasis particle; also unvocalized form of أَلَّا 'that not'",
    353: "these",
    389: "Islamic",
    500: "speech; statement; remark; talk; saying",
    550: "results; consequences",
    646: "judgment; ruling; judiciary; judicial authority; fulfillment/performance",
    660: "success",
    770: "faster; fastest; hasten; hurry",
    785: "petroleum; oil",
    793: "lower; lowest; underneath",
    798: "sleep",
    852: "medical treatment; therapy; processing",
})

v3.v2.POS_OVERRIDE.update({
    33: "verb",
    209: "collective noun / plural noun",
    270: "noun",
    292: "particle",
    353: "demonstrative pronoun",
    389: "adjective",
    500: "noun",
    550: "noun",
    646: "noun / verbal noun",
    660: "noun",
    770: "comparative adjective / verb",
    785: "noun",
    793: "adjective / adverb",
    798: "noun",
    852: "noun",
})

if __name__ == "__main__":
    v3.v2.main()
