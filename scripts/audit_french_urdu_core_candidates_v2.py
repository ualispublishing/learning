#!/usr/bin/env python3
"""Run the French/Urdu semantic audit with function-word-aware agreement.

The base auditor intentionally removes English stopwords for ordinary lexical
comparison. That is wrong for cards whose *entire meaning* is a function word
(`et` = `and`, `de` = `of/from`, `je` = `I`, `être` = `to be`). This wrapper
adds an exact/near-exact sense comparison for short meanings, while retaining the
more conservative content-word overlap for normal lexical entries.
"""
from __future__ import annotations

import re
import unicodedata

import audit_french_urdu_core_candidates as base

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
    # Articles around a lexical head do not matter for very short dictionary senses.
    if len(tokens) > 1 and tokens[0] in {"a", "an", "the"}:
        tokens = tokens[1:]
    return " ".join(tokens)


def short_senses(text: str) -> list[str]:
    return [canonical_sense(p) for p in SPLIT_RE.split(text or "") if canonical_sense(p)]


def agree_v2(a: str, b: str) -> tuple[bool, str]:
    # First retain the base auditor's conservative content-word comparison.
    ok, terms = base.agree(a, b)
    if ok:
        return ok, terms

    a_senses = short_senses(a)
    b_senses = short_senses(b)
    exact = sorted(set(a_senses) & set(b_senses))
    if exact:
        return True, "|".join(exact[:12])

    # Handle infinitival/function variants such as `to be` vs `be`, and tiny
    # closed-class glosses such as `of/from`, `and`, `I`, `who/which/that`.
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

    # Finally allow a single identical closed-class semantic atom only when that
    # atom constitutes a complete short sense on both sides. This avoids treating
    # incidental stopword overlap inside long definitions as semantic agreement.
    a_atoms = {s for s in ar if len(s.split()) == 1}
    b_atoms = {s for s in br if len(s.split()) == 1}
    atom_overlap = sorted(a_atoms & b_atoms)
    if atom_overlap:
        return True, "|".join(atom_overlap[:12])

    return False, ""


base.agree = agree_v2

if __name__ == "__main__":
    base.main()
