#!/usr/bin/env python3
"""Generate French B1 Unit 01 (sequences 1-6) as a guarded calibration unit."""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_a2_unit03 as base

ROOT=Path(__file__).resolve().parents[2]
A1=ROOT/'french'/'a1'/'passages.jsonl'
A2=ROOT/'french'/'a2'/'passages.jsonl'
CANON=ROOT/'french'/'b1'/'passages.jsonl'
SCHEMA=ROOT/'schema'/'passage.schema.json'
EXPECTED_A1_BLOB='0493a2fa13e51b5997db05e91cdea4d8dc5e647b'
EXPECTED_A2_BLOB='d0a80b8866071f426019aa0ad143e1d270dba4de'
FORMS=('poursuivre','époque','trace','convaincre','position','impliquer','machine','code','recommencer','étranger','peuple','futur','regretter','profiter','ennui')

SPECS=[
{
'id':'fr-b1-u01-p01','sequence':1,'ptype':'instructional','title':'Poursuivre les traces d’une autre époque','genre':'local-history research narrative','domains':['educational','public'],'topics':['local history','archives','neighborhood change'],'forms':['poursuivre','époque','trace'],'reviews':['habiter','milieu'],
'paragraphs':[
"Pour commencer son projet B1, Camille choisit d’étudier l’histoire du quartier où elle vient habiter. Elle connaît déjà le milieu actuel : les commerces, l’école, le parc et les immeubles récents. Pourtant, une vieille photographie affichée à la bibliothèque montre une rue presque méconnaissable. Au lieu de considérer l’image comme une simple curiosité, Camille décide de poursuivre la recherche et de comprendre ce qui a changé.",
"La bibliothécaire lui explique que chaque époque laisse une trace différente. Un ancien plan peut garder la trace d’une usine disparue, tandis qu’un journal peut raconter pourquoi des familles sont arrivées ou parties. Camille apprend aussi qu’une trace n’est pas forcément une preuve complète : elle indique une piste qu’il faut comparer avec d’autres sources. Elle poursuit donc son enquête dans les archives municipales plutôt que de tirer une conclusion à partir d’une seule photo.",
"À la fin de l’après-midi, Camille peut déjà relier trois documents à la même époque. Elle remarque que le quartier était plus industriel et que moins de personnes venaient y habiter. Son but n’est pas de dire que le passé était meilleur ou pire. Elle veut poursuivre une question précise : comment le milieu s’est-il transformé, et quelles traces permettent de raconter cette transformation sans inventer ce que les documents ne montrent pas ?"
],
'grammar':[{'id':'fr-b1-u01-relative-ou','role':'review','description':'embed relative clauses with où while tracking place and time referents'}],
'discourse':[{'id':'fr-b1-u01-source-trail','role':'new','description':'build a claim by following several partial historical traces instead of treating one source as conclusive'}],
'items':[
('gist','Quel est l’objectif principal de la recherche de Camille ?','Comprendre comment son quartier s’est transformé en comparant plusieurs traces du passé.',['poursuivre','trace']),
('literal_detail','Quel document pousse Camille à commencer sa recherche ?','Une vieille photographie affichée à la bibliothèque.',['époque']),
('cause_effect','Pourquoi Camille poursuit-elle l’enquête dans les archives ?','Parce qu’une seule trace ne suffit pas pour tirer une conclusion solide.',['poursuivre','trace']),
('vocabulary_in_context','Dans ce texte, que signifie « poursuivre » une recherche ?','La continuer de manière organisée au lieu de l’abandonner.',['poursuivre']),
('vocabulary_in_context','Que représente une « trace » dans l’enquête ?','Un indice laissé par le passé qui peut orienter la recherche sans constituer à lui seul une preuve complète.',['trace']),
('inference','Pourquoi Camille évite-t-elle de dire que le passé était meilleur ou pire ?','Parce qu’elle cherche à décrire une transformation à partir des documents plutôt qu’à imposer un jugement général.',['époque']),
('reference_resolution','À quoi renvoie « elle indique une piste » ?','À une trace historique.',['trace']),
('grammar_in_context','Quel rôle joue « où » dans « le quartier où elle vient habiter » ?','Il relie le quartier à l’action d’y habiter et évite de répéter le lieu.',['habiter']),
('cloze_transfer','Complète : Les chercheurs décident de _____ leur enquête après la découverte d’un nouveau document.','poursuivre',['poursuivre']),
('summary','Résume la méthode de Camille en une phrase.','Elle suit plusieurs traces d’une même époque, compare les sources et limite ses conclusions à ce que les documents permettent d’établir.',['trace','époque'])
]},
{
'id':'fr-b1-u01-p02','sequence':2,'ptype':'reinforcement','title':'Convaincre sans effacer la position des autres','genre':'community-meeting narrative','domains':['public','educational'],'topics':['public discussion','persuasion','stakeholders'],'forms':['convaincre','position','impliquer'],'reviews':['cuisine','fenêtre'],
'paragraphs':[
"Quelques jours plus tard, Camille assiste à une réunion sur la rénovation d’une petite salle communautaire. Le projet semble simple : déplacer la cuisine, agrandir l’espace principal et remplacer une fenêtre ancienne. Pourtant, les habitants n’ont pas tous la même position. Certains veulent commencer les travaux rapidement, tandis que d’autres craignent que le coût augmente et demandent davantage d’informations.",
"Sami prépare une courte présentation pour convaincre le groupe de conserver une partie du budget pour l’accessibilité. Il comprend vite que convaincre ne consiste pas seulement à parler plus fort. Il doit présenter des raisons qui répondent à la position des personnes hésitantes. Une résidente explique par exemple que déplacer la cuisine pourrait réduire l’espace disponible. Sami modifie alors son schéma et montre une option qui garde la cuisine au même endroit tout en améliorant l’entrée.",
"La responsable souhaite aussi impliquer les personnes qui utilisent rarement la salle, car les travaux auront des conséquences pour elles aussi. Elle distribue donc un questionnaire et propose une seconde rencontre. Camille remarque que cette méthode n’oblige personne à changer immédiatement de position. Elle cherche plutôt à impliquer davantage de voix avant la décision. À la fin, Sami n’a pas convaincu tout le monde, mais la discussion est devenue plus précise : les désaccords portent maintenant sur des choix concrets plutôt que sur des impressions générales."
],
'grammar':[{'id':'fr-b1-u01-concession-pourtant','role':'review','description':'use pourtant to maintain a contrast across sentences and paragraphs'}],
'discourse':[{'id':'fr-b1-u01-position-response','role':'new','description':'represent competing positions fairly, respond to objections and broaden participation before a decision'}],
'items':[
('gist','Comment la discussion devient-elle plus utile ?','Les participants précisent leurs positions, répondent à des objections concrètes et impliquent davantage d’usagers.',['position','impliquer']),
('literal_detail','Quel point Sami veut-il protéger dans le budget ?','Une partie du budget consacrée à l’accessibilité.',['convaincre']),
('motive','Pourquoi Sami modifie-t-il son schéma ?','Pour répondre à la position d’une résidente qui craint de perdre de l’espace.',['position']),
('vocabulary_in_context','Que signifie « convaincre » dans cette réunion ?','Amener quelqu’un à considérer ou accepter une proposition grâce à des raisons pertinentes.',['convaincre']),
('vocabulary_in_context','Que signifie « impliquer » les usagers ?','Les faire participer au processus plutôt que décider sans eux.',['impliquer']),
('inference','Pourquoi la responsable souhaite-t-elle consulter aussi les personnes qui utilisent rarement la salle ?','Parce qu’elles peuvent quand même être affectées par les travaux et apporter un point de vue absent de la réunion.',['impliquer']),
('reference_resolution','À qui renvoie « elles aussi » ?','Aux personnes qui utilisent rarement la salle.',['impliquer']),
('grammar_in_context','Quel effet produit « Pourtant » au début du premier paragraphe ?','Il oppose l’apparente simplicité du projet à la diversité réelle des positions.',['position']),
('cloze_transfer','Complète : Pour _____ un public hésitant, il faut répondre à ses objections.','convaincre',['convaincre']),
('summary','Résume la stratégie de décision proposée dans le texte.','Présenter les positions, répondre aux préoccupations concrètes et impliquer davantage de personnes avant de choisir.',['position','impliquer'])
]},
{
'id':'fr-b1-u01-p03','sequence':3,'ptype':'interleaved','title':'Quand la machine refuse le nouveau code','genre':'technical troubleshooting narrative','domains':['educational','professional'],'topics':['technology','troubleshooting','documentation'],'forms':['machine','code','recommencer'],'reviews':['vidéo','caméra'],
'paragraphs':[
"Pour préparer la présentation finale, la classe veut installer une petite exposition interactive. Une machine de découpe doit produire des étiquettes, tandis qu’une caméra enregistre une courte vidéo montrant les étapes du projet. Sami entre un nouveau code de réglage dans la machine, mais l’écran affiche immédiatement un message d’erreur. Il pense d’abord avoir cassé quelque chose et propose de recommencer toute l’installation.",
"Camille lui demande de ne pas recommencer trop vite. Elle compare le code avec l’exemple du manuel et remarque qu’un seul caractère est différent. La machine interprète pourtant ce caractère comme une commande inconnue. Après la correction, elle accepte le code, mais les étiquettes sortent encore trop petites. Cette fois, le problème ne vient pas du code : le document envoyé à la machine utilise une mauvaise échelle. Les élèves corrigent donc le fichier sans effacer les autres réglages.",
"La vidéo enregistrée par la caméra montre finalement deux erreurs différentes et deux méthodes de correction. Camille décide de conserver cette partie au montage, car elle illustre une idée importante : recommencer depuis zéro peut parfois résoudre un problème, mais cela peut aussi effacer des informations utiles. Une démarche plus efficace consiste à identifier ce qui fonctionne déjà, isoler la cause probable, modifier un élément, puis observer le résultat avant de recommencer davantage."
],
'grammar':[{'id':'fr-b1-u01-ne-pas-trop-vite','role':'new','description':'use negated infinitive complements to advise against a premature action'}],
'discourse':[{'id':'fr-b1-u01-troubleshooting-chain','role':'new','description':'separate two technical causes and justify incremental troubleshooting over full reset'}],
'items':[
('gist','Quelle méthode de dépannage Camille préfère-t-elle ?','Identifier ce qui fonctionne, modifier un élément à la fois et observer le résultat avant de recommencer davantage.',['recommencer']),
('literal_detail','Quelle est la première erreur trouvée dans le code ?','Un seul caractère diffère de l’exemple du manuel.',['code']),
('cause_effect','Pourquoi les étiquettes restent-elles trop petites après la correction du code ?','Parce que le document envoyé à la machine utilise une mauvaise échelle.',['machine','code']),
('vocabulary_in_context','Que désigne « machine » ici ?','L’appareil de découpe qui produit les étiquettes.',['machine']),
('vocabulary_in_context','Que signifie « recommencer depuis zéro » ?','Refaire l’ensemble de l’installation au lieu de corriger seulement la partie fautive.',['recommencer']),
('inference','Pourquoi Camille garde-t-elle les erreurs dans la vidéo ?','Parce qu’elles montrent une méthode de résolution de problème plus instructive qu’un résultat parfait sans explication.',['vidéo','caméra']),
('reference_resolution','Dans « elle accepte le code », que désigne « elle » ?','La machine.',['machine','code']),
('grammar_in_context','Pourquoi le texte dit-il « de ne pas recommencer trop vite » ?','La négation porte sur l’action conseillée : Camille recommande d’éviter un redémarrage prématuré.',['recommencer']),
('cloze_transfer','Complète : Avant de _____ tout le processus, vérifie si une seule étape suffit.','recommencer',['recommencer']),
('summary','Résume les deux causes techniques découvertes.','Un caractère rendait le code invalide, puis une mauvaise échelle du fichier produisait des étiquettes trop petites.',['code','machine'])
]},
{
'id':'fr-b1-u01-p04','sequence':4,'ptype':'transfer','title':'Un regard étranger sur le passé et le futur','genre':'museum interview and reflection','domains':['public','educational'],'topics':['migration','museum interpretation','future perspective'],'forms':['étranger','peuple','futur'],'reviews':['retenir','image'],
'paragraphs':[
"Dans un musée local, Camille rencontre Leïla, une chercheuse étrangère venue comparer plusieurs villes industrielles. Le mot étranger ne signifie pas ici qu’elle comprend moins bien le sujet : il indique simplement qu’elle vient d’un autre pays et qu’elle observe certains détails avec une expérience différente. Devant une grande image d’ouvriers quittant une usine, Leïla demande ce que le musée veut retenir de cette période.",
"Le panneau explique qu’un peuple ne se résume pas à une seule histoire. Les habitants de la région ont connu des métiers, des langues et des parcours très variés. Leïla remarque toutefois que l’exposition présente surtout les personnes déjà installées depuis longtemps et parle moins des nouveaux arrivants. Elle ne conclut pas que le musée a tort ; elle demande plutôt quelles voix pourraient être ajoutées lors d’une future mise à jour.",
"La conversation se déplace alors du passé vers le futur. Camille comprend qu’une exposition historique choisit toujours ce qu’elle veut retenir, même lorsqu’elle utilise de nombreuses sources. L’image d’une époque peut donc changer quand de nouveaux témoignages apparaissent. Leïla propose que le futur espace du musée permette aux visiteurs de comparer plusieurs récits. Pour Camille, le regard d’une chercheuse étrangère devient utile précisément parce qu’il révèle des habitudes de présentation que les visiteurs réguliers ne remarquent plus forcément."
],
'grammar':[{'id':'fr-b1-u01-ne-se-resume-pas','role':'new','description':'use ne se résume pas à to reject an overly narrow characterization'}],
'discourse':[{'id':'fr-b1-u01-outsider-perspective','role':'new','description':'use an outsider perspective to expose omissions without treating difference as automatic correctness'}],
'items':[
('gist','Quel apport Leïla fait-elle à la visite du musée ?','Son regard étranger l’aide à remarquer des voix peu représentées et à proposer une exposition future plus comparative.',['étranger','futur']),
('literal_detail','Que montre la grande image observée par Camille et Leïla ?','Des ouvriers quittant une usine.',['image']),
('motive','Pourquoi Leïla demande-t-elle quelles voix pourraient être ajoutées ?','Parce qu’elle remarque que l’exposition parle moins des nouveaux arrivants.',['étranger']),
('vocabulary_in_context','Que signifie « étranger » lorsqu’il décrit Leïla ?','Qu’elle vient d’un autre pays, sans implication sur la valeur de son analyse.',['étranger']),
('vocabulary_in_context','Comment le texte emploie-t-il « peuple » ?','Pour parler d’une population dont l’histoire contient des parcours variés et ne peut être réduite à un seul récit.',['peuple']),
('inference','Pourquoi le texte précise-t-il que Leïla ne conclut pas que le musée a tort ?','Pour distinguer une critique des omissions d’un jugement selon lequel toute l’exposition serait fausse.',['étranger']),
('reference_resolution','Dans « il révèle des habitudes », à quoi renvoie « il » ?','Au regard d’une chercheuse étrangère.',['étranger']),
('grammar_in_context','Quel effet a « ne se résume pas à » dans l’argument ?','L’expression rejette une représentation trop simple avant d’introduire la diversité des expériences.',['peuple']),
('cloze_transfer','Complète : Le musée prépare une nouvelle salle pour le _____.','futur',['futur']),
('summary','Résume le lien entre passé et futur dans le passage.','Le musée choisit ce qu’il veut retenir du passé, mais de nouvelles voix peuvent modifier l’image proposée au public futur.',['retenir','image','futur'])
]},
{
'id':'fr-b1-u01-p05','sequence':5,'ptype':'integration','title':'Profiter du projet sans regretter les détours','genre':'project reflection essay','domains':['educational','personal'],'topics':['project reflection','opportunity cost','learning process'],'forms':['regretter','profiter','ennui'],'reviews':['proposer','gérer'],
'paragraphs':[
"À l’approche de la présentation, Camille relit son carnet de projet. Elle pourrait regretter le temps consacré à certaines pistes qui n’ont rien donné : une archive fermée, une interview déplacée et plusieurs essais techniques inutilisables. Pourtant, elle constate que ces détours lui ont appris à mieux gérer l’incertitude. Elle ne veut donc pas supprimer toute difficulté de son récit simplement pour donner l’impression que le projet s’est déroulé sans problème.",
"Sami lui propose de profiter de la présentation pour montrer aussi une décision abandonnée. Camille accepte et choisit l’exemple de la machine. Au début, recommencer tout le réglage semblait logique ; ensuite, le groupe a compris qu’une correction plus précise suffisait. Ce changement permet d’expliquer comment une erreur peut devenir utile lorsqu’on en tire une méthode. La classe doit néanmoins gérer le temps : elle ne peut pas raconter chaque détail.",
"Camille pense aussi à l’ennui. Certaines tâches répétitives, comme classer des fichiers, lui ont donné de l’ennui sur le moment, mais elles ont rendu les comparaisons plus fiables. Elle ne cherche pas à profiter artificiellement de chaque minute ni à prétendre que tout était passionnant. Son bilan est plus nuancé : elle peut regretter une mauvaise décision tout en profitant de ce qu’elle lui a appris. Pour la présentation, elle propose donc de distinguer les détours inutiles des erreurs qui ont produit une meilleure façon de travailler."
],
'grammar':[{'id':'fr-b1-u01-tout-en','role':'new','description':'use tout en + present participle/infinitive framing to hold two apparently conflicting evaluations together'}],
'discourse':[{'id':'fr-b1-u01-reflective-evaluation','role':'new','description':'distinguish wasted effort, productive error and unavoidable boring work in a nuanced project evaluation'}],
'items':[
('gist','Quel bilan Camille fait-elle de ses difficultés ?','Elle distingue les détours inutiles des erreurs ou tâches difficiles qui lui ont appris une meilleure méthode.',['regretter','profiter','ennui']),
('literal_detail','Quel exemple Sami propose-t-il de montrer ?','Une décision abandonnée, notamment le premier plan de réglage de la machine.',['proposer']),
('cause_effect','Pourquoi Camille ne raconte-t-elle pas chaque détail ?','Parce qu’elle doit gérer un temps de présentation limité.',['gérer']),
('vocabulary_in_context','Que signifie « regretter » une décision ici ?','Reconnaître qu’on aurait préféré prendre une autre décision.',['regretter']),
('vocabulary_in_context','Que signifie « profiter de ce qu’elle lui a appris » ?','Tirer un bénéfice ou un apprentissage de l’expérience.',['profiter']),
('inference','Pourquoi Camille parle-t-elle aussi de l’ennui ?','Pour montrer qu’une tâche utile peut être peu intéressante sur le moment sans être inutile.',['ennui']),
('reference_resolution','Dans « ce qu’elle lui a appris », à quoi renvoie « elle » ?','À la mauvaise décision ou à l’expérience associée.',['regretter','profiter']),
('grammar_in_context','Que permet d’exprimer « tout en profitant » dans la conclusion ?','Que le regret d’une décision et l’apprentissage qu’elle produit peuvent être vrais en même temps.',['regretter','profiter']),
('cloze_transfer','Complète : Nous pouvons _____ de cette occasion pour expliquer notre méthode.','profiter',['profiter']),
('summary','Résume le principe de sélection de Camille pour la présentation.','Elle veut montrer les erreurs qui éclairent une méthode, mentionner l’ennui utile sans l’exagérer et supprimer les détails qui n’aident pas le public.',['ennui'])
]}
]

CHECKPOINT={
'id':'fr-b1-u01-p06','sequence':6,'ptype':'checkpoint','title':'Ce que l’enquête a vraiment changé','genre':'B1 cumulative project summary','domains':['educational','public','personal'],'topics':['research process','evidence','reflection'],'paragraphs':[
"Au terme du projet, Camille ne considère plus une enquête comme une ligne droite. Pour poursuivre une question sur une autre époque, elle a appris à chercher chaque trace, puis à comparer ce qu’elle indique avec d’autres documents. Dans les réunions, elle sait qu’une position n’est pas un obstacle à éliminer : pour convaincre, il faut comprendre les raisons de l’autre personne et impliquer celles qui seront touchées par la décision.",
"Le travail technique lui a donné une leçon semblable. Une machine peut refuser un code pour une petite erreur, mais recommencer tout le système n’est pas toujours la meilleure réponse. Au musée, le regard d’un chercheur étranger lui a rappelé qu’un peuple contient plusieurs histoires et que la manière de raconter le passé influence aussi le futur. Aucune de ces observations ne fournit une règle parfaite ; elles donnent plutôt des questions à poser avant d’agir.",
"Camille peut regretter certains détours sans regretter le projet. Elle a appris à profiter d’une erreur lorsqu’elle révèle une méthode, et à accepter l’ennui de certaines tâches lorsqu’elles rendent le résultat plus fiable. Elle sait aussi que proposer une solution exige souvent de gérer le temps, les sources et les rôles. Son progrès principal n’est donc pas d’éviter toute erreur, mais de mieux décider laquelle mérite une correction rapide, laquelle demande une enquête plus longue et laquelle peut devenir une source d’apprentissage."
],
'grammar':[{'id':'fr-b1-u01-cumulative-contrast','role':'integration','description':'integrate contrast, relative clauses and infinitive complements across a multi-paragraph summary'}],
'discourse':[{'id':'fr-b1-u01-calibration-checkpoint','role':'integration','description':'synthesize evidence, participation, troubleshooting, perspective and reflective evaluation across the unit'}],
'items':[
('gist','Quelle compétence générale Camille développe-t-elle pendant le projet ?','Elle apprend à vérifier, comparer, impliquer les autres et adapter sa réponse au type de problème.',['impliquer']),
('literal_detail','Que doit-elle comparer lorsqu’elle poursuit une question historique ?','Chaque trace avec d’autres documents de la même enquête.',['poursuivre','trace']),
('cause_effect','Pourquoi comprendre une position peut-il aider à convaincre ?','Parce que les raisons de cette position indiquent quelles préoccupations une proposition doit réellement traiter.',['position','convaincre']),
('vocabulary_in_context','Quels trois mots résument le problème technique du deuxième paragraphe ?','machine, code et recommencer',['machine','code','recommencer']),
('inference','Quel lien le passage établit-il entre un regard étranger, un peuple et le futur ?','Un regard extérieur peut révéler des récits absents, ce qui peut modifier la manière dont un peuple choisit de se présenter à l’avenir.',['étranger','peuple','futur']),
('motive','Pourquoi Camille accepte-t-elle certaines tâches qui provoquent de l’ennui ?','Parce qu’elles peuvent rendre le résultat plus fiable même si elles sont peu intéressantes sur le moment.',['ennui']),
('grammar_in_context','Quel contraste exprime « peut regretter certains détours sans regretter le projet » ?','Elle distingue le jugement sur quelques décisions du jugement sur l’ensemble de l’expérience.',['regretter']),
('reference_resolution','Dans « elles donnent plutôt des questions », à quoi renvoie « elles » ?','Aux observations et leçons tirées des différentes situations.',['époque']),
('cloze_transfer','Complète : Une erreur peut être utile si l’on sait _____ de ce qu’elle révèle.','profiter',['profiter']),
('summary','Résume l’unité en une phrase.','Camille apprend à poursuivre les traces, discuter des positions, corriger un code, comparer les récits d’un peuple et profiter des erreurs sans ignorer leurs limites.',['poursuivre','trace','position','code','peuple','profiter'])
]}

def text_of(s): return '\n\n'.join(s['paragraphs'])
def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s['items'],ids); text=text_of(s)
    return {'id':s['id'],'language':'fr','cefr':'B1','unit':1,'sequence':s['sequence'],'revision':1,
            'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],'topics':s['topics'],
            'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),
            'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,
            'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':q,'answer_key':a,
            'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'French B1 Unit 01 calibration; final language-wide audit deferred.'},
            'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French B1 Unit 01 calibration batch.','All-prior-French freshness, source identity, B1 word band, exact deliberate-review visibility, question linkage and zero-new checkpoint are enforced.']},
            'paired_text_group':None,'prerequisites':['French A1 and A2 generated with generation-integrity PASS'],
            'difficulty_notes_internal':'B1 calibration: multi-paragraph connected text, multi-sentence inference, motive, summary and broader context transfer.',
            'reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_b1_u01','calibration']}

def build(a1,a2,D):
    prior=base.prior(a1+a2); bad=[]
    prior_forms={t.get('form') for r in a1+a2 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    for f in FORMS:
        if f not in D: bad.append(f+':missing_lexicon')
        if prior.get(f) or f in prior_forms: bad.append(f+':already_deliberate')
    if bad: raise AssertionError('B1 Unit01 candidate failures: '+', '.join(bad))
    out=[]
    for s in SPECS:
        text=text_of(s); new=[base.nt(f,text,D) for f in s['forms']]; reviews=[base.rev(f,prior) for f in s['reviews']]
        ids={t['form']:t['id'] for t in new+reviews}; out.append(mk(s,new,reviews,ids))
    cp=dict(CHECKPOINT); cp['paragraphs']=CHECKPOINT['paragraphs']; text=text_of(cp)
    reviews=[base.cur(f,D) for f in FORMS]; ids={t['form']:t['id'] for t in reviews}; out.append(mk(cp,[],reviews,ids,True))
    return out

def main():
    a1_blob=subprocess.check_output(['git','hash-object',str(A1)],text=True).strip(); a2_blob=subprocess.check_output(['git','hash-object',str(A2)],text=True).strip()
    if a1_blob!=EXPECTED_A1_BLOB: raise AssertionError(f'A1 blob drift: {a1_blob} != {EXPECTED_A1_BLOB}')
    if a2_blob!=EXPECTED_A2_BLOB: raise AssertionError(f'A2 blob drift: {a2_blob} != {EXPECTED_A2_BLOB}')
    if CANON.exists() and CANON.read_text(encoding='utf-8').strip(): raise AssertionError('B1 canonical already exists/nonempty; Unit01 writer refuses collision')
    a1=[json.loads(x) for x in A1.read_text(encoding='utf-8').splitlines() if x.strip()]; a2=[json.loads(x) for x in A2.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(a1)!=60 or len(a2)!=60 or a1[-1]['id']!='fr-a1-u10-p06' or a2[-1]['id']!='fr-a2-u10-p06': raise AssertionError('unexpected A1/A2 prerequisite state')
    D=base.deck(); unit=build(a1,a2,D); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    prior_ids={t.get('id') for r in a1+a2 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}; prior_forms={t.get('form') for r in a1+a2 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
    newids=[]; newforms=[]
    if [r['sequence'] for r in unit]!=list(range(1,7)) or [r['id'] for r in unit]!=[f'fr-b1-u01-p{i:02d}' for i in range(1,7)]: raise AssertionError('B1 Unit01 continuity failure')
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 220<=r['word_count']<=350: raise AssertionError(f"{r['id']}: B1 word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        amap={a['question_id']:a['id'] for a in r['answer_key']}; decl={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[]) if isinstance(t,dict)}
        for q in r['questions']:
            if amap.get(q['id'])!=q['answer_id'] or any(x not in decl for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} {q['id']}: linkage/target declaration")
        if r['sequence']<=5 and len(r['new_lexical_targets'])!=3: raise AssertionError(f"{r['id']}: expected controlled calibration load of 3 new targets")
        for t in r['new_lexical_targets']:
            s=D.get(t['form'])
            if t['id'] in prior_ids or t['form'] in prior_forms or not s or t['source_rank']!=s['rank'] or t['id']!=base.tid(s['rank']) or base.cnt(r['text'],t['form'])!=t['exposures_in_text']: raise AssertionError(f"{r['id']}: source/exposure/freshness drift {t}")
            newids.append(t['id']); newforms.append(t['form'])
        for t in r['review_lexical_targets']:
            if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if len(newids)!=15 or len(set(newids))!=15 or len(set(newforms))!=15 or unit[-1]['new_lexical_targets']!=[]: raise AssertionError('B1 Unit01 lexical-cycle invariant')
    CANON.parent.mkdir(parents=True,exist_ok=True); CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in unit),encoding='utf-8')
    print(json.dumps({'status':'PASS','level':'B1','unit':1,'passages':6,'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':D[f]['rank'],'id':base.tid(D[f]['rank'])} for f in FORMS],'questions':60,'answers':60,'p06_new_targets':0},ensure_ascii=False))
if __name__=='__main__': main()
