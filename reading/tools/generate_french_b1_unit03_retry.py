#!/usr/bin/env python3
"""Retry B1 Unit 03 with source-backed `rôle` and intact B1 guards.

Repairs are narrow and pre-canonical: replace missing-lexicon `existence` with
source-backed `rôle`, then expand P02 naturally above the unchanged 220-word B1
floor. No source, freshness, linkage, review-visibility, or checkpoint guard is
weakened.
"""
from __future__ import annotations
import generate_french_b1_unit03 as base

base.FORMS=('zone','séparer','morceau','causer','rapide','agir','espoir','oser','liberté','nourriture','accompagner','sonner','art','paix','rôle')

p2=next(s for s in base.SPECS if s['id']=='fr-b1-u03-p02')
p2['paragraphs'][-1]+=" Sami ajoute aussi que cette chronologie permettra au support de comparer rapidement un prochain incident avec celui-ci, sans confondre une hypothèse initiale avec la cause finalement confirmée."

p5=next(s for s in base.SPECS if s['id']=='fr-b1-u03-p05')
p5['forms']=['art','paix','rôle']
p5['title']='Le rôle de l’art dans un message de paix'
p5['paragraphs']="""Lors d’une visite au musée, Camille participe à une conversation sur une affiche créée après une guerre. L’œuvre utilise l’art pour représenter le retour de la paix : deux personnes se serrent la main devant une ville reconstruite. Un premier panneau affirme que l’image « montre l’unité complète de la population ». Une historienne demande toutefois au groupe d’admettre que cette phrase va plus loin que ce que l’affiche peut prouver.

Elle explique que le rôle d’une affiche en faveur de la paix peut être de défendre un idéal ou d’encourager une vision du futur. Cela ne signifie pas que tout le monde partageait ce message. Certains documents de la même période révèlent encore des conflits et des désaccords. L’historienne ne qualifie pas l’œuvre de mensonge. Elle distingue l’art, qui peut exprimer un espoir ou une position, d’une enquête historique qui cherche à décrire l’ensemble de la société. Cette différence ouvre une conversation plus riche sur le rôle de l’image.

Camille comprend alors pourquoi le rôle du panneau explicatif est important. Une œuvre d’art peut défendre la paix sans devenir une mesure précise de l’opinion publique. Le musée décide de modifier le panneau : au lieu d’affirmer une unité complète, il expliquera que l’affiche présente un idéal de paix promu par certains acteurs. Admettre cette limite ne diminue pas l’intérêt de l’œuvre. Au contraire, cela évite de transformer une interprétation trop large en mensonge présenté comme un fait.""".split('\n\n')
p5['items']=[
('gist','Quelle distinction l’historienne demande-t-elle de faire ?','Distinguer le message de paix porté par l’art d’une preuve que toute la population partageait ce message.',['art','paix']),
('literal_detail','Que représentent les deux personnes sur l’affiche ?','Elles se serrent la main devant une ville reconstruite.',['paix']),
('cause_effect','Pourquoi le musée modifie-t-il son panneau ?','Parce que le rôle d’une affiche est d’exprimer ou promouvoir un message, pas de prouver une unité complète de la population.',['rôle']),
('vocabulary_in_context','Que signifie « rôle » dans ce passage ?','La fonction jouée par l’affiche ou le panneau dans la manière de présenter un message.',['rôle']),
('vocabulary_in_context','Comment le texte emploie-t-il « art » ?','Comme une forme d’expression pouvant présenter un idéal ou une vision sans être un relevé complet de la réalité.',['art']),
('inference','Pourquoi l’historienne refuse-t-elle de qualifier l’affiche elle-même de mensonge ?','Parce que l’œuvre exprime un message ; le problème vient d’une interprétation historique trop forte du panneau.',['mensonge']),
('motive','Pourquoi faut-il admettre la limite du document ?','Pour éviter de présenter comme fait ce que l’affiche seule ne permet pas d’établir.',['admettre']),
('reference_resolution','Dans « Cette différence ouvre une conversation », quelle différence est visée ?','La différence entre le rôle expressif de l’art et celui d’une enquête historique.',['conversation','rôle']),
('cloze_transfer','Complète : Le _____ de cette affiche est de présenter un idéal de paix.','rôle',['rôle','paix']),
('summary','Résume la conclusion de Camille.','Le rôle d’une œuvre d’art peut être de défendre la paix et d’ouvrir une conversation, mais il faut admettre ses limites pour ne pas transformer une interprétation en mensonge.',['rôle','art','paix','conversation','admettre','mensonge'])
]

cp=base.CHECKPOINT
cp['paragraphs']=[
"Camille remarque que plusieurs problèmes deviennent plus faciles lorsqu’on les découpe avant de décider. Sur le terrain, une zone peut être trop variée pour être décrite en une phrase : il faut la séparer en secteurs et observer chaque morceau. Lors d’un incident technique, une panne peut causer plusieurs symptômes ; une réponse rapide consiste à agir sur ce qui est confirmé sans multiplier les changements. Dans un projet créatif, l’espoir d’attirer un public peut donner la liberté d’oser une idée, mais cette idée doit encore être testée.",
"La même méthode apparaît dans les tâches quotidiennes. Pour livrer de la nourriture, un bénévole peut accompagner une nouvelle personne et décider quand sonner en fonction des consignes. Dans un musée, l’art peut défendre la paix sans jouer le rôle d’une enquête sur l’opinion générale. Les mots et les documents doivent donc être reliés à ce qu’ils montrent réellement.",
"Les unités précédentes ajoutent d’autres vérifications : un détail apparemment simple peut changer une conclusion ; un choix sur un ordinateur peut avoir des conséquences ; une dépense peut coûter cher sans être inutile ; et une conversation peut contenir un mensonge qu’il faut admettre publiquement. Camille apprend ainsi à agir sans précipitation, à respecter les limites des preuves et à garder assez de liberté pour corriger une première solution."
]
cp['items']=[
('gist','Quelle méthode générale relie les situations ?','Décomposer le problème, vérifier chaque partie puis agir sans dépasser ce que les preuves permettent.',['agir']),
('literal_detail','Quels mots décrivent la méthode de terrain ?','zone, séparer et morceau',['zone','séparer','morceau']),
('cause_effect','Pourquoi une réponse rapide ne signifie-t-elle pas changer tout le système ?','Parce qu’il faut identifier ce qui peut causer le problème avant de multiplier les modifications.',['rapide','causer']),
('vocabulary_in_context','Quels mots décrivent l’attitude créative du troisième passage ?','espoir, oser et liberté',['espoir','oser','liberté']),
('vocabulary_in_context','Quels mots appartiennent à la situation de livraison ?','nourriture, accompagner et sonner',['nourriture','accompagner','sonner']),
('inference','Pourquoi le texte rapproche-t-il l’observation scientifique et l’interprétation d’un musée ?','Dans les deux cas, il faut limiter la conclusion au rôle réel d’une partie, d’un document ou d’une méthode.',['rôle','art']),
('motive','Pourquoi Camille garde-t-elle de la liberté après avoir commencé à agir ?','Pour pouvoir corriger une première solution si les nouvelles observations la contredisent.',['liberté','agir']),
('reference_resolution','Dans « cette idée doit encore être testée », à quoi renvoie « cette idée » ?','À l’idée créative que le groupe a osé proposer.',['oser']),
('cloze_transfer','Complète : Une œuvre peut défendre la _____ sans jouer le rôle d’une enquête.','paix',['paix','rôle']),
('summary','Résume l’unité en une phrase.','Camille apprend à séparer une zone, agir de façon rapide mais contrôlée, oser avec liberté, accompagner une livraison et interpréter le rôle de l’art dans un message de paix sans dépasser les preuves.',['séparer','zone','agir','rapide','oser','liberté','accompagner','rôle','art','paix'])
]

base.main()
