#!/usr/bin/env python3
"""Quality preflight for C2 Unit02: deepen the synthesis checkpoint when short."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c2_unit02.py'
ns={'__name__':'c2_u02_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
ns['EXTRA']=list(ns['EXTRA'])+[
"Le dossier ajoute un conflit entre deux principes d’interprétation qui coïncident dans les cas ordinaires. L’un privilégie la formulation la plus spécifique; l’autre privilégie la lecture qui évite de rendre une garantie voisine pratiquement inutile. Le lecteur doit montrer pourquoi aucun principe ne fonctionne comme une commande automatique et quelle propriété du cas donne ici davantage de poids à l’un qu’à l’autre.",
"La synthèse distingue aussi le droit invoqué du remède choisi. Reconnaître qu’une règle a été mal appliquée ne détermine pas encore s’il faut annuler, corriger, recommencer la procédure ou seulement modifier l’avenir. Le remède doit répondre au type d’erreur, à ses conséquences et à la possibilité de rétablir la situation sans créer un avantage sans rapport avec la violation constatée.",
"Enfin, le texte compare correction rétrospective et changement prospectif. Une nouvelle interprétation peut être justifiée tout en soulevant une question distincte sur les décisions anciennes prises de bonne foi sous la règle précédente. L’analyse annonce alors les coûts d’erreur dans les deux directions, les attentes créées et le critère qui détermine jusqu’où la nouvelle lecture doit remonter."
]
ns['main']()
