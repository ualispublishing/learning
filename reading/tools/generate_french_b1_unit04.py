#!/usr/bin/env python3
"""Append French B1 Unit 04 (sequences 19-24) as one guarded transfer batch."""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_a2_unit03 as base

REPO=Path(__file__).resolve().parents[2]
A1=REPO/'reading'/'french'/'a1'/'passages.jsonl'
A2=REPO/'reading'/'french'/'a2'/'passages.jsonl'
CANON=REPO/'reading'/'french'/'b1'/'passages.jsonl'
SCHEMA=REPO/'reading'/'schema'/'passage.schema.json'
EXPECTED_A1_BLOB='0493a2fa13e51b5997db05e91cdea4d8dc5e647b'
EXPECTED_A2_BLOB='d0a80b8866071f426019aa0ad143e1d270dba4de'
EXPECTED_B1_BLOB='8dfb17e274d33227c356b16bad00624f3779342f'
FORMS=('probablement','prouver','recherche','scène','voix','créer','rejoindre','ligne','bout','normal','système','prévenir','relation','reconnaître','présent')

SPECS=[
{
'id':'fr-b1-u04-p01','sequence':19,'ptype':'instructional','title':'Une recherche qui ne cherche pas à prouver trop vite','genre':'citizen-science field report','domains':['educational','public'],'topics':['water quality','research method','evidence'],'forms':['probablement','prouver','recherche'],'reviews':['zone','séparer','morceau'],
'paragraphs':[
"Pour un projet de sciences, Camille retourne dans la zone humide étudiée le mois précédent. Cette fois, la classe mène une recherche sur la qualité de l’eau après plusieurs jours de pluie. À première vue, l’eau paraît plus sombre près du chemin. Certains élèves pensent que la pluie a probablement transporté davantage de terre vers le bassin. Camille rappelle cependant qu’une observation visuelle ne suffit pas à prouver la cause du changement.",
"L’équipe décide de séparer la zone en trois secteurs et de prélever un petit morceau de végétation ainsi qu’un échantillon d’eau dans chacun. La recherche compare ensuite la clarté de l’eau, la température et la quantité de particules visibles. Les résultats montrent une différence nette près du chemin, mais ils ne peuvent pas prouver que la pluie est la seule cause. Des travaux ont aussi eu lieu à proximité pendant la semaine, ce qui fournit une autre explication possible.",
"Dans son compte rendu, Camille écrit qu’il est probablement raisonnable de poursuivre l’hypothèse liée au ruissellement, tout en signalant les autres facteurs. Elle comprend qu’une bonne recherche n’a pas pour objectif de prouver l’idée préférée du groupe. Elle doit plutôt séparer les observations, décrire chaque morceau de preuve et indiquer ce qui reste incertain. Cette prudence ne rend pas le résultat moins utile : elle montre précisément quelle conclusion les données permettent de soutenir et quelle question demande encore une nouvelle mesure."
],
'grammar':[{'id':'fr-b1-u04-probablement-modal','role':'new','description':'use probablement to mark a supported but non-certain interpretation'}],
'discourse':[{'id':'fr-b1-u04-research-hypothesis','role':'new','description':'distinguish observation, plausible hypothesis and what the data can actually prove'}],
'items':[
('gist','Quelle règle de recherche Camille applique-t-elle ?','Elle distingue ce qui est probable de ce que les données peuvent réellement prouver.',['probablement','prouver','recherche']),
('literal_detail','En combien de secteurs l’équipe décide-t-elle de séparer la zone ?','En trois secteurs.',['séparer','zone']),
('cause_effect','Pourquoi les résultats ne prouvent-ils pas que la pluie est la seule cause ?','Parce que des travaux proches peuvent aussi expliquer une partie du changement.',['prouver']),
('vocabulary_in_context','Que signifie « probablement » dans le rapport ?','Que l’explication paraît vraisemblable sans être certaine.',['probablement']),
('vocabulary_in_context','Que signifie « recherche » ici ?','Une démarche organisée pour recueillir et comparer des observations.',['recherche']),
('inference','Pourquoi Camille considère-t-elle la prudence comme utile ?','Parce qu’elle permet de savoir exactement quelle conclusion est soutenue et quelle question reste ouverte.',['recherche']),
('reference_resolution','Dans « elle doit plutôt séparer les observations », à quoi renvoie « elle » ?','À une bonne recherche.',['recherche']),
('grammar_in_context','Quel effet a « probablement » sur l’hypothèse du ruissellement ?','Le mot réduit le degré de certitude et présente l’hypothèse comme plausible plutôt que prouvée.',['probablement','prouver']),
('cloze_transfer','Complète : Un seul résultat ne suffit pas toujours à _____ une cause.','prouver',['prouver']),
('summary','Résume la méthode du groupe.','La recherche sépare la zone, examine chaque morceau de preuve et distingue ce qui est probablement vrai de ce qu’elle peut prouver.',['recherche','séparer','zone','morceau','probablement','prouver'])
]},
{
'id':'fr-b1-u04-p02','sequence':20,'ptype':'reinforcement','title':'Créer une scène où chaque voix reste claire','genre':'theatre rehearsal narrative','domains':['educational','cultural'],'topics':['theatre','rehearsal','sound design'],'forms':['scène','voix','créer'],'reviews':['causer','rapide','agir'],
'paragraphs':[
"La classe prépare une courte représentation pour la soirée de l’école. Sur scène, quatre élèves doivent parler pendant qu’un bruit de rue est diffusé en arrière-plan. À la première répétition, le volume est si fort qu’il couvre presque chaque voix. Sami propose une solution rapide : supprimer complètement le son. Camille préfère agir autrement, car ce bruit aide à créer l’ambiance de la scène et explique pourquoi les personnages doivent parfois se rapprocher pour s’entendre.",
"Le groupe cherche ce qui peut causer la perte de clarté. Le problème vient moins des acteurs que de deux enceintes placées trop près du devant de la scène. Les élèves les déplacent, réduisent légèrement le volume et demandent à chaque personne de projeter sa voix vers le public. Ils enregistrent ensuite trente secondes pour vérifier le résultat. L’action est rapide, mais elle repose sur un problème identifié plutôt que sur un changement au hasard.",
"À la deuxième répétition, la scène garde son atmosphère et chaque voix devient compréhensible. La professeure souligne que créer un effet théâtral ne signifie pas ajouter le plus de sons possible. Il faut décider ce que chaque élément doit apporter. Camille retient aussi qu’une difficulté peut causer plusieurs réactions possibles : supprimer, déplacer, réduire ou modifier la façon d’agir. Dans ce cas, l’équipe a réussi à créer une scène plus lisible en conservant l’idée originale et en ajustant seulement ce qui empêchait les voix d’atteindre le public."
],
'grammar':[{'id':'fr-b1-u04-chaque-voix','role':'new','description':'use distributive chaque to track individual voices inside a group performance'}],
'discourse':[{'id':'fr-b1-u04-stage-sound-balance','role':'new','description':'diagnose a performance problem and preserve the artistic purpose while making speech intelligible'}],
'items':[
('gist','Quel compromis l’équipe trouve-t-elle ?','Elle conserve le bruit utile à la scène tout en rendant chaque voix compréhensible.',['scène','voix']),
('literal_detail','Qu’est-ce qui peut causer la perte de clarté ?','Deux enceintes placées trop près du devant de la scène.',['causer','scène']),
('cause_effect','Pourquoi Camille refuse-t-elle de supprimer tout le son ?','Parce qu’il aide à créer l’ambiance et soutient le sens de la scène.',['créer','scène']),
('vocabulary_in_context','Que désigne « scène » ici ?','L’espace et la séquence théâtrale où les élèves jouent.',['scène']),
('vocabulary_in_context','Que désigne « voix » ?','Le son produit par une personne lorsqu’elle parle.',['voix']),
('inference','Pourquoi l’action rapide reste-t-elle méthodique ?','Parce que l’équipe identifie d’abord la cause probable puis modifie seulement les éléments concernés.',['rapide','agir']),
('motive','Pourquoi les élèves enregistrent-ils trente secondes ?','Pour vérifier si leur modification rend les voix plus claires avant de poursuivre.',['voix']),
('grammar_in_context','Que souligne l’expression « chaque voix » ?','Elle demande que la parole de chaque acteur reste intelligible, pas seulement le son général du groupe.',['voix']),
('cloze_transfer','Complète : Le groupe veut _____ une ambiance sans couvrir les acteurs.','créer',['créer']),
('summary','Résume la correction de la répétition.','L’équipe agit rapidement sur ce qui peut causer le problème, déplace les enceintes et réussit à créer une scène où chaque voix reste claire.',['agir','rapide','causer','créer','scène','voix'])
]},
{
'id':'fr-b1-u04-p03','sequence':21,'ptype':'interleaved','title':'Rejoindre la bonne ligne jusqu’au bout','genre':'urban wayfinding narrative','domains':['public','personal'],'topics':['transit','wayfinding','independence'],'forms':['rejoindre','ligne','bout'],'reviews':['espoir','oser','liberté'],
'paragraphs':[
"Camille doit rejoindre un centre de formation dans un quartier qu’elle connaît peu. Elle espère faire le trajet seule afin de gagner davantage de liberté dans ses déplacements. L’application lui conseille de prendre le métro puis une ligne d’autobus. À la sortie de la station, deux arrêts portent des noms presque identiques. Camille hésite, mais elle décide d’oser vérifier le plan affiché plutôt que de suivre automatiquement le groupe qui marche devant elle.",
"Le plan indique qu’elle doit rejoindre la ligne 24 vers l’ouest et rester dans l’autobus presque jusqu’au bout du parcours. Un petit symbole précise que la ligne change légèrement de trajet pendant des travaux. Camille compare le numéro de l’arrêt avec celui de l’application et demande au conducteur si le centre se trouve bien avant le terminus. Il lui répond qu’elle devra descendre deux arrêts avant le bout de la ligne. Cette confirmation réduit son hésitation sans lui retirer la responsabilité du trajet.",
"Camille arrive à l’heure et ressent un véritable espoir de pouvoir refaire ce déplacement sans aide. Pour elle, la liberté ne consiste pas à ne jamais poser de question. Elle signifie pouvoir rejoindre une destination en sachant où vérifier les informations importantes. Oser demander une confirmation lui a évité une erreur, tandis que lire le plan lui a permis de comprendre la ligne plutôt que de mémoriser seulement un ordre d’étapes. Au retour, elle choisit le bon arrêt beaucoup plus rapidement et suit le trajet jusqu’au bout prévu."
],
'grammar':[{'id':'fr-b1-u04-jusquau-bout','role':'new','description':'use jusqu’au bout / avant le bout to express endpoint relations in a route'}],
'discourse':[{'id':'fr-b1-u04-independent-wayfinding','role':'new','description':'combine map reading, confirmation and endpoint reasoning to navigate independently'}],
'items':[
('gist','Comment Camille réussit-elle à se déplacer seule ?','Elle vérifie le plan, rejoint la bonne ligne et confirme l’arrêt où descendre.',['rejoindre','ligne']),
('literal_detail','Quelle ligne doit-elle prendre ?','La ligne 24.',['ligne']),
('cause_effect','Pourquoi demande-t-elle au conducteur une confirmation ?','Parce que la ligne est modifiée par des travaux et elle veut vérifier où descendre.',['ligne']),
('vocabulary_in_context','Que signifie « rejoindre » la ligne 24 ?','Atteindre l’arrêt ou le service permettant de prendre cette ligne.',['rejoindre']),
('vocabulary_in_context','Que signifie « bout » dans « bout de la ligne » ?','L’extrémité ou la fin du parcours.',['bout']),
('inference','Pourquoi demander une question ne réduit-il pas sa liberté ?','Parce que la vérification lui permet de prendre elle-même une décision informée et de comprendre le trajet.',['liberté']),
('motive','Pourquoi Camille ose-t-elle consulter le plan au lieu de suivre le groupe ?','Elle veut éviter de dépendre du comportement des autres et apprendre le trajet elle-même.',['oser']),
('grammar_in_context','Quelle différence y a-t-il entre « jusqu’au bout » et « avant le bout » ?','Le premier atteint la fin du parcours ; le second situe un point avant cette fin.',['bout']),
('cloze_transfer','Complète : Pour aller au centre, il faut _____ la ligne 24.','rejoindre',['rejoindre']),
('summary','Résume ce que Camille apprend.','Avec l’espoir de gagner en liberté, elle ose vérifier le plan, rejoint la bonne ligne et comprend où se situe le bout du trajet.',['espoir','liberté','oser','rejoindre','ligne','bout'])
]},
{
'id':'fr-b1-u04-p04','sequence':22,'ptype':'transfer','title':'Un système normal qui aide à prévenir une perte','genre':'food-safety operations narrative','domains':['professional','public'],'topics':['food safety','monitoring system','prevention'],'forms':['normal','système','prévenir'],'reviews':['nourriture','accompagner','sonner'],
'paragraphs':[
"Dans une cuisine communautaire, Camille accompagne une responsable qui vérifie les réfrigérateurs avant une distribution de nourriture. Un petit appareil commence à sonner lorsque la porte d’un réfrigérateur reste ouverte trop longtemps. Un nouveau bénévole pense que l’alarme indique une panne, mais la responsable explique que ce signal est normal : le système est justement conçu pour prévenir une hausse prolongée de la température.",
"Ils vérifient l’écran et constatent que la température reste dans la plage normale. La porte avait été mal refermée pendant le rangement. La responsable montre au bénévole comment le système enregistre l’heure de chaque alarme et lui demande d’accompagner la prochaine vérification afin de comprendre la procédure. Si une alarme continue à sonner après la fermeture de la porte, il faut alors mesurer la température avec un second appareil et déplacer la nourriture si nécessaire.",
"Camille remarque qu’un système utile ne prévient pas tous les problèmes automatiquement. Il peut prévenir certaines conséquences en attirant rapidement l’attention, mais une personne doit encore interpréter le signal et agir. Le bruit normal d’une alarme ne doit donc ni être ignoré ni être traité comme une catastrophe. Pour prévenir une perte de nourriture, l’équipe combine le système, une vérification humaine et une procédure claire. Accompagner les nouveaux bénévoles rend cette procédure plus fiable, car ils apprennent quand une alarme doit sonner et quelle réponse devient nécessaire ensuite."
],
'grammar':[{'id':'fr-b1-u04-si-alarm','role':'new','description':'use si-clauses to separate normal alarm behavior from escalation conditions'}],
'discourse':[{'id':'fr-b1-u04-prevention-system','role':'new','description':'interpret a monitoring system as one layer in a preventive procedure rather than an automatic solution'}],
'items':[
('gist','Quel est le rôle du système d’alarme ?','Aider à prévenir une hausse prolongée de température en attirant l’attention sur une porte restée ouverte.',['système','prévenir']),
('literal_detail','Pourquoi l’appareil commence-t-il à sonner ?','Parce que la porte du réfrigérateur est restée ouverte trop longtemps.',['sonner']),
('cause_effect','Pourquoi le signal est-il considéré comme normal ?','Parce que le système est conçu pour produire cette alarme dans cette situation.',['normal','système']),
('vocabulary_in_context','Que signifie « prévenir » une hausse de température ici ?','Empêcher ou limiter cette hausse avant qu’elle cause une perte.',['prévenir']),
('vocabulary_in_context','Que signifie « normal » pour l’alarme ?','Conforme au fonctionnement prévu du système dans cette situation.',['normal']),
('inference','Pourquoi une personne doit-elle encore vérifier la situation ?','Parce que le système signale un risque mais ne détermine pas seul la cause ni toute la réponse nécessaire.',['système']),
('motive','Pourquoi la responsable demande-t-elle au nouveau bénévole d’accompagner une vérification ?','Pour qu’il apprenne la procédure concrète autour de la nourriture et des alarmes.',['accompagner','nourriture']),
('grammar_in_context','Quel rôle joue la proposition « Si une alarme continue à sonner » ?','Elle définit la condition qui déclenche une vérification plus poussée.',['sonner']),
('cloze_transfer','Complète : Cette alarme sert à _____ une perte de nourriture.','prévenir',['prévenir','nourriture']),
('summary','Résume la procédure.','Le système produit une alarme normale pour prévenir un risque ; l’équipe vérifie la nourriture, sait quand l’appareil doit sonner et accompagne les nouveaux dans la réponse.',['système','normal','prévenir','nourriture','sonner','accompagner'])
]},
{
'id':'fr-b1-u04-p05','sequence':23,'ptype':'integration','title':'Reconnaître la relation entre l’art du passé et le présent','genre':'museum interpretation narrative','domains':['public','educational'],'topics':['art history','historical interpretation','present-day context'],'forms':['relation','reconnaître','présent'],'reviews':['art','paix','rôle'],
'paragraphs':[
"Dans une nouvelle exposition, Camille observe une série d’affiches consacrées à la paix après différentes périodes de conflit. Le rôle de l’art varie d’une affiche à l’autre : certaines cherchent à rassurer, d’autres à convaincre ou à commémorer. Le musée veut montrer la relation entre ces images historiques et le présent, mais sans prétendre que les problèmes d’aujourd’hui sont identiques à ceux du passé.",
"Une médiatrice demande aux visiteurs de reconnaître deux choses à la fois. Premièrement, une œuvre appartient à son contexte d’origine et doit être lue avec les mots, les événements et les attentes de cette époque. Deuxièmement, le public du présent apporte ses propres questions. La relation entre ces deux moments peut aider à voir ce qui change et ce qui reste familier. Reconnaître cette relation ne signifie donc pas effacer les différences historiques.",
"Camille choisit une affiche où une colombe occupe presque toute l’image. Aujourd’hui, ce symbole lui paraît immédiatement lié à la paix, mais la médiatrice montre que le texte original insistait surtout sur la reconstruction. Camille comprend que l’art du passé peut rester présent dans la mémoire collective tout en changeant de sens selon le contexte. Pour elle, reconnaître cette évolution est plus intéressant que chercher une interprétation unique. Le présent devient alors un point de comparaison, pas une mesure qui décide automatiquement ce que l’œuvre signifiait autrefois."
],
'grammar':[{'id':'fr-b1-u04-deux-choses-a-la-fois','role':'new','description':'use parallel framing to hold historical context and present-day interpretation together'}],
'discourse':[{'id':'fr-b1-u04-past-present-relation','role':'new','description':'relate historical artwork to present interpretation while preserving contextual differences'}],
'items':[
('gist','Quelle relation le musée cherche-t-il à montrer ?','La relation entre l’art historique et les questions du public au présent.',['relation','art','présent']),
('literal_detail','Quel symbole Camille observe-t-elle sur une affiche ?','Une colombe.',['paix']),
('cause_effect','Pourquoi faut-il reconnaître les différences historiques ?','Parce que relier le passé au présent ne signifie pas que les deux contextes sont identiques.',['reconnaître','présent']),
('vocabulary_in_context','Que signifie « relation » ici ?','Le lien comparatif entre deux contextes ou interprétations.',['relation']),
('vocabulary_in_context','Que signifie « reconnaître » dans ce passage ?','Admettre ou identifier clairement un fait ou une différence.',['reconnaître']),
('inference','Pourquoi le symbole de la colombe peut-il être compris différemment aujourd’hui ?','Parce que le public du présent apporte des associations différentes du contexte original de l’affiche.',['présent']),
('motive','Pourquoi le musée ne veut-il pas présenter les problèmes actuels comme identiques au passé ?','Pour préserver le rôle du contexte historique dans l’interprétation de l’art.',['rôle','art']),
('grammar_in_context','Que permet l’expression « deux choses à la fois » ?','Elle maintient ensemble le contexte d’origine et les questions du présent sans réduire l’un à l’autre.',['présent']),
('cloze_transfer','Complète : Il faut _____ la différence entre les deux périodes.','reconnaître',['reconnaître']),
('summary','Résume la méthode du musée.','Il examine la relation entre l’art du passé et le présent, reconnaît les différences de contexte et étudie le rôle des symboles de paix sans imposer un sens unique.',['relation','art','présent','reconnaître','rôle','paix'])
]}
]

CHECKPOINT={
'id':'fr-b1-u04-p06','sequence':24,'ptype':'checkpoint','title':'De l’impression à une décision vérifiée','genre':'B1 cumulative verification summary','domains':['educational','public','professional'],'topics':['research','performance','wayfinding','systems','interpretation'],'paragraphs':[
"Camille apprend à transformer une première impression en décision vérifiée. Dans une recherche, une explication est probablement plausible sans que les observations puissent encore la prouver. Sur une scène, il faut créer une ambiance tout en gardant chaque voix claire. Dans les transports, savoir rejoindre une ligne suppose de comprendre où elle mène et où se trouve le bout du trajet, plutôt que de suivre les autres sans vérifier.",
"Dans une cuisine communautaire, un signal normal peut faire partie d’un système conçu pour prévenir un problème. La technologie aide, mais une personne doit encore interpréter ce qu’elle observe. Au musée, reconnaître une relation entre le passé et le présent demande la même prudence : un lien peut être utile sans effacer les différences de contexte.",
"Ces exemples prolongent les méthodes précédentes. Camille sait séparer une zone en morceaux, agir rapidement sans confondre vitesse et précipitation, oser une idée avec assez de liberté pour la réviser, accompagner une livraison de nourriture et réfléchir au rôle de l’art dans un message de paix. Elle comprend surtout qu’une bonne décision n’est pas celle qui paraît certaine le plus vite. Elle décrit ce qu’elle sait, vérifie ce qui peut être prouvé et choisit ensuite une réponse adaptée."
],
'grammar':[{'id':'fr-b1-u04-cumulative-verification','role':'integration','description':'integrate modality, endpoints, system conditions and recognition across several contexts'}],
'discourse':[{'id':'fr-b1-u04-impression-to-decision','role':'integration','description':'synthesize research uncertainty, performance design, navigation, prevention and historical interpretation'}],
'items':[
('gist','Quelle méthode générale relie l’unité ?','Passer d’une première impression à une décision fondée sur une vérification adaptée.',['recherche']),
('literal_detail','Quels mots décrivent la première situation ?','probablement, prouver et recherche',['probablement','prouver','recherche']),
('cause_effect','Pourquoi la scène demande-t-elle un compromis ?','Parce qu’il faut créer une ambiance sans couvrir chaque voix.',['scène','créer','voix']),
('vocabulary_in_context','Quels mots résument le trajet en transport ?','rejoindre, ligne et bout',['rejoindre','ligne','bout']),
('vocabulary_in_context','Quels mots décrivent la procédure de prévention ?','normal, système et prévenir',['normal','système','prévenir']),
('inference','Quel principe commun unit la recherche et l’interprétation du musée ?','Une relation ou une hypothèse peut être utile sans être traitée comme une preuve complète.',['relation','présent']),
('motive','Pourquoi Camille continue-t-elle à vérifier après un signal ou une impression ?','Pour distinguer ce qui est réellement établi de ce qui demande encore une interprétation.',['reconnaître']),
('reference_resolution','Dans « où elle mène », à quoi renvoie « elle » ?','À la ligne de transport.',['ligne']),
('cloze_transfer','Complète : Il faut _____ ce qui est confirmé avant de conclure.','reconnaître',['reconnaître']),
('summary','Résume l’unité en une phrase.','Camille apprend à mener une recherche prudente, créer une scène claire, rejoindre une ligne, comprendre un système de prévention et reconnaître la relation entre passé et présent.',['recherche','créer','scène','rejoindre','ligne','système','prévenir','reconnaître','relation','présent'])
]}

def text_of(s): return '\n\n'.join(s['paragraphs'])
def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s['items'],ids); text=text_of(s)
    return {'id':s['id'],'language':'fr','cefr':'B1','unit':4,'sequence':s['sequence'],'revision':1,'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],'topics':s['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':q,'answer_key':a,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'French B1 Unit 04 guarded transfer batch; final language-wide audit deferred.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French B1 Unit 04 transfer batch.','All-prior-French freshness, source identity, B1 word band, exact deliberate-review visibility, question linkage and zero-new checkpoint are enforced.']},'paired_text_group':None,'prerequisites':['French B1 Units 01-03 canonical corpus'],'difficulty_notes_internal':'B1 transfer across field research, performance, transit, prevention systems and historical interpretation.','reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_b1_u04']}

def build(a1,a2,b1,D):
    prior=base.prior(a1+a2+b1); bad=[]
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    for f in FORMS:
        if f not in D: bad.append(f+':missing_lexicon')
        elif base.tid(D[f]['rank']) in prior_ids or f in prior_forms or prior.get(f): bad.append(f+':already_deliberate')
    if bad: raise AssertionError('B1 Unit04 candidate failures: '+', '.join(bad))
    review_sets=[['zone','séparer','morceau'],['causer','rapide','agir'],['espoir','oser','liberté'],['nourriture','accompagner','sonner'],['art','paix','rôle']]
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
    if len(a1)!=60 or len(a2)!=60 or len(b1)!=18 or b1[-1]['id']!='fr-b1-u03-p06': raise AssertionError('unexpected prerequisite frontier')
    D=base.deck(); unit=build(a1,a2,b1,D); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    if [r['sequence'] for r in unit]!=list(range(19,25)) or [r['id'] for r in unit]!=[f'fr-b1-u04-p{i:02d}' for i in range(1,7)]: raise AssertionError('B1 Unit04 continuity failure')
    newids=[]; newforms=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 220<=r['word_count']<=350: raise AssertionError(f"{r['id']}: B1 word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        if r['sequence']<=23 and len(r['new_lexical_targets'])!=3: raise AssertionError(f"{r['id']}: calibrated Unit04 load must be 3")
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
    if len(newids)!=15 or len(set(newids))!=15 or len(set(newforms))!=15 or unit[-1]['new_lexical_targets']!=[]: raise AssertionError('B1 Unit04 lexical-cycle invariant')
    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in b1+unit),encoding='utf-8')
    print(json.dumps({'status':'PASS','level':'B1','unit':4,'appended_passages':6,'b1_passages':24,'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':D[f]['rank'],'id':base.tid(D[f]['rank'])} for f in FORMS],'questions':60,'answers':60,'p06_new_targets':0},ensure_ascii=False))

if __name__=='__main__': main()
