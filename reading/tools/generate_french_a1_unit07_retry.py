#!/usr/bin/env python3
"""Retry Unit 07 using validated lemma `droit` for reader-facing surface `droite`."""
from __future__ import annotations
import generate_french_a1_unit07 as base

_original_lexicon = base.lexicon
_original_build = base.build

def lexicon():
    L = _original_lexicon()
    if 'droite' in L:
        raise AssertionError('Unexpected standalone droite source entry; remove alias and use direct source')
    if 'droit' not in L:
        raise AssertionError('Validated french_top1000.csv contains neither droite nor required lemma droit')
    L['droite'] = dict(L['droit'])
    return L

def build(rows, L):
    unit = _original_build(rows, L)
    hits=[]
    for row in unit:
        for target in row.get('new_lexical_targets',[]):
            if target.get('form') == 'droite':
                target['lemma'] = 'droit'
                target['source_lookup_form'] = 'droit'
                hits.append((row['id'], target['id'], target['source_rank']))
    if len(hits) != 1:
        raise AssertionError(f'expected exactly one droite/droit target, got {hits}')
    return unit

base.lexicon = lexicon
base.build = build
base.main()
