#!/usr/bin/env python3
"""Append French B1 Unit 05 (sequences 25-30) as one guarded transfer batch."""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit04 as prev
base=prev.base

REPO=Path(__file__).resolve().parents[2]
A1=REPO/'reading'/'french'/'a1'/'passages.jsonl'
A2=REPO/'reading'/'french'/'a2'/'passages.jsonl'
CANON=REPO/'reading'/'french'/'b1'/'passages.jsonl'
SCHEMA=REPO/'reading'/'schema'/'passage.schema.json'
EXPECTED_A1_BLOB='0493a2fa13e51b5997db05e91cdea4d8dc5e647b'
EXPECTED_A2_BLOB='d0a80b8866071f426019aa0ad143e1d270dba4de'
EXPECTED_B1_BLOB='0c629bd045f0c86a501f5efcd1b5cd46ed76f1ce'
FORMS=('clair','reprendre','déranger','empêcher','récupérer','sinon','ancien','vivant','honneur','inviter','remercier','mériter','prix','réaliser','arranger')

SPECS=[
{
'id':'fr-b1-u05-p01','sequence':25,'ptype':'instructional','title':'Reprendre avec un message clair sans déranger davantage','genre':'incident communication narrative','domains':['professional','public'],'topics':['communication','incident response','evidence'],'forms':['clair','reprendre','déranger'],'reviews':['probablement','prouver','sérieux'],
'paragraphs':[
"Dans un centre de formation, une séance en ligne s’interrompt pendant quinze minutes à cause d’un problème de réseau. Quand la connexion revient, plusieurs participants écrivent en même temps au support. Camille doit reprendre la présentation, mais elle veut d’abord donner un message clair. Elle explique que l’équipe sait seulement qu’une partie du bâtiment a perdu l’accès au réseau. Il est probablement trop tôt pour annoncer une cause précise, car aucun test ne permet encore de la prouver.",
"Un collègue propose d’envoyer immédiatement un long compte rendu technique. Camille pense qu’un message sérieux peut être plus court : dire ce qui est confirmé, ce qui reste en cours de vérification et quand une nouvelle information sera donnée. Elle évite aussi de déranger les techniciens avec cinq demandes identiques. Une personne centralise les questions pendant que les autres reprennent leurs tâches. Ainsi, reprendre l’activité ne signifie pas faire comme si rien ne s’était passé ; cela signifie avancer avec une information claire et limitée.",
"Trente minutes plus tard, le support identifie un équipement défectueux. Camille met à jour le groupe et précise ce que les tests peuvent réellement prouver. Elle remarque qu’un incident peut déranger les participants deux fois : d’abord par la panne elle-même, puis par des messages contradictoires. Pour éviter cette seconde difficulté, elle garde un ton clair, distingue le probable du certain et indique les prochaines étapes. Cette méthode permet de reprendre le travail sans transformer une hypothèse en conclusion et sans ajouter du bruit à une situation déjà sérieuse."
],
'grammar':[{'id':'fr-b1-u05-reprendre-sans','role':'new','description':'use reprendre and sans + infinitive to describe controlled resumption after disruption'}],
'discourse':[{'id':'fr-b1-u05-incident-message','role':'new','description':'separate confirmed facts, probable explanations and next communication steps'}],
'items':[
('gist','Quelle stratégie de communication Camille choisit-elle ?','Elle reprend l’activité avec un message clair qui sépare les faits confirmés des hypothèses.',['reprendre','clair']),
('literal_detail','Combien de temps la séance est-elle interrompue ?','Quinze minutes.',['reprendre']),
('cause_effect','Pourquoi Camille évite-t-elle un diagnostic immédiat ?','Parce qu’aucun test ne permet encore de prouver la cause précise.',['prouver']),
('vocabulary_in_context','Que signifie « clair » lorsqu’il décrit le message ?','Facile à comprendre et limité aux informations utiles.',['clair']),
('vocabulary_in_context','Que signifie « déranger » les techniciens ?','Interrompre ou gêner inutilement leur travail.',['déranger']),
('inference','Pourquoi un message sérieux peut-il être court ?','Parce que sa qualité dépend de la précision des faits et des prochaines étapes, pas de sa longueur.',['sérieux']),
('motive','Pourquoi une seule personne centralise-t-elle les questions ?','Pour éviter de déranger plusieurs fois les techniciens avec les mêmes demandes.',['déranger']),
('grammar_in_context','Que montre « reprendre le travail sans transformer une hypothèse en conclusion » ?','La reprise est possible tout en conservant une limite sur ce qui est encore incertain.',['reprendre']),
('cloze_transfer','Complète : Après l’incident, Camille veut _____ la présentation avec un message clair.','reprendre',['reprendre','clair']),
('summary','Résume la méthode de Camille.','Elle reprend avec un message clair, évite de déranger le support et distingue ce qui est probablement vrai de ce que les tests peuvent prouver.',['reprendre','clair','déranger','probablement','prouver'])
]},
{
'id':'fr-b1-u05-p02','sequence':26,'ptype':'reinforcement','title':'Récupérer le fichier, sinon reconstruire autrement','genre':'digital recovery problem-solving narrative','domains':['educational','professional'],'topics':['file recovery','backup','creative work'],'forms':['empêcher','récupérer','sinon'],'reviews':['scène','spécial','créer'],
'paragraphs':[
"La veille d’une représentation, l’équipe découvre qu’un ordinateur ne trouve plus le fichier vidéo utilisé sur scène. Cette vidéo doit créer un effet spécial pendant le dernier passage. Sami veut immédiatement refaire le montage, mais Camille propose d’abord de vérifier les sauvegardes. Le but est de récupérer le fichier existant si possible et d’empêcher une reconstruction inutile. Sinon, le groupe devra créer une version plus simple avec les images encore disponibles.",
"Ils commencent par regarder la corbeille, puis l’historique du logiciel et enfin le dossier partagé. Une copie de la veille apparaît dans le stockage en ligne. Camille peut récupérer le montage presque complet, mais deux modifications récentes manquent. Pour empêcher la même situation de se reproduire, elle active une sauvegarde automatique du dossier de scène. Elle note aussi une règle claire : avant chaque répétition importante, vérifier qu’une copie récente existe sur un second emplacement ; sinon, exporter une version de secours.",
"Le groupe termine les deux modifications manquantes sans retarder la répétition. L’effet spécial reste identique et la scène peut se dérouler comme prévu. Camille comprend qu’une bonne procédure de récupération ne cherche pas seulement à récupérer ce qui a disparu. Elle doit aussi empêcher la prochaine perte. Le mot sinon devient utile dans la procédure, car il oblige l’équipe à prévoir une solution de remplacement : récupérer la copie principale ; sinon utiliser la version exportée ; sinon créer un effet plus simple. Cette succession réduit le stress et donne plusieurs chemins vers le même objectif."
],
'grammar':[{'id':'fr-b1-u05-sinon-fallback','role':'new','description':'use sinon to express explicit fallback branches in a recovery procedure'}],
'discourse':[{'id':'fr-b1-u05-recovery-ladder','role':'new','description':'build a staged recovery plan that preserves a creative goal while adding prevention'}],
'items':[
('gist','Quelle méthode l’équipe utilise-t-elle pour résoudre la perte du fichier ?','Elle essaie de récupérer une sauvegarde, puis prévoit des solutions de remplacement avec « sinon ».',['récupérer','sinon']),
('literal_detail','Où trouve-t-elle une copie de la veille ?','Dans le stockage en ligne.',['récupérer']),
('cause_effect','Pourquoi active-t-elle une sauvegarde automatique ?','Pour empêcher qu’une perte semblable bloque une prochaine répétition.',['empêcher']),
('vocabulary_in_context','Que signifie « récupérer » le fichier ?','Retrouver et restaurer une copie utilisable du fichier.',['récupérer']),
('vocabulary_in_context','Quel rôle joue « sinon » ?','Il introduit la solution de remplacement si l’étape précédente échoue.',['sinon']),
('inference','Pourquoi le groupe ne recommence-t-il pas immédiatement tout le montage ?','Parce qu’une copie peut préserver le travail déjà réalisé et éviter un effort inutile.',['récupérer']),
('motive','Pourquoi garder une version exportée en plus du dossier principal ?','Pour disposer d’un second chemin si le projet principal ne peut pas être récupéré.',['sinon']),
('grammar_in_context','Comment « sinon » organise-t-il la dernière procédure ?','Il relie plusieurs branches successives : solution principale puis solutions de secours.',['sinon']),
('cloze_transfer','Complète : Une sauvegarde peut _____ une petite erreur de devenir une perte complète.','empêcher',['empêcher']),
('summary','Résume la solution.','L’équipe récupère le fichier de scène, ajoute une sauvegarde pour empêcher une nouvelle perte et prépare des options avec « sinon » afin de préserver l’effet spécial à créer.',['récupérer','empêcher','sinon','scène','spécial','créer'])
]},
{
'id':'fr-b1-u05-p03','sequence':27,'ptype':'interleaved','title':'Un ancien bateau raconté comme une histoire vivante','genre':'harbor museum interpretive narrative','domains':['educational','public'],'topics':['local history','museum interpretation','harbor'],'forms':['ancien','vivant','honneur'],'reviews':['rejoindre','ligne','bout'],
'paragraphs':[
"Au musée du port, Camille rejoint une visite consacrée à un ancien bateau de sauvetage. Le bateau est installé au bout d’une longue salle qui suit, comme une ligne, l’évolution du port. Une plaque explique qu’il a servi pendant plusieurs décennies. Le musée veut rendre cette histoire vivante sans inventer des aventures qui ne sont pas documentées. Pour cela, il combine des objets, des photos, des cartes et des témoignages enregistrés par d’anciens membres d’équipage.",
"La guide raconte qu’une cérémonie annuelle rend honneur aux personnes qui ont participé aux opérations de secours. Elle précise toutefois que rendre honneur ne signifie pas transformer chaque décision passée en geste parfait. Certains rapports montrent des erreurs, des hésitations et des changements de procédure. Cette complexité rend l’histoire plus vivante : les visiteurs voient des personnes qui apprennent, corrigent leurs méthodes et travaillent dans des conditions difficiles. L’ancien matériel permet aussi de comprendre pourquoi certaines décisions prenaient plus de temps qu’aujourd’hui.",
"Camille suit la ligne chronologique jusqu’au bout et compare les outils de plusieurs périodes. Elle comprend que le mot ancien ne signifie pas inutile et que vivant ne signifie pas spectaculaire. Un récit vivant relie des faits précis à des choix humains compréhensibles. Rendre honneur aux équipes consiste alors à reconnaître leur travail réel, y compris les améliorations qu’elles ont dû apporter. En quittant le musée, Camille peut rejoindre les différentes parties du récit : l’ancien bateau, les documents, les voix enregistrées et la cérémonie d’honneur forment ensemble une histoire plus solide qu’une simple légende héroïque."
],
'grammar':[{'id':'fr-b1-u05-ancien-vivant','role':'new','description':'contrast adjective meanings to avoid equating old with useless or vivid with exaggerated'}],
'discourse':[{'id':'fr-b1-u05-honor-with-complexity','role':'new','description':'honor historical actors while retaining documented uncertainty and mistakes'}],
'items':[
('gist','Comment le musée rend-il l’histoire du bateau vivante ?','Il relie un ancien bateau à des documents, des objets et des témoignages sans inventer les faits.',['ancien','vivant']),
('literal_detail','Où se trouve le bateau dans la salle ?','Au bout d’une longue salle chronologique.',['bout']),
('cause_effect','Pourquoi la guide mentionne-t-elle aussi les erreurs ?','Parce que rendre honneur aux équipes ne demande pas de présenter chaque décision comme parfaite.',['honneur']),
('vocabulary_in_context','Que signifie « ancien » ici ?','Qui appartient à une période passée.',['ancien']),
('vocabulary_in_context','Que signifie « vivant » pour un récit ?','Concret et humain, capable de rendre les choix compréhensibles sans les exagérer.',['vivant']),
('inference','Pourquoi les outils anciens aident-ils à juger les décisions passées ?','Ils montrent les contraintes techniques dans lesquelles les équipes devaient agir.',['ancien']),
('motive','Pourquoi le musée organise-t-il une cérémonie ?','Pour rendre honneur aux personnes qui ont participé aux opérations de secours.',['honneur']),
('reference_resolution','Dans « cette complexité rend l’histoire plus vivante », à quoi renvoie « cette complexité » ?','Aux réussites, erreurs, hésitations et corrections présentes dans les documents.',['vivant']),
('cloze_transfer','Complète : La cérémonie veut rendre _____ aux équipes du port.','honneur',['honneur']),
('summary','Résume la visite.','Camille rejoint une ligne chronologique jusqu’au bout et découvre comment un ancien bateau peut soutenir une histoire vivante qui rend honneur aux équipes sans effacer leurs difficultés.',['rejoindre','ligne','bout','ancien','vivant','honneur'])
]},
{
'id':'fr-b1-u05-p04','sequence':28,'ptype':'transfer','title':'Inviter, remercier et reconnaître ce qui mérite du temps','genre':'volunteer coordination narrative','domains':['public','professional'],'topics':['volunteering','coordination','recognition'],'forms':['inviter','remercier','mériter'],'reviews':['normal','système','prévenir'],
'paragraphs':[
"Une association prépare une journée de nettoyage dans plusieurs parcs. Son système d’inscription envoie normalement un message automatique aux bénévoles. Cette fois, Camille remarque qu’un groupe n’a rien reçu. Elle veut prévenir une confusion avant le matin de l’activité. Plutôt que d’attendre, elle décide d’inviter directement les personnes concernées à confirmer leur présence et explique que le problème vient du système, pas de leur inscription.",
"La coordinatrice profite de l’occasion pour revoir la façon de remercier les bénévoles. Jusqu’ici, un message identique est envoyé à tout le monde. Camille propose de remercier chaque équipe en mentionnant un résultat concret : sacs ramassés, zones triées ou matériel préparé. Elle ne veut pas créer une compétition. Selon elle, le temps donné par les bénévoles mérite une reconnaissance précise, même lorsque la tâche paraît normale. Cette attention peut aussi prévenir l’impression que certaines contributions passent inaperçues.",
"Après l’activité, l’association décide d’inviter les responsables de chaque secteur à une courte réunion de retour. Ils identifient ce qui mérite d’être conservé et ce qui doit changer dans le système d’inscription. Camille prend quelques minutes pour remercier les personnes qui ont signalé le problème tôt, car leur message a permis de prévenir plusieurs absences. Elle retient qu’inviter et remercier ne sont pas de simples gestes de politesse. Bien utilisés, ils soutiennent un système de coopération : inviter donne une place claire à quelqu’un, remercier reconnaît son effort et décider ce qui mérite du temps aide le groupe à améliorer ses pratiques."
],
'grammar':[{'id':'fr-b1-u05-meriter-inf','role':'new','description':'use mériter + noun/infinitive-style complements to evaluate what deserves attention or recognition'}],
'discourse':[{'id':'fr-b1-u05-volunteer-recognition','role':'new','description':'connect invitation, concrete thanks and process improvement in volunteer coordination'}],
'items':[
('gist','Quelle idée relie l’invitation et les remerciements ?','Les deux rendent la participation visible et soutiennent un système de coopération.',['inviter','remercier']),
('literal_detail','Quel problème Camille remarque-t-elle ?','Un groupe de bénévoles n’a pas reçu le message automatique.',['système']),
('cause_effect','Pourquoi contacte-t-elle directement les personnes ?','Pour prévenir une confusion et confirmer leur présence.',['prévenir','inviter']),
('vocabulary_in_context','Que signifie « remercier » ici ?','Exprimer une reconnaissance précise pour le temps et le travail donnés.',['remercier']),
('vocabulary_in_context','Que signifie « mériter » dans ce passage ?','Être suffisamment important ou utile pour recevoir du temps, de l’attention ou de la reconnaissance.',['mériter']),
('inference','Pourquoi Camille préfère-t-elle des remerciements concrets ?','Parce qu’ils montrent que la contribution réelle de chaque équipe a été remarquée.',['remercier']),
('motive','Pourquoi organiser une réunion après l’activité ?','Pour décider ce qui mérite d’être conservé ou changé dans le système.',['mériter','système']),
('grammar_in_context','Comment « mérite » fonctionne-t-il dans « le temps donné mérite une reconnaissance » ?','Il évalue la contribution comme digne d’une reconnaissance.',['mériter']),
('cloze_transfer','Complète : L’association veut _____ les bénévoles après l’activité.','remercier',['remercier']),
('summary','Résume la coordination.','Camille utilise le système pour prévenir les problèmes, choisit d’inviter directement les personnes concernées, veut remercier concrètement les bénévoles et décide ce qui mérite d’être amélioré.',['système','prévenir','inviter','remercier','mériter'])
]},
{
'id':'fr-b1-u05-p05','sequence':29,'ptype':'transfer','title':'Arranger le plan pour réaliser le projet au bon prix','genre':'community budget planning narrative','domains':['professional','public'],'topics':['budget','planning','tradeoffs'],'forms':['prix','réaliser','arranger'],'reviews':['relation','reconnaître','plutôt'],
'paragraphs':[
"Un centre communautaire veut réaliser une petite exposition photographique avec des travaux d’élèves. Le premier devis dépasse largement le budget. Camille compare le prix de l’impression, des cadres, de l’éclairage et du transport. Elle cherche la relation entre chaque dépense et l’objectif pédagogique. Plutôt que de réduire toutes les lignes du budget de la même manière, elle veut reconnaître quelles dépenses influencent réellement la qualité de l’exposition.",
"L’équipe découvre qu’elle peut arranger le plan de la salle pour utiliser moins de cadres sans montrer moins de photos. Deux murs accueilleront des séries d’images sous un même cadre large, tandis que les œuvres principales garderont un cadre individuel. Le nouveau prix devient acceptable. Camille précise toutefois que réaliser un projet moins cher ne signifie pas choisir automatiquement l’option au prix le plus bas. Un matériau très fragile pourrait coûter moins aujourd’hui mais demander un remplacement rapide.",
"Le groupe décide donc de réaliser une version qui équilibre coût, durée et lisibilité. Il demande au fournisseur d’arranger la livraison afin que tout arrive le même jour, ce qui réduit aussi le prix du transport. Camille reconnaît que chaque choix crée une relation entre plusieurs contraintes. Elle préfère arranger le plan plutôt que supprimer une partie importante de l’exposition. Au final, le centre peut réaliser le projet dans son budget, conserver les objectifs essentiels et expliquer clairement pourquoi certains éléments méritent un prix plus élevé que d’autres. Cette justification transforme le budget en outil de décision plutôt qu’en simple liste de nombres."
],
'grammar':[{'id':'fr-b1-u05-plutot-arranger','role':'new','description':'combine plutôt que with infinitive choices to articulate budget tradeoffs'}],
'discourse':[{'id':'fr-b1-u05-budget-tradeoff','role':'new','description':'connect price to function and rearrange a plan before cutting essential outcomes'}],
'items':[
('gist','Comment l’équipe réduit-elle le budget ?','Elle arrange le plan de l’exposition et compare le prix de chaque choix à sa fonction.',['arranger','prix']),
('literal_detail','Quelle modification réduit le nombre de cadres ?','Plusieurs photos sont regroupées sous un même grand cadre.',['arranger']),
('cause_effect','Pourquoi le prix le plus bas n’est-il pas toujours le meilleur ?','Parce qu’un matériau fragile peut demander un remplacement et coûter davantage ensuite.',['prix']),
('vocabulary_in_context','Que signifie « réaliser » le projet ?','Le mener à terme et produire concrètement l’exposition prévue.',['réaliser']),
('vocabulary_in_context','Que signifie « arranger » le plan ?','Le modifier ou l’organiser de manière plus adaptée aux contraintes.',['arranger']),
('inference','Pourquoi Camille examine-t-elle la relation entre dépense et objectif ?','Pour reconnaître quelles dépenses protègent réellement la qualité du projet.',['relation','reconnaître']),
('motive','Pourquoi préfère-t-elle arranger plutôt que supprimer ?','Pour respecter le budget sans retirer une partie essentielle de l’exposition.',['plutôt','arranger']),
('grammar_in_context','Que met en contraste « plutôt que » ?','La préférence pour réorganiser le projet au lieu de supprimer un élément important.',['plutôt']),
('cloze_transfer','Complète : Le centre veut _____ l’exposition sans dépasser son budget.','réaliser',['réaliser']),
('summary','Résume la décision budgétaire.','L’équipe compare le prix et la relation de chaque dépense avec l’objectif, choisit d’arranger le plan plutôt que supprimer des éléments et peut finalement réaliser le projet.',['prix','relation','arranger','plutôt','réaliser'])
]}
]

CHECKPOINT={
'id':'fr-b1-u05-p06','sequence':30,'ptype':'checkpoint','title':'Communiquer, récupérer, comprendre et ajuster','genre':'B1 cumulative response-and-planning summary','domains':['educational','public','professional'],'topics':['communication','recovery','history','coordination','budget'],'paragraphs':[
"Camille apprend qu’une réponse utile commence souvent par une structure claire. Après un incident, elle peut reprendre le travail sans déranger davantage les personnes qui cherchent la cause. Dans un projet numérique, une sauvegarde peut empêcher une perte importante et permettre de récupérer un fichier ; sinon, une solution de remplacement doit être prête. Ces méthodes ne suppriment pas l’incertitude, mais elles empêchent qu’un petit problème devienne automatiquement une crise plus grande.",
"Au musée, un ancien bateau peut soutenir un récit vivant qui rend honneur aux équipes sans cacher leurs erreurs. Dans une association, inviter des bénévoles, les remercier précisément et décider ce qui mérite du temps rendent la coopération plus visible. Dans un budget, le prix doit être relié à une fonction : on peut arranger un plan pour réaliser un projet autrement plutôt que supprimer immédiatement ce qui coûte le plus.",
"Les unités précédentes restent présentes dans ces décisions. Camille distingue ce qui est probablement vrai de ce qu’un test peut prouver dans un travail sérieux. Elle sait créer une scène avec un effet spécial utile, rejoindre une ligne jusqu’au bon bout, comprendre quand un signal est normal dans un système conçu pour prévenir un problème et reconnaître la relation entre plusieurs interprétations. Elle retient surtout qu’une bonne méthode offre plusieurs chemins : reprendre avec une information claire, récupérer ce qui peut l’être, honorer les faits anciens sans les simplifier, inviter et remercier les personnes concernées, puis arranger les contraintes afin de réaliser l’objectif au prix justifié."
],
'grammar':[{'id':'fr-b1-u05-cumulative-branches','role':'integration','description':'integrate fallback branches, evaluation and infinitive choices across response and planning contexts'}],
'discourse':[{'id':'fr-b1-u05-response-to-plan','role':'integration','description':'synthesize communication, recovery, historical interpretation, coordination and budget adjustment'}],
'items':[
('gist','Quelle idée générale relie les cinq situations ?','Construire une réponse claire, prévoir des solutions de remplacement et ajuster le plan sans perdre l’objectif.',['clair','arranger']),
('literal_detail','Quels mots résument la première situation ?','clair, reprendre et déranger',['clair','reprendre','déranger']),
('cause_effect','Pourquoi une sauvegarde est-elle utile ?','Elle peut empêcher une perte et permettre de récupérer le fichier ; sinon une autre solution est prévue.',['empêcher','récupérer','sinon']),
('vocabulary_in_context','Quels mots décrivent la visite historique ?','ancien, vivant et honneur',['ancien','vivant','honneur']),
('vocabulary_in_context','Quels mots décrivent la coordination des bénévoles ?','inviter, remercier et mériter',['inviter','remercier','mériter']),
('inference','Pourquoi le prix n’est-il pas traité seul ?','Parce qu’il doit être relié à la fonction de la dépense et à l’objectif à réaliser.',['prix','réaliser']),
('motive','Pourquoi Camille préfère-t-elle arranger certaines contraintes ?','Pour conserver l’objectif essentiel plutôt que supprimer automatiquement un élément coûteux.',['arranger']),
('reference_resolution','Dans « sinon, une solution de remplacement », à quelle situation renvoie « sinon » ?','Au cas où la récupération principale du fichier échoue.',['sinon','récupérer']),
('cloze_transfer','Complète : Une procédure claire doit _____ qu’un petit problème devienne une crise.','empêcher',['empêcher']),
('summary','Résume l’unité en une phrase.','Camille apprend à reprendre clairement sans déranger, récupérer ou prévoir sinon, comprendre un récit ancien et vivant avec honneur, inviter et remercier ce qui mérite de l’attention, puis arranger le prix pour réaliser un projet.',['reprendre','clair','déranger','récupérer','sinon','ancien','vivant','honneur','inviter','remercier','mériter','arranger','prix','réaliser'])
]}

def text_of(s): return '\n\n'.join(s['paragraphs'])
def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s['items'],ids); text=text_of(s)
    return {'id':s['id'],'language':'fr','cefr':'B1','unit':5,'sequence':s['sequence'],'revision':1,'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],'topics':s['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':q,'answer_key':a,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'French B1 Unit 05 guarded transfer batch; final language-wide audit deferred.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French B1 Unit 05 transfer batch.','All-prior-French freshness, source identity, B1 word band, exact deliberate-review visibility, question linkage and zero-new checkpoint are enforced.']},'paired_text_group':None,'prerequisites':['French B1 Units 01-04 canonical corpus'],'difficulty_notes_internal':'B1 transfer across communication, digital recovery, historical interpretation, volunteer coordination and budget planning.','reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_b1_u05']}

def build(a1,a2,b1,D):
    prior=base.prior(a1+a2+b1); bad=[]
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    for f in FORMS:
        if f not in D: bad.append(f+':missing_lexicon')
        elif base.tid(D[f]['rank']) in prior_ids or f in prior_forms or prior.get(f): bad.append(f+':already_deliberate')
    if bad: raise AssertionError('B1 Unit05 candidate failures: '+', '.join(bad))
    review_sets=[['probablement','prouver','sérieux'],['scène','spécial','créer'],['rejoindre','ligne','bout'],['normal','système','prévenir'],['relation','reconnaître','plutôt']]
    out=[]
    for s,rfs in zip(SPECS,review_sets):
        text=text_of(s); new=[base.nt(f,text,D) for f in s['forms']]; reviews=[base.rev(f,prior) for f in rfs]
        ids={t['form']:t['id'] for t in new+reviews}; out.append(mk(s,new,reviews,ids))
    reviews=[base.cur(f,D) for f in FORMS]; ids={t['form']:t['id'] for t in reviews}; out.append(mk(CHECKPOINT,[],reviews,ids,True))
    return out

def main():
    for path,expected,label in [(A1,EXPECTED_A1_BLOB,'A1'),(A2,EXPECTED_A2_BLOB,'A2'),(CANON,EXPECTED_B1_BLOB,'B1')]:
        blob=subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
        if blob!=expected: raise AssertionError(f'{label} blob drift: {blob} != {expected}')
    a1=[json.loads(x) for x in A1.read_text(encoding='utf-8').splitlines() if x.strip()]
    a2=[json.loads(x) for x in A2.read_text(encoding='utf-8').splitlines() if x.strip()]
    b1=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(a1)!=60 or len(a2)!=60 or len(b1)!=24 or b1[-1]['id']!='fr-b1-u04-p06': raise AssertionError('unexpected prerequisite frontier')
    D=base.deck(); unit=build(a1,a2,b1,D); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    if [r['sequence'] for r in unit]!=list(range(25,31)) or [r['id'] for r in unit]!=[f'fr-b1-u05-p{i:02d}' for i in range(1,7)]: raise AssertionError('B1 Unit05 continuity failure')
    newids=[]; newforms=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 220<=r['word_count']<=350: raise AssertionError(f"{r['id']}: B1 word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        if r['sequence']<=29 and len(r['new_lexical_targets'])!=3: raise AssertionError(f"{r['id']}: calibrated Unit05 load must be 3")
        amap={a['question_id']:a['id'] for a in r['answer_key']}
        decl={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[]) if isinstance(t,dict)}
        for q in r['questions']:
            if amap.get(q['id'])!=q['answer_id'] or any(x not in decl for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} {q['id']}: linkage/target declaration")
        for t in r['new_lexical_targets']:
            s=D.get(t['form'])
            if t['id'] in prior_ids or t['form'] in prior_forms or not s or t['source_rank']!=s['rank'] or t['id']!=base.tid(s['rank']) or base.cnt(r['text'],t['form'])!=t['exposures_in_text']: raise AssertionError(f"{r['id']}: source/exposure/freshness drift {t}")
            newids.append(t['id']); newforms.append(t['form'])
        for t in r['review_lexical_targets']:
            if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if len(newids)!=15 or len(set(newids))!=15 or len(set(newforms))!=15 or unit[-1]['new_lexical_targets']!=[]: raise AssertionError('B1 Unit05 lexical-cycle invariant')
    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in b1+unit),encoding='utf-8')
    print(json.dumps({'status':'PASS','level':'B1','unit':5,'appended_passages':6,'b1_passages':30,'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':D[f]['rank'],'id':base.tid(D[f]['rank'])} for f in FORMS],'questions':60,'answers':60,'p06_new_targets':0},ensure_ascii=False))

if __name__=='__main__': main()
