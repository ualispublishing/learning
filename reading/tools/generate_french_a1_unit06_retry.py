#!/usr/bin/env python3
"""Retry Unit 06 after making the P05 `enfant` review visibly singular in prose."""
from __future__ import annotations
import re
import generate_french_a1_unit06 as base

_original_build = base.build

def build(rows, lex):
    unit = _original_build(rows, lex)
    p05 = next(r for r in unit if r['id'] == 'fr-a1-u06-p05')
    old = 'D’autres enfants arrivent bientôt avec leurs parents.'
    new = 'Un enfant arrive bientôt avec son père, puis d’autres enfants arrivent avec leurs parents.'
    if p05['text'].count(old) != 1:
        raise AssertionError('Unit 06 P05 retry source sentence drift')
    p05['text'] = p05['text'].replace(old, new)
    p05['word_count'] = len(p05['text'].split())
    p05['sentence_count'] = max(1, len(re.findall(r'[.!?](?:[»”"])?', p05['text'])))
    if base.count_form(p05['text'], 'enfant') != 1:
        raise AssertionError('Unit 06 P05 singular enfant review is not exactly visible once')
    return unit

base.build = build
base.main()
