#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "reading" / "audit" / "urdu_b2_u06_generation_candidate"
TARGET = ROOT / "reading" / "urdu" / "b2" / "passages.jsonl"
SCHEMA = ROOT / "reading" / "schema" / "passage.schema.json"
DATE = "2026-08-25"
EXPECTED_IDS = [f"ur-b2-u06-p{i:02d}" for i in range(1, 7)]
EXPECTED_SEQ = list(range(31, 37))
EXPECTED_TARGETS = [
    "ur-rank-2424", "ur-rank-2431",
    "ur-rank-2503", "ur-rank-2445",
    "ur-rank-2444", "ur-rank-2495",
    "ur-rank-2464", "ur-rank-2488",
    "ur-rank-2486", "ur-rank-2475",
]
EXPECTED_ROLES = ["instructional", "reinforcement", "interleaved", "transfer", "integration", "checkpoint"]
REQUIRED_GENRES = {"analysis", "policy-style summary", "paired opinions"}
EXPECTED_ROADMAP = {
    "unit": 6,
    "theme": "digital life and privacy",
    "genres": ["analysis", "policy-style summary", "paired opinions"],
}
NEXT_ROADMAP = {
    "unit": 7,
    "theme": "arts and interpretation",
    "genres": ["review", "profile", "critical comparison"],
}


def jl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def fail(msg: str) -> None:
    raise SystemExit(f"Fail closed: {msg}")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        fail(f"{label}: expected exact live-state phrase once: {old!r}")
    return text.replace(old, new, 1)


def exact_form_count(text: str, form: str) -> int:
    return len(re.findall(rf"(?<!\w){re.escape(form)}(?!\w)", text, flags=re.UNICODE))


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = set(schema["required"])
    passage_types = set(schema["properties"]["passage_type"]["enum"])
    domains = set(schema["properties"]["domains"]["items"]["enum"])
    qtypes = set(schema["$defs"]["question"]["properties"]["type"]["enum"])
    strategies = set(schema["$defs"]["newLexicalTarget"]["properties"]["context_strategy"]["items"]["enum"])
    review_reps = set(schema["$defs"]["reviewLexicalTarget"]["properties"]["representation"]["enum"])
    review_stages = set(schema["$defs"]["reviewLexicalTarget"]["properties"]["review_stage"]["enum"])

    a1 = jl(ROOT / "reading" / "urdu" / "a1" / "passages.jsonl")
    a2 = jl(ROOT / "reading" / "urdu" / "a2" / "passages.jsonl")
    b1 = jl(ROOT / "reading" / "urdu" / "b1" / "passages.jsonl")
    b2 = jl(TARGET)
    if [len(a1), len(a2), len(b1)] != [60, 60, 60]:
        fail("Urdu A1, A2, and B1 must each contain exactly 60 canonical passages")
    if len(b2) != 30 or [r.get("sequence") for r in b2] != list(range(1, 31)):
        fail("Urdu B2 must contain exactly sequences 1-30 before Unit 6 promotion")

    status_path = ROOT / "reading" / "STATUS.json"
    continuation_path = ROOT / "reading" / "CONTINUATION.json"
    plan_path = ROOT / "reading" / "planning" / "ACTIVE_GENERATION_PLAN.json"
    tasks_path = ROOT / "reading" / "TASKS.md"
    handoff_path = ROOT / "reading" / "AGENT_HANDOFF_V2.md"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    continuation = json.loads(continuation_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    if status["current"]["canonical_passages"] != 930 or status["languages"]["urdu"]["canonical_passages"] != 210:
        fail("STATUS counts are no longer the reviewed B2 Unit 6 pre-promotion state")
    if status["current"]["active_language"] != "urdu" or status["current"]["active_level"] != "B2":
        fail("STATUS active frontier is no longer Urdu B2")
    if plan.get("active_unit") != 6 or plan.get("start_sequence") != 31 or plan.get("existing_active_level_passages") != 30:
        fail("ACTIVE_GENERATION_PLAN no longer points to Urdu B2 Unit 6 / sequence 31")
    if plan.get("active_unit_roadmap") != EXPECTED_ROADMAP:
        fail("ACTIVE_GENERATION_PLAN Unit 6 roadmap drifted")
    action = continuation.get("active_frontier", {}).get("production", {}).get("action", "")
    if "Urdu B2 Unit 6 / sequence 31" not in action:
        fail("CONTINUATION frontier no longer points to Urdu B2 Unit 6 / sequence 31")

    before = TARGET.read_bytes()
    before_sha = hashlib.sha256(before).hexdigest()
    prior_rows = a1 + a2 + b1 + b2
    taught_ids = {t["id"] for r in prior_rows for t in r.get("new_lexical_targets", [])}
    collision = sorted(taught_ids.intersection(EXPECTED_TARGETS))
    if collision:
        fail(f"Unit 6 target-ID freshness collision: {collision}")

    canonical_quality = json.loads(json.dumps(b2[-1]["quality"]))
    rows: list[dict] = []
    learner_parts: list[str] = []
    for i in range(1, 7):
        path = STAGE / f"ur-b2-u06-p{i:02d}.json"
        if not path.exists():
            fail(f"missing candidate {path.relative_to(ROOT)}")
        row = json.loads(path.read_text(encoding="utf-8"))
        row["quality"] = json.loads(json.dumps(canonical_quality))
        row["word_count"] = len(row["text"].split())
        row["sentence_count"] = row["text"].count("۔")
        for target in row.get("new_lexical_targets", []):
            target["exposures_in_text"] = exact_form_count(row["text"], target["form"])
        path.write_text(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        rows.append(row)
        learner_parts.extend([row["title"], row["text"]])
        learner_parts.extend(q["prompt"] for q in row["questions"])
        learner_parts.extend(a["answer"] for a in row["answer_key"])

    if [r["id"] for r in rows] != EXPECTED_IDS or [r["sequence"] for r in rows] != EXPECTED_SEQ:
        fail("Unit 6 ID/sequence contract failed")
    if [r["passage_type"] for r in rows] != EXPECTED_ROLES:
        fail("Unit 6 role cycle failed")
    if [len(r["new_lexical_targets"]) for r in rows] != [2, 2, 2, 2, 2, 0]:
        fail("Unit 6 target distribution failed")
    if [t["id"] for r in rows[:5] for t in r["new_lexical_targets"]] != EXPECTED_TARGETS:
        fail("Unit 6 target order/identity failed")
    if any(t["exposures_in_text"] < 1 for r in rows for t in r["new_lexical_targets"]):
        fail("Unit 6 has a new target absent from passage text")
    if not REQUIRED_GENRES.issubset({r["genre"] for r in rows}):
        fail("required Unit 6 genres are missing")

    prior_learner = ""
    for row in rows[:5]:
        for target in row["new_lexical_targets"]:
            if exact_form_count(prior_learner, target["form"]) > 0:
                fail(f"premature exact-form exposure before first introduction: {target['form']} / {target['id']}")
        prior_learner += "\n" + "\n".join(
            [row["title"], row["text"]]
            + [q["prompt"] for q in row["questions"]]
            + [a["answer"] for a in row["answer_key"]]
        )

    p6 = rows[-1]
    expected_forms = {t["form"] for r in rows[:5] for t in r["new_lexical_targets"]}
    checkpoint_forms = {t["form"] for t in p6["review_lexical_targets"] if t["representation"] == "running_text"}
    if p6["new_lexical_targets"] or not p6["speed_training"]["timed"] or p6["speed_training"]["new_word_policy"] != "none":
        fail("Unit 6 P6 checkpoint policy failed")
    if checkpoint_forms != expected_forms or any(exact_form_count(p6["text"], form) < 1 for form in expected_forms):
        fail("Unit 6 P6 does not visibly recycle all ten new targets")

    current_new_ids = {t["id"] for r in rows for t in r.get("new_lexical_targets", [])}
    known_target_ids = taught_ids | current_new_ids
    for row in rows:
        missing = required - set(row)
        if missing:
            fail(f"{row['id']} missing required fields: {sorted(missing)}")
        if row["passage_type"] not in passage_types or any(d not in domains for d in row["domains"]):
            fail(f"schema passage/domain enum failure: {row['id']}")
        if len(row["questions"]) != 10 or len(row["answer_key"]) != 10:
            fail(f"10x10 question-answer contract failed: {row['id']}")
        if not 350 <= row["word_count"] <= 550:
            fail(f"B2 word band failed {row['id']}: {row['word_count']}")
        qids = {q["id"] for q in row["questions"]}
        aids = {a["id"] for a in row["answer_key"]}
        if qids != {f"q{i}" for i in range(1, 11)} or aids != {f"a{i}" for i in range(1, 11)}:
            fail(f"question/answer IDs drifted: {row['id']}")
        amap = {a["id"]: a for a in row["answer_key"]}
        for target in row.get("new_lexical_targets", []):
            if any(s not in strategies for s in target["context_strategy"]):
                fail(f"invalid context strategy: {row['id']}/{target['id']}")
        for rt in row.get("review_lexical_targets", []):
            if rt["representation"] not in review_reps:
                fail(f"invalid review representation: {row['id']}/{rt['id']}/{rt['representation']}")
            if rt["review_stage"] not in review_stages:
                fail(f"invalid review stage: {row['id']}/{rt['id']}/{rt['review_stage']}")
            if rt["id"] not in known_target_ids:
                fail(f"unknown review target: {row['id']}/{rt['id']}")
        for q in row["questions"]:
            if q["type"] not in qtypes or q["answer_id"] not in amap or amap[q["answer_id"]]["question_id"] != q["id"]:
                fail(f"QA link/type failure: {row['id']}/{q['id']}")
            refs = set(q.get("target_ids", []))
            if not refs.issubset(known_target_ids):
                fail(f"question target reference is unknown: {row['id']}/{q['id']}/{sorted(refs - known_target_ids)}")

    learner_text = "\n".join(learner_parts)
    if re.search(r"[A-Za-z\u0900-\u097F\u3400-\u9FFF]", learner_text):
        fail("learner-facing Latin/Devanagari/CJK leakage")

    payload = "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows).encode("utf-8")
    TARGET.write_bytes(before + payload)
    after = TARGET.read_bytes()
    if after[: len(before)] != before:
        fail("pre-existing Urdu B2 canonical bytes changed")
    final = jl(TARGET)
    if len(final) != 36 or [r["sequence"] for r in final] != list(range(1, 37)) or [r["id"] for r in final[-6:]] != EXPECTED_IDS:
        fail("canonical B2 post-append check failed")

    (STAGE / "manifest.json").write_text(json.dumps({
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "ur",
        "cefr": "B2",
        "unit": 6,
        "date": DATE,
        "status": "CANONICALIZED",
        "canonical_target": "reading/urdu/b2/passages.jsonl",
        "sequence_range": [31, 36],
        "record_count": 6,
        "release_promotion": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks = {k: "PASS" for k in [
        "prior_a1_a2_b1_60_each",
        "prior_b2_sequences_1_through_30_exact",
        "freshness_across_all_prior_urdu_target_ids",
        "record_count",
        "sequence_31_through_36",
        "role_cycle",
        "question_answer_10x10",
        "bidirectional_links",
        "new_target_distribution_2_2_2_2_2_0",
        "new_target_text_exposure",
        "first_introduction_order_unicode_word_boundary",
        "required_genres",
        "p6_checkpoint_policy",
        "p6_all_target_recycling",
        "learner_script_scan",
        "schema_required_fields_enums_context_and_review_metadata",
        "review_target_identity_check",
        "b2_word_band_350_550",
        "quality_metadata_preserved_from_prior_canonical_b2",
        "preexisting_canonical_bytes_preserved",
    ]}
    (ROOT / "reading" / "audit" / "urdu_b2_u06_generation_validation_2026-08-25.json").write_text(json.dumps({
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "ur",
        "cefr": "B2",
        "unit": 6,
        "date": DATE,
        "canonicalized": True,
        "release_promotion": False,
        "word_counts": [r["word_count"] for r in rows],
        "checks": checks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "reading" / "audit" / "urdu_b2_u06_promotion_2026-08-25.json").write_text(json.dumps({
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "ur",
        "cefr": "B2",
        "unit": 6,
        "date": DATE,
        "status": "CANONICAL_PROMOTION_PASS",
        "release_promotion": False,
        "before_record_count": 30,
        "after_record_count": 36,
        "appended_sequences": EXPECTED_SEQ,
        "appended_ids": EXPECTED_IDS,
        "preexisting_bytes_preserved_exactly": True,
        "canonical_sha256_before": before_sha,
        "canonical_sha256_after": hashlib.sha256(after).hexdigest(),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lexical_path = ROOT / "reading" / "audit" / "urdu_b2_u06_lexical_sense_check_2026-08-25.json"
    lexical = json.loads(lexical_path.read_text(encoding="utf-8"))
    lexical["status"] = "PASS_FOR_GENERATION_TARGET_SENSES_AND_CANONICAL_FRESHNESS"
    lexical["freshness_result"] = "PASS"
    lexical["freshness_scope"] = "Exact target IDs checked against all canonical Urdu A1-B1 and B2 sequences 1-30 immediately before Unit 6 append."
    lexical_path.write_text(json.dumps(lexical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status["current"]["canonical_passages"] = 936
    status["current"]["remaining_generation_passages"] = 144
    urdu_status = status["languages"]["urdu"]
    urdu_status["generation_state"] = "B2_IN_PROGRESS"
    urdu_status["canonical_passages"] = 216
    urdu_status["remaining_generation_passages"] = 144
    urdu_status["next_generation_level"] = "B2"
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    continuation["updated"] = DATE
    continuation["production"]["canonical_passages"] = 936
    continuation["production"]["urdu"]["canonical_passages"] = 216
    continuation["active_frontier"]["production"]["action"] = "Continue generation-first production from Urdu B2 Unit 7 / sequence 37 using the canonical roadmap and ten-question contract."
    if len(continuation.get("exact_next_actions", [])) < 2:
        fail("CONTINUATION exact_next_actions is unexpectedly short")
    continuation["exact_next_actions"][1] = "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu B2 Unit 7 generation at sequence 37."
    continuation_path.write_text(json.dumps(continuation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    plan["active_unit"] = 7
    plan["start_sequence"] = 37
    plan["existing_active_level_passages"] = 36
    plan["active_unit_roadmap"] = NEXT_ROADMAP
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tasks = tasks_path.read_text(encoding="utf-8")
    tasks = replace_once(tasks, "Canonical production frontier: **Urdu B2, Unit 6, sequence 31**.", "Canonical production frontier: **Urdu B2, Unit 7, sequence 37**.", "TASKS frontier")
    tasks = replace_once(tasks, "- Urdu: 210/360 generated; A1-B1 complete, B2 in progress.", "- Urdu: 216/360 generated; A1-B1 complete, B2 in progress.", "TASKS Urdu total")
    tasks = replace_once(tasks, "- Project: 930/1080 generated.", "- Project: 936/1080 generated.", "TASKS project total")
    tasks_path.write_text(tasks, encoding="utf-8")

    handoff = handoff_path.read_text(encoding="utf-8")
    handoff = replace_once(handoff, "- Canonical generated total: **930**.", "- Canonical generated total: **936**.", "HANDOFF project total")
    handoff = replace_once(handoff, "- Urdu: **210/360**; A1-B1 generation complete and B2 generation in progress.", "- Urdu: **216/360**; A1-B1 generation complete and B2 generation in progress.", "HANDOFF Urdu total")
    handoff = replace_once(handoff, "Continue **Urdu B2**, starting from Unit 6 / sequence 31, under:", "Continue **Urdu B2**, starting from Unit 7 / sequence 37, under:", "HANDOFF frontier")
    handoff = replace_once(handoff, "B2 Unit 6 uses the roadmap theme **digital life and privacy** with `analysis`, `policy-style summary`, and `paired opinions` genres.", "B2 Unit 7 uses the roadmap theme **arts and interpretation** with `review`, `profile`, and `critical comparison` genres.", "HANDOFF roadmap")
    handoff = replace_once(handoff, "Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu B2 Unit 6 / sequence 31** using the B2 Unit 6 roadmap theme `digital life and privacy`.", "Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu B2 Unit 7 / sequence 37** using the B2 Unit 7 roadmap theme `arts and interpretation`.", "HANDOFF next action")
    handoff_path.write_text(handoff, encoding="utf-8")

    print("Urdu B2 Unit 6 promotion validation: PASS")
    print("canonical B2 passages: 36; project passages: 936; Urdu passages: 216")
    print("next frontier: Urdu B2 Unit 7 / sequence 37 — arts and interpretation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
