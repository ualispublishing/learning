from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "reading/urdu/c1/passages.jsonl"
CANDIDATE = ROOT / "reading/urdu/c1/candidates/unit03.jsonl"
CONTINUATION = ROOT / "reading/CONTINUATION.json"
STATUS = ROOT / "reading/STATUS.json"
PLAN = ROOT / "reading/planning/ACTIVE_GENERATION_PLAN.json"
MATRIX = ROOT / "reading/planning/topic_genre_matrix.json"
TASKS = ROOT / "reading/TASKS.md"
HANDOFF = ROOT / "reading/AGENT_HANDOFF_V2.md"
QA = ROOT / "reading/audit/urdu_c1_u03_generation_qa_2026-08-26.json"

EXPECTED_EXISTING = list(range(1, 13))
EXPECTED_CANDIDATE = list(range(13, 19))
NEXT_UNIT = 4
NEXT_SEQUENCE = 19
PROJECT_TOTAL = 978
URDU_TOTAL = 258
REMAINING = 102
DATE = "2026-08-26"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    require(old in text, f"Expected {label} text not found: {old!r}")
    return text.replace(old, new, 1)


def main() -> None:
    canonical = load_jsonl(CANONICAL)
    candidate = load_jsonl(CANDIDATE)

    canonical_sequences = [r.get("sequence") for r in canonical]
    candidate_sequences = [r.get("sequence") for r in candidate]
    require(candidate_sequences == EXPECTED_CANDIDATE, f"Candidate sequences drifted: {candidate_sequences}")
    require(all(r.get("language") == "ur" and r.get("cefr") == "C1" and r.get("unit") == 3 for r in candidate), "Candidate language/level/unit drift")
    require(all(len(r.get("questions", [])) == 10 and len(r.get("answer_key", [])) == 10 for r in candidate), "Candidate question/answer contract failed")
    require(len({r["id"] for r in candidate}) == 6, "Candidate IDs are not unique")

    if canonical_sequences == list(range(1, 19)):
        existing_ids = {r["id"] for r in canonical}
        require(all(r["id"] in existing_ids for r in candidate), "Sequences 13-18 exist but candidate IDs do not match")
    else:
        require(canonical_sequences == EXPECTED_EXISTING, f"Canonical frontier drifted: {canonical_sequences}")
        existing_ids = {r["id"] for r in canonical}
        require(not any(r["id"] in existing_ids for r in candidate), "Candidate ID already exists in canonical corpus")
        canonical.extend(candidate)
        write_jsonl(CANONICAL, canonical)

    continuation = load_json(CONTINUATION)
    require(continuation["production"]["canonical_passages"] in (972, PROJECT_TOTAL), "Unexpected continuation project count")
    require(continuation["production"]["urdu"]["canonical_passages"] in (252, URDU_TOTAL), "Unexpected continuation Urdu count")
    continuation["updated"] = DATE
    continuation["production"]["canonical_passages"] = PROJECT_TOTAL
    continuation["production"]["urdu"]["canonical_passages"] = URDU_TOTAL
    continuation["active_frontier"]["production"]["language"] = "urdu"
    continuation["active_frontier"]["production"]["level"] = "C1"
    continuation["active_frontier"]["production"]["action"] = "Continue generation-first production from Urdu C1 Unit 4 / sequence 19 using the canonical roadmap and ten-question contract."
    continuation["exact_next_actions"] = [
        "Validate the routed state bundle and live canonical counts.",
        "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu C1 Unit 4 generation at sequence 19.",
        "Keep release/educator verification separate from generation progress."
    ]
    write_json(CONTINUATION, continuation)

    status = load_json(STATUS)
    require(status["current"]["canonical_passages"] in (972, PROJECT_TOTAL), "Unexpected status project count")
    require(status["languages"]["urdu"]["canonical_passages"] in (252, URDU_TOTAL), "Unexpected status Urdu count")
    status["updated"] = DATE
    status["current"]["canonical_passages"] = PROJECT_TOTAL
    status["current"]["remaining_generation_passages"] = REMAINING
    status["current"]["active_language"] = "urdu"
    status["current"]["active_level"] = "C1"
    status["languages"]["urdu"]["canonical_passages"] = URDU_TOTAL
    status["languages"]["urdu"]["remaining_generation_passages"] = REMAINING
    status["languages"]["urdu"]["generation_state"] = "C1_IN_PROGRESS"
    status["languages"]["urdu"]["next_generation_level"] = "C1"
    write_json(STATUS, status)

    matrix = load_json(MATRIX)
    roadmap = next(x for x in matrix["levels"]["C1"] if x["unit"] == NEXT_UNIT)
    plan = load_json(PLAN)
    require(plan["active_language"] == "urdu" and plan["active_level"] == "C1", "Active plan route drift")
    require(plan["active_unit"] in (3, NEXT_UNIT), "Unexpected active unit in generation plan")
    plan["active_unit"] = NEXT_UNIT
    plan["start_sequence"] = NEXT_SEQUENCE
    plan["existing_active_level_passages"] = 18
    plan["active_unit_roadmap"] = roadmap
    write_json(PLAN, plan)

    tasks = TASKS.read_text(encoding="utf-8")
    tasks = tasks.replace("Canonical production frontier: **Urdu C1, Unit 3, sequence 13**.", "Canonical production frontier: **Urdu C1, Unit 4, sequence 19**.")
    tasks = tasks.replace("Urdu: 252/360 generated; A1-B2 complete, C1 in progress.", "Urdu: 258/360 generated; A1-B2 complete, C1 in progress.")
    tasks = tasks.replace("Project: 972/1080 generated.", "Project: 978/1080 generated.")
    TASKS.write_text(tasks, encoding="utf-8")

    handoff = HANDOFF.read_text(encoding="utf-8")
    handoff = handoff.replace("Canonical generated total: **972**.", "Canonical generated total: **978**.")
    handoff = handoff.replace("Urdu: **252/360**; A1-B2 generation complete and C1 generation in progress.", "Urdu: **258/360**; A1-B2 generation complete and C1 generation in progress.")
    handoff = handoff.replace("Continue **Urdu C1**, starting from Unit 3 / sequence 13, under:", "Continue **Urdu C1**, starting from Unit 4 / sequence 19, under:")
    handoff = handoff.replace("C1 Unit 3 uses the roadmap theme **institutions and incentives** with `analysis`, `commentary`, and `policy note` genres.", "C1 Unit 4 uses the roadmap theme **language, identity, and society** with `essay`, `analysis`, and `paired viewpoints` genres.")
    handoff = handoff.replace("resume guarded generation at **Urdu C1 Unit 3 / sequence 13** using the C1 Unit 3 roadmap theme `institutions and incentives`.", "resume guarded generation at **Urdu C1 Unit 4 / sequence 19** using the C1 Unit 4 roadmap theme `language, identity, and society`.")
    HANDOFF.write_text(handoff, encoding="utf-8")

    qa = load_json(QA)
    qa["canonicalization_status"] = "CANONICALIZED"
    qa["canonicalized_on"] = DATE
    qa["canonical_path"] = "reading/urdu/c1/passages.jsonl"
    qa["post_append_frontier"] = {"urdu_c1_passages": 18, "next_sequence": NEXT_SEQUENCE, "next_unit": NEXT_UNIT, "overall_reading_count": PROJECT_TOTAL}
    write_json(QA, qa)

    subprocess.run([sys.executable, str(ROOT / "reading/tools/refresh_state_manifest.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "reading/tools/validate_continuation_state.py")], cwd=ROOT, check=True)

    final = load_jsonl(CANONICAL)
    require([r["sequence"] for r in final] == list(range(1, 19)), "Final canonical sequences are not 1-18")
    print("Urdu C1 Unit 3 canonicalized: sequences 13-18; next frontier Unit 4 / sequence 19.")


if __name__ == "__main__":
    main()
