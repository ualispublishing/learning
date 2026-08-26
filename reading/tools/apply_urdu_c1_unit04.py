from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "reading/urdu/c1/passages.jsonl"
CANDIDATE_DIR = ROOT / "reading/urdu/c1/candidates/unit04"
CONTINUATION = ROOT / "reading/CONTINUATION.json"
STATUS = ROOT / "reading/STATUS.json"
PLAN = ROOT / "reading/planning/ACTIVE_GENERATION_PLAN.json"
MATRIX = ROOT / "reading/planning/topic_genre_matrix.json"
TASKS = ROOT / "reading/TASKS.md"
HANDOFF = ROOT / "reading/AGENT_HANDOFF_V2.md"
QA = ROOT / "reading/audit/urdu_c1_u04_generation_qa_2026-08-26.json"

EXPECTED_EXISTING = list(range(1, 19))
EXPECTED_CANDIDATE = list(range(19, 25))
EXPECTED_IDS = [f"ur-c1-u04-p{i:02d}" for i in range(1, 7)]
EXPECTED_ROLES = ["instructional", "reinforcement", "interleaved", "transfer", "integration", "checkpoint"]
EXPECTED_GENRES = ["essay", "analysis", "paired viewpoints", "essay", "analysis", "paired viewpoints"]
EXPECTED_TARGET_IDS = ["ur-rank-1978", "ur-rank-2496", "ur-rank-2920", "ur-rank-2746", "ur-rank-1526", "ur-rank-1152"]
NEXT_UNIT = 5
NEXT_SEQUENCE = 25
PROJECT_TOTAL = 984
URDU_TOTAL = 264
REMAINING = 96
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
    candidate_files = sorted(CANDIDATE_DIR.glob("p*.json"))
    require(len(candidate_files) == 6, f"Expected 6 Unit 4 candidate files, found {len(candidate_files)}")
    candidate = [load_json(path) for path in candidate_files]

    candidate_sequences = [r.get("sequence") for r in candidate]
    require(len(candidate) == 6, f"Expected 6 candidate passages, found {len(candidate)}")
    require(candidate_sequences == EXPECTED_CANDIDATE, f"Candidate sequences drifted: {candidate_sequences}")
    require([r.get("id") for r in candidate] == EXPECTED_IDS, "Candidate IDs drifted")
    require([r.get("passage_type") for r in candidate] == EXPECTED_ROLES, "Candidate passage roles drifted")
    require([r.get("genre") for r in candidate] == EXPECTED_GENRES, "Candidate genre cycle drifted")
    require(all(r.get("language") == "ur" and r.get("cefr") == "C1" and r.get("unit") == 4 for r in candidate), "Candidate language/level/unit drift")
    require(all(r.get("topics") == ["language, identity, and society"] for r in candidate), "Candidate roadmap topic drift")
    require(all(len(r.get("questions", [])) == 10 and len(r.get("answer_key", [])) == 10 for r in candidate), "Candidate question/answer contract failed")

    target_ids = []
    for row in candidate:
        questions = row["questions"]
        answers = row["answer_key"]
        require([q["id"] for q in questions] == [f"q{i}" for i in range(1, 11)], f"Question IDs drifted for {row['id']}")
        require([a["id"] for a in answers] == [f"a{i}" for i in range(1, 11)], f"Answer IDs drifted for {row['id']}")
        answer_map = {a["question_id"]: a["id"] for a in answers}
        require(all(answer_map.get(q["id"]) == q["answer_id"] for q in questions), f"Question/answer mapping failed for {row['id']}")
        targets = row.get("new_lexical_targets", [])
        require(len(targets) == 1, f"Expected exactly one new lexical target in {row['id']}")
        target = targets[0]
        target_ids.append(target["id"])
        require(target.get("first_introduced") is True, f"Target freshness flag failed in {row['id']}")
        actual_exposure = row["text"].count(target["form"])
        require(actual_exposure == target["exposures_in_text"] and actual_exposure >= 2, f"Target exposure mismatch in {row['id']}: {target['form']}={actual_exposure}")
    require(target_ids == EXPECTED_TARGET_IDS, f"Candidate target set drifted: {target_ids}")
    require(len(set(target_ids)) == 6, "Candidate target IDs are not unique")

    canonical_sequences = [r.get("sequence") for r in canonical]
    if canonical_sequences == list(range(1, 25)):
        by_sequence = {r["sequence"]: r["id"] for r in canonical}
        require(all(by_sequence.get(row["sequence"]) == row["id"] for row in candidate), "Sequences 19-24 exist but candidate IDs do not match")
    else:
        require(canonical_sequences == EXPECTED_EXISTING, f"Canonical frontier drifted: {canonical_sequences}")
        existing_ids = {r["id"] for r in canonical}
        existing_target_ids = {t["id"] for r in canonical for t in r.get("new_lexical_targets", [])}
        require(not any(r["id"] in existing_ids for r in candidate), "Candidate passage ID already exists in canonical corpus")
        require(not any(tid in existing_target_ids for tid in target_ids), "Candidate lexical target ID already exists in canonical corpus")
        canonical.extend(candidate)
        write_jsonl(CANONICAL, canonical)

    continuation = load_json(CONTINUATION)
    require(continuation["production"]["canonical_passages"] in (978, PROJECT_TOTAL), "Unexpected continuation project count")
    require(continuation["production"]["urdu"]["canonical_passages"] in (258, URDU_TOTAL), "Unexpected continuation Urdu count")
    require(continuation["active_frontier"]["production"]["language"] == "urdu" and continuation["active_frontier"]["production"]["level"] == "C1", "Continuation route drift")
    continuation["updated"] = DATE
    continuation["production"]["canonical_passages"] = PROJECT_TOTAL
    continuation["production"]["urdu"]["canonical_passages"] = URDU_TOTAL
    continuation["active_frontier"]["production"]["action"] = "Continue generation-first production from Urdu C1 Unit 5 / sequence 25 using the canonical roadmap and ten-question contract."
    continuation["exact_next_actions"] = [
        "Validate the routed state bundle and live canonical counts.",
        "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu C1 Unit 5 generation at sequence 25.",
        "Keep release/educator verification separate from generation progress."
    ]
    write_json(CONTINUATION, continuation)

    status = load_json(STATUS)
    require(status["current"]["canonical_passages"] in (978, PROJECT_TOTAL), "Unexpected status project count")
    require(status["languages"]["urdu"]["canonical_passages"] in (258, URDU_TOTAL), "Unexpected status Urdu count")
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
    require(plan["active_unit"] in (4, NEXT_UNIT), "Unexpected active unit in generation plan")
    require(plan["start_sequence"] in (19, NEXT_SEQUENCE), "Unexpected start sequence in generation plan")
    plan["active_unit"] = NEXT_UNIT
    plan["start_sequence"] = NEXT_SEQUENCE
    plan["existing_active_level_passages"] = 24
    plan["active_unit_roadmap"] = roadmap
    write_json(PLAN, plan)

    tasks = TASKS.read_text(encoding="utf-8")
    tasks = replace_once(tasks, "Canonical production frontier: **Urdu C1, Unit 4, sequence 19**.", "Canonical production frontier: **Urdu C1, Unit 5, sequence 25**.", "TASKS frontier")
    tasks = replace_once(tasks, "Urdu: 258/360 generated; A1-B2 complete, C1 in progress.", "Urdu: 264/360 generated; A1-B2 complete, C1 in progress.", "TASKS Urdu count")
    tasks = replace_once(tasks, "Project: 978/1080 generated.", "Project: 984/1080 generated.", "TASKS project count")
    TASKS.write_text(tasks, encoding="utf-8")

    handoff = HANDOFF.read_text(encoding="utf-8")
    handoff = replace_once(handoff, "Canonical generated total: **978**.", "Canonical generated total: **984**.", "handoff project count")
    handoff = replace_once(handoff, "Urdu: **258/360**; A1-B2 generation complete and C1 generation in progress.", "Urdu: **264/360**; A1-B2 generation complete and C1 generation in progress.", "handoff Urdu count")
    handoff = replace_once(handoff, "Continue **Urdu C1**, starting from Unit 4 / sequence 19, under:", "Continue **Urdu C1**, starting from Unit 5 / sequence 25, under:", "handoff frontier")
    handoff = replace_once(handoff, "C1 Unit 4 uses the roadmap theme **language, identity, and society** with `essay`, `analysis`, and `paired viewpoints` genres.", "C1 Unit 5 uses the roadmap theme **scientific uncertainty and communication** with `research summary`, `journalistic analysis`, and `critique` genres.", "handoff roadmap")
    HANDOFF.write_text(handoff, encoding="utf-8")

    qa = load_json(QA)
    qa["canonicalization_status"] = "CANONICAL_APPEND_CONFIRMED"
    qa["canonicalized_on"] = DATE
    qa["canonical_path"] = "reading/urdu/c1/passages.jsonl"
    qa["canonical_passage_count"] = 24
    qa["project_canonical_passages"] = PROJECT_TOTAL
    qa["urdu_canonical_passages"] = URDU_TOTAL
    qa["next_frontier"] = "Urdu C1 Unit 5 / sequence 25"
    qa["formal_release_audit"] = "DEFERRED"
    qa["release_note"] = "Generation-stage QA only. This does not mark educator/publication release approval."
    write_json(QA, qa)

    subprocess.run([sys.executable, str(ROOT / "reading/tools/refresh_state_manifest.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "reading/tools/validate_continuation_state.py")], cwd=ROOT, check=True)

    final = load_jsonl(CANONICAL)
    require([r["sequence"] for r in final] == list(range(1, 25)), "Final canonical sequences are not 1-24")
    print("Urdu C1 Unit 4 canonicalized: sequences 19-24; next frontier Unit 5 / sequence 25.")


if __name__ == "__main__":
    main()
