#!/usr/bin/env python3
"""Quality-depth preflight for French C2 Unit05."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c2_unit05.py'
ns={'__name__':'c2_u05_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
ns['EXTRA']=list(ns['EXTRA'])+[
"Le checkpoint ajoute une analyse de rythme. Deux versions d’une même scène gardent les mêmes événements, mais l’une utilise de longues phrases coordonnées tandis que l’autre fragmente l’action. Le lecteur décrit d’abord la différence formelle, puis vérifie si elle produit attente, accélération ou hésitation. Une impression de vitesse n’est retenue que si l’organisation syntaxique et la position des coupures la soutiennent.",
"Une seconde tâche porte sur la focalisation. Une information identique est racontée une fois depuis un observateur extérieur et une fois depuis un personnage qui ignore une partie de la situation. La comparaison montre comment l’accès au savoir distribue sympathie, surprise et ironie. Elle évite de confondre ce que le texte permet au lecteur d’inférer avec ce qu’un personnage peut lui-même connaître.",
"Le dossier teste ensuite l’ellipse. Une explication est retirée entre deux actions compatibles avec plusieurs causes. Le lecteur doit décider si le manque crée une ambiguïté productive ou s’il détruit une relation nécessaire à la cohérence. Cette distinction empêche de célébrer toute obscurité comme subtilité : certaines omissions ouvrent la lecture, d’autres la rendent simplement insuffisamment déterminée.",
"Enfin, le lecteur reformule une interprétation à trois niveaux de confiance. Il sépare ce qui est directement observable dans la forme, ce qui est fortement inféré par convergence de plusieurs indices et ce qui reste une hypothèse possible. Cette hiérarchie permet de conserver la richesse du texte sans présenter une association séduisante comme une conclusion établie."
]
ns['main']()
