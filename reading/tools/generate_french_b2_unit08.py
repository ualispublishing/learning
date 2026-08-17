#!/usr/bin/env python3
"""Append French B2 Unit08 (seq43-48): history and explanation.

Reads the audited Unit08 selection artifact so vocabulary choice remains
source-backed and fresh without guessing. Four new targets in P01-P05; P06 is
zero-new. Canonical write is guarded by exact source blobs, the Unit07 frontier
lock, schema/linkage, word band, exposure, exact-review and uniqueness checks.
"""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2]
A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';CANON=R/'reading/french/b2/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json';LOCK=R/'reading/audit/french_b2_unit07_frontier_lock.json';PROBE=R/'reading/audit/french_b2_unit08_target_probe.json';SELECT=R/'reading/audit/french_b2_unit08_target_selection.json'
EXPECTED={'A1':'0493a2fa13e51b5997db05e91cdea4d8dc5e647b','A2':'d0a80b8866071f426019aa0ad143e1d270dba4de','B1':'4a2cd9ff30c3cea58caf20fca2822b06200622ca','B2':'5ff899452326f679b7c16b0ff33d8f38fa99719a'}
REVIEWS=[['film','musique','chanson','jouer'],['histoire','lire','écrire','mot'],['ton','sens','sujet','imaginer'],['avis','aimer','beau','drôle'],['vie','présent','société','politique']]

# Prefer natural exact-lemma use for likely selections. A quoted contextual
# fallback remains grammatical for any less-common fresh candidate selected by
# the deterministic artifact, without changing the target itself.
USE={
'époque':"Cette époque est décrite comme un moment de transition, et non comme un bloc uniforme.",
'siècle':"Le siècle étudié contient plusieurs phases que le récit refuse de confondre.",
'période':"Cette période est découpée en étapes afin de rendre la chronologie vérifiable.",
'date':"La date retenue sert de repère documentaire plutôt que de cause automatique.",
'début':"Au début de la séquence, les acteurs disposent encore de plusieurs options.",
'fin':"À la fin de la séquence, le résultat paraît inévitable seulement si l’on oublie les choix antérieurs.",
'avant':"Avant la décision finale, plusieurs solutions concurrentes restent encore ouvertes.",
'après':"Après la décision, les documents changent de ton parce que les acteurs connaissent désormais le résultat.",
'longtemps':"Longtemps, le récit officiel a résumé cette séquence par une seule décision spectaculaire.",
'état':"L’état fictif présenté dans le dossier possède des institutions fragiles et des intérêts concurrents.",
'empire':"L’empire fictif réunit des régions différentes dont les intérêts ne se confondent pas.",
'peuple':"Le peuple n’apparaît pas comme un acteur unique : les sources montrent plusieurs groupes et attentes.",
'nation':"La nation est évoquée par les sources, mais sa définition varie selon les auteurs.",
'roi':"Le roi signe le texte final, sans être pour autant l’unique cause des changements décrits.",
'armée':"L’armée intervient dans la chronologie, mais le dossier distingue sa présence de son influence réelle.",
'paix':"La paix qui suit le conflit reste fragile et dépend de plusieurs accords locaux.",
'bataille':"La bataille occupe une place visible dans le récit, mais elle n’explique pas seule l’issue politique.",
'victoire':"La victoire militaire ne produit pas immédiatement une solution durable dans les institutions.",
'défaite':"La défaite accélère certaines décisions sans créer à elle seule les tensions antérieures.",
'soldat':"Un soldat apparaît dans une lettre, offrant une perspective individuelle plutôt qu’une vue complète.",
'conséquence':"Une conséquence observée après la réforme ne doit pas être prise automatiquement pour sa cause.",
'changement':"Le changement devient visible sur plusieurs années et résulte de décisions successives.",
'développer':"Les autorités cherchent à développer le quartier, mais leurs mesures produisent des effets inégaux.",
'produire':"Une même décision peut produire plusieurs effets selon le groupe concerné.",
'commencer':"Le processus ne commence pas au moment où la crise devient visible dans les journaux.",
'finir':"L’analyse refuse de finir la chaîne causale au premier événement spectaculaire.",
'augmenter':"Les taxes commencent à augmenter avant que les protestations deviennent massives.",
'réduire':"Une mesure destinée à réduire un coût en déplace une partie vers d’autres acteurs.",
'détruire':"La fermeture ne suffit pas à détruire les réseaux économiques déjà formés.",
'créer':"La nouvelle règle peut créer un avantage pour certains métiers tout en fragilisant d’autres.",
'danger':"Le danger invoqué par les autorités change de sens selon les documents consultés.",
'commerce':"Le commerce local dépend à la fois des routes, des règles et de la confiance entre acteurs.",
'port':"Le port fictif devient un nœud important parce qu’il relie plusieurs réseaux de transport.",
'frontière':"La frontière administrative modifie les coûts sans arrêter complètement les échanges.",
'marché':"Le marché local réagit aux règles, mais aussi aux récoltes et aux attentes des négociants.",
'travail':"Le travail change d’organisation lorsque de nouvelles règles modifient les horaires et les contrats.",
'impôt':"L’impôt est une pression parmi d’autres, et son effet dépend des revenus des groupes concernés.",
'faim':"La faim apparaît dans certaines sources, mais sa fréquence doit être vérifiée avant toute généralisation.",
'maladie':"La maladie réduit temporairement la main-d’œuvre et complique l’interprétation des données économiques.",
'crise':"La crise résulte d’une accumulation de tensions plutôt que d’un seul événement.",
'réforme':"La réforme répond à des problèmes existants tout en créant de nouvelles oppositions.",
'document':"Le document principal a été produit par une administration et répond à un objectif précis.",
'source':"La source étudiée informe sur un acteur autant que sur l’événement qu’elle décrit.",
'rapport':"Le rapport résume plusieurs faits, mais sélectionne ceux qui servent sa mission administrative.",
'discours':"Le discours cherche à convaincre un public et doit être lu comme une intervention, pas comme un relevé neutre.",
'registre':"Le registre offre des séries régulières, mais laisse de côté ce qui n’était pas compté par l’administration.",
'lettre':"La lettre donne accès à une expérience située, sans représenter automatiquement tout un groupe.",
'témoin':"Le témoin décrit ce qu’il a vu, avec les limites de sa position et de sa mémoire.",
'témoignage':"Le témoignage apporte une expérience directe, mais doit être comparé à d’autres traces.",
'archive':"L’archive conserve plusieurs types de traces dont les objectifs d’origine sont différents.",
'mémoire':"La mémoire d’un acteur peut éclairer une expérience tout en réorganisant les événements après coup.",
'journal':"Le journal raconte les événements au fur et à mesure et ne connaît pas encore leur issue finale.",
'version':"Une version du conflit insiste sur l’ordre public, tandis qu’une autre insiste sur les revendications sociales.",
'point':"Un point de désaccord porte sur le moment où la confrontation devient inévitable.",
'vue':"La vue proposée par l’administration diffère de celle des associations locales.",
'position':"La position de l’auteur influence les faits qu’il juge importants dans son récit.",
'objectif':"L’objectif du texte aide à expliquer pourquoi certains détails sont développés et d’autres écartés.",
'vérifier':"Pour vérifier une affirmation, l’historien cherche une trace indépendante ou un élément contradictoire.",
'noter':"Il faut noter ce que la source affirme, mais aussi ce qu’elle ne pouvait pas connaître.",
'décrire':"Décrire une séquence ne suffit pas à expliquer pourquoi elle a pris cette direction.",
'observer':"Observer une répétition aide à formuler une hypothèse sans transformer la corrélation en cause.",
'expliquer':"Expliquer exige de relier mécanismes, chronologie et alternatives plutôt que d’aligner des événements.",
'conflit':"Le conflit se développe entre plusieurs groupes dont les objectifs ne sont pas identiques.",
'révolution':"La révolution est présentée comme un processus composé de phases, pas comme une journée isolée.",
'mouvement':"Le mouvement réunit des participants qui ne partagent pas tous la même stratégie.",
'protestation':"La protestation visible n’est qu’une partie d’une mobilisation plus longue.",
'élection':"L’élection modifie le rapport de forces sans effacer les institutions déjà en place.",
'traité':"Le traité clôt une négociation formelle mais laisse plusieurs questions locales ouvertes.",
'alliance':"L’alliance unit temporairement des acteurs qui conservent des intérêts différents.",
'autorité':"L’autorité publique cherche à imposer une règle, mais sa capacité varie selon les lieux.",
'pouvoir':"Le pouvoir n’est pas concentré dans un seul acteur : plusieurs institutions peuvent bloquer ou modifier une décision.",
'institution':"L’institution conserve ses propres procédures, ce qui ralentit certaines transformations.",
'administration':"L’administration produit des catégories utiles à son travail, mais pas toujours à l’analyse historique.",
'gouvernement':"Le gouvernement annonce une politique dont l’application dépend ensuite d’acteurs locaux.",
'majorité':"La majorité soutient une mesure dans un vote, sans que toutes ses raisons soient identiques.",
'minorité':"La minorité conserve des moyens d’action qui empêchent de réduire le conflit au résultat du vote.",
'communauté':"La communauté évoquée dans les sources contient des groupes aux intérêts parfois opposés.",
'génération':"Une génération plus jeune relit les événements avec d’autres priorités que ses prédécesseurs.",
'population':"La population n’est pas une catégorie uniforme : les effets varient selon métier, lieu et revenu.",
'national':"Le cadre national explique certaines règles, mais ne suffit pas à décrire toutes les différences locales.",
'international':"Le contexte international pèse sur les décisions sans déterminer mécaniquement leur résultat.",
'économique':"Le facteur économique compte, mais il interagit avec les choix politiques et institutionnels.",
'militaire':"La dimension militaire modifie les ressources disponibles sans remplacer l’analyse politique.",
'social':"Le contexte social aide à comprendre pourquoi la même mesure produit des réactions différentes.",
'gagner':"Un groupe peut gagner une négociation précise tout en perdre de l’influence sur un autre terrain.",
'perdre':"Perdre un vote n’empêche pas un acteur de modifier ensuite l’application de la décision.",
'attaquer':"Attaquer une position adverse change la chronologie, mais ne révèle pas à lui seul l’objectif politique.",
'défendre':"Défendre une institution peut signifier protéger des règles différentes selon les acteurs.",
'quitter':"Certains responsables choisissent de quitter la coalition lorsque le compromis change.",
'revenir':"Plusieurs acteurs décident de revenir à la table des négociations après l’échec d’une première stratégie.",
'chef':"Le chef du groupe prend la parole, mais les documents montrent que ses membres ne pensent pas tous pareil.",
'membre':"Chaque membre possède une marge d’action qui complique l’idée d’un groupe parfaitement uni.",
'citoyen':"Un citoyen apparaît dans les sources comme acteur local, pas seulement comme destinataire des décisions.",
'responsable':"Un responsable administratif explique la décision depuis le point de vue de son service.",
'travailleur':"Le travailleur cité dans le dossier décrit les effets concrets d’une règle sur son quotidien.",
'intérêt':"L’intérêt d’un acteur aide à expliquer son choix, sans prouver qu’il agit toujours de manière calculée.",
'objectif':"L’objectif déclaré peut différer des effets réellement produits par une décision.",
'but':"Le but annoncé fournit un critère pour comparer la politique à ses résultats.",
'erreur':"Une erreur de calcul accélère le problème sans expliquer les tensions déjà présentes.",
'différence':"La différence entre deux régions permet de tester une explication au lieu de l’affirmer partout.",
'relation':"La relation entre deux événements doit être décrite avant d’être appelée causalité.",
'lien':"Le lien proposé par l’historien gagne en force lorsqu’il respecte la chronologie et un mécanisme plausible.",
'complexe':"Le résultat reste complexe parce que plusieurs causes interagissent et changent d’importance dans le temps.",
'local':"Le niveau local révèle des variations que le récit général peut masquer.",
'religieux':"Le facteur religieux apparaît dans certaines sources, mais son importance varie selon les groupes.",
'probable':"Une explication probable reste ouverte à la comparaison avec des hypothèses concurrentes.",
'faible':"Un indice faible peut soutenir une piste sans justifier une conclusion forte.",
'fort':"Un argument fort relie plusieurs sources indépendantes à un mécanisme cohérent."
}

def usage(form):
 return USE.get(form,f"Le terme « {form} » est utilisé explicitement dans le dossier pour préciser une dimension de l’explication historique plutôt que comme simple étiquette.")

def load_selection():
 s=json.loads(SELECT.read_text(encoding='utf-8'))
 if s.get('status')!='PASS' or s.get('b2_source_blob')!=EXPECTED['B2'] or s.get('selected_count')!=20:raise AssertionError('Unit08 target selection missing/stale')
 groups=s.get('passage_groups',{})
 if sorted(groups)!=['p01','p02','p03','p04','p05'] or any(len(groups[k])!=4 for k in groups):raise AssertionError('Unit08 selection groups malformed')
 flat=[f for k in ['p01','p02','p03','p04','p05'] for f in groups[k]]
 if len(set(flat))!=20:raise AssertionError('Unit08 selection duplicates')
 return groups

def passage_specs(groups):
 g1,g2,g3,g4,g5=[groups[f'p0{i}'] for i in range(1,6)]
 return [
 {'id':'fr-b2-u08-p01','sequence':43,'ptype':'instructional','genre':'historical account','title':'Un documentaire historique : remettre une décision spectaculaire dans sa chronologie','domains':['educational','public'],'topics':['history and explanation','chronology','historical account'],'forms':g1,'reviews':REVIEWS[0],
 'paras':[
 "Un documentaire fictif raconte la transformation politique d’une région imaginaire après plusieurs années de tension. Il commence par une scène spectaculaire : une foule se rassemble devant un bâtiment officiel tandis qu’une musique grave accompagne les images. La chanson entendue ensuite donne l’impression d’un tournant immédiat. Pourtant, le commentaire avertit que le film ne doit pas jouer avec la chronologie au point de faire croire qu’une seule journée a créé tout le changement. Pour expliquer l’événement, il faut remonter aux décisions, aux institutions et aux conflits qui existaient déjà.",
 usage(g1[0])+" "+usage(g1[1])+" Le documentaire place ensuite plusieurs repères sur une ligne du temps et distingue les décisions prises avant la crise des décisions qui en résultent. Cette organisation permet de voir qu’un événement visible peut accélérer un processus sans l’avoir créé. Elle oblige aussi le spectateur à demander quelles alternatives restaient possibles à chaque étape, plutôt que de lire le passé comme si tous les acteurs connaissaient déjà la fin.",
 usage(g1[2])+" "+usage(g1[3])+" Une seconde partie compare les images publiques avec des notes administratives fictives. Certaines sources cherchent à célébrer une décision, d’autres à justifier un compromis. Le film utilise ces différences pour montrer que la chronologie n’est pas seulement une suite de dates : elle sert à tester une explication. Si une cause proposée apparaît après l’effet qu’elle est censée produire, le raisonnement doit être révisé.",
 "La conclusion du documentaire garde donc la scène spectaculaire, mais la traite comme un point dans une séquence plus longue. La musique et la chanson peuvent rendre ce point mémorable; elles ne remplacent pas la preuve historique. Le spectateur est invité à regarder quand chaque source a été produite, ce que ses auteurs savaient alors et quelles décisions n’étaient pas encore prises. Une bonne histoire historique ne retire pas le drame d’un événement. Elle explique pourquoi ce drame devient intelligible seulement lorsqu’il est replacé dans une chronologie où plusieurs chemins restaient ouverts."
 ]},
 {'id':'fr-b2-u08-p02','sequence':44,'ptype':'reinforcement','genre':'causal analysis','title':'Pourquoi un quartier commercial décline : construire une chaîne de causes plutôt qu’un récit unique','domains':['educational','public'],'topics':['history and explanation','causal analysis','economic change'],'forms':g2,'reviews':REVIEWS[1],
 'paras':[
 "Un dossier fictif cherche à expliquer pourquoi un ancien quartier d’ateliers perd une partie de son activité sur vingt ans. Une histoire populaire attribue tout à l’ouverture d’une nouvelle route. Les chercheurs commencent par lire les registres, écrire une chronologie des fermetures et relever chaque mot utilisé par les acteurs lorsqu’ils décrivent leurs difficultés. La route compte, mais l’ordre des événements montre que certains ateliers étaient déjà fragiles. L’objectif n’est pas de remplacer une cause simple par une liste désordonnée, mais de construire une chaîne où chaque mécanisme peut être discuté.",
 usage(g2[0])+" "+usage(g2[1])+" Le dossier compare ensuite les coûts de transport, les règles municipales et l’accès aux fournisseurs. Une explication causale doit montrer comment un facteur modifie les choix disponibles. Dire que deux tendances apparaissent au même moment ne suffit pas. Les chercheurs cherchent des étapes intermédiaires : quels prix changent, quels contrats sont renouvelés, quels acteurs peuvent s’adapter et lesquels supportent le coût le plus rapidement.",
 usage(g2[2])+" "+usage(g2[3])+" Les auteurs examinent aussi une explication concurrente fondée sur la technologie. Elle explique une partie des différences entre métiers, mais moins bien le moment précis où plusieurs fermetures se concentrent. Une troisième hypothèse concerne les règles de propriété. Plutôt que de choisir immédiatement un vainqueur, le texte demande quel ensemble d’indices chaque hypothèse explique et quel fait resterait surprenant si elle était correcte.",
 "La conclusion défend donc une causalité graduée. Certains facteurs rendent le quartier plus vulnérable, d’autres déclenchent une décision, et d’autres encore amplifient ses effets. Lire cette histoire exige de distinguer condition, mécanisme et conséquence. Écrire une explication convaincante signifie aussi montrer les alternatives : si un facteur avait été absent, qu’aurait-on raisonnablement attendu ? Le mot le plus important n’est pas forcément celui qui revient le plus souvent dans les sources. Il faut suivre les relations entre événements et reconnaître qu’une cause historique peut être importante sans être unique."
 ]},
 {'id':'fr-b2-u08-p03','sequence':45,'ptype':'interleaved','genre':'source comparison','title':'Deux sources sur la même journée : comparer leur but avant de choisir leur version','domains':['educational','public'],'topics':['history and explanation','source comparison','perspective'],'forms':g3,'reviews':REVIEWS[2],
 'paras':[
 "Un atelier d’histoire compare deux textes fictifs sur une manifestation ancienne. Le premier a été produit par une administration le soir même; le second a été rédigé plusieurs années plus tard par une participante. Les élèves remarquent immédiatement que le ton diffère. L’administration insiste sur l’ordre, tandis que la participante insiste sur les demandes du groupe. L’enseignante demande quel sens donner à cette différence. Le sujet n’est pas de décider quelle personne dit toute la vérité, mais de comprendre ce que chaque source pouvait savoir, vouloir et sélectionner.",
 usage(g3[0])+" "+usage(g3[1])+" Les élèves commencent par séparer les affirmations qui peuvent être comparées directement : heure, lieu, nombre approximatif de participants, décisions annoncées. Ils évitent d’imaginer une intention cachée lorsque le texte ne fournit aucun indice. En revanche, ils notent les mots employés pour désigner les mêmes personnes et demandent ce que ces choix révèlent sur le public visé.",
 usage(g3[2])+" "+usage(g3[3])+" Un désaccord apparaît sur un passage où les deux récits ne donnent pas le même ordre des événements. L’atelier cherche alors une troisième trace fictive, produite indépendamment, mais rappelle qu’une troisième source n’est pas automatiquement neutre. Elle peut confirmer un détail et rester silencieuse sur un autre. La comparaison progresse donc affirmation par affirmation plutôt qu’en attribuant une note globale de fiabilité.",
 "La conclusion distingue contradiction, perspective et complément. Deux sources peuvent se contredire sur un fait; elles peuvent aussi décrire des aspects différents d’une même journée. Le ton aide à comprendre leur position, mais il ne suffit pas à rejeter un texte. Pour construire du sens, l’historien doit dire quel sujet chaque source traite, quelles informations lui étaient accessibles et ce qu’il serait nécessaire d’imaginer pour combler ses silences. Une source devient utile lorsqu’on connaît ses limites aussi bien que ses informations."
 ]},
 {'id':'fr-b2-u08-p04','sequence':46,'ptype':'transfer','genre':'source comparison and counterargument','title':'Pourquoi deux historiens expliquent différemment la même réforme','domains':['educational','public'],'topics':['history and explanation','competing explanations','historian perspective'],'forms':g4,'reviews':REVIEWS[3],
 'paras':[
 "Deux historiens fictifs publient un avis différent sur une réforme ancienne. Le premier explique surtout la décision par les institutions; le second insiste sur la pression venue des groupes locaux. Les lecteurs peuvent aimer l’élégance du premier récit parce qu’il est très ordonné, ou trouver le second plus vivant et parfois drôle dans sa manière de citer les acteurs. Mais une explication historique n’est pas meilleure parce qu’elle paraît plus beau dans sa structure ou plus agréable à lire. Il faut comparer ce que chaque argument explique réellement.",
 usage(g4[0])+" "+usage(g4[1])+" Le premier historien montre que plusieurs règles limitaient les choix des responsables. Son argument devient moins convaincant lorsqu’il suppose que ces règles produisaient partout le même effet. Le second insiste sur la mobilisation locale, mais il doit expliquer pourquoi des mobilisations semblables n’ont pas toujours obtenu le même résultat. Chaque lecture possède donc une force et un point vulnérable.",
 usage(g4[2])+" "+usage(g4[3])+" Les auteurs utilisent ensuite des sources différentes. L’un privilégie les archives administratives; l’autre cite davantage de journaux et de correspondances locales. Cette différence de corpus peut créer un désaccord sans qu’un chercheur soit simplement de mauvaise foi. La critique demande alors si les conclusions changeraient si les deux ensembles de sources étaient mis en relation.",
 "La comparaison finale ne choisit pas un vainqueur absolu. Elle demande à chaque historien de répondre au meilleur contreargument : les institutions seules expliquent-elles le calendrier ? La mobilisation seule explique-t-elle les limites du compromis ? Un avis solide précise aussi ce qu’il ne peut pas établir. On peut aimer un récit clair, trouver un exemple beau ou drôle, mais ces réactions ne remplacent pas la comparaison des mécanismes, des sources et des cas où l’explication devrait échouer."
 ]},
 {'id':'fr-b2-u08-p05','sequence':47,'ptype':'integration','genre':'historical causal synthesis','title':'Relier acteurs, intérêts et contexte sans transformer la politique en cause unique','domains':['educational','public'],'topics':['history and explanation','multi-causal synthesis','historical actors'],'forms':g5,'reviews':REVIEWS[4],
 'paras':[
 "Un chapitre fictif étudie une réforme urbaine ancienne qui modifie l’accès à plusieurs services. Dans le présent, il serait facile de raconter l’épisode uniquement comme une victoire ou un échec politique. Le chapitre préfère reconstruire la vie des institutions et des habitants au moment de la décision. La société concernée n’est pas homogène : commerçants, responsables locaux, familles et associations évaluent les coûts de manière différente. L’analyse cherche donc à relier acteurs, ressources et calendrier plutôt qu’à attribuer tout le changement à une idée unique.",
 usage(g5[0])+" "+usage(g5[1])+" Les sources montrent que certaines personnes adaptent leur stratégie lorsque les règles changent. D’autres disposent de moins de marge. Le chapitre demande alors qui peut agir, qui doit attendre et qui supporte un coût sans participer directement à la décision. Cette distribution aide à expliquer pourquoi une mesure annoncée comme générale produit des réactions différentes selon les groupes.",
 usage(g5[2])+" "+usage(g5[3])+" L’auteur examine ensuite une interprétation centrée uniquement sur la politique. Elle explique bien les débats officiels, mais moins bien les variations entre quartiers. Une interprétation centrée uniquement sur l’économie rencontre le problème inverse. Le texte propose de relier les deux échelles et de préciser le mécanisme chaque fois qu’il affirme qu’un contexte social, matériel ou institutionnel influence une décision.",
 "La conclusion insiste sur la différence entre contexte et cause. Dire qu’un événement se produit dans une société donnée ne suffit pas à montrer pourquoi il se produit. De même, connaître sa signification dans le présent ne doit pas effacer les options disponibles à l’époque. Une explication historique convaincante reconstruit la vie des acteurs, décrit leurs contraintes, puis montre comment ces contraintes rendent certains choix plus probables sans les rendre inévitables. La politique compte, mais elle agit avec d’autres mécanismes que l’analyse doit rendre visibles."
 ]}
 ]

def items_for(spec):
 f=spec['forms'];r=spec['reviews'];seq=spec['sequence']
 if seq==43:
  return [('main_claim','Pourquoi le documentaire refuse-t-il de commencer et finir son explication avec la scène spectaculaire ?','Parce que cette scène n’est qu’un moment d’un processus antérieur dont la chronologie et les choix doivent être reconstruits.',[f[0],f[1]]),('literal_detail','Quels éléments artistiques rendent la scène mémorable ?','La musique et une chanson accompagnent les images du film.',r[:3]),('argument_relation','Comment la chronologie sert-elle à tester une cause ?','Elle permet de vérifier qu’une cause proposée précède l’effet et que des mécanismes relient les étapes.',[f[1]]),('vocabulary_in_context',f'Quel rôle joue « {f[0]} » dans le passage ?','Il sert à situer précisément le cadre temporel sans le traiter comme une période uniforme.',[f[0]]),('vocabulary_in_context',f'Quel rôle joue « {f[2]} » dans le récit ?','Il désigne un acteur ou cadre historique dont l’influence doit être distinguée de celle des autres acteurs.',[f[2]]),('vocabulary_in_context',f'Comment « {f[3]} » est-il utilisé ?','Il précise une dimension du conflit ou de son issue sans être présenté comme explication unique.',[f[3]]),('assumption','Quelle hypothèse soutient l’idée que les alternatives comptent ?','Que les acteurs du passé ne connaissaient pas encore le résultat final et disposaient de choix réels.',[f[1]]),('inference','Pourquoi comparer images publiques et notes administratives ?','Parce que leurs objectifs différents révèlent ce que chaque source sélectionne et permet de mieux comprendre la séquence.',[f[2]]),('stance','Quelle position le texte adopte-t-il envers la dramatisation ?','Il l’accepte comme forme narrative si elle ne remplace pas la chronologie et les preuves.',r[:2]),('summary','Résume la méthode du documentaire.','Le film garde musique et chanson mais les fait jouer dans une histoire chronologique où les quatre repères nouveaux servent à distinguer cadre, séquence, acteurs et conflit.',f+r)]
 if seq==44:
  return [('main_claim','Quelle conception de la causalité le dossier défend-il ?','Une chaîne où vulnérabilités, déclencheurs et mécanismes se combinent, plutôt qu’une cause unique.',[f[0],f[1]]),('literal_detail','Quels types de données sont comparés ?','Les registres, coûts de transport, règles, fournisseurs, contrats et chronologie des fermetures.',r[:3]),('argument_relation','Pourquoi la simultanéité ne suffit-elle pas ?','Parce que deux tendances peuvent apparaître ensemble sans qu’un mécanisme montre que l’une produit l’autre.',[f[0]]),('vocabulary_in_context',f'Quel rôle joue « {f[0]} » ?','Il sert à qualifier une transformation, un résultat ou une étape de la chaîne causale.',[f[0]]),('vocabulary_in_context',f'Pourquoi « {f[1]} » est-il important ?','Il décrit une pression ou modification dont il faut suivre les effets concrets au lieu de supposer son impact.',[f[1]]),('vocabulary_in_context',f'Comment « {f[2]} » intervient-il ?','Il désigne un mécanisme économique ou spatial susceptible de modifier les choix des acteurs.',[f[2]]),('vocabulary_in_context',f'Comment « {f[3]} » est-il traité ?','Comme une condition ou crise à comparer aux autres facteurs, pas comme réponse automatique.',[f[3]]),('assumption','Pourquoi examiner une hypothèse technologique concurrente ?','Pour tester si l’explication principale rend mieux compte du calendrier et des différences entre métiers.',r[0:2]),('stance','Quelle position le dossier adopte-t-il envers une cause unique ?','Il la refuse lorsque plusieurs mécanismes indépendants sont nécessaires pour expliquer les observations.',[f[0]]),('summary','Résume l’analyse causale.','Lire et écrire cette histoire exige de suivre chaque mot des sources et de relier les quatre cibles nouvelles à une chaîne de mécanismes, de tests et d’alternatives.',f+r)]
 if seq==45:
  return [('main_claim','Quelle règle principale guide la comparaison des sources ?','Comparer les affirmations, buts, possibilités de connaissance et limites de chaque source plutôt que choisir globalement un vainqueur.',[f[0],f[2]]),('literal_detail','Quelles deux sources sont comparées au départ ?','Un texte administratif rédigé le soir même et un récit ultérieur d’une participante.',r[:2]),('argument_relation','Pourquoi une troisième trace n’est-elle pas automatiquement neutre ?','Parce qu’elle possède elle aussi un objectif, un champ d’observation et des silences.',[f[0]]),('vocabulary_in_context',f'Quel rôle joue « {f[0]} » dans la méthode ?','Il désigne un type de trace dont l’origine et le but doivent être établis avant utilisation.',[f[0]]),('vocabulary_in_context',f'Comment « {f[1]} » contribue-t-il à l’analyse ?','Il apporte une expérience ou conservation du passé qui doit être comparée à d’autres traces.',[f[1]]),('vocabulary_in_context',f'Pourquoi « {f[2]} » compte-t-il ?','Il rend visible un angle, une finalité ou une manière particulière d’organiser les faits.',[f[2]]),('vocabulary_in_context',f'Quel rôle joue « {f[3]} » ?','Il décrit l’opération méthodologique utilisée pour contrôler une affirmation ou préciser ses limites.',[f[3]]),('inference','Pourquoi le ton n’est-il pas une raison suffisante pour rejeter une source ?','Parce qu’il renseigne sur la position et le public sans décider à lui seul de l’exactitude de chaque fait.',r[0:2]),('stance','Quelle position l’atelier adopte-t-il envers les silences ?','Il demande de les reconnaître sans imaginer automatiquement l’intention qui les aurait produits.',r[2:4]),('summary','Résume la comparaison.','Ton, sens, sujet et imagination restent encadrés par les quatre cibles nouvelles : type de source, expérience conservée, perspective et méthode de contrôle.',f+r)]
 if seq==46:
  return [('main_claim','Comment le texte propose-t-il de comparer les deux historiens ?','En confrontant leurs mécanismes, corpus, limites et réponses aux meilleurs contrearguments.',[f[0],f[1]]),('literal_detail','Quelles familles de sources privilégient-ils ?','L’un privilégie les archives administratives, l’autre les journaux et correspondances locales.',[f[1]]),('argument_relation','Pourquoi des corpus différents peuvent-ils produire des explications différentes ?','Parce qu’ils rendent visibles des acteurs et mécanismes différents sans impliquer automatiquement de mauvaise foi.',[f[2]]),('vocabulary_in_context',f'Comment « {f[0]} » est-il mobilisé ?','Il désigne un événement ou processus collectif dont les causes restent discutées.',[f[0]]),('vocabulary_in_context',f'Quel rôle joue « {f[1]} » ?','Il nomme une capacité, institution ou acteur qui structure les décisions étudiées.',[f[1]]),('vocabulary_in_context',f'Pourquoi « {f[2]} » est-il utile ?','Il distingue la composition des groupes au lieu de les traiter comme parfaitement homogènes.',[f[2]]),('vocabulary_in_context',f'Comment « {f[3]} » qualifie-t-il l’échelle d’analyse ?','Il précise le niveau ou la dimension à laquelle un mécanisme doit être évalué.',[f[3]]),('assumption','Pourquoi chaque historien doit-il répondre au meilleur contreargument ?','Parce qu’une explication gagne en force lorsqu’elle traite les faits que l’hypothèse concurrente explique mieux.',r[0:2]),('stance','Quelle position le texte adopte-t-il envers le style agréable ?','Il peut rendre un récit beau ou drôle, mais ne remplace pas la qualité de l’explication.',r[2:4]),('summary','Résume la comparaison critique.','Les avis peuvent différer et les lecteurs peuvent aimer des styles différents, mais les quatre cibles nouvelles obligent à comparer conflit, autorité, groupes et échelle avec des sources et contrearguments.',f+r)]
 return [('main_claim','Quelle distinction centrale organise le chapitre ?','Il distingue contexte, contraintes, acteurs et mécanismes afin de ne pas transformer la politique en cause unique.',[f[2],f[3]]),('literal_detail','Quels acteurs sont explicitement mentionnés ?','Des commerçants, responsables locaux, familles et associations.',r[:2]),('argument_relation','Pourquoi une explication uniquement politique est-elle insuffisante ?','Elle explique les débats officiels mais moins bien les variations entre lieux et groupes.',r[2:4]),('vocabulary_in_context',f'Quel rôle joue « {f[0]} » ?','Il précise une action ou évolution des acteurs qui doit être replacée dans ses contraintes.',[f[0]]),('vocabulary_in_context',f'Comment « {f[1]} » est-il utilisé ?','Il désigne un acteur ou rôle dont la marge d’action doit être reconstruite.',[f[1]]),('vocabulary_in_context',f'Pourquoi « {f[2]} » est-il important ?','Il aide à formuler le mécanisme ou la motivation sans être traité comme cause suffisante.',[f[2]]),('vocabulary_in_context',f'Comment « {f[3]} » qualifie-t-il l’explication ?','Il indique le degré, l’échelle ou la difficulté de la relation causale étudiée.',[f[3]]),('assumption','Pourquoi les options disponibles à l’époque doivent-elles être reconstruites ?','Parce qu’un résultat connu dans le présent peut donner l’illusion que la décision était inévitable.',r[0:2]),('stance','Quelle position le texte adopte-t-il envers une cause politique unique ?','Il reconnaît la politique comme facteur important mais exige de la relier aux mécanismes sociaux, matériels et institutionnels.',r[2:4]),('summary','Résume le chapitre.','La vie des acteurs, leur société et leur politique dans le présent de l’époque sont expliquées par les quatre cibles nouvelles qui rendent visibles action, acteur, mécanisme et qualification causale.',f+r)]

def make(spec,prior,deck):
 text='\n\n'.join(spec['paras']);new=[base.nt(f,text,deck) for f in spec['forms']];reviews=[base.rev(f,prior) for f in spec['reviews']];ids={t['form']:t['id'] for t in new+reviews};q,a=base.qa(items_for(spec),ids)
 return {'id':spec['id'],'language':'fr','cefr':'B2','unit':8,'sequence':spec['sequence'],'revision':1,'title':spec['title'],'passage_type':spec['ptype'],'genre':spec['genre'],'domains':spec['domains'],'topics':spec['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':[{'id':f"fr-b2-u08-g-{spec['sequence']}",'role':'new','description':'historical explanation through chronology, causal qualification, source perspective and counterfactual limits'}],'discourse_targets':[{'id':f"fr-b2-u08-d-{spec['sequence']}",'role':'new','description':'distinguish chronology, mechanism, evidence, competing explanation and source perspective'}],'questions':q,'answer_key':a,'speed_training':{'timed':False,'benchmark_eligible':False,'comprehension_gate':0.8,'new_word_policy':'controlled','notes':'French B2 Unit 08 guarded production batch.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French B2 Unit 08: history and explanation.','Four selected fresh targets; fictional/generic historical scenarios only.']},'paired_text_group':None,'prerequisites':['French B2 Units 01-07 canonical and Unit07 frontier lock PASS'],'difficulty_notes_internal':'B2 historical reasoning: chronology, causality, source comparison, counterargument and multi-causal synthesis.','reader_tags':['unit_role:'+spec['ptype'],'generation_batch','french_b2_u08']}

def checkpoint(groups,deck):
 forms=[f for k in ['p01','p02','p03','p04','p05'] for f in groups[k]];paras=[
 "L’unité historique commence par la chronologie. Un film peut utiliser musique, chanson et montage pour jouer avec l’attention, mais l’explication doit encore établir ce qui vient avant quoi. "+' '.join(usage(f) for f in groups['p01'])+" Ces repères servent à empêcher qu’un événement spectaculaire soit transformé en cause unique simplement parce qu’il est facile à raconter.",
 "La causalité ajoute une deuxième exigence. Une histoire bien écrite ne se contente pas d’aligner un mot après l’autre : elle décrit les mécanismes qui relient conditions, décisions et résultats. "+' '.join(usage(f) for f in groups['p02'])+" Chaque facteur doit être testé contre des explications concurrentes et contre les cas où l’effet attendu n’apparaît pas.",
 "Les sources ajoutent ensuite la perspective. Le ton d’un texte influence la lecture, mais le sens dépend aussi du sujet, du public et de ce que l’auteur pouvait connaître; il ne faut pas imaginer les silences sans indice. "+' '.join(usage(f) for f in groups['p03'])+" Comparer une affirmation précise vaut mieux que classer une source entière comme vraie ou fausse.",
 "Les débats entre historiens ajoutent le contreargument. Un avis peut être élégant, et un lecteur peut aimer un récit beau ou drôle, mais le style ne résout pas le désaccord. "+' '.join(usage(f) for f in groups['p04'])+" Une comparaison solide demande ce que chaque explication rend visible, ce qu’elle laisse de côté et comment elle répond à la meilleure objection.",
 "Enfin, la synthèse relie l’événement à la vie des acteurs. Le présent de l’époque, la société et la politique créent des contraintes sans transformer les personnes en marionnettes. "+' '.join(usage(f) for f in groups['p05'])+" Expliquer consiste alors à montrer comment action, acteurs, intérêts et échelle rendent certains résultats plus plausibles, tout en conservant la possibilité d’autres chemins."
 ];text='\n\n'.join(paras);reviews=[base.cur(f,deck) for f in forms];ids={t['form']:t['id'] for t in reviews}
 its=[('main_claim','Quelle méthode générale l’unité propose-t-elle ?','Relier chronologie, mécanismes, sources, contrearguments et contexte sans réduire l’histoire à une cause unique.',[groups['p01'][0],groups['p02'][0]]),('argument_relation','Pourquoi la chronologie précède-t-elle l’analyse causale ?','Parce qu’une cause doit être située avant son effet et reliée à lui par un mécanisme plausible.',[groups['p01'][1],groups['p02'][0]]),('cross_text_synthesis','Quel lien unit source et contreargument ?','Une source limite ce qu’une explication peut affirmer, tandis qu’un contreargument teste les faits qu’une lecture concurrente explique mieux.',[groups['p03'][0],groups['p04'][0]]),('assumption','Pourquoi reconstruire les options disponibles aux acteurs ?','Pour éviter de traiter le résultat connu comme s’il avait été inévitable dès le départ.',[groups['p01'][1],groups['p05'][0]]),('inference','Pourquoi plusieurs causes peuvent-elles être importantes en même temps ?','Parce qu’elles peuvent agir à des étapes ou échelles différentes et se renforcer ou se limiter mutuellement.',[groups['p02'][2],groups['p05'][3]]),('reference_resolution','Dans la dernière partie, à quoi renvoie « alors » ?','Au moment où l’analyse combine contexte, acteurs, intérêts et alternatives pour construire l’explication.',[groups['p05'][2]]),('stance','Quelle position la synthèse adopte-t-elle envers un récit très élégant ?','Elle accepte sa valeur narrative mais exige que le style reste subordonné à la chronologie, aux sources et aux mécanismes.',[groups['p04'][0]]),('vocabulary_in_context','Comment les vingt cibles nouvelles sont-elles organisées ?','En cinq groupes : chronologie/conflit, causalité, sources, explications concurrentes et synthèse des acteurs/contexte.',forms[:4]),('synthesis','Que doit faire une bonne explication historique lorsqu’une source contredit le récit préféré ?','Réexaminer l’affirmation précise, comparer les perspectives et modifier la force ou la portée de la conclusion si nécessaire.',[groups['p03'][3],groups['p04'][2]]),('summary','Résume l’unité.','L’unité relie les vingt cibles nouvelles pour construire une histoire où chronologie, causalité, sources, désaccords et contexte rendent les choix explicables sans les rendre inévitables.',forms)]
 q,a=base.qa(its,ids)
 return {'id':'fr-b2-u08-p06','language':'fr','cefr':'B2','unit':8,'sequence':48,'revision':1,'title':'Chronologie, causes et sources : expliquer le passé sans fabriquer l’inévitable','passage_type':'checkpoint','genre':'B2 cumulative history checkpoint','domains':['educational','public'],'topics':['history and explanation','synthesis','source comparison'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':[],'review_lexical_targets':reviews,'grammar_targets':[{'id':'fr-b2-u08-g-checkpoint','role':'review','description':'synthesize chronology, causal qualification, source perspective and alternatives'}],'discourse_targets':[{'id':'fr-b2-u08-d-checkpoint','role':'review','description':'integrate historical account, causal analysis, source comparison and counterargument'}],'questions':q,'answer_key':a,'speed_training':{'timed':True,'benchmark_eligible':True,'comprehension_gate':0.8,'new_word_policy':'none','notes':'French B2 Unit 08 cumulative checkpoint.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Zero-new Unit08 checkpoint using all 20 selected forms exactly.']},'paired_text_group':None,'prerequisites':['French B2 Unit08 P01-P05'],'difficulty_notes_internal':'B2 synthesis of chronology, causal inference, source limits and competing historical explanations.','reader_tags':['unit_role:checkpoint','generation_batch','french_b2_u08']}

def main():
 for lab,p in [('A1',A1),('A2',A2),('B1',B1),('B2',CANON)]:
  got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
  if got!=EXPECTED[lab]:raise AssertionError(f'{lab} blob drift: {got} != {EXPECTED[lab]}')
 lock=json.loads(LOCK.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'))
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=42 or lock.get('canonical_blob')!=EXPECTED['B2']:raise AssertionError('Unit07 lock mismatch')
 if probe.get('status')!='PASS' or probe.get('b2_source_blob')!=EXPECTED['B2']:raise AssertionError('Unit08 probe mismatch')
 groups=load_selection();selected={f for v in groups.values() for f in v};fresh={x['form'] for x in probe['fresh']}
 if selected-fresh:raise AssertionError(f'selected targets no longer fresh: {sorted(selected-fresh)}')
 load=lambda p:[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 a1,a2,b1,b2=map(load,(A1,A2,B1,CANON));deck=base.deck();prior=base.prior(a1+a2+b1+b2);pid={t.get('id') for r in a1+a2+b1+b2 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};pf={t.get('form') for r in a1+a2+b1+b2 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
 if len(b2)!=42 or b2[-1]['id']!='fr-b2-u07-p06':raise AssertionError('unexpected B2 frontier')
 unit=[make(s,prior,deck) for s in passage_specs(groups)];unit.append(checkpoint(groups,deck));V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')));newids=[];newforms=[]
 if [r['sequence'] for r in unit]!=list(range(43,49)) or [r['id'] for r in unit]!=[f'fr-b2-u08-p{i:02d}' for i in range(1,7)]:raise AssertionError('Unit08 sequence/id failure')
 for r in unit:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:8]]}")
  if not 350<=r['word_count']<=550:raise AssertionError(f"{r['id']}: word band {r['word_count']}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: assessment count")
  if r['sequence']<=47 and len(r['new_lexical_targets'])!=4:raise AssertionError(f"{r['id']}: expected four new")
  if r['sequence']==48 and r['new_lexical_targets']:raise AssertionError('P06 must have zero new')
  local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(tid not in local for tid in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage failure")
  for t in r['new_lexical_targets']:
   src=deck.get(t['form'])
   if t['id'] in pid or t['form'] in pf or not src or t['source_rank']!=src['rank'] or t['id']!=base.tid(src['rank']) or base.cnt(r['text'],t['form'])!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: new target drift {t}")
   newids.append(t['id']);newforms.append(t['form'])
  for t in r['review_lexical_targets']:
   if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
 if len(newids)!=20 or len(set(newids))!=20 or len(set(newforms))!=20 or set(newforms)!=selected:raise AssertionError('Unit08 target selection/uniqueness failure')
 CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in b2+unit),encoding='utf-8')
 print(json.dumps({'status':'PASS','unit':8,'theme':'history and explanation','b2_passages':48,'questions':60,'answers':60,'new_targets':20,'selected_groups':groups,'word_counts':{r['id']:r['word_count'] for r in unit}},ensure_ascii=False))
if __name__=='__main__':main()
