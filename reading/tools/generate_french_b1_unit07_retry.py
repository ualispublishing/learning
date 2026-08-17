#!/usr/bin/env python3
"""Retry B1 Unit 07 after fail-closed checkpoint/review findings.

Repairs only the stale prior-unit checkpoint tag and exact running-text review
visibility for `souhaiter`; no target-set or validation guard changes.
"""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b1_unit07.py')
src=p.read_text(encoding='utf-8')
old="('motive','Pourquoi Camille conserve-t-elle les méthodes de l’unité précédente ?','Parce qu’elles l’aident à vérifier les conditions et les preuves avant de corriger une décision.',['surveiller','prévoir'])"
new="('motive','Pourquoi Camille conserve-t-elle les méthodes de l’unité précédente ?','Parce qu’elles l’aident à vérifier les conditions et les preuves avant de corriger une décision.',[])"
if src.count(old)!=1: raise AssertionError(f'expected one stale checkpoint tag, found {src.count(old)}')
src=src.replace(old,new)
needle="Les élèves mesurent l’ombre, observent le sol et notent les interventions déjà réalisées. Ils souhaitent que le parc reste accueillant, mais ils comprennent qu’un souhait doit être relié à des observations."
replacement="Les élèves mesurent l’ombre, observent le sol et notent les interventions déjà réalisées. Chacun peut souhaiter que le parc reste accueillant, mais ils comprennent qu’un souhait doit être relié à des observations."
if src.count(needle)!=1: raise AssertionError(f'expected one P05 souhaiter location, found {src.count(needle)}')
src=src.replace(needle,replacement)
code=compile(src,str(p),'exec'); ns={'__name__':'__main__','__file__':str(p),'__package__':None}; exec(code,ns)
