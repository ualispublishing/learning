#!/usr/bin/env python3
"""Append French B1 Unit 03 (sequences 13-18) as a guarded transfer batch."""
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
EXPECTED_B1_BLOB='cc4f24514448e60e5439ef6d36f8f20d44f36c65'
FORMS=('zone','séparer','morceau','causer','rapide','agir','espoir','oser','liberté','nourriture','accompagner','sonner','art','paix','existence')

SPECS=[
{
'id':'fr-b1-u03-p01','sequence':13,'ptype':'instructional','title':'Séparer la zone en morceaux observables','genre':'environmental fieldwork report','domains':['educational','public'],'topics':['field observation','sampling','environment'],'forms':['zone','séparer','morceau'],'reviews':['apparemment','détail','honnête'],
'paragraphs':[
"Dans le cadre d’un projet de sciences, Camille rejoint une équipe qui observe un petit terrain humide près d’un parc. Apparemment, toute la zone semble identique : de l’herbe, quelques arbres et une partie boueuse. Pourtant, un détail attire son attention. Certaines plantes poussent seulement près de l’eau, tandis que d’autres apparaissent sur le sol plus sec. Pour décrire le lieu de manière honnête, l’équipe décide de ne pas traiter toute la zone comme un seul ensemble.",
"La responsable propose de séparer le terrain en quatre secteurs et d’observer chaque morceau pendant le même temps. Le mot morceau ne signifie pas qu’ils vont couper physiquement le sol ; il désigne ici une partie limitée de la zone étudiée. Les élèves notent la quantité d’eau visible, la hauteur des plantes et le nombre d’insectes observés. Ils prennent aussi une photo de chaque secteur pour pouvoir comparer leurs notes plus tard.",
"Les résultats montrent que la différence la plus nette se trouve entre les secteurs proches de l’eau et ceux du bord du chemin. Camille comprend pourquoi il fallait séparer les observations avant de résumer le site. Si elle avait écrit seulement « la zone est humide », elle aurait perdu un détail important sur la variation du terrain. Une description honnête peut donc être simple sans être vague : elle indique comment l’espace a été divisé et ce que chaque morceau permet réellement d’observer."
],
'grammar':[{'id':'fr-b1-u03-si-past-result','role':'new','description':'use si + plus-que-parfait / conditional-style counterfactual framing to explain why a method mattered'}],
'discourse':[{'id':'fr-b1-u03-spatial-sampling','role':'new','description':'divide a heterogeneous area into comparable observation sectors before generalizing'}],
'items':[
('gist','Pourquoi l’équipe divise-t-elle le terrain ?','Pour comparer des parties différentes de la zone au lieu de généraliser trop vite.',['zone','séparer']),
('literal_detail','En combien de secteurs le terrain est-il divisé ?','En quatre secteurs.',['séparer']),
('cause_effect','Pourquoi l’affirmation « la zone est humide » serait-elle insuffisante ?','Parce qu’elle cacherait le détail des différences entre les secteurs.',['zone','détail']),
('vocabulary_in_context','Que signifie « morceau » dans le protocole ?','Une partie limitée du terrain utilisée comme unité d’observation.',['morceau']),
('vocabulary_in_context','Que signifie « séparer » le terrain ici ?','Le diviser conceptuellement en secteurs pour comparer les observations.',['séparer']),
('inference','Pourquoi l’équipe observe-t-elle chaque secteur pendant le même temps ?','Pour rendre la comparaison plus honnête et réduire une différence créée seulement par la durée d’observation.',['honnête']),
('reference_resolution','Dans « il désigne ici », que désigne « il » ?','Le mot morceau.',['morceau']),
('grammar_in_context','Que montre la phrase « Si elle avait écrit seulement… » ?','Elle imagine une autre méthode afin d’expliquer ce qui aurait été perdu.',['détail']),
('cloze_transfer','Complète : Nous allons _____ la carte en quatre secteurs pour les comparer.','séparer',['séparer']),
('summary','Résume la méthode de terrain.','L’équipe sépare la zone en secteurs, observe chaque morceau de façon comparable et conserve les détails nécessaires à une description honnête.',['zone','séparer','morceau','détail','honnête'])
]},
{
'id':'fr-b1-u03-p02','sequence':14,'ptype':'reinforcement','title':'Agir vite sans confondre rapide et précipité','genre':'workplace incident-response narrative','domains':['professional','educational'],'topics':['incident response','digital tools','documentation'],'forms':['causer','rapide','agir'],'reviews':['ordinateur','installer','remplir'],
'paragraphs':[
"Pendant son stage, Sami remarque qu’un dossier partagé ne s’ouvre plus sur son ordinateur. Deux collègues rencontrent le même problème presque au même moment. Une mise à jour récente pourrait causer l’erreur, mais personne n’en est certain. Un collègue veut immédiatement installer une ancienne version du logiciel. Sami pense qu’une réponse rapide est nécessaire, mais qu’il faut agir sans multiplier les changements impossibles à distinguer ensuite.",
"L’équipe commence par vérifier si le problème touche tous les fichiers ou seulement le dossier commun. Elle découvre que les documents locaux s’ouvrent normalement. La responsable demande alors de ne rien installer avant d’avoir sauvegardé le message d’erreur. Elle contacte le support, qui confirme qu’une panne du serveur peut causer exactement ce comportement. La solution la plus rapide consiste finalement à utiliser une copie temporaire du dossier pendant que le serveur est réparé.",
"Après l’incident, Sami doit remplir un court rapport sur l’ordinateur. Il note l’heure, les symptômes, les actions tentées et la réponse du support. Pour lui, agir rapidement ne signifie pas choisir la première solution disponible. Une action rapide reste utile seulement si elle réduit le problème sans effacer les informations nécessaires pour comprendre ce qui a pu le causer. Le rapport permettra aussi d’éviter d’installer inutilement une autre version si la même panne revient."
],
'grammar':[{'id':'fr-b1-u03-pouvoir-causer','role':'new','description':'use pouvoir + causer to express a plausible causal hypothesis without claiming certainty'}],
'discourse':[{'id':'fr-b1-u03-fast-controlled-response','role':'new','description':'respond quickly while preserving diagnostic evidence and limiting simultaneous changes'}],
'items':[
('gist','Quelle différence Sami fait-il entre une réponse rapide et une réponse précipitée ?','Une réponse rapide agit sur le problème tout en conservant les informations nécessaires au diagnostic.',['rapide','agir']),
('literal_detail','Quel appareil Sami utilise-t-il ?','Son ordinateur.',['ordinateur']),
('cause_effect','Qu’est-ce qui peut causer le problème selon le support ?','Une panne du serveur.',['causer']),
('vocabulary_in_context','Que signifie « agir » dans cet incident ?','Prendre une action concrète en réponse au problème.',['agir']),
('vocabulary_in_context','Que signifie « rapide » lorsqu’il décrit la solution ?','Qui peut être mise en œuvre en peu de temps.',['rapide']),
('inference','Pourquoi l’équipe refuse-t-elle d’installer immédiatement une ancienne version ?','Parce qu’un changement supplémentaire pourrait compliquer le diagnostic alors que la cause n’est pas encore connue.',['installer']),
('motive','Pourquoi Sami doit-il remplir un rapport après l’incident ?','Pour conserver les faits et les actions afin d’aider une future réponse.',['remplir']),
('grammar_in_context','Quelle prudence exprime « pourrait causer » ?','La tournure présente une cause possible, pas une cause déjà prouvée.',['causer']),
('cloze_transfer','Complète : Avant d’_____ trop vite, vérifions ce qui fonctionne encore.','agir',['agir']),
('summary','Résume la méthode d’intervention.','L’équipe agit de façon rapide mais contrôlée : elle observe sur l’ordinateur, évite d’installer au hasard, identifie ce qui peut causer la panne et remplit un rapport.',['agir','rapide','ordinateur','installer','causer','remplir'])
]},
{
'id':'fr-b1-u03-p03','sequence':15,'ptype':'interleaved','title':'Oser une idée tout en gardant la liberté de la modifier','genre':'science-communication design narrative','domains':['educational','public'],'topics':['creative choice','science communication','revision'],'forms':['espoir','oser','liberté'],'reviews':['planète','attirer','durer'],
'paragraphs':[
"La classe prépare ensuite une affiche pour expliquer au public comment les scientifiques étudient une planète lointaine. Camille a l’espoir de créer quelque chose qui puisse attirer des visiteurs qui n’entrent pas habituellement dans les expositions de sciences. La professeure donne au groupe une grande liberté : le contenu scientifique obligatoire est défini, mais la forme reste ouverte. Sami propose d’oser une affiche presque sans texte, avec une seule grande question au centre.",
"Certains élèves craignent qu’une idée aussi simple ne fasse pas durer l’attention. Camille suggère donc un test : deux versions sont montrées à de petits groupes. La première attire rapidement le regard grâce à une grande image de la planète, tandis que la seconde ajoute trois étapes de réponse. Les visiteurs restent plus longtemps devant la seconde, mais plusieurs disent préférer l’entrée visuelle de la première. Le groupe décide alors de combiner les deux.",
"Pour Camille, avoir la liberté de créer ne signifie pas refuser toute contrainte. Le groupe peut oser une proposition inhabituelle, puis la modifier lorsqu’un test montre une faiblesse. Son espoir initial n’était pas de prouver que sa première idée serait parfaite ; il était de trouver une forme capable d’attirer le public et de faire durer une vraie question. La liberté devient donc utile lorsqu’elle s’accompagne du droit de réviser son choix au lieu de le défendre simplement parce qu’il est original."
],
'grammar':[{'id':'fr-b1-u03-sans-que','role':'new','description':'use subordinate evaluation to express concern about whether an effect will last'}],
'discourse':[{'id':'fr-b1-u03-creative-test-revise','role':'new','description':'turn creative freedom into an iterative design process tested against audience behavior'}],
'items':[
('gist','Comment le groupe utilise-t-il sa liberté créative ?','Il ose une idée, la teste puis combine les éléments qui fonctionnent le mieux.',['liberté','oser']),
('literal_detail','Quel sujet scientifique l’affiche présente-t-elle ?','L’étude d’une planète lointaine.',['planète']),
('cause_effect','Pourquoi le groupe combine-t-il les deux versions ?','Parce que l’une attire mieux au départ tandis que l’autre fait davantage durer l’attention.',['attirer','durer']),
('vocabulary_in_context','Que signifie « oser » une affiche inhabituelle ?','Avoir le courage d’essayer une forme qui sort des choix habituels.',['oser']),
('vocabulary_in_context','Que signifie « espoir » dans le premier paragraphe ?','L’attente positive de parvenir à attirer un nouveau public.',['espoir']),
('inference','Pourquoi la liberté n’est-elle pas présentée comme l’absence de contraintes ?','Parce que le contenu scientifique reste obligatoire et que les choix doivent encore être testés et révisés.',['liberté']),
('motive','Pourquoi Camille propose-t-elle un test ?','Pour vérifier si l’idée originale attire et fait réellement durer l’attention.',['attirer','durer']),
('reference_resolution','Dans « il était de trouver une forme », à quoi renvoie « il » ?','À l’espoir initial de Camille.',['espoir']),
('cloze_transfer','Complète : L’équipe décide d’_____ une présentation différente.','oser',['oser']),
('summary','Résume la leçon créative de Camille.','La liberté permet d’oser avec espoir, mais une idée doit encore attirer, durer et pouvoir être modifiée après observation.',['liberté','oser','espoir','attirer','durer'])
]},
{
'id':'fr-b1-u03-p04','sequence':16,'ptype':'transfer','title':'Accompagner la nourriture jusqu’à la bonne porte','genre':'community delivery logistics narrative','domains':['public','professional'],'topics':['food delivery','access needs','cost control'],'forms':['nourriture','accompagner','sonner'],'reviews':['coûter','respecter','inutile'],
'paragraphs':[
"Une association locale prépare des paniers de nourriture pour des personnes qui ont temporairement du mal à se déplacer. Camille aide à organiser les livraisons. Chaque panier contient une fiche indiquant l’adresse, les allergies et la consigne éventuelle de ne pas sonner. Certains bénévoles pensent qu’il serait plus simple de déposer tous les paniers devant les portes, mais la responsable rappelle qu’il faut respecter les instructions de chaque personne.",
"Pour les premières tournées, un bénévole expérimenté va accompagner les nouveaux. Il leur montre comment vérifier le numéro, protéger la nourriture de la pluie et décider quand sonner. Dans un immeuble, la fiche demande justement de ne pas sonner parce qu’un enfant dort l’après-midi. Le bénévole appelle donc le téléphone indiqué et attend une confirmation. Cette étape peut coûter quelques minutes, mais elle évite de laisser le panier au mauvais endroit ou de déranger inutilement la famille.",
"Camille observe que l’accompagnement n’est pas inutile même lorsque le trajet paraît facile. Accompagner un nouveau bénévole permet de transmettre des décisions pratiques qui ne tiennent pas toutes dans une liste. L’association mesure aussi ce que chaque livraison va coûter afin de regrouper les adresses proches. Son objectif n’est pas de réduire chaque minute, mais de respecter à la fois le budget et les besoins des personnes. La nourriture arrive ainsi de manière plus fiable, sans transformer la vitesse en unique critère de réussite."
],
'grammar':[{'id':'fr-b1-u03-ne-pas-sonner','role':'new','description':'use negated infinitive instructions inside reported logistical constraints'}],
'discourse':[{'id':'fr-b1-u03-logistics-with-needs','role':'new','description':'balance delivery efficiency with recipient-specific access and disturbance constraints'}],
'items':[
('gist','Quel principe guide les livraisons ?','Livrer la nourriture efficacement tout en respectant les consignes propres à chaque personne.',['nourriture','respecter']),
('literal_detail','Qui va accompagner les nouveaux bénévoles ?','Un bénévole expérimenté.',['accompagner']),
('cause_effect','Pourquoi le bénévole décide-t-il de ne pas sonner dans un immeuble ?','Parce que la fiche indique qu’un enfant dort l’après-midi.',['sonner']),
('vocabulary_in_context','Que signifie « accompagner » un nouveau bénévole ?','Faire la tournée avec lui afin de le guider pendant les premières livraisons.',['accompagner']),
('vocabulary_in_context','Que signifie « sonner » ici ?','Utiliser la sonnette pour signaler sa présence à la porte.',['sonner']),
('inference','Pourquoi quelques minutes supplémentaires ne sont-elles pas jugées inutiles ?','Parce qu’elles peuvent éviter une erreur de livraison ou un dérangement et donc protéger la qualité du service.',['inutile']),
('motive','Pourquoi l’association regroupe-t-elle les adresses proches ?','Pour contrôler ce que les livraisons vont coûter sans ignorer les besoins.',['coûter']),
('grammar_in_context','Quel effet a la consigne « ne pas sonner » ?','Elle transforme une action normalement possible en instruction négative liée à une situation précise.',['sonner']),
('cloze_transfer','Complète : Un bénévole expérimenté va _____ la nouvelle personne pendant sa première tournée.','accompagner',['accompagner']),
('summary','Résume la stratégie logistique.','L’association accompagne les bénévoles, protège la nourriture, décide quand sonner et vérifie ce que le service va coûter afin de respecter les personnes sans travail inutile.',['accompagner','nourriture','sonner','coûter','respecter','inutile'])
]},
{
'id':'fr-b1-u03-p05','sequence':17,'ptype':'integration','title':'L’art, la paix et l’existence de plusieurs récits','genre':'museum interpretation discussion','domains':['public','educational'],'topics':['art interpretation','peace','propaganda'],'forms':['art','paix','existence'],'reviews':['admettre','mensonge','conversation'],
'paragraphs':[
"Lors d’une visite au musée, Camille participe à une conversation sur une affiche créée après une guerre. L’œuvre utilise l’art pour représenter le retour de la paix : deux personnes se serrent la main devant une ville reconstruite. Un premier panneau affirme que l’image « montre l’unité complète de la population ». Une historienne demande toutefois au groupe d’admettre que cette phrase va plus loin que ce que l’affiche peut prouver.",
"Elle explique que l’existence d’une affiche en faveur de la paix montre qu’un message circulait, mais pas que tout le monde partageait ce message. Certains documents de la même période révèlent encore des conflits et des désaccords. L’historienne ne qualifie pas l’œuvre de mensonge. Elle distingue l’art, qui peut exprimer un espoir ou une vision, d’une affirmation historique qui prétend décrire exactement l’ensemble de la société. Cette différence ouvre une conversation plus riche sur la fonction de l’image.",
"Camille comprend alors pourquoi l’existence de plusieurs récits est importante. Une œuvre d’art peut défendre la paix sans devenir une mesure précise de l’opinion publique. Le musée décide de modifier le panneau : au lieu d’affirmer une unité complète, il expliquera que l’affiche présente un idéal de paix promu par certains acteurs. Admettre cette limite ne diminue pas l’intérêt de l’œuvre. Au contraire, cela évite de transformer une interprétation trop large en mensonge présenté comme un fait."
],
'grammar':[{'id':'fr-b1-u03-ne-pas-que','role':'new','description':'use contrastive negation to distinguish what evidence shows from what it cannot establish'}],
'discourse':[{'id':'fr-b1-u03-art-evidence-limit','role':'new','description':'separate artistic message, document existence and historical claim strength'}],
'items':[
('gist','Quelle distinction l’historienne demande-t-elle de faire ?','Distinguer le message de paix porté par l’art d’une preuve que toute la population partageait ce message.',['art','paix']),
('literal_detail','Que représentent les deux personnes sur l’affiche ?','Elles se serrent la main devant une ville reconstruite.',['paix']),
('cause_effect','Pourquoi le musée modifie-t-il son panneau ?','Parce que l’existence de l’affiche ne prouve pas une unité complète de la population.',['existence']),
('vocabulary_in_context','Que signifie « existence » dans ce passage ?','Le fait qu’un document ou plusieurs récits soient réellement présents ou attestés.',['existence']),
('vocabulary_in_context','Comment le texte emploie-t-il « art » ?','Comme une forme d’expression pouvant présenter un idéal ou une vision sans être un relevé complet de la réalité.',['art']),
('inference','Pourquoi l’historienne refuse-t-elle de qualifier l’affiche elle-même de mensonge ?','Parce que l’œuvre exprime un message ; le problème vient d’une interprétation historique trop forte du panneau.',['mensonge']),
('motive','Pourquoi faut-il admettre la limite du document ?','Pour éviter de présenter comme fait ce que l’affiche seule ne permet pas d’établir.',['admettre']),
('reference_resolution','Dans « cette différence ouvre une conversation », quelle différence est visée ?','La différence entre l’expression artistique et une affirmation historique générale.',['conversation']),
('cloze_transfer','Complète : Le document défend un idéal de _____.','paix',['paix']),
('summary','Résume la conclusion de Camille.','L’existence d’une œuvre d’art favorable à la paix peut nourrir une conversation historique, mais il faut admettre ses limites pour ne pas transformer une interprétation en mensonge.',['existence','art','paix','conversation','admettre','mensonge'])
]}
]

CHECKPOINT={
'id':'fr-b1-u03-p06','sequence':18,'ptype':'checkpoint','title':'Découper le problème avant d’agir','genre':'B1 cumulative method summary','domains':['educational','public','professional'],'topics':['observation','response','design','logistics','interpretation'],'paragraphs':[
"Camille remarque que plusieurs problèmes deviennent plus faciles lorsqu’on les découpe avant de décider. Sur le terrain, une zone peut être trop variée pour être décrite en une phrase : il faut la séparer en secteurs et observer chaque morceau. Lors d’un incident technique, une panne peut causer plusieurs symptômes ; une réponse rapide consiste à agir sur ce qui est confirmé sans multiplier les changements. Dans un projet créatif, l’espoir d’attirer un public peut donner la liberté d’oser une idée, mais cette idée doit encore être testée.",
"La même méthode apparaît dans les tâches quotidiennes. Pour livrer de la nourriture, un bénévole peut accompagner une nouvelle personne et décider quand sonner en fonction des consignes. Dans un musée, l’art peut défendre la paix sans prouver l’existence d’un accord général. Les mots et les documents doivent donc être reliés à ce qu’ils montrent réellement.",
"Les unités précédentes ajoutent d’autres vérifications : un détail apparemment simple peut changer une conclusion ; un choix sur un ordinateur peut avoir des conséquences ; une dépense peut coûter cher sans être inutile ; et une conversation peut contenir un mensonge qu’il faut admettre publiquement. Camille apprend ainsi à agir sans précipitation, à respecter les limites des preuves et à garder assez de liberté pour corriger une première solution."
],
'grammar':[{'id':'fr-b1-u03-cumulative-method','role':'integration','description':'integrate infinitive chains, modal causes and evidence limits across several domains'}],
'discourse':[{'id':'fr-b1-u03-decompose-before-action','role':'integration','description':'synthesize spatial decomposition, controlled action, iterative design, logistics and evidence-limited interpretation'}],
'items':[
('gist','Quelle méthode générale relie les situations ?','Décomposer le problème, vérifier chaque partie puis agir sans dépasser ce que les preuves permettent.',['agir']),
('literal_detail','Quels mots décrivent la méthode de terrain ?','zone, séparer et morceau',['zone','séparer','morceau']),
('cause_effect','Pourquoi une réponse rapide ne signifie-t-elle pas changer tout le système ?','Parce qu’il faut identifier ce qui peut causer le problème avant de multiplier les modifications.',['rapide','causer']),
('vocabulary_in_context','Quels mots décrivent l’attitude créative du troisième passage ?','espoir, oser et liberté',['espoir','oser','liberté']),
('vocabulary_in_context','Quels mots appartiennent à la situation de livraison ?','nourriture, accompagner et sonner',['nourriture','accompagner','sonner']),
('inference','Pourquoi le texte rapproche-t-il l’observation scientifique et l’interprétation d’un musée ?','Dans les deux cas, il faut limiter la conclusion à ce qu’une partie ou un document permet réellement d’observer.',['existence','art']),
('motive','Pourquoi Camille garde-t-elle de la liberté après avoir commencé à agir ?','Pour pouvoir corriger une première solution si les nouvelles observations la contredisent.',['liberté','agir']),
('reference_resolution','Dans « cette idée doit encore être testée », à quoi renvoie « cette idée » ?','À l’idée créative que le groupe a osé proposer.',['oser']),
('cloze_transfer','Complète : Une œuvre peut défendre la _____ sans prouver un accord général.','paix',['paix']),
('summary','Résume l’unité en une phrase.','Camille apprend à séparer une zone, agir de façon rapide mais contrôlée, oser avec liberté, accompagner une livraison et interpréter l’existence d’un art de paix sans dépasser les preuves.',['séparer','zone','agir','rapide','oser','liberté','accompagner','existence','art','paix'])
]}

def text_of(s): return '\n\n'.join(s['paragraphs'])
def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s['items'],ids); text=text_of(s)
    return {'id':s['id'],'language':'fr','cefr':'B1','unit':3,'sequence':s['sequence'],'revision':1,'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],'topics':s['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':q,'answer_key':a,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'French B1 Unit 03 guarded transfer batch; final language-wide audit deferred.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French B1 Unit 03 transfer batch.','All-prior-French freshness, source identity, B1 word band, exact deliberate-review visibility, question linkage and zero-new checkpoint are enforced.']},'paired_text_group':None,'prerequisites':['French B1 Units 01-02 canonical corpus'],'difficulty_notes_internal':'B1 transfer across fieldwork, incident response, creative design, logistics and cultural interpretation.','reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_b1_u03']}

def build(a1,a2,b1,D):
    prior=base.prior(a1+a2+b1); bad=[]
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    for f in FORMS:
        if f not in D: bad.append(f+':missing_lexicon')
        elif base.tid(D[f]['rank']) in prior_ids or f in prior_forms or prior.get(f): bad.append(f+':already_deliberate')
    if bad: raise AssertionError('B1 Unit03 candidate failures: '+', '.join(bad))
    review_sets=[['apparemment','détail','honnête'],['ordinateur','installer','remplir'],['planète','attirer','durer'],['coûter','respecter','inutile'],['admettre','mensonge','conversation']]
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
    if len(a1)!=60 or len(a2)!=60 or len(b1)!=12 or b1[-1]['id']!='fr-b1-u02-p06': raise AssertionError('unexpected prerequisite frontier')
    D=base.deck(); unit=build(a1,a2,b1,D); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    prior_ids={t.get('id') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}; prior_forms={t.get('form') for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    if [r['sequence'] for r in unit]!=list(range(13,19)) or [r['id'] for r in unit]!=[f'fr-b1-u03-p{i:02d}' for i in range(1,7)]: raise AssertionError('B1 Unit03 continuity failure')
    newids=[]; newforms=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 220<=r['word_count']<=350: raise AssertionError(f"{r['id']}: B1 word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        if r['sequence']<=17 and len(r['new_lexical_targets'])!=3: raise AssertionError(f"{r['id']}: calibrated Unit03 load must be 3")
        amap={a['question_id']:a['id'] for a in r['answer_key']}; decl={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[]) if isinstance(t,dict)}
        for q in r['questions']:
            if amap.get(q['id'])!=q['answer_id'] or any(x not in decl for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} {q['id']}: linkage/target declaration")
        for t in r['new_lexical_targets']:
            s=D.get(t['form'])
            if t['id'] in prior_ids or t['form'] in prior_forms or not s or t['source_rank']!=s['rank'] or t['id']!=base.tid(s['rank']) or base.cnt(r['text'],t['form'])!=t['exposures_in_text']: raise AssertionError(f"{r['id']}: source/exposure/freshness drift {t}")
            newids.append(t['id']); newforms.append(t['form'])
        for t in r['review_lexical_targets']:
            if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if len(newids)!=15 or len(set(newids))!=15 or len(set(newforms))!=15 or unit[-1]['new_lexical_targets']!=[]: raise AssertionError('B1 Unit03 lexical-cycle invariant')
    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in b1+unit),encoding='utf-8')
    print(json.dumps({'status':'PASS','level':'B1','unit':3,'appended_passages':6,'b1_passages':18,'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':D[f]['rank'],'id':base.tid(D[f]['rank'])} for f in FORMS],'questions':60,'answers':60,'p06_new_targets':0},ensure_ascii=False))

if __name__=='__main__': main()
