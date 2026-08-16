#!/usr/bin/env python3
"""Append French A1 Unit 02 (sequences 7-12) as one guarded batch.

The script is intentionally fail-closed:
- it requires the exact six-passage Unit 01 canonical blob it was reviewed against;
- it verifies all ten new lexical lemmas/ranks against french_top1000.csv;
- it never rewrites sequences 1-6;
- it validates the resulting 12 rows against the canonical schema;
- it requires 10 questions + 10 one-to-one linked answers per row;
- every question target must be declared locally as new or review vocabulary;
- A1 word counts must stay in the 90-140 planning band;
- Unit 02 P06 is a zero-new-target checkpoint.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "reading/french/a1/passages.jsonl"
SCHEMA_PATH = ROOT / "reading/schema/passage.schema.json"
LEXICON = ROOT / "french_top1000.csv"
EXPECTED_UNIT01_BLOB = "6a4b91a16d90c7d28833255efea119076e640cce"

TARGETS = {
    "fr-rank-0013": dict(lemma="aller", form="aller", rank=13, sense="to go", pos="noun / verb"),
    "fr-rank-0014": dict(lemma="faire", form="faire", rank=14, sense="to do; to make", pos="verb"),
    "fr-rank-0022": dict(lemma="dire", form="dire", rank=22, sense="to say; to tell", pos="noun / verb"),
    "fr-rank-0026": dict(lemma="savoir", form="savoir", rank=26, sense="know; know how", pos="noun / verb"),
    "fr-rank-0032": dict(lemma="si", form="si", rank=32, sense="if; whether", pos="adverb / conjunction / noun"),
    "fr-rank-0036": dict(lemma="devoir", form="doit", rank=36, sense="must; have to", pos="noun / verb"),
    "fr-rank-0037": dict(lemma="plus", form="plus", rank=37, sense="more", pos="adverb / noun"),
    "fr-rank-0038": dict(lemma="mon", form="mon", rank=38, sense="my", pos="adjective"),
    "fr-rank-0043": dict(lemma="tout", form="tout", rank=43, sense="all; everything", pos="adjective / adverb / noun / pronoun"),
    "fr-rank-0044": dict(lemma="sur", form="sur", rank=44, sense="on; upon", pos="adjective / preposition"),
}


def qa(items):
    questions = []
    answers = []
    for i, item in enumerate(items, 1):
        qtype, prompt, answer, target_ids = item
        qid, aid = f"q{i}", f"a{i}"
        q = {"id": qid, "type": qtype, "prompt": prompt, "answer_id": aid}
        if target_ids:
            q["target_ids"] = target_ids
        questions.append(q)
        answers.append({"id": aid, "question_id": qid, "answer": answer, "explanation": ""})
    return questions, answers


def review(target_id, form, stage, representation):
    return {
        "id": target_id,
        "form": form,
        "review_stage": stage,
        "representation": representation,
        "expected_exposure_number": None,
    }


def target(target_id, exposures, strategies):
    spec = TARGETS[target_id]
    return {
        "id": target_id,
        "form": spec["form"],
        "lemma": spec["lemma"],
        "intended_sense": spec["sense"],
        "part_of_speech": spec["pos"],
        "register": "contemporary standard",
        "variety": None,
        "context_strategy": strategies,
        "first_introduced": True,
        "exposures_in_text": exposures,
        "source_lexicon": "french_top1000.csv",
        "source_rank": spec["rank"],
        "beyond_base": False,
    }


def base_row(*, pid, seq, ptype, title, genre, domains, topics, text, new_targets,
             reviews, grammar, discourse, qa_items, speed=False):
    questions, answers = qa(qa_items)
    return {
        "id": pid,
        "language": "fr",
        "cefr": "A1",
        "unit": 2,
        "sequence": seq,
        "revision": 1,
        "title": title,
        "passage_type": ptype,
        "genre": genre,
        "domains": domains,
        "topics": topics,
        "text": text,
        "word_count": len(text.split()),
        "sentence_count": max(1, len(re.findall(r"[.!?](?:[»”\"])?", text))),
        "estimated_known_token_coverage": 0,
        "new_lexical_targets": new_targets,
        "review_lexical_targets": reviews,
        "grammar_targets": grammar,
        "discourse_targets": discourse,
        "questions": questions,
        "answer_key": answers,
        "speed_training": {
            "timed": speed,
            "benchmark_eligible": speed,
            "comprehension_gate": 0.8,
            "new_word_policy": "none" if speed else "controlled",
            "notes": "Generation-stage Unit 02 passage; full multi-pass audit is deferred until the French corpus reaches its final review phase.",
        },
        "quality": {
            "status": "draft",
            "schema_check": "pending",
            "linguistic_review": "pending",
            "pedagogical_review": "pending",
            "answer_key_check": "pending",
            "coverage_check": "pending",
            "fact_check": "not_required",
            "notes": [
                "French A1 Unit 02 generated under the generation-first policy and active ten-question contract.",
                "Lightweight generation guards verify schema, source identity, linkage, target declaration, sequence, and word-band invariants; full linguistic/pedagogical audit is intentionally deferred.",
            ],
        },
        "paired_text_group": None,
        "prerequisites": ["French A1 Unit 01 canonical calibration cycle"],
        "difficulty_notes_internal": "A1 continuation: concrete planning, messages, obligations, possession/location, quantity, and cumulative organization.",
        "reader_tags": ["unit_role:" + ptype, "generation_batch", "french_a1_u02"],
    }


def build_rows():
    rows = []

    text = """Samedi matin, Camille veut aller au centre sportif avec Sami. Avant de partir, elle regarde son sac et fait une petite liste. Elle doit prendre une bouteille d’eau, une serviette et ses chaussures. Sa mère lui demande : « Qu’est-ce que tu vas faire là-bas ? » Camille répond : « Je vais faire un cours de danse, puis je veux aller à la piscine. » Sami arrive devant l’immeuble et ils marchent ensemble jusqu’à l’arrêt de bus. Pendant le trajet, Camille vérifie encore sa liste. Au centre sportif, elle met ses affaires dans un casier. Elle est contente : elle peut maintenant aller au cours sans revenir chercher quelque chose à la maison."""
    rows.append(base_row(
        pid="fr-a1-u02-p01", seq=7, ptype="instructional", title="Une matinée au centre sportif",
        genre="daily planning narrative", domains=["personal"], topics=["sport", "planning", "travel"], text=text,
        new_targets=[target("fr-rank-0013", 3, ["scenario_resolution"]), target("fr-rank-0014", 2, ["scenario_resolution"])],
        reviews=[review("fr-rank-0047", "venir", "R2", "contrast"), review("fr-rank-0060", "prendre", "R1", "running_text")],
        grammar=[{"id":"fr-a1-aller-faire-infinitive","role":"new","description":"basic infinitive use after a modal or near-future frame"}],
        discourse=[{"id":"fr-a1-plan-before-action","role":"new","description":"follow a simple preparation sequence before an activity"}],
        qa_items=[
            ("gist", "Pourquoi Camille prépare-t-elle une liste avant de partir ?", "Pour vérifier qu’elle a les affaires nécessaires pour le centre sportif.", []),
            ("literal_detail", "Quels endroits Camille veut-elle visiter au centre sportif ?", "Le cours de danse et la piscine.", []),
            ("vocabulary_in_context", "Que signifie « aller » dans « aller au centre sportif » ?", "Se déplacer vers le centre sportif.", ["fr-rank-0013"]),
            ("vocabulary_in_context", "Que signifie « faire » dans « faire un cours de danse » ?", "Participer au cours de danse.", ["fr-rank-0014"]),
            ("sequence", "Que fait Camille juste avant de mettre ses affaires dans un casier ?", "Elle vérifie encore sa liste pendant le trajet.", []),
            ("single_word_definition", "Quel est le sens courant de « aller » dans cette unité ?", "Se déplacer vers un lieu.", ["fr-rank-0013"]),
            ("grammar_category", "Quelle est la catégorie de « faire » dans « je vais faire un cours » ?", "Un verbe.", ["fr-rank-0014"]),
            ("contrast", "Pour parler d’un déplacement vers un lieu, quel verbe convient ici : « aller » ou « venir » ?", "aller", ["fr-rank-0013", "fr-rank-0047"]),
            ("cloze_transfer", "Complète : Demain, nous voulons _____ au parc.", "aller", ["fr-rank-0013"]),
            ("cloze_transfer", "Complète : Avant le sport, je vais _____ une petite liste.", "faire", ["fr-rank-0014"]),
        ],
    ))

    text = """Après le cours, Camille reçoit un message de sa mère. Elle doit lui dire à quelle heure elle rentre. Camille regarde l’horloge, mais elle ne sait pas encore si elle va prendre le bus ou marcher avec Sami. Elle demande l’heure du prochain bus à l’accueil. L’employée lui dit qu’il arrive dans dix minutes. Maintenant, Camille sait quoi faire. Elle écrit à sa mère : « Je prends le bus de quatre heures et je serai bientôt à la maison. » Sami préfère marcher. Avant de partir, il dit au revoir à Camille. Dans le bus, Camille regarde le quartier par la fenêtre. Elle aime savoir où elle est et pouvoir dire clairement quand elle va arriver."""
    rows.append(base_row(
        pid="fr-a1-u02-p02", seq=8, ptype="reinforcement", title="Un message avant de rentrer",
        genre="message and travel narrative", domains=["personal"], topics=["message", "bus", "time"], text=text,
        new_targets=[target("fr-rank-0022", 2, ["scenario_resolution"]), target("fr-rank-0026", 1, ["scenario_resolution"])],
        reviews=[review("fr-rank-0061", "quand", "R2", "running_text")],
        grammar=[{"id":"fr-a1-dire-savoir-present","role":"new","description":"high-frequency present-tense forms of dire and savoir"}],
        discourse=[{"id":"fr-a1-message-time","role":"new","description":"extract and communicate a simple time plan"}],
        qa_items=[
            ("gist", "Pourquoi Camille écrit-elle à sa mère ?", "Pour lui dire à quelle heure elle va rentrer.", []),
            ("literal_detail", "Dans combien de minutes arrive le prochain bus ?", "Dans dix minutes.", []),
            ("vocabulary_in_context", "Que signifie « dire » quand Camille doit dire l’heure à sa mère ?", "Communiquer l’information à sa mère.", ["fr-rank-0022"]),
            ("vocabulary_in_context", "Que signifie « savoir » dans « elle aime savoir où elle est » ?", "Connaître l’information.", ["fr-rank-0026"]),
            ("sequence", "Que fait Camille après avoir demandé l’heure du bus ?", "Elle écrit à sa mère pour lui donner son heure de retour.", []),
            ("single_word_definition", "Dans cette unité, que signifie « savoir » ?", "Connaître une information ou savoir comment faire quelque chose.", ["fr-rank-0026"]),
            ("grammar_choice", "Choisis la forme correcte : « Camille sait l’heure » ou « Camille saitent l’heure ».", "Camille sait l’heure.", ["fr-rank-0026"]),
            ("contrast", "Pour communiquer une information à quelqu’un, quel verbe convient : « dire » ou « voir » ?", "dire", ["fr-rank-0022"]),
            ("cloze_transfer", "Complète : Je veux _____ la vérité à mon ami.", "dire", ["fr-rank-0022"]),
            ("cloze_transfer", "Complète : Elle veut _____ à quelle heure le magasin ferme.", "savoir", ["fr-rank-0026"]),
        ],
    ))

    text = """Le dimanche, la tante de Camille vient déjeuner. Camille veut aider à préparer la table. Sa mère lui explique ce qu’elle doit faire : elle doit mettre quatre assiettes, quatre verres et les serviettes. Camille commence tout de suite. Si elle ne trouve pas quelque chose, elle doit demander. Elle cherche les serviettes et ne les voit pas dans le tiroir habituel. « Si elles ne sont pas ici, où sont-elles ? » demande-t-elle. Sa mère montre une étagère près de la fenêtre. Camille les prend et termine la table. Ensuite, elle vérifie encore une fois chaque place. Elle comprend qu’elle doit poser une question si elle n’est pas sûre, au lieu de choisir au hasard."""
    rows.append(base_row(
        pid="fr-a1-u02-p03", seq=9, ptype="interleaved", title="Avant le déjeuner",
        genre="household task narrative", domains=["personal"], topics=["family", "table", "instructions"], text=text,
        new_targets=[target("fr-rank-0032", 3, ["conditional_assumption"]), target("fr-rank-0036", 4, ["scenario_resolution"])],
        reviews=[review("fr-rank-0021", "pouvoir", "R2", "contrast"), review("fr-rank-0060", "prendre", "R2", "running_text")],
        grammar=[{"id":"fr-a1-si-present-condition","role":"new","description":"si + present for a simple condition"}, {"id":"fr-a1-devoir-obligation","role":"new","description":"devoir + infinitive for a simple obligation"}],
        discourse=[{"id":"fr-a1-condition-action","role":"new","description":"connect a simple condition with the action that follows"}],
        qa_items=[
            ("gist", "Quelle tâche Camille aide-t-elle à faire ?", "Elle aide à préparer la table pour le déjeuner.", []),
            ("literal_detail", "Où se trouvent finalement les serviettes ?", "Sur une étagère près de la fenêtre.", []),
            ("vocabulary_in_context", "Que montre « si » dans « Si elle ne trouve pas quelque chose, elle doit demander » ?", "Une condition.", ["fr-rank-0032"]),
            ("vocabulary_in_context", "Que signifie « doit » dans « elle doit mettre quatre assiettes » ?", "Elle a l’obligation ou la tâche de le faire.", ["fr-rank-0036"]),
            ("cause_effect", "Pourquoi Camille pose-t-elle une question au lieu de choisir au hasard ?", "Parce qu’elle n’est pas sûre de l’endroit où sont les serviettes.", []),
            ("single_word_definition", "Quel sens de « devoir » est travaillé ici ?", "Avoir à faire quelque chose ; être obligé de le faire.", ["fr-rank-0036"]),
            ("grammar_function", "Quel rôle joue « si » au début d’une phrase comme « Si je ne sais pas, je demande » ?", "Il introduit une condition.", ["fr-rank-0032"]),
            ("contrast", "Pour une obligation, quel verbe convient : « devoir » ou « pouvoir » ?", "devoir", ["fr-rank-0036", "fr-rank-0021"]),
            ("cloze_transfer", "Complète : _____ tu as une question, demande au professeur.", "Si", ["fr-rank-0032"]),
            ("cloze_transfer", "Complète : Avant le repas, Camille _____ mettre les verres sur la table.", "doit", ["fr-rank-0036"]),
        ],
    ))

    text = """Lundi, Camille cherche son petit carnet avant de partir à l’école. Elle dit : « Mon carnet était ici hier. » Elle regarde dans son sac, sous la chaise et près de la fenêtre. Rien. Puis son frère entre et montre la table du salon. Le carnet est sur un livre, juste à côté d’un crayon. Camille rit : « Voilà mon carnet ! » Elle le prend et écrit son nom sur la première page. Sur la deuxième page, elle note trois choses à faire après les cours. Avant de sortir, elle pose son téléphone sur la table pour le charger. Elle sait maintenant que, si elle met toujours son carnet au même endroit, elle le trouvera plus facilement le matin."""
    rows.append(base_row(
        pid="fr-a1-u02-p04", seq=10, ptype="transfer", title="Mon carnet est sur la table",
        genre="lost-object micro-story", domains=["personal", "educational"], topics=["notebook", "location", "school"], text=text,
        new_targets=[target("fr-rank-0038", 2, ["form_function"]), target("fr-rank-0044", 4, ["scenario_resolution"])],
        reviews=[review("fr-rank-0060", "prendre", "R2", "running_text")],
        grammar=[{"id":"fr-a1-mon-possession","role":"new","description":"mon before a masculine singular noun"}, {"id":"fr-a1-sur-location","role":"new","description":"sur + noun phrase for location on a surface"}],
        discourse=[{"id":"fr-a1-search-location","role":"new","description":"follow a simple search through successive locations"}],
        qa_items=[
            ("gist", "Que cherche Camille avant l’école ?", "Son petit carnet.", []),
            ("literal_detail", "Où Camille trouve-t-elle le carnet ?", "Sur un livre, sur la table du salon.", []),
            ("vocabulary_in_context", "Que montre « mon » dans « mon carnet » ?", "Que le carnet appartient à la personne qui parle.", ["fr-rank-0038"]),
            ("vocabulary_in_context", "Que signifie « sur » dans « le carnet est sur un livre » ?", "Le carnet est posé au-dessus du livre, en contact avec lui.", ["fr-rank-0044"]),
            ("sequence", "Que fait Camille après avoir trouvé le carnet ?", "Elle le prend et écrit son nom sur la première page.", []),
            ("single_word_definition", "Dans une phrase de lieu, que signifie généralement « sur » ?", "Sur une surface ; au-dessus et en contact avec elle.", ["fr-rank-0044"]),
            ("grammar_category", "Quel type de mot est « mon » dans « mon carnet » ?", "Un déterminant possessif.", ["fr-rank-0038"]),
            ("contrast", "Si le carnet appartient au locuteur, lequel convient : « mon carnet » ou « ton carnet » ?", "mon carnet", ["fr-rank-0038"]),
            ("cloze_transfer", "Complète : Le téléphone est _____ la table.", "sur", ["fr-rank-0044"]),
            ("cloze_transfer", "Complète : Je prends _____ sac avant de partir.", "mon", ["fr-rank-0038"]),
        ],
    ))

    text = """Après l’école, Camille prépare une petite affiche pour le club de lecture. Elle met tout le matériel sur la table : une grande feuille, deux crayons, une règle et des feutres. Elle écrit le titre, mais elle veut plus de place pour dessiner. Elle déplace le titre vers le haut et gagne un peu plus d’espace. Sami arrive et regarde l’affiche. « Tout est clair, mais il manque l’heure », dit-il. Camille ajoute l’heure sous le titre. Ensuite, ils relisent tout ensemble. Il reste encore un peu de place, alors Camille dessine un petit livre dans un coin. Quand l’affiche est terminée, elle arrête d’ajouter des éléments. Elle préfère un message simple où chaque information est facile à lire."""
    rows.append(base_row(
        pid="fr-a1-u02-p05", seq=11, ptype="integration", title="L’affiche du club",
        genre="school project narrative", domains=["educational"], topics=["club", "poster", "quantity"], text=text,
        new_targets=[target("fr-rank-0043", 3, ["category_relation"]), target("fr-rank-0037", 2, ["contrast"])],
        reviews=[review("fr-rank-0061", "quand", "R3", "running_text"), review("fr-rank-0063", "alors", "R3", "running_text")],
        grammar=[{"id":"fr-a1-tout-totality","role":"new","description":"tout for totality in a simple noun phrase or pronoun use"}, {"id":"fr-a1-plus-de-quantity","role":"new","description":"plus de + noun for a greater quantity"}],
        discourse=[{"id":"fr-a1-revise-poster","role":"integration","description":"integrate a simple feedback-and-revision sequence"}],
        qa_items=[
            ("gist", "Que préparent Camille et Sami ?", "Une affiche pour le club de lecture.", []),
            ("literal_detail", "Quelle information Sami remarque-t-il comme manquante ?", "L’heure.", []),
            ("vocabulary_in_context", "Que signifie « tout » dans « tout le matériel » ?", "L’ensemble du matériel nécessaire.", ["fr-rank-0043"]),
            ("vocabulary_in_context", "Que signifie « plus » dans « plus de place » ?", "Une quantité ou un espace plus grand.", ["fr-rank-0037"]),
            ("sequence", "Que fait Camille après que Sami remarque l’information manquante ?", "Elle ajoute l’heure sous le titre.", []),
            ("single_word_definition", "Dans cette unité, que signifie « plus » sans négation ?", "Davantage ; une quantité supérieure.", ["fr-rank-0037"]),
            ("grammar_function", "Dans « plus de place », que fait l’expression « plus de » ?", "Elle indique une quantité plus grande.", ["fr-rank-0037"]),
            ("contrast", "Pour parler de l’ensemble du matériel, lequel convient : « tout » ou « une partie » ?", "tout", ["fr-rank-0043"]),
            ("cloze_transfer", "Complète : Il me faut _____ de temps pour finir.", "plus", ["fr-rank-0037"]),
            ("cloze_transfer", "Complète : J’ai vérifié _____ le travail avant de partir.", "tout", ["fr-rank-0043"]),
        ],
    ))

    text = """Cette semaine, Camille a mieux organisé ses activités. Quand elle veut aller quelque part, elle prépare d’abord ce qu’elle doit prendre. Elle sait aussi qu’elle peut demander une information si elle n’est pas sûre. Au centre sportif, elle a appris à dire à sa mère quand elle rentre. À la maison, elle met son carnet sur la même table pour le trouver facilement. Pour le club de lecture, elle fait une affiche simple et vérifie que tout est clair. Sami l’aide parfois, mais Camille peut aussi travailler seule. Elle comprend qu’un peu d’organisation donne plus de temps pour les choses qu’elle aime. Avant de sortir, elle regarde une dernière fois son sac, puis elle part sans stress."""
    rows.append(base_row(
        pid="fr-a1-u02-p06", seq=12, ptype="checkpoint", title="Une semaine mieux organisée",
        genre="fluency checkpoint summary", domains=["personal", "educational"], topics=["organization", "review", "routine"], text=text,
        new_targets=[],
        reviews=[
            review("fr-rank-0013", "aller", "R2", "summary"), review("fr-rank-0014", "faire", "R2", "summary"),
            review("fr-rank-0022", "dire", "R2", "summary"), review("fr-rank-0026", "savoir", "R2", "summary"),
            review("fr-rank-0032", "si", "R1", "running_text"), review("fr-rank-0036", "devoir", "R1", "summary"),
            review("fr-rank-0038", "mon", "R1", "cloze"), review("fr-rank-0044", "sur", "R1", "running_text"),
            review("fr-rank-0043", "tout", "R1", "running_text"), review("fr-rank-0037", "plus", "R1", "contrast"),
        ],
        grammar=[{"id":"fr-a1-u02-grammar-integration","role":"integration","description":"review obligation, condition, possession, location, and simple quantity expressions"}],
        discourse=[{"id":"fr-a1-u02-routine-summary","role":"integration","description":"integrate several concrete routines into a short organizational summary"}],
        qa_items=[
            ("gist", "Quelle est l’idée principale du texte ?", "Camille utilise quelques habitudes simples pour mieux organiser sa semaine.", []),
            ("literal_detail", "Où Camille met-elle son carnet pour le retrouver facilement ?", "Sur la même table.", ["fr-rank-0044"]),
            ("vocabulary_in_context", "Dans ce texte, que signifie « sait » dans « elle sait aussi » ?", "Elle connaît l’information ou la manière d’agir.", ["fr-rank-0026"]),
            ("reference_resolution", "Dans « elle prépare d’abord ce qu’elle doit prendre », à qui renvoie « elle » ?", "À Camille.", []),
            ("cause_effect", "Pourquoi l’organisation donne-t-elle plus de temps à Camille ?", "Parce qu’elle prépare et vérifie ses affaires au lieu de perdre du temps à les chercher.", ["fr-rank-0037"]),
            ("single_word_definition", "Que signifie « devoir » quand il exprime une obligation ?", "Avoir à faire quelque chose.", ["fr-rank-0036"]),
            ("grammar_choice", "Choisis la forme correcte pour un garçon qui parle de son sac : « mon sac » ou « ma sac ».", "mon sac", ["fr-rank-0038"]),
            ("contrast", "Lequel signifie « davantage » : « plus » ou « tout » ?", "plus", ["fr-rank-0037", "fr-rank-0043"]),
            ("cloze_transfer", "Complète : Après l’école, nous voulons _____ à la bibliothèque.", "aller", ["fr-rank-0013"]),
            ("cloze_transfer", "Complète : Pour préparer le projet, je vais _____ une liste.", "faire", ["fr-rank-0014"]),
        ],
        speed=True,
    ))
    return rows


def read_rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def verify_source_identity():
    by_front = {}
    with LEXICON.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            by_front[row["Front"]] = row["Back"]
    for tid, spec in TARGETS.items():
        back = by_front.get(spec["lemma"])
        if not back:
            raise AssertionError(f"missing source lemma {spec['lemma']}")
        m = re.search(r"Rank:\s*(\d+)", back)
        if not m or int(m.group(1)) != spec["rank"]:
            raise AssertionError(f"source-rank drift for {tid}/{spec['lemma']}: {m.group(1) if m else None} != {spec['rank']}")


def declared_ids(row):
    return {
        str(t["id"])
        for field in ("new_lexical_targets", "review_lexical_targets")
        for t in row.get(field, [])
        if isinstance(t, dict) and t.get("id")
    }


def validate_row(row, validator):
    errors = sorted(validator.iter_errors(row), key=lambda e: list(e.path))
    if errors:
        raise AssertionError(f"schema failure {row['id']}: {errors[0].message} @ {list(errors[0].path)}")
    if not 90 <= row["word_count"] <= 140:
        raise AssertionError(f"A1 word-band failure {row['id']}: {row['word_count']}")
    if len(row["questions"]) != 10 or len(row["answer_key"]) != 10:
        raise AssertionError(f"ten-question contract failure {row['id']}")
    qids = [q["id"] for q in row["questions"]]
    aids = [a["id"] for a in row["answer_key"]]
    if qids != [f"q{i}" for i in range(1,11)] or aids != [f"a{i}" for i in range(1,11)]:
        raise AssertionError(f"question/answer ID sequence failure {row['id']}")
    q_to_answer = {a["question_id"]: a["id"] for a in row["answer_key"]}
    if len(q_to_answer) != 10:
        raise AssertionError(f"duplicate/missing answer linkage {row['id']}")
    for q in row["questions"]:
        if q_to_answer.get(q["id"]) != q["answer_id"]:
            raise AssertionError(f"linkage failure {row['id']} {q['id']}")
    local = declared_ids(row)
    for q in row["questions"]:
        for tid in q.get("target_ids", []):
            if tid not in local:
                raise AssertionError(f"undeclared question target {row['id']} {q['id']} {tid}")
    if row["id"].endswith("-p06") and row["new_lexical_targets"]:
        raise AssertionError(f"checkpoint introduced new target {row['id']}")


def main():
    if subprocess.check_output(["git", "hash-object", str(CANON)], text=True).strip() != EXPECTED_UNIT01_BLOB:
        raise AssertionError("French A1 canonical source drift: expected untouched six-passage Unit 01 blob")
    existing = read_rows(CANON)
    if len(existing) != 6:
        raise AssertionError(f"expected exactly 6 existing French A1 rows, got {len(existing)}")
    if [r.get("sequence") for r in existing] != list(range(1,7)):
        raise AssertionError("existing French A1 sequence drift")
    if [r.get("id") for r in existing] != [f"fr-a1-u01-p{i:02d}" for i in range(1,7)]:
        raise AssertionError("existing French A1 ID drift")
    existing_new_ids = {
        t.get("id") for r in existing for t in r.get("new_lexical_targets", []) if isinstance(t, dict)
    }
    overlap = set(TARGETS) & existing_new_ids
    if overlap:
        raise AssertionError(f"Unit 02 attempts to re-introduce existing target IDs: {sorted(overlap)}")

    verify_source_identity()
    new_rows = build_rows()
    if [r["sequence"] for r in new_rows] != list(range(7,13)):
        raise AssertionError("new sequence contract failure")
    if [r["id"] for r in new_rows] != [f"fr-a1-u02-p{i:02d}" for i in range(1,7)]:
        raise AssertionError("new Unit 02 ID contract failure")

    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    for row in new_rows:
        validate_row(row, validator)
    for row in existing:
        errors = list(validator.iter_errors(row))
        if errors:
            raise AssertionError(f"pre-existing Unit 01 schema drift at {row.get('id')}: {errors[0].message}")

    # Recompute declared lexical exposure counts for literal surface forms used by
    # this batch. Conjugated forms are intentionally not guessed by the guard.
    for row in new_rows:
        for t in row["new_lexical_targets"]:
            literal = len(re.findall(rf"(?<!\w){re.escape(t['form'])}(?!\w)", row["text"], flags=re.IGNORECASE))
            if literal == 0:
                # devoir is intentionally introduced through the very frequent
                # surface form doit while retaining canonical lemma/source rank.
                raise AssertionError(f"new target surface not present: {row['id']} {t['id']} {t['form']}")
            if literal != t["exposures_in_text"]:
                raise AssertionError(f"exposure drift {row['id']} {t['id']}: {literal} != {t['exposures_in_text']}")

    original = CANON.read_text(encoding="utf-8")
    if original and not original.endswith("\n"):
        original += "\n"
    addition = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in new_rows)
    CANON.write_text(original + addition, encoding="utf-8")

    final = read_rows(CANON)
    if len(final) != 12 or [r["sequence"] for r in final] != list(range(1,13)):
        raise AssertionError("post-write French A1 continuity failure")
    for row in final:
        validate_row(row, validator)

    print(json.dumps({
        "status": "PASS",
        "unit": 2,
        "appended_passages": len(new_rows),
        "sequences": [7, 8, 9, 10, 11, 12],
        "word_counts": {r["id"]: r["word_count"] for r in new_rows},
        "new_targets": sum(len(r["new_lexical_targets"]) for r in new_rows),
        "checkpoint_new_targets": len(new_rows[-1]["new_lexical_targets"]),
        "questions": sum(len(r["questions"]) for r in new_rows),
        "answers": sum(len(r["answer_key"]) for r in new_rows),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
