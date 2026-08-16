#!/usr/bin/env python3
"""Append French A2 Unit 08 (sequences 43-48) as one guarded batch."""
from __future__ import annotations
import json,re,subprocess
from jsonschema import Draft202012Validator
import generate_french_a2_unit03 as base

A1=base.A1
CANON=base.CANON
SCHEMA=base.SCHEMA
EXPECTED_A1_BLOB="0493a2fa13e51b5997db05e91cdea4d8dc5e647b"
EXPECTED_BLOB="423be512ea3675939ad174e188791259035d6656"
FORMS=("étrange","répéter","appartenir","signe","plusieurs","compagnie","douter","test","but","parole")

SPECS=[
{
"id":"fr-a2-u08-p01","sequence":43,"ptype":"instructional","title":"Un message étrange à répéter",
"genre":"listening clarification narrative","domains":["educational","personal"],"topics":["uncertain information","repetition","clarification"],
"forms":["étrange","répéter"],"reviews":["tenter","tranquille"],
"text":"""Au début d’un atelier, Camille et Sami s’installent dans une salle tranquille. La responsable lance un court enregistrement, mais un bruit étrange couvre une partie du message. Camille croit entendre une heure différente de celle écrite au tableau et commence à douter. Au lieu de deviner, elle demande à la responsable de répéter la phrase. Celle-ci accepte et fait écouter le passage une seconde fois. Le bruit étrange revient, mais moins fort, et Camille comprend enfin que le rendez-vous est prévu à quinze heures. Sami propose de tenter une troisième écoute pour vérifier un mot, puis le groupe compare ce qu’il a entendu. Camille remarque que répéter une information n’est pas inutile quand le premier message reste incertain. Elle préfère poser une question claire plutôt que faire semblant d’avoir compris. À la fin, chacun note l’heure correcte et l’atelier peut continuer dans une ambiance tranquille, sans transformer un détail étrange en grande confusion.""",
"grammar":[{"id":"fr-a2-u08-demander-de","role":"new","description":"use demander à quelqu’un de + infinitive for a clarification request"}],
"discourse":[{"id":"fr-a2-u08-hear-check-repeat","role":"new","description":"move from uncertain hearing to repetition and confirmed understanding"}],
"items":[
("gist","Quel problème Camille rencontre-t-elle avec l’enregistrement ?","Un bruit étrange l’empêche de comprendre une partie du message.",["étrange"]),
("literal_detail","Que demande-t-elle à la responsable ?","De répéter la phrase.",["répéter"]),
("sequence","Que propose Sami après la deuxième écoute ?","De tenter une troisième écoute.",["tenter"]),
("cause_effect","Pourquoi la phrase doit-elle être répétée ?","Parce qu’un bruit couvre une partie du message.",["répéter","étrange"]),
("vocabulary_in_context","Que signifie « étrange » ici ?","Inhabituel ou difficile à expliquer immédiatement.",["étrange"]),
("vocabulary_in_context","Que signifie « répéter » ?","Dire ou faire entendre la même information une nouvelle fois.",["répéter"]),
("reference_resolution","Dans « celle-ci accepte », qui est « celle-ci » ?","La responsable.",[]),
("inference","Pourquoi l’ambiance peut-elle rester tranquille ?","Parce que le groupe vérifie calmement l’information au lieu de paniquer.",["tranquille"]),
("cloze_transfer","Complète : Ce son est inhabituel ; il paraît _____.","étrange",["étrange"]),
("cloze_transfer","Complète : Je n’ai pas entendu ; pouvez-vous _____ la phrase ?","répéter",["répéter"])
]},
{
"id":"fr-a2-u08-p02","sequence":44,"ptype":"reinforcement","title":"À qui appartient la boîte ?",
"genre":"lost-object identification narrative","domains":["educational","personal"],"topics":["ownership","clues","shared space"],
"forms":["appartenir","signe"],"reviews":["déjeuner","partager"],
"text":"""À midi, les participants prennent leur déjeuner dans une salle commune et décident de partager deux grandes tables. Après le repas, Camille remarque une petite boîte sous une chaise. Personne ne sait à qui elle peut appartenir. Sur le couvercle, un signe en forme d’étoile est dessiné au feutre, mais aucun nom n’apparaît. Sami pense que ce signe appartient peut-être au logo d’un club scolaire. Camille préfère demander avant de conclure. Elle montre la boîte au groupe et explique où elle l’a trouvée. Une élève reconnaît immédiatement le signe et dit que la boîte appartient à sa sœur, qui participe à un autre atelier dans le même bâtiment. Camille la remet à l’accueil au lieu de la donner directement. Elle comprend qu’un objet peut sembler facile à identifier sans que le premier indice soit suffisant. Le déjeuner partagé a créé beaucoup de mouvements dans la salle ; vérifier à qui quelque chose appartient évite donc une erreur.""",
"grammar":[{"id":"fr-a2-u08-appartenir-a","role":"new","description":"use appartenir à to express ownership"}],
"discourse":[{"id":"fr-a2-u08-clue-confirm-owner","role":"new","description":"use a visible clue as a hypothesis, then confirm ownership before acting"}],
"items":[
("gist","Quel objet Camille trouve-t-elle après le déjeuner ?","Une petite boîte dont le propriétaire n’est pas immédiatement connu.",["déjeuner","appartenir"]),
("literal_detail","Quel signe voit-elle sur le couvercle ?","Une étoile dessinée au feutre.",["signe"]),
("sequence","Que fait Camille avant de remettre la boîte à l’accueil ?","Elle montre la boîte au groupe et demande des informations.",[]),
("cause_effect","Pourquoi ne donne-t-elle pas directement la boîte à l’élève ?","Parce qu’elle veut que l’accueil gère correctement l’objet trouvé.",[]),
("vocabulary_in_context","Que signifie « appartenir » à quelqu’un ?","Être la propriété de cette personne.",["appartenir"]),
("vocabulary_in_context","Que signifie « signe » ici ?","Une marque visible qui peut donner un indice.",["signe"]),
("reference_resolution","Dans « elle montre la boîte », qui est « elle » ?","Camille.",[]),
("inference","Pourquoi le signe seul n’est-il pas une preuve suffisante ?","Parce qu’une même marque peut être interprétée de plusieurs façons.",["signe"]),
("cloze_transfer","Complète : Cette veste semble _____ à Sami.","appartenir",["appartenir"]),
("cloze_transfer","Complète : Une étoile sert de _____ sur la boîte.","signe",["signe"])
]},
{
"id":"fr-a2-u08-p03","sequence":45,"ptype":"interleaved","title":"Plusieurs compagnies sur le quai",
"genre":"service identification narrative","domains":["public","educational"],"topics":["service providers","comparison","reservation"],
"forms":["plusieurs","compagnie"],"reviews":["vue","avancer"],
"text":"""L’après-midi, la classe prépare une petite sortie sur la rivière. Depuis le quai, la vue est claire et Camille distingue plusieurs bateaux. La professeure explique que plusieurs compagnies proposent une promenade similaire, mais que la classe a réservé auprès d’une compagnie précise. Pour avancer vers le bon bateau, les élèves doivent comparer le nom inscrit sur leur billet avec celui affiché près de chaque embarcation. Sami voit d’abord un bateau presque identique et pense que c’est le leur. Camille remarque pourtant qu’il appartient à une autre compagnie. Ils continuent à avancer le long du quai et trouvent finalement le bon point d’embarquement. La professeure rappelle que plusieurs choix peuvent se ressembler sans être équivalents. Camille profite encore de la vue pendant quelques minutes, puis range son billet. Elle comprend qu’une compagnie peut offrir le même type de service qu’une autre, mais que les détails de réservation permettent de savoir laquelle correspond réellement au groupe.""",
"grammar":[{"id":"fr-a2-u08-celui-affiche","role":"new","description":"track celui as a pronoun referring to a previously named label or name"}],
"discourse":[{"id":"fr-a2-u08-compare-providers","role":"new","description":"distinguish similar service providers using reservation evidence"}],
"items":[
("gist","Pourquoi les élèves comparent-ils les noms sur le quai ?","Parce que plusieurs compagnies ont des bateaux similaires et ils doivent trouver la bonne.",["plusieurs","compagnie"]),
("literal_detail","Qu’est-ce qui est clair depuis le quai ?","La vue.",["vue"]),
("sequence","Que font-ils après avoir remarqué le mauvais bateau ?","Ils continuent à avancer jusqu’au bon point d’embarquement.",["avancer"]),
("cause_effect","Pourquoi le premier bateau n’est-il pas le bon ?","Parce qu’il appartient à une autre compagnie.",["compagnie"]),
("vocabulary_in_context","Que signifie « plusieurs » ?","Plus d’un, sans donner un nombre exact.",["plusieurs"]),
("vocabulary_in_context","Que désigne « compagnie » ici ?","Une entreprise qui propose le service de promenade en bateau.",["compagnie"]),
("reference_resolution","Dans « c’est le leur », que désigne « le leur » ?","Le bateau réservé pour leur classe.",[]),
("inference","Pourquoi le billet est-il plus utile que l’apparence du bateau ?","Parce qu’il donne le nom précis de la compagnie réservée.",["compagnie"]),
("cloze_transfer","Complète : Il y a _____ options possibles.","plusieurs",["plusieurs"]),
("cloze_transfer","Complète : Cette _____ organise la promenade en bateau.","compagnie",["compagnie"])
]},
{
"id":"fr-a2-u08-p04","sequence":46,"ptype":"transfer","title":"Douter puis faire un test",
"genre":"purchase verification narrative","domains":["public","personal"],"topics":["verification","testing","purchase decision"],
"forms":["douter","test"],"reviews":["marché","poste"],
"text":"""Le lendemain, Camille passe au marché avant d’accompagner Sami à la poste. Un vendeur lui propose une petite lampe rechargeable et affirme qu’elle fonctionne parfaitement. Camille en doute un peu, car l’objet est présenté sans emballage. Elle demande donc s’il est possible de faire un test avant de payer. Le vendeur accepte, branche la lampe et montre les trois niveaux de lumière. Le test révèle que le bouton fonctionne, mais que la batterie est presque vide. Camille ne doute plus du fonctionnement général, mais elle demande combien de temps il faudra pour la charger. Après avoir obtenu une réponse claire, elle décide de ne pas l’acheter, car elle n’en a pas vraiment besoin. À la poste, Sami plaisante en disant que le test leur a au moins appris quelque chose. Camille pense qu’il est raisonnable de douter d’une affirmation quand on peut la vérifier facilement, sans accuser la personne qui la présente.""",
"grammar":[{"id":"fr-a2-u08-douter-de","role":"new","description":"use douter de / en douter to express uncertainty about a claim"}],
"discourse":[{"id":"fr-a2-u08-claim-test-decision","role":"new","description":"move from a claim through a simple test to a purchase decision"}],
"items":[
("gist","Pourquoi Camille demande-t-elle un test ?","Parce qu’elle doute un peu de l’affirmation sur la lampe.",["douter","test"]),
("literal_detail","Où va-t-elle avant d’accompagner Sami à la poste ?","Au marché.",["marché","poste"]),
("sequence","Que fait le vendeur pendant le test ?","Il branche la lampe et montre ses niveaux de lumière.",["test"]),
("cause_effect","Pourquoi Camille n’achète-t-elle finalement pas la lampe ?","Parce qu’elle n’en a pas vraiment besoin.",[]),
("vocabulary_in_context","Que signifie « douter » ici ?","Ne pas être certain qu’une affirmation est vraie.",["douter"]),
("vocabulary_in_context","Que signifie « test » ici ?","Un essai pratique pour vérifier le fonctionnement de l’objet.",["test"]),
("reference_resolution","Dans « elle fonctionne parfaitement », que désigne « elle » ?","La lampe.",[]),
("inference","Pourquoi le test ne force-t-il pas Camille à acheter ?","Parce que vérifier un produit et décider de l’acheter sont deux décisions différentes.",["test"]),
("cloze_transfer","Complète : Sans preuve, je peux _____ de cette affirmation.","douter",["douter"]),
("cloze_transfer","Complète : Nous faisons un _____ pour vérifier la machine.","test",["test"])
]},
{
"id":"fr-a2-u08-p05","sequence":47,"ptype":"integration","title":"Le but du mur et le droit à la parole",
"genre":"public discussion narrative","domains":["public","educational"],"topics":["public art","discussion","purpose"],
"forms":["but","parole"],"reviews":["intérêt","mur"],
"text":"""Dans l’après-midi, le groupe participe à une discussion devant le mur peint découvert la veille. Camille avait montré beaucoup d’intérêt pour cette œuvre et veut maintenant comprendre son but. La médiatrice donne d’abord la parole à deux jeunes qui ont travaillé sur le projet. Ils expliquent que le but du mur n’est pas seulement de décorer la rue : chaque image raconte une expérience du quartier. Ensuite, la médiatrice donne la parole aux visiteurs. Camille demande pourquoi certaines parties utilisent des couleurs très différentes. Un artiste répond que ce contraste aide à séparer plusieurs histoires tout en les gardant sur le même mur. Sami prend aussi la parole pour demander comment les thèmes ont été choisis. À la fin, Camille comprend mieux le but collectif de l’œuvre. Son intérêt ne vient plus seulement de l’apparence du mur ; il vient aussi des paroles des personnes qui l’ont créé et des intentions qu’elles ont expliquées.""",
"grammar":[{"id":"fr-a2-u08-ne-pas-seulement","role":"new","description":"use ne... pas seulement to expand an initial interpretation"}],
"discourse":[{"id":"fr-a2-u08-purpose-through-voices","role":"new","description":"infer a project purpose by listening to several participants"}],
"items":[
("gist","Que cherche Camille à comprendre pendant la discussion ?","Le but du mur peint.",["but","mur"]),
("literal_detail","À qui la médiatrice donne-t-elle d’abord la parole ?","À deux jeunes qui ont travaillé sur le projet.",["parole"]),
("sequence","Qui prend la parole après Camille ?","Sami.",["parole"]),
("cause_effect","Pourquoi l’intérêt de Camille augmente-t-il en profondeur ?","Parce qu’elle apprend les intentions et les histoires derrière l’œuvre.",["intérêt"]),
("vocabulary_in_context","Que signifie « but » ici ?","L’objectif ou la raison principale du projet.",["but"]),
("vocabulary_in_context","Que signifie « donner la parole » ?","Permettre à quelqu’un de parler devant le groupe.",["parole"]),
("reference_resolution","Dans « ils expliquent », qui sont « ils » ?","Les deux jeunes ayant travaillé sur le projet.",[]),
("inference","Pourquoi les explications changent-elles la perception du mur ?","Parce qu’elles ajoutent le contexte et les intentions des créateurs.",["mur"]),
("cloze_transfer","Complète : Le _____ de cette activité est d’apprendre ensemble.","but",["but"]),
("cloze_transfer","Complète : La médiatrice me donne la _____ pour poser une question.","parole",["parole"])
]}
]

CHECKPOINT={
"id":"fr-a2-u08-p06","sequence":48,"ptype":"checkpoint","title":"Vérifier avant de conclure",
"genre":"A2 cumulative information-evaluation summary","domains":["educational","public","personal"],"topics":["evidence","clarification","decision making"],
"text":"""Quand Camille reçoit une information incertaine, elle évite de deviner trop vite. Si quelque chose paraît étrange, elle peut demander de répéter le message et observer un signe utile. Pour savoir à qui un objet peut appartenir, elle cherche un indice puis confirme son idée. Lorsqu’une classe doit choisir entre plusieurs services, elle vérifie le nom de la compagnie avant d’avancer. Si elle doute d’une affirmation simple, un test peut parfois apporter une réponse concrète. Camille apprend aussi que la parole aide à comprendre le but d’un projet : devant un mur qui suscite son intérêt, écouter les personnes concernées ajoute du contexte. Ces habitudes restent utiles pendant un déjeuner partagé, une sortie avec une belle vue ou une course entre le marché et la poste. Camille comprend finalement qu’une bonne décision repose rarement sur un seul détail. Elle rassemble plusieurs éléments, pose une question précise et accepte de corriger sa première impression quand les signes montrent autre chose.""",
"grammar":[{"id":"fr-a2-u08-evidence-summary","role":"integration","description":"integrate conditional clauses and infinitives in an evidence-checking summary"}],
"discourse":[{"id":"fr-a2-u08-check-before-conclude","role":"integration","description":"summarize clarification, ownership, comparison, testing and purpose inference"}],
"items":[
("gist","Quelle stratégie générale Camille utilise-t-elle face à une information incertaine ?","Elle rassemble des indices, pose des questions et vérifie avant de conclure.",[]),
("literal_detail","Que peut-elle demander si un message paraît étrange ?","De répéter le message.",["étrange","répéter"]),
("sequence","Que fait-elle pour vérifier à qui un objet appartient ?","Elle cherche un signe ou un indice puis confirme son idée.",["appartenir","signe"]),
("cause_effect","Pourquoi compare-t-elle le nom d’un service ?","Parce que plusieurs compagnies peuvent proposer des services semblables.",["plusieurs","compagnie"]),
("vocabulary_in_context","Quels mots expriment l’incertitude et la vérification pratique ?","douter et test",["douter","test"]),
("vocabulary_in_context","Quels mots permettent de parler de l’objectif et du droit de parler ?","but et parole",["but","parole"]),
("reference_resolution","Dans « elle rassemble plusieurs éléments », qui est « elle » ?","Camille.",["plusieurs"]),
("inference","Pourquoi un seul indice peut-il être insuffisant ?","Parce qu’il peut être ambigu et conduire à une première impression incorrecte.",["signe"]),
("cloze_transfer","Complète : Cette boîte peut _____ à quelqu’un d’autre.","appartenir",["appartenir"]),
("summary","Résume la méthode de Camille en une phrase.","Elle clarifie les éléments étranges, compare plusieurs indices, teste les affirmations simples et écoute la parole des personnes concernées avant de décider.",["étrange","plusieurs","test","parole"])
]}

def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s["items"],ids); text=s["text"]
    return {"id":s["id"],"language":"fr","cefr":"A2","unit":8,"sequence":s["sequence"],"revision":1,
            "title":s["title"],"passage_type":s["ptype"],"genre":s["genre"],"domains":s["domains"],"topics":s["topics"],
            "text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),
            "estimated_known_token_coverage":0,"new_lexical_targets":new,"review_lexical_targets":reviews,
            "grammar_targets":s["grammar"],"discourse_targets":s["discourse"],"questions":q,"answer_key":a,
            "speed_training":{"timed":speed,"benchmark_eligible":speed,"comprehension_gate":0.8,"new_word_policy":"none" if speed else "controlled","notes":"Generation-stage French A2 Unit 08; final language-wide audit deferred."},
            "quality":{"status":"draft","schema_check":"pending","linguistic_review":"pending","pedagogical_review":"pending","answer_key_check":"pending","coverage_check":"pending","fact_check":"not_required","notes":["Guarded French A2 Unit 08 generation batch.","A1+A2 freshness, source identity, A2 word band, exact review visibility, local target linkage, continuity and zero-new checkpoint are enforced."]},
            "paired_text_group":None,"prerequisites":["French A2 Units 01-07 canonical corpus"],
            "difficulty_notes_internal":"A2 information evaluation and evidence checking with Unit 07 city vocabulary recycled as explicit review.",
            "reader_tags":["unit_role:"+s["ptype"],"generation_batch","french_a2_u08"]}

def build(a1,a2,D):
    P=base.prior(a1+a2); bad=[]
    for f in FORMS:
        if f not in D: bad.append(f+":missing_lexicon")
        if P.get(f): bad.append(f+":already_deliberate")
    if bad: raise AssertionError("Unit08 candidate failures: "+", ".join(bad))
    out=[]
    for s in SPECS:
        new=[base.nt(f,s["text"],D) for f in s["forms"]]
        reviews=[base.rev(f,P) for f in s["reviews"]]
        ids={t["form"]:t["id"] for t in new+reviews}
        out.append(mk(s,new,reviews,ids))
    reviews=[base.cur(f,D) for f in FORMS]
    ids={t["form"]:t["id"] for t in reviews}
    out.append(mk(CHECKPOINT,[],reviews,ids,True))
    return out

def main():
    a1_blob=subprocess.check_output(["git","hash-object",str(A1)],text=True).strip()
    blob=subprocess.check_output(["git","hash-object",str(CANON)],text=True).strip()
    if a1_blob!=EXPECTED_A1_BLOB: raise AssertionError(f"A1 blob drift: {a1_blob} != {EXPECTED_A1_BLOB}")
    if blob!=EXPECTED_BLOB: raise AssertionError(f"A2 blob drift: {blob} != {EXPECTED_BLOB}")
    a1=[json.loads(x) for x in A1.read_text(encoding="utf-8").splitlines() if x.strip()]
    a2=[json.loads(x) for x in CANON.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(a1)!=60 or a1[-1]["id"]!="fr-a1-u10-p06": raise AssertionError("unexpected A1 prerequisite state")
    if len(a2)!=42 or [r["sequence"] for r in a2]!=list(range(1,43)) or a2[-1]["id"]!="fr-a2-u07-p06": raise AssertionError("expected exact A2 frontier through Unit07")
    D=base.deck(); unit=build(a1,a2,D)
    V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    old={t["id"] for r in a1+a2 for t in r.get("new_lexical_targets",[]) if isinstance(t,dict) and t.get("id")}
    if [r["sequence"] for r in unit]!=list(range(43,49)): raise AssertionError("Unit08 sequence continuity failure")
    if [r["id"] for r in unit]!=[f"fr-a2-u08-p{i:02d}" for i in range(1,7)]: raise AssertionError("Unit08 id continuity failure")
    newids=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 140<=r["word_count"]<=220: raise AssertionError(f"{r['id']}: A2 word band {r['word_count']}")
        if len(r["questions"])!=10 or len(r["answer_key"])!=10: raise AssertionError(f"{r['id']}: assessment count")
        amap={a["question_id"]:a["id"] for a in r["answer_key"]}
        decl={t["id"] for fld in ("new_lexical_targets","review_lexical_targets") for t in r.get(fld,[]) if isinstance(t,dict)}
        for q in r["questions"]:
            if amap.get(q["id"])!=q["answer_id"] or any(x not in decl for x in q.get("target_ids",[])): raise AssertionError(f"{r['id']} {q['id']}: linkage/target declaration")
        for t in r["new_lexical_targets"]:
            s=D.get(t["form"])
            if t["id"] in old or not s or t["source_rank"]!=s["rank"] or t["id"]!=base.tid(s["rank"]) or base.cnt(r["text"],t["form"])!=t["exposures_in_text"]: raise AssertionError(f"{r['id']}: source/exposure/reintroduction drift {t}")
            newids.append(t["id"])
        for t in r["review_lexical_targets"]:
            if t["representation"] in {"running_text","summary"} and base.cnt(r["text"],t["form"])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if len(newids)!=10 or len(set(newids))!=10 or unit[-1]["new_lexical_targets"]!=[]: raise AssertionError("Unit08 lexical-cycle invariant")
    CANON.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in a2+unit),encoding="utf-8")
    print(json.dumps({"status":"PASS","level":"A2","unit":8,"appended_passages":6,"a2_passages":48,
                      "word_counts":{r["id"]:r["word_count"] for r in unit},
                      "new_targets":[{"form":f,"rank":D[f]["rank"],"id":base.tid(D[f]["rank"])} for f in FORMS],
                      "questions":60,"answers":60,"p06_new_targets":0},ensure_ascii=False))

if __name__=="__main__": main()
