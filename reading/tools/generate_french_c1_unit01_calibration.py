#!/usr/bin/env python3
"""Generate French C1 Unit01 calibration (seq1-6) from canonical plan artifacts.

This is intentionally plan-adaptive: the resolved topic/genre matrix supplies the
Unit01 theme/genres and the readiness artifact supplies the exact C1 word band.
Four fresh targets per P01-P05 are a calibration candidate only; P06 is zero-new.
P02/P03 form a paired viewpoint set. Full post-calibration review is required
before any C1 production default is accepted.
"""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2]
A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json'
B2AUD=R/'reading/audit/french_b2_generation_integrity.json';READY=R/'reading/audit/french_c1_readiness.json';PLAN=R/'reading/audit/french_c1_unit01_plan.json';PROBE=R/'reading/audit/french_c1_unit01_target_probe.json';SELECT=R/'reading/audit/french_c1_unit01_target_selection.json'
EXPECTED_STABLE={'A1':'0493a2fa13e51b5997db05e91cdea4d8dc5e647b','A2':'d0a80b8866071f426019aa0ad143e1d270dba4de','B1':'4a2cd9ff30c3cea58caf20fca2822b06200622ca'}
PAIR='fr-c1-u01-action-under-uncertainty-viewpoints'
USE={
'conclusion':'La conclusion reste explicitement proportionnée aux éléments qui la soutiennent et ne prétend pas clore les questions encore ouvertes.',
'hypothèse':'Une hypothèse utile précise le mécanisme attendu ainsi que l’observation qui pourrait la fragiliser.',
'affirmation':'Toute affirmation importante est séparée de l’exemple qui l’illustre et de la preuve qui pourrait réellement la soutenir.',
'préciser':'L’auteur doit préciser la portée de son propos avant d’en tirer une recommandation générale.',
'démontrer':'Démontrer exige davantage qu’une succession d’exemples concordants : il faut relier les observations à un raisonnement contrôlable.',
'constater':'Constater une différence ne suffit pas à expliquer pourquoi elle apparaît ni à décider comment agir.',
'établir':'Établir un résultat demande de distinguer ce qui est directement observé de ce qui dépend d’une interprétation.',
'question':'La question centrale est formulée de manière assez précise pour que plusieurs réponses puissent être comparées.',
'néanmoins':'Néanmoins, une objection sérieuse demeure si le mécanisme proposé n’explique pas les cas qui s’écartent de la tendance.',
'toutefois':'Toutefois, la prudence ne doit pas devenir un prétexte pour repousser indéfiniment toute décision révisable.',
'pourtant':'Pourtant, deux lecteurs peuvent accepter les mêmes données et diverger sur le seuil à partir duquel une action devient justifiée.',
'cependant':'Cependant, le désaccord change de nature lorsque l’on sépare les faits, les définitions et les valeurs en jeu.',
'malgré':'Malgré la convergence de plusieurs indices, la portée de la conclusion reste limitée par la qualité des mesures.',
'contraire':'L’hypothèse contraire mérite d’être formulée dans sa version la plus forte afin de tester réellement l’argument préféré.',
'différent':'Un résultat différent dans un cas comparable peut révéler une condition que l’analyse initiale avait négligée.',
'nuance':'La nuance ne consiste pas à hésiter entre toutes les positions, mais à ajuster la force d’une conclusion à la preuve disponible.',
'méthode':'La méthode décrit non seulement ce qui a été mesuré, mais aussi les choix qui ont déterminé ce qui pouvait devenir visible.',
'analyse':'L’analyse distingue les observations, les mécanismes proposés et les conséquences normatives que l’auteur veut en tirer.',
'donnée':'Une donnée isolée acquiert du sens lorsqu’on connaît son origine, son unité de mesure et les cas qu’elle ne représente pas.',
'élément':'Chaque élément du dossier reçoit une fonction précise au lieu d’être ajouté comme confirmation générale.',
'indice':'Un indice peut orienter l’enquête sans posséder, à lui seul, la force nécessaire pour conclure.',
'observer':'Observer une régularité permet de formuler une piste, mais pas d’ignorer les explications concurrentes.',
'comparer':'Comparer devient utile lorsque les cas diffèrent sur un facteur pertinent et restent suffisamment proches sur les autres dimensions.',
'interpréter':'Interpréter exige de montrer pourquoi une lecture rend mieux compte du texte ou des données qu’une lecture concurrente.',
'contexte':'Le contexte modifie la signification pratique d’un résultat sans constituer automatiquement une cause.',
'condition':'Une condition de validité indique le cadre dans lequel l’argument peut raisonnablement être transféré.',
'limite':'La limite principale est annoncée avant la recommandation afin que le lecteur puisse juger sa portée réelle.',
'exception':'Une exception bien expliquée peut révéler une variable cachée plutôt que simplement affaiblir la règle.',
'considérer':'Il faut considérer les effets sur les groupes moins visibles avant de transformer une moyenne en décision générale.',
'dépendre':'La réponse peut dépendre du seuil choisi, de l’horizon temporel ou de la manière dont le problème est défini.',
'relation':'La relation entre deux phénomènes est décrite séparément du mécanisme causal que l’auteur propose ensuite.',
'ensemble':'L’ensemble des sources doit être lu comme un système de contraintes mutuelles, et non comme une pile d’arguments allant tous dans le même sens.',
'conséquence':'Une conséquence prévisible n’a pas le même poids moral ou politique selon qu’elle est réversible ou durable.',
'implication':'L’implication pratique d’un résultat doit être distinguée de sa signification statistique ou descriptive.',
'décision':'Une décision défendable indique ce qu’elle cherche à obtenir, le coût qu’elle accepte et les conditions de révision.',
'juger':'Juger la qualité d’une proposition suppose de rendre explicites les critères utilisés plutôt que de s’en remettre à une impression globale.',
'évaluer':'Évaluer demande de fixer les indicateurs avant de savoir quelle option ils favoriseront.',
'modifier':'Modifier une conclusion après une nouvelle preuve est présenté comme une exigence de rigueur, non comme une faiblesse.',
'adapter':'Adapter la méthode à un nouveau domaine signifie conserver sa logique tout en changeant les sources, les contraintes et les indicateurs.',
'perspective':'Une perspective révèle certains aspects du problème tout en laissant d’autres dimensions moins visibles.'
}

def txt(v):
 if isinstance(v,str):return v
 if isinstance(v,list):return ' / '.join(str(x) for x in v)
 if isinstance(v,dict):
  for k in ('theme','title','topic','name'):
   if k in v:return str(v[k])
  return json.dumps(v,ensure_ascii=False,sort_keys=True)
 return str(v)
def genre_list(v):
 if isinstance(v,list):return [str(x) for x in v if str(x).strip()]
 if isinstance(v,str):
  parts=[x.strip() for x in re.split(r'[/;,|]',v) if x.strip()];return parts or [v]
 if isinstance(v,dict):return [str(x) for x in v.values() if isinstance(x,(str,int,float))]
 return []
def load_state():
 audit=json.loads(B2AUD.read_text(encoding='utf-8'));ready=json.loads(READY.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));sel=json.loads(SELECT.read_text(encoding='utf-8'));b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if audit.get('status')!='PASS' or audit.get('canonical_blob')!=b2blob or audit.get('passages')!=60:raise AssertionError('C1 generator requires sealed live B2')
 for name,obj in [('ready',ready),('plan',plan),('probe',probe),('selection',sel)]:
  if obj.get('status')!='PASS' or obj.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'C1 {name} prerequisite missing/stale')
 if sel.get('calibration_new_targets_per_standard_passage')!=4 or sel.get('selected_count')!=20:raise AssertionError('unexpected C1 calibration lexical load')
 groups=sel['passage_groups'];details={(x['passage'],x['slot']):x for x in sel['selected']}
 if any(len(groups.get(f'p0{i}',[]))!=4 for i in range(1,6)) or len(details)!=20:raise AssertionError('C1 selection structure drift')
 return audit,ready,plan,probe,sel,groups,details

def lexical(form,detail):
 if form in USE:return USE[form]
 return f"Dans ce passage, le mot « {form} » prend une fonction précise dans le raisonnement; le contexte permet d’en déterminer la portée sans lui attribuer artificiellement une valeur de preuve."
def review_bridge(forms):
 return f"Pour maintenir la continuité avec la synthèse B2, l’auteur réemploie aussi « {forms[0]} », « {forms[1]} », « {forms[2]} » et « {forms[3]} » comme quatre points d’appui dont la fonction doit rester explicite dans l’argument."
def fit(paras,lo,hi,extras):
 p=list(paras);text='\n\n'.join(p);i=0
 while len(text.split())<lo and i<len(extras):
  p[-1]+=' '+extras[i];i+=1;text='\n\n'.join(p)
 if len(text.split())<lo:raise AssertionError(f'C1 draft below word minimum after substantive expansion: {len(text.split())} < {lo}')
 if len(text.split())>hi:raise AssertionError(f'C1 draft above word maximum: {len(text.split())} > {hi}')
 return p,text

def plans(theme,genres):
 g=(genres+['analytical essay','paired commentary','critical synthesis','source critique','integrated position paper'])[:5]
 return [
 {'id':'fr-c1-u01-p01','sequence':1,'ptype':'instructional','genre':g[0],'title':f'Définir le désaccord avant de défendre une position — {theme}','prefix':'p01','pair':None,'paras':[
 f"Un dossier de niveau C1 consacré à « {theme} » ne devient pas complexe parce qu’il contient beaucoup d’informations, mais parce que plusieurs types de désaccord peuvent y être confondus. Deux auteurs peuvent diverger sur les faits disponibles, sur la définition d’un concept, sur le mécanisme qui relie deux phénomènes ou sur la valeur qu’ils accordent à un résultat. Tant que ces plans restent mélangés, chaque réponse semble contredire l’autre alors qu’elles ne répondent parfois pas à la même question. Le premier travail consiste donc à reconstruire l’architecture du désaccord avant de choisir une position.",
 "L’analyste commence par isoler les affirmations descriptives. Il demande ce qui est directement observé, ce qui dépend d’une catégorie construite et ce qui repose sur une comparaison. Une statistique peut être exacte tout en mesurant un phénomène différent de celui que le débat public croit discuter. Inversement, un témoignage peut décrire une expérience importante sans permettre une estimation générale. La difficulté C1 consiste à attribuer à chaque élément une portée précise et à empêcher qu’un type de preuve soit utilisé pour répondre à une question qu’il ne peut pas trancher.",
 "Le deuxième niveau concerne les mécanismes. Même lorsque deux parties acceptent les mêmes observations, elles peuvent expliquer différemment la relation entre elles. L’une invoque une cause directe; l’autre une chaîne de conditions. Pour comparer ces lectures, il faut chercher non seulement les cas qui confirment chaque proposition, mais les observations qui les distingueraient. Un argument gagne en précision lorsqu’il annonce le type de contre-exemple qui obligerait à le modifier.",
 "Enfin viennent les valeurs et les seuils de décision. Un même résultat peut sembler suffisant à une personne qui privilégie la réversibilité et insuffisant à une autre qui redoute un dommage rare mais durable. Ce désaccord n’est pas nécessairement une erreur factuelle. Le texte doit donc montrer le passage entre preuve et recommandation : quel critère normatif intervient, qui supporte le risque et pourquoi le seuil choisi est jugé acceptable. Une position C1 devient ainsi plus forte lorsqu’elle révèle ses conditions de validité au lieu de masquer ses choix derrière un vocabulaire technique."
 ],'extras':[
 "Cette décomposition permet aussi de repérer les faux désaccords : deux textes peuvent employer des mots différents pour une distinction identique, ou le même mot pour des concepts incompatibles.",
 "L’analyse gagne alors en économie argumentative, car elle réserve la réfutation aux points qui changent réellement la conclusion.",
 "Elle évite surtout qu’une objection pertinente sur la définition soit rejetée comme si elle niait les données elles-mêmes.",
 "Le lecteur peut ainsi reconstruire la chaîne complète : observation, interprétation, critère, puis recommandation."
 ]},
 {'id':'fr-c1-u01-p02','sequence':2,'ptype':'reinforcement','genre':g[1],'title':f'Point de vue A : agir tôt lorsque l’expérience reste réversible — {theme}','prefix':'p02','pair':PAIR,'paras':[
 f"Dans un débat fictif lié à « {theme} », Léa défend une stratégie d’action précoce. Elle part d’un constat : attendre l’accord complet entre experts peut avoir lui aussi un coût, surtout lorsque la décision peut être testée à petite échelle puis corrigée. Son argument ne consiste pas à minimiser l’incertitude. Il consiste à distinguer les décisions irréversibles, qui exigent une preuve plus forte, des expériences limitées dont l’objectif principal est précisément de produire l’information qui manque.",
 "Léa propose donc un pilote avec des seuils annoncés avant le lancement. Les critères incluent le résultat recherché, les effets sur des groupes différents, le coût de mise en œuvre et les signaux qui imposeraient un arrêt. Une telle architecture évite que le projet soit déclaré réussi simplement parce qu’il a commencé. Elle transforme l’incertitude en question opérationnelle : quelles observations futures feraient continuer, modifier ou abandonner l’action ?",
 "Son raisonnement reconnaît toutefois un danger. Un pilote peut créer des attentes, déplacer des ressources ou modifier le comportement des acteurs avant même qu’une décision définitive soit prise. Il n’est donc jamais totalement neutre. Léa répond que ces effets doivent entrer dans l’évaluation du caractère réversible. Un essai acceptable n’est pas celui que l’on peut annuler juridiquement, mais celui dont les principaux coûts peuvent être contenus si l’hypothèse initiale se révèle mauvaise.",
 "Cette position privilégie enfin l’apprentissage institutionnel. Pour Léa, une organisation devient plus rationnelle lorsqu’elle sait concevoir des décisions qui produisent simultanément un résultat et une information sur ce résultat. La prudence n’est alors ni l’inaction ni la vitesse. Elle correspond à un rapport proportionné entre l’incertitude, l’ampleur de l’engagement et la qualité du mécanisme de révision."
 ],'extras':[
 "Elle insiste également sur la publication du protocole avant les résultats, afin que les critères ne puissent pas être déplacés silencieusement lorsque les premières données apparaissent.",
 "Les acteurs opposés au pilote doivent pouvoir contester les mesures choisies et proposer des indicateurs alternatifs avant que l’essai ne commence.",
 "Cette ouverture transforme le désaccord en test concurrent plutôt qu’en simple affrontement de préférences.",
 "La décision finale reste ainsi liée à une trace argumentative que des lecteurs extérieurs peuvent reconstruire."
 ]},
 {'id':'fr-c1-u01-p03','sequence':3,'ptype':'interleaved','genre':g[2],'title':f'Point de vue B : certains pilotes créent précisément les conditions qui rendent leur évaluation trompeuse — {theme}','prefix':'p03','pair':PAIR,'paras':[
 f"Dans le même débat sur « {theme} », Malik accepte qu’une action limitée puisse produire une information utile, mais il conteste l’idée que la réversibilité soit facile à reconnaître. Certaines interventions changent les attentes, les investissements ou la composition des participants. Le résultat observé pendant le pilote peut alors dépendre du caractère provisoire de l’expérience et ne pas prévoir ce qui se passerait si la mesure devenait permanente. Une expérience apparemment prudente peut donc créer le contexte qui rend sa propre extrapolation fragile.",
 "Malik donne un exemple abstrait. Si seuls les acteurs les plus motivés participent au début, une forte satisfaction ne permet pas d’anticiper l’adoption générale. Si les organisations savent que le financement est temporaire, elles peuvent reporter des investissements qui deviendraient rationnels dans un programme stable. Le pilote ne mesure donc pas simplement l’effet d’une politique plus petite; il mesure une configuration institutionnelle différente. Cette distinction doit être analysée avant de transférer les résultats.",
 "Il formule aussi une objection distributive. Les coûts d’apprentissage ne tombent pas toujours sur les mêmes personnes que les bénéfices futurs. Un groupe peut supporter les erreurs du test tandis qu’un autre profite de la politique améliorée. Malik demande que cette asymétrie entre dans la justification du pilote et pas seulement dans son évaluation finale. Sans cette étape, le langage de l’expérimentation risque de présenter comme technique une décision qui contient déjà un choix sur la répartition du risque.",
 "Sa conclusion reste néanmoins compatible avec certaines expériences. Il accepte un pilote lorsque ses effets de contexte sont explicitement modélisés, lorsque les groupes exposés peuvent influencer les critères et lorsque l’analyste explique ce qui ne pourra pas être extrapolé. Sa position ne réfute donc pas l’apprentissage par l’action; elle déplace la charge de preuve vers la validité du transfert entre l’essai et la décision durable."
 ],'extras':[
 "Cette exigence oblige aussi à distinguer validité interne et pertinence externe : un effet bien mesuré dans l’essai peut rester peu informatif pour un système plus large.",
 "L’incertitude porte alors moins sur le chiffre observé que sur la relation entre deux contextes institutionnels.",
 "Un rapport C1 devrait présenter cette différence avant de proposer une généralisation, et non dans une note marginale après la recommandation.",
 "Le désaccord avec Léa devient ainsi testable : les deux positions ne divergent pas sur la valeur de l’apprentissage, mais sur les conditions qui rendent cet apprentissage transférable."
 ]},
 {'id':'fr-c1-u01-p04','sequence':4,'ptype':'transfer','genre':g[3],'title':f'Lire trois sources qui ne parlent pas depuis le même endroit — {theme}','prefix':'p04','pair':None,'paras':[
 f"Un second dossier consacré à « {theme} » réunit trois sources : un rapport institutionnel, une étude de terrain et une série d’entretiens. Une lecture superficielle cherche immédiatement laquelle est la plus fiable. Une lecture C1 pose une question différente : quel type d’affirmation chaque source est-elle en mesure de soutenir, compte tenu de sa méthode, de son objectif et de ce qu’elle laisse hors champ ? Le rapport peut disposer d’une couverture large tout en utilisant des catégories administratives; l’étude peut contrôler davantage ses mesures mais porter sur peu de cas; les entretiens peuvent révéler des mécanismes invisibles dans les tableaux sans fournir une fréquence générale.",
 "L’analyste construit d’abord une carte des affirmations. Certaines concernent la distribution d’un phénomène, d’autres son mécanisme, d’autres encore la manière dont les personnes comprennent une décision. Il serait incohérent de demander aux entretiens de fournir seuls une proportion représentative, mais tout aussi incohérent de rejeter leur description d’un processus simplement parce qu’elle n’est pas statistique. L’intégration commence lorsque la fonction de chaque source est explicitée.",
 "Le travail suivant porte sur les contradictions. Si le rapport indique une amélioration moyenne alors que plusieurs entretiens décrivent une détérioration, les deux résultats peuvent être compatibles : la moyenne peut cacher des sous-groupes. Mais cette compatibilité n’est pas automatique. Il faut chercher les catégories, les périodes et les lieux qui permettraient de vérifier l’hypothèse. La contradiction devient ainsi une invitation à formuler une comparaison plus précise plutôt qu’un prétexte pour choisir la source préférée.",
 "La synthèse finale hiérarchise les conclusions. Certaines sont solidement établies par plusieurs méthodes; d’autres restent plausibles mais dépendent d’un mécanisme qui n’a pas été observé directement. D’autres encore concernent une expérience minoritaire dont l’importance normative peut être élevée même si sa fréquence est faible. Le texte C1 doit être capable de maintenir ces statuts différents dans la même argumentation sans les réduire à une note unique de fiabilité."
 ],'extras':[
 "Cette hiérarchie protège également contre une erreur fréquente : confondre abondance documentaire et indépendance des preuves lorsque plusieurs sources reprennent en réalité la même donnée initiale.",
 "L’origine de l’information doit donc être retracée avant de compter le nombre apparent de confirmations.",
 "Une source secondaire peut apporter une interprétation nouvelle sans constituer une observation indépendante du fait qu’elle commente.",
 "Cette distinction renforce la synthèse en séparant diversité des voix et diversité des bases empiriques."
 ]},
 {'id':'fr-c1-u01-p05','sequence':5,'ptype':'integration','genre':g[4],'title':f'De la preuve à l’action : écrire une recommandation qui peut survivre à une objection sérieuse — {theme}','prefix':'p05','pair':None,'paras':[
 f"La dernière lecture standard de l’unité revient à « {theme} » pour transformer une analyse en recommandation. Cette étape est souvent la plus fragile : un texte peut décrire soigneusement les données puis sauter brusquement vers une solution. La recommandation C1 doit au contraire exposer la norme qui relie les deux. Quel résultat compte comme amélioration ? Quel niveau de risque est acceptable ? Qui supporte les coûts ? Quelles conséquences seraient suffisamment graves pour justifier une option plus prudente ?",
 "L’auteur formule d’abord deux options concurrentes dans leur meilleure version. Il ne suffit pas de présenter l’une comme ambitieuse et l’autre comme passive. Chaque option reçoit un objectif, un mécanisme, des ressources nécessaires et un risque d’échec. Le texte identifie ensuite le point où les valeurs interviennent. Deux lecteurs peuvent accepter les mêmes prévisions et préférer des options différentes parce qu’ils évaluent autrement la réversibilité, l’équité ou la distribution temporelle des bénéfices.",
 "Une objection forte est alors intégrée au raisonnement. Si elle révèle un coût que la recommandation initiale ignorait, le texte doit changer : réduction de portée, condition supplémentaire, période d’essai ou mécanisme de compensation. Répondre ne signifie pas répéter la conclusion après avoir mentionné l’objection. La qualité du raisonnement se mesure au fait que l’alternative concurrente laisse une trace visible dans la proposition finale.",
 "La recommandation se termine par une règle de révision. Elle précise les informations futures qui pourraient déplacer le choix vers l’autre option et les indicateurs qui doivent être suivis. Cette ouverture n’affaiblit pas la position. Elle montre que l’auteur distingue conviction et irréversibilité argumentative. Une conclusion suffisamment forte pour guider l’action peut rester suffisamment ouverte pour changer lorsque le monde ne se comporte pas comme le modèle l’anticipait."
 ],'extras':[
 "Le texte précise aussi l’horizon temporel : une option peut être préférable à court terme et moins défendable lorsque les effets cumulés deviennent visibles.",
 "Il sépare les coûts certains des risques probabilistes afin d’éviter de les additionner comme s’ils avaient le même statut.",
 "Lorsque les valeurs restent réellement incompatibles, l’auteur le reconnaît au lieu de simuler un consensus que les preuves ne peuvent pas produire.",
 "La recommandation devient ainsi un jugement argumenté dont les prémisses empiriques et normatives peuvent être discutées séparément."
 ]}
 ]

def core_items(seq,theme):
 data={
 1:[('main_claim','Quelle est la tâche centrale du premier texte ?','Décomposer le désaccord en faits, définitions, mécanismes et valeurs avant de choisir une position.'),('argument_relation','Pourquoi une statistique exacte peut-elle rester insuffisante ?','Parce qu’elle peut mesurer une catégorie différente de celle que le débat cherche réellement à trancher.'),('assumption','Pourquoi faut-il formuler des observations qui distingueraient deux mécanismes ?','Parce qu’une explication n’est informative que si elle peut être comparée à une lecture concurrente.'),('inference','Que révèle un désaccord sur le seuil de décision ?','Qu’une divergence peut venir de valeurs ou de tolérance au risque plutôt que d’une erreur sur les faits.'),('stance','Quelle conception de la nuance le texte défend-il ?','Une adaptation précise de la force et de la portée de la conclusion, pas une hésitation générale.'),('summary',f'Résume la méthode appliquée à « {theme} ».','Le texte sépare les plans du désaccord, attribue une portée à chaque preuve, compare les mécanismes et rend visibles les critères normatifs qui mènent à la recommandation.')],
 2:[('main_claim','Quelle thèse Léa défend-elle ?','Une action limitée et révisable peut être rationnelle lorsque l’attente a elle-même un coût et que le pilote produit l’information manquante.'),('argument_relation','Pourquoi le protocole doit-il être publié avant les résultats ?','Pour empêcher que les critères de réussite soient déplacés afin de protéger le projet.'),('assumption','Que suppose l’idée de réversibilité ?','Que les principaux coûts d’une erreur peuvent être contenus ou corrigés si l’hypothèse se révèle mauvaise.'),('inference','Pourquoi un pilote n’est-il jamais totalement neutre ?','Parce qu’il peut modifier les attentes, les ressources et les comportements avant la décision définitive.'),('stance','Comment Léa définit-elle la prudence ?','Comme une proportion entre incertitude, ampleur de l’engagement et qualité du mécanisme de révision.'),('summary','Résume le point de vue A.','Léa accepte l’incertitude lorsqu’une action limitée possède des critères préalables, des coûts contenus et une règle de révision qui transforme l’expérience en apprentissage institutionnel.')],
 3:[('main_claim','Quelle objection principale Malik adresse-t-il au point de vue A ?','Un pilote peut créer un contexte provisoire si différent du système durable que ses résultats deviennent difficiles à transférer.'),('argument_relation','Pourquoi une forte satisfaction initiale peut-elle tromper ?','Parce que les premiers participants peuvent être atypiquement motivés et ne pas représenter l’adoption générale.'),('assumption','Pourquoi les coûts d’apprentissage posent-ils une question normative ?','Parce qu’ils peuvent être supportés par des groupes différents de ceux qui recevront les bénéfices futurs.'),('inference','Dans quel cas Malik accepterait-il un pilote ?','Lorsque les effets de contexte sont modélisés, les groupes exposés influencent les critères et les limites d’extrapolation sont explicites.'),('cross_text_synthesis','Sur quoi Léa et Malik s’accordent-ils malgré leur désaccord ?','Sur la valeur potentielle de l’apprentissage par l’action; ils divergent surtout sur les conditions qui rendent cet apprentissage transférable.'),('summary','Résume le point de vue B.','Malik accepte certains essais mais exige une analyse de la validité externe, de la répartition des risques et de la différence entre contexte provisoire et politique durable.')],
 4:[('main_claim','Pourquoi le texte refuse-t-il de classer globalement les trois sources par fiabilité ?','Parce qu’elles soutiennent des types d’affirmations différents selon leur méthode, leur objectif et leur champ d’observation.'),('argument_relation','Comment une moyenne positive et des témoignages négatifs peuvent-ils être compatibles ?','La moyenne peut cacher des sous-groupes; cette hypothèse doit ensuite être testée par catégories, périodes ou lieux.'),('assumption','Pourquoi faut-il retracer l’origine de l’information ?','Pour ne pas compter plusieurs reprises d’une même donnée comme des confirmations indépendantes.'),('inference','Quelle valeur peuvent avoir des témoignages peu représentatifs ?','Ils peuvent révéler un mécanisme ou une expérience normativement importante sans estimer sa fréquence générale.'),('stance','Quelle conception de la synthèse le passage défend-il ?','Une hiérarchie de conclusions aux statuts différents plutôt qu’une note unique de fiabilité.'),('summary','Résume la méthode d’intégration des sources.','Attribuer une fonction à chaque source, transformer les contradictions en hypothèses testables, vérifier l’indépendance des preuves et maintenir plusieurs degrés de conclusion.')],
 5:[('main_claim','Que doit ajouter une recommandation C1 à une bonne analyse descriptive ?','Une norme explicite reliant preuves, objectifs, risques, coûts et critères de décision.'),('argument_relation','Pourquoi l’objection doit-elle laisser une trace dans la proposition finale ?','Parce qu’une réponse authentique modifie la portée, les conditions ou le mécanisme lorsque l’objection révèle un coût réel.'),('assumption','Pourquoi deux lecteurs peuvent-ils choisir différemment avec les mêmes prévisions ?','Parce qu’ils peuvent accorder des poids différents à la réversibilité, l’équité ou la distribution temporelle des bénéfices.'),('inference','Pourquoi une règle de révision renforce-t-elle plutôt qu’elle n’affaiblit la recommandation ?','Elle montre que la conclusion dépend de preuves et critères explicites et peut changer si ces prémisses changent.'),('stance','Quelle position le texte adopte-t-il envers un consensus artificiel ?','Il préfère reconnaître une incompatibilité de valeurs plutôt que prétendre que les preuves la résolvent.'),('summary','Résume la transition de la preuve à l’action.','Comparer les meilleures options, rendre visibles les critères normatifs, intégrer le meilleur contreargument puis annoncer les conditions futures de révision.')]
 }
 return data[seq]

def make(spec,forms,review_forms,details,prior,deck,lo,hi,theme):
 paras=list(spec['paras']);lex=' '.join(lexical(f,details[(spec['sequence'],i+1)]) for i,f in enumerate(forms));paras[1]+=' '+lex;paras[2]+=' '+review_bridge(review_forms);paras,text=fit(paras,lo,hi,spec['extras']);new=[base.nt(f,text,deck) for f in forms];reviews=[base.rev(f,prior) for f in review_forms];ids={t['form']:t['id'] for t in new+reviews};raw=core_items(spec['sequence'],theme);items=[]
 for i,(typ,p,a) in enumerate(raw):
  tags=[]
  if i==0:tags=[forms[0],forms[1]]
  elif i==1:tags=[forms[2]]
  elif i==2:tags=[forms[3]]
  elif i==3:tags=[review_forms[0]]
  elif i==4:tags=[review_forms[1]]
  elif i==5:tags=forms+review_forms
  items.append((typ,p,a,tags))
 # Four explicit vocabulary questions bring the total to 10.
 for i,f in enumerate(forms):items.append(('vocabulary_in_context',f'Quelle fonction « {f} » remplit-il dans le raisonnement ?',f'Il sert à préciser une composante de l’argument dont la portée est définie par le contexte du passage.',[f]))
 q,a=base.qa(items,ids)
 return {'id':spec['id'],'language':'fr','cefr':'C1','unit':1,'sequence':spec['sequence'],'revision':1,'title':spec['title'],'passage_type':spec['ptype'],'genre':spec['genre'],'domains':['educational','public'],'topics':[theme,'C1 calibration','critical reasoning'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':[{'id':f"fr-c1-u01-g-{spec['sequence']}",'role':'new','description':'scope claims through concession, qualification, counterfactual conditions and explicit revision criteria'}],'discourse_targets':[{'id':f"fr-c1-u01-d-{spec['sequence']}",'role':'new','description':'separate evidence, mechanism, normative criterion and recommendation while preserving competing viewpoints'}],'questions':q,'answer_key':a,'speed_training':{'timed':False,'benchmark_eligible':False,'comprehension_gate':0.8,'new_word_policy':'controlled','notes':'French C1 Unit01 calibration.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['French C1 Unit01 calibration generated from canonical plan/readiness artifacts.','Four fresh targets are a calibration candidate only, not yet the C1 production default.']},'paired_text_group':spec['pair'],'prerequisites':['French B2 generation-integrity PASS','French C1 Unit01 plan/readiness PASS'],'difficulty_notes_internal':'C1 calibration: implicit assumptions, source role, concession, scope, normative bridge, paired viewpoints, transfer and revision.','reader_tags':['unit_role:'+spec['ptype'],'generation_batch','french_c1_u01_calibration']}

def checkpoint(groups,deck,lo,hi,theme,genre):
 forms=[f for k in ['p01','p02','p03','p04','p05'] for f in groups[k]];reviews=[base.cur(f,deck) for f in forms];ids={t['form']:t['id'] for t in reviews};g=[groups[f'p0{i}'] for i in range(1,6)]
 paras=[
 f"Le checkpoint revient au thème « {theme} » sans introduire de nouveau lexique délibéré. La première exigence C1 consiste à reconstruire l’architecture d’un désaccord avant de choisir une conclusion. Les quatre repères « {g[0][0]} », « {g[0][1]} », « {g[0][2]} » et « {g[0][3]} » rappellent qu’une position doit distinguer ce qu’elle affirme, ce qui la soutient, sa portée et les conditions dans lesquelles elle pourrait être révisée. Cette discipline empêche une formulation très assurée de masquer une base empirique étroite.",
 f"La deuxième exigence est dialogique. Les repères « {g[1][0]} », « {g[1][1]} », « {g[1][2]} » et « {g[1][3]} » servent à traiter une position concurrente sans la caricaturer. Une concession n’oblige pas à adopter l’argument opposé; elle oblige à reconnaître ce qu’il explique correctement. La réponse gagne alors en précision parce qu’elle porte sur le meilleur désaccord réel plutôt que sur une version facile à réfuter.",
 f"La troisième exigence concerne les sources. « {g[2][0]} », « {g[2][1]} », « {g[2][2]} » et « {g[2][3]} » organisent l’attention portée à la méthode, aux données, aux comparaisons et à l’interprétation. Deux sources peuvent être compatibles sans être indépendantes; elles peuvent aussi sembler contradictoires parce qu’elles mesurent des groupes ou des périodes différents. Le lecteur doit donc reconstruire la fonction de chaque preuve avant de les synthétiser.",
 f"La quatrième exigence concerne la portée. Les termes « {g[3][0]} », « {g[3][1]} », « {g[3][2]} » et « {g[3][3]} » rappellent qu’une conclusion dépend d’un contexte, de conditions et de limites qui déterminent son transfert. Une exception pertinente peut révéler une variable ignorée plutôt que détruire toute régularité. La nuance C1 consiste à modifier exactement ce qui doit l’être et à conserver ce qui reste soutenu.",
 f"Enfin, « {g[4][0]} », « {g[4][1]} », « {g[4][2]} » et « {g[4][3]} » relient l’analyse à la décision. Une recommandation sérieuse expose les conséquences, les valeurs, les critères d’évaluation et les informations qui pourraient conduire à une modification. Elle peut guider l’action sans prétendre à l’irréversibilité. La maîtrise C1 apparaît lorsque l’auteur sait maintenir simultanément une position identifiable, un degré de certitude proportionné et une ouverture réelle à la preuve contraire."
 ];extras=[
 "Cette structure permet aussi de distinguer désaccord empirique et désaccord normatif, ce qui évite de demander aux données de résoudre seules une question de valeurs.",
 "Elle invite le lecteur à suivre la chaîne complète entre observation, interprétation, principe de décision et conséquence pratique.",
 "Lorsque plusieurs conclusions restent possibles, le texte doit expliquer quelle information supplémentaire aurait le plus de valeur pour les départager.",
 "Le checkpoint évalue ainsi moins la quantité d’informations retenues que la capacité à organiser leur statut dans une argumentation révisable."
 ];paras,text=fit(paras,lo,hi,extras)
 items=[
 ('main_claim','Quelles sont les cinq exigences que le checkpoint synthétise ?','Architecture du désaccord, réponse à une position concurrente, fonction des sources, portée/conditions et passage de l’analyse à la décision.',[g[0][0],g[4][3]]),
 ('argument_relation','Pourquoi une concession ne signifie-t-elle pas adopter la position adverse ?','Parce qu’elle reconnaît seulement la partie que l’argument concurrent explique correctement avant de préciser le désaccord restant.',[g[1][0],g[1][2]]),
 ('cross_text_synthesis','Quel point commun relie la paire Léa–Malik et la critique des sources ?','Dans les deux cas, la question centrale porte sur les conditions qui rendent un résultat transférable au-delà de son contexte immédiat.',[g[1][3],g[3][0]]),
 ('assumption','Pourquoi une exception peut-elle renforcer l’analyse ?','Parce qu’elle peut révéler une condition ou variable cachée et permettre de réduire précisément la portée de la règle.',[g[3][1],g[3][2]]),
 ('inference','Que montre une règle explicite de révision ?','Que la conclusion dépend de critères et de preuves identifiables plutôt que de la défense d’une position initiale.',[g[4][1],g[4][3]]),
 ('reference_resolution','Dans « elles peuvent aussi sembler contradictoires », à quoi renvoie « elles » ?','Aux différentes sources comparées dans l’analyse.',[g[2][0]]),
 ('stance','Quelle conception de la maîtrise C1 le passage défend-il ?','Une position identifiable mais qualifiée, capable de répondre au meilleur contreargument et de changer lorsque les preuves pertinentes changent.',[g[0][3],g[4][2]]),
 ('vocabulary_in_context','Pourquoi les vingt formes sont-elles organisées en cinq groupes ?','Chaque groupe correspond à une fonction du raisonnement : cadrer, dialoguer, analyser les sources, limiter la portée et décider/réviser.',g[2]),
 ('synthesis','Comment les données et les valeurs sont-elles reliées sans être confondues ?','Les données établissent ou fragilisent des descriptions et mécanismes; les valeurs interviennent explicitement dans le critère qui transforme ces résultats en recommandation.',[g[2][1],g[4][0]]),
 ('summary','Résume le checkpoint C1.','Le checkpoint organise les vingt formes de l’unité autour d’un raisonnement qui sépare preuve, interprétation, portée, contreargument et critère de décision tout en restant réellement révisable.',forms)
 ];q,a=base.qa(items,ids)
 return {'id':'fr-c1-u01-p06','language':'fr','cefr':'C1','unit':1,'sequence':6,'revision':1,'title':f'Checkpoint C1 : argumenter avec portée, contradiction et révision — {theme}','passage_type':'checkpoint','genre':genre,'domains':['educational','public'],'topics':[theme,'C1 calibration','checkpoint'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':[],'review_lexical_targets':reviews,'grammar_targets':[{'id':'fr-c1-u01-g-checkpoint','role':'review','description':'synthesize concession, scope, source role, normative bridge and revision conditions'}],'discourse_targets':[{'id':'fr-c1-u01-d-checkpoint','role':'review','description':'integrate paired viewpoints, source critique, transfer limits and decision criteria'}],'questions':q,'answer_key':a,'speed_training':{'timed':True,'benchmark_eligible':True,'comprehension_gate':0.8,'new_word_policy':'none','notes':'French C1 Unit01 calibration checkpoint.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Zero-new C1 Unit01 checkpoint.','Calibration only; C1 production default not yet accepted.']},'paired_text_group':None,'prerequisites':['French C1 Unit01 P01-P05'],'difficulty_notes_internal':'C1 cumulative checkpoint for argument architecture, source roles, scope, counterargument and revision.','reader_tags':['unit_role:checkpoint','generation_batch','french_c1_u01_calibration']}

def main():
 for lab,p in [('A1',A1),('A2',A2),('B1',B1)]:
  got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
  if got!=EXPECTED_STABLE[lab]:raise AssertionError(f'{lab} blob drift: {got}')
 audit,ready,plan,probe,sel,groups,details=load_state();theme=txt(plan['theme']);genres=genre_list(plan.get('genres'));lo=int(plan['c1_word_min']);hi=int(plan['c1_word_max'])
 if not 300<=lo<hi<=2000:raise AssertionError(f'implausible C1 word band {lo}-{hi}')
 existing=[]
 if C1.exists():existing=[json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
 if existing:raise AssertionError(f'C1 calibration requires empty canonical C1; found {len(existing)} rows')
 allrows=[]
 for p in (A1,A2,B1,B2):allrows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 deck=base.deck();prior=base.prior(allrows);pid={t['id'] for r in allrows for t in r.get('new_lexical_targets',[])};pf={t['form'] for r in allrows for t in r.get('new_lexical_targets',[])}
 b2u10=allrows[-6:];review_groups={f'p0{i}':[t['form'] for t in b2u10[i-1]['new_lexical_targets']] for i in range(1,6)}
 if any(len(v)!=4 for v in review_groups.values()):raise AssertionError('B2 Unit10 review groups unavailable')
 unit=[]
 for spec in plans(theme,genres):unit.append(make(spec,groups[spec['prefix']],review_groups[spec['prefix']],details,prior,deck,lo,hi,theme))
 checkpoint_genre=(genres[0] if genres else 'C1 cumulative synthesis');unit.append(checkpoint(groups,deck,lo,hi,theme,checkpoint_genre));V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')));newids=[];newforms=[];selected={x['form'] for x in sel['selected']}
 if [r['id'] for r in unit]!=[f'fr-c1-u01-p{i:02d}' for i in range(1,7)] or [r['sequence'] for r in unit]!=list(range(1,7)):raise AssertionError('C1 Unit01 id/sequence failure')
 if unit[1]['paired_text_group']!=PAIR or unit[2]['paired_text_group']!=PAIR or any(unit[i]['paired_text_group'] is not None for i in (0,3,4,5)):raise AssertionError('C1 paired structure failure')
 for r in unit:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:8]]}")
  if not lo<=r['word_count']<=hi or r['word_count']!=len(r['text'].split()):raise AssertionError(f"{r['id']}: C1 word band/count {r['word_count']}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: expected 10 Q/A")
  if r['sequence']<=5 and len(r['new_lexical_targets'])!=4:raise AssertionError(f"{r['id']}: calibration requires four new")
  if r['sequence']==6 and r['new_lexical_targets']:raise AssertionError('C1 P06 must have zero new')
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage failure")
  for t in r['new_lexical_targets']:
   src=deck.get(t['form'])
   if not src or t['id'] in pid or t['form'] in pf or t['source_rank']!=src['rank'] or t['id']!=base.tid(src['rank']) or base.cnt(r['text'],t['form'])!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: new target/source/exposure drift {t}")
   newids.append(t['id']);newforms.append(t['form'])
  for t in r['review_lexical_targets']:
   if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
 if len(newids)!=20 or len(set(newids))!=20 or len(set(newforms))!=20 or set(newforms)!=selected:raise AssertionError('C1 Unit01 target selection/uniqueness failure')
 C1.parent.mkdir(parents=True,exist_ok=True);C1.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in unit),encoding='utf-8')
 print(json.dumps({'status':'PASS','theme':theme,'genres':genres,'word_band':[lo,hi],'passages':6,'questions':60,'answers':60,'new_targets':20,'paired_group':PAIR,'word_counts':{r['id']:r['word_count'] for r in unit}},ensure_ascii=False))
if __name__=='__main__':main()
