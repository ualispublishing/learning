#!/usr/bin/env python3
"""Run the French/Urdu semantic audit with function-word-aware agreement."""
from __future__ import annotations

import re
import unicodedata

import audit_french_urdu_core_candidates as base

BASE_AGREE = base.agree
RAW_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*", re.I)
SPLIT_RE = re.compile(r"\s*(?:;|/|\||,(?!\s*(?:which|who|that|when|where)))\s*")


def raw_tokens(text: str) -> list[str]:
    vals = []
    for token in RAW_WORD_RE.findall(unicodedata.normalize("NFKC", text or "").lower()):
        token = token.strip("'-")
        if token:
            vals.append(token)
    return vals


def canonical_sense(text: str) -> str:
    tokens = raw_tokens(text)
    if len(tokens) > 1 and tokens[0] in {"a", "an", "the"}:
        tokens = tokens[1:]
    return " ".join(tokens)


def short_senses(text: str) -> list[str]:
    return [canonical_sense(p) for p in SPLIT_RE.split(text or "") if canonical_sense(p)]


def agree_v2(a: str, b: str) -> tuple[bool, str]:
    ok, terms = BASE_AGREE(a, b)
    if ok:
        return ok, terms

    a_senses = short_senses(a)
    b_senses = short_senses(b)
    exact = sorted(set(a_senses) & set(b_senses))
    if exact:
        return True, "|".join(exact[:12])

    def reduced(s: str) -> str:
        toks = s.split()
        if toks and toks[0] == "to" and len(toks) == 2:
            return toks[1]
        return s

    ar = {reduced(s) for s in a_senses if len(s.split()) <= 4}
    br = {reduced(s) for s in b_senses if len(s.split()) <= 4}
    overlap = sorted(ar & br)
    if overlap:
        return True, "|".join(overlap[:12])

    a_atoms = {s for s in ar if len(s.split()) == 1}
    b_atoms = {s for s in br if len(s.split()) == 1}
    atom_overlap = sorted(a_atoms & b_atoms)
    if atom_overlap:
        return True, "|".join(atom_overlap[:12])

    return False, ""


base.agree = agree_v2

if __name__ == "__main__":
    base.main()
