#!/usr/bin/env python3
"""Fail-closed repair wrapper for French B2 Unit05.

Repairs local linkage, exact target/review visibility and learner-facing French
while preserving the verified target pool and every base generation guard.
"""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b2_unit05.py')
ns={'__name__':'unit05_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
specs=ns['SPECS']; cp=ns['CHECKPOINT']
if [s['id'] for s in specs] != [f'fr-b2-u05-p{i:02d}' for i in range(1,6)]:
    raise AssertionError('unexpected Unit05 spec structure')

p1=specs[0]; fixed=[]; seen=0
for typ,prompt,answer,targets in p1['items']:
    if prompt == 'Quelle hypothèse soutient l’idée qu’une série plus longue renforce une conclusion ?':
        if targets != ['long','année']: raise AssertionError(f'unexpected P01 q6 targets: {targets}')
        targets=['année','mois']; seen+=1
    fixed.append((typ,prompt,answer,targets))
if seen != 1: raise AssertionError(f'expected one P01 linkage repair, found {seen}')
p1['items']=fixed
p1['paragraphs'][1] += " De l’autre côté de la comparaison, les variations nocturnes peuvent raconter une histoire différente."
p1['paragraphs'][3]=p1['paragraphs'][3].replace("comparer chaque côté du temps disponible aide à savoir jusqu’où on peut généraliser.","comparer plusieurs périodes disponibles aide à savoir jusqu’où on peut généraliser.")

p2=specs[1]
p2['paragraphs']=[x.replace('ce qui a changer','ce qui a changé') for x in p2['paragraphs']]
p2['paragraphs'][0] += " Un intervalle long permet davantage de comparaisons, sans transformer une tendance en certitude."
p2['paragraphs'][2] += " Dans cet exemple, un accès proche de l’école reste pertinent seulement s’il répond à un besoin défini."
p2['items']=[(typ,prompt,answer.replace('ce qui a changer','ce qui a changé'),targets) for typ,prompt,answer,targets in p2['items']]

p3=specs[2]; fixed=[]
for typ,prompt,answer,targets in p3['items']:
    if prompt == 'Quelle distinction centrale organise le rapport ?': answer=answer.replace('Compter et montrer un signal décrit sa robustesse','Compter et montrer un signal décrivent sa robustesse')
    fixed.append((typ,prompt,answer,targets))
p3['items']=fixed

p4=specs[3]
p4['paragraphs']=[x.replace('une valeur moyenne plus haut sur le graphique','une valeur moyenne plus haute sur le graphique').replace('une valeur plus bas ne signifie','une valeur plus basse ne signifie') for x in p4['paragraphs']]

cp['paragraphs']=[x.replace('ce qui a changer','ce qui a changé') for x in cp['paragraphs']]
cp['paragraphs'][3] += " Cette discipline exige aussi de dire à l’avance quelles observations feraient changer la conclusion. Un horizon long ne garantit rien à lui seul, mais il permet de confronter davantage de situations. Une décision devient ainsi vérifiable : on sait ce qui la soutient aujourd’hui, quels seuils la feraient évoluer et pourquoi une révision future resterait cohérente avec le raisonnement initial."
cp['items']=[(typ,prompt,answer.replace('ce qui a changer','ce qui a changé'),targets) for typ,prompt,answer,targets in cp['items']]

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
if offenders: raise AssertionError(f'Unit05 preflight non-local target forms: {offenders}')

ns['main']()
