#!/usr/bin/env python3
"""Final learner-semantic lock: all 1,000 Arabic meanings are explicit/reviewed."""
import rebuild_arabic_top1000_learner_safe_v3 as v3

v3.v2.MANUAL.update({
    33: "want; desire; intend",
    270: "type; kind; form",
    500: "speech; statement; remark; talk; saying",
    550: "results; consequences",
    660: "success",
    770: "faster; fastest; hasten; hurry",
    785: "petroleum; oil",
    793: "lower; lowest; underneath",
    798: "sleep",
    852: "medical treatment; therapy; processing",
})

v3.v2.POS_OVERRIDE.update({
    33: "verb",
    270: "noun",
    500: "noun",
    550: "noun",
    660: "noun",
    770: "comparative adjective / verb",
    785: "noun",
    793: "adjective / adverb",
    798: "noun",
    852: "noun",
})

if __name__ == "__main__":
    v3.v2.main()
