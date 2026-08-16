#!/usr/bin/env python3
"""Retry Unit 06 with fresh `visite` replacing already-deliberate `place`."""
from __future__ import annotations
import generate_french_a2_unit06 as base

base.FORMS=("voyage","train","route","départ","hôtel","chambre","retour","visite","plan","avion")

p04=next(r for r in base.DATA['specs'] if r['id']=='fr-a2-u06-p04')
p04['title']='Une visite avant le retour'
p04['topics']=['return','visit','schedule change']
p04['forms']=['retour','visite']
p04['text']='''Le dernier matin, Camille et sa mère apprennent que leur train de retour partira beaucoup plus tard que prévu. Comme il n’y a aucune urgence, elles décident d’utiliser ce temps pour une courte visite dans un musée proche de la gare. Sa mère propose de choisir l’exposition avec soin afin de ne pas aller trop loin. Camille vérifie l’heure du retour, la durée de la visite et le temps nécessaire pour revenir à la gare. Elles laissent leurs sacs à la consigne, entrent dans le musée et regardent seulement deux salles. Une heure plus tard, Camille reçoit une notification : le train gardera finalement son nouvel horaire. Elles terminent donc la visite comme prévu et reviennent tranquillement à la gare. Camille comprend qu’un changement de retour n’oblige pas toujours à attendre sans rien faire. Avec assez de temps et des informations claires, on peut adapter le programme, profiter d’une visite courte et revenir avant le départ sans transformer un simple changement d’horaire en problème.'''
p04['grammar']=[{'id':'fr-a2-u06-afin-de','role':'new','description':'use afin de + infinitive to express a practical purpose'}]
p04['discourse']=[{'id':'fr-a2-u06-use-delay','role':'new','description':'adapt a return schedule by evaluating time for a short visit'}]
p04['items']=[
 ('gist','Que font Camille et sa mère pendant le retard du train ?','Elles font une courte visite dans un musée.',['visite']),
 ('literal_detail','Pourquoi choisissent-elles un musée proche ?','Pour pouvoir revenir facilement à la gare.',['retour']),
 ('sequence','Que vérifie Camille avant d’entrer au musée ?','L’heure du retour, la durée de la visite et le temps pour revenir.',['retour','visite']),
 ('cause_effect','Pourquoi ne se précipitent-elles pas ?','Parce qu’il n’y a pas d’urgence et qu’elles ont le temps de choisir avec soin.',['soin','urgence']),
 ('vocabulary_in_context','Que signifie « retour » ici ?','Le trajet pour revenir à la maison.',['retour']),
 ('vocabulary_in_context','Que signifie « visite » ?','Le fait d’aller voir un lieu pendant un temps limité.',['visite']),
 ('reference_resolution','Dans « elles laissent leurs sacs », qui sont « elles » ?','Camille et sa mère.',[]),
 ('inference','Pourquoi ne regardent-elles que deux salles ?','Pour que la visite reste assez courte avant le train.',['visite']),
 ('cloze_transfer','Complète : Notre _____ est prévu dimanche soir.','retour',['retour']),
 ('cloze_transfer','Complète : Nous faisons une _____ du musée.','visite',['visite'])
]

p06=base.DATA['checkpoint']
p06['text']='''Pour organiser un déplacement, Camille commence par définir le voyage et choisir le moyen de transport. Si elle prend le train, elle vérifie l’heure, le quai et les informations utiles avant le départ. Quand plusieurs chemins sont possibles, elle compare la route la plus courte avec celle qui convient le mieux à la situation. Si elle passe une nuit ailleurs, elle confirme le nom de l’hôtel et le numéro de la chambre. Elle prépare aussi le retour au lieu de penser seulement à l’aller et garde parfois du temps pour une visite courte. Pour un trajet plus long en avion, elle construit un plan avec assez de temps pour les documents et les déplacements entre les étapes. Camille sait qu’un bon plan ne garantit pas que tout se passera exactement comme prévu. Il sert surtout à rendre les décisions plus simples quand un horaire change, qu’une visite doit être raccourcie ou qu’une autre route devient nécessaire.'''
p06['items']=[
 ('gist','Quelle stratégie générale Camille utilise-t-elle pour voyager ?','Elle prépare les étapes importantes et garde la possibilité d’adapter son plan.',[]),
 ('literal_detail','Que vérifie-t-elle avant le départ d’un train ?','L’heure, le quai et les informations utiles.',['train','départ']),
 ('sequence','Que prépare-t-elle en plus du trajet aller ?','Le retour.',['retour']),
 ('cause_effect','Pourquoi laisse-t-elle du temps dans son plan ?','Pour gérer plus facilement les documents et les changements.',['plan']),
 ('vocabulary_in_context','Que signifie « route » ici ?','Le chemin choisi pour aller vers une destination.',['route']),
 ('vocabulary_in_context','Quels mots désignent le lieu et la pièce où dormir ?','hôtel et chambre',['hôtel','chambre']),
 ('reference_resolution','Dans « il sert surtout », que désigne « il » ?','Un bon plan.',['plan']),
 ('inference','Pourquoi une visite doit-elle parfois être raccourcie ?','Pour respecter les horaires du reste du voyage.',['visite','voyage']),
 ('cloze_transfer','Complète : Nous faisons une courte _____ avant de repartir.','visite',['visite']),
 ('summary','Résume les trois idées principales du texte.','Préparer le voyage, vérifier les informations et adapter le plan si nécessaire.',['voyage','plan'])
]

base.main()
