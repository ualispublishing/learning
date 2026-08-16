#!/usr/bin/env python3
"""Append French A2 Unit 07 (sequences 37-42) as one guarded batch."""
from __future__ import annotations
import json,re,subprocess
from jsonschema import Draft202012Validator
import generate_french_a2_unit03 as base

A1=base.A1
CANON=base.CANON
SCHEMA=base.SCHEMA
EXPECTED_A1_BLOB="0493a2fa13e51b5997db05e91cdea4d8dc5e647b"
EXPECTED_BLOB="9abd3006e264234e6b5ff2f7c9d37e56cf807fa9"
FORMS=("gauche","tranquille","déjeuner","partager","vue","avancer","marché","poste","intérêt","mur")

SPECS=[
{
"id":"fr-a2-u07-p01","sequence":37,"ptype":"instructional","title":"Tourner à gauche dans une rue tranquille",
"genre":"city navigation narrative","domains":["public","educational"],"topics":["directions","city walking","calm route"],
"forms":["gauche","tranquille"],"reviews":["voyage","train"],
"text":"""Après le voyage de la semaine précédente, Camille et Sami arrivent dans une ville voisine pour une activité scolaire. Leur train entre en gare à l’heure, mais le groupe doit encore marcher jusqu’au centre culturel. La professeure montre une petite carte et demande aux élèves de tourner à gauche après la grande place. Camille remarque qu’une rue semble très animée, tandis qu’une autre paraît plus tranquille. Le groupe choisit la rue tranquille parce qu’il reste assez de temps avant l’activité. À gauche d’une boulangerie, ils trouvent enfin le bâtiment indiqué sur la carte. Sami vérifie le nom sur la porte pour éviter une erreur de direction. Camille comprend qu’un trajet simple devient plus facile quand on observe les repères au lieu de suivre seulement les autres. Le voyage continue donc sans retard, et le groupe entre calmement dans le centre culturel quelques minutes avant le début de la visite.""",
"grammar":[{"id":"fr-a2-u07-apres-location","role":"new","description":"use à gauche de / après to locate a turn relative to a landmark"}],
"discourse":[{"id":"fr-a2-u07-route-choice","role":"new","description":"compare two walking routes and justify a practical choice"}],
"items":[
("gist","Comment le groupe trouve-t-il le centre culturel ?","Il suit la carte, tourne à gauche et choisit une rue tranquille.",["gauche","tranquille"]),
("literal_detail","Quel moyen de transport amène le groupe en ville ?","Le train.",["train"]),
("sequence","Après quel repère les élèves doivent-ils tourner ?","Après la grande place.",["gauche"]),
("cause_effect","Pourquoi le groupe choisit-il la rue tranquille ?","Parce qu’il reste assez de temps et que cette rue semble moins animée.",["tranquille"]),
("vocabulary_in_context","Que signifie « gauche » dans « tourner à gauche » ?","Le côté opposé à la droite.",["gauche"]),
("vocabulary_in_context","Que signifie « tranquille » ici ?","Calme et peu agité.",["tranquille"]),
("reference_resolution","Dans « ils trouvent enfin le bâtiment », qui sont « ils » ?","Les élèves du groupe.",[]),
("inference","Pourquoi Sami vérifie-t-il le nom sur la porte ?","Pour confirmer qu’ils sont arrivés au bon bâtiment.",[]),
("cloze_transfer","Complète : Au carrefour, tourne à _____.","gauche",["gauche"]),
("cloze_transfer","Complète : Cette petite rue est calme et _____.","tranquille",["tranquille"])
]},
{
"id":"fr-a2-u07-p02","sequence":38,"ptype":"reinforcement","title":"Partager le déjeuner avant le départ",
"genre":"meal planning narrative","domains":["public","personal"],"topics":["lunch","sharing","schedule"],
"forms":["déjeuner","partager"],"reviews":["route","départ"],
"text":"""À midi, le groupe doit choisir où prendre son déjeuner avant le départ de l’après-midi. La route vers la gare passe près de plusieurs petits restaurants, mais certains sont déjà pleins. Camille propose un café où chacun peut commander rapidement. Sami veut partager une grande pizza, tandis que deux autres élèves préfèrent prendre leur propre déjeuner. Ils regardent l’heure du départ et décident qu’ils ont quarante minutes. Camille accepte de partager la pizza avec Sami, mais ils demandent deux assiettes pour que chacun puisse manger facilement. Après le déjeuner, le groupe vérifie encore la route vers la gare. Une rue est fermée pour des travaux, alors la professeure choisit un chemin un peu plus long. Personne ne se presse inutilement : ils savent que partager un repas peut être agréable, mais que le départ reste prioritaire. Ils quittent le café ensemble et atteignent la gare avec assez de temps.""",
"grammar":[{"id":"fr-a2-u07-pour-que","role":"new","description":"use pour que + clause to express the purpose of a practical arrangement"}],
"discourse":[{"id":"fr-a2-u07-meal-schedule","role":"new","description":"coordinate a shared meal with a fixed departure time"}],
"items":[
("gist","Que fait le groupe avant de retourner à la gare ?","Il prend son déjeuner en gardant l’heure du départ en tête.",["déjeuner","départ"]),
("literal_detail","Que veulent partager Camille et Sami ?","Une grande pizza.",["partager"]),
("sequence","Que vérifie le groupe après le déjeuner ?","La route vers la gare.",["déjeuner","route"]),
("cause_effect","Pourquoi la professeure choisit-elle un chemin plus long ?","Parce qu’une rue de la route habituelle est fermée.",["route"]),
("vocabulary_in_context","Que signifie « déjeuner » ici ?","Le repas pris à midi.",["déjeuner"]),
("vocabulary_in_context","Que signifie « partager » la pizza ?","La manger à plusieurs en divisant le même plat.",["partager"]),
("reference_resolution","Dans « ils demandent deux assiettes », qui sont « ils » ?","Camille et Sami.",[]),
("inference","Pourquoi personne ne se presse-t-il inutilement ?","Parce que le groupe a vérifié l’heure et dispose encore d’assez de temps.",["départ"]),
("cloze_transfer","Complète : À midi, nous prenons notre _____.","déjeuner",["déjeuner"]),
("cloze_transfer","Complète : Nous allons _____ ce gâteau à deux.","partager",["partager"])
]},
{
"id":"fr-a2-u07-p03","sequence":39,"ptype":"interleaved","title":"Avancer ensemble pour profiter de la vue",
"genre":"group walking narrative","domains":["public","personal"],"topics":["view","group movement","hotel"],
"forms":["vue","avancer"],"reviews":["hôtel","chambre"],
"text":"""Le lendemain, Camille se réveille dans la chambre de l’hôtel avant les autres élèves. Par la fenêtre, elle aperçoit une belle vue sur le quartier et décide de descendre quelques minutes plus tôt. Dans le hall de l’hôtel, la professeure rappelle que le groupe doit avancer ensemble jusqu’au musée. Camille décrit la vue qu’elle a observée et Sami propose de prendre une photo depuis la place voisine. La professeure accepte, à condition que personne ne s’éloigne. Le groupe commence donc à avancer lentement, puis s’arrête à un point où la vue est encore plus claire. Camille prend une photo, range son téléphone et rejoint immédiatement les autres. Elle comprend qu’avancer ne signifie pas forcément marcher vite : il faut parfois progresser en gardant le groupe réuni. Avant de quitter l’hôtel pour de bon, elle vérifie aussi le numéro de sa chambre et s’assure de n’avoir rien oublié.""",
"grammar":[{"id":"fr-a2-u07-a-condition-que","role":"new","description":"recognize à condition que as a condition attached to permission"}],
"discourse":[{"id":"fr-a2-u07-group-progress","role":"new","description":"balance a short observation stop with coordinated group movement"}],
"items":[
("gist","Que fait le groupe entre l’hôtel et le musée ?","Il avance ensemble et s’arrête brièvement pour profiter de la vue.",["avancer","vue","hôtel"]),
("literal_detail","D’où Camille voit-elle d’abord le quartier ?","Depuis la fenêtre de sa chambre.",["chambre","vue"]),
("sequence","Que fait Camille après avoir pris la photo ?","Elle range son téléphone et rejoint les autres.",[]),
("cause_effect","À quelle condition la professeure accepte-t-elle l’arrêt ?","À condition que personne ne s’éloigne du groupe.",[]),
("vocabulary_in_context","Que signifie « vue » ici ?","Ce que l’on peut observer depuis un endroit.",["vue"]),
("vocabulary_in_context","Que signifie « avancer » dans ce texte ?","Continuer à se déplacer vers la destination.",["avancer"]),
("reference_resolution","Dans « elle vérifie aussi le numéro », qui est « elle » ?","Camille.",["chambre"]),
("inference","Pourquoi la professeure veut-elle que le groupe avance ensemble ?","Pour éviter que des élèves se séparent pendant le trajet.",["avancer"]),
("cloze_transfer","Complète : De cette fenêtre, la _____ est magnifique.","vue",["vue"]),
("cloze_transfer","Complète : Le chemin est libre ; nous pouvons _____.","avancer",["avancer"])
]},
{
"id":"fr-a2-u07-p04","sequence":40,"ptype":"transfer","title":"Du marché à la poste",
"genre":"city errands narrative","domains":["public","personal"],"topics":["market","post office","free time"],
"forms":["marché","poste"],"reviews":["retour","visite"],
"text":"""Avant le retour à la maison, la classe dispose d’une heure libre pour une dernière visite dans le centre-ville. Camille veut aller au marché couvert afin d’acheter un petit cadeau, tandis que Sami doit passer à la poste pour envoyer une carte. La professeure accepte les deux idées parce que le marché et la poste se trouvent dans la même rue. Au marché, Camille compare plusieurs objets et choisit un carnet fabriqué localement. Elle garde son reçu, puis rejoint Sami devant la poste. Celui-ci a déjà acheté un timbre et écrit l’adresse sur sa carte. Ils vérifient ensuite l’heure du retour et décident de ne pas commencer une autre visite. Sur le chemin de la gare, Camille remarque qu’un marché permet de découvrir des produits locaux, alors qu’une poste répond à un besoin très différent. Les deux lieux font pourtant partie des services utiles d’un quartier et peuvent s’intégrer facilement à un programme bien organisé.""",
"grammar":[{"id":"fr-a2-u07-alors-que","role":"new","description":"use alors que to contrast the functions of two nearby places"}],
"discourse":[{"id":"fr-a2-u07-two-errands","role":"new","description":"sequence two nearby errands without endangering the return schedule"}],
"items":[
("gist","Quels deux lieux Camille et Sami visitent-ils pendant l’heure libre ?","Le marché et la poste.",["marché","poste","visite"]),
("literal_detail","Qu’achète Camille ?","Un carnet fabriqué localement.",["marché"]),
("sequence","Où Camille rejoint-elle Sami après son achat ?","Devant la poste.",["poste"]),
("cause_effect","Pourquoi la professeure accepte-t-elle les deux idées ?","Parce que le marché et la poste sont dans la même rue.",["marché","poste"]),
("vocabulary_in_context","Que signifie « marché » ici ?","Un lieu où plusieurs vendeurs proposent des produits.",["marché"]),
("vocabulary_in_context","Que signifie « poste » ici ?","Le service où Sami peut envoyer sa carte.",["poste"]),
("reference_resolution","Dans « celui-ci a déjà acheté un timbre », qui est « celui-ci » ?","Sami.",["poste"]),
("inference","Pourquoi ne commencent-ils pas une autre visite ?","Parce qu’ils doivent respecter l’heure du retour.",["retour","visite"]),
("cloze_transfer","Complète : J’achète des légumes au _____.","marché",["marché"]),
("cloze_transfer","Complète : Je vais à la _____ pour envoyer cette carte.","poste",["poste"])
]},
{
"id":"fr-a2-u07-p05","sequence":41,"ptype":"integration","title":"Un mur qui attire l’intérêt",
"genre":"public art narrative","domains":["public","educational"],"topics":["public art","interest","time management"],
"forms":["intérêt","mur"],"reviews":["plan","avion"],
"text":"""Pendant le trajet vers l’aéroport, la classe s’arrête devant un centre d’art public. Camille montre beaucoup d’intérêt pour un grand mur couvert de peintures réalisées par des jeunes du quartier. Sami voudrait rester plus longtemps, mais la professeure rappelle que leur plan prévoit d’arriver tôt pour l’avion. Elle leur accorde dix minutes afin d’observer le mur et de lire le panneau explicatif. Camille découvre que chaque partie de la peinture représente une histoire différente. Son intérêt augmente lorsqu’elle apprend que les habitants ont proposé les thèmes du projet. Avant de repartir, elle prend une photo du mur sans bloquer le passage. Le groupe consulte ensuite le plan du trajet et rejoint l’arrêt de bus. Camille pense qu’un programme peut garder une place pour l’intérêt personnel sans mettre en danger les étapes importantes. L’avion ne les attendra pas, mais quelques minutes bien utilisées peuvent rendre le voyage plus riche.""",
"grammar":[{"id":"fr-a2-u07-lorsque","role":"new","description":"use lorsque to connect a new piece of information with a change in reaction"}],
"discourse":[{"id":"fr-a2-u07-interest-time","role":"new","description":"balance personal interest with a fixed transport plan"}],
"items":[
("gist","Pourquoi le groupe s’arrête-t-il devant le centre d’art ?","Parce que Camille s’intéresse au grand mur peint et que le plan permet un court arrêt.",["intérêt","mur","plan"]),
("literal_detail","Combien de temps la professeure accorde-t-elle au groupe ?","Dix minutes.",[]),
("sequence","Que fait le groupe après avoir observé le mur ?","Il consulte le plan du trajet et rejoint l’arrêt de bus.",["mur","plan"]),
("cause_effect","Pourquoi l’arrêt doit-il rester court ?","Parce que le groupe doit arriver tôt pour l’avion.",["avion"]),
("vocabulary_in_context","Que signifie « intérêt » ici ?","L’attention et la curiosité que Camille porte à l’œuvre.",["intérêt"]),
("vocabulary_in_context","Que désigne le « mur » ?","La grande surface verticale couverte de peintures.",["mur"]),
("reference_resolution","Dans « elle prend une photo », qui est « elle » ?","Camille.",["mur"]),
("inference","Que montre la décision de la professeure ?","Qu’un plan peut inclure un petit arrêt sans compromettre l’étape importante suivante.",["plan"]),
("cloze_transfer","Complète : Cette exposition éveille mon _____.","intérêt",["intérêt"]),
("cloze_transfer","Complète : Une grande peinture couvre le _____.","mur",["mur"])
]}
]

CHECKPOINT={
"id":"fr-a2-u07-p06","sequence":42,"ptype":"checkpoint","title":"Une journée pratique en ville",
"genre":"A2 cumulative city-skills summary","domains":["public","personal"],"topics":["city navigation","services","time management"],
"text":"""Lors d’une sortie en ville, Camille apprend à combiner orientation, temps libre et services pratiques. Après le train, elle suit une carte et tourne à gauche lorsqu’un repère l’indique. Elle préfère parfois une rue tranquille à un chemin plus bruyant. Au moment du déjeuner, elle peut partager un plat avec Sami tout en surveillant l’heure du départ. Depuis la chambre de l’hôtel, elle observe une belle vue, puis elle rejoint le groupe pour avancer ensemble. Avant le retour, elle passe au marché pour acheter un petit objet et accompagne Sami à la poste. Plus tard, son intérêt pour une peinture sur un mur lui donne envie de s’arrêter quelques minutes. Elle vérifie pourtant le plan avant de prolonger la visite, car le groupe doit encore prendre un avion. Camille comprend ainsi qu’une journée réussie ne dépend pas seulement de la vitesse : il faut savoir avancer, choisir un endroit tranquille, partager le temps et garder assez de marge pour les étapes importantes.""",
"grammar":[{"id":"fr-a2-u07-city-summary","role":"integration","description":"integrate temporal links and infinitives in a practical city-day summary"}],
"discourse":[{"id":"fr-a2-u07-adaptive-city-day","role":"integration","description":"summarize orientation, errands, shared time and schedule control"}],
"items":[
("gist","Quelles compétences Camille combine-t-elle pendant la sortie ?","Elle combine l’orientation, la gestion du temps et l’utilisation de services pratiques.",[]),
("literal_detail","Dans quelle direction tourne-t-elle après le train ?","À gauche.",["gauche"]),
("sequence","Que fait-elle avant de passer au marché et à la poste ?","Elle observe une vue puis avance avec le groupe.",["vue","avancer","marché","poste"]),
("cause_effect","Pourquoi vérifie-t-elle le plan avant de prolonger la visite ?","Parce que le groupe doit encore prendre un avion.",[]),
("vocabulary_in_context","Quels mots décrivent le repas et l’action de le prendre ensemble ?","déjeuner et partager",["déjeuner","partager"]),
("vocabulary_in_context","Quels mots désignent le lieu de vente et le service postal ?","marché et poste",["marché","poste"]),
("reference_resolution","Dans « son intérêt », à qui renvoie « son » ?","À Camille.",["intérêt"]),
("inference","Pourquoi une rue tranquille peut-elle être utile pendant cette sortie ?","Parce qu’elle peut rendre le déplacement plus simple et moins agité.",["tranquille"]),
("cloze_transfer","Complète : Une peinture couvre le _____.","mur",["mur"]),
("summary","Résume la stratégie de Camille en une phrase.","Elle s’oriente, avance avec le groupe, utilise les services utiles et protège le temps nécessaire aux étapes importantes.",["avancer"])
]}

def mk(s,new,reviews,ids,speed=False):
    q,a=base.qa(s["items"],ids)
    text=s["text"]
    return {
        "id":s["id"],"language":"fr","cefr":"A2","unit":7,"sequence":s["sequence"],"revision":1,
        "title":s["title"],"passage_type":s["ptype"],"genre":s["genre"],"domains":s["domains"],
        "topics":s["topics"],"text":text,"word_count":len(text.split()),
        "sentence_count":max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),
        "estimated_known_token_coverage":0,"new_lexical_targets":new,"review_lexical_targets":reviews,
        "grammar_targets":s["grammar"],"discourse_targets":s["discourse"],"questions":q,"answer_key":a,
        "speed_training":{"timed":speed,"benchmark_eligible":speed,"comprehension_gate":0.8,
                          "new_word_policy":"none" if speed else "controlled",
                          "notes":"Generation-stage French A2 Unit 07; final language-wide audit deferred."},
        "quality":{"status":"draft","schema_check":"pending","linguistic_review":"pending",
                   "pedagogical_review":"pending","answer_key_check":"pending","coverage_check":"pending",
                   "fact_check":"not_required","notes":[
                       "Guarded French A2 Unit 07 generation batch.",
                       "A1+A2 freshness, source identity, A2 word band, exact review visibility, local target linkage, continuity and zero-new checkpoint are enforced."
                   ]},
        "paired_text_group":None,"prerequisites":["French A2 Units 01-06 canonical corpus"],
        "difficulty_notes_internal":"A2 city navigation and practical services with travel vocabulary recycled as explicit review.",
        "reader_tags":["unit_role:"+s["ptype"],"generation_batch","french_a2_u07"]
    }

def build(a1,a2,D):
    P=base.prior(a1+a2)
    bad=[]
    for f in FORMS:
        if f not in D:
            bad.append(f+":missing_lexicon")
        if P.get(f):
            bad.append(f+":already_deliberate")
    if bad:
        raise AssertionError("Unit07 candidate failures: "+", ".join(bad))
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
    if a1_blob!=EXPECTED_A1_BLOB:
        raise AssertionError(f"A1 blob drift: {a1_blob} != {EXPECTED_A1_BLOB}")
    if blob!=EXPECTED_BLOB:
        raise AssertionError(f"A2 blob drift: {blob} != {EXPECTED_BLOB}")
    a1=[json.loads(x) for x in A1.read_text(encoding="utf-8").splitlines() if x.strip()]
    a2=[json.loads(x) for x in CANON.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(a1)!=60 or a1[-1]["id"]!="fr-a1-u10-p06":
        raise AssertionError("unexpected A1 prerequisite state")
    if len(a2)!=36 or [r["sequence"] for r in a2]!=list(range(1,37)) or a2[-1]["id"]!="fr-a2-u06-p06":
        raise AssertionError("expected exact A2 frontier through Unit06")
    D=base.deck()
    unit=build(a1,a2,D)
    V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    old={t["id"] for r in a1+a2 for t in r.get("new_lexical_targets",[]) if isinstance(t,dict) and t.get("id")}
    if [r["sequence"] for r in unit]!=list(range(37,43)):
        raise AssertionError("Unit07 sequence continuity failure")
    if [r["id"] for r in unit]!=[f"fr-a2-u07-p{i:02d}" for i in range(1,7)]:
        raise AssertionError("Unit07 id continuity failure")
    newids=[]
    for r in unit:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs:
            raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 140<=r["word_count"]<=220:
            raise AssertionError(f"{r['id']}: A2 word band {r['word_count']}")
        if len(r["questions"])!=10 or len(r["answer_key"])!=10:
            raise AssertionError(f"{r['id']}: assessment count")
        amap={a["question_id"]:a["id"] for a in r["answer_key"]}
        decl={t["id"] for fld in ("new_lexical_targets","review_lexical_targets") for t in r.get(fld,[]) if isinstance(t,dict)}
        for q in r["questions"]:
            if amap.get(q["id"])!=q["answer_id"] or any(x not in decl for x in q.get("target_ids",[])):
                raise AssertionError(f"{r['id']} {q['id']}: linkage/target declaration")
        for t in r["new_lexical_targets"]:
            s=D.get(t["form"])
            if t["id"] in old or not s or t["source_rank"]!=s["rank"] or t["id"]!=base.tid(s["rank"]) or base.cnt(r["text"],t["form"])!=t["exposures_in_text"]:
                raise AssertionError(f"{r['id']}: source/exposure/reintroduction drift {t}")
            newids.append(t["id"])
        for t in r["review_lexical_targets"]:
            if t["representation"] in {"running_text","summary"} and base.cnt(r["text"],t["form"])<1:
                raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if len(newids)!=10 or len(set(newids))!=10 or unit[-1]["new_lexical_targets"]!=[]:
        raise AssertionError("Unit07 lexical-cycle invariant")
    CANON.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in a2+unit),encoding="utf-8")
    print(json.dumps({
        "status":"PASS","level":"A2","unit":7,"appended_passages":6,"a2_passages":42,
        "word_counts":{r["id"]:r["word_count"] for r in unit},
        "new_targets":[{"form":f,"rank":D[f]["rank"],"id":base.tid(D[f]["rank"])} for f in FORMS],
        "questions":60,"answers":60,"p06_new_targets":0
    },ensure_ascii=False))

if __name__=="__main__":
    main()
