#!/usr/bin/env python3
"""Fail-closed repair wrapper for French B2 Unit03.

Keeps the original guarded generator intact while repairing one non-local
question target and one exact review-form visibility issue found during review.
"""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b2_unit03.py')
src=p.read_text(encoding='utf-8')
ns={'__name__':'unit03_base','__file__':str(p),'__package__':None}
exec(compile(src,str(p),'exec'),ns)

specs=ns['SPECS']
if [s['id'] for s in specs] != [f'fr-b2-u03-p{i:02d}' for i in range(1,6)]:
    raise AssertionError('unexpected Unit03 spec structure')

# P02: remove accidental later-passage target `aider`; keep the same answer
# semantics while linking only locally declared Unit03/Unit02 review targets.
p2=specs[1]
fixed=[];seen=0
for typ,prompt,answer,targets in p2['items']:
    if prompt == 'Quelle position le texte adopte-t-il envers l’autorité scolaire ?':
        if targets != ['aider','obliger']:
            raise AssertionError(f'unexpected P02 target shape: {targets}')
        targets=['permettre','obliger']
        seen+=1
    fixed.append((typ,prompt,answer,targets))
if seen!=1: raise AssertionError(f'expected one P02 linkage repair, found {seen}')
p2['items']=fixed

# P04: exact running-text review form required by the established guard.
p4=specs[3]
p4['paragraphs'][3] += " Le comité explique pourquoi préférer une règle révisable ne signifie pas hésiter sans fin."

# Preflight local question targets before the original generator constructs IDs.
off=[]
for s in specs:
    local=set(s['forms'])|set(s['reviews'])
    for i,item in enumerate(s['items'],1):
        bad=[f for f in item[3] if f not in local]
        if bad: off.append((s['id'],i,bad))
cp=ns['CHECKPOINT']; cp_local=set(ns['FORMS'])
for i,item in enumerate(cp['items'],1):
    bad=[f for f in item[3] if f not in cp_local]
    if bad: off.append((cp['id'],i,bad))
if off: raise AssertionError(f'Unit03 preflight non-local target forms: {off}')

ns['main']()
