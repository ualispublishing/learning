#!/usr/bin/env python3
"""Retry B1 Unit 01 with corrected paths and calibration-length reinforcement."""
from pathlib import Path
import generate_french_b1_unit01 as base

REPO=Path(__file__).resolve().parents[2]
base.A1=REPO/'reading'/'french'/'a1'/'passages.jsonl'
base.A2=REPO/'reading'/'french'/'a2'/'passages.jsonl'
base.CANON=REPO/'reading'/'french'/'b1'/'passages.jsonl'
base.SCHEMA=REPO/'reading'/'schema'/'passage.schema.json'

SUPPLEMENTS={
'fr-b1-u01-p01':" Elle note également les questions qui restent ouvertes afin de ne pas confondre une absence de document avec une absence d’événement. Cette distinction lui servira lorsqu’elle présentera ses conclusions au groupe.",
'fr-b1-u01-p02':" Avant de partir, les participants inscrivent les points encore discutés sur un tableau commun. Cette liste permettra de comparer les nouvelles réponses sans faire comme si le désaccord avait déjà disparu.",
'fr-b1-u01-p03':" Les élèves ajoutent finalement une courte note technique sous la vidéo. Elle précise quelle modification a produit quel effet, afin que le public puisse suivre le raisonnement au lieu de voir seulement le résultat final.",
'fr-b1-u01-p04':" Camille ajoute cette question à son carnet : quelles personnes ne sont pas encore visibles dans l’exposition ? Elle veut la conserver pour une prochaine visite plutôt que chercher une réponse immédiate.",
'fr-b1-u01-p05':" Elle décide enfin de montrer une page de son carnet où deux pistes sont barrées. Le public verra ainsi que sélectionner une méthode implique aussi de renoncer à certaines possibilités.",
'fr-b1-u01-p06':" Ce bilan lui donne aussi une méthode pour les prochains projets : distinguer ce qui est certain, ce qui reste probable et ce qui doit encore être vérifié avant de devenir une conclusion."
}
for spec in base.SPECS:
    spec['paragraphs'][-1]+=SUPPLEMENTS[spec['id']]
base.CHECKPOINT['paragraphs'][-1]+=SUPPLEMENTS['fr-b1-u01-p06']

base.main()
