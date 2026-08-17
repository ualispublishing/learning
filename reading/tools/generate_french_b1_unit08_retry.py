#!/usr/bin/env python3
"""Retry Unit 08 with only a natural checkpoint length repair."""
from pathlib import Path
p=Path(__file__).with_name('generate_french_b1_unit08.py')
src=p.read_text(encoding='utf-8')
needle='"Les acquis précédents restent utiles : préparer un projet entier, charger le matériel doucement, organiser une opération qui peut reposer sur le bord observé, reconnaître une blague sans tout deviner quand quelqu’un veut plaisanter, permettre à une classe d’essayer un second plan intelligent, puis distinguer ce qui peut naître, survivre et rester debout. Camille comprend maintenant que corriger une action ne suffit pas : il faut aussi conserver le raisonnement qui explique pourquoi on a choisi de régler, diriger, remarquer, couvrir ou revoir ce qui avait échappé au plan."'
replacement='"Les acquis précédents restent utiles : préparer un projet entier, charger le matériel doucement, organiser une opération qui peut reposer sur le bord observé, reconnaître une blague sans tout deviner quand quelqu’un veut plaisanter, permettre à une classe d’essayer un second plan intelligent, puis distinguer ce qui peut naître, survivre et rester debout. Camille comprend maintenant que corriger une action ne suffit pas : il faut aussi conserver le raisonnement qui explique pourquoi on a choisi de régler, diriger, remarquer, couvrir ou revoir ce qui avait échappé au plan. Cette trace rend les décisions comparables et permet à une autre personne de vérifier le chemin suivi avant de proposer une nouvelle correction."'
if src.count(needle)!=1: raise AssertionError(f'expected one checkpoint paragraph, found {src.count(needle)}')
src=src.replace(needle,replacement)
code=compile(src,str(p),'exec'); ns={'__name__':'__main__','__file__':str(p),'__package__':None}; exec(code,ns)
