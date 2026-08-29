from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CANON = ROOT / "reading/urdu/c2/passages.jsonl"
CONT = ROOT / "reading/CONTINUATION.json"
STATUS = ROOT / "reading/STATUS.json"
PLAN = ROOT / "reading/planning/ACTIVE_GENERATION_PLAN.json"
TASKS = ROOT / "reading/TASKS.md"
HANDOFF = ROOT / "reading/AGENT_HANDOFF_V2.md"
QA = ROOT / "reading/audit/urdu_c2_u01_generation_qa_2026-08-29.json"
SPECS = ROOT / "reading/tools/unit01_c2_specs.json"

UNIT = 1
START_SEQUENCE = 1
EXPECTED_EXISTING = 0
EXPECTED_PROJECT = 1020
EXPECTED_URDU = 300
NEW_PROJECT = 1026
NEW_URDU = 306
NEW_REMAINING = 54
NEXT_UNIT = 2
NEXT_SEQUENCE = 7
THEME = "philosophy and conceptual distinctions"
GENRES = ["argumentative essay", "critique", "counterexample"]
NEXT_THEME = "law and competing interpretations"
NEXT_GENRES = ["dense analysis", "case commentary", "position comparison"]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sentence_count(text):
    return max(1, len(re.findall(r"[۔؟!]+", text)))


def word_count(text):
    return len(text.split())


def make_record(spec, idx):
    seq = START_SEQUENCE + idx
    pid = f"ur-c2-u01-p{idx + 1:02d}"
    target = spec.get("target")
    new_targets = []
    if target:
        exposures = spec["text"].count(target["form"])
        if exposures < 2:
            raise SystemExit(f"Target {target['form']!r} has only {exposures} text exposures")
        new_targets = [{
            **target,
            "first_introduced": True,
            "exposures_in_text": exposures,
            "variety": "standard Urdu",
        }]

    if len(spec["questions"]) != 10 or len(spec["answers"]) != 10:
        raise SystemExit(f"{pid} must have exactly 10 questions and 10 answers")

    questions = []
    answers = []
    for n, ((qtype, prompt), answer) in enumerate(zip(spec["questions"], spec["answers"]), 1):
        q = {"id": f"q{n}", "type": qtype, "prompt": prompt, "answer_id": f"a{n}"}
        if target and n == 10:
            q["target_ids"] = [target["id"]]
        questions.append(q)
        answers.append({"id": f"a{n}", "question_id": f"q{n}", "answer": answer, "explanation": ""})

    return {
        "id": pid,
        "language": "ur",
        "cefr": "C2",
        "unit": UNIT,
        "sequence": seq,
        "revision": 1,
        "title": spec["title"],
        "passage_type": spec["passage_type"],
        "genre": spec["genre"],
        "domains": spec["domains"],
        "topics": [THEME],
        "text": spec["text"],
        "word_count": word_count(spec["text"]),
        "sentence_count": sentence_count(spec["text"]),
        "estimated_known_token_coverage": 0,
        "new_lexical_targets": new_targets,
        "review_lexical_targets": [],
        "grammar_targets": [{
            "id": "ur-c2-u01-grammar-01",
            "role": "integration",
            "description": "Use concessive, conditional, contrastive, scope-sensitive, and evidential structures to distinguish definitions, conditions, counterexamples, and normative conclusions."
        }],
        "discourse_targets": [{
            "id": "ur-c2-u01-discourse-01",
            "role": "integration",
            "description": "Track conceptual distinctions, premise types, hidden assumptions, category boundaries, counterexamples, semantic shifts, and revisions across dense philosophical argument."
        }],
        "questions": questions,
        "answer_key": answers,
        "speed_training": {
            "timed": False,
            "benchmark_eligible": False,
            "comprehension_gate": 0.8,
            "new_word_policy": "minimal" if idx == 5 else "controlled",
            "notes": "Generation-stage C2 reading passage; formal speed calibration is deferred."
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
                "Generation-stage QA only; formal educator/publication release audit is deferred.",
                "All cases, institutions, policies, and examples are explicitly hypothetical instructional constructs rather than factual claims about real entities."
            ]
        },
        "reader_tags": ["C2", "philosophy", "conceptual distinctions", "argument", "synthetic scenario"],
        "difficulty_notes_internal": "C2 generation-stage record; formal calibration pending."
    }


def validate_existing(existing, cont, status, plan):
    if len(existing) != EXPECTED_EXISTING:
        raise SystemExit(f"Expected empty Urdu C2 corpus, found {len(existing)} passages")
    if cont["production"]["canonical_passages"] != EXPECTED_PROJECT:
        raise SystemExit("CONTINUATION project count drift")
    if cont["production"]["urdu"]["canonical_passages"] != EXPECTED_URDU:
        raise SystemExit("CONTINUATION Urdu count drift")
    if "C2 Unit 1 / sequence 1" not in cont["active_frontier"]["production"]["action"]:
        raise SystemExit("CONTINUATION frontier drift")
    if status["current"]["canonical_passages"] != EXPECTED_PROJECT:
        raise SystemExit("STATUS project count drift")
    if status["languages"]["urdu"]["canonical_passages"] != EXPECTED_URDU:
        raise SystemExit("STATUS Urdu count drift")
    if status["current"]["active_language"] != "urdu" or status["current"]["active_level"] != "C2":
        raise SystemExit("STATUS active frontier drift")
    if plan["active_language"] != "urdu" or plan["active_level"] != "C2":
        raise SystemExit("ACTIVE_GENERATION_PLAN language/level drift")
    if plan["active_unit"] != UNIT or plan["start_sequence"] != START_SEQUENCE:
        raise SystemExit("ACTIVE_GENERATION_PLAN frontier drift")
    if plan.get("existing_active_level_passages") != 0:
        raise SystemExit("ACTIVE_GENERATION_PLAN expected empty C2 level")
    roadmap = plan["active_unit_roadmap"]
    if roadmap.get("theme") != THEME or roadmap.get("genres") != GENRES:
        raise SystemExit("ACTIVE_GENERATION_PLAN Unit 1 roadmap drift")


def validate_new_records(records):
    expected_types = ["instructional", "reinforcement", "interleaved", "transfer", "integration", "checkpoint"]
    if [r["passage_type"] for r in records] != expected_types:
        raise SystemExit("Unit 1 passage-role cycle drift")
    if [r["sequence"] for r in records] != list(range(1, 7)):
        raise SystemExit("Unit 1 sequences must be 1..6")
    if len({r["id"] for r in records}) != 6:
        raise SystemExit("Duplicate Unit 1 passage ids")
    for r in records:
        if r["genre"] not in GENRES:
            raise SystemExit(f"Off-roadmap genre in {r['id']}: {r['genre']}")
        if len(r["questions"]) != 10 or len(r["answer_key"]) != 10:
            raise SystemExit(f"Question/answer contract failed in {r['id']}")
        for n in range(1, 11):
            if r["questions"][n-1]["answer_id"] != f"a{n}" or r["answer_key"][n-1]["question_id"] != f"q{n}":
                raise SystemExit(f"Question/answer linkage failed in {r['id']}")
        if r["word_count"] < 400:
            raise SystemExit(f"{r['id']} is unexpectedly short at {r['word_count']} words")
        if r["sentence_count"] < 18:
            raise SystemExit(f"{r['id']} has too few sentence boundaries")
    if records[-1]["new_lexical_targets"]:
        raise SystemExit("C2 Unit 1 checkpoint must introduce no new lexical target")


def update_state(cont, status, plan):
    cont["updated"] = "2026-08-29"
    cont["production"]["canonical_passages"] = NEW_PROJECT
    cont["production"]["urdu"]["canonical_passages"] = NEW_URDU
    cont["active_frontier"]["production"]["action"] = (
        "Continue generation-first production from Urdu C2 Unit 2 / sequence 7 using the canonical roadmap and ten-question contract."
    )
    cont["exact_next_actions"] = [
        "Validate the routed state bundle and live canonical counts.",
        "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu C2 Unit 2 generation at sequence 7.",
        "Keep release/educator verification separate from generation progress."
    ]

    status["updated"] = "2026-08-29"
    status["current"]["canonical_passages"] = NEW_PROJECT
    status["current"]["remaining_generation_passages"] = NEW_REMAINING
    status["languages"]["urdu"]["canonical_passages"] = NEW_URDU
    status["languages"]["urdu"]["remaining_generation_passages"] = NEW_REMAINING

    plan["active_unit"] = NEXT_UNIT
    plan["start_sequence"] = NEXT_SEQUENCE
    plan["existing_active_level_passages"] = 6
    plan["active_unit_roadmap"] = {
        "unit": NEXT_UNIT,
        "theme": NEXT_THEME,
        "genres": NEXT_GENRES
    }


def replace_required(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Could not find expected {label} text")
    return text.replace(old, new)


def update_markdown():
    tasks = TASKS.read_text(encoding="utf-8")
    tasks = re.sub(r"^Updated: .*?$", "Updated: 2026-08-29", tasks, count=1, flags=re.M)
    tasks = replace_required(tasks,
        "Canonical production frontier: **Urdu C2, Unit 1, sequence 1**.",
        "Canonical production frontier: **Urdu C2, Unit 2, sequence 7**.",
        "TASKS frontier")
    tasks = replace_required(tasks,
        "Read `reading/planning/ACTIVE_GENERATION_PLAN.json` and the exact C1 entry in `reading/planning/topic_genre_matrix.json`.",
        "Read `reading/planning/ACTIVE_GENERATION_PLAN.json` and the exact C2 entry in `reading/planning/topic_genre_matrix.json`.",
        "TASKS roadmap-level wording")
    tasks = replace_required(tasks,
        "Generate Urdu C1 in guarded unit or large bounded batches under the generation-first policy.",
        "Generate Urdu C2 in guarded unit or large bounded batches under the generation-first policy.",
        "TASKS generation-level wording")
    tasks = replace_required(tasks,
        "- Urdu: 300/360 generated; A1-C1 complete, C2 in progress.",
        "- Urdu: 306/360 generated; A1-C1 complete, C2 in progress.",
        "TASKS Urdu total")
    tasks = replace_required(tasks,
        "- Project: 1020/1080 generated.",
        "- Project: 1026/1080 generated.",
        "TASKS project total")
    TASKS.write_text(tasks, encoding="utf-8")

    handoff = HANDOFF.read_text(encoding="utf-8")
    handoff = re.sub(r"^Updated: .*?$", "Updated: 2026-08-29", handoff, count=1, flags=re.M)
    handoff = replace_required(handoff,
        "- Canonical generated total: **1020**.",
        "- Canonical generated total: **1026**.",
        "handoff project total")
    handoff = replace_required(handoff,
        "- Urdu: **300/360**; A1-C1 generation complete and C2 generation in progress.",
        "- Urdu: **306/360**; A1-C1 generation complete and C2 generation in progress.",
        "handoff Urdu total")
    handoff = replace_required(handoff,
        "Continue **Urdu C2**, starting from Unit 1 / sequence 1, under:",
        "Continue **Urdu C2**, starting from Unit 2 / sequence 7, under:",
        "handoff frontier")
    handoff = replace_required(handoff,
        "C2 Unit 1 uses the roadmap theme **philosophy and conceptual distinctions** with `argumentative essay`, `critique`, and `counterexample` genres.",
        "C2 Unit 2 uses the roadmap theme **law and competing interpretations** with `dense analysis`, `case commentary`, and `position comparison` genres.",
        "handoff roadmap")
    handoff = replace_required(handoff,
        "Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu C2 Unit 1 / sequence 1** using the C2 Unit 1 roadmap theme `philosophy and conceptual distinctions`.",
        "Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu C2 Unit 2 / sequence 7** using the C2 Unit 2 roadmap theme `law and competing interpretations`.",
        "handoff exact next action")
    HANDOFF.write_text(handoff, encoding="utf-8")


def main():
    subprocess.run([sys.executable, "reading/tools/validate_continuation_state.py"], cwd=ROOT, check=True)

    existing = []
    if CANON.exists():
        existing = [json.loads(line) for line in CANON.read_text(encoding="utf-8").splitlines() if line.strip()]
    cont = load_json(CONT)
    status = load_json(STATUS)
    plan = load_json(PLAN)
    validate_existing(existing, cont, status, plan)

    specs = load_json(SPECS)
    if len(specs) != 6:
        raise SystemExit(f"Expected 6 C2 Unit 1 specs, found {len(specs)}")
    records = [make_record(spec, idx) for idx, spec in enumerate(specs)]
    validate_new_records(records)

    CANON.parent.mkdir(parents=True, exist_ok=True)
    with CANON.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    update_state(cont, status, plan)
    dump_json(CONT, cont)
    dump_json(STATUS, status)
    dump_json(PLAN, plan)
    update_markdown()

    qa = {
        "project_id": "LANG-A1C2",
        "language": "urdu",
        "level": "C2",
        "unit": UNIT,
        "sequences": list(range(1, 7)),
        "passage_ids": [r["id"] for r in records],
        "theme": THEME,
        "genres": [r["genre"] for r in records],
        "canonicalization_status": "CANONICAL_APPEND_CONFIRMED",
        "canonical_passage_count": 6,
        "project_canonical_passages": NEW_PROJECT,
        "urdu_canonical_passages": NEW_URDU,
        "remaining_generation_passages": NEW_REMAINING,
        "new_target_ids": [t["id"] for r in records for t in r["new_lexical_targets"]],
        "word_counts": [r["word_count"] for r in records],
        "questions_per_passage": 10,
        "answers_per_passage": 10,
        "hard_errors": 0,
        "formal_release_audit": "DEFERRED",
        "release_claim": False,
        "next_frontier": "Urdu C2 Unit 2 / sequence 7",
        "notes": [
            "All six passages use explicitly hypothetical philosophical and institutional scenarios; no factual real-world claim is asserted.",
            "Five specialist Unit 1 lexical targets are marked beyond_base rather than assigned invented frequency ranks; the checkpoint introduces no new lexical target.",
            "Generation-stage QA preserves the six-role progression and ten-question/ten-answer contract while keeping educator/publication release review separate."
        ]
    }
    dump_json(QA, qa)

    subprocess.run([sys.executable, "reading/tools/refresh_state_manifest.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "reading/tools/validate_continuation_state.py"], cwd=ROOT, check=True)

    print(json.dumps({
        "status": "ok",
        "appended": 6,
        "urdu_c2_passages": 6,
        "project_passages": NEW_PROJECT,
        "next_frontier": "Urdu C2 Unit 2 / sequence 7"
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
