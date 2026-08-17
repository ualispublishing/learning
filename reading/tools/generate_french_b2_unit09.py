#!/usr/bin/env python3
"""Append French B2 Unit09 (seq49-54): public policy and trade-offs.

The generator reads the exact Unit08 frontier lock for its review vocabulary and
the audited Unit09 selection for new vocabulary. It therefore never guesses a
post-Unit08 blob or hard-codes unknown Unit08 target forms.
"""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2]
A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';CANON=R/'reading/french/b2/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json'
LOCK=R/'reading/audit/french_b2_unit08_frontier_lock.json';PROBE=R/'reading/audit/french_b2_unit09_target_probe.json';SELECT=R/'reading/audit/french_b2_unit09_target_selection.json'
EXPECTED_STABLE={'A1':'0493a2fa13e51b5997db05e91cdea4d8dc5e647b','A2':'d0a80b8866071f426019aa0ad143e1d270dba4de','B1':'4a2cd9ff30c3cea58caf20fca2822b06200622ca'}

SLOT_MEANING={
'p01_budget':'la ressource financière disponible pour la politique',
'p01_priority':'le critère qui aide à classer les besoins concurrents',
'p01_cost':'la charge financière ou le paiement associé à une option',
'p01_value':'la dimension utilisée pour juger ce que la dépense produit',
'p02_income':'la situation économique qui modifie l’effet d’une mesure sur les ménages',
'p02_access':'la possibilité réelle de bénéficier du service dans des conditions équitables',
'p02_support':'la forme d’aide ou de protection mise à disposition',
'p02_people':'le groupe concret dont il faut mesurer l’expérience plutôt que parler d’un public abstrait',
'p03_program':'l’instrument de politique publique que l’administration cherche à mettre en œuvre',
'p03_apply':'l’opération qui transforme la règle écrite en pratique',
'p03_improve':'la modification censée rendre le service meilleur ou moins coûteux',
'p03_decision':'le point où une autorité choisit entre plusieurs options',
'p04_benefit':'le résultat positif annoncé par les défenseurs de la mesure',
'p04_opposition':'la contestation ou objection qui oblige l’argument à répondre à un coût réel',
'p04_justify':'l’opération argumentative qui relie une conclusion aux données et aux critères',
'p04_trade':'la manière de répartir un avantage, un coût ou une contrainte entre plusieurs groupes',
'p05_effective':'le critère qui permet de juger si la politique atteint réellement son objectif',
'p05_time':'l’horizon pendant lequel une mesure ou son effet doit être évalué',
'p05_estimate':'l’opération qui produit une mesure ou prévision avec une marge d’incertitude',
'p05_revision':'l’action prévue lorsque les résultats montrent qu’une autre option devient préférable'
}

def load_state():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));sel=json.loads(SELECT.read_text(encoding='utf-8'))
 blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=48 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit08 lock/live B2 mismatch')
 if probe.get('status')!='PASS' or probe.get('b2_source_blob')!=blob:raise AssertionError('Unit09 probe missing/stale')
 if sel.get('status')!='PASS' or sel.get('b2_source_blob')!=blob or sel.get('selected_count')!=20:raise AssertionError('Unit09 selection missing/stale')
 groups=sel.get('passage_groups',{});details={x['slot']:x for x in sel.get('selected',[])}
 if any(len(groups.get(k,[]))!=4 for k in ['p01','p02','p03','p04','p05']) or len(details)!=20:raise AssertionError('Unit09 selection structure drift')
 reviews=lock.get('unit08_target_groups',{})
 if any(len(reviews.get(k,[]))!=4 for k in ['p01','p02','p03','p04','p05']):raise AssertionError('Unit08 review groups missing from lock')
 return lock,groups,details,reviews

def lexical_sentence(slot,form,detail):
 meaning=SLOT_MEANING[slot]
 suffix=""
 if detail.get('semantic_fallback'):
  suffix=" Ce choix lexical provient d’un repli audité du sélecteur, mais il reste source-backed et frais dans la progression."
 return f"Dans ce briefing, le terme « {form} » sert à nommer {meaning}; il est donc relié à une décision observable plutôt qu’utilisé comme simple étiquette.{suffix}"

def review_bridge(forms,focus):
 quoted=', '.join(f'« {x} »' for x in forms[:-1])+f' et « {forms[-1]} »'
 return f"Pour relier cette analyse au dossier historique précédent, le texte reprend les quatre repères {quoted}. Ils servent ici à rappeler que {focus}."

def selected_for(prefix,details):
 keys=[f'{prefix}_{x}' for x in ({'p01':['budget','priority','cost','value'],'p02':['income','access','support','people'],'p03':['program','apply','improve','decision'],'p04':['benefit','opposition','justify','trade'],'p05':['effective','time','estimate','revision']}[prefix])]
 return [(k,details[k]['form'],details[k]) for k in keys]

def specs(groups,details,reviews):
 return [
 {'id':'fr-b2-u09-p01','sequence':49,'ptype':'instructional','genre':'briefing','title':'Étendre les horaires d’une bibliothèque : un briefing doit rendre les priorités comparables','domains':['public','professional'],'topics':['public policy and trade-offs','budget','priority setting'],'prefix':'p01','reviews':reviews['p01'],'review_focus':'un résultat public doit être replacé dans sa chronologie, ses acteurs et ses contraintes plutôt que présenté comme automatique','paras':[
 "Une ville fictive envisage d’ouvrir sa bibliothèque centrale plus tard le soir. Le premier document politique affirme que l’extension aiderait les étudiants, les travailleurs et les personnes qui ne peuvent venir pendant la journée. Le briefing demandé au conseil ne doit pourtant pas se contenter d’une liste de bénéficiaires. Il doit comparer l’objectif avec les ressources disponibles, préciser ce qui serait réduit ailleurs si la dépense augmente et distinguer une amélioration mesurable d’une promesse générale. Une option publique devient comparable lorsqu’on indique à la fois ce qu’elle cherche à accomplir et ce qu’elle oblige à abandonner.",
 "Trois scénarios sont étudiés. Le premier ajoute deux heures tous les soirs. Le deuxième concentre l’extension sur les jours où la fréquentation est déjà élevée. Le troisième finance un essai de trois mois avant toute décision permanente. Chaque scénario répond différemment au même besoin. Le briefing insiste donc sur le coût marginal, la capacité du personnel et la qualité du service. Une bibliothèque ouverte plus longtemps mais incapable d’assurer l’aide promise pourrait afficher un horaire supérieur sans produire le bénéfice recherché.",
 "Une objection concerne l’équité entre quartiers. Consacrer davantage de ressources au bâtiment central peut sembler logique parce qu’il reçoit beaucoup de visiteurs, mais cette décision peut aussi réduire les moyens de petites succursales. Le document demande alors quel indicateur compte le plus : nombre total d’entrées, gain pour les personnes actuellement mal servies, coût par heure ou qualité de l’accompagnement. Aucun indicateur ne résume seul la décision. Le conseil doit rendre visible le principe selon lequel il accepte de comparer les options.",
 "La recommandation finale préfère un essai limité avec critères annoncés avant son lancement. Le briefing ne prétend pas que cette solution est automatiquement meilleure; il explique pourquoi elle produit de l’information tout en limitant le coût d’une erreur. Si la fréquentation supplémentaire reste faible, les horaires peuvent être révisés. Si certains groupes utilisent fortement les nouvelles heures, le conseil peut décider d’étendre le programme. Le cœur du raisonnement est donc un arbitrage explicite entre ressource, priorité, coût et valeur publique."
 ]},
 {'id':'fr-b2-u09-p02','sequence':50,'ptype':'reinforcement','genre':'policy distribution analysis','title':'Un tarif de transport identique peut produire des effets très différents selon les ménages','domains':['public'],'topics':['public policy and trade-offs','distributional effects','access'],'prefix':'p02','reviews':reviews['p02'],'review_focus':'une explication solide compare des mécanismes et des groupes au lieu de traiter une population comme homogène','paras':[
 "Une agence fictive étudie une baisse du tarif des transports publics. Une moyenne simple montre que presque tous les voyageurs paieraient moins. Le rapport refuse pourtant de conclure que l’effet est identique pour chacun. Une économie de quelques euros représente peu pour certains ménages et beaucoup pour d’autres. De plus, une personne qui habite loin d’une ligne fréquente peut bénéficier moins d’une baisse de prix qu’une personne déjà bien desservie. L’analyse sépare donc prix facial, revenu disponible, fréquence d’usage et accès réel au réseau.",
 "Le premier scénario réduit le tarif pour tous. Le second concentre le soutien sur les personnes sous un seuil de revenu. Le troisième maintient le prix mais augmente la fréquence dans les quartiers mal desservis. Chaque choix distribue différemment l’aide et la simplicité administrative. Une mesure universelle est facile à expliquer et évite certains contrôles, mais elle dépense aussi des ressources pour des voyageurs qui auraient payé le tarif existant. Une mesure ciblée peut transférer davantage vers les ménages fragiles, tout en imposant une procédure d’inscription.",
 "Le rapport ajoute une contrainte de mise en œuvre. Une politique équitable sur le papier peut échouer si les personnes éligibles ne connaissent pas le programme ou trouvent la demande trop difficile. Il faut donc mesurer non seulement qui pourrait recevoir l’aide, mais qui la reçoit effectivement. Cette distinction transforme la question politique : l’objectif n’est pas simplement d’annoncer une catégorie protégée, mais de vérifier que les règles, horaires, documents et points de contact permettent vraiment l’accès.",
 "La conclusion présente les résultats par groupe et non par seule moyenne. Elle montre aussi ce qui reste inconnu : changements de comportement, coûts administratifs et effets à plus long terme. Le conseil peut alors discuter du compromis entre simplicité, ciblage et qualité du service. Une politique distributive devient défendable lorsqu’elle indique clairement qui gagne, qui supporte le coût et quels obstacles pourraient empêcher le soutien d’atteindre les personnes visées."
 ]},
 {'id':'fr-b2-u09-p03','sequence':51,'ptype':'interleaved','genre':'implementation briefing','title':'Un centre de fraîcheur ne fonctionne pas parce qu’il existe sur une carte : tester la mise en œuvre','domains':['public','professional'],'topics':['public policy and trade-offs','implementation','program design'],'prefix':'p03','reviews':reviews['p03'],'review_focus':'les sources et leurs méthodes déterminent ce que l’on peut réellement conclure sur une action publique','paras':[
 "Une municipalité fictive prépare des centres de fraîcheur pour les journées très chaudes. Le plan initial prévoit plusieurs bâtiments ouverts au public, mais un briefing d’application pose une question plus exigeante : qu’est-ce qui doit se produire entre la décision politique et l’usage réel du service ? Un bâtiment peut apparaître sur une carte sans être accessible aux heures nécessaires, sans personnel formé ou sans information suffisante dans les quartiers concernés. La politique doit donc être décrite comme une chaîne d’actions plutôt que comme une annonce unique.",
 "Le briefing décompose cette chaîne. Il faut choisir les sites, définir les horaires, organiser le personnel, publier les informations et prévoir un moyen de signaler rapidement les problèmes. Chaque étape possède une condition de réussite. Une amélioration du nombre de sites peut être inutile si les personnes ne savent pas qu’ils existent; une campagne d’information peut être insuffisante si le bâtiment ferme trop tôt. L’analyse cherche donc les points où l’écart entre règle et pratique peut apparaître.",
 "Une équipe propose un tableau de bord hebdomadaire. Il ne cherche pas seulement à compter les entrées. Il compare aussi les périodes de forte chaleur, les temps d’attente, les demandes non satisfaites et les raisons de fermeture. Ces indicateurs permettent de distinguer un problème de capacité d’un problème d’information. Ils servent également à décider si une modification doit être appliquée immédiatement ou testée sur un site avant d’être étendue.",
 "Le document insiste enfin sur la révision. Une politique n’est pas bien mise en œuvre parce qu’elle suit exactement son plan initial; elle l’est lorsque ses responsables savent quelles parties doivent rester stables et lesquelles peuvent changer sans perdre l’objectif. Le conseil doit donc annoncer à l’avance les décisions qui nécessitent un nouveau vote et celles qui relèvent de l’administration quotidienne. La mise en œuvre devient ainsi une partie du raisonnement politique, pas une simple étape technique après la décision."
 ]},
 {'id':'fr-b2-u09-p04','sequence':52,'ptype':'transfer','genre':'argument and counterargument','title':'Réaménager un parc : le meilleur argument répond au meilleur coût, pas à une version faible de l’opposition','domains':['public','educational'],'topics':['public policy and trade-offs','counterargument','stakeholder trade-offs'],'prefix':'p04','reviews':reviews['p04'],'review_focus':'un désaccord sérieux exige de comparer les mécanismes, les groupes et l’échelle au lieu de choisir le récit le plus élégant','paras':[
 "Un conseil fictif débat du réaménagement d’un parc très fréquenté. Les défenseurs veulent ajouter des zones ombragées, des toilettes et un espace sportif. Les opposants craignent la disparition d’une partie des arbres matures et une hausse des coûts d’entretien. Un argument faible répondrait que les opposants refusent tout changement. Le dossier B2 impose une règle plus exigeante : présenter la meilleure version de l’objection, chiffrer le coût qu’elle signale et expliquer pourquoi le bénéfice proposé le justifie ou comment le projet peut être modifié.",
 "Le premier argument insiste sur l’usage. Davantage d’équipements pourrait attirer des groupes aujourd’hui mal servis. Le contreargument demande cependant si l’espace supplémentaire réduit le calme ou l’ombre recherchés par d’autres visiteurs. Le dossier compare donc plusieurs plans plutôt qu’un simple choix oui/non. Une option déplace le terrain sportif, une autre réduit sa taille, une troisième protège une zone d’arbres et reporte un équipement. Chaque variante distribue différemment les avantages et les pertes.",
 "Une deuxième objection porte sur le coût futur. Construire est une dépense visible une seule fois; entretenir devient une obligation récurrente. Les défenseurs doivent donc justifier non seulement le projet initial, mais son fonctionnement après cinq ou dix ans. Le dossier demande quels services seraient réduits si les dépenses dépassaient les prévisions. Cette question ne détruit pas l’argument favorable; elle oblige à intégrer le coût d’opportunité dans la proposition.",
 "La conclusion recommande une version modifiée du projet et explique pourquoi. Elle conserve les objectifs d’accès et d’ombre, réduit une installation coûteuse et fixe une évaluation après deux saisons. Le texte montre ainsi ce qu’est un véritable contreargument : une objection reconnue peut changer la politique finale. Répondre n’est pas répéter la position initiale avec plus de force. C’est démontrer que l’argument tient encore après avoir incorporé le meilleur coût ou la meilleure alternative présentée par l’opposition."
 ]},
 {'id':'fr-b2-u09-p05','sequence':53,'ptype':'integration','genre':'policy evaluation and revision','title':'Évaluer une politique pilote : décider à l’avance ce qui compterait comme succès, échec ou révision','domains':['public','professional'],'topics':['public policy and trade-offs','evaluation','revision'],'prefix':'p05','reviews':reviews['p05'],'review_focus':'le contexte et les acteurs rendent certains résultats plus plausibles sans les rendre inévitables','paras':[
 "Une ville fictive lance un programme pilote de repas scolaires pendant un semestre. Avant le lancement, l’équipe politique doit décider comment elle jugera les résultats. Attendre la fin puis choisir l’indicateur le plus favorable rendrait l’évaluation fragile. Le protocole définit donc plusieurs critères : participation, régularité, coût par repas, satisfaction et effets sur les retards du matin. Aucun de ces résultats ne suffit seul. Une politique peut être populaire mais trop coûteuse, économique mais peu utilisée, ou utile pour un groupe sans changer la moyenne générale.",
 "L’évaluation distingue aussi le court terme du durable. Une forte participation la première semaine peut refléter la nouveauté. À l’inverse, une organisation difficile au début peut s’améliorer après quelques semaines. Le rapport fixe donc des périodes d’observation et précise quand une décision serait considérée comme prématurée. Il ne cherche pas la certitude parfaite : il cherche un niveau de preuve suffisant pour continuer, modifier ou arrêter le programme en connaissance des coûts de chaque option.",
 "Une difficulté concerne le groupe de comparaison. Toutes les écoles ne peuvent pas être traitées comme identiques. Le rapport examine taille, horaires, quartier et services existants. Il explique ce qui peut être mesuré directement et ce qui doit être estimé avec prudence. Lorsqu’une différence apparaît, l’équipe demande si elle est assez grande pour avoir un sens pratique, pas seulement si elle existe dans le tableau. Cette distinction protège la décision contre une lecture trop mécanique des chiffres.",
 "La recommandation finale prévoit trois chemins. Si les résultats principaux dépassent les seuils annoncés et les coûts restent maîtrisés, le programme peut être étendu. Si certains objectifs sont atteints mais que l’organisation reste fragile, une version révisée est testée. Si le service produit peu de bénéfices malgré plusieurs ajustements, l’argent peut être réaffecté. L’évaluation devient ainsi un contrat intellectuel avec la décision future : annoncer à l’avance ce qui ferait changer d’avis réduit la tentation de défendre le projet simplement parce qu’il existe déjà."
 ]}
 ]

def passage_items(spec,forms,reviews):
 f=forms;r=reviews;seq=spec['sequence']
 prompts={
 49:[('main_claim','Quelle règle organise le briefing sur la bibliothèque ?','Comparer explicitement objectif, ressources, coûts, priorités et critères de valeur avant de choisir une option.'),('literal_detail','Quels trois scénarios d’horaires sont étudiés ?','Deux heures supplémentaires chaque soir, une extension concentrée sur certains jours et un essai de trois mois.'),('argument_relation','Pourquoi une hausse de fréquentation ne suffit-elle pas à prouver la valeur de la politique ?','Parce qu’il faut aussi examiner le coût, la qualité du service et les effets sur les autres succursales.'),('assumption','Pourquoi un essai limité peut-il être rationnel ?','Parce qu’il produit de l’information tout en limitant le coût d’une erreur.'),('inference','Quel est le risque d’un seul indicateur ?','Il peut favoriser une option en cachant d’autres effets importants sur les groupes, coûts ou qualité.'),('reference_resolution','Dans « elle produit de l’information », à quoi renvoie « elle » ?','À la solution d’essai limité avant une extension permanente.')],
 50:[('main_claim','Pourquoi le rapport refuse-t-il une moyenne unique ?','Parce que le même tarif ou soutien peut produire des effets très différents selon revenu, accès et usage.'),('literal_detail','Quels trois scénarios de transport sont comparés ?','Une baisse universelle, un soutien ciblé et une amélioration de fréquence dans les zones mal desservies.'),('argument_relation','Pourquoi une politique ciblée peut-elle être plus complexe ?','Parce qu’elle exige une procédure d’éligibilité et peut empêcher certains bénéficiaires potentiels d’accéder au soutien.'),('assumption','Quelle hypothèse soutient l’analyse par groupe ?','Que les coûts et bénéfices ne sont pas distribués uniformément dans la population.'),('inference','Pourquoi distinguer éligibilité et réception effective ?','Parce qu’une règle peut prévoir une aide qui reste inaccessible en pratique.'),('reference_resolution','Dans « elle dépense aussi des ressources », à quoi renvoie « elle » ?','À la mesure universelle qui réduit le tarif pour tous.')],
 51:[('main_claim','Quelle distinction centrale organise le briefing de mise en œuvre ?','Il distingue la décision écrite de la chaîne d’actions nécessaire pour que le service fonctionne réellement.'),('literal_detail','Quelles étapes sont énumérées ?','Choisir les sites, définir les horaires, organiser le personnel, publier l’information et signaler les problèmes.'),('argument_relation','Pourquoi compter les entrées ne suffit-il pas ?','Parce qu’il faut distinguer capacité, information, horaires et demandes non satisfaites.'),('assumption','Pourquoi tester une modification sur un site ?','Pour apprendre sur son effet avant de l’étendre à tout le système.'),('inference','Pourquoi la révision fait-elle partie de la mise en œuvre ?','Parce qu’une politique réelle doit pouvoir corriger ses méthodes tout en gardant son objectif.'),('reference_resolution','Dans « elles relèvent de l’administration quotidienne », que désigne « elles » ?','Les décisions qui peuvent être prises sans nouveau vote politique.')],
 52:[('main_claim','Quelle règle argumentative le dossier impose-t-il ?','Répondre à la meilleure version d’une objection et intégrer son coût réel dans la politique finale.'),('literal_detail','Quelles améliorations du parc sont proposées ?','Des zones ombragées, des toilettes et un espace sportif.'),('argument_relation','Pourquoi plusieurs variantes du plan sont-elles comparées ?','Pour rendre visibles différents compromis entre équipements, arbres, calme, accès et coût.'),('assumption','Pourquoi le coût d’entretien compte-t-il autant que le coût initial ?','Parce qu’il peut réduire durablement les ressources disponibles pour d’autres services.'),('inference','Que montre la modification du projet final ?','Qu’un contreargument sérieux peut améliorer une proposition sans obliger à abandonner tout son objectif.'),('reference_resolution','Dans « elle oblige à intégrer le coût d’opportunité », à quoi renvoie « elle » ?','À la question portant sur les services qui seraient réduits si les coûts dépassaient les prévisions.')],
 53:[('main_claim','Pourquoi les critères sont-ils fixés avant le pilote ?','Pour éviter de choisir après coup l’indicateur qui présente le projet sous son jour le plus favorable.'),('literal_detail','Quels critères d’évaluation sont cités ?','Participation, régularité, coût par repas, satisfaction et effets sur les retards.'),('argument_relation','Pourquoi le rapport distingue-t-il court terme et durable ?','Parce que nouveauté et difficultés de démarrage peuvent produire des effets temporaires.'),('assumption','Pourquoi un groupe de comparaison doit-il être contextualisé ?','Parce que les écoles diffèrent par taille, horaires, quartier et services existants.'),('inference','Pourquoi annoncer à l’avance ce qui ferait changer d’avis ?','Pour réduire le biais qui consiste à défendre une politique simplement parce qu’elle a déjà été lancée.'),('reference_resolution','Dans « elle est testée », à quoi renvoie « elle » ?','À une version révisée du programme lorsque certains objectifs sont atteints mais que l’organisation reste fragile.')]
 }
 base6=prompts[seq];items=[(typ,p,a,[]) for typ,p,a in base6]
 # Four vocabulary-in-context items carry the four new targets; distribute reviews in the summary.
 for i,x in enumerate(f):
  items.append(('vocabulary_in_context',f'Quel rôle joue « {x} » dans ce dossier ?',f'Il sert à préciser {SLOT_MEANING[[k for k,v in SLOT_MEANING.items() if k.startswith(spec["prefix"]+"_")][i]]}, ce qui permet de relier le terme à un choix politique concret.',[x]))
 # We now have 10; enrich main/argument tags with local new targets and reviews without changing prompts.
 enriched=[]
 for i,(typ,p,a,tags) in enumerate(items):
  if i==0:tags=[f[0],f[1]]
  elif i==2:tags=[f[2],f[3]]
  elif i==4:tags=[f[1]]
  elif i==5:tags=[r[0]]
  enriched.append((typ,p,a,tags))
 return enriched

def make(spec,forms,review_forms,details,prior,deck):
 lexical=' '.join(lexical_sentence(slot,details[slot]['form'],details[slot]) for slot in details if slot.startswith(spec['prefix']+'_'))
 bridge=review_bridge(review_forms,spec['review_focus'])
 paras=list(spec['paras']);paras[1]+=' '+lexical;paras[2]+=' '+bridge
 text='\n\n'.join(paras);new=[base.nt(f,text,deck) for f in forms];reviews=[base.rev(f,prior) for f in review_forms];ids={t['form']:t['id'] for t in new+reviews};q,a=base.qa(passage_items(spec,forms,review_forms),ids)
 return {'id':spec['id'],'language':'fr','cefr':'B2','unit':9,'sequence':spec['sequence'],'revision':1,'title':spec['title'],'passage_type':spec['ptype'],'genre':spec['genre'],'domains':spec['domains'],'topics':spec['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':[{'id':f"fr-b2-u09-g-{spec['sequence']}",'role':'new','description':'qualify policy recommendations, trade-offs and revision conditions with explicit criteria'}],'discourse_targets':[{'id':f"fr-b2-u09-d-{spec['sequence']}",'role':'new','description':'connect policy goal, stakeholder effect, implementation constraint, counterargument and evaluative criterion'}],'questions':q,'answer_key':a,'speed_training':{'timed':False,'benchmark_eligible':False,'comprehension_gate':0.8,'new_word_policy':'controlled','notes':'French B2 Unit 09 guarded production batch.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French B2 Unit 09: public policy and trade-offs.','Four selected fresh targets; all policy scenarios fictional/generic.']},'paired_text_group':None,'prerequisites':['French B2 Units 01-08 canonical and Unit08 frontier lock PASS'],'difficulty_notes_internal':'B2 policy reasoning: goals, distribution, implementation, counterargument, evaluation and revision.','reader_tags':['unit_role:'+spec['ptype'],'generation_batch','french_b2_u09']}

def checkpoint(groups,details,deck):
 forms=[f for k in ['p01','p02','p03','p04','p05'] for f in groups[k]];review=[base.cur(f,deck) for f in forms];ids={t['form']:t['id'] for t in review}
 g=[groups[f'p0{i}'] for i in range(1,6)]
 text=(
 "Une politique publique devient plus lisible lorsqu’on sépare cinq questions. D’abord, quelles ressources et quels critères permettent de choisir entre des priorités concurrentes ? Les quatre repères « %s », « %s », « %s » et « %s » structurent cette première étape. Ils obligent à dire ce qui sera financé, ce qui ne le sera pas et selon quelle définition de la valeur publique.\n\n" % tuple(g[0])+
 "Ensuite vient la distribution. Une moyenne peut cacher des effets opposés entre groupes. Les termes « %s », « %s », « %s » et « %s » rappellent qu’il faut regarder situation économique, accès réel, soutien et personnes effectivement touchées. Une règle égale sur le papier peut produire des résultats inégaux si certains groupes rencontrent davantage d’obstacles pour utiliser le service.\n\n" % tuple(g[1])+
 "La troisième question concerne la mise en œuvre. Une annonce ne devient pas automatiquement un service réel. Les repères « %s », « %s », « %s » et « %s » servent à décrire l’instrument, son application, l’amélioration recherchée et le point de décision. La quatrième question porte sur le désaccord : « %s », « %s », « %s » et « %s » aident à distinguer bénéfice annoncé, opposition sérieuse, justification et répartition du compromis. Un argument B2 doit répondre au meilleur coût concurrent, pas à une caricature.\n\n" % tuple(g[2]+g[3])+
 "Enfin, l’évaluation doit préciser ce qui ferait continuer, modifier ou arrêter la politique. Les quatre dernières cibles « %s », « %s », « %s » et « %s » organisent efficacité, horizon temporel, estimation et révision. Le but n’est pas d’obtenir une certitude parfaite. Il est d’annoncer des critères assez clairs pour qu’une nouvelle donnée puisse réellement changer la décision. La synthèse relie ainsi budget, distribution, mise en œuvre, contreargument et révision dans une même chaîne de responsabilité publique." % tuple(g[4])
 )
 # Ensure substantive B2 minimum if compact synthesis is short.
 if len(text.split())<350:
  text += " Une recommandation robuste indique également qui supporte le coût d’une erreur et à quel moment le conseil doit revoir son choix. Cette discipline empêche de déplacer silencieusement les critères après les résultats. Elle rend aussi les désaccords plus utiles : deux positions peuvent poursuivre le même objectif tout en préférant des répartitions différentes des coûts, des délais et des risques."
 items=[
 ('main_claim','Quelle chaîne de raisonnement organise la synthèse ?','Ressources et priorités, distribution, mise en œuvre, contreargument, puis évaluation et révision.',[g[0][0],g[4][3]]),
 ('argument_relation','Pourquoi une moyenne est-elle insuffisante pour juger une politique ?','Parce qu’elle peut cacher des effets très différents entre groupes et des obstacles d’accès.',[g[1][0],g[1][1]]),
 ('cross_text_synthesis','Quel lien unit mise en œuvre et évaluation ?','Les conditions d’application déterminent ce qui est réellement produit, puis l’évaluation indique ce qui doit être maintenu ou révisé.',[g[2][1],g[4][3]]),
 ('assumption','Pourquoi faut-il annoncer les critères avant les résultats ?','Pour éviter de déplacer les règles d’évaluation afin de défendre la politique après coup.',[g[0][3],g[4][0]]),
 ('inference','Pourquoi le meilleur contreargument peut-il améliorer une politique ?','Parce qu’il révèle un coût ou une alternative que la proposition initiale doit intégrer.',[g[3][1],g[3][2]]),
 ('reference_resolution','Dans « ils obligent à dire », à quoi renvoie « ils » ?','Aux quatre repères du premier groupe consacrés aux ressources, priorités, coûts et valeur.',g[0]),
 ('stance','Quelle position la synthèse adopte-t-elle envers la certitude parfaite ?','Elle ne l’exige pas; elle demande des critères explicites et révisables proportionnés aux décisions.',[g[4][2],g[4][3]]),
 ('vocabulary_in_context','Pourquoi les vingt cibles sont-elles regroupées par quatre ?','Chaque groupe correspond à une fonction du raisonnement politique : choisir, distribuer, appliquer, débattre et réviser.',g[2]),
 ('synthesis','Comment coût et distribution se rejoignent-ils ?','Une dépense publique doit être jugée non seulement par son total mais par qui reçoit le bénéfice et qui supporte le coût.',[g[0][2],g[1][3]]),
 ('summary','Résume l’unité en une phrase.','Une politique B2 explicite les vingt cibles de budget, distribution, mise en œuvre, contreargument et révision afin de rendre visibles objectifs, coûts, bénéficiaires, contraintes et critères de changement.',forms)
 ]
 q,a=base.qa(items,ids)
 return {'id':'fr-b2-u09-p06','language':'fr','cefr':'B2','unit':9,'sequence':54,'revision':1,'title':'Choisir, distribuer, appliquer, contester, réviser : un cadre B2 pour les arbitrages publics','passage_type':'checkpoint','genre':'B2 cumulative policy checkpoint','domains':['public','professional'],'topics':['public policy and trade-offs','synthesis','evaluation'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':[],'review_lexical_targets':review,'grammar_targets':[{'id':'fr-b2-u09-g-checkpoint','role':'review','description':'synthesize policy criteria, distribution, implementation, counterargument and revision'}],'discourse_targets':[{'id':'fr-b2-u09-d-checkpoint','role':'review','description':'integrate briefing, distributional analysis, implementation, rebuttal and evaluation'}],'questions':q,'answer_key':a,'speed_training':{'timed':True,'benchmark_eligible':True,'comprehension_gate':0.8,'new_word_policy':'none','notes':'French B2 Unit 09 cumulative checkpoint.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Zero-new Unit09 checkpoint using all 20 selected forms exactly.']},'paired_text_group':None,'prerequisites':['French B2 Unit09 P01-P05'],'difficulty_notes_internal':'B2 synthesis of policy goals, distribution, implementation, counterargument and revision.','reader_tags':['unit_role:checkpoint','generation_batch','french_b2_u09']}

def main():
 for lab,p in [('A1',A1),('A2',A2),('B1',B1)]:
  got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
  if got!=EXPECTED_STABLE[lab]:raise AssertionError(f'{lab} blob drift: {got}')
 lock,groups,details,review_groups=load_state();b2blob=lock['canonical_blob'];rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=48 or rows[-1]['id']!='fr-b2-u08-p06':raise AssertionError('unexpected B2 Unit08 frontier')
 deck=base.deck();prior=base.prior([json.loads(x) for p in (A1,A2,B1,CANON) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]);pid={t.get('id') for r in prior for t in []} # placeholder, rebuilt below
 allrows=[]
 for p in (A1,A2,B1,CANON):allrows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 pid={t.get('id') for r in allrows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};pf={t.get('form') for r in allrows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};prior=base.prior(allrows)
 unit=[]
 for spec in specs(groups,details,review_groups):
  forms=groups[spec['prefix']];unit.append(make(spec,forms,spec['reviews'],details,prior,deck))
 unit.append(checkpoint(groups,details,deck));V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')));selected={x['form'] for x in json.loads(SELECT.read_text(encoding='utf-8'))['selected']};newids=[];newforms=[]
 if [r['sequence'] for r in unit]!=list(range(49,55)) or [r['id'] for r in unit]!=[f'fr-b2-u09-p{i:02d}' for i in range(1,7)]:raise AssertionError('Unit09 sequence/id failure')
 for r in unit:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:8]]}")
  if not 350<=r['word_count']<=550:raise AssertionError(f"{r['id']}: word band {r['word_count']}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: assessment count")
  if r['sequence']<=53 and len(r['new_lexical_targets'])!=4:raise AssertionError(f"{r['id']}: expected four new")
  if r['sequence']==54 and r['new_lexical_targets']:raise AssertionError('P06 must have zero new')
  local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(tid not in local for tid in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage failure")
  for t in r['new_lexical_targets']:
   src=deck.get(t['form'])
   if t['id'] in pid or t['form'] in pf or not src or t['source_rank']!=src['rank'] or t['id']!=base.tid(src['rank']) or base.cnt(r['text'],t['form'])!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: new target drift {t}")
   newids.append(t['id']);newforms.append(t['form'])
  for t in r['review_lexical_targets']:
   if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
 if len(newids)!=20 or len(set(newids))!=20 or len(set(newforms))!=20 or set(newforms)!=selected:raise AssertionError('Unit09 selection/uniqueness failure')
 CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows+unit),encoding='utf-8')
 print(json.dumps({'status':'PASS','unit':9,'source_blob':b2blob,'b2_passages':54,'questions':60,'answers':60,'new_targets':20,'groups':groups,'word_counts':{r['id']:r['word_count'] for r in unit}},ensure_ascii=False))
if __name__=='__main__':main()
