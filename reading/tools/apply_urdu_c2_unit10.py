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
QA = ROOT / "reading/audit/urdu_c2_u10_generation_qa_2026-08-30.json"
SPECS_DIR = ROOT / "reading/tools/c2_unit10_specs"

UNIT = 10
START_SEQUENCE = 55
EXPECTED_EXISTING = 54
EXPECTED_PROJECT = 1074
EXPECTED_URDU = 354
NEW_PROJECT = 1080
NEW_URDU = 360
NEW_REMAINING = 0
THEME = "C2 capstone"
GENRES = ["multi-source-style synthesis", "complex paired texts", "final checkpoint"]
EXPECTED_TAIL = "ur-c2-u09-p06"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def word_count(text):
    return len(text.split())


def sentence_count(text):
    return max(1, len(re.findall(r"[۔؟!]+", text)))


def load_specs():
    files = sorted(SPECS_DIR.glob("p*.json"))
    if len(files) != 6:
        raise SystemExit(f"Expected 6 C2 Unit 10 spec files, found {len(files)}")
    return [load_json(path) for path in files]


def make_record(spec, idx):
    seq = START_SEQUENCE + idx
    pid = f"ur-c2-u10-p{idx + 1:02d}"
    target = spec.get("target")
    new_targets = []
    if target:
        exposures = spec["text"].count(target["form"])
        if exposures < 2:
            raise SystemExit(f"Target {target['form']!r} has only {exposures} text exposures")
        if target.get("beyond_base") is not True:
            raise SystemExit(f"Specialist target {target['form']!r} must use beyond_base=true")
        if "frequency_rank" in target:
            raise SystemExit(f"Specialist target {target['form']!r} must not invent a frequency rank")
        new_targets = [{**target, "first_introduced": True, "exposures_in_text": exposures, "variety": "standard Urdu"}]

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
            "id": "ur-c2-u10-grammar-01",
            "role": "integration",
            "description": "Use concessive, evidential, comparative, counterfactual, scope-sensitive, and qualification structures to synthesize competing claims without overstating certainty."
        }],
        "discourse_targets": [{
            "id": "ur-c2-u10-discourse-01",
            "role": "integration",
            "description": "Integrate multiple synthetic sources while preserving source function, evidence weight, claim limits, perspective shifts, uncertainty, ethical trade-offs, alternative explanations, and revision conditions."
        }],
        "questions": questions,
        "answer_key": answers,
        "speed_training": {
            "timed": False,
            "benchmark_eligible": False,
            "comprehension_gate": 0.8,
            "new_word_policy": "minimal" if idx == 5 else "controlled",
            "notes": "Generation-stage C2 capstone passage; formal speed calibration is deferred."
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
                "Generation-stage QA only; formal educator/publication release audit is separate and not implied by generation completion.",
                "All reports, institutions, quotations, historical analogies, technologies, translations, data, and outcomes are original hypothetical instructional constructs; no current factual claim or sourced quotation is asserted."
            ]
        },
        "reader_tags": ["C2", "capstone", "multi-source synthesis", "critical reading", "synthetic scenario"],
        "difficulty_notes_internal": "Final C2 generation-stage record; formal educator calibration and release review remain pending."
    }


def validate_existing(existing, cont, status, plan):
    if len(existing) != EXPECTED_EXISTING:
        raise SystemExit(f"Expected {EXPECTED_EXISTING} existing Urdu C2 passages, found {len(existing)}")
    if [p.get("sequence") for p in existing] != list(range(1, EXPECTED_EXISTING + 1)):
        raise SystemExit("Existing Urdu C2 sequence is not exactly 1..54")
    if existing[-1].get("id") != EXPECTED_TAIL:
        raise SystemExit(f"Unexpected Urdu C2 tail id: {existing[-1].get('id')}")
    if cont["production"]["canonical_passages"] != EXPECTED_PROJECT or cont["production"]["urdu"]["canonical_passages"] != EXPECTED_URDU:
        raise SystemExit("CONTINUATION production count drift")
    if "C2 Unit 10 / sequence 55" not in cont["active_frontier"]["production"]["action"]:
        raise SystemExit("CONTINUATION frontier drift")
    if status["current"]["canonical_passages"] != EXPECTED_PROJECT or status["languages"]["urdu"]["canonical_passages"] != EXPECTED_URDU:
        raise SystemExit("STATUS production count drift")
    if status["current"]["remaining_generation_passages"] != 6 or status["languages"]["urdu"]["remaining_generation_passages"] != 6:
        raise SystemExit("STATUS remaining-generation count drift")
    if status["current"]["active_language"] != "urdu" or status["current"]["active_level"] != "C2":
        raise SystemExit("STATUS active frontier drift")
    if plan["active_language"] != "urdu" or plan["active_level"] != "C2" or plan["active_unit"] != UNIT or plan["start_sequence"] != START_SEQUENCE:
        raise SystemExit("ACTIVE_GENERATION_PLAN frontier drift")
    if plan.get("existing_active_level_passages") != EXPECTED_EXISTING:
        raise SystemExit("ACTIVE_GENERATION_PLAN existing passage count drift")
    roadmap = plan["active_unit_roadmap"]
    if roadmap.get("theme") != THEME or roadmap.get("genres") != GENRES:
        raise SystemExit("ACTIVE_GENERATION_PLAN Unit 10 roadmap drift")


def validate_new_records(records):
    expected_types = ["instructional", "reinforcement", "interleaved", "transfer", "integration", "checkpoint"]
    expected_genres = [
        "multi-source-style synthesis",
        "complex paired texts",
        "multi-source-style synthesis",
        "complex paired texts",
        "multi-source-style synthesis",
        "final checkpoint",
    ]
    if [r["passage_type"] for r in records] != expected_types:
        raise SystemExit("Unit 10 passage-role cycle drift")
    if [r["sequence"] for r in records] != list(range(55, 61)):
        raise SystemExit("Unit 10 sequences must be 55..60")
    if [r["genre"] for r in records] != expected_genres:
        raise SystemExit("Unit 10 genre progression drift")
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
        if r["word_count"] < 400:
            raise SystemExit(f"{r['id']} is unexpectedly short at {r['word_count']} words")
        if r["sentence_count"] < 18:
            raise SystemExit(f"{r['id']} has too few sentence boundaries at {r['sentence_count']}")
    if records[-1]["new_lexical_targets"]:
        raise SystemExit("C2 Unit 10 final checkpoint must introduce no new lexical target")
    if any(len(r["new_lexical_targets"]) != 1 for r in records[:5]):
        raise SystemExit("C2 Unit 10 first five passages must each introduce exactly one specialist target")


def replace_required(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Could not find expected {label} text")
    return text.replace(old, new, 1)


def update_state(cont, status, plan):
    cont["updated"] = "2026-08-30"
    cont["production"]["canonical_passages"] = NEW_PROJECT
    urdu_cont = cont["production"]["urdu"]
    urdu_cont["state"] = "GENERATION_COMPLETE"
    urdu_cont["canonical_passages"] = NEW_URDU
    if "C2" not in urdu_cont["complete_levels"]:
        urdu_cont["complete_levels"].append("C2")
    urdu_cont["next_generation_level"] = None
    cont["active_frontier"]["production"] = {
        "language": None,
        "level": None,
        "action": "Canonical generation complete at 1080/1080 across Arabic, French, and Urdu A1-C2. Proceed only with separate verification/release workstreams unless fresh evidence identifies a concrete production defect."
    }
    cont["exact_next_actions"] = [
        "Validate the routed state bundle and exact 1080/1080 canonical counts.",
        "Continue the independent Arabic, French, and Urdu educator-release workstreams under reading/RELEASE_STATUS.json and reading/VERIFICATION_TASKS.md.",
        "Use reading/planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md for final review; do not infer release readiness from generation completion."
    ]

    status["updated"] = "2026-08-30"
    status["current"]["canonical_passages"] = NEW_PROJECT
    status["current"]["remaining_generation_passages"] = NEW_REMAINING
    status["current"]["active_language"] = None
    status["current"]["active_level"] = None
    status["current"]["active_generation_plan"] = None
    urdu_status = status["languages"]["urdu"]
    urdu_status["generation_state"] = "COMPLETE"
    urdu_status["canonical_passages"] = NEW_URDU
    urdu_status["remaining_generation_passages"] = NEW_REMAINING
    if "C2" not in urdu_status["complete_levels"]:
        urdu_status["complete_levels"].append("C2")
    urdu_status["next_generation_level"] = None

    plan["state_type"] = "GENERATION_COMPLETE"
    plan["active_language"] = None
    plan["active_level"] = None
    plan["active_unit"] = None
    plan["start_sequence"] = None
    plan["canonical_active_path"] = None
    plan["existing_active_level_passages"] = 60
    plan["roadmap_lookup"] = None
    plan["active_unit_roadmap"] = None
    plan["generation_first"] = False
    plan["formal_release_audits_deferred_during_ordinary_generation"] = False
    plan["generation_complete"] = True
    plan["completion_summary"] = {
        "canonical_passages": NEW_PROJECT,
        "arabic": 360,
        "french": 360,
        "urdu": 360,
        "remaining_generation_passages": 0,
        "completed_level": "Urdu C2",
        "final_sequence": 60,
        "release_claim": False
    }
    plan["guardrails"] = [
        "STATUS.json, CONTINUATION.json, and this plan must agree that there is no active generation language or level.",
        "Live canonical JSONL must total exactly 1080 passages: 360 Arabic, 360 French, and 360 Urdu.",
        "Generation completion must never be interpreted as educator/publication release approval.",
        "Do not reopen canonical production unless fresh evidence identifies a concrete defect requiring bounded repair.",
        "Release and educator verification are controlled by RELEASE_STATUS.json, VERIFICATION_TASKS.md, and the final review protocol."
    ]
    plan["on_frontier_change"] = [
        "There is no next generation frontier after the completed 1080/1080 corpus.",
        "If a concrete defect later changes canonical production, reconcile CONTINUATION.json, STATUS.json, this plan, TASKS.md, AGENT_HANDOFF_V2.md, and STATE_MANIFEST.json in the same bounded repair."
    ]


def update_markdown():
    tasks = TASKS.read_text(encoding="utf-8")
    tasks = replace_required(tasks, "Updated: 2026-08-29", "Updated: 2026-08-30", "TASKS date")
    old_block = """## P1 — active production: Urdu C2

Canonical production frontier: **Urdu C2, Unit 10, sequence 55**.

- [ ] Read `reading/planning/ACTIVE_GENERATION_PLAN.json` and the exact C2 entry in `reading/planning/topic_genre_matrix.json`.
- [ ] Generate Urdu C2 in guarded unit or large bounded batches under the generation-first policy.
- [ ] Preserve 6 passages per unit and the active 10-question/10-answer contract unless a documented pedagogical exception is necessary.
- [ ] Write independent natural contemporary Urdu; do not translate Arabic/French passage-by-passage.
- [ ] Independently learner-check every deliberately taught lexical sense before assessing that sense in a question.
- [ ] Fix obvious severe defects immediately, but do not interrupt ordinary generation with repeated whole-corpus release audits.
- [ ] After each canonical batch, update the live production state files in the same work unit.

Current production totals:

- Arabic: 360/360 generated.
- French: 360/360 generated.
- Urdu: 354/360 generated; A1-C1 complete, C2 in progress.
- Project: 1074/1080 generated.
"""
    new_block = """## P1 — canonical generation complete

There is **no active production frontier**. Arabic, French, and Urdu A1-C2 canonical generation is complete at **1080/1080**.

- [x] Arabic: 360/360 generated.
- [x] French: 360/360 generated.
- [x] Urdu: 360/360 generated; A1-C2 complete.
- [x] Project: 1080/1080 generated.
- [ ] Do not reopen canonical generation unless fresh evidence identifies a concrete defect requiring bounded repair.
- [ ] Keep all educator/publication release claims under the independent release/verification workstreams below.
"""
    tasks = replace_required(tasks, old_block, new_block, "TASKS completed production block")
    tasks = tasks.replace("- exactly one current production frontier;", "- no active production frontier after generation completion;", 1)
    tasks = tasks.replace("- exactly one explicit next production action;", "- exactly one explicit next verification/release action;", 1)
    TASKS.write_text(tasks, encoding="utf-8")

    handoff = HANDOFF.read_text(encoding="utf-8")
    handoff = replace_required(handoff, "Updated: 2026-08-29", "Updated: 2026-08-30", "handoff date")
    handoff = replace_required(handoff, "- Canonical generated total: **1074**.", "- Canonical generated total: **1080/1080**; canonical generation complete.", "handoff project total")
    handoff = replace_required(handoff, "- Urdu: **354/360**; A1-C1 generation complete and C2 generation in progress.", "- Urdu: **360/360**; A1-C2 generation complete.", "handoff Urdu total")
    old_frontier = """## Active production frontier

Continue **Urdu C2**, starting from Unit 10 / sequence 55, under:

- `reading/planning/ACTIVE_GENERATION_PLAN.json`
- `reading/planning/topic_genre_matrix.json`
- `reading/planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md`
- `reading/planning/TEN_QUESTION_STANDARD.md`
- `reading/schema/passage.schema.json`

C2 Unit 10 uses the roadmap theme **C2 capstone** with `multi-source-style synthesis`, `complex paired texts`, and `final checkpoint` genres.

Generate in guarded unit or large bounded batches. Do not reopen Urdu A1 generation unless fresh evidence identifies a concrete defect.
"""
    new_frontier = """## Production generation status

Canonical generation is **complete**: Arabic, French, and Urdu each contain 360 passages across A1-C2, for **1080/1080** total. There is no Unit 11 or other active generation frontier.

Do not reopen canonical production unless fresh evidence identifies a concrete defect requiring a bounded repair. Generation completion is not educator/publication approval; continue only the independent release/verification lanes below under `reading/RELEASE_STATUS.json`, `reading/VERIFICATION_TASKS.md`, and `reading/planning/FINAL_REVIEW_EXECUTION_PROTOCOL.md`.
"""
    handoff = replace_required(handoff, old_frontier, new_frontier, "handoff production frontier block")
    handoff = replace_required(
        handoff,
        "Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu C2 Unit 10 / sequence 55** using the C2 capstone roadmap.",
        "Run `python reading/tools/validate_continuation_state.py`; if it passes, preserve the completed 1080/1080 production corpus and continue the separate educator-release workstreams under `reading/RELEASE_STATUS.json` and `reading/VERIFICATION_TASKS.md`.",
        "handoff exact next action"
    )
    HANDOFF.write_text(handoff, encoding="utf-8")


def main():
    subprocess.run([sys.executable, "reading/tools/validate_continuation_state.py"], cwd=ROOT, check=True)
    existing = [json.loads(line) for line in CANON.read_text(encoding="utf-8").splitlines() if line.strip()]
    cont, status, plan = load_json(CONT), load_json(STATUS), load_json(PLAN)
    validate_existing(existing, cont, status, plan)

    records = [make_record(spec, idx) for idx, spec in enumerate(load_specs())]
    validate_new_records(records)

    with CANON.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

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
        "sequences": list(range(55, 61)),
        "passage_ids": [r["id"] for r in records],
        "theme": THEME,
        "genres": [r["genre"] for r in records],
        "canonicalization_status": "CANONICAL_APPEND_CONFIRMED",
        "canonical_passage_count": 60,
        "project_canonical_passages": NEW_PROJECT,
        "urdu_canonical_passages": NEW_URDU,
        "remaining_generation_passages": NEW_REMAINING,
        "generation_complete": True,
        "new_target_ids": [t["id"] for r in records for t in r["new_lexical_targets"]],
        "word_counts": [r["word_count"] for r in records],
        "sentence_counts": [r["sentence_count"] for r in records],
        "questions_per_passage": 10,
        "answers_per_passage": 10,
        "hard_errors": 0,
        "formal_release_audit": "DEFERRED_TO_POST_GENERATION_REVIEW",
        "release_claim": False,
        "next_frontier": "GENERATION_COMPLETE — verification/release workstreams only",
        "notes": [
            "All six capstone passages use original hypothetical sources and scenarios; no current factual claim or sourced quotation is asserted.",
            "Five specialist capstone lexical targets are marked beyond_base rather than assigned invented frequency ranks; the final checkpoint introduces no new lexical target.",
            "Canonical generation is complete at 1080/1080, but this production milestone does not imply educator/publication release readiness."
        ]
    }
    dump_json(QA, qa)

    subprocess.run([sys.executable, "reading/tools/refresh_state_manifest.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "reading/tools/validate_continuation_state.py"], cwd=ROOT, check=True)

    final = [json.loads(line) for line in CANON.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(final) != 60 or final[-1].get("id") != "ur-c2-u10-p06" or final[-1].get("sequence") != 60:
        raise SystemExit("Final Urdu C2 canonical tail/count verification failed")
    print("Canonical Urdu C2 Unit 10 appended and LANG-A1C2 generation completed at 1080/1080.")


if __name__ == "__main__":
    main()
