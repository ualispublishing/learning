#!/usr/bin/env python3
"""Append French B1 Unit 06 (sequences 31-36) as one guarded transfer batch."""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit05 as prev
base=prev.base

REPO=Path(__file__).resolve().parents[2]
A1=REPO/'reading'/'french'/'a1'/'passages.jsonl'
A2=REPO/'reading'/'french'/'a2'/'passages.jsonl'
CANON=REPO/'reading'/'french'/'b1'/'passages.jsonl'
SCHEMA=REPO/'reading'/'schema'/'passage.schema.json'
EXPECTED_A1_BLOB='0493a2fa13e51b5997db05e91cdea4d8dc5e647b'
EXPECTED_A2_BLOB='d0a80b8866071f426019aa0ad143e1d270dba4de'
EXPECTED_B1_BLOB='dfd2b675884c9481906ce6b5bbba263f6c95b063'
FORMS=('signer','règle','témoin','dangereux','surveiller','risquer','journal','impression','signifier','personnel','mission','prévoir','discuter','colère','souhaiter')

SPECS=[
{
'id':'fr-b1-u06-p01','sequence':31,'ptype':'instructional','title':'Signer une règle comprise, avec un témoin du processus','genre':'community equipment-loan procedure narrative','domains':['public','professional'],'topics':['procedure','equipment loan','documentation'],'forms':['signer','règle','témoin'],'reviews':['clair','reprendre','déranger'],
'paragraphs':[
"Une bibliothèque de quartier prête désormais du matériel audio pour des projets scolaires. Avant le premier prêt, Camille relit le formulaire avec l’équipe. Une règle demande de rendre le matériel avant dix-huit heures, une autre précise comment signaler un dommage. Le responsable veut que chaque personne puisse signer seulement après avoir compris ces conditions. Camille reformule donc les points principaux dans un langage clair afin que personne ne signe simplement parce que les autres le font.",
"Pour les premiers prêts, un membre du personnel reste témoin de la remise du matériel. Son rôle n’est pas de surveiller la personne qui emprunte, mais de confirmer que l’état des appareils a été vérifié ensemble. Si une question dérange le déroulement, l’équipe préfère la traiter immédiatement plutôt que de la laisser devenir un conflit plus tard. Une fois la règle comprise, l’emprunteur peut signer et repartir avec une copie du document. Le témoin note seulement la date et le numéro du matériel.",
"Une semaine plus tard, Camille reprend le formulaire après plusieurs retours. Elle remarque qu’une phrase reste ambiguë et propose de la rendre plus claire. Le changement n’ajoute aucune nouvelle obligation ; il explique mieux une règle déjà présente. La bibliothèque décide aussi que le témoin doit demander à l’emprunteur de résumer les deux points essentiels avant de signer. Cette petite vérification permet de reprendre une information avec ses propres mots et réduit les malentendus. Camille comprend qu’un document utile n’est pas seulement signé : chaque règle doit être lisible, le témoin doit avoir une fonction limitée, et la procédure doit permettre de poser une question sans déranger inutilement le service."
],
'grammar':[{'id':'fr-b1-u06-sign-before-after','role':'new','description':'use avant/après + infinitive or completed action to sequence a documented procedure'}],
'discourse':[{'id':'fr-b1-u06-procedure-comprehension','role':'new','description':'distinguish understanding, signature and witness confirmation in a public procedure'}],
'items':[
('gist','Quel principe guide la nouvelle procédure ?','Une personne doit comprendre chaque règle avant de signer, tandis qu’un témoin confirme seulement le processus.',['règle','signer','témoin']),
('literal_detail','À quelle heure le matériel doit-il être rendu ?','Avant dix-huit heures.',['règle']),
('cause_effect','Pourquoi le formulaire est-il reformulé ?','Parce qu’une règle ambiguë peut créer des malentendus même si son contenu ne change pas.',['règle']),
('vocabulary_in_context','Que signifie « signer » ici ?','Ajouter sa signature après avoir compris les conditions du prêt.',['signer']),
('vocabulary_in_context','Quel est le rôle du « témoin » ?','Confirmer que la vérification et l’explication ont eu lieu, sans surveiller l’emprunteur.',['témoin']),
('inference','Pourquoi demander un résumé avant la signature ?','Pour vérifier que les règles ont réellement été comprises plutôt que simplement lues.',['signer','règle']),
('motive','Pourquoi Camille emploie-t-elle un langage clair ?','Pour que chacun puisse comprendre le document sans dépendre des choix des autres.',['clair']),
('reference_resolution','Dans « il explique mieux une règle », à quoi renvoie « il » ?','Au changement apporté à la phrase du formulaire.',['règle']),
('cloze_transfer','Complète : L’emprunteur peut _____ après avoir compris les conditions.','signer',['signer']),
('summary','Résume la procédure.','La bibliothèque rend chaque règle claire, laisse chacun signer après compréhension et utilise un témoin limité au processus afin de pouvoir reprendre les informations sans déranger le service.',['règle','clair','signer','témoin','reprendre','déranger'])
]},
{
'id':'fr-b1-u06-p02','sequence':32,'ptype':'reinforcement','title':'Surveiller un signal sans risquer une réaction dangereuse','genre':'school laboratory safety-monitoring narrative','domains':['educational','professional'],'topics':['monitoring','safety','decision making'],'forms':['dangereux','surveiller','risquer'],'reviews':['empêcher','récupérer','sinon'],
'paragraphs':[
"Dans un atelier scientifique scolaire, un capteur indique une température inhabituelle dans une armoire de stockage. L’enseignante ne demande pas aux élèves d’ouvrir l’armoire. Elle explique qu’il serait dangereux d’agir sans savoir si le signal vient du contenu ou du capteur lui-même. Camille aide plutôt à surveiller les mesures à distance pendant que le responsable de laboratoire suit la procédure prévue. Le but est d’empêcher une réaction improvisée qui pourrait risquer d’aggraver la situation.",
"Les mesures restent stables pendant plusieurs minutes. Le responsable compare ensuite le capteur principal avec un second appareil installé à proximité. Il veut récupérer assez d’informations pour savoir si l’alerte correspond à un changement réel ; sinon, il faudra vérifier le capteur avant de prendre une autre décision. Camille note que surveiller ne signifie pas attendre passivement. L’équipe observe une tendance, vérifie plusieurs sources et garde une distance sûre. Elle évite aussi de risquer du matériel ou la sécurité simplement pour obtenir une réponse plus vite.",
"Finalement, le second appareil montre une température normale et le responsable conclut que le premier capteur doit être contrôlé. L’armoire reste fermée jusqu’à cette vérification. L’épisode devient un exercice sur la différence entre un signal dangereux et une action dangereuse. Un signal peut demander de surveiller davantage, mais il ne justifie pas n’importe quelle intervention. Pour empêcher une erreur, l’équipe doit récupérer des données, comparer les instruments et prévoir ce qu’elle fera sinon. Camille retient surtout qu’on peut risquer de créer un problème en voulant résoudre trop vite une alerte encore mal comprise."
],
'grammar':[{'id':'fr-b1-u06-risquer-de','role':'new','description':'use risquer de + infinitive to express an unintended possible consequence'}],
'discourse':[{'id':'fr-b1-u06-monitor-before-act','role':'new','description':'separate signal observation from intervention and compare independent measurements'}],
'items':[
('gist','Pourquoi l’équipe ne réagit-elle pas immédiatement en ouvrant l’armoire ?','Parce qu’elle veut surveiller et vérifier le signal sans risquer une action dangereuse.',['surveiller','risquer','dangereux']),
('literal_detail','Quel élément est comparé au capteur principal ?','Un second appareil installé à proximité.',['surveiller']),
('cause_effect','Pourquoi l’armoire reste-t-elle fermée ?','Parce que les données suggèrent d’abord un problème de capteur qui doit être vérifié.',['dangereux']),
('vocabulary_in_context','Que signifie « surveiller » ici ?','Observer les mesures de façon suivie sans intervenir directement sur l’armoire.',['surveiller']),
('vocabulary_in_context','Comment « risquer » est-il utilisé ?','Pour indiquer qu’une action précipitée pourrait créer une conséquence indésirable.',['risquer']),
('inference','Pourquoi deux instruments sont-ils utiles ?','Ils permettent de récupérer une seconde source d’information et de vérifier si l’alerte est réelle.',['récupérer']),
('motive','Pourquoi l’équipe veut-elle empêcher une réaction improvisée ?','Parce qu’elle pourrait devenir plus dangereuse que le signal lui-même.',['empêcher','dangereux']),
('grammar_in_context','Que signifie « risquer d’aggraver » ?','Pouvoir entraîner involontairement une aggravation.',['risquer']),
('cloze_transfer','Complète : L’équipe continue de _____ les mesures à distance.','surveiller',['surveiller']),
('summary','Résume la méthode.','L’équipe surveille un signal potentiellement dangereux, récupère des données pour empêcher une réaction précipitée et évite de risquer une intervention inutile ; sinon elle vérifie le capteur.',['surveiller','dangereux','récupérer','empêcher','risquer','sinon'])
]},
{
'id':'fr-b1-u06-p03','sequence':33,'ptype':'interleaved','title':'Ce qu’un journal peut signifier au-delà de la première impression','genre':'media-literacy archive narrative','domains':['educational','public'],'topics':['media literacy','archive','interpretation'],'forms':['journal','impression','signifier'],'reviews':['ancien','vivant','honneur'],
'paragraphs':[
"Dans les archives municipales, Camille consulte un ancien journal publié après l’ouverture d’un grand parc. Le titre annonce « Une réussite pour toute la ville » et donne d’abord l’impression que le projet a reçu un soutien complet. L’archiviste lui rappelle pourtant qu’un journal représente une sélection de textes, de photos et de témoignages. Une formule enthousiaste peut signifier l’opinion de la rédaction sans résumer l’avis de chaque habitant.",
"Camille lit ensuite les pages intérieures. Un article rend honneur aux bénévoles qui ont planté des arbres, tandis qu’une lettre de lecteur critique le manque de transport vers le parc. Ce contraste rend le document plus vivant. L’impression initiale change : le journal montre à la fois de la fierté et des désaccords. L’archiviste demande alors ce que peut signifier le silence sur certains quartiers. Camille répond qu’une absence peut poser une question, mais ne prouve pas automatiquement que les habitants concernés étaient opposés au projet.",
"Pour terminer, elle compare ce journal avec des comptes rendus de réunions et des photographies. Le but n’est pas de diminuer la valeur du document ancien. Au contraire, il permet d’entendre plusieurs voix de son époque lorsque ses limites sont reconnues. Camille comprend que l’impression produite par un titre doit être vérifiée dans le reste du journal et dans d’autres sources. Un mot ou une image peut signifier quelque chose dans un contexte précis sans porter seul toute l’histoire. Rendre honneur au passé consiste donc aussi à conserver sa complexité et à éviter qu’une formule vivante devienne une conclusion trop simple."
],
'grammar':[{'id':'fr-b1-u06-pouvoir-signifier','role':'new','description':'use pouvoir + signifier to frame a plausible interpretation without asserting certainty'}],
'discourse':[{'id':'fr-b1-u06-headline-to-archive','role':'new','description':'revise a first impression by comparing headline, inner pages and independent archival sources'}],
'items':[
('gist','Comment Camille révise-t-elle sa première lecture du document ?','Elle passe de l’impression du titre à une lecture du journal complet et d’autres sources.',['impression','journal']),
('literal_detail','Quel désaccord apparaît dans une lettre de lecteur ?','Le manque de transport vers le parc.',['journal']),
('cause_effect','Pourquoi le document devient-il plus complexe après la lecture intérieure ?','Parce que le journal contient à la fois des éloges et des critiques.',['journal','impression']),
('vocabulary_in_context','Que signifie « impression » ici ?','La première perception ou idée produite par le titre.',['impression']),
('vocabulary_in_context','Que signifie « signifier » dans le passage ?','Exprimer ou indiquer un sens dans un contexte donné.',['signifier']),
('inference','Pourquoi le silence sur un quartier ne suffit-il pas à conclure ?','Parce qu’une absence dans un journal peut avoir plusieurs causes et doit être comparée à d’autres sources.',['journal','signifier']),
('motive','Pourquoi l’archiviste conserve-t-il aussi les critiques ?','Pour garder une histoire vivante qui rend honneur au passé sans effacer les désaccords.',['vivant','honneur']),
('reference_resolution','Dans « ses limites sont reconnues », à quoi renvoie « ses » ?','Au journal ancien comme source historique.',['ancien','journal']),
('cloze_transfer','Complète : Un titre peut _____ l’opinion de la rédaction sans résumer toute la ville.','signifier',['signifier']),
('summary','Résume la leçon des archives.','Un ancien journal peut créer une première impression et signifier plusieurs choses selon le contexte ; une lecture vivante rend honneur au passé en comparant les sources.',['ancien','journal','impression','signifier','vivant','honneur'])
]},
{
'id':'fr-b1-u06-p04','sequence':34,'ptype':'transfer','title':'Prévoir le personnel selon la mission réelle','genre':'public-event staffing narrative','domains':['professional','public'],'topics':['staffing','planning','event operations'],'forms':['personnel','mission','prévoir'],'reviews':['inviter','remercier','mériter'],
'paragraphs':[
"Un centre culturel prépare une journée portes ouvertes. Le premier planning prévoit le même nombre de personnes dans chaque salle. Camille demande plutôt de définir la mission de chaque espace avant de répartir le personnel. La salle d’accueil doit orienter les visiteurs, l’atelier doit expliquer une activité, et l’espace technique doit répondre aux problèmes de matériel. Prévoir le personnel devient alors une question de fonctions, pas seulement de nombres.",
"L’équipe décide d’inviter deux bénévoles expérimentés à l’accueil pendant l’heure la plus chargée. Elle veut aussi remercier les personnes qui acceptent une mission moins visible, comme préparer les badges ou vérifier les réserves. Camille souligne que ce travail peut mériter autant d’attention qu’une présentation publique. Pour prévoir les pauses, elle examine la durée de chaque mission et ajoute une personne mobile capable de remplacer temporairement un collègue. Ainsi, le personnel n’est pas fixé de manière rigide pour toute la journée.",
"La veille de l’événement, une intervenante annule sa participation. Grâce au planning, l’équipe sait déjà quelle mission peut être simplifiée et quel membre du personnel peut changer de poste pendant trente minutes. Camille comprend que prévoir ne signifie pas deviner exactement ce qui arrivera. Il s’agit de préparer des options qui gardent la mission essentielle possible. Après l’événement, le centre prend le temps de remercier le personnel et d’inviter les bénévoles à expliquer ce qui a bien fonctionné. Les remarques qui méritent une modification sont ajoutées au prochain planning. Cette boucle aide l’équipe à prévoir avec plus de précision sans transformer chaque imprévu en urgence."
],
'grammar':[{'id':'fr-b1-u06-prevoir-capable','role':'new','description':'combine prévoir with purpose and capable de to express staffing flexibility'}],
'discourse':[{'id':'fr-b1-u06-mission-before-headcount','role':'new','description':'derive staffing levels and contingencies from the mission of each space'}],
'items':[
('gist','Comment Camille construit-elle le planning ?','Elle définit d’abord la mission de chaque espace puis prévoit le personnel nécessaire et des remplacements.',['mission','prévoir','personnel']),
('literal_detail','Quel espace doit orienter les visiteurs ?','La salle d’accueil.',['mission']),
('cause_effect','Pourquoi une personne mobile est-elle ajoutée ?','Pour prévoir les pauses et remplacer temporairement un membre du personnel.',['prévoir','personnel']),
('vocabulary_in_context','Que désigne « personnel » ?','Les personnes chargées de faire fonctionner l’événement.',['personnel']),
('vocabulary_in_context','Que signifie « mission » ici ?','La fonction ou l’objectif confié à un espace ou à une personne.',['mission']),
('inference','Pourquoi le planning résiste-t-il à une annulation ?','Parce qu’il prévoit des options et distingue les missions essentielles de celles qui peuvent être simplifiées.',['prévoir','mission']),
('motive','Pourquoi remercier les tâches moins visibles ?','Parce qu’elles peuvent mériter autant d’attention que les rôles publics.',['remercier','mériter']),
('reference_resolution','Dans « il s’agit de préparer des options », à quoi renvoie cette idée ?','À ce que signifie réellement prévoir.',['prévoir']),
('cloze_transfer','Complète : Le centre doit _____ assez de personnel pour chaque mission.','prévoir',['prévoir','personnel','mission']),
('summary','Résume l’organisation.','Le centre définit chaque mission, prévoit un personnel flexible, choisit qui inviter, prend le temps de remercier les contributions et retient les remarques qui méritent une modification.',['mission','prévoir','personnel','inviter','remercier','mériter'])
]},
{
'id':'fr-b1-u06-p05','sequence':35,'ptype':'transfer','title':'Discuter avant que la colère décide pour le groupe','genre':'community meeting mediation narrative','domains':['public','personal'],'topics':['discussion','emotion','mediation'],'forms':['discuter','colère','souhaiter'],'reviews':['liste','réaliser','arranger'],
'paragraphs':[
"Lors d’une réunion de quartier, deux groupes ne sont pas d’accord sur l’emplacement d’un marché temporaire. Une personne parle avec colère parce qu’elle pense que sa rue recevra tout le bruit. Une autre affirme que le projet ne pourra jamais être réalisé ailleurs. Camille propose de discuter d’abord des besoins précis avant de choisir un lieu. Elle écrit une liste : accès aux transports, espace disponible, heures de livraison et distance par rapport aux logements.",
"Le président de séance demande ensuite à chacun ce qu’il souhaite protéger et ce qu’il peut accepter de modifier. Camille remarque que souhaiter une rue plus calme ne signifie pas refuser tout marché. De l’autre côté, souhaiter réaliser l’événement ne signifie pas ignorer les habitants. Le groupe essaie donc d’arranger les horaires et le trajet des véhicules. La colère diminue lorsque les personnes voient leurs contraintes inscrites dans la même liste au lieu d’être présentées comme des attaques personnelles.",
"Après une heure, les participants comparent deux emplacements. Aucun n’est parfait, mais l’un permet d’arranger les livraisons plus tôt et de réaliser le marché avec moins de circulation près des maisons. Camille souligne que discuter n’a pas supprimé toutes les différences. La discussion a surtout transformé la colère en informations que le groupe pouvait examiner. Chacun peut souhaiter un résultat différent tout en participant à une décision commune. Le compte rendu conserve la liste des critères et explique pourquoi le lieu choisi répond mieux à l’ensemble. Camille retient qu’un désaccord devient plus facile à traiter lorsqu’on peut discuter de ce que chacun souhaite avant de tenter d’arranger une solution."
],
'grammar':[{'id':'fr-b1-u06-souhaiter-inf','role':'new','description':'use souhaiter + infinitive/noun complement to state preferred outcomes without treating them as facts'}],
'discourse':[{'id':'fr-b1-u06-emotion-to-criteria','role':'new','description':'convert conflict claims into shared criteria and compare options against them'}],
'items':[
('gist','Comment Camille aide-t-elle le groupe à avancer ?','Elle propose de discuter des besoins, transforme les positions en liste de critères et cherche ensuite à arranger une solution.',['discuter','liste','arranger']),
('literal_detail','Quels critères sont inscrits dans la liste ?','Les transports, l’espace, les heures de livraison et la distance des logements.',['liste']),
('cause_effect','Pourquoi la colère diminue-t-elle ?','Parce que les contraintes sont reconnues comme des informations communes plutôt que des attaques personnelles.',['colère']),
('vocabulary_in_context','Que signifie « discuter » ici ?','Examiner ensemble les besoins et les options avant de décider.',['discuter']),
('vocabulary_in_context','Que signifie « souhaiter » ?','Exprimer le résultat que l’on aimerait obtenir.',['souhaiter']),
('inference','Pourquoi aucun souhait n’est-il traité comme une décision automatique ?','Parce que le groupe doit comparer plusieurs contraintes pour réaliser une solution commune.',['souhaiter','réaliser']),
('motive','Pourquoi Camille prépare-t-elle une liste ?','Pour donner au groupe des critères communs à discuter au lieu de rester dans la colère.',['liste','discuter','colère']),
('grammar_in_context','Que montre « souhaiter réaliser l’événement » ?','Un objectif désiré, pas une preuve que toute option permettant l’événement est acceptable.',['souhaiter','réaliser']),
('cloze_transfer','Complète : Avant de décider, le groupe doit _____ des besoins précis.','discuter',['discuter']),
('summary','Résume la médiation.','Le groupe utilise une liste pour discuter malgré la colère, préciser ce que chacun peut souhaiter, puis arranger les contraintes afin de réaliser une solution commune.',['liste','discuter','colère','souhaiter','arranger','réaliser'])
]}
]

CHECKPOINT={
'id':'fr-b1-u06-p06','sequence':36,'ptype':'checkpoint','title':'Comprendre la procédure, surveiller les preuves et prévoir les choix','genre':'B1 cumulative evidence-and-coordination summary','domains':['educational','public','professional'],'topics':['procedure','monitoring','media','planning','mediation'],'paragraphs':[
"Camille voit maintenant le même principe dans des contextes très différents. Une personne peut signer après avoir compris chaque règle, tandis qu’un témoin confirme seulement que la procédure a été suivie. Dans un atelier, un signal dangereux demande parfois de surveiller les données plutôt que de risquer une intervention précipitée. Le but commun est de distinguer ce qui est observé, ce qui est demandé et ce qui reste à vérifier.",
"Dans les archives, un journal peut produire une impression forte sans signifier que toute une population partage le même avis. Dans un événement, le personnel doit être réparti selon la mission de chaque espace et le planning doit prévoir des remplacements. Dans une réunion, discuter permet de transformer la colère en critères communs et de préciser ce que chacun peut souhaiter sans présenter un désir comme un fait.",
"Ces nouvelles situations prolongent les méthodes de l’unité précédente. Camille sait reprendre avec un message clair sans déranger, empêcher une perte en essayant de récupérer un fichier ou en prévoyant une solution sinon, lire un document ancien comme une source vivante qui peut rendre honneur sans simplifier, inviter et remercier les personnes dont le travail peut mériter du temps, puis utiliser une liste pour réaliser un objectif et arranger les contraintes. Elle retient qu’une décision solide combine compréhension, observation et coordination : signer une règle comprise, surveiller sans risquer, lire le journal au-delà de l’impression, prévoir le personnel selon sa mission et discuter de la colère pour comprendre ce que chacun peut souhaiter."
],
'grammar':[{'id':'fr-b1-u06-cumulative-modal','role':'integration','description':'integrate modal interpretation, infinitive complements and procedure sequencing across five contexts'}],
'discourse':[{'id':'fr-b1-u06-evidence-coordination','role':'integration','description':'synthesize procedure comprehension, safety monitoring, source interpretation, staffing and mediation'}],
'items':[
('gist','Quel principe général relie l’unité ?','Comprendre les conditions, surveiller les preuves et coordonner les choix avant d’agir.',['surveiller','prévoir']),
('literal_detail','Quels mots résument la procédure de prêt ?','signer, règle et témoin',['signer','règle','témoin']),
('cause_effect','Pourquoi surveiller avant d’intervenir ?','Pour éviter de risquer une réaction dangereuse lorsqu’un signal reste incertain.',['surveiller','risquer','dangereux']),
('vocabulary_in_context','Quels mots décrivent la lecture des archives ?','journal, impression et signifier',['journal','impression','signifier']),
('vocabulary_in_context','Quels mots décrivent l’organisation d’un événement ?','personnel, mission et prévoir',['personnel','mission','prévoir']),
('inference','Pourquoi une impression ou un souhait ne suffit-il pas pour décider ?','Parce qu’une impression doit être vérifiée et que ce que quelqu’un peut souhaiter doit être comparé aux autres contraintes.',['impression','souhaiter']),
('motive','Pourquoi le groupe choisit-il de discuter malgré la colère ?','Pour transformer l’émotion en besoins et critères qu’il peut examiner ensemble.',['discuter','colère']),
('reference_resolution','Dans « le planning doit prévoir des remplacements », à quoi sert « prévoir » ?','À préparer des options avant qu’un changement ne se produise.',['prévoir']),
('cloze_transfer','Complète : Un texte peut _____ quelque chose sans prouver toute une conclusion.','signifier',['signifier']),
('summary','Résume l’unité en une phrase.','Camille apprend à signer une règle avec un témoin du processus, surveiller sans risquer face au dangereux, lire un journal au-delà de l’impression et de ce qu’il peut signifier, prévoir le personnel selon sa mission, puis discuter malgré la colère de ce que chacun peut souhaiter.',['signer','règle','témoin','surveiller','risquer','dangereux','journal','impression','signifier','prévoir','personnel','mission','discuter','colère','souhaiter'])
]}

def text_of(s): return '\n\n'.join(s['paragraphs'])
def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s['items'],ids); text=text_of(s)
    return {'id':s['id'],'language':'fr','cefr':'B1','unit':6,'sequence':s['sequence'],'revision':1,'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],'topics':s['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':q,'answer_key':a,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'French B1 Unit 06 guarded transfer batch; final language-wide audit deferred.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French B1 Unit 06 transfer batch.','All-prior-French freshness, source identity, B1 word band, exact deliberate-review visibility, question linkage and zero-new checkpoint are enforced.']},'paired_text_group':None,'prerequisites':['French B1 Units 01-05 canonical corpus'],'difficulty_notes_internal':'B1 transfer across public procedure, safety monitoring, media interpretation, staffing and mediation.','reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_b1_u06']}

def build(a1,a2,b1,D):
    prior=base.prior(a1+a2+b1); bad=[]
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    for f in FORMS:
        if f not in D: bad.append(f+':missing_lexicon')
        elif base.tid(D[f]['rank']) in prior_ids or f in prior_forms or prior.get(f): bad.append(f+':already_deliberate')
    if bad: raise AssertionError('B1 Unit06 candidate failures: '+', '.join(bad))
    review_sets=[['clair','reprendre','déranger'],['empêcher','récupérer','sinon'],['ancien','vivant','honneur'],['inviter','remercier','mériter'],['liste','réaliser','arranger']]
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
    if len(a1)!=60 or len(a2)!=60 or len(b1)!=30 or b1[-1]['id']!='fr-b1-u05-p06': raise AssertionError('unexpected prerequisite frontier')
    D=base.deck(); unit=build(a1,a2,b1,D); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    if [r['sequence'] for r in unit]!=list(range(31,37)) or [r['id'] for r in unit]!=[f'fr-b1-u06-p{i:02d}' for i in range(1,7)]: raise AssertionError('B1 Unit06 continuity failure')
    newids=[]; newforms=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 220<=r['word_count']<=350: raise AssertionError(f"{r['id']}: B1 word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        if r['sequence']<=35 and len(r['new_lexical_targets'])!=3: raise AssertionError(f"{r['id']}: calibrated Unit06 load must be 3")
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
    if len(newids)!=15 or len(set(newids))!=15 or len(set(newforms))!=15 or unit[-1]['new_lexical_targets']!=[]: raise AssertionError('B1 Unit06 lexical-cycle invariant')
    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in b1+unit),encoding='utf-8')
    print(json.dumps({'status':'PASS','level':'B1','unit':6,'appended_passages':6,'b1_passages':36,'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':D[f]['rank'],'id':base.tid(D[f]['rank'])} for f in FORMS],'questions':60,'answers':60,'p06_new_targets':0},ensure_ascii=False))

if __name__=='__main__': main()
