#!/usr/bin/env python3
"""Third-pass learner-facing semantic precision overrides for French/Urdu core1000.

This layer keeps the v2 reviewed exception set, then tightens entries that are
lexically valid but still poor or misleading for a learner. Rank and inventory
are unchanged.
"""
import refine_french_urdu_candidate_meanings_v2 as v2

v2.base.FRENCH_SAFE.update({
    "chose": "thing; matter; something; affair",
    "derrière": "behind; rear; back; backside",
    "presque": "almost; nearly",
    "gentil": "kind; nice; gentle; sweet",
    "service": "service; department; duty; favor; set (of dishes/cutlery)",
    "moyen": "means; way; method; average; medium; middle",
    "lieu": "place; location; site",
    "coucher": "to put to bed; lie down; go to bed; sleep; bedding",
    "enlever": "to remove; take off; take away; kidnap/abduct",
    "abandonner": "to abandon; leave; give up; quit",
    "seigneur": "lord; nobleman; seigneur",
    "gamin": "kid; boy; child; mischievous child (informal)",
    "relation": "relationship; relation; connection; account/report",
    "complètement": "completely; entirely; fully",
    "mignon": "cute; pretty; charming; lovely",
    "gueule": "mouth/muzzle; face (informal); gob/mug (informal)",
    "debout": "standing; upright; up; on one's feet",
    "expérience": "experience; experiment",
    "attaque": "attack; assault; aggression",
    "terrible": "terrible; dreadful; awful; severe/intense",
    "profiter": "to benefit; take advantage of; enjoy; profit from",
    "époque": "era; period; age",
    "merveilleux": "wonderful; marvelous; marvellous",
    "recommencer": "to restart; start again; begin again; do again",
    "lycée": "high school; secondary school; lycée",
    "programme": "program; programme; schedule; plan",
    "noir": "black; dark; Black person (noun use)",
})

# Remove distracting letter-name side senses from ordinary high-frequency Urdu
# verb/particle cards where the lexical/corpus reading is the learner target.
v2.base.URDU_SAFE.update({
    "سی": "like; as; -like (feminine comparative/resemblance form)",
    "آ": "come; come! (stem/imperative of آنا)",
    "آئی": "came (feminine singular)",
})

if __name__ == "__main__":
    v2.base.main()
