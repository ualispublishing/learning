#!/usr/bin/env python3
"""Final explicit exception layer for the Arabic Top-1000 learner-safe rebuild."""
import rebuild_arabic_top1000_learner_safe_v2 as v2

v2.MANUAL.update({
    88: "many; much; a lot",
    172: "small; little; young",
    219: "beautiful; nice",
    236: "look!; see!",
    249: "different; various",
    314: "bigger; larger; greatest; largest",
    346: "higher; highest; upper",
    361: "go!",
    389: "Islamic",
    429: "listen!; hear!",
    459: "many; numerous",
    568: "trustworthy; honest; faithful",
    604: "bad; poor",
    878: "bad; poor (feminine)",
    898: "dead",
    924: "do!; act!",
})

v2.POS_OVERRIDE.update({
    88: "adjective / quantifying adjective",
    172: "adjective",
    219: "adjective",
    236: "imperative verb",
    249: "adjective",
    314: "comparative/superlative adjective",
    346: "comparative/superlative adjective",
    361: "imperative verb",
    389: "adjective",
    429: "imperative verb",
    459: "quantifier / adjective",
    568: "adjective",
    604: "adjective",
    878: "adjective",
    898: "adjective",
    924: "imperative verb",
})

if __name__ == "__main__":
    v2.main()
