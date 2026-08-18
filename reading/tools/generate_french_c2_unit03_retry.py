#!/usr/bin/env python3
"""Quality preflight for C2 Unit03: deepen zero-new epistemology checkpoint when short."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c2_unit03.py'
ns={'__name__':'c2_u03_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
ns['EXTRA']=list(ns['EXTRA'])+[
"Le dossier traite aussi le cas où le test théoriquement décisif n’est pas encore accessible. Plutôt que de choisir arbitrairement un modèle, l’analyse distingue les prédictions observables déjà communes, les engagements qui restent sous-déterminés et les développements instrumentaux qui rendraient un futur test discriminant possible. Une limite actuelle devient ainsi une propriété de l’état de connaissance, non une conclusion définitive sur l’impossibilité de départager les modèles.",
"Une décomposition des erreurs complète cette comparaison. Un écart entre modèle et observation peut venir de la mesure, d’un paramètre mal estimé, d’une idéalisation qui cesse d’être tolérable ou d’un mécanisme absent. Attribuer automatiquement tout résidu au mécanisme principal protégerait le modèle contre la critique; l’analyse cherche donc quel type d’erreur chaque hypothèse prédit et quelles corrections devraient améliorer la performance si elle est vraie.",
"Le checkpoint examine enfin l’usage décisionnel. Deux modèles théoriquement différents peuvent conduire à la même action dans la plage actuelle des données, puis diverger lorsque le coût d’une erreur augmente ou qu’une condition sort du domaine de calibration. La décision peut alors exiger une marge de sécurité avant que le débat ontologique soit résolu. Cette prudence pratique n’équivaut ni à confirmer l’un des modèles ni à déclarer leur différence sans importance."
]
ns['main']()
