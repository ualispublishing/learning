#!/usr/bin/env python3
"""Retry B2 Unit 01 after fail-closed exact-form and local-target findings.

Repairs only exact `général` exposure and one stale P03 target tag in a P05
assessment. The 20-word calibration pool and all validation guards remain.
"""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b2_unit01.py')
src=p.read_text(encoding='utf-8')
old="une carte très intéressante peut donner tort au lecteur qui suppose que chaque zone a été observée de la même façon."
new="un portrait général très intéressant peut donner tort au lecteur qui suppose que chaque zone a été observée de la même façon."
if src.count(old)!=1: raise AssertionError(f'expected one general-exposure location, found {src.count(old)}')
src=src.replace(old,new)
old_tag="('assumption','Qu’est-ce qui doit être vrai pour que la procédure vaille l’effort ?','Elle doit apporter une information ou une compréhension utile qui justifie son coût de validation et de gestion.',['valoir','apporter'])"
new_tag="('assumption','Qu’est-ce qui doit être vrai pour que la procédure vaille l’effort ?','Elle doit apporter une information ou une compréhension utile qui justifie son coût de validation et de gestion.',['valoir'])"
if src.count(old_tag)!=1: raise AssertionError(f'expected one stale P05 apporter tag, found {src.count(old_tag)}')
src=src.replace(old_tag,new_tag)
code=compile(src,str(p),'exec');ns={'__name__':'__main__','__file__':str(p),'__package__':None};exec(code,ns)
