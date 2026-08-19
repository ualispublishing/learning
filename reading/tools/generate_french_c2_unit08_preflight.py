#!/usr/bin/env python3
"""Quality-depth preflight for French C2 Unit08."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c2_unit08.py'
ns={'__name__':'c2_u08_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)

# Extend only when fit() needs more material to meet the strict C2 floor. Each
# paragraph adds a distinct source-criticism operation rather than filler.
ns['EXTRA']=list(ns['EXTRA'])+[
    "Le checkpoint ajoute une matrice d’indépendance des sources. Deux documents qui utilisent les mêmes mots peuvent être indépendants s’ils proviennent d’observations séparées; deux documents très différents peuvent dépendre d’une même information initiale. Le lecteur trace donc les chaînes de transmission avant de compter les convergences et distingue confirmation indépendante, copie, adaptation et simple reprise de rumeur.",
    "Une autre tâche porte sur la datation relative. Lorsqu’une pièce n’a pas de date explicite, le lecteur utilise seulement des indices internes compatibles — personnes mentionnées, état d’un bâtiment, ordre des événements, relation avec une copie — puis exprime une fourchette plutôt qu’un jour artificiellement précis. Chaque indice reçoit aussi une alternative afin d’éviter qu’un seul détail devienne une chronologie entière.",
    "Le dossier teste ensuite les explications contrefactuelles. Pour une cause proposée, le lecteur demande ce qui devrait être différent si ce facteur avait été absent alors que les autres conditions restaient comparables. Ce raisonnement ne recrée pas le passé avec certitude; il oblige à préciser la fonction causale attribuée au facteur et révèle les explications qui se contentent de renommer le résultat.",
    "Enfin, la synthèse sépare preuve de l’événement, preuve du mécanisme et preuve de l’intention. Un registre peut établir qu’une action a eu lieu, une séquence de décisions peut soutenir un mécanisme, et une déclaration contemporaine peut éclairer une intention; aucune de ces pièces ne remplace automatiquement les deux autres. Le lecteur formule donc des conclusions distinctes avec des niveaux de confiance distincts."
]

ns['main']()
