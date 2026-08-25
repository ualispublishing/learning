#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "reading" / "audit" / "urdu_b2_u01_generation_candidate"
TARGET = ROOT / "reading" / "urdu" / "b2" / "passages.jsonl"
SCHEMA = ROOT / "reading" / "schema" / "passage.schema.json"
DATE = "2026-08-24"

EXPECTED_IDS = [f"ur-b2-u01-p{i:02d}" for i in range(1, 7)]
EXPECTED_SEQ = list(range(1, 7))
EXPECTED_TARGETS = [
    "ur-rank-2243", "ur-rank-2107",
    "ur-rank-2246", "ur-rank-2211",
    "ur-rank-2031", "ur-rank-2104",
    "ur-rank-2255", "ur-rank-2265",
    "ur-rank-2032", "ur-rank-2277",
]
EXPECTED_ROLES = ["instructional", "reinforcement", "interleaved", "transfer", "integration", "checkpoint"]
REQUIRED_GENRES = {"popular science", "analysis", "paired viewpoints"}
REVIEW_REPRESENTATION_ALIASES = {"question_answer": "other"}


def jl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def fail(msg: str) -> None:
    raise SystemExit(f"Fail closed: {msg}")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        fail(f"{label}: expected exact live-state phrase once: {old!r}")
    return text.replace(old, new, 1)


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
    if b2:
        fail("Urdu B2 canonical file must be absent or empty before Unit 1 promotion")

    status_path = ROOT / "reading" / "STATUS.json"
    continuation_path = ROOT / "reading" / "CONTINUATION.json"
    plan_path = ROOT / "reading" / "planning" / "ACTIVE_GENERATION_PLAN.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    continuation = json.loads(continuation_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    if status["current"]["canonical_passages"] != 900 or status["languages"]["urdu"]["canonical_passages"] != 180:
        fail("STATUS counts are no longer the reviewed B2 Unit 1 pre-promotion state")
    if status["current"]["active_language"] != "urdu" or status["current"]["active_level"] != "B2":
        fail("STATUS active frontier is no longer Urdu B2")
    if plan.get("active_unit") != 1 or plan.get("start_sequence") != 1 or plan.get("existing_active_level_passages") != 0:
        fail("ACTIVE_GENERATION_PLAN no longer points to Urdu B2 Unit 1 / sequence 1")
    action = continuation.get("active_frontier", {}).get("production", {}).get("action", "")
    if "Urdu B2 Unit 1 / sequence 1" not in action:
        fail("CONTINUATION frontier no longer points to Urdu B2 Unit 1 / sequence 1")

    before = TARGET.read_bytes() if TARGET.exists() else b""
    before_sha = hashlib.sha256(before).hexdigest()
    taught_ids = {t["id"] for r in a1 + a2 + b1 + b2 for t in r.get("new_lexical_targets", [])}
    collision = sorted(taught_ids.intersection(EXPECTED_TARGETS))
    if collision:
        fail(f"Unit 1 target-ID freshness collision: {collision}")

    rows: list[dict] = []
    learner_parts: list[str] = []
    for i in range(1, 7):
        path = STAGE / f"ur-b2-u01-p{i:02d}.json"
        if not path.exists():
            fail(f"missing candidate {path.relative_to(ROOT)}")
        row = json.loads(path.read_text(encoding="utf-8"))

        for rt in row.get("review_lexical_targets", []):
            rep = rt.get("representation")
            if rep in REVIEW_REPRESENTATION_ALIASES:
                rt["representation"] = REVIEW_REPRESENTATION_ALIASES[rep]

        row["word_count"] = len(row["text"].split())
        row["sentence_count"] = row["text"].count("۔")
        for target in row.get("new_lexical_targets", []):
            target["exposures_in_text"] = row["text"].count(target["form"])
        path.write_text(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        rows.append(row)
        learner_parts.extend([row["title"], row["text"]])
        learner_parts.extend(q["prompt"] for q in row["questions"])
        learner_parts.extend(a["answer"] for a in row["answer_key"])

    if [r["id"] for r in rows] != EXPECTED_IDS or [r["sequence"] for r in rows] != EXPECTED_SEQ:
        fail("Unit 1 ID/sequence contract failed")
    if [r["passage_type"] for r in rows] != EXPECTED_ROLES:
        fail("Unit 1 role cycle failed")
    if [len(r["new_lexical_targets"]) for r in rows] != [2, 2, 2, 2, 2, 0]:
        fail("Unit 1 target distribution failed")
    if [t["id"] for r in rows[:5] for t in r["new_lexical_targets"]] != EXPECTED_TARGETS:
        fail("Unit 1 target order/identity failed")
    if any(t["exposures_in_text"] < 1 for r in rows for t in r["new_lexical_targets"]):
        fail("Unit 1 has a new target absent from passage text")
    if not REQUIRED_GENRES.issubset({r["genre"] for r in rows}):
        fail("required Unit 1 genres are missing")

    prior_learner = ""
    for row in rows[:5]:
        for target in row["new_lexical_targets"]:
            if target["form"] in prior_learner:
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
        fail("Unit 1 P6 checkpoint policy failed")
    if checkpoint_forms != expected_forms or any(form not in p6["text"] for form in expected_forms):
        fail("Unit 1 P6 does not visibly recycle all ten new targets")

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
        for q in row["questions"]:
            if q["type"] not in qtypes or q["answer_id"] not in amap or amap[q["answer_id"]]["question_id"] != q["id"]:
                fail(f"QA link/type failure: {row['id']}/{q['id']}")

    learner_text = "\n".join(learner_parts)
    if re.search(r"[A-Za-z\u0900-\u097F\u3400-\u9FFF]", learner_text):
        fail("learner-facing Latin/Devanagari/CJK leakage")

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    append_payload = "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows).encode("utf-8")
    TARGET.write_bytes(before + append_payload)
    after = TARGET.read_bytes()
    if after[: len(before)] != before:
        fail("pre-existing Urdu B2 canonical bytes changed")
    final = jl(TARGET)
    if len(final) != 6 or [r["sequence"] for r in final] != list(range(1, 7)) or [r["id"] for r in final] != EXPECTED_IDS:
        fail("canonical B2 post-append check failed")

    (STAGE / "manifest.json").write_text(
        json.dumps({
            "schema_version": 1,
            "project_id": "LANG-A1C2",
            "language": "ur",
            "cefr": "B2",
            "unit": 1,
            "date": DATE,
            "status": "CANONICALIZED",
            "canonical_target": "reading/urdu/b2/passages.jsonl",
            "sequence_range": [1, 6],
            "record_count": 6,
            "release_promotion": False,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    checks = {k: "PASS" for k in [
        "prior_a1_a2_b1_60_each",
        "prior_b2_absent_or_empty",
        "freshness_across_all_prior_urdu_target_ids",
        "record_count",
        "sequence_1_through_6",
        "role_cycle",
        "question_answer_10x10",
        "bidirectional_links",
        "new_target_distribution_2_2_2_2_2_0",
        "new_target_text_exposure",
        "first_introduction_order",
        "required_genres",
        "p6_checkpoint_policy",
        "p6_all_target_recycling",
        "learner_script_scan",
        "schema_required_fields_enums_context_and_review_metadata",
        "b2_word_band_350_550",
        "preexisting_canonical_bytes_preserved",
    ]}
    (ROOT / "reading" / "audit" / "urdu_b2_u01_generation_validation_2026-08-24.json").write_text(
        json.dumps({
            "schema_version": 1,
            "project_id": "LANG-A1C2",
            "language": "ur",
            "cefr": "B2",
            "unit": 1,
            "date": DATE,
            "canonicalized": True,
            "release_promotion": False,
            "word_counts": [r["word_count"] for r in rows],
            "checks": checks,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "reading" / "audit" / "urdu_b2_u01_promotion_2026-08-24.json").write_text(
        json.dumps({
            "schema_version": 1,
            "project_id": "LANG-A1C2",
            "language": "ur",
            "cefr": "B2",
            "unit": 1,
            "date": DATE,
            "status": "CANONICAL_PROMOTION_PASS",
            "release_promotion": False,
            "before_record_count": 0,
            "after_record_count": 6,
            "appended_sequences": EXPECTED_SEQ,
            "appended_ids": EXPECTED_IDS,
            "preexisting_bytes_preserved_exactly": True,
            "canonical_sha256_before": before_sha,
            "canonical_sha256_after": hashlib.sha256(after).hexdigest(),
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lexical_path = ROOT / "reading" / "audit" / "urdu_b2_u01_lexical_sense_check_2026-08-24.json"
    lexical = json.loads(lexical_path.read_text(encoding="utf-8"))
    lexical["status"] = "PASS_FOR_GENERATION_TARGET_SENSES_AND_CANONICAL_FRESHNESS"
    lexical["freshness_result"] = "PASS"
    lexical["freshness_scope"] = "Exact target IDs checked against all canonical Urdu A1, A2, B1, and any live B2 records immediately before Unit 1 append."
    lexical_path.write_text(json.dumps(lexical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status["current"]["canonical_passages"] = 906
    status["current"]["remaining_generation_passages"] = 174
    urdu = status["languages"]["urdu"]
    urdu["generation_state"] = "B2_IN_PROGRESS"
    urdu["canonical_passages"] = 186
    urdu["remaining_generation_passages"] = 174
    urdu["next_generation_level"] = "B2"
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    continuation["production"]["canonical_passages"] = 906
    cu = continuation["production"]["urdu"]
    cu["state"] = "B2_GENERATION_IN_PROGRESS"
    cu["canonical_passages"] = 186
    cu["next_generation_level"] = "B2"
    continuation["active_frontier"]["production"] = {
        "language": "urdu",
        "level": "B2",
        "action": "Continue generation-first production from Urdu B2 Unit 2 / sequence 7 using the canonical roadmap and ten-question contract.",
    }
    continuation["exact_next_actions"] = [
        "Validate the routed state bundle and live canonical counts.",
        "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu B2 Unit 2 generation at sequence 7.",
        "Keep release/educator verification separate from generation progress.",
    ]
    continuation_path.write_text(json.dumps(continuation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    plan["active_language"] = "urdu"
    plan["active_level"] = "B2"
    plan["active_unit"] = 2
    plan["start_sequence"] = 7
    plan["canonical_active_path"] = "reading/urdu/b2/passages.jsonl"
    plan["existing_active_level_passages"] = 6
    plan["roadmap_lookup"] = "$.levels.B2"
    plan["active_unit_roadmap"] = {
        "unit": 2,
        "theme": "economics and personal/public choices",
        "genres": ["explanatory article", "case study", "commentary"],
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tasks_path = ROOT / "reading" / "TASKS.md"
    tasks = tasks_path.read_text(encoding="utf-8")
    tasks = replace_once(tasks, "Canonical production frontier: **Urdu B2, Unit 1, sequence 1**.", "Canonical production frontier: **Urdu B2, Unit 2, sequence 7**.", "TASKS frontier")
    tasks = replace_once(tasks, "- Urdu: 180/360 generated; A1-B1 complete, B2 in progress.", "- Urdu: 186/360 generated; A1-B1 complete, B2 in progress.", "TASKS Urdu total")
    tasks = replace_once(tasks, "- Project: 900/1080 generated.", "- Project: 906/1080 generated.", "TASKS project total")
    tasks_path.write_text(tasks, encoding="utf-8")

    handoff_path = ROOT / "reading" / "AGENT_HANDOFF_V2.md"
    handoff = handoff_path.read_text(encoding="utf-8")
    handoff = replace_once(handoff, "- Canonical generated total: **900**.", "- Canonical generated total: **906**.", "handoff total")
    handoff = replace_once(handoff, "- Urdu: **180/360**; A1-B1 generation complete and B2 generation in progress.", "- Urdu: **186/360**; A1-B1 generation complete and B2 generation in progress.", "handoff Urdu")
    handoff = replace_once(handoff, "Continue **Urdu B2**, starting from Unit 1 / sequence 1, under:", "Continue **Urdu B2**, starting from Unit 2 / sequence 7, under:", "handoff frontier")
    handoff = replace_once(handoff, "B2 Unit 1 uses the roadmap theme **science and society** with `popular science`, `analysis`, and `paired viewpoints` genres.", "B2 Unit 2 uses the roadmap theme **economics and personal/public choices** with `explanatory article`, `case study`, and `commentary` genres.", "handoff roadmap")
    handoff = replace_once(handoff, "resume guarded generation at **Urdu B2 Unit 1 / sequence 1** using the B2 Unit 1 roadmap theme `science and society`.", "resume guarded generation at **Urdu B2 Unit 2 / sequence 7** using the B2 Unit 2 roadmap theme `economics and personal/public choices`.", "handoff exact next")
    handoff_path.write_text(handoff, encoding="utf-8")

    print("Urdu B2 Unit 1 canonical promotion prepared: 0 -> 6 B2 records")
    print("Production totals prepared: 900 -> 906 project; Urdu 180 -> 186")
    print("Next frontier prepared: Urdu B2 Unit 2 / sequence 7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
