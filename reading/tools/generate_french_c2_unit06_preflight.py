#!/usr/bin/env python3
"""Quality-depth preflight for French C2 Unit06."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
p = HERE / 'generate_french_c2_unit06.py'
ns = {'__name__': 'c2_u06_base', '__file__': str(p), '__package__': None}
exec(compile(p.read_text(encoding='utf-8'), str(p), 'exec'), ns)

# Extend the cumulative checkpoint with genuine institutional-analysis tasks.
# fit() remains strict at 700–1200 words; these are used only if needed.
ns['EXTRA'] = list(ns['EXTRA']) + [
    "Le checkpoint ajoute une matrice de recours. Pour chaque décision, le lecteur distingue une erreur de fait, une erreur de procédure, une incohérence avec la règle et un désaccord sur l’objectif. Il précise ensuite quel acteur possède l’information ou l’autorité nécessaire pour corriger chaque type d’erreur. Cette cartographie évite de supposer qu’un même mécanisme de contrôle convient à toutes les défaillances.",
    "Une autre tâche compare représentativité et qualité délibérative. Un dispositif peut recueillir beaucoup de réponses brèves alors qu’un autre permet à un groupe plus petit de confronter des raisons. Le lecteur ne choisit pas abstraitement entre quantité et profondeur : il relie la méthode à la question posée, puis indique quelle information supplémentaire serait nécessaire pour généraliser au-delà des participants observés.",
    "Le dossier examine aussi la responsabilité documentaire. Une décision peut être traçable sans que chaque document soit public, ou publique sans que l’enchaînement entre preuve et conclusion soit facile à reconstruire. Le lecteur décrit quelles traces sont nécessaires pour attribuer une action, vérifier une justification et corriger une erreur, tout en reconnaissant les limites légitimes liées à la confidentialité du scénario.",
    "Enfin, une comparaison temporelle oppose résultat immédiat et capacité future. Une règle qui améliore rapidement un indicateur peut réduire la marge d’adaptation, tandis qu’une procédure plus coûteuse aujourd’hui peut préserver une possibilité de correction. Le lecteur reformule alors le compromis avec un horizon explicite et refuse de présenter comme universelle une conclusion qui dépend de la durée retenue."
]

ns['main']()
