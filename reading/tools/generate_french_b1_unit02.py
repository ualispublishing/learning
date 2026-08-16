#!/usr/bin/env python3
"""Append French B1 Unit 02 (sequences 7-12) as one guarded transfer batch."""
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
EXPECTED_B1_BLOB='beed8c8337be567325a4b329b79c7d070511f3b1'
FORMS=('apparemment','détail','honnête','ordinateur','installer','remplir','planète','attirer','durer','coûter','respecter','inutile','admettre','mensonge','conversation')

SPECS=[
{
'id':'fr-b1-u02-p01','sequence':7,'ptype':'instructional','title':'Apparemment exact, sauf un détail','genre':'public-information correction narrative','domains':['public','educational'],'topics':['information verification','correction','source transparency'],'forms':['apparemment','détail','honnête'],'reviews':['poursuivre','époque','trace'],
'paragraphs':[
"Camille aide la bibliothèque à préparer une courte notice sur un ancien bâtiment du quartier. Le premier texte paraît apparemment solide : il donne une date de construction, décrit l’activité de l’époque et cite une photographie comme trace principale. Pourtant, Camille remarque un détail qui ne correspond pas au registre municipal. La notice affirme que le bâtiment a ouvert en 1928, alors que le registre indique 1929.",
"La responsable hésite à modifier le panneau, car l’impression est déjà prévue. Camille propose de poursuivre la vérification avant de décider. Elle retrouve un article de journal qui mentionne une cérémonie en 1928, mais l’ouverture au public l’année suivante. Le détail n’est donc pas une simple faute de frappe : deux événements différents ont été confondus. Camille pense qu’une correction honnête doit expliquer cette distinction plutôt que remplacer une date sans contexte. Elle rédige une phrase courte : la cérémonie a eu lieu en 1928, tandis que l’activité régulière a commencé en 1929.",
"La bibliothèque conserve aussi une note interne sur la modification. Pour Camille, être honnête avec le public ne signifie pas raconter toute l’enquête dans le panneau. Il suffit de ne pas présenter comme certain ce qui reste ambigu et de garder une trace des sources utilisées. Apparemment, une petite date pouvait sembler sans importance ; pourtant, ce détail change la manière de raconter la transition entre deux étapes de l’histoire du bâtiment."
],
'grammar':[{'id':'fr-b1-u02-apparently-contrast','role':'new','description':'use apparemment with pourtant to contrast first appearance and later evidence'}],
'discourse':[{'id':'fr-b1-u02-correct-public-record','role':'new','description':'identify a conflicting detail, pursue source verification and publish a transparent correction'}],
'items':[
('gist','Pourquoi la bibliothèque modifie-t-elle sa notice ?','Parce qu’un détail révèle que deux événements de dates différentes avaient été confondus.',['détail']),
('literal_detail','Quelle trace la première notice utilise-t-elle principalement ?','Une photographie.',['trace']),
('cause_effect','Pourquoi Camille poursuit-elle la vérification au lieu de changer immédiatement la date ?','Parce qu’elle veut comprendre la cause de la contradiction entre les sources.',['poursuivre']),
('vocabulary_in_context','Quel rôle joue « apparemment » au début du texte ?','Il indique que la notice semble correcte à première vue, avant la découverte d’un problème.',['apparemment']),
('vocabulary_in_context','Que signifie une correction « honnête » ici ?','Une correction qui distingue clairement ce qui est établi de ce qui avait été mal interprété.',['honnête']),
('inference','Pourquoi la note interne est-elle utile même si le public ne la lit pas ?','Elle conserve une trace de la raison du changement et des sources utilisées.',['trace']),
('reference_resolution','Dans « ce détail change la manière », à quoi renvoie « ce détail » ?','À la distinction entre la cérémonie de 1928 et l’ouverture régulière de 1929.',['détail']),
('grammar_in_context','Pourquoi « pourtant » convient-il après « apparemment » ?','Il introduit une information qui contredit l’impression initiale.',['apparemment']),
('cloze_transfer','Complète : Le rapport paraît _____ correct, mais nous devons encore vérifier une source.','apparemment',['apparemment']),
('summary','Résume la méthode de correction de Camille.','Elle repère un détail contradictoire, poursuit la recherche et formule une correction honnête fondée sur plusieurs traces.',['détail','honnête','poursuivre','trace'])
]},
{
'id':'fr-b1-u02-p02','sequence':8,'ptype':'reinforcement','title':'Installer le logiciel sans remplir les cases au hasard','genre':'workplace onboarding narrative','domains':['professional','educational'],'topics':['computer setup','forms','requirements'],'forms':['ordinateur','installer','remplir'],'reviews':['convaincre','position','impliquer'],
'paragraphs':[
"Pendant un stage d’observation, Sami reçoit un ordinateur partagé pour préparer des tableaux. Un message lui demande d’installer une nouvelle application avant la réunion de l’après-midi. Le formulaire d’installation comporte plusieurs cases techniques qu’il ne comprend pas. Un collègue lui conseille de tout remplir rapidement avec les valeurs proposées, mais Sami préfère vérifier ce que chaque choix peut impliquer pour les fichiers de l’équipe.",
"La responsable informatique explique que deux cases servent seulement aux équipes qui travaillent à distance. Les remplir sans besoin pourrait modifier l’emplacement de sauvegarde. Elle montre ensuite comment installer l’application avec les paramètres standards. Sami comprend qu’il n’a pas besoin de convaincre ses collègues que sa position est toujours meilleure ; il doit surtout distinguer une préférence personnelle d’une exigence technique. Lorsqu’une option peut impliquer un changement important, il note la question et demande une confirmation.",
"Après l’installation, l’ordinateur redémarre et l’application ouvre correctement les documents existants. Sami doit encore remplir son compte rendu de stage. Il y décrit les étapes utiles, mais évite de recopier chaque écran. Sa conclusion est simple : installer un outil n’est pas seulement cliquer sur « suivant ». Il faut comprendre quelles cases sont obligatoires, lesquelles dépendent du contexte et quelle position adopter lorsqu’une instruction reste ambiguë. Cette méthode prend quelques minutes de plus, mais elle évite de transformer une configuration banale en problème collectif."
],
'grammar':[{'id':'fr-b1-u02-lequel-choice','role':'review','description':'use lequel/laquelle-style reference implicitly through which-option contrasts while maintaining noun referents'}],
'discourse':[{'id':'fr-b1-u02-setup-requirements','role':'new','description':'separate required settings from optional ones and document consequences before installation'}],
'items':[
('gist','Quelle méthode Sami adopte-t-il pour configurer l’application ?','Il vérifie les options, demande confirmation lorsque nécessaire et n’active pas des réglages au hasard.',['installer','remplir']),
('literal_detail','Quel appareil Sami utilise-t-il ?','Un ordinateur partagé.',['ordinateur']),
('cause_effect','Pourquoi ne veut-il pas remplir toutes les cases avec les valeurs proposées ?','Parce que certaines options peuvent impliquer un changement important dans la sauvegarde.',['remplir','impliquer']),
('vocabulary_in_context','Que signifie « installer » l’application ?','Mettre le logiciel en place sur l’ordinateur afin qu’il puisse être utilisé.',['installer','ordinateur']),
('vocabulary_in_context','Que signifie « remplir » un formulaire ici ?','Ajouter les informations ou choix demandés dans ses cases.',['remplir']),
('inference','Pourquoi Sami distingue-t-il une préférence d’une exigence technique ?','Parce qu’une position personnelle ne suffit pas pour justifier un réglage qui affecte l’équipe.',['position']),
('motive','Pourquoi note-t-il une question au lieu d’essayer de convaincre immédiatement ?','Pour obtenir une confirmation technique avant de défendre un choix incertain.',['convaincre']),
('reference_resolution','Dans « les remplir sans besoin », à quoi renvoie « les » ?','Aux deux cases destinées aux équipes à distance.',['remplir']),
('cloze_transfer','Complète : Avant d’_____ ce programme, vérifie les paramètres de sauvegarde.','installer',['installer']),
('summary','Résume la règle de Sami pour une configuration ambiguë.','Sur l’ordinateur, il remplit seulement les champs compris, vérifie ce qu’un réglage peut impliquer et demande de l’aide avant d’installer.',['ordinateur','remplir','impliquer','installer'])
]},
{
'id':'fr-b1-u02-p03','sequence':9,'ptype':'interleaved','title':'Pourquoi une planète peut attirer notre attention longtemps','genre':'science-museum explanation','domains':['educational','public'],'topics':['astronomy','attention','exhibit design'],'forms':['planète','attirer','durer'],'reviews':['machine','code','recommencer'],
'paragraphs':[
"Au musée des sciences, Camille teste une exposition consacrée à une planète située très loin de la Terre. Une machine projette des données sur un grand écran, tandis qu’un code simple permet aux visiteurs de choisir différents scénarios. L’équipe veut savoir ce qui peut attirer l’attention sans transformer l’activité en jeu sans contenu. Camille observe d’abord une animation spectaculaire, puis une explication plus lente sur les conditions de la planète.",
"La première séquence attire facilement les visiteurs, mais leur attention ne semble pas durer. Beaucoup regardent quelques secondes puis passent à autre chose. Dans la seconde version, une question apparaît avant l’animation : « Que se passerait-il si cette planète recevait deux fois plus de lumière ? » Les visiteurs doivent choisir une réponse, voir le résultat, puis expliquer leur raisonnement. Plusieurs recommencent volontairement pour comparer un autre scénario. La machine n’a pas changé et le code reste presque identique ; seule l’organisation de l’information est différente.",
"Camille conclut qu’attirer le regard et faire durer l’attention sont deux problèmes distincts. Une image forte peut attirer quelqu’un vers l’écran, mais une question claire peut lui donner une raison de rester. Si un visiteur veut recommencer, ce n’est pas nécessairement parce que le premier essai a échoué : il peut chercher à tester une autre hypothèse sur la planète. Pour l’équipe, cette distinction aide à concevoir une exposition où la technologie soutient la réflexion au lieu de la remplacer."
],
'grammar':[{'id':'fr-b1-u02-faire-durer','role':'new','description':'contrast attirer with faire durer to distinguish initial attraction from sustained attention'}],
'discourse':[{'id':'fr-b1-u02-exhibit-comparison','role':'new','description':'compare two exhibit versions and infer why one sustains attention longer'}],
'items':[
('gist','Quelle distinction principale Camille fait-elle ?','Elle distingue ce qui attire d’abord le regard de ce qui fait durer l’attention.',['attirer','durer']),
('literal_detail','Que représente l’exposition ?','Une planète située très loin de la Terre.',['planète']),
('cause_effect','Pourquoi davantage de visiteurs recommencent-ils la seconde version ?','Parce qu’ils peuvent comparer une autre hypothèse après avoir vu le résultat.',['recommencer']),
('vocabulary_in_context','Que signifie « attirer » l’attention ?','Faire venir ou orienter l’attention vers quelque chose.',['attirer']),
('vocabulary_in_context','Que signifie « durer » lorsqu’on parle de l’attention ?','Continuer pendant une certaine période au lieu de disparaître immédiatement.',['durer']),
('inference','Pourquoi la seconde version semble-t-elle plus éducative sans changer beaucoup la machine ou le code ?','Parce qu’elle organise l’information autour d’une question qui demande un raisonnement actif.',['machine','code']),
('reference_resolution','Dans « il peut chercher à tester », qui est « il » ?','Un visiteur qui choisit de recommencer.',['recommencer']),
('grammar_in_context','Quelle différence le texte crée-t-il entre « attirer » et « faire durer » ?','Le premier verbe concerne l’entrée de l’attention, le second sa continuité.',['attirer','durer']),
('cloze_transfer','Complète : Cette question peut _____ les visiteurs vers l’exposition.','attirer',['attirer']),
('summary','Résume la conclusion de Camille sur l’exposition.','Une planète spectaculaire peut attirer le regard, mais une question et un scénario comparatif font durer l’attention et donnent une raison de recommencer.',['planète','attirer','durer','recommencer'])
]},
{
'id':'fr-b1-u02-p04','sequence':10,'ptype':'transfer','title':'Ce qui coûte cher n’est pas toujours ce qu’il faut supprimer','genre':'cultural-event budget analysis','domains':['public','professional'],'topics':['budget','cultural event','constraints'],'forms':['coûter','respecter','inutile'],'reviews':['étranger','peuple','futur'],
'paragraphs':[
"Une association prépare une petite fête culturelle consacrée aux récits de plusieurs régions du monde. Un artiste étranger doit présenter des chansons liées à l’histoire de son peuple, puis discuter avec le public. Le budget est limité et certains membres proposent de supprimer la traduction, car elle semble coûter trop cher. Camille participe à l’analyse en pensant aussi au futur de l’événement : une économie immédiate peut modifier l’accès du public et la réputation de l’association.",
"Elle demande d’abord combien chaque service va coûter réellement. La traduction représente une dépense importante, mais elle permet à davantage de visiteurs de suivre la discussion. En revanche, une décoration très coûteuse n’a qu’un rôle secondaire. Camille ne dit pas que la décoration est inutile ; elle explique qu’elle devient moins prioritaire si l’équipe doit respecter une limite précise. L’association contacte alors un fournisseur et réduit certains éléments visuels au lieu de supprimer la traduction.",
"La décision finale doit aussi respecter les engagements déjà annoncés au public. L’artiste étranger avait accepté de participer en pensant que ses paroles seraient comprises au-delà des personnes parlant sa langue. Pour Camille, gérer un budget signifie donc comparer ce que chaque choix va coûter avec la fonction qu’il remplit. Qualifier trop vite une dépense d’inutile peut cacher une conséquence importante. Le groupe garde cette analyse pour préparer une future édition plus tôt et négocier de meilleurs prix."
],
'grammar':[{'id':'fr-b1-u02-si-priority','role':'new','description':'use si-clauses to make priorities conditional on budget constraints'}],
'discourse':[{'id':'fr-b1-u02-budget-function','role':'new','description':'compare cost with function, obligations and access rather than cutting the largest expense automatically'}],
'items':[
('gist','Comment l’association choisit-elle ce qu’elle réduit ?','Elle compare ce que chaque élément coûte avec sa fonction et les engagements à respecter.',['coûter','respecter']),
('literal_detail','Quel service l’équipe décide-t-elle de conserver ?','La traduction.',['coûter']),
('cause_effect','Pourquoi la décoration devient-elle moins prioritaire ?','Parce qu’elle remplit une fonction secondaire lorsque le budget doit respecter une limite stricte.',['respecter']),
('vocabulary_in_context','Que signifie « coûter » dans ce passage ?','Demander une certaine somme d’argent.',['coûter']),
('vocabulary_in_context','Pourquoi « inutile » est-il un jugement trop fort pour la décoration ?','Parce qu’elle peut avoir une fonction, même si cette fonction est moins prioritaire.',['inutile']),
('inference','Pourquoi la présence d’un artiste étranger rend-elle la traduction particulièrement importante ?','Parce qu’elle permet à un public plus large de comprendre ses paroles et le récit lié à son peuple.',['étranger','peuple']),
('motive','Pourquoi le groupe garde-t-il l’analyse pour le futur ?','Pour préparer plus tôt la prochaine édition et mieux négocier les dépenses.',['futur']),
('grammar_in_context','Quel effet produit « si l’équipe doit respecter une limite » ?','La proposition rend la priorité de la décoration dépendante de la contrainte budgétaire.',['respecter']),
('cloze_transfer','Complète : Cette option peut _____ plus cher, mais elle répond à un besoin essentiel.','coûter',['coûter']),
('summary','Résume la règle budgétaire défendue par Camille.','Avant de déclarer une dépense inutile, il faut savoir ce qu’elle coûte, quelle fonction elle remplit et quels engagements il faut respecter.',['inutile','coûter','respecter'])
]},
{
'id':'fr-b1-u02-p05','sequence':11,'ptype':'integration','title':'Admettre un mensonge sans transformer toute la conversation','genre':'podcast editorial-review narrative','domains':['educational','professional'],'topics':['media correction','trust','conversation'],'forms':['admettre','mensonge','conversation'],'reviews':['regretter','profiter','ennui'],
'paragraphs':[
"Camille participe à la préparation d’un petit podcast scolaire. Dans une conversation enregistrée, un invité raconte qu’il a terminé un long parcours sportif en une seule journée. Après l’émission, il écrit à l’équipe pour admettre que cette phrase était fausse : il avait réalisé le parcours en deux jours. Il appelle lui-même cette exagération un mensonge et dit regretter d’avoir voulu rendre son histoire plus impressionnante.",
"L’équipe se demande s’il faut supprimer toute la conversation. Sami pense qu’une correction suffit, tandis qu’une autre élève craint que le mensonge rende le reste du témoignage peu fiable. Camille propose de profiter de l’erreur pour montrer au public comment l’équipe corrige une information. Elle réécoute les passages concernés et vérifie les autres faits vérifiables. Certains moments parlent simplement de fatigue, d’ennui pendant l’entraînement et de la motivation nécessaire pour continuer ; rien n’indique qu’ils soient faux.",
"Le podcast conserve donc la conversation, mais ajoute une introduction qui explique la correction avant l’extrait. L’invité peut admettre clairement le mensonge dans une courte phrase. Camille ne cherche pas à minimiser la faute ni à prétendre qu’elle ne compte pas. Elle distingue plutôt une affirmation fausse du reste du contenu vérifié. Pour elle, regretter une erreur est utile seulement si la correction devient visible. L’équipe peut profiter de cette transparence pour renforcer sa méthode éditoriale, sans transformer chaque imperfection en raison de supprimer tout le travail."
],
'grammar':[{'id':'fr-b1-u02-admettre-que','role':'new','description':'use admettre que to acknowledge a false or uncomfortable fact explicitly'}],
'discourse':[{'id':'fr-b1-u02-correct-without-erasing','role':'new','description':'separate one admitted falsehood from the rest of a record and make the correction visible'}],
'items':[
('gist','Pourquoi l’équipe conserve-t-elle la conversation ?','Parce qu’elle peut corriger clairement le mensonge tout en vérifiant le reste du témoignage.',['conversation','mensonge']),
('literal_detail','Qu’est-ce que l’invité doit admettre ?','Qu’il a terminé le parcours en deux jours et non en une seule journée.',['admettre']),
('cause_effect','Pourquoi Camille vérifie-t-elle les autres faits ?','Pour déterminer si le mensonge concerne une seule affirmation ou remet en cause davantage de contenu.',['mensonge']),
('vocabulary_in_context','Que signifie « admettre » ici ?','Reconnaître ouvertement qu’une affirmation était fausse.',['admettre']),
('vocabulary_in_context','Que désigne « conversation » ?','L’échange enregistré entre l’invité et l’équipe du podcast.',['conversation']),
('inference','Pourquoi le passage sur l’ennui n’est-il pas supprimé automatiquement ?','Parce qu’aucun élément ne montre qu’il soit faux et qu’il est distinct du mensonge corrigé.',['ennui']),
('motive','Pourquoi Camille veut-elle profiter de l’erreur ?','Pour rendre la méthode de correction visible et améliorer la pratique éditoriale.',['profiter']),
('grammar_in_context','Quelle fonction a « admettre que » dans le passage ?','L’expression introduit le fait précis que l’invité reconnaît comme vrai après sa correction.',['admettre']),
('cloze_transfer','Complète : Le témoin décide d’_____ que son premier récit était faux.','admettre',['admettre']),
('summary','Résume la position éditoriale de Camille.','Elle demande d’admettre le mensonge, de corriger la conversation publiquement et de profiter de l’erreur sans effacer ce qui reste vérifié.',['admettre','mensonge','conversation','profiter'])
]}
]

CHECKPOINT={
'id':'fr-b1-u02-p06','sequence':12,'ptype':'checkpoint','title':'Vérifier, expliquer, puis décider','genre':'B1 cumulative evidence-and-decision summary','domains':['educational','public','professional'],'topics':['verification','technology','science','budget','media'],'paragraphs':[
"Dans des situations très différentes, Camille apprend à ne pas confondre une première impression avec une conclusion. Une information apparemment correcte peut contenir un détail important ; une correction honnête demande alors de vérifier les sources. Sur un ordinateur, installer un outil ou remplir un formulaire exige de comprendre les conséquences des options plutôt que de cliquer au hasard. Dans une exposition, une planète spectaculaire peut attirer le regard sans faire durer l’attention : la forme d’une question peut être aussi importante que la machine qui l’affiche.",
"La même logique apparaît lorsqu’une équipe doit décider ce qu’un service va coûter. Une dépense n’est pas automatiquement inutile parce qu’elle est élevée ; il faut respecter les engagements et comparer le prix avec la fonction réelle. Dans un podcast, un invité peut admettre un mensonge au milieu d’une conversation plus longue. La correction doit être visible, mais elle n’oblige pas forcément à supprimer tout ce qui a été vérifié séparément.",
"Ces cas prolongent les habitudes de l’unité précédente. Camille sait poursuivre une trace, examiner une position, demander ce qu’un choix peut impliquer, corriger un code sans recommencer inutilement et profiter d’une erreur sans nier l’ennui qu’elle a parfois causé. Elle comprend maintenant qu’une décision solide repose sur une question simple : quel détail change réellement l’interprétation, quelle conséquence peut durer, et quelle réponse reste honnête et proportionnée aux faits ?"
],
'grammar':[{'id':'fr-b1-u02-cumulative-evidence','role':'integration','description':'integrate contrast, infinitive complements and modal judgments across several decision domains'}],
'discourse':[{'id':'fr-b1-u02-check-explain-decide','role':'integration','description':'synthesize source checking, technical setup, attention design, budget reasoning and visible media correction'}],
'items':[
('gist','Quelle méthode générale relie les cinq situations ?','Vérifier le détail pertinent, expliquer ses conséquences et choisir une réponse proportionnée.',['détail']),
('literal_detail','Quels mots du premier paragraphe concernent la configuration numérique ?','ordinateur, installer et remplir',['ordinateur','installer','remplir']),
('cause_effect','Pourquoi une planète spectaculaire ne suffit-elle pas nécessairement à maintenir le public ?','Parce qu’elle peut attirer le regard sans faire durer l’attention.',['planète','attirer','durer']),
('vocabulary_in_context','Quels mots servent à évaluer une dépense et une obligation ?','coûter, inutile et respecter',['coûter','inutile','respecter']),
('inference','Pourquoi le texte rapproche-t-il une correction historique et une correction de podcast ?','Dans les deux cas, une information erronée doit être rendue visible sans exagérer ce que l’erreur prouve sur le reste du contenu.',['honnête','mensonge','conversation']),
('motive','Pourquoi Camille continue-t-elle à demander ce qu’un choix peut impliquer ?','Pour anticiper les conséquences avant d’agir et éviter une décision fondée seulement sur l’apparence.',['impliquer']),
('grammar_in_context','Quel rôle joue « apparemment » dans la première phrase d’exemple ?','Il marque une impression initiale qui peut être révisée après vérification.',['apparemment']),
('reference_resolution','Dans « elle n’oblige pas forcément », à quoi renvoie « elle » ?','À la correction visible du mensonge.',['mensonge']),
('cloze_transfer','Complète : Une équipe crédible doit _____ une erreur lorsqu’elle est confirmée.','admettre',['admettre']),
('summary','Résume l’unité en une phrase.','Camille apprend à examiner un détail apparemment simple, configurer un ordinateur avec soin, faire durer l’attention, respecter les contraintes et admettre un mensonge de manière honnête.',['détail','apparemment','ordinateur','durer','respecter','admettre','mensonge','honnête'])
]}

def text_of(s): return '\n\n'.join(s['paragraphs'])
def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s['items'],ids); text=text_of(s)
    return {'id':s['id'],'language':'fr','cefr':'B1','unit':2,'sequence':s['sequence'],'revision':1,'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],'topics':s['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':q,'answer_key':a,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'French B1 Unit 02 guarded transfer batch; final language-wide audit deferred.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French B1 Unit 02 transfer batch.','All-prior-French freshness, source identity, B1 word band, exact deliberate-review visibility, question linkage and zero-new checkpoint are enforced.']},'paired_text_group':None,'prerequisites':['French B1 Unit 01 accepted calibration'],'difficulty_notes_internal':'B1 transfer: public correction, workplace setup, science explanation, budget reasoning and media correction with multi-paragraph inference.','reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_b1_u02']}

def build(a1,a2,b1,D):
    prior=base.prior(a1+a2+b1); bad=[]
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    for f in FORMS:
        if f not in D: bad.append(f+':missing_lexicon')
        elif base.tid(D[f]['rank']) in prior_ids or f in prior_forms or prior.get(f): bad.append(f+':already_deliberate')
    if bad: raise AssertionError('B1 Unit02 candidate failures: '+', '.join(bad))
    out=[]
    review_sets=[['poursuivre','époque','trace'],['convaincre','position','impliquer'],['machine','code','recommencer'],['étranger','peuple','futur'],['regretter','profiter','ennui']]
    for s,rfs in zip(SPECS,review_sets):
        text=text_of(s); new=[base.nt(f,text,D) for f in s['forms']]; reviews=[base.rev(f,prior) for f in rfs]
        ids={t['form']:t['id'] for t in new+reviews}; out.append(mk(s,new,reviews,ids))
    text=text_of(CHECKPOINT); reviews=[base.cur(f,D) for f in FORMS]; ids={t['form']:t['id'] for t in reviews]; out.append(mk(CHECKPOINT,[],reviews,ids,True))
    return out

def main():
    for path,expected,label in [(A1,EXPECTED_A1_BLOB,'A1'),(A2,EXPECTED_A2_BLOB,'A2'),(CANON,EXPECTED_B1_BLOB,'B1')]:
        blob=subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
        if blob!=expected: raise AssertionError(f'{label} blob drift: {blob} != {expected}')
    a1=[json.loads(x) for x in A1.read_text(encoding='utf-8').splitlines() if x.strip()]; a2=[json.loads(x) for x in A2.read_text(encoding='utf-8').splitlines() if x.strip()]; b1=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(a1)!=60 or len(a2)!=60 or len(b1)!=6 or b1[-1]['id']!='fr-b1-u01-p06': raise AssertionError('unexpected prerequisite frontier')
    D=base.deck(); unit=build(a1,a2,b1,D); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}; prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    if [r['sequence'] for r in unit]!=list(range(7,13)) or [r['id'] for r in unit]!=[f'fr-b1-u02-p{i:02d}' for i in range(1,7)]: raise AssertionError('B1 Unit02 continuity failure')
    newids=[]; newforms=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 220<=r['word_count']<=350: raise AssertionError(f"{r['id']}: B1 word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        if r['sequence']<=11 and len(r['new_lexical_targets'])!=3: raise AssertionError(f"{r['id']}: calibrated Unit02 load must be 3")
        amap={a['question_id']:a['id'] for a in r['answer_key']}; decl={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[]) if isinstance(t,dict)}
        for q in r['questions']:
            if amap.get(q['id'])!=q['answer_id'] or any(x not in decl for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} {q['id']}: linkage/target declaration")
        for t in r['new_lexical_targets']:
            s=D.get(t['form'])
            if t['id'] in prior_ids or t['form'] in prior_forms or not s or t['source_rank']!=s['rank'] or t['id']!=base.tid(s['rank']) or base.cnt(r['text'],t['form'])!=t['exposures_in_text']: raise AssertionError(f"{r['id']}: source/exposure/freshness drift {t}")
            newids.append(t['id']); newforms.append(t['form'])
        for t in r['review_lexical_targets']:
            if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if len(newids)!=15 or len(set(newids))!=15 or len(set(newforms))!=15 or unit[-1]['new_lexical_targets']!=[]: raise AssertionError('B1 Unit02 lexical-cycle invariant')
    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in b1+unit),encoding='utf-8')
    print(json.dumps({'status':'PASS','level':'B1','unit':2,'appended_passages':6,'b1_passages':12,'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':D[f]['rank'],'id':base.tid(D[f]['rank'])} for f in FORMS],'questions':60,'answers':60,'p06_new_targets':0},ensure_ascii=False))

if __name__=='__main__': main()
