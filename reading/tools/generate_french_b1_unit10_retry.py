#!/usr/bin/env python3
"""Retry B1 Unit 10 after fail-closed freshness/checkpoint findings.

`vêtement` is replaced with source-backed `dent` (rank 968), and the B1 final
checkpoint declares only Unit 10 summary vocabulary. All guards remain intact.
"""
import generate_french_b1_unit10 as base

base.FORMS=('monstre','ridicule','innocent','vide','débarrasser','centre','bain','toilette','baisser','peau','nez','dent','couleur','énorme','traîner')

p4=next(s for s in base.SPECS if s['id']=='fr-b1-u10-p04')
p4['forms']=['peau','nez','dent']
p4['title']='Peau, nez et dent : trois indices qui ne racontent pas la même chose'
p4['topics']=['biology','observation']
p4['paragraphs']=[
"Dans un atelier de biologie, les élèves observent des photographies très rapprochées de différentes parties du corps. Un élève donne l’exemple d’une surface claire et affirme que toutes les structures visibles peuvent être décrites de la même manière. Camille trouve l’idée intéressante mais trop large. La peau, le nez et une dent sont tous visibles sur le corps, pourtant leur structure et leur fonction sont très différentes. Une ressemblance de couleur ou de forme ne suffit donc pas à les classer ensemble.",
"La classe compare ensuite plusieurs caractéristiques. La peau forme une enveloppe souple qui couvre une grande partie du corps. Le nez contient des structures liées notamment au passage de l’air et à l’odorat. Une dent possède une surface dure adaptée à d’autres fonctions. L’élève reconnaît qu’il avait tort de traiter ces éléments comme une seule catégorie simplement parce qu’ils appartiennent au même organisme. Son exemple reste utile : il oblige le groupe à préciser ce qu’il compare avant de conclure.",
"Les élèves construisent enfin un tableau avec les colonnes position, structure visible et fonction générale. Ils placent peau, nez et dent sur trois lignes séparées. Camille trouve ce classement intéressant parce qu’il transforme une impression visuelle en comparaison explicite. Avoir tort sur la première classification rend l’exemple plus instructif : on voit exactement quelle hypothèse a dû changer. Le groupe retient qu’une observation précise commence par des mots précis. Dire qu’une dent, le nez et la peau sont simplement des « parties du corps » est vrai mais insuffisant si la question porte sur leur structure ou leur fonction."
]
p4['items']=base.qa(p4['forms'],p4['reviews'],'biology')

cp=base.CHECKPOINT
cp['paragraphs'][1]=cp['paragraphs'][1].replace('peau, nez et vêtement', 'peau, nez et dent').replace('liés au froid', 'des parties du corps')
cp['items']=[
('gist','Quelle méthode clôt le niveau B1 ?','Définir le problème, observer les indices, vérifier le sens, comparer les explications et limiter la conclusion.',['vide']),
('literal_detail','Quels mots appartiennent au récit ?','monstre, ridicule et innocent',['monstre','ridicule','innocent']),
('cause_effect','Pourquoi créer un espace vide ?','Pour se débarrasser du désordre et rendre le centre de la réserve accessible.',['vide','débarrasser','centre']),
('vocabulary_in_context','Quels mots décrivent la conservation d’eau ?','bain, toilette et baisser',['bain','toilette','baisser']),
('vocabulary_in_context','Quels mots décrivent l’observation biologique ?','peau, nez et dent',['peau','nez','dent']),
('inference','Pourquoi la couleur ou la taille doit-elle être testée selon le support ?','Parce qu’une couleur ou un titre énorme peut fonctionner à un endroit mais faire traîner une décision sans critère.',['couleur','énorme','traîner']),
('motive','Pourquoi Camille limite-t-elle ses conclusions ?','Pour ne pas présenter comme établi ce que les observations ne permettent pas de soutenir.',[]),
('reference_resolution','Dans la comparaison biologique, quels trois éléments sont séparés ?','La peau, le nez et la dent.',['peau','nez','dent']),
('cloze_transfer','Complète : Une réparation utile peut faire _____ la consommation.','baisser',['baisser']),
('summary','Résume l’unité.','Camille distingue monstre, ridicule et innocent ; utilise vide, débarrasser et centre pour organiser ; compare bain, toilette et baisser ; sépare peau, nez et dent ; puis teste couleur et énorme pour éviter de faire traîner le projet.',['monstre','ridicule','innocent','vide','débarrasser','centre','bain','toilette','baisser','peau','nez','dent','couleur','énorme','traîner'])
]

base.main()
