#!/usr/bin/env python3
"""Quality preflight for C1 Unit06; only adds substantive interpretive depth when short."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c1_unit06.py'
ns={'__name__':'c1_u06_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
base_extra=list(ns['EXTRA'])
ns['EXTRA']=base_extra+[
"Le dossier précise aussi qui porte la charge de justifier une mesure lorsqu’elle restreint fortement la situation d’une personne. Cette charge ne signifie pas qu’une seule partie doit prouver chaque détail; elle oblige surtout l’institution qui agit à rendre visibles les faits, la règle et le lien qui autorise la conséquence choisie.",
"Une erreur institutionnelle n’est pas traitée comme une simple imperfection administrative lorsque ses effets persistent. La voie de correction doit indiquer qui peut demander un nouvel examen, quelles informations peuvent être ajoutées et comment une décision corrigée modifie concrètement la restriction antérieure."
]
ns['main']()
