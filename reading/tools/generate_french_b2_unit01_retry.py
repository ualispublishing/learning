#!/usr/bin/env python3
"""Retry B2 Unit 01 after exact-form `général` exposure failed closed."""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b2_unit01.py')
src=p.read_text(encoding='utf-8')
old="une carte très intéressante peut donner tort au lecteur qui suppose que chaque zone a été observée de la même façon."
new="un portrait général très intéressant peut donner tort au lecteur qui suppose que chaque zone a été observée de la même façon."
if src.count(old)!=1: raise AssertionError(f'expected one general-exposure location, found {src.count(old)}')
src=src.replace(old,new)
code=compile(src,str(p),'exec');ns={'__name__':'__main__','__file__':str(p),'__package__':None};exec(code,ns)
