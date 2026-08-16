#!/usr/bin/env python3
"""Retry French A2 Unit 07 with fresh `tenter` replacing already-deliberate `gauche`."""
from __future__ import annotations
import generate_french_a2_unit07 as base

base.FORMS=("tenter","tranquille","déjeuner","partager","vue","avancer","marché","poste","intérêt","mur")

p01=next(r for r in base.SPECS if r["id"]=="fr-a2-u07-p01")
p01["title"]="Tenter un chemin plus tranquille"
p01["topics"]=["route choice","city walking","calm route"]
p01["forms"]=["tenter","tranquille"]
p01["text"]="""Après le voyage de la semaine précédente, Camille et Sami arrivent dans une ville voisine pour une activité scolaire. Leur train entre en gare à l’heure, mais le groupe doit encore marcher jusqu’au centre culturel. L’application de la professeure propose une grande avenue très animée. Camille remarque aussi une petite rue qui semble plus tranquille. La professeure demande au groupe s’il veut tenter de passer par cette rue, car il reste assez de temps avant l’activité. Les élèves acceptent de tenter ce chemin et vérifient les noms des rues sur la carte. Après quelques minutes, ils découvrent des travaux devant eux, mais un panneau indique un passage pour les piétons. Ils peuvent donc continuer sans revenir à la gare. Camille comprend que tenter un itinéraire différent ne signifie pas avancer au hasard : il faut observer les repères et garder une solution de retour. Le voyage continue calmement, et le groupe arrive au centre culturel avant le début de la visite."""
p01["grammar"]=[{"id":"fr-a2-u07-tenter-de","role":"new","description":"use tenter de + infinitive to describe trying a practical alternative"}]
p01["discourse"]=[{"id":"fr-a2-u07-route-choice","role":"new","description":"compare a main route with a quieter alternative and verify the result"}]
p01["items"]=[
("gist","Quelle solution différente le groupe essaie-t-il ?","Il tente de passer par une rue plus tranquille.",["tenter","tranquille"]),
("literal_detail","Quel moyen de transport amène le groupe en ville ?","Le train.",["train"]),
("sequence","Que font les élèves après avoir choisi la petite rue ?","Ils vérifient les noms des rues sur la carte.",[]),
("cause_effect","Pourquoi peuvent-ils tenter un autre chemin ?","Parce qu’il reste assez de temps avant l’activité.",["tenter"]),
("vocabulary_in_context","Que signifie « tenter » ici ?","Essayer une solution sans savoir encore exactement quel sera le résultat.",["tenter"]),
("vocabulary_in_context","Que signifie « tranquille » ici ?","Calme et peu agité.",["tranquille"]),
("reference_resolution","Dans « ils découvrent des travaux », qui sont « ils » ?","Les élèves du groupe.",[]),
("inference","Pourquoi Camille dit-elle qu’il ne faut pas avancer au hasard ?","Parce qu’une autre route doit quand même être vérifiée avec des repères.",["tenter"]),
("cloze_transfer","Complète : Nous pouvons _____ de prendre une autre rue.","tenter",["tenter"]),
("cloze_transfer","Complète : Cette petite rue est calme et _____.","tranquille",["tranquille"])
]

p06=base.CHECKPOINT
p06["text"]="""Lors d’une sortie en ville, Camille apprend à combiner orientation, temps libre et services pratiques. Après le train, elle peut tenter de suivre une rue tranquille quand la carte montre une solution claire. Au moment du déjeuner, elle peut partager un plat avec Sami tout en surveillant l’heure du départ. Depuis la chambre de l’hôtel, elle observe une belle vue, puis elle rejoint le groupe pour avancer ensemble. Avant le retour, elle passe au marché pour acheter un petit objet et accompagne Sami à la poste. Plus tard, son intérêt pour une peinture sur un mur lui donne envie de s’arrêter quelques minutes. Elle vérifie pourtant le plan avant de prolonger la visite, car le groupe doit encore prendre un avion. Camille comprend ainsi qu’une journée réussie ne dépend pas seulement de la vitesse : il faut savoir tenter une solution raisonnable, avancer avec les autres, choisir un endroit tranquille, partager le temps et garder assez de marge pour les étapes importantes."""
p06["items"]=[
("gist","Quelles compétences Camille combine-t-elle pendant la sortie ?","Elle combine l’orientation, la gestion du temps et l’utilisation de services pratiques.",[]),
("literal_detail","Quelle solution peut-elle tenter après le train ?","Elle peut tenter de suivre une rue tranquille.",["tenter","tranquille"]),
("sequence","Que fait-elle avant de passer au marché et à la poste ?","Elle observe une vue puis avance avec le groupe.",["vue","avancer","marché","poste"]),
("cause_effect","Pourquoi vérifie-t-elle le plan avant de prolonger la visite ?","Parce que le groupe doit encore prendre un avion.",[]),
("vocabulary_in_context","Quels mots décrivent le repas et l’action de le prendre ensemble ?","déjeuner et partager",["déjeuner","partager"]),
("vocabulary_in_context","Quels mots désignent le lieu de vente et le service postal ?","marché et poste",["marché","poste"]),
("reference_resolution","Dans « son intérêt », à qui renvoie « son » ?","À Camille.",["intérêt"]),
("inference","Pourquoi une rue tranquille peut-elle être utile pendant cette sortie ?","Parce qu’elle peut rendre le déplacement plus simple et moins agité.",["tranquille"]),
("cloze_transfer","Complète : Une peinture couvre le _____.","mur",["mur"]),
("summary","Résume la stratégie de Camille en une phrase.","Elle tente des solutions raisonnables, avance avec le groupe, utilise les services utiles et protège le temps nécessaire aux étapes importantes.",["tenter","avancer"])
]

base.main()
