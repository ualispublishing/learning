#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "reading" / "audit" / "urdu_b1_u05_generation_candidate"
TARGET = ROOT / "reading" / "urdu" / "b1" / "passages.jsonl"
SCHEMA = ROOT / "reading" / "schema" / "passage.schema.json"
DATE = "2026-08-24"

EXPECTED_IDS = [f"ur-b1-u05-p{i:02d}" for i in range(1, 7)]
EXPECTED_SEQ = list(range(25, 31))
EXPECTED_TARGETS = [
    "ur-rank-1653","ur-rank-1739","ur-rank-1796",
    "ur-rank-1654","ur-rank-1790","ur-rank-1777",
    "ur-rank-1686","ur-rank-1683","ur-rank-1781",
    "ur-rank-1742","ur-rank-1775","ur-rank-1667",
    "ur-rank-1738","ur-rank-1737","ur-rank-1691",
]
EXPECTED_ROLES = ["instructional","reinforcement","interleaved","transfer","integration","checkpoint"]
REQUIRED_GENRES = {"popular-science explanation","case story","advice critique"}


def jl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def fail(msg: str) -> None:
    raise SystemExit(f"Fail closed: {msg}")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        fail(f"{label}: expected exact live-state phrase once: {old!r}")
    return text.replace(old, new, 1)


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    req = set(schema["required"])
    ptypes = set(schema["properties"]["passage_type"]["enum"])
    domains = set(schema["properties"]["domains"]["items"]["enum"])
    qtypes = set(schema["$defs"]["question"]["properties"]["type"]["enum"])
    strategies = set(schema["$defs"]["newLexicalTarget"]["properties"]["context_strategy"]["items"]["enum"])

    a1 = jl(ROOT / "reading" / "urdu" / "a1" / "passages.jsonl")
    a2 = jl(ROOT / "reading" / "urdu" / "a2" / "passages.jsonl")
    b1 = jl(TARGET)
    if len(a1) != 60 or len(a2) != 60:
        fail("Urdu A1/A2 must each contain exactly 60 canonical passages")
    if len(b1) != 24 or [r.get("sequence") for r in b1] != list(range(1,25)):
        fail("Urdu B1 must contain exactly sequences 1-24 before Unit 5 promotion")

    status_path = ROOT / "reading" / "STATUS.json"
    continuation_path = ROOT / "reading" / "CONTINUATION.json"
    plan_path = ROOT / "reading" / "planning" / "ACTIVE_GENERATION_PLAN.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    continuation = json.loads(continuation_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if status["current"]["canonical_passages"] != 864 or status["languages"]["urdu"]["canonical_passages"] != 144:
        fail("STATUS counts are no longer the reviewed Unit 5 pre-promotion state")
    if status["current"]["active_language"] != "urdu" or status["current"]["active_level"] != "B1":
        fail("STATUS active frontier is no longer Urdu B1")
    if plan.get("active_unit") != 5 or plan.get("start_sequence") != 25 or plan.get("existing_active_level_passages") != 24:
        fail("ACTIVE_GENERATION_PLAN no longer points to Urdu B1 Unit 5 / sequence 25")
    action = continuation.get("active_frontier",{}).get("production",{}).get("action","")
    if "Urdu B1 Unit 5 / sequence 25" not in action:
        fail("CONTINUATION frontier no longer points to Unit 5 / sequence 25")

    before = TARGET.read_bytes()
    before_sha = hashlib.sha256(before).hexdigest()
    taught_ids = {t["id"] for r in a1 + a2 + b1 for t in r.get("new_lexical_targets", [])}
    collision = sorted(taught_ids.intersection(EXPECTED_TARGETS))
    if collision:
        fail(f"Unit 5 target-ID freshness collision: {collision}")

    rows: list[dict] = []
    learner_parts: list[str] = []
    for i in range(1,7):
        path = STAGE / f"ur-b1-u05-p{i:02d}.json"
        if not path.exists():
            fail(f"missing candidate {path.relative_to(ROOT)}")
        r = json.loads(path.read_text(encoding="utf-8"))
        r["word_count"] = len(r["text"].split())
        r["sentence_count"] = r["text"].count("۔")
        for t in r.get("new_lexical_targets", []):
            t["exposures_in_text"] = r["text"].count(t["form"])
        path.write_text(json.dumps(r, ensure_ascii=False, separators=(",",":")) + "\n", encoding="utf-8")
        rows.append(r)
        learner_parts += [r["title"], r["text"]]
        learner_parts += [q["prompt"] for q in r["questions"]]
        learner_parts += [a["answer"] for a in r["answer_key"]]

    if [r["id"] for r in rows] != EXPECTED_IDS or [r["sequence"] for r in rows] != EXPECTED_SEQ:
        fail("Unit 5 ID/sequence contract failed")
    if [r["passage_type"] for r in rows] != EXPECTED_ROLES:
        fail("Unit 5 role cycle failed")
    if [len(r["new_lexical_targets"]) for r in rows] != [3,3,3,3,3,0]:
        fail("Unit 5 target distribution failed")
    if [t["id"] for r in rows[:5] for t in r["new_lexical_targets"]] != EXPECTED_TARGETS:
        fail("Unit 5 target order/identity failed")
    if any(t["exposures_in_text"] < 1 for r in rows for t in r["new_lexical_targets"]):
        fail("Unit 5 has a new target absent from passage text")
    if not REQUIRED_GENRES.issubset({r["genre"] for r in rows}):
        fail("required Unit 5 genres are missing")

    prior_learner = ""
    for r in rows[:5]:
        for t in r["new_lexical_targets"]:
            if t["form"] in prior_learner:
                fail(f"premature exact-form exposure before first introduction: {t['form']} / {t['id']}")
        prior_learner += "\n" + "\n".join(
            [r["title"],r["text"]] + [q["prompt"] for q in r["questions"]] + [a["answer"] for a in r["answer_key"]]
        )

    p6 = rows[-1]
    if p6["new_lexical_targets"] or not p6["speed_training"]["timed"] or p6["speed_training"]["new_word_policy"] != "none":
        fail("Unit 5 P6 checkpoint policy failed")
    expected_forms = {t["form"] for r in rows[:5] for t in r["new_lexical_targets"]}
    review_forms = {t["form"] for t in p6["review_lexical_targets"] if t["representation"] == "running_text"}
    if review_forms != expected_forms or any(form not in p6["text"] for form in expected_forms):
        fail("Unit 5 P6 does not visibly recycle all 15 new targets")

    for r in rows:
        missing = req - set(r)
        if missing:
            fail(f"{r['id']} missing required fields: {sorted(missing)}")
        if r["passage_type"] not in ptypes or any(d not in domains for d in r["domains"]):
            fail(f"schema enum failure: {r['id']}")
        if len(r["questions"]) != 10 or len(r["answer_key"]) != 10:
            fail(f"10x10 question-answer contract failed: {r['id']}")
        if not 220 <= r["word_count"] <= 320:
            fail(f"B1 word band failed {r['id']}: {r['word_count']}")
        qids = {q["id"] for q in r["questions"]}
        aids = {a["id"] for a in r["answer_key"]}
        if qids != {f"q{i}" for i in range(1,11)} or aids != {f"a{i}" for i in range(1,11)}:
            fail(f"question/answer IDs drifted: {r['id']}")
        amap = {a["id"]:a for a in r["answer_key"]}
        for t in r.get("new_lexical_targets", []):
            if any(s not in strategies for s in t["context_strategy"]):
                fail(f"invalid context strategy: {r['id']}/{t['id']}")
        for q in r["questions"]:
            if q["type"] not in qtypes or q["answer_id"] not in amap or amap[q["answer_id"]]["question_id"] != q["id"]:
                fail(f"QA link/type failure: {r['id']}/{q['id']}")

    if re.search(r"[A-Za-z\u0900-\u097F]", "\n".join(learner_parts)):
        fail("learner-facing Latin/Devanagari leakage")

    append_payload = "".join(json.dumps(r, ensure_ascii=False, separators=(",",":")) + "\n" for r in rows).encode("utf-8")
    TARGET.write_bytes(before + append_payload)
    after = TARGET.read_bytes()
    if after[:len(before)] != before:
        fail("pre-existing Urdu B1 canonical bytes changed")
    final = jl(TARGET)
    if len(final) != 30 or [r["sequence"] for r in final] != list(range(1,31)) or [r["id"] for r in final[-6:]] != EXPECTED_IDS:
        fail("canonical B1 post-append check failed")

    (STAGE / "manifest.json").write_text(json.dumps({
        "schema_version":1,"project_id":"LANG-A1C2","language":"ur","cefr":"B1","unit":5,
        "date":DATE,"status":"CANONICALIZED","canonical_target":"reading/urdu/b1/passages.jsonl",
        "sequence_range":[25,30],"record_count":6,"release_promotion":False
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validation = {
        "schema_version":1,"project_id":"LANG-A1C2","language":"ur","cefr":"B1","unit":5,
        "date":DATE,"canonicalized":True,"release_promotion":False,
        "word_counts":[r["word_count"] for r in rows],
        "checks":{
            "prior_a1_a2_60_each":"PASS","prior_b1_sequences_1_through_24_exact":"PASS",
            "freshness_across_all_prior_urdu_target_ids":"PASS","record_count":"PASS",
            "sequence_25_through_30":"PASS","role_cycle":"PASS","question_answer_10x10":"PASS",
            "bidirectional_links":"PASS","new_target_distribution_3_3_3_3_3_0":"PASS",
            "new_target_text_exposure":"PASS","first_introduction_order":"PASS","required_genres":"PASS",
            "p6_checkpoint_policy":"PASS","p6_all_target_recycling":"PASS","learner_script_scan":"PASS",
            "schema_required_fields_enums_and_context_strategies":"PASS","b1_word_band":"PASS",
            "preexisting_canonical_bytes_preserved":"PASS"
        }
    }
    (ROOT / "reading" / "audit" / "urdu_b1_u05_generation_validation_2026-08-24.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    promotion = {
        "schema_version":1,"project_id":"LANG-A1C2","language":"ur","cefr":"B1","unit":5,
        "date":DATE,"status":"CANONICAL_PROMOTION_PASS","release_promotion":False,
        "before_record_count":24,"after_record_count":30,
        "appended_sequences":EXPECTED_SEQ,"appended_ids":EXPECTED_IDS,
        "preexisting_bytes_preserved_exactly":True,
        "canonical_sha256_before":before_sha,
        "canonical_sha256_after":hashlib.sha256(after).hexdigest()
    }
    (ROOT / "reading" / "audit" / "urdu_b1_u05_promotion_2026-08-24.json").write_text(
        json.dumps(promotion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lex_path = ROOT / "reading" / "audit" / "urdu_b1_u05_lexical_sense_check_2026-08-24.json"
    lex = json.loads(lex_path.read_text(encoding="utf-8"))
    lex["status"] = "PASS_FOR_GENERATION_TARGET_SENSES_AND_CANONICAL_FRESHNESS"
    lex["freshness_result"] = "PASS"
    lex["freshness_scope"] = "Exact target IDs checked against all canonical Urdu A1, A2, and B1 sequences 1-24 immediately before Unit 5 append."
    lex_path.write_text(json.dumps(lex, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status["current"]["canonical_passages"] = 870
    status["current"]["remaining_generation_passages"] = 210
    u = status["languages"]["urdu"]
    u["generation_state"] = "B1_IN_PROGRESS"
    u["canonical_passages"] = 150
    u["remaining_generation_passages"] = 210
    u["next_generation_level"] = "B1"
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    continuation["production"]["canonical_passages"] = 870
    cu = continuation["production"]["urdu"]
    cu["state"] = "B1_GENERATION_IN_PROGRESS"
    cu["canonical_passages"] = 150
    cu["next_generation_level"] = "B1"
    continuation["active_frontier"]["production"] = {
        "language":"urdu","level":"B1",
        "action":"Continue generation-first production from Urdu B1 Unit 6 / sequence 31 using the canonical roadmap and ten-question contract."
    }
    continuation["exact_next_actions"] = [
        "Validate the routed state bundle and live canonical counts.",
        "Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu B1 Unit 6 generation at sequence 31.",
        "Keep release/educator verification separate from generation progress."
    ]
    continuation_path.write_text(json.dumps(continuation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    plan["active_language"] = "urdu"
    plan["active_level"] = "B1"
    plan["active_unit"] = 6
    plan["start_sequence"] = 31
    plan["canonical_active_path"] = "reading/urdu/b1/passages.jsonl"
    plan["existing_active_level_passages"] = 30
    plan["roadmap_lookup"] = "$.levels.B1"
    plan["active_unit_roadmap"] = {
        "unit":6,"theme":"travel, culture, and misunderstanding",
        "genres":["narrative","cultural explanation","reflection"]
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tasks_path = ROOT / "reading" / "TASKS.md"
    tasks = tasks_path.read_text(encoding="utf-8")
    tasks = replace_once(tasks, "Canonical production frontier: **Urdu B1, Unit 5, sequence 25**.",
                         "Canonical production frontier: **Urdu B1, Unit 6, sequence 31**.", "TASKS frontier")
    tasks = replace_once(tasks, "- Urdu: 144/360 generated; A1-A2 complete, B1 in progress.",
                         "- Urdu: 150/360 generated; A1-A2 complete, B1 in progress.", "TASKS Urdu total")
    tasks = replace_once(tasks, "- Project: 864/1080 generated.",
                         "- Project: 870/1080 generated.", "TASKS project total")
    tasks_path.write_text(tasks, encoding="utf-8")

    handoff_path = ROOT / "reading" / "AGENT_HANDOFF_V2.md"
    h = handoff_path.read_text(encoding="utf-8")
    h = replace_once(h, "- Canonical generated total: **864**.", "- Canonical generated total: **870**.", "handoff total")
    h = replace_once(h, "- Urdu: **144/360**; A1-A2 generation complete and B1 generation in progress.",
                     "- Urdu: **150/360**; A1-A2 generation complete and B1 generation in progress.", "handoff Urdu")
    h = replace_once(h, "Continue **Urdu B1**, starting from Unit 5 / sequence 25, under:",
                     "Continue **Urdu B1**, starting from Unit 6 / sequence 31, under:", "handoff frontier")
    h = replace_once(h,
                     "B1 Unit 5 uses the roadmap theme **health, habits, and evidence** with `popular-science explanation`, `case story`, and `advice critique` genres.",
                     "B1 Unit 6 uses the roadmap theme **travel, culture, and misunderstanding** with `narrative`, `cultural explanation`, and `reflection` genres.",
                     "handoff roadmap")
    h = replace_once(h,
                     "resume guarded generation at **Urdu B1 Unit 5 / sequence 25** using the B1 Unit 5 roadmap theme `health, habits, and evidence`.",
                     "resume guarded generation at **Urdu B1 Unit 6 / sequence 31** using the B1 Unit 6 roadmap theme `travel, culture, and misunderstanding`.",
                     "handoff exact next")
    handoff_path.write_text(h, encoding="utf-8")

    print("Unit 5 canonical promotion prepared: 24 -> 30 B1 records")
    print("Production totals prepared: 864 -> 870 project; Urdu 144 -> 150")
    print("Next frontier prepared: Urdu B1 Unit 6 / sequence 31")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
