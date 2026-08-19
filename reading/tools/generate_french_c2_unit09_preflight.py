#!/usr/bin/env python3
"""Quality-depth preflight for French C2 Unit09."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c2_unit09.py'
ns={'__name__':'c2_u09_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
ns['EXTRA']=list(ns['EXTRA'])+[
 "Le checkpoint ajoute une carte des dommages distributifs. Une amélioration moyenne peut masquer un petit groupe qui supporte presque tout le coût, ou au contraire une dégradation légère mais très répandue. Le lecteur décrit donc séparément gravité, fréquence, concentration et possibilité de réparation avant d’agréger les effets dans une seule conclusion.",
 "Une seconde tâche construit un plan de retour en arrière concret. Il faut identifier les dépendances créées par le nouveau service, les données qui devraient être restaurées, les personnes à prévenir et le délai maximal acceptable. Une mesure dite réversible ne l’est réellement que si les moyens matériels, organisationnels et décisionnels de revenir en arrière existent encore au moment où ils deviennent nécessaires.",
 "Le dossier teste aussi la dérive après déploiement. Les entrées peuvent changer, les usagers peuvent apprendre à contourner une règle et les responsables peuvent étendre progressivement la finalité initiale. Le lecteur choisit donc quelques observations sentinelles capables de révéler qu’un résultat ancien ne décrit plus correctement le fonctionnement présent.",
 "Enfin, la recommandation doit nommer un risque résiduel. Aucun contrôle raisonnable ne supprime toutes les erreurs; l’enjeu est de dire quel risque demeure après les protections, pourquoi il est accepté provisoirement et quelle nouvelle information rendrait cet arbitrage inacceptable. Cette étape empêche le mot sécurité de fonctionner comme une promesse absolue."
]
ns['main']()
