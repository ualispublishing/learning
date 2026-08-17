#!/usr/bin/env python3
"""Fail-closed preflight wrapper for French B2 Unit06.

Repairs stale checkpoint target tags, verifies all assessment target forms are
locally declared and the paired-opinion link is intact, then delegates to the
original guarded main(). This is the authoritative Unit06 workflow trigger.
"""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b2_unit06.py')
ns={'__name__':'unit06_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
specs=ns['SPECS']; cp=ns['CHECKPOINT']; pair=ns['PAIR']
if [s['id'] for s in specs] != [f'fr-b2-u06-p{i:02d}' for i in range(1,6)]:
    raise AssertionError('unexpected Unit06 spec structure')
if specs[2].get('pair') != pair or specs[3].get('pair') != pair:
    raise AssertionError('Unit06 paired-opinion metadata drift')
if any(specs[i].get('pair') is not None for i in (0,1,4)) or cp.get('pair') is not None:
    raise AssertionError('unexpected paired-text membership outside P03/P04')

# P06 is a zero-new checkpoint whose declared review set is the 20 Unit06
# forms. Three questions accidentally retained Unit05 target tags; remap them
# to the Unit06 concepts actually assessed by the prompts/answers.
fixed=[]; repaired=0
for typ,prompt,answer,targets in cp['items']:
    if prompt == 'Quelle position la synthèse adopte-t-elle envers une formule générale de confidentialité ?':
        if targets != ['croire','comprendre']:
            raise AssertionError(f'unexpected P06 q7 targets: {targets}')
        targets=['client','bureau']; repaired+=1
    elif prompt == 'Pourquoi « cacher » et « montrer » sont-ils opposés ?':
        if targets != ['cacher','montrer']:
            raise AssertionError(f'unexpected P06 q8 targets: {targets}')
        targets=['cacher','connaître']; repaired+=1
    elif prompt == 'Comment le temps intervient-il dans la confidentialité ?':
        if targets != ['rester','devenir','continuer']:
            raise AssertionError(f'unexpected P06 q9 targets: {targets}')
        targets=['suivre','connaître']; repaired+=1
    fixed.append((typ,prompt,answer,targets))
if repaired != 3:
    raise AssertionError(f'expected three checkpoint linkage repairs, found {repaired}')
cp['items']=fixed

# Narrow learner-facing wording cleanup without changing target semantics.
specs[1]['paragraphs'][1]=specs[1]['paragraphs'][1].replace(
    'Une personne peut changer de situation, de nom ou de préférence;',
    'La situation, le nom utilisé publiquement ou les préférences d’une personne peuvent changer;'
)

offenders=[]
for s in specs:
    local=set(s['forms'])|set(s['reviews'])
    for i,item in enumerate(s['items'],1):
        bad=[f for f in item[3] if f not in local]
        if bad: offenders.append((s['id'],i,bad))
cp_local=set(ns['FORMS'])
for i,item in enumerate(cp['items'],1):
    bad=[f for f in item[3] if f not in cp_local]
    if bad: offenders.append((cp['id'],i,bad))
if offenders:
    raise AssertionError(f'Unit06 preflight non-local target forms: {offenders}')

ns['main']()
