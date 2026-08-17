#!/usr/bin/env python3
"""Fail-closed Unit04 wrapper repairing exact review-form visibility."""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b2_unit04.py')
ns={'__name__':'unit04_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
specs=ns['SPECS']
if [s['id'] for s in specs] != [f'fr-b2-u04-p{i:02d}' for i in range(1,6)]:raise AssertionError('unexpected Unit04 structure')
# Exact prior-target forms required in running text.
specs[1]['paragraphs'][3] += " La ville doit pouvoir refuser une exception qui ne correspond à aucun besoin lié à l’accès."
specs[2]['paragraphs'][3] += " Le vrai test du projet reste donc son fonctionnement dans plusieurs situations, pas seulement son image."
specs[3]['paragraphs'][1] += " Une victime d’un mauvais parcours serait ici une personne effectivement empêchée d’atteindre le service, pas une catégorie abstraite."
# Preflight question target forms are local before base.qa resolves IDs.
off=[]
for s in specs:
 local=set(s['forms'])|set(s['reviews'])
 for i,item in enumerate(s['items'],1):
  bad=[f for f in item[3] if f not in local]
  if bad:off.append((s['id'],i,bad))
cp=ns['CHECKPOINT'];local=set(ns['FORMS'])
for i,item in enumerate(cp['items'],1):
 bad=[f for f in item[3] if f not in local]
 if bad:off.append((cp['id'],i,bad))
if off:raise AssertionError(f'Unit04 preflight non-local targets: {off}')
ns['main']()
