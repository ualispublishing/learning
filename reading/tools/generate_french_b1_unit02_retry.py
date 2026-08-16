#!/usr/bin/env python3
"""Retry B1 Unit 02 after two pre-canonical generator repairs.

Repairs are deliberately narrow: one malformed comprehension bracket and one
checkpoint question that accidentally tagged prior-unit `impliquer` even though
P06 declares only Unit02 summary targets. No canonical or root-lexicon guard is
weakened.
"""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b1_unit02.py')
src=p.read_text(encoding='utf-8')

bad="ids={t['form']:t['id'] for t in reviews]"
good="ids={t['form']:t['id'] for t in reviews}"
if src.count(bad)!=1:
    raise AssertionError(f'expected exactly one known bracket typo, found {src.count(bad)}')
src=src.replace(bad,good)

old="('motive','Pourquoi Camille continue-t-elle à demander ce qu’un choix peut impliquer ?','Pour anticiper les conséquences avant d’agir et éviter une décision fondée seulement sur l’apparence.',['impliquer']),"
new="('motive','Pourquoi Camille continue-t-elle à demander ce qu’un choix peut impliquer ?','Pour anticiper les conséquences avant d’agir et éviter une décision fondée seulement sur l’apparence.',[]),"
if src.count(old)!=1:
    raise AssertionError(f'expected exactly one known checkpoint target-tag issue, found {src.count(old)}')
src=src.replace(old,new)

code=compile(src,str(p),'exec')
ns={'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code,ns)
