#!/usr/bin/env python3
"""Quality preflight for C1 Unit09: deepen historiographical source reasoning."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c1_unit09.py'
ns={'__name__':'c1_u09_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
ns['EXTRA']=list(ns['EXTRA'])+[
"Le dossier examine également la dépendance entre sources. Deux récits qui répètent la même formulation ne constituent pas forcément deux confirmations indépendantes si l’un a copié l’autre ou si tous deux reposent sur un bulletin commun. La corroboration devient plus forte lorsque la convergence vient de chaînes d’information réellement distinctes.",
"L’absence d’un fait dans une source est traitée avec la même prudence. Un silence devient informatif seulement si le document aurait normalement dû enregistrer l’événement en question. Ne pas trouver une mention dans une archive qui ne collectait jamais ce type d’information ne constitue pas une preuve solide de l’absence historique du phénomène."
]
ns['main']()
