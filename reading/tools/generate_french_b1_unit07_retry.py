#!/usr/bin/env python3
"""Retry B1 Unit 07 after a stale prior-unit checkpoint target tag failed closed."""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b1_unit07.py')
src=p.read_text(encoding='utf-8')
old="('motive','Pourquoi Camille conserve-t-elle les méthodes de l’unité précédente ?','Parce qu’elles l’aident à vérifier les conditions et les preuves avant de corriger une décision.',['surveiller','prévoir'])"
new="('motive','Pourquoi Camille conserve-t-elle les méthodes de l’unité précédente ?','Parce qu’elles l’aident à vérifier les conditions et les preuves avant de corriger une décision.',[])"
if src.count(old)!=1: raise AssertionError(f'expected one stale checkpoint tag, found {src.count(old)}')
src=src.replace(old,new)
code=compile(src,str(p),'exec'); ns={'__name__':'__main__','__file__':str(p),'__package__':None}; exec(code,ns)
