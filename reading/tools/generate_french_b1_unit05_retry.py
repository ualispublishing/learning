#!/usr/bin/env python3
"""Retry B1 Unit 05 after `prix` was rejected as already deliberate.

The other fourteen candidates remain unchanged. `prix` is replaced by fresh,
source-backed `liste` (rank 646) in the budget/planning passage and checkpoint.
"""
import generate_french_b1_unit05 as base

base.FORMS=('clair','reprendre','déranger','empêcher','récupérer','sinon','ancien','vivant','honneur','inviter','remercier','mériter','liste','réaliser','arranger')

p5=next(s for s in base.SPECS if s['id']=='fr-b1-u05-p05')
p5['forms']=['liste','réaliser','arranger']
p5['title']='Arranger la liste des coûts pour réaliser le projet'
p5['paragraphs']=[
"Un centre communautaire veut réaliser une petite exposition photographique avec des travaux d’élèves. Le premier devis dépasse largement le budget. Camille dresse une liste des coûts : impression, cadres, éclairage et transport. Elle cherche la relation entre chaque dépense et l’objectif pédagogique. Plutôt que de réduire toutes les lignes du budget de la même manière, elle veut reconnaître quelles dépenses influencent réellement la qualité de l’exposition et lesquelles peuvent être réorganisées.",
"L’équipe découvre qu’elle peut arranger le plan de la salle pour utiliser moins de cadres sans montrer moins de photos. Deux murs accueilleront des séries d’images sous un même cadre large, tandis que les œuvres principales garderont un cadre individuel. La liste est alors mise à jour avec le nouveau nombre de cadres et les coûts correspondants. Camille précise toutefois que réaliser un projet moins cher ne signifie pas choisir automatiquement le matériau le moins coûteux. Un matériau très fragile pourrait demander un remplacement rapide.",
"Le groupe décide donc de réaliser une version qui équilibre coût, durée et lisibilité. Il demande au fournisseur d’arranger la livraison afin que tout arrive le même jour, ce qui réduit aussi le transport. Camille reconnaît que chaque choix crée une relation entre plusieurs contraintes. Elle préfère arranger le plan plutôt que supprimer une partie importante de l’exposition. Au final, la liste permet de justifier chaque dépense : certaines diminuent, d’autres restent parce qu’elles protègent un objectif essentiel. Le centre peut réaliser le projet dans son budget et expliquer clairement pourquoi la liste finale n’est pas simplement la version la moins chère, mais la version la plus cohérente avec le résultat attendu."
]
p5['items']=[
('gist','Comment l’équipe réduit-elle le budget ?','Elle arrange le plan de l’exposition et utilise une liste des coûts reliée aux fonctions de chaque dépense.',['arranger','liste']),
('literal_detail','Quels types de coûts apparaissent dans la liste ?','L’impression, les cadres, l’éclairage et le transport.',['liste']),
('cause_effect','Pourquoi l’équipe met-elle la liste à jour ?','Parce que le nouvel arrangement réduit le nombre de cadres et modifie les coûts.',['liste','arranger']),
('vocabulary_in_context','Que signifie « réaliser » le projet ?','Le mener à terme et produire concrètement l’exposition prévue.',['réaliser']),
('vocabulary_in_context','Que signifie « arranger » le plan ?','Le modifier ou l’organiser de manière plus adaptée aux contraintes.',['arranger']),
('inference','Pourquoi Camille examine-t-elle la relation entre dépense et objectif ?','Pour reconnaître quelles dépenses protègent réellement la qualité du projet.',['relation','reconnaître']),
('motive','Pourquoi préfère-t-elle arranger plutôt que supprimer ?','Pour respecter le budget sans retirer une partie essentielle de l’exposition.',['plutôt','arranger']),
('grammar_in_context','Que met en contraste « plutôt que » ?','La préférence pour réorganiser le projet au lieu de supprimer un élément important.',['plutôt']),
('cloze_transfer','Complète : Camille prépare une _____ des coûts avant de modifier le projet.','liste',['liste']),
('summary','Résume la décision budgétaire.','L’équipe utilise une liste pour relier les coûts aux objectifs, choisit d’arranger le plan plutôt que supprimer des éléments et peut finalement réaliser le projet.',['liste','relation','arranger','plutôt','réaliser'])
]

cp=base.CHECKPOINT
cp['paragraphs'][1]="Au musée, un ancien bateau peut soutenir un récit vivant qui rend honneur aux équipes sans cacher leurs erreurs. Dans une association, inviter des bénévoles, les remercier précisément et décider ce qui mérite du temps rendent la coopération plus visible. Dans un budget, une liste de coûts doit être reliée aux fonctions du projet : on peut arranger le plan pour réaliser l’objectif autrement plutôt que supprimer immédiatement une partie essentielle."
cp['paragraphs'][2]="Les unités précédentes restent présentes dans ces décisions. Camille distingue ce qui est probablement vrai de ce qu’un test peut prouver dans un travail sérieux. Elle sait créer une scène avec un effet spécial utile, rejoindre une ligne jusqu’au bon bout, comprendre quand un signal est normal dans un système conçu pour prévenir un problème et reconnaître la relation entre plusieurs interprétations. Elle retient surtout qu’une bonne méthode offre plusieurs chemins : reprendre avec une information claire, récupérer ce qui peut l’être, honorer les faits anciens sans les simplifier, inviter et remercier les personnes concernées, puis arranger une liste de contraintes afin de réaliser l’objectif de manière justifiée."
cp['items']=[
('gist','Quelle idée générale relie les cinq situations ?','Construire une réponse claire, prévoir des solutions de remplacement et ajuster le plan sans perdre l’objectif.',['clair','arranger']),
('literal_detail','Quels mots résument la première situation ?','clair, reprendre et déranger',['clair','reprendre','déranger']),
('cause_effect','Pourquoi une sauvegarde est-elle utile ?','Elle peut empêcher une perte et permettre de récupérer le fichier ; sinon une autre solution est prévue.',['empêcher','récupérer','sinon']),
('vocabulary_in_context','Quels mots décrivent la visite historique ?','ancien, vivant et honneur',['ancien','vivant','honneur']),
('vocabulary_in_context','Quels mots décrivent la coordination des bénévoles ?','inviter, remercier et mériter',['inviter','remercier','mériter']),
('inference','Pourquoi la liste n’est-elle pas traitée comme une simple série de nombres ?','Parce qu’elle relie chaque coût à une fonction et à l’objectif à réaliser.',['liste','réaliser']),
('motive','Pourquoi Camille préfère-t-elle arranger certaines contraintes ?','Pour conserver l’objectif essentiel plutôt que supprimer automatiquement un élément.',['arranger']),
('reference_resolution','Dans « sinon, une solution de remplacement », à quelle situation renvoie « sinon » ?','Au cas où la récupération principale du fichier échoue.',['sinon','récupérer']),
('cloze_transfer','Complète : Une procédure claire doit _____ qu’un petit problème devienne une crise.','empêcher',['empêcher']),
('summary','Résume l’unité en une phrase.','Camille apprend à reprendre clairement sans déranger, récupérer ou prévoir sinon, comprendre un récit ancien et vivant avec honneur, inviter et remercier ce qui mérite de l’attention, puis arranger une liste pour réaliser un projet.',['reprendre','clair','déranger','récupérer','sinon','ancien','vivant','honneur','inviter','remercier','mériter','arranger','liste','réaliser'])
]

base.main()
