#!/usr/bin/env python3
"""Final explicit-review resolution layer for French/Urdu core1000."""
import refine_french_urdu_candidate_meanings_v3 as v3

# Rows isolated by the stricter independent semantic audit. Meanings are concise,
# learner-facing resolutions of ordinary contemporary senses; rank/front inventory
# is unchanged.
v3.v2.base.FRENCH_SAFE.update({
    "ils": "they (masculine or mixed group)",
    "toi": "you; yourself (informal singular, stressed/disjunctive form)",
    "ou": "or",
    "falloir": "to be necessary; must; have to (impersonal verb)",
    "notre": "our",
    "quelqu'un": "someone; somebody",
    "mourir": "to die",
    "chez": "at/to the home, place, or business of; among; in the work of",
    "depuis": "since; for (a duration); from",
    "voilà": "there is/are; there it is; here it is",
    "cela": "that",
    "beau": "beautiful; handsome; fine; nice",
    "ah": "ah!",
    "elles": "they (feminine)",
    "tant": "so much; so many; as much; as many",
    "contre": "against; versus; in exchange for",
    "sous": "under; below; beneath",
    "dont": "whose; of whom; of which; including",
    "papa": "dad; father",
    "dessus": "on top; above; on it; top",
    "ignorer": "to not know; be unaware of; ignore",
    "d'abord": "first; first of all; initially",
    "ceci": "this",
    "couper": "to cut; cut off; switch off; interrupt",
    "tromper": "to deceive; mislead; be mistaken; cheat on",
    "patron": "boss; employer; owner/manager; pattern/template",
    "reprendre": "to take back; resume; start again; retake",
    "cheveu": "hair; a single hair",
    "autour": "around; surrounding",
    "selon": "according to; depending on; in accordance with",
    "enfuir": "to flee; run away; escape (usually s'enfuir)",
    "coincer": "to jam; get stuck; trap; wedge",
    "nul": "no; none; worthless/lousy; draw/tie",
    "bande": "band; group; strip; tape",
})

v3.v2.base.URDU_SAFE.update({
    "ساتھ": "with; together; alongside",
    "کام": "work; task; job; use",
    "پہلے": "before; earlier; first; previously",
    "دوسرے": "second; other (plural/oblique form)",
    "سامنے": "in front of; facing; opposite",
    "درمیان": "between; middle; midst",
    "یہی": "this very; this same; exactly this",
    "اندر": "inside; in; within",
    "نیچے": "below; under; down",
})

if __name__ == "__main__":
    v3.v2.base.main()
