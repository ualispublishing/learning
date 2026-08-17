#!/usr/bin/env python3
"""Fail-closed Unit02 retry: add exact lemma visibility caught by strict guards."""
from pathlib import Path

p = Path(__file__).with_name('generate_french_b2_unit02_retry4.py')
src = p.read_text(encoding='utf-8')
anchor = "p3 = specs[2]"
if src.count(anchor) != 1:
    raise AssertionError(f'unexpected retry4 repair anchor count: {src.count(anchor)}')
insert = '''p4 = specs[3]\np4['paragraphs'][3] += " Cette règle permet de préférer une option pour des raisons explicites plutôt que par intuition seule."\np5 = specs[4]\np5['paragraphs'][3] += " Pour valoir comme explication, une observation doit résister à cette comparaison plus contrôlée."\n\np3 = specs[2]'''
src = src.replace(anchor, insert)
code = compile(src, str(p), 'exec')
ns = {'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code, ns)
