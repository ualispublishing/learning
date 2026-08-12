#!/usr/bin/env python3
"""Third-pass learner-facing semantic precision for French/Urdu core1000.

French policy:
- preserve rank/front inventory;
- lock high-frequency grammatical words to conservative learner meanings;
- retain a legacy learner gloss only when every slash/semicolon sense is
  independently corroborated by the freshly downloaded Kaikki evidence;
- likewise reject an uncorroborated FreeDict gloss so Kaikki becomes the safe
  fallback instead of allowing stale/archaic English to perpetuate itself;
- apply narrow manual overrides for known learner-facing failures.

Urdu keeps the v2 multi-source policy plus a few narrow learner-sense cleanups.
"""
from __future__ import annotations

import csv
import re

import refine_french_urdu_candidate_meanings_v2 as v2

# Conservative locks for grammatical/high-frequency French entries where a
# lexicographic source may describe usage rather than give the learner translation.
v2.base.FRENCH_SAFE.update({
    "de": "of; from",
    "je": "I",
    "pas": "not; step",
    "que": "that; what; than",
    "vous": "you (plural or formal singular)",
    "tu": "you (informal singular)",
    "et": "and",
    "il": "he; it",
    "un": "a; an; one",
    "en": "in; of it; some; from there (pronoun/adverb uses)",
    "on": "one; we; people; they (indefinite subject pronoun)",
    "ce": "this; that; it",
    "pour": "for; to; in order to",
    "qui": "who; which; that",
    "mais": "but; however",
    "nous": "we; us",
    "dans": "in; into",
    "elle": "she; it (feminine)",
    "bien": "well; good; quite; indeed",
    "me": "me; myself",
    "si": "if; whether; so; yes (replying to a negative question)",
    "non": "no; not",
    "avec": "with",
    "devoir": "must; have to; owe; duty",
    "plus": "more; most; no more (with negation)",
    "la": "the (feminine singular); her; it",
    "les": "the (plural); them",
    "des": "of the; from the; some (plural article)",
    "à": "to; at; in",
    "au": "to the; at the; in the (à + le)",
    "aux": "to the; at the; in the (plural; à + les)",
    "ne": "not (first part of standard French negation)",
    "se": "oneself; himself; herself; themselves (reflexive pronoun)",
    "y": "there; to it; in it",
    "lui": "him; her; to him; to her",
    "leur": "their; to them",
    "par": "by; through; per",
    "sur": "on; upon; about",
    "sans": "without",

    # Learner-facing lexical repairs discovered in the source/evidence sweep.
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
    "année": "year",
    "vieux": "old; elderly; old man (noun use)",
    "ensemble": "together; set; ensemble",
    "prêt": "ready; loan (noun)",
})

# Remove distracting letter-name side senses from ordinary high-frequency Urdu
# verb/particle cards where the lexical/corpus reading is the learner target.
v2.base.URDU_SAFE.update({
    "سی": "like; as; -like (feminine comparative/resemblance form)",
    "آ": "come; come! (stem/imperative of آنا)",
    "آئی": "came (feminine singular)",
})

_WORD = re.compile(r"[a-z]+(?:'[a-z]+)?", re.I)
_STOP = {
    "a", "an", "the", "to", "of", "and", "or", "for", "as", "be", "is", "are",
    "was", "were", "with", "by", "from", "that", "which", "who", "whom", "this",
    "these", "those", "it", "he", "she", "they", "you", "i", "we", "one",
}


def _tokens(text: str) -> set[str]:
    out = {t.lower() for t in _WORD.findall(text or "") if t.lower() not in _STOP}
    expanded = set(out)
    for t in list(out):
        if len(t) > 4 and t.endswith("ies"):
            expanded.add(t[:-3] + "y")
        if len(t) > 4 and t.endswith("es"):
            expanded.add(t[:-2])
        if len(t) > 3 and t.endswith("s"):
            expanded.add(t[:-1])
        if len(t) > 5 and t.endswith("ing"):
            expanded.add(t[:-3])
        if len(t) > 4 and t.endswith("ed"):
            expanded.add(t[:-2])
    return expanded


def _all_senses_supported(gloss: str, evidence: str) -> bool:
    """Require each legacy/FreeDict slash-or-semicolon sense to touch Kaikki evidence."""
    ev = _tokens(evidence)
    if not ev:
        return False
    pieces = [p.strip() for p in re.split(r"\s*(?:;|/)\s*", gloss or "") if p.strip()]
    if not pieces:
        return False
    for piece in pieces:
        pt = _tokens(piece)
        if not pt:
            return False
        if not (pt & ev):
            return False
    return True


def _fresh_french_kaikki() -> dict[str, str]:
    path = v2.base.AUDIT / "french_core1000_candidate_evidence.csv"
    try:
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        return {}
    return {
        v2.base.norm_fr(r.get("front", "")): (r.get("kaikki_meaning", "") or "").strip()
        for r in rows if r.get("front")
    }


_ORIG_LEGACY_MAP = v2.base.legacy_map
_ORIG_FREEDICT_MAP = v2.base.freedict_map


def _precision_legacy_map(path, normalizer):
    data = _ORIG_LEGACY_MAP(path, normalizer)
    if normalizer is not v2.base.norm_fr:
        return data
    evidence = _fresh_french_kaikki()
    safe = v2.base.FRENCH_SAFE
    out = {}
    for word, gloss in data.items():
        if word in safe or _all_senses_supported(gloss, evidence.get(word, "")):
            out[word] = gloss
    return out


def _precision_freedict_map(path, targets):
    data = _ORIG_FREEDICT_MAP(path, targets)
    evidence = _fresh_french_kaikki()
    return {
        word: gloss for word, gloss in data.items()
        if _all_senses_supported(gloss, evidence.get(word, ""))
    }


v2.base.legacy_map = _precision_legacy_map
v2.base.freedict_map = _precision_freedict_map

if __name__ == "__main__":
    v2.base.main()
