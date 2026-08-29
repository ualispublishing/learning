from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CANON = ROOT / "reading/urdu/c1/passages.jsonl"
CONT = ROOT / "reading/CONTINUATION.json"
STATUS = ROOT / "reading/STATUS.json"
PLAN = ROOT / "reading/planning/ACTIVE_GENERATION_PLAN.json"
TASKS = ROOT / "reading/TASKS.md"
HANDOFF = ROOT / "reading/AGENT_HANDOFF_V2.md"
QA = ROOT / "reading/audit/urdu_c1_u10_generation_qa_2026-08-29.json"
SPECS = ROOT / "reading/tools/unit10_specs.json"

UNIT = 10
START_SEQUENCE = 55
EXPECTED_EXISTING = 54
EXPECTED_PROJECT = 1014
EXPECTED_URDU = 294
NEW_PROJECT = 1020
NEW_URDU = 300
NEW_REMAINING = 60
THEME = "C1 synthesis"
GENRES = ["multi-section essay", "paired perspectives", "checkpoint"]
NEXT_LEVEL = "C2"
NEXT_UNIT = 1
NEXT_SEQUENCE = 1
NEXT_THEME = "philosophy and conceptual distinctions"
NEXT_GENRES = ["argumentative essay", "critique", "counterexample"]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def word_count(text):
    return len(text.split())


def sentence_count(text):
    return max(1, len(re.findall(r"[۔؟!]+", text)))


def make_record(spec, idx):
    seq = START_SEQUENCE + idx
    pid = f"ur-c1-u10-p{idx + 1:02d}"
    target = spec.get("target")
    new_targets = []
    if target:
        exposures = spec["text"].count(target["form"])
        if exposures < 2:
            raise SystemExit(f"Target {target['form']!r} has only {exposures} text exposures")
        new_targets = [{**target, "first_introduced": True, "exposures_in_text": exposures, "variety": "standard Urdu"}]

    if len(spec["questions"]) != 10 or len(spec["answers"]) != 10:
        raise SystemExit(f"{pid} must have exactly 10 questions and 10 answers")

    questions, answers = [], []
    for n, ((qtype, prompt), answer) in enumerate(zip(spec["questions"], spec["answers"]), 1):
        q = {"id": f"q{n}", "type": qtype, "prompt": prompt, "answer_id": f"a{n}"}
        if target and n == 10:
            q["target_ids"] = [target["id"]]
        questions.append(q)
        answers.append({"id": f"a{n}", "question_id": f"q{n}", "answer": answer, "explanation": ""})

    return {
        "id": pid,
        "language": "ur",
        "cefr": "C1",
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
            "id": "ur-c1-u10-grammar-01",
            "role": "integration",
            "description": "Use conditional, concessive, evidential, contrastive, and modal structures to calibrate claims across evidence, values, interpretation, and uncertainty."
        }],
        "discourse_targets": [{
            "id": "ur-c1-u10-discourse-01",
            "role": "integration",
            "description": "Synthesize multiple perspectives, evidence streams, institutional incentives, interpretive frames, risks, and limits into a coherent C1-level judgment."
        }],
        "questions": questions,
        "answer_key": answers,
        "speed_training": {
            "timed": False,
            "benchmark_eligible": False,
            "comprehension_gate": 0.8,
            "new_word_policy": "minimal" if idx == 5 else "controlled",
            "notes": "Generation-stage C1 synthesis passage; formal speed calibration is deferred."
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
                "People, institutions, policies, records, programs, and disputes in this unit are explicitly hypothetical instructional constructs."
            ]
        },
        "reader_tags": ["C1", "synthesis", "evidence", "judgment", "synthetic scenario"],
        "difficulty_notes_internal": "C1 synthesis generation-stage record; formal calibration pending."
    }


def validate_existing(existing, cont, status, plan):
    if len(existing) != EXPECTED_EXISTING:
        raise SystemExit(f"Expected {EXPECTED_EXISTING} existing Urdu C1 passages, found {len(existing)}")
    if [p.get("sequence") for p in existing] != list(range(1, EXPECTED_EXISTING + 1)):
        raise SystemExit("Existing Urdu C1 sequence is not exactly 1..54")
    if existing[-1].get("id") != "ur-c1-u09-p06":
        raise SystemExit(f"Unexpected Urdu C1 tail id: {existing[-1].get('id')}")
    if cont["production"]["canonical_passages"] != EXPECTED_PROJECT or cont["production"]["urdu"]["canonical_passages"] != EXPECTED_URDU:
        raise SystemExit("CONTINUATION count drift")
    if status["current"]["canonical_passages"] != EXPECTED_PROJECT or status["languages"]["urdu"]["canonical_passages"] != EXPECTED_URDU:
        raise SystemExit("STATUS count drift")
    if "Unit 10 / sequence 55" not in cont["active_frontier"]["production"]["action"]:
        raise SystemExit("CONTINUATION frontier drift")
    if plan["active_language"] != "urdu" or plan["active_level"] != "C1" or plan["active_unit"] != UNIT or plan["start_sequence"] != START_SEQUENCE:
        raise SystemExit("ACTIVE_GENERATION_PLAN frontier drift")
    roadmap = plan["active_unit_roadmap"]
    if roadmap.get("theme") != THEME or roadmap.get("genres") != GENRES:
        raise SystemExit("ACTIVE_GENERATION_PLAN Unit 10 roadmap drift")


def validate_new_records(records):
    expected_types = ["instructional", "reinforcement", "interleaved", "transfer", "integration", "checkpoint"]
    if [r["passage_type"] for r in records] != expected_types:
        raise SystemExit("Unit 10 passage-role cycle drift")
    if [r["sequence"] for r in records] != list(range(55, 61)):
        raise SystemExit("Unit 10 sequences must be 55..60")
    if len({r["id"] for r in records}) != 6:
        raise SystemExit("Duplicate Unit 10 passage ids")
    for r in records:
        if r["genre"] not in GENRES:
            raise SystemExit(f"Off-roadmap genre in {r['id']}: {r['genre']}")
        if len(r["questions"]) != 10 or len(r["answer_key"]) != 10:
            raise SystemExit(f"Question/answer contract failed in {r['id']}")
        for n in range(1, 11):
            if r["questions"][n - 1]["answer_id"] != f"a{n}" or r["answer_key"][n - 1]["question_id"] != f"q{n}":
                raise SystemExit(f"Question/answer linkage failed in {r['id']}")
        if r["word_count"] < 350:
            raise SystemExit(f"{r['id']} is unexpectedly short at {r['word_count']} words")
        if r["sentence_count"] < 15:
            raise SystemExit(f"{r['id']} has too few sentence boundaries at {r['sentence_count']}")


def update_state(cont, status, plan):
    cont["updated"] = "2026-08-29"
    cont["production"]["canonical_passages"] = NEW_PROJECT
    u = cont["production"]["urdu"]
    u["state"] = "C2_GENERATION_IN_PROGRESS"
    u["canonical_passages"] = NEW_URDU
    u["complete_levels"] = ["A1", "A2", "B1", "B2", "C1"]
    u["next_generation_level"] = "C2"
    cont["active_frontier"]["production"] = {
        "language": "urdu",
        "level": "C2",
        "action": "Continue generation-first production from Urdu C2 Unit 1 / sequence 1 using the canonical roadmap and ten-question contract."
    }
    cont["exact_next_actions"] = [
        "Validate the routed state bundle and live canonical counts.",
        "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu C2 Unit 1 generation at sequence 1.",
        "Keep release/educator verification separate from generation progress."
    ]

    status["updated"] = "2026-08-29"
    status["current"]["canonical_passages"] = NEW_PROJECT
    status["current"]["remaining_generation_passages"] = NEW_REMAINING
    status["current"]["active_level"] = "C2"
    su = status["languages"]["urdu"]
    su["generation_state"] = "C2_IN_PROGRESS"
    su["canonical_passages"] = NEW_URDU
    su["remaining_generation_passages"] = NEW_REMAINING
    su["complete_levels"] = ["A1", "A2", "B1", "B2", "C1"]
    su["next_generation_level"] = "C2"

    plan["active_level"] = "C2"
    plan["active_unit"] = NEXT_UNIT
    plan["start_sequence"] = NEXT_SEQUENCE
    plan["canonical_active_path"] = "reading/urdu/c2/passages.jsonl"
    plan["existing_active_level_passages"] = 0
    plan["roadmap_lookup"] = "$.levels.C2"
    plan["active_unit_roadmap"] = {"unit": 1, "theme": NEXT_THEME, "genres": NEXT_GENRES}


def update_markdown():
    tasks = TASKS.read_text(encoding="utf-8")
    tasks = re.sub(r"^Updated: .*?$", "Updated: 2026-08-29", tasks, count=1, flags=re.M)
    tasks = re.sub(r"Canonical production frontier: \*\*Urdu C1, Unit 10, sequence 55\*\*\.", "Canonical production frontier: **Urdu C2, Unit 1, sequence 1**.", tasks, count=1)
    tasks = re.sub(r"- Urdu: 294/360 generated; A1-B2 complete, C1 in progress\.", "- Urdu: 300/360 generated; A1-C1 complete, C2 in progress.", tasks, count=1)
    tasks = re.sub(r"- Project: 1014/1080 generated\.", "- Project: 1020/1080 generated.", tasks, count=1)
    tasks = re.sub(r"## P1 — active production: Urdu C1", "## P1 — active production: Urdu C2", tasks, count=1)
    TASKS.write_text(tasks, encoding="utf-8")

    handoff = HANDOFF.read_text(encoding="utf-8")
    handoff = re.sub(r"^Updated: .*?$", "Updated: 2026-08-29", handoff, count=1, flags=re.M)
    handoff = re.sub(r"- Canonical generated total: \*\*1014\*\*\.", "- Canonical generated total: **1020**.", handoff, count=1)
    handoff = re.sub(r"- Urdu: \*\*294/360\*\*; A1-B2 generation complete and C1 generation in progress\.", "- Urdu: **300/360**; A1-C1 generation complete and C2 generation in progress.", handoff, count=1)
    handoff = re.sub(r"Continue \*\*Urdu C1\*\*, starting from Unit 10 / sequence 55, under:", "Continue **Urdu C2**, starting from Unit 1 / sequence 1, under:", handoff, count=1)
    handoff = re.sub(r"C1 Unit 10 uses the roadmap theme \*\*C1 synthesis\*\* with `multi-section essay`, `paired perspectives`, and `checkpoint` genres\.", "C2 Unit 1 uses the roadmap theme **philosophy and conceptual distinctions** with `argumentative essay`, `critique`, and `counterexample` genres.", handoff, count=1)
    handoff = re.sub(r"Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at \*\*Urdu C1 Unit 10 / sequence 55\*\* using the C1 Unit 10 roadmap theme `C1 synthesis`\.", "Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu C2 Unit 1 / sequence 1** using the C2 Unit 1 roadmap theme `philosophy and conceptual distinctions`.", handoff, count=1)
    HANDOFF.write_text(handoff, encoding="utf-8")


def main():
    subprocess.run([sys.executable, "reading/tools/validate_continuation_state.py"], cwd=ROOT, check=True)
    existing = [json.loads(line) for line in CANON.read_text(encoding="utf-8").splitlines() if line.strip()]
    cont, status, plan = load_json(CONT), load_json(STATUS), load_json(PLAN)
    validate_existing(existing, cont, status, plan)

    specs = load_json(SPECS)
    if len(specs) != 6:
        raise SystemExit(f"Expected 6 Unit 10 specs, found {len(specs)}")
    records = [make_record(spec, idx) for idx, spec in enumerate(specs)]
    validate_new_records(records)

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
        "level": "C1",
        "unit": 10,
        "sequences": list(range(55, 61)),
        "passage_ids": [r["id"] for r in records],
        "theme": THEME,
        "genres": [r["genre"] for r in records],
        "canonicalization_status": "CANONICAL_APPEND_CONFIRMED",
        "canonical_passage_count": 60,
        "level_generation_state": "C1_GENERATION_COMPLETE",
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
        "next_frontier": "Urdu C2 Unit 1 / sequence 1",
        "notes": [
            "All six passages are explicitly hypothetical C1 synthesis scenarios; no factual real-world claim is asserted.",
            "Five specialist synthesis targets are marked beyond_base rather than assigned invented frequency ranks; the checkpoint introduces no new lexical target.",
            "C1 generation completion advances production to C2 but does not imply educator/publication release readiness."
        ]
    }
    dump_json(QA, qa)

    subprocess.run([sys.executable, "reading/tools/refresh_state_manifest.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "reading/tools/validate_continuation_state.py"], cwd=ROOT, check=True)
    print(json.dumps({
        "status": "ok",
        "appended": 6,
        "urdu_c1_passages": 60,
        "project_passages": NEW_PROJECT,
        "next_frontier": "Urdu C2 Unit 1 / sequence 1"
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
