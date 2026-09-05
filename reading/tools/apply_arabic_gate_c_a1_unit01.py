#!/usr/bin/env python3
"""Apply the first fresh Arabic Gate C comprehension/answer-grounding repair.

Scope is deliberately narrow: Arabic A1 Unit 1, exact-current canonical bytes,
one contextual answer-sense repair, no quality promotion, and no release claim.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/a1/passages.jsonl"
RELEASE = READING / "RELEASE_STATUS.json"
DECISION = READING / "audit/arabic_gate_c_decisions_2026-09-05/a1_u01.json"
EXPECTED_SHA256 = "bbc91220ddf54e0f26765570071bcd7b8e099613ddab0f8e5dba995e7569ed1c"
EXPECTED_MANIFEST_SHA256 = "f442199c624f688418c9be651e166de8d1ccf7f582582616202b0d8e26ad2312"
NOTE = (
    "2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 1): "
    "60 question-answer pairs reviewed; one contextual-sense key repaired; "
    "no educator/publication release claim."
)
OLD_ANSWER = "أن الأمر ممكن."
NEW_ANSWER = "أن ليلى تطلب الإذن لأخذ كتاب."
PROMPT = "ماذا تعني «يمكن» في قول ليلى: «هل يمكن أن آخذ كتابا؟»"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if DECISION.exists():
        raise SystemExit("refusing duplicate Gate C A1 Unit 1 frontier")

    manifest = json.loads((READING / "STATE_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("aggregate_sha256") != EXPECTED_MANIFEST_SHA256:
        raise SystemExit("live state manifest drift; rebind Gate C frontier before writing")

    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    arabic = release.get("languages", {}).get("arabic", {})
    if arabic.get("release_state") != "REOPEN_REQUIRED" or arabic.get("educator_release_ready") is not False:
        raise SystemExit("Arabic release boundary is not the expected blocked state")
    natural = arabic.get("naturalness_review_progress", {})
    if natural.get("status") != "FRESH_GATE_B_INTERNAL_REVIEW_COMPLETE" or natural.get("fresh_records_reviewed") != 360:
        raise SystemExit("Gate B must be complete before Gate C starts")
    gate = arabic.get("latest_deterministic_gate", {})
    if gate.get("open_findings") != 1080 or gate.get("finding_classes") != {
        "coverage_missing_or_zero": 360,
        "coverage_not_pass": 360,
        "not_approved": 360,
    }:
        raise SystemExit("unexpected deterministic frontier before Gate C")
    cprog = arabic.get("comprehension_review_progress")
    if cprog not in (None, {}) and int(cprog.get("fresh_records_reviewed", 0) or 0) != 0:
        raise SystemExit("Gate C progress already exists; expected fresh frontier")

    raw = PATH.read_bytes()
    if sha256(raw) != EXPECTED_SHA256:
        raise SystemExit("Arabic A1 canonical drift; re-review before writing")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("Arabic A1 canonical layout drift")
    expected_ids = [f"ar-a1-u01-p{i:02d}" for i in range(1, 7)]
    if [rows[i].get("id") for i in range(6)] != expected_ids:
        raise SystemExit("Arabic A1 Unit 1 frontier/id drift")

    before = {r["id"]: json.loads(json.dumps(r, ensure_ascii=False)) for r in rows[:6]}
    target = rows[3]
    if target.get("id") != "ar-a1-u01-p04":
        raise SystemExit("unexpected target record")
    q_by_id = {q.get("id"): q for q in target.get("questions", [])}
    a_by_qid = {a.get("question_id"): a for a in target.get("answer_key", [])}
    if q_by_id.get("q3", {}).get("prompt") != PROMPT:
        raise SystemExit("p04/q3 prompt drift")
    if a_by_qid.get("q3", {}).get("answer") != OLD_ANSWER:
        raise SystemExit("p04/q3 answer drift")
    a_by_qid["q3"]["answer"] = NEW_ANSWER
    target["revision"] = int(target.get("revision", 0) or 0) + 1
    notes = target.setdefault("quality", {}).setdefault("notes", [])
    if NOTE not in notes:
        notes.append(NOTE)

    for i, pid in enumerate(expected_ids):
        old = before[pid]
        new = rows[i]
        if len(new.get("questions", [])) != 10 or len(new.get("answer_key", [])) != 10:
            raise SystemExit(f"{pid}: 10Q/10A invariant failed")
        qlinks = {q.get("answer_id") for q in new["questions"]}
        aids = {a.get("id") for a in new["answer_key"]}
        if qlinks != aids:
            raise SystemExit(f"{pid}: answer linkage drift")
        if new.get("text") != old.get("text"):
            raise SystemExit(f"{pid}: Gate C repair must not change passage text")
        if new.get("questions") != old.get("questions"):
            raise SystemExit(f"{pid}: Gate C repair must not change questions")
        if new.get("new_lexical_targets") != old.get("new_lexical_targets") or new.get("review_lexical_targets") != old.get("review_lexical_targets"):
            raise SystemExit(f"{pid}: lexical metadata drift")
        for key in ("status", "coverage_check", "linguistic_review", "pedagogical_review", "answer_key_check", "schema_check"):
            if new.get("quality", {}).get(key) != old.get("quality", {}).get(key):
                raise SystemExit(f"{pid}: quality flag {key} changed")
        if pid != "ar-a1-u01-p04" and new != old:
            raise SystemExit(f"{pid}: clean PASS record changed unexpectedly")

    PATH.write_text("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": "C",
        "level": "A1",
        "unit": 1,
        "records_reviewed": 6,
        "qa_pairs_reviewed": 60,
        "records_repaired": 1,
        "fresh_findings": 1,
        "repaired": "ar-a1-u01-p04/answer q3",
        "quality_promotion": False,
        "release_claim": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
