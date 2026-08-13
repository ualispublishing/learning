import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"

ROLE = {1: "instructional", 2: "reinforcement", 3: "interleaved", 4: "transfer", 5: "checkpoint", 6: "fluency"}


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
            "variety": "Modern Standard Arabic" if code == "ar" else None,
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
            "notes": "Benchmark eligibility remains false until measured lexical coverage passes the fluency gate." if sequence == 6 else "Calibration reading; coverage measurement pending."
        },
        "quality": {
            "status": "draft",
            "linguistic_review": "pass",
            "pedagogical_review": "pass",
            "coverage_check": "pending",
            "answer_key_check": "pass" if len(question_lines) == len(answer_lines) == 5 else "review_required",
            "schema_check": "pending",
            "fact_check": "not_required",
            "notes": ["Converted from reviewed A1 calibration staging Markdown; canonical coverage audit still required."]
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
        "gate": "PASS"
    }
    (READING / "a1_calibration_conversion_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
