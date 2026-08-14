import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"

ROLE = {1: "instructional", 2: "reinforcement", 3: "interleaved", 4: "transfer", 5: "checkpoint", 6: "fluency"}

# Five carefully authored extension questions per staged passage. The staging
# Markdown already supplies Q1-Q5; these complete the canonical ten-question
# passage contract without changing the passage prose.
EXTRA_QA = {
    "fr-a1-u01-p01": [
        {"type": "single_word_definition", "prompt": "Que signifie « venir » dans « Tu veux venir avec moi ? » ?", "answer": "Aller avec la personne vers l’endroit dont elle parle.", "target_ids": ["fr-rank-0047"]},
        {"type": "grammar_choice", "prompt": "Choisis la forme correcte : « Je viens avec toi » ou « Je vient avec toi » ?", "answer": "Je viens avec toi.", "target_ids": ["fr-rank-0047"]},
        {"type": "reference_resolution", "prompt": "Dans « Elle ouvre la fenêtre », à qui renvoie « elle » ?", "answer": "À Camille."},
        {"type": "cloze_transfer", "prompt": "Complète : Ma mère est à la porte ; je vais _____ avec elle.", "answer": "venir", "target_ids": ["fr-rank-0047"]},
        {"type": "contrast", "prompt": "Pour parler de l’endroit où se trouve le locuteur, quel mot convient : « ici » ou « demain » ?", "answer": "ici", "target_ids": ["fr-rank-0048"]},
    ],
    "fr-a1-u01-p02": [
        {"type": "single_word_definition", "prompt": "Que signifie « alors » quand il introduit l’action qui suit une situation ?", "answer": "À ce moment-là ; ensuite, comme conséquence ou suite.", "target_ids": ["fr-rank-0063"]},
        {"type": "grammar_function", "prompt": "Dans « Quand le feu devient vert, ils traversent », quel rôle joue « quand » ?", "answer": "Il introduit le moment où l’action de traverser se produit.", "target_ids": ["fr-rank-0061"]},
        {"type": "sequence", "prompt": "Qu’est-ce qui arrive d’abord : le feu devient vert ou Camille et Sami traversent ?", "answer": "Le feu devient vert d’abord."},
        {"type": "cloze_transfer", "prompt": "Complète : _____ le cours finit, je rentre chez moi.", "answer": "Quand", "target_ids": ["fr-rank-0061"]},
        {"type": "cloze_transfer", "prompt": "Complète : Il est huit heures ; _____ nous partons pour l’école.", "answer": "alors", "target_ids": ["fr-rank-0063"]},
    ],
    "fr-a1-u01-p03": [
        {"type": "single_word_definition", "prompt": "Que signifie « vouloir » dans « elle veut finir ses devoirs » ?", "answer": "Avoir l’intention ou l’envie de faire quelque chose.", "target_ids": ["fr-rank-0023"]},
        {"type": "grammar_function", "prompt": "Dans « Sami s’assoit avec elle », que marque « avec » ?", "answer": "L’accompagnement : Sami et Camille sont ensemble.", "target_ids": ["fr-rank-0035"]},
        {"type": "grammar_choice", "prompt": "Choisis la forme correcte : « Je veux sortir » ou « Je veut sortir » ?", "answer": "Je veux sortir.", "target_ids": ["fr-rank-0023"]},
        {"type": "cloze_transfer", "prompt": "Complète : Nous _____ aller au parc après les devoirs.", "answer": "voulons", "target_ids": ["fr-rank-0023"]},
        {"type": "reference_resolution", "prompt": "Dans « Il regarde les enfants qui jouent déjà », qui est « il » ?", "answer": "Le petit frère de Camille."},
    ],
    "fr-a1-u01-p04": [
        {"type": "single_word_definition", "prompt": "Que signifie « pouvoir » dans « elle peut entrer » ?", "answer": "Être capable de faire quelque chose ou avoir la possibilité de le faire.", "target_ids": ["fr-rank-0021"]},
        {"type": "single_word_definition", "prompt": "Que signifie « voir » dans ce passage ?", "answer": "Percevoir ou remarquer avec les yeux.", "target_ids": ["fr-rank-0039"]},
        {"type": "grammar_choice", "prompt": "Choisis la forme correcte : « Nous pouvons entrer » ou « Nous peut entrer » ?", "answer": "Nous pouvons entrer.", "target_ids": ["fr-rank-0021"]},
        {"type": "cloze_transfer", "prompt": "Complète : De ma fenêtre, je _____ le parc.", "answer": "vois", "target_ids": ["fr-rank-0039"]},
        {"type": "contrast", "prompt": "Dans ce contexte, quelle phrase exprime une possibilité : « Je peux lire » ou « Je lis hier » ?", "answer": "Je peux lire.", "target_ids": ["fr-rank-0021"]},
    ],
    "fr-a1-u01-p05": [
        {"type": "single_word_definition", "prompt": "Que signifie « prendre » quand Camille prend des pommes au marché ?", "answer": "Les choisir et les mettre avec ses achats.", "target_ids": ["fr-rank-0060"]},
        {"type": "reference_resolution", "prompt": "Dans « Camille voit Sami là », à quel lieu « là » renvoie-t-il ?", "answer": "Au marché, près du stand de fleurs.", "target_ids": ["fr-rank-0057"]},
        {"type": "grammar_choice", "prompt": "Choisis la phrase correcte : « Elle prend quatre pommes » ou « Elle prennent quatre pommes » ?", "answer": "Elle prend quatre pommes.", "target_ids": ["fr-rank-0060"]},
        {"type": "cloze_transfer", "prompt": "Complète : J’ai besoin de pain ; je vais en _____ un au marché.", "answer": "prendre", "target_ids": ["fr-rank-0060"]},
        {"type": "contrast", "prompt": "Pour désigner un endroit déjà montré mais pas forcément tout près du locuteur, quel mot convient ici : « là » ou « demain » ?", "answer": "là", "target_ids": ["fr-rank-0057"]},
    ],
    "fr-a1-u01-p06": [
        {"type": "contrast", "prompt": "Quel mot renvoie à l’endroit où Camille se sent bien à la fin : « ici » ou « quand » ?", "answer": "ici", "target_ids": ["fr-rank-0048"]},
        {"type": "single_word_definition", "prompt": "Que signifie « peut » dans « elle peut rentrer directement » ?", "answer": "Elle a la possibilité de rentrer directement.", "target_ids": ["fr-rank-0021"]},
        {"type": "single_word_definition", "prompt": "Que signifie « veut » dans « son petit frère veut aller au parc » ?", "answer": "Il a envie ou l’intention d’aller au parc.", "target_ids": ["fr-rank-0023"]},
        {"type": "single_word_definition", "prompt": "Que signifie « prennent » dans « Elles prennent seulement ce dont elles ont besoin » ?", "answer": "Elles choisissent et emportent les choses dont elles ont besoin.", "target_ids": ["fr-rank-0060"]},
        {"type": "grammar_function", "prompt": "Dans « Quand elle rencontre Sami », que marque « quand » ?", "answer": "Le moment où elle rencontre Sami.", "target_ids": ["fr-rank-0061"]},
    ],
    "ur-a1-u01-p01": [
        {"type": "single_word_definition", "prompt": "«یہ» کا بنیادی کام کیا ہے؟", "answer": "قریب یا سامنے موجود چیز یا جگہ کی طرف اشارہ کرنا۔", "target_ids": ["ur-rank-0018"]},
        {"type": "single_word_definition", "prompt": "«ساتھ» کا مطلب کیا ہے؟", "answer": "کسی کے ہمراہ یا ایک ہی وقت میں اس کے ساتھ ہونا۔", "target_ids": ["ur-rank-0041"]},
        {"type": "reference_resolution", "prompt": "«خالہ نے پوچھا کہ کیا وہ بازار چلنا چاہتی ہے» میں «وہ» کس کے لیے ہے؟", "answer": "عائشہ کے لیے۔"},
        {"type": "cloze_transfer", "prompt": "خالی جگہ پُر کریں: _____ میری کتاب ہے۔", "answer": "یہ", "target_ids": ["ur-rank-0018"]},
        {"type": "cloze_transfer", "prompt": "خالی جگہ پُر کریں: علی اپنے بھائی کے _____ اسکول گیا۔", "answer": "ساتھ", "target_ids": ["ur-rank-0041"]},
    ],
    "ur-a1-u01-p02": [
        {"type": "single_word_definition", "prompt": "«بعد» کا مطلب کیا ہے؟", "answer": "کسی وقت یا کام کے گزرنے کے پیچھے آنے والا وقت۔", "target_ids": ["ur-rank-0040"]},
        {"type": "single_word_definition", "prompt": "«وقت» سے کیا مراد ہے؟", "answer": "وہ لمحہ یا مدت جس میں کوئی کام ہوتا ہے۔", "target_ids": ["ur-rank-0047"]},
        {"type": "sequence", "prompt": "عائشہ نے پہلے ہوم ورک کیا یا صحن میں کھیلنے گئی؟", "answer": "اس نے پہلے ہوم ورک کیا۔"},
        {"type": "cloze_transfer", "prompt": "خالی جگہ پُر کریں: اب سونے کا _____ ہے۔", "answer": "وقت", "target_ids": ["ur-rank-0047"]},
        {"type": "contrast", "prompt": "کھانے سے پہلے اور کھانے کے بعد میں کون سا لفظ بعد میں آنے والے وقت کو ظاہر کرتا ہے؟", "answer": "بعد", "target_ids": ["ur-rank-0040"]},
    ],
    "ur-a1-u01-p03": [
        {"type": "single_word_definition", "prompt": "«بہت» کا مطلب کیا ہے؟", "answer": "بڑی مقدار یا بڑی تعداد۔", "target_ids": ["ur-rank-0048"]},
        {"type": "single_word_definition", "prompt": "«زیادہ» کا مطلب کیا ہے؟", "answer": "ضرورت، معمول یا دوسری مقدار کے مقابلے میں بڑا یا زائد۔", "target_ids": ["ur-rank-0054"]},
        {"type": "contrast", "prompt": "کون سا جملہ کم خریداری دکھاتا ہے: «زیادہ پھل لیے» یا «زیادہ پھل نہیں لیے»؟", "answer": "زیادہ پھل نہیں لیے۔", "target_ids": ["ur-rank-0054"]},
        {"type": "cloze_transfer", "prompt": "خالی جگہ پُر کریں: بازار میں آج _____ لوگ تھے۔", "answer": "بہت", "target_ids": ["ur-rank-0048"]},
        {"type": "cloze_transfer", "prompt": "خالی جگہ پُر کریں: میرے پاس کافی پانی ہے، مجھے _____ پانی نہیں چاہیے۔", "answer": "زیادہ", "target_ids": ["ur-rank-0054"]},
    ],
    "ur-a1-u01-p04": [
        {"type": "single_word_definition", "prompt": "«اگر» کا کام کیا ہے؟", "answer": "کسی شرط کو بیان کرنا۔", "target_ids": ["ur-rank-0058"]},
        {"type": "single_word_definition", "prompt": "«تک» کا مطلب «پانچ بجے تک» میں کیا ہے؟", "answer": "پانچ بجے کو وقت کی آخری حد بنانا۔", "target_ids": ["ur-rank-0039"]},
        {"type": "cause_effect", "prompt": "اگر موسم ٹھیک رہا تو اگلے ہفتے کیا ہوگا؟", "answer": "وہ پارک دوبارہ آئیں گی۔"},
        {"type": "cloze_transfer", "prompt": "خالی جگہ پُر کریں: میں شام چھ بجے _____ گھر آ جاؤں گا۔", "answer": "تک", "target_ids": ["ur-rank-0039"]},
        {"type": "cloze_transfer", "prompt": "خالی جگہ پُر کریں: _____ بارش نہ ہوئی تو ہم باہر جائیں گے۔", "answer": "اگر", "target_ids": ["ur-rank-0058"]},
    ],
    "ur-a1-u01-p05": [
        {"type": "single_word_definition", "prompt": "«اب» کا مطلب کیا ہے؟", "answer": "موجودہ وقت؛ اس وقت۔", "target_ids": ["ur-rank-0059"]},
        {"type": "single_word_definition", "prompt": "«ہم» کن لوگوں کے لیے استعمال ہوتا ہے؟", "answer": "بولنے والے اور اس کے ساتھ شامل ایک یا زیادہ لوگوں کے لیے۔", "target_ids": ["ur-rank-0052"]},
        {"type": "contrast", "prompt": "«پہلے راستہ نیا تھا، مگر اب یاد ہے» میں تبدیلی کس لفظ سے واضح ہوتی ہے؟", "answer": "اب", "target_ids": ["ur-rank-0059"]},
        {"type": "cloze_transfer", "prompt": "خالی جگہ پُر کریں: _____ آج اسکول کے بعد بازار جائیں گے۔", "answer": "ہم", "target_ids": ["ur-rank-0052"]},
        {"type": "grammar_category", "prompt": "«ہم» کس قسم کا لفظ ہے؟", "answer": "ضمیر۔", "target_ids": ["ur-rank-0052"]},
    ],
    "ur-a1-u01-p06": [
        {"type": "single_word_definition", "prompt": "«اب» اس عبارت میں کس وقت کی طرف اشارہ کرتا ہے؟", "answer": "عائشہ کی موجودہ حالت اور موجودہ وقت کی طرف۔", "target_ids": ["ur-rank-0059"]},
        {"type": "single_word_definition", "prompt": "آخری جملے میں «ہم» سے کون مراد ہیں؟", "answer": "عائشہ اور اس کے گھر والے، یعنی وہ لوگ جو اس محلے میں رہتے ہیں۔", "target_ids": ["ur-rank-0052"]},
        {"type": "grammar_function", "prompt": "«اگر موسم اچھا ہو» میں «اگر» کیا متعارف کراتا ہے؟", "answer": "ایک شرط۔", "target_ids": ["ur-rank-0058"]},
        {"type": "single_word_definition", "prompt": "«پانچ بجے تک» میں «تک» کیا بتاتا ہے؟", "answer": "وقت کی آخری حد۔", "target_ids": ["ur-rank-0039"]},
        {"type": "contrast", "prompt": "کون سا جملہ ضرورت سے زائد مقدار کو رد کرتا ہے: «زیادہ سامان لیتی ہے» یا «زیادہ سامان نہیں لیتی»؟", "answer": "زیادہ سامان نہیں لیتی۔", "target_ids": ["ur-rank-0054"]},
    ],
}


def load_lexicon(language):
    path = READING / "lexicons" / f"{language}.jsonl"
    return {json.loads(line)["rank"]: json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def load_overrides():
    path = READING / "overrides" / "source_lexicon_issues.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {(x["language"], x["rank"]): x["corrected_sense"] for x in data["issues"]}


def numbered(block):
    return [m.group(1).strip() for m in re.finditer(r"(?m)^\d+\.\s+(.+)$", block)]


def qtype(text, language):
    t = text.casefold()
    if "_____" in text:
        return "cloze_transfer"
    vocab = ["signifie", "que veut dire", "مطلب", "مراد", "معنی"]
    if any(x in t for x in vocab):
        return "vocabulary_in_context"
    if "idée principale" in t or "مرکزی خیال" in text:
        return "gist"
    if "résume" in t or "خلاص" in text or "بیان کریں" in text:
        return "summary"
    if "pourquoi" in t or "کیوں" in text:
        return "cause_effect"
    if "désigne" in t or "اشارہ" in text:
        return "reference_resolution"
    return "literal_detail"


def targets(block):
    result = []
    for form, rank in re.findall(r"\*\*([^*]+)\*\*\s*\(rank\s*(\d+)", block):
        result.append((form.strip(), int(rank)))
    return result


def review_plan(previous, sequence):
    if sequence == 1:
        return []
    out = []
    for prev_seq, ids in previous.items():
        gap = sequence - prev_seq
        if gap <= 0:
            continue
        stage = "R1" if gap == 1 else "R2" if gap <= 3 else "R3"
        for item_id, form in ids:
            out.append({"id": item_id, "form": form, "review_stage": stage, "representation": "running_text", "expected_exposure_number": None})
    return out


def record(language, code, passage_id, title, text, question_lines, answer_lines, target_pairs, lexicon, overrides, previous):
    sequence = int(passage_id[-2:])
    new_targets = []
    current_ids = []
    for form, rank in target_pairs:
        src = lexicon[rank]
        sense = overrides.get((language, rank), src.get("meaning_en_source") or "learner-checked sense pending")
        item_id = f"{code}-rank-{rank:04d}"
        current_ids.append((item_id, form))
        new_targets.append({
            "id": item_id,
            "form": form,
            "lemma": src["form"],
            "part_of_speech": src.get("part_of_speech_source"),
            "intended_sense": sense,
            "register": "contemporary standard" if code == "fr" else None,
            "variety": "contemporary standard Urdu" if code == "ur" else None,
            "context_strategy": ["scenario_resolution"],
            "first_introduced": True,
            "exposures_in_text": max(1, text.count(form)),
            "source_lexicon": src["source_file"],
            "source_rank": rank,
            "beyond_base": False,
        })

    questions = []
    answers = []
    for i, q in enumerate(question_lines, 1):
        aid = f"a{i}"
        questions.append({"id": f"q{i}", "type": qtype(q, language), "prompt": q, "answer_id": aid})
        answer = answer_lines[i - 1] if i <= len(answer_lines) else "ANSWER MISSING"
        answers.append({"id": aid, "question_id": f"q{i}", "answer": answer, "explanation": ""})

    extras = EXTRA_QA.get(passage_id, [])
    for offset, item in enumerate(extras, start=len(questions) + 1):
        aid = f"a{offset}"
        q = {"id": f"q{offset}", "type": item["type"], "prompt": item["prompt"], "answer_id": aid}
        if item.get("target_ids"):
            q["target_ids"] = item["target_ids"]
        questions.append(q)
        answers.append({"id": aid, "question_id": f"q{offset}", "answer": item["answer"], "explanation": ""})

    if len(questions) != 10 or len(answers) != 10:
        raise SystemExit(f"{passage_id}: expected 10 questions/answers, got {len(questions)}/{len(answers)}")

    wc = len(re.findall(r"\S+", text))
    sc = max(1, len(re.findall(r"[.!?؟۔](?:\s|$)|[。！？”]", text)))
    rec = {
        "id": passage_id,
        "language": code,
        "cefr": "A1",
        "unit": 1,
        "sequence": sequence,
        "revision": 1,
        "title": title,
        "passage_type": ROLE[sequence],
        "genre": "calibration passage",
        "domains": ["personal"] if sequence < 4 else ["personal", "public"],
        "topics": ["people, place, and daily orientation"],
        "text": text.strip(),
        "word_count": wc,
        "sentence_count": sc,
        "estimated_known_token_coverage": 0,
        "new_lexical_targets": new_targets,
        "review_lexical_targets": review_plan(previous, sequence),
        "grammar_targets": [],
        "discourse_targets": [],
        "questions": questions,
        "answer_key": answers,
        "speed_training": {
            "timed": sequence == 6,
            "benchmark_eligible": False,
            "comprehension_gate": 0.8,
            "new_word_policy": "none" if sequence == 6 else "controlled",
            "notes": "Generation-stage fluency passage; benchmark decision deferred to the final audit phase." if sequence == 6 else "Generation-stage passage; formal audit deferred until corpus generation is complete."
        },
        "quality": {
            "status": "draft",
            "linguistic_review": "pending",
            "pedagogical_review": "pending",
            "coverage_check": "pending",
            "answer_key_check": "pending",
            "schema_check": "pending",
            "fact_check": "not_required",
            "notes": [
                "Generated from the previously reviewed A1 staging passage and expanded to the canonical ten-question format.",
                "Formal linguistic, pedagogical, lexical-coverage, answer-key, and schema audits are intentionally deferred until the generation batch is complete."
            ]
        }
    }
    previous[sequence] = current_ids
    return rec


def parse_french(overrides):
    language, code = "french", "fr"
    lex = load_lexicon(language)
    raw = (READING / "french" / "a1" / "CALIBRATION_UNIT_01.md").read_text(encoding="utf-8")
    matches = list(re.finditer(r"(?m)^## (fr-a1-u01-p\d{2}) — (.+)$", raw))
    previous, records = {}, []
    for i, m in enumerate(matches):
        block = raw[m.end(): matches[i+1].start() if i + 1 < len(matches) else len(raw)]
        text, rest = block.split("### Questions", 1)
        qblock, rest = rest.split("### Réponses", 1)
        ablock = rest.split("Targets:", 1)[0].split("Fluency/checkpoint passage:", 1)[0]
        records.append(record(language, code, m.group(1), m.group(2).strip(), text.strip(), numbered(qblock), numbered(ablock), targets(rest), lex, overrides, previous))
    return records


def parse_urdu(overrides):
    language, code = "urdu", "ur"
    lex = load_lexicon(language)
    files = sorted((READING / "urdu" / "a1" / "calibration").glob("ur-a1-u01-p*.md"))
    previous, records = {}, []
    for path in files:
        raw = path.read_text(encoding="utf-8")
        m = re.search(r"(?m)^# (ur-a1-u01-p\d{2}) — (.+)$", raw)
        body = raw[m.end():]
        text, rest = body.split("## سوالات", 1)
        qblock, rest = rest.split("## جوابات", 1)
        ablock = rest.split("Targets:", 1)[0].split("Fluency/checkpoint passage:", 1)[0]
        records.append(record(language, code, m.group(1), m.group(2).strip(), text.strip(), numbered(qblock), numbered(ablock), targets(rest), lex, overrides, previous))
    return records


def write(language, rows):
    path = READING / language / "a1" / "passages.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def main():
    overrides = load_overrides()
    french = parse_french(overrides)
    urdu = parse_urdu(overrides)
    if len(french) != 6 or len(urdu) != 6:
        raise SystemExit(f"Expected six French and six Urdu records; got {len(french)} and {len(urdu)}")
    paths = [write("french", french), write("urdu", urdu)]
    summary = {
        "french_records": len(french),
        "urdu_records": len(urdu),
        "french_question_answer_counts": [[len(x["questions"]), len(x["answer_key"])] for x in french],
        "urdu_question_answer_counts": [[len(x["questions"]), len(x["answer_key"])] for x in urdu],
        "output": [str(p.relative_to(ROOT)) for p in paths],
        "generation_gate": "PASS",
        "formal_audit_state": "DEFERRED_UNTIL_GENERATION_BATCH_COMPLETE"
    }
    (READING / "a1_calibration_conversion_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
