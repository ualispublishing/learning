#!/usr/bin/env python3
"""Fail-closed preflight wrapper for French B2 Unit07; repaired canonical workflow trigger."""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b2_unit07.py')
ns={'__name__':'unit07_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
specs=ns['SPECS'];cp=ns['CHECKPOINT']
if [s['id'] for s in specs] != [f'fr-b2-u07-p{i:02d}' for i in range(1,6)]:raise AssertionError('unexpected Unit07 structure')
fixed=[];repaired=0
for typ,prompt,answer,targets in cp['items']:
 if prompt == 'Pourquoi le fait de vendre une création ne décide-t-il pas de sa valeur critique ?':
  if targets != ['vendre','sujet']:raise AssertionError(f'unexpected P06 market-context targets: {targets}')
  targets=['avis','sujet'];repaired+=1
 fixed.append((typ,prompt,answer,targets))
if repaired!=1:raise AssertionError(f'expected one Unit07 checkpoint repair, found {repaired}')
cp['items']=fixed
# P03 was five words below the B2 minimum. Add substantive revision logic.
specs[2]['paragraphs'][3] += " Une lecture rigoureuse indique aussi quel indice contraire pourrait l’obliger à revoir son interprétation au lieu de protéger sa première impression."
# Exact deliberate review lemma for the checkpoint; `belle` alone is not enough.
cp['paragraphs'][1] += " Le beau peut être un critère explicite, mais il doit encore être relié à des propriétés observables plutôt que traité comme une preuve en soi."
off=[]
for s in specs:
 local=set(s['forms'])|set(s['reviews'])
 for i,item in enumerate(s['items'],1):
  bad=[f for f in item[3] if f not in local]
  if bad:off.append((s['id'],i,bad))
local=set(ns['FORMS'])
for i,item in enumerate(cp['items'],1):
 bad=[f for f in item[3] if f not in local]
 if bad:off.append((cp['id'],i,bad))
if off:raise AssertionError(f'Unit07 preflight non-local target forms: {off}')
ns['main']()
