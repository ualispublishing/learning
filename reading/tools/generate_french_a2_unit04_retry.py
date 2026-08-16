#!/usr/bin/env python3
"""Retry French A2 Unit 04 with exact-form visibility for the P02 `perdre` review."""
from __future__ import annotations
import generate_french_a2_unit04 as base

_orig_specs = base.specs

def specs():
    rows = _orig_specs()
    p02 = next(r for r in rows if r['id'] == 'fr-a2-u04-p02')
    old = "La responsable lui conseille de ne pas chercher partout en même temps."
    new = "La responsable lui conseille de ne pas chercher partout en même temps, car il peut perdre encore plus de temps."
    if old not in p02['text']:
        raise AssertionError('P02 retry anchor drift')
    p02['text'] = p02['text'].replace(old, new, 1)
    return rows

base.specs = specs
base.main()
