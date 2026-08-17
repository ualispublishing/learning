#!/usr/bin/env python3
"""Fail-closed repair wrapper for French B2 Unit05.

Repairs one non-local assessment tag, exact visibility of one Unit04 review form,
and two learner-facing passé-composé typos while preserving the verified target
pool and all base guards. This file is the authoritative Unit05 retry trigger.
"""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b2_unit05.py')
ns={'__name__':'unit05_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
specs=ns['SPECS']; cp=ns['CHECKPOINT']
if [s['id'] for s in specs] != [f'fr-b2-u05-p{i:02d}' for i in range(1,6)]:
    raise AssertionError('unexpected Unit05 spec structure')

# P01: `long` belongs to P02, so q6 must only reference locally declared targets.
p1=specs[0]; fixed=[]; seen=0
for typ,prompt,answer,targets in p1['items']:
    if prompt == 'Quelle hypothèse soutient l’idée qu’une série plus longue renforce une conclusion ?':
        if targets != ['long','année']:
            raise AssertionError(f'unexpected P01 q6 targets: {targets}')
        targets=['année','mois']; seen+=1
    fixed.append((typ,prompt,answer,targets))
if seen != 1: raise AssertionError(f'expected one P01 linkage repair, found {seen}')
p1['items']=fixed

# P02: standard French participle in learner-facing prose and answer, while
# retaining several exact infinitive `changer` exposures elsewhere.
p2=specs[1]
p2['paragraphs']=[x.replace('ce qui a changer', 'ce qui a changé') for x in p2['paragraphs']]
fixed=[]
for typ,prompt,answer,targets in p2['items']:
    answer=answer.replace('ce qui a changer', 'ce qui a changé')
    fixed.append((typ,prompt,answer,targets))
p2['items']=fixed
# Exact Unit04 review form `proche` must be visible in running text.
p2['paragraphs'][2] += " Dans cet exemple, un accès proche de l’école reste pertinent seulement s’il répond à un besoin défini."

# P06: same passé-composé repair; exact `changer` remains in "faire changer".
cp['paragraphs']=[x.replace('ce qui a changer', 'ce qui a changé') for x in cp['paragraphs']]
fixed=[]
for typ,prompt,answer,targets in cp['items']:
    answer=answer.replace('ce qui a changer', 'ce qui a changé')
    fixed.append((typ,prompt,answer,targets))
cp['items']=fixed

# Preflight every assessment target form before base.qa resolves IDs.
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
    raise AssertionError(f'Unit05 preflight non-local target forms: {offenders}')

ns['main']()
