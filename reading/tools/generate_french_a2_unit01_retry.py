#!/usr/bin/env python3
"""Retry French A2 Unit 01 after loader syntax failure, with bounded content corrections."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "reading/tools/generate_french_a2_unit01.py"


def load_base_namespace():
    source = BASE.read_text(encoding="utf-8")
    broken = "'))).decode())"
    fixed = "')).decode())"
    if source.count(broken) != 1:
        raise AssertionError("unexpected A2 Unit 01 loader state; refuse blind syntax rewrite")
    source = source.replace(broken, fixed, 1)
    ns = {"__name__": "french_a2_unit01_base", "__file__": str(BASE)}
    exec(compile(source, str(BASE), "exec"), ns)
    return ns


def main():
    ns = load_base_namespace()
    data = ns["DATA"]

    # Repair the one accidental English word in the draft answer key before generation.
    typo_hits = 0
    for spec in data["specs"]:
        for item in spec["items"]:
            if isinstance(item[2], str) and "mistake" in item[2]:
                item[2] = item[2].replace("par mistake", "par erreur").replace("mistake", "erreur")
                typo_hits += 1
    if typo_hits != 1:
        raise AssertionError(f"expected exactly one draft English-word repair, got {typo_hits}")

    # The root deck gloss for prévenir is 'prevent', while the first draft used its
    # notify/warn sense. Avoid teaching a sense that does not match the scheduled
    # source metadata: replace that target with validated 'éviter' and rewrite P04.
    p4 = next(s for s in data["specs"] if s["pid"] == "fr-a2-u01-p04")
    if set(p4["forms"]) != {"réparer", "prévenir"}:
        raise AssertionError(f"unexpected P04 target state: {p4['forms']}")
    p4["title"] = "Un bruit dans le vélo"
    p4["forms"] = ["réparer", "éviter"]
    p4["text"] = (
        "Mercredi, le vélo de Camille fait un bruit étrange quand elle rentre de l’école. "
        "Elle s’arrête devant un petit atelier, car elle préfère vérifier le problème avant de continuer. "
        "Le réparateur regarde la roue et lui explique qu’une pièce est desserrée. Il peut réparer le vélo "
        "tout de suite, et le prix reste raisonnable. Camille a assez d’argent, mais elle avait prévu d’acheter "
        "un vêtement après les cours. Elle décide donc de reporter cet achat. Pendant que le réparateur travaille, "
        "il lui montre comment vérifier les pneus et les freins chaque semaine. Selon lui, quelques minutes "
        "d’entretien peuvent éviter une panne plus importante. Camille écoute son conseil et prend une photo des "
        "étapes avec son téléphone. Quand le vélo est prêt, elle paie, remercie le réparateur et rentre plus lentement. "
        "Elle comprend qu’un petit contrôle régulier peut éviter un problème coûteux plus tard."
    )
    p4["grammar"] = [
        {"id": "fr-a2-reparer-infinitive", "role": "new", "description": "infinitive after pouvoir: peut réparer"},
        {"id": "fr-a2-eviter-infinitive", "role": "new", "description": "infinitive after modal expression: peut éviter"},
    ]
    p4["discourse"] = [
        {"id": "fr-a2-problem-prevention", "role": "new", "description": "connect a present repair to prevention of a later problem"}
    ]
    p4["items"] = [
        ["gist", "Pourquoi Camille entre-t-elle dans l’atelier ?", "Parce que son vélo fait un bruit étrange et qu’elle veut vérifier le problème.", []],
        ["literal_detail", "Quel achat Camille décide-t-elle de reporter ?", "L’achat d’un vêtement.", ["vêtement"]],
        ["vocabulary_in_context", "Que signifie « réparer » dans ce texte ?", "Remettre le vélo en bon état pour qu’il fonctionne correctement.", ["réparer"]],
        ["vocabulary_in_context", "Que signifie « éviter » dans la dernière partie ?", "Empêcher qu’un problème ou une panne arrive.", ["éviter"]],
        ["inference", "Pourquoi Camille prend-elle une photo des étapes ?", "Pour se souvenir des vérifications et pouvoir les refaire plus tard.", []],
        ["single_word_definition", "Que signifie « éviter » ici ?", "Faire en sorte qu’un problème n’arrive pas.", ["éviter"]],
        ["grammar_category", "Quel type de mot est « réparer » ?", "Un verbe.", ["réparer"]],
        ["contrast", "Lequel concerne le problème actuel : « réparer » ou « éviter » ?", "réparer", ["réparer", "éviter"]],
        ["cloze_transfer", "Complète : Le technicien peut _____ le vélo aujourd’hui.", "réparer", ["réparer"]],
        ["cloze_transfer", "Complète : Un contrôle régulier peut _____ une panne.", "éviter", ["éviter"]],
    ]

    # Rebuild the capstone so all ten accepted targets are visible in the intended senses.
    data["p6"]["text"] = (
        "Depuis qu’elle commence le niveau A2, Camille rencontre des situations un peu moins prévisibles. "
        "Un matin, un retard de bus l’oblige à changer son trajet, et un conseil l’aide à choisir une autre solution. "
        "À l’école, une erreur dans un formulaire lui demande d’expliquer ce qui s’est passé. Devant une machine, "
        "elle doit essayer plusieurs étapes pour voir ce qui est possible. Quand son vélo fait un bruit étrange, "
        "elle préfère le faire réparer rapidement et apprend qu’un entretien simple peut éviter une panne. Plus tard, "
        "elle arrive à un rendez-vous et découvre un service qu’elle ne connaissait pas. Dans chaque situation, Camille "
        "doit comprendre la cause du problème, comparer des options et agir. Elle ne connaît pas toujours la réponse "
        "immédiatement, mais elle sait maintenant demander des précisions, relier plusieurs informations et expliquer "
        "pourquoi elle choisit une solution plutôt qu’une autre."
    )
    data["p6"]["items"] = [
        ["gist", "Quelle nouvelle capacité générale Camille développe-t-elle au début d’A2 ?", "Elle apprend à gérer de petits problèmes en reliant plusieurs informations et en choisissant une action.", []],
        ["literal_detail", "Qu’est-ce qui l’aide après le retard du bus ?", "Un conseil.", ["retard", "conseil"]],
        ["vocabulary_in_context", "Que signifie « erreur » dans le passage ?", "Une information ou une action incorrecte.", ["erreur"]],
        ["vocabulary_in_context", "Que signifie « rendez-vous » ici ?", "Une rencontre prévue à une heure ou à un moment déterminé.", ["rendez-vous"]],
        ["inference", "Pourquoi Camille compare-t-elle plusieurs options ?", "Parce qu’une situation peut avoir plusieurs réponses et qu’elle doit choisir celle qui convient.", []],
        ["single_word_definition", "Que signifie « découvrir » dans ce texte ?", "Apprendre ou trouver quelque chose qu’on ne connaissait pas auparavant.", ["découvrir"]],
        ["grammar_category", "Quel type de mot est « essayer » ?", "Un verbe.", ["essayer"]],
        ["contrast", "Lequel est un verbe d’action : « essayer » ou « possible » ?", "essayer", ["essayer", "possible"]],
        ["cloze_transfer", "Complète : Je vais _____ pourquoi j’ai choisi cette option.", "expliquer", ["expliquer"]],
        ["summary", "Résume en une phrase la stratégie de Camille face à un problème.", "Elle identifie la cause, cherche ou essaie des options, puis choisit une solution et peut expliquer son choix.", []],
    ]

    ns["NEW_FORMS"] = (
        "retard", "conseil", "erreur", "expliquer", "essayer",
        "possible", "réparer", "éviter", "rendez-vous", "découvrir",
    )

    # Verify the replacement itself is backed by the root validated source before running main().
    lex = ns["lexicon"]()
    if "éviter" not in lex or lex["éviter"]["rank"] != 662:
        raise AssertionError(f"validated éviter source changed: {lex.get('éviter')}")

    ns["main"]()


if __name__ == "__main__":
    main()
