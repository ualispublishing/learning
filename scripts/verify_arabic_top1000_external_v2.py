#!/usr/bin/env python3
"""Compatibility wrapper for the Arabic external semantic verifier.

Some Wn releases expose Synset.id/pos/ili as properties while others expose one
or more as zero-argument callables. The underlying verifier should not care.
"""
from __future__ import annotations

from collections import defaultdict

import verify_arabic_top1000_external as base
import wn


def value(obj, name):
    attr = getattr(obj, name, None)
    return attr() if callable(attr) else attr


def build_awn_index():
    arb = wn.Wordnet("omw-arb:2.0")
    eng = wn.Wordnet("oewn:2025")
    idx = defaultdict(list)
    for word in arb.words():
        form = base.undiac(word.lemma())
        if form:
            idx[form].extend(word.synsets())
    for spelling, syns in list(idx.items()):
        seen = set()
        unique = []
        for syn in syns:
            sid = value(syn, "id")
            if sid not in seen:
                seen.add(sid)
                unique.append(syn)
        idx[spelling] = unique
    return idx, eng


def awn_evidence(front: str, meaning: str, pos: str, idx, eng) -> dict:
    syns = idx.get(front, [])
    if not syns:
        return {"exists": False, "pos_support": False, "semantic_support": False,
                "score": 0.0, "hits": "", "synsets": 0}

    expected = base.canonical_pos(pos)
    wn_pos_map = {"noun": "n", "verb": "v", "adjective": "a", "adverb": "r"}
    expected_wn = {wn_pos_map[p] for p in expected if p in wn_pos_map}
    syn_pos = [value(s, "pos") for s in syns]
    pos_support = (not expected_wn) or any(
        p in expected_wn or (p == "s" and "a" in expected_wn) for p in syn_pos
    )

    evidence_parts = []
    for syn in syns:
        definition = syn.definition()
        if definition:
            evidence_parts.append(definition)
        ili = value(syn, "ili")
        if ili:
            for es in eng.synsets(ili=ili):
                evidence_parts.extend(es.lemmas())
                definition = es.definition()
                if definition:
                    evidence_parts.append(definition)

    evidence = " ; ".join(evidence_parts)
    sem, score, hits = base.semantic_overlap(meaning, evidence)
    return {
        "exists": True,
        "pos_support": pos_support,
        "semantic_support": sem,
        "score": score,
        "hits": hits,
        "synsets": len(syns),
    }


base.build_awn_index = build_awn_index
base.awn_evidence = awn_evidence

if __name__ == "__main__":
    base.main()
