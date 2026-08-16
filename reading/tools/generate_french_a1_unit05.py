#!/usr/bin/env python3
"""Append French A1 Unit 05 (sequences 25-30) as one guarded batch."""
from __future__ import annotations

import csv, json, re, subprocess
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "reading/french/a1/passages.jsonl"
SCHEMA = ROOT / "reading/schema/passage.schema.json"
LEXICON = ROOT / "french_top1000.csv"
EXPECTED_BLOB = "53778d358071b94472bb8d8210ebd888810938ca"
NEW_FORMS = ("heure","matin","soir","semaine","fois","chose","place","question","enfant","ville")

def parse_lexicon():
    out={}
    with LEXICON.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            form=(row.get("Front") or "").strip()
            back=row.get("Back") or ""
            m_rank=re.search(r"Rank:\s*(\d+)",back)
            m_mean=re.search(r"Meaning:\s*(.+)",back)
            m_pos=re.search(r"Part of speech:\s*(.+)",back)
            if form and m_rank and m_mean and m_pos:
                out[form]={"rank":int(m_rank.group(1)),"sense":m_mean.group(1).strip(),"pos":m_pos.group(1).strip()}
    return out

def tid(rank): return f"fr-rank-{rank:04d}"

def qa(items):
    qs=[]; ans=[]
    for i,(typ,prompt,answer,tids) in enumerate(items,1):
        qid=f"q{i}"; aid=f"a{i}"
        q={"id":qid,"type":typ,"prompt":prompt,"answer_id":aid}
        if tids: q["target_ids"]=tids
        qs.append(q)
        ans.append({"id":aid,"question_id":qid,"answer":answer,"explanation":""})
    return qs,ans

def count_form(text, form):
    return len(re.findall(rf"(?<!\w){re.escape(form)}(?!\w)", text, flags=re.I|re.UNICODE))

def new_target(form,text,lex):
    s=lex[form]
    c=count_form(text,form)
    if c < 1: raise AssertionError(f"{form}: new target has no exact running-text exposure")
    return {"id":tid(s["rank"]),"form":form,"lemma":form,"intended_sense":s["sense"],
            "part_of_speech":s["pos"],"register":"contemporary standard","variety":None,
            "context_strategy":["scenario_resolution"],"first_introduced":True,
            "exposures_in_text":c,"source_lexicon":"french_top1000.csv",
            "source_rank":s["rank"],"beyond_base":False}

def prior_index(rows):
    out={}
    for r in rows:
        for t in r.get("new_lexical_targets",[]):
            if isinstance(t,dict) and t.get("form"):
                out.setdefault(t["form"],[]).append(t)
    return out

def review(form, stage, rep, prior):
    hits=prior.get(form,[])
    if len(hits)!=1: raise AssertionError(f"{form}: expected one prior deliberate introduction, got {len(hits)}")
    t=hits[0]
    return {"id":t["id"],"form":form,"review_stage":stage,"representation":rep,"expected_exposure_number":None}

def unit_review(form, stage, rep, lex):
    s=lex[form]
    return {"id":tid(s["rank"]),"form":form,"review_stage":stage,"representation":rep,"expected_exposure_number":None}

def mk(pid,seq,ptype,title,genre,domains,topics,text,new,reviews,grammar,discourse,items,speed=False):
    qs,ans=qa(items)
    return {
        "id":pid,"language":"fr","cefr":"A1","unit":5,"sequence":seq,"revision":1,
        "title":title,"passage_type":ptype,"genre":genre,"domains":domains,"topics":topics,
        "text":text,"word_count":len(text.split()),
        "sentence_count":max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),
        "estimated_known_token_coverage":0,
        "new_lexical_targets":new,"review_lexical_targets":reviews,
        "grammar_targets":grammar,"discourse_targets":discourse,
        "questions":qs,"answer_key":ans,
        "speed_training":{"timed":speed,"benchmark_eligible":speed,"comprehension_gate":0.8,
                          "new_word_policy":"none" if speed else "controlled",
                          "notes":"Generation-stage French A1 Unit 05; full multi-pass audit deferred."},
        "quality":{"status":"draft","schema_check":"pending","linguistic_review":"pending",
                   "pedagogical_review":"pending","answer_key_check":"pending","coverage_check":"pending",
                   "fact_check":"not_required",
                   "notes":["Guarded French A1 Unit 05 generation batch under the active ten-question contract.",
                            "Schema, source identity, word band, local target declaration, linkage, continuity, review, and checkpoint invariants are enforced during generation."]},
        "paired_text_group":None,"prerequisites":["French A1 Units 01-04 canonical corpus"],
        "difficulty_notes_internal":"A1 continuation: time of day/week, repeated occasions, things/places/questions, children/city, and cumulative everyday organization.",
        "reader_tags":["unit_role:"+ptype,"generation_batch","french_a1_u05"],
    }

def build(existing,lex):
    prior=prior_index(existing)
    for f in NEW_FORMS:
        if f not in lex: raise AssertionError(f"{f}: missing from french_top1000.csv")
        if prior.get(f): raise AssertionError(f"{f}: already deliberately introduced before Unit 05")

    o=[]
    text="""Lundi matin, Camille arrive à l’école une heure avant le début du cours. Elle veut finir une affiche avec Sami. Le matin, la salle est encore calme et ils peuvent travailler sans bruit. Camille regarde l’heure sur l’horloge : il est huit heures, et le cours commence à neuf heures. Elle écrit le titre pendant que Sami place les images. Après trente minutes, ils relisent tout et ajoutent une autre feuille. Camille dit qu’ils ont encore une demi-heure. Ils utilisent ce temps pour corriger deux mots et ranger la table. Quand les autres élèves arrivent, leur travail est déjà prêt et très clair."""
    n1=new_target("heure",text,lex); n2=new_target("matin",text,lex)
    o.append(mk("fr-a1-u05-p01",25,"instructional","Une heure avant le cours","school preparation narrative",
      ["educational"],["school","time","preparation"],text,[n1,n2],
      [review("très","R2","running_text",prior),review("autre","R2","running_text",prior)],
      [{"id":"fr-a1-heure-clock","role":"new","description":"heure for clock time or duration"},
       {"id":"fr-a1-matin-part-day","role":"new","description":"matin as the morning part of the day"}],
      [{"id":"fr-a1-time-planning","role":"new","description":"follow a simple preparation timeline"}],
      [("gist","Pourquoi Camille arrive-t-elle tôt à l’école ?","Pour finir une affiche avec Sami.",[]),
       ("literal_detail","À quelle heure commence le cours ?","À neuf heures.",[]),
       ("vocabulary_in_context","Que signifie « heure » dans « une heure avant le début du cours » ?","Une durée de soixante minutes.",[n1["id"]]),
       ("vocabulary_in_context","Que désigne « matin » dans le texte ?","La première partie de la journée.",[n2["id"]]),
       ("sequence","Que font Camille et Sami après avoir relu l’affiche ?","Ils ajoutent une autre feuille puis corrigent deux mots.",[]),
       ("single_word_definition","Que signifie « heure » ici ?","Une unité de temps ou un moment indiqué par l’horloge.",[n1["id"]]),
       ("grammar_category","Quel type de mot est « matin » dans « lundi matin » ?","Un nom.",[n2["id"]]),
       ("contrast","Pour parler d’un moment précis sur l’horloge, lequel convient : « heure » ou « matin » ?","heure",[n1["id"],n2["id"]]),
       ("cloze_transfer","Complète : Le cours commence dans une _____.","heure",[n1["id"]]),
       ("cloze_transfer","Complète : Je prépare mon sac le _____.","matin",[n2["id"]])]))

    text="""Cette semaine, Camille a plusieurs petites choses à faire après l’école. Le lundi soir, elle doit terminer un exercice. Le mardi soir, elle va à la bibliothèque avec Sami. Le mercredi, elle reste à la maison parce que sa mère rentre tard. Camille regarde son calendrier et écrit une activité pour chaque jour de la semaine. Elle garde toujours ce calendrier dans son sac. Elle trouve que le soir est plus simple quand elle sait déjà ce qu’elle doit faire. Vendredi, elle n’a pas de devoir urgent. Elle décide alors de passer le soir avec sa famille et de lire un peu avant de dormir."""
    n1=new_target("soir",text,lex); n2=new_target("semaine",text,lex)
    o.append(mk("fr-a1-u05-p02",26,"reinforcement","Le calendrier de la semaine","weekly routine narrative",
      ["personal","educational"],["calendar","week","evening routine"],text,[n1,n2],
      [review("temps","R2","running_text",prior),review("toujours","R2","running_text",prior)],
      [{"id":"fr-a1-soir-part-day","role":"new","description":"soir as the evening part of the day"},
       {"id":"fr-a1-semaine-cycle","role":"new","description":"semaine as a seven-day period"}],
      [{"id":"fr-a1-weekly-sequence","role":"new","description":"follow activities across several days"}],
      [("gist","Pourquoi Camille regarde-t-elle son calendrier ?","Pour organiser ses activités de la semaine.",[]),
       ("literal_detail","Que fait-elle le mardi soir ?","Elle va à la bibliothèque avec Sami.",[]),
       ("vocabulary_in_context","Que signifie « soir » dans « le lundi soir » ?","La partie de la journée après l’après-midi.",[n1["id"]]),
       ("vocabulary_in_context","Que signifie « semaine » ici ?","Une période de sept jours.",[n2["id"]]),
       ("sequence","Quel jour Camille reste-t-elle à la maison ?","Le mercredi.",[]),
       ("single_word_definition","Que signifie « semaine » ?","Une période de sept jours.",[n2["id"]]),
       ("grammar_category","Quel type de mot est « soir » ?","Un nom.",[n1["id"]]),
       ("contrast","Pour parler de plusieurs jours ensemble, lequel convient : « semaine » ou « soir » ?","semaine",[n1["id"],n2["id"]]),
       ("cloze_transfer","Complète : Je lis un peu le _____.","soir",[n1["id"]]),
       ("cloze_transfer","Complète : Cette _____, j’ai cours du lundi au vendredi.","semaine",[n2["id"]])]))

    text="""Au marché, Camille veut acheter des pommes comme la dernière fois. Cette fois, elle voit aussi des poires jaunes. Elle hésite et demande à sa mère si elles peuvent essayer une autre chose. Sa mère répond oui. Camille prend deux poires et trois pommes. Une fois les fruits dans le sac, elle vérifie la liste. Il manque encore du pain. Une personne attend devant le stand voisin, alors Camille patiente. Ensuite, le vendeur lui donne le pain. Camille regarde une dernière fois la liste avant de partir. Elle comprend qu’une petite chose oubliée peut obliger à revenir plus tard."""
    n1=new_target("fois",text,lex); n2=new_target("chose",text,lex)
    o.append(mk("fr-a1-u05-p03",27,"interleaved","Cette fois au marché","shopping choice narrative",
      ["personal","public"],["shopping","repetition","objects"],text,[n1,n2],
      [review("encore","R2","running_text",prior),review("personne","R2","running_text",prior)],
      [{"id":"fr-a1-fois-occasion","role":"new","description":"fois as an occasion or occurrence"},
       {"id":"fr-a1-chose-item","role":"new","description":"chose as a general thing or item"}],
      [{"id":"fr-a1-check-list","role":"new","description":"use a list to verify simple purchases"}],
      [("gist","Qu’achète Camille au marché ?","Des pommes, des poires et du pain.",[]),
       ("literal_detail","Combien de poires prend-elle ?","Deux.",[]),
       ("vocabulary_in_context","Que signifie « fois » dans « cette fois » ?","Cette occasion-ci.",[n1["id"]]),
       ("vocabulary_in_context","Que signifie « chose » dans « une autre chose » ?","Un objet ou un élément non nommé précisément.",[n2["id"]]),
       ("cause_effect","Pourquoi Camille vérifie-t-elle la liste ?","Pour voir s’il manque encore quelque chose.",[]),
       ("single_word_definition","Que signifie « fois » ici ?","Une occasion ou une occurrence.",[n1["id"]]),
       ("grammar_category","Quel type de mot est « chose » ?","Un nom.",[n2["id"]]),
       ("contrast","Pour parler d’un objet sans le nommer précisément, lequel convient : « chose » ou « fois » ?","chose",[n1["id"],n2["id"]]),
       ("cloze_transfer","Complète : Cette _____, je prends le bus.","fois",[n1["id"]]),
       ("cloze_transfer","Complète : Il y a une _____ importante dans mon sac.","chose",[n2["id"]])]))

    text="""Samedi, Camille va à la bibliothèque à vélo. Ce jour-là, beaucoup de personnes sont déjà dehors. Devant l’entrée, elle cherche une place pour laisser son vélo. La première place est prise, mais il y en a une autre près d’un arbre. Camille attache son vélo et entre. À l’accueil, elle a une question sur un livre qu’elle doit rendre. Elle pose sa question à la bibliothécaire, qui lui montre une boîte spéciale pour les retours. Avant de partir, Camille vérifie que son vélo est toujours à sa place. Elle aime savoir exactement où elle met ses affaires dans un lieu public."""
    n1=new_target("place",text,lex); n2=new_target("question",text,lex)
    o.append(mk("fr-a1-u05-p04",28,"transfer","Une place pour le vélo","library errand narrative",
      ["public"],["library","bike","asking for information"],text,[n1,n2],
      [review("jour","R2","running_text",prior),review("avant","R2","running_text",prior)],
      [{"id":"fr-a1-place-location","role":"new","description":"place as a spot or position for something"},
       {"id":"fr-a1-question-information","role":"new","description":"question as something asked to get information"}],
      [{"id":"fr-a1-public-errand","role":"new","description":"complete a small public-place errand"}],
      [("gist","Pourquoi Camille entre-t-elle dans la bibliothèque ?","Pour rendre un livre.",[]),
       ("literal_detail","Où laisse-t-elle son vélo ?","Près d’un arbre.",[]),
       ("vocabulary_in_context","Que signifie « place » dans « une place pour laisser son vélo » ?","Un endroit disponible pour le vélo.",[n1["id"]]),
       ("vocabulary_in_context","Que signifie « question » dans le texte ?","Quelque chose qu’on demande pour obtenir une information.",[n2["id"]]),
       ("sequence","Que fait Camille avant de repartir ?","Elle vérifie que son vélo est toujours à sa place.",[]),
       ("single_word_definition","Que signifie « question » ?","Une demande d’information.",[n2["id"]]),
       ("grammar_category","Quel type de mot est « place » ?","Un nom.",[n1["id"]]),
       ("contrast","Pour demander une information, lequel convient : « question » ou « place » ?","question",[n1["id"],n2["id"]]),
       ("cloze_transfer","Complète : Il reste une _____ près de la fenêtre.","place",[n1["id"]]),
       ("cloze_transfer","Complète : J’ai une _____ pour le professeur.","question",[n2["id"]])]))

    text="""Mercredi après-midi, Camille accompagne son petit frère à une activité pour enfants dans le centre-ville. Chaque enfant reçoit une feuille et des crayons. L’animatrice demande aux enfants de dessiner un endroit de leur ville. Le frère de Camille choisit le parc. Un autre enfant dessine l’école et un troisième dessine une grande rue. Camille reste près de la porte et regarde les dessins. À la fin, les enfants expliquent leur dessin en une phrase. Camille voit que la ville peut être décrite de plusieurs façons selon ce que chaque enfant remarque. Après l’activité, Camille et son frère rentrent à la maison."""
    n1=new_target("enfant",text,lex); n2=new_target("ville",text,lex)
    o.append(mk("fr-a1-u05-p05",29,"integration","Dessiner la ville","community activity narrative",
      ["public","personal"],["children","city","drawing"],text,[n1,n2],
      [review("après","R2","running_text",prior),review("maison","R2","running_text",prior)],
      [{"id":"fr-a1-enfant-person","role":"new","description":"enfant as a young person"},
       {"id":"fr-a1-ville-place","role":"new","description":"ville as an urban place"}],
      [{"id":"fr-a1-multiple-perspectives","role":"new","description":"notice different simple views of the same city"}],
      [("gist","Que font les enfants pendant l’activité ?","Ils dessinent un endroit de leur ville.",[]),
       ("literal_detail","Quel lieu choisit le frère de Camille ?","Le parc.",[]),
       ("vocabulary_in_context","Que signifie « enfant » ici ?","Une jeune personne.",[n1["id"]]),
       ("vocabulary_in_context","Que signifie « ville » dans le texte ?","Le lieu urbain où ils habitent et se déplacent.",[n2["id"]]),
       ("inference","Pourquoi les dessins sont-ils différents ?","Parce que chaque enfant remarque ou choisit un lieu différent.",[]),
       ("single_word_definition","Que signifie « ville » ?","Une grande localité où vivent beaucoup de personnes.",[n2["id"]]),
       ("grammar_category","Quel type de mot est « enfant » ?","Un nom.",[n1["id"]]),
       ("contrast","Lequel désigne une personne : « enfant » ou « ville » ?","enfant",[n1["id"],n2["id"]]),
       ("cloze_transfer","Complète : Chaque _____ reçoit un crayon.","enfant",[n1["id"]]),
       ("cloze_transfer","Complète : Nous visitons le centre de la _____.","ville",[n2["id"]])]))

    text="""Pendant une semaine normale, Camille organise maintenant beaucoup de petites activités. Le matin, elle regarde l’heure avant de partir à l’école. Le soir, elle vérifie ce qu’elle doit faire le lendemain. Une fois au marché ou à la bibliothèque, elle garde sa liste et pose une question si quelque chose n’est pas clair. Elle cherche une place pour ses affaires et vérifie encore avant de partir. Quand elle accompagne son frère, elle observe les enfants et les différents lieux de la ville. Ces habitudes simples l’aident à utiliser son temps, à se souvenir de chaque chose importante et à se déplacer avec plus de confiance."""
    reviews=[unit_review(f,"R1","summary",lex) for f in NEW_FORMS]
    o.append(mk("fr-a1-u05-p06",30,"checkpoint","Une semaine bien organisée","cumulative routine summary",
      ["personal","public","educational"],["routine","time","organization"],text,[],reviews,
      [{"id":"fr-a1-u05-cumulative-time","role":"integration","description":"integrate time-of-day and weekly expressions"},
       {"id":"fr-a1-u05-cumulative-nouns","role":"integration","description":"integrate common people/place/thing nouns"}],
      [{"id":"fr-a1-u05-cumulative-routine","role":"integration","description":"summarize everyday routines across contexts"}],
      [("gist","Quelle est l’idée principale du texte ?","Camille organise mieux ses activités quotidiennes.",[]),
       ("literal_detail","Que regarde-t-elle le matin ?","L’heure.",[]),
       ("vocabulary_in_context","Que signifie « semaine » dans ce résumé ?","Une période de sept jours.",[tid(lex["semaine"]["rank"])]),
       ("vocabulary_in_context","Que signifie « place » quand Camille cherche où mettre ses affaires ?","Un endroit disponible ou prévu pour ses affaires.",[tid(lex["place"]["rank"])]),
       ("sequence","Que fait Camille le soir avant le lendemain ?","Elle vérifie ce qu’elle doit faire.",[]),
       ("single_word_definition","Que signifie « fois » dans « une fois au marché » ?","Quand elle y est arrivée ; à cette occasion.",[tid(lex["fois"]["rank"])]),
       ("grammar_category","Quel type de mot est « question » ?","Un nom.",[tid(lex["question"]["rank"])]),
       ("contrast","Lequel désigne une personne : « enfant » ou « ville » ?","enfant",[tid(lex["enfant"]["rank"]),tid(lex["ville"]["rank"])]),
       ("cloze_transfer","Complète : Je lis un peu le _____.","soir",[tid(lex["soir"]["rank"])]),
       ("summary","Résume la routine de Camille en une phrase.","Elle vérifie son temps et ses tâches, pose des questions quand nécessaire et organise ses affaires dans différents lieux.",[])],speed=True))
    return o

def main():
    blob=subprocess.check_output(["git","hash-object",str(CANON)],text=True).strip()
    if blob != EXPECTED_BLOB:
        raise AssertionError(f"canonical blob drift: {blob} != {EXPECTED_BLOB}")
    rows=[json.loads(x) for x in CANON.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows)!=24 or [r["sequence"] for r in rows]!=list(range(1,25)) or rows[-1]["id"]!="fr-a1-u04-p06":
        raise AssertionError("expected exact 24-passage French A1 frontier through Unit 04")
    lex=parse_lexicon()
    unit=build(rows,lex)
    if [r["sequence"] for r in unit]!=list(range(25,31)):
        raise AssertionError("Unit 05 sequence construction failure")
    if len({r["id"] for r in rows+unit})!=30:
        raise AssertionError("duplicate passage IDs")
    validator=Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    old_target_ids={t["id"] for r in rows for t in r.get("new_lexical_targets",[]) if isinstance(t,dict)}
    for r in unit:
        errs=sorted(validator.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema errors: {[e.message for e in errs[:5]]}")
        if not (90 <= r["word_count"] <= 140): raise AssertionError(f"{r['id']}: word band {r['word_count']}")
        if len(r["questions"])!=10 or len(r["answer_key"])!=10: raise AssertionError(f"{r['id']}: 10x assessment invariant")
        amap={a["question_id"]:a["id"] for a in r["answer_key"]}
        if len(amap)!=10: raise AssertionError(f"{r['id']}: answer linkage duplicate")
        declared={t["id"] for field in ("new_lexical_targets","review_lexical_targets") for t in r.get(field,[]) if isinstance(t,dict)}
        for q in r["questions"]:
            if amap.get(q["id"]) != q["answer_id"]: raise AssertionError(f"{r['id']} {q['id']}: answer linkage")
            for x in q.get("target_ids",[]):
                if x not in declared: raise AssertionError(f"{r['id']} {q['id']}: undeclared target {x}")
        for t in r["new_lexical_targets"]:
            if t["id"] in old_target_ids: raise AssertionError(f"{r['id']}: reintroduced target {t['id']}")
            src=lex.get(t["form"])
            if not src or t["source_rank"]!=src["rank"] or t["id"]!=tid(src["rank"]):
                raise AssertionError(f"{r['id']}: source identity drift {t}")
    if sum(len(r["new_lexical_targets"]) for r in unit[:5])!=10: raise AssertionError("expected 10 Unit 05 new targets")
    if unit[-1]["new_lexical_targets"] != []: raise AssertionError("Unit 05 P06 must have zero new targets")
    CANON.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows+unit),encoding="utf-8")
    print(json.dumps({"status":"PASS","unit":5,"appended_passages":6,"sequences":[25,26,27,28,29,30],
                      "word_counts":{r["id"]:r["word_count"] for r in unit},
                      "new_targets":[{"form":f,"rank":lex[f]["rank"],"id":tid(lex[f]["rank"])} for f in NEW_FORMS],
                      "checkpoint_new_targets":0,"questions":60,"answers":60},ensure_ascii=False))

if __name__=="__main__":
    main()
