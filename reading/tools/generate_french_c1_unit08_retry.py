#!/usr/bin/env python3
"""Quality preflight for C1 Unit08: deepen forecast reasoning when needed."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c1_unit08.py'
ns={'__name__':'c1_u08_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
ns['EXTRA']=list(ns['EXTRA'])+[
"Le rapport décompose également l’erreur de prévision. Une estimation peut être fausse parce que le niveau de départ était mal mesuré, parce qu’un paramètre a changé, parce que la dispersion a été sous-estimée ou parce qu’un événement extérieur a rompu la relation historique. Ces erreurs n’appellent pas la même correction : recalibrer un niveau, réviser un mécanisme et élargir un intervalle sont trois réponses distinctes.",
"La valeur d’une information supplémentaire dépend enfin de la décision qu’elle pourrait modifier. Attendre une donnée plus précise n’est utile que si cette donnée a une chance raisonnable d’inverser le choix ou d’en réduire un risque important avant l’échéance. Le texte formule donc une condition d’arrêt : lorsque l’information attendue ne changerait plus l’action de manière proportionnée à son coût, retarder davantage devient lui-même une décision coûteuse."
]
ns['main']()
