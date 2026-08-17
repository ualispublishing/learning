#!/usr/bin/env python3
"""Retry B1 Unit 04 after authoritative freshness rejected three candidates.

`recherche`, `voix`, and `présent` were already deliberate earlier in French.
They are replaced by fresh source-backed `sérieux` (rank 640), `spécial` (rank
633), and `plutôt` (rank 644). The other twelve candidates are unchanged.
"""
from __future__ import annotations
import generate_french_b1_unit04 as base

base.FORMS=('probablement','prouver','sérieux','scène','spécial','créer','rejoindre','ligne','bout','normal','système','prévenir','relation','reconnaître','plutôt')

p1=next(s for s in base.SPECS if s['id']=='fr-b1-u04-p01')
p1['forms']=['probablement','prouver','sérieux']
p1['title']='Un résultat sérieux sans vouloir prouver trop vite'
p1['paragraphs']=[
"Pour un projet de sciences, Camille retourne dans la zone humide étudiée le mois précédent. Cette fois, la classe examine la qualité de l’eau après plusieurs jours de pluie. À première vue, l’eau paraît plus sombre près du chemin. Certains élèves pensent que la pluie a probablement transporté davantage de terre vers le bassin. Camille rappelle cependant qu’une observation visuelle ne suffit pas à prouver la cause du changement, même lorsqu’une hypothèse paraît raisonnable.",
"L’équipe décide de séparer la zone en trois secteurs et de prélever un petit morceau de végétation ainsi qu’un échantillon d’eau dans chacun. Pour obtenir un résultat sérieux, les élèves utilisent la même méthode dans chaque secteur : même durée d’observation, même type de récipient et mêmes mesures. Les données montrent une différence nette près du chemin, mais elles ne peuvent pas prouver que la pluie est la seule cause. Des travaux ont aussi eu lieu à proximité pendant la semaine.",
"Dans son compte rendu, Camille écrit qu’il est probablement raisonnable de poursuivre l’hypothèse liée au ruissellement, tout en signalant les autres facteurs. Elle explique qu’un travail sérieux ne cherche pas à confirmer l’idée préférée du groupe à tout prix. Il sépare les observations, décrit chaque morceau de preuve et indique ce qui reste incertain. Cette prudence ne rend pas le résultat moins utile : elle montre précisément quelle conclusion les données permettent de soutenir, ce qu’elles ne peuvent pas encore prouver et quelle question mérite une nouvelle mesure."
]
p1['items']=[
('gist','Quelle règle Camille applique-t-elle à l’étude ?','Elle cherche un résultat sérieux en distinguant ce qui est probable de ce que les données peuvent réellement prouver.',['sérieux','probablement','prouver']),
('literal_detail','En combien de secteurs l’équipe décide-t-elle de séparer la zone ?','En trois secteurs.',['séparer','zone']),
('cause_effect','Pourquoi les résultats ne prouvent-ils pas que la pluie est la seule cause ?','Parce que des travaux proches peuvent aussi expliquer une partie du changement.',['prouver']),
('vocabulary_in_context','Que signifie « probablement » dans le rapport ?','Que l’explication paraît vraisemblable sans être certaine.',['probablement']),
('vocabulary_in_context','Que signifie « sérieux » lorsqu’il décrit le travail ?','Rigoureux et traité avec suffisamment de soin pour être crédible.',['sérieux']),
('inference','Pourquoi l’équipe applique-t-elle la même méthode dans chaque secteur ?','Pour rendre la comparaison plus sérieuse et éviter que la méthode elle-même crée les différences observées.',['sérieux']),
('reference_resolution','Dans « Il sépare les observations », à quoi renvoie « Il » ?','Au travail sérieux décrit par Camille.',['sérieux']),
('grammar_in_context','Quel effet a « probablement » sur l’hypothèse du ruissellement ?','Le mot réduit le degré de certitude et présente l’hypothèse comme plausible plutôt que prouvée.',['probablement','prouver']),
('cloze_transfer','Complète : Un seul résultat ne suffit pas toujours à _____ une cause.','prouver',['prouver']),
('summary','Résume la méthode du groupe.','L’équipe sépare la zone, examine chaque morceau de preuve et cherche un résultat sérieux en distinguant ce qui est probablement vrai de ce qu’elle peut prouver.',['séparer','zone','morceau','sérieux','probablement','prouver'])
]

p2=next(s for s in base.SPECS if s['id']=='fr-b1-u04-p02')
p2['forms']=['scène','spécial','créer']
p2['title']='Créer un effet spécial sans perdre la scène'
p2['paragraphs']=[
"La classe prépare une courte représentation pour la soirée de l’école. Sur scène, quatre élèves doivent parler pendant qu’un bruit de rue est diffusé en arrière-plan. Le groupe veut aussi ajouter un effet spécial : une lumière doit changer lorsque les personnages comprennent qu’un orage approche. À la première répétition, le son est si fort qu’il couvre presque les acteurs et l’effet spécial attire davantage l’attention que l’histoire. Sami propose une solution rapide : supprimer tous les effets.",
"Camille préfère agir autrement, car le bruit et la lumière aident à créer l’ambiance de la scène. Le groupe cherche donc ce qui peut causer la perte de clarté. Deux enceintes sont trop proches du devant, tandis que la lumière spéciale change trop souvent. Les élèves déplacent les enceintes, réduisent légèrement le volume et gardent un seul changement de lumière. Ils enregistrent ensuite trente secondes pour vérifier le résultat. L’action est rapide, mais elle répond à des problèmes identifiés plutôt qu’à une impression générale.",
"À la deuxième répétition, la scène garde son atmosphère et le public test comprend mieux les dialogues. La professeure souligne qu’un effet spécial n’est utile que s’il sert une intention. Créer une scène claire ne signifie pas ajouter le plus d’éléments possible. Camille retient aussi qu’une difficulté peut causer plusieurs réactions : supprimer, déplacer, réduire ou modifier la façon d’agir. Ici, l’équipe réussit à créer une scène plus lisible en conservant un effet spécial précis et en ajustant seulement ce qui empêchait l’histoire d’atteindre le public."
]
p2['items']=[
('gist','Quel compromis l’équipe trouve-t-elle ?','Elle garde un effet spécial utile tout en rendant la scène plus claire.',['spécial','scène']),
('literal_detail','Quel effet spécial est prévu ?','Un changement de lumière lorsque les personnages comprennent qu’un orage approche.',['spécial']),
('cause_effect','Pourquoi Camille refuse-t-elle de supprimer tous les effets ?','Parce qu’ils peuvent aider à créer l’ambiance de la scène lorsqu’ils sont bien réglés.',['créer','scène']),
('vocabulary_in_context','Que désigne « scène » ici ?','L’espace et la séquence théâtrale où les élèves jouent.',['scène']),
('vocabulary_in_context','Que signifie « spécial » dans « effet spécial » ?','Un effet particulier ajouté à la représentation pour produire une impression précise.',['spécial']),
('inference','Pourquoi l’action rapide reste-t-elle méthodique ?','Parce que l’équipe identifie ce qui peut causer chaque problème avant de modifier les réglages.',['rapide','agir','causer']),
('motive','Pourquoi les élèves enregistrent-ils trente secondes ?','Pour vérifier si leurs changements servent mieux la scène avant de poursuivre.',['scène']),
('grammar_in_context','Que montre la phrase « n’est utile que s’il sert une intention » ?','Elle limite la valeur d’un effet spécial à sa fonction dans la représentation.',['spécial']),
('cloze_transfer','Complète : Le groupe veut _____ une ambiance sans surcharger la représentation.','créer',['créer']),
('summary','Résume la correction de la répétition.','L’équipe agit rapidement sur ce qui peut causer le problème et réussit à créer une scène claire avec un seul effet spécial bien choisi.',['agir','rapide','causer','créer','scène','spécial'])
]

p5=next(s for s in base.SPECS if s['id']=='fr-b1-u04-p05')
p5['forms']=['relation','reconnaître','plutôt']
p5['title']='Reconnaître une relation plutôt que forcer une ressemblance'
p5['paragraphs']=[
"Dans une nouvelle exposition, Camille observe une série d’affiches consacrées à la paix après différentes périodes de conflit. Le rôle de l’art varie d’une affiche à l’autre : certaines cherchent à rassurer, d’autres à convaincre ou à commémorer. Le musée veut montrer la relation entre ces images historiques et les questions actuelles, mais il préfère parler de comparaison plutôt que prétendre que les problèmes d’aujourd’hui sont identiques à ceux du passé.",
"Une médiatrice demande aux visiteurs de reconnaître deux choses à la fois. Premièrement, une œuvre appartient à son contexte d’origine et doit être lue avec les mots, les événements et les attentes de son époque. Deuxièmement, les visiteurs apportent leurs propres questions. La relation entre ces deux moments peut aider à voir ce qui change et ce qui reste familier. Reconnaître cette relation signifie donc comparer plutôt que fusionner les contextes. Le musée cherche une lecture nuancée plutôt qu’une ressemblance facile.",
"Camille choisit une affiche où une colombe occupe presque toute l’image. Aujourd’hui, ce symbole lui paraît immédiatement lié à la paix, mais la médiatrice montre que le texte original insistait surtout sur la reconstruction. Camille comprend que l’art du passé peut rester dans la mémoire collective tout en changeant de sens selon le contexte. Pour elle, reconnaître cette évolution est plus intéressant que chercher une interprétation unique. Elle préfère expliquer la relation entre les lectures plutôt que décider qu’une seule période fournit automatiquement la bonne réponse pour toutes les autres."
]
p5['items']=[
('gist','Quelle relation le musée cherche-t-il à montrer ?','La relation entre l’art historique et les questions que les visiteurs posent aujourd’hui.',['relation','art']),
('literal_detail','Quel symbole Camille observe-t-elle sur une affiche ?','Une colombe.',['paix']),
('cause_effect','Pourquoi le musée parle-t-il de comparaison plutôt que d’identité ?','Parce qu’il veut reconnaître les liens sans effacer les différences historiques.',['reconnaître','plutôt']),
('vocabulary_in_context','Que signifie « relation » ici ?','Le lien comparatif entre deux contextes ou interprétations.',['relation']),
('vocabulary_in_context','Quel rôle joue « plutôt » dans « comparer plutôt que fusionner » ?','Il marque une préférence entre deux façons d’interpréter les contextes.',['plutôt']),
('inference','Pourquoi la colombe peut-elle recevoir une lecture différente aujourd’hui ?','Parce que les visiteurs apportent des associations qui ne sont pas exactement celles du contexte original.',['relation']),
('motive','Pourquoi le musée évite-t-il une ressemblance facile ?','Pour préserver le rôle du contexte historique dans l’interprétation de l’art.',['rôle','art']),
('grammar_in_context','Que permet la structure « plutôt que » ?','Elle oppose une option préférée à une autre que le texte rejette ou limite.',['plutôt']),
('cloze_transfer','Complète : Il faut _____ la différence entre les deux contextes.','reconnaître',['reconnaître']),
('summary','Résume la méthode du musée.','Il examine la relation entre les œuvres et les lectures actuelles, préfère comparer plutôt que fusionner les contextes et cherche à reconnaître le rôle historique des symboles de paix.',['relation','plutôt','reconnaître','rôle','art','paix'])
]

cp=base.CHECKPOINT
cp['paragraphs']=[
"Camille apprend à transformer une première impression en décision vérifiée. Dans une étude sérieuse, une explication est probablement plausible sans que les observations puissent encore la prouver. Sur une scène, il faut créer une ambiance et décider si un effet spécial sert réellement l’histoire. Dans les transports, savoir rejoindre une ligne suppose de comprendre où elle mène et où se trouve le bout du trajet, plutôt que de suivre les autres sans vérifier.",
"Dans une cuisine communautaire, un signal normal peut faire partie d’un système conçu pour prévenir un problème. La technologie aide, mais une personne doit encore interpréter ce qu’elle observe. Au musée, reconnaître une relation entre deux périodes demande la même prudence : il vaut mieux comparer plutôt que forcer une ressemblance qui efface le contexte.",
"Ces exemples prolongent les méthodes précédentes. Camille sait séparer une zone en morceaux, agir rapidement sans confondre vitesse et précipitation, oser une idée avec assez de liberté pour la réviser, accompagner une livraison de nourriture et réfléchir au rôle de l’art dans un message de paix. Elle comprend surtout qu’une bonne décision n’est pas celle qui paraît certaine le plus vite. Elle décrit ce qu’elle sait, vérifie ce qui peut être prouvé et choisit ensuite une réponse adaptée."
]
cp['items']=[
('gist','Quelle méthode générale relie l’unité ?','Passer d’une première impression à une décision fondée sur une vérification adaptée.',['sérieux']),
('literal_detail','Quels mots décrivent la première situation ?','probablement, prouver et sérieux',['probablement','prouver','sérieux']),
('cause_effect','Pourquoi la scène demande-t-elle un choix ?','Parce qu’il faut créer une ambiance sans laisser un effet spécial dominer l’histoire.',['scène','créer','spécial']),
('vocabulary_in_context','Quels mots résument le trajet en transport ?','rejoindre, ligne et bout',['rejoindre','ligne','bout']),
('vocabulary_in_context','Quels mots décrivent la procédure de prévention ?','normal, système et prévenir',['normal','système','prévenir']),
('inference','Quel principe commun unit l’étude scientifique et l’interprétation du musée ?','Une hypothèse ou une relation peut être utile sans être traitée comme une preuve complète ou une identité parfaite.',['relation']),
('motive','Pourquoi Camille préfère-t-elle comparer plutôt que forcer une conclusion ?','Pour préserver les différences et limiter la décision à ce qui est réellement soutenu.',['plutôt']),
('reference_resolution','Dans « où elle mène », à quoi renvoie « elle » ?','À la ligne de transport.',['ligne']),
('cloze_transfer','Complète : Il faut _____ ce qui est confirmé avant de conclure.','reconnaître',['reconnaître']),
('summary','Résume l’unité en une phrase.','Camille apprend à mener un travail sérieux, créer une scène avec un effet spécial utile, rejoindre une ligne, comprendre un système de prévention et reconnaître une relation plutôt que forcer une conclusion.',['sérieux','créer','scène','spécial','rejoindre','ligne','système','prévenir','reconnaître','relation','plutôt'])
]

base.main()
