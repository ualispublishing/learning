#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 2 comprehension/grounding repair.

Exactly one ambiguity repair is allowed: p01/q9 must make the keyed «قبل» unique.
No passage text, answer, lexical metadata, quality flag, or other record may change.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/a1/passages.jsonl"
RELEASE = READING / "RELEASE_STATUS.json"
DECISION = READING / "audit/arabic_gate_c_decisions_2026-09-05/a1_u02.json"
EXPECTED_GIT_BLOB = "5d00d03e7c8ebbc70009bae4d2950e4a1439ad8e"
EXPECTED_MANIFEST_SHA256 = "3a9393aab226940bc04708495226d2948bdbd0cb108bccd56c1fb0a09e4918dc"
OLD_PROMPT = "أكمل: أغسل يدي _____ الطعام."
NEW_PROMPT = "أكمل بما يدل على الزمن الأسبق: أغسل يدي _____ الطعام."
NOTE = (
    "2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 2): "
    "60 question-answer pairs reviewed; one ambiguous transfer prompt repaired; "
    "no educator/publication release claim."
)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def main() -> None:
    if DECISION.exists():
        raise SystemExit("refusing duplicate Gate C A1 Unit 2 frontier")
    manifest = json.loads((READING / "STATE_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("aggregate_sha256") != EXPECTED_MANIFEST_SHA256:
        raise SystemExit("live state manifest drift; rebind Gate C Unit 2 frontier before writing")
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    arabic = release.get("languages", {}).get("arabic", {})
    if arabic.get("release_state") != "REOPEN_REQUIRED" or arabic.get("educator_release_ready") is not False:
        raise SystemExit("Arabic release boundary is not blocked as expected")
    b = arabic.get("naturalness_review_progress", {})
    c = arabic.get("comprehension_review_progress", {})
    d = arabic.get("latest_deterministic_gate", {})
    if (b.get("status"), b.get("fresh_records_reviewed"), b.get("fresh_records_with_findings"), b.get("fresh_findings")) != (
        "FRESH_GATE_B_INTERNAL_REVIEW_COMPLETE", 360, 308, 560
    ):
        raise SystemExit("Gate B frontier drift")
    if (c.get("fresh_records_reviewed"), c.get("fresh_qa_pairs_reviewed"), c.get("fresh_records_with_findings"), c.get("fresh_findings")) != (6, 60, 1, 1):
        raise SystemExit("Gate C A1 Unit 1 frontier is not exact")
    if c.get("decision_artifacts") != ["reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u01.json"]:
        raise SystemExit("unexpected Gate C decision frontier")
    if d.get("open_findings") != 1080 or d.get("finding_classes") != {
        "coverage_missing_or_zero": 360,
        "coverage_not_pass": 360,
        "not_approved": 360,
    }:
        raise SystemExit("unexpected deterministic blocker frontier")

    raw = PATH.read_bytes()
    if git_blob_sha(raw) != EXPECTED_GIT_BLOB:
        raise SystemExit("Arabic A1 canonical blob drift; re-review before writing")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("Arabic A1 canonical layout drift")
    expected_ids = [f"ar-a1-u02-p{i:02d}" for i in range(1, 7)]
    if [rows[i].get("id") for i in range(6, 12)] != expected_ids:
        raise SystemExit("Arabic A1 Unit 2 frontier/id drift")

    before = {r["id"]: json.loads(json.dumps(r, ensure_ascii=False)) for r in rows[6:12]}
    target = rows[6]
    q_by_id = {q.get("id"): q for q in target.get("questions", [])}
    a_by_qid = {a.get("question_id"): a for a in target.get("answer_key", [])}
    q9 = q_by_id.get("q9", {})
    if q9.get("prompt") != OLD_PROMPT or q9.get("type") != "cloze_transfer" or q9.get("target_ids") != ["ar-r63"]:
        raise SystemExit("p01/q9 prompt/type/target drift")
    if a_by_qid.get("q9", {}).get("answer") != "قبل":
        raise SystemExit("p01/q9 keyed answer drift")
    q9["prompt"] = NEW_PROMPT
    target["revision"] = int(target.get("revision", 0) or 0) + 1
    notes = target.setdefault("quality", {}).setdefault("notes", [])
    if NOTE not in notes:
        notes.append(NOTE)

    for i, pid in enumerate(expected_ids, start=6):
        old = before[pid]
        new = rows[i]
        if len(new.get("questions", [])) != 10 or len(new.get("answer_key", [])) != 10:
            raise SystemExit(f"{pid}: 10Q/10A invariant failed")
        if {q.get("answer_id") for q in new["questions"]} != {a.get("id") for a in new["answer_key"]}:
            raise SystemExit(f"{pid}: answer linkage drift")
        if new.get("text") != old.get("text") or new.get("answer_key") != old.get("answer_key"):
            raise SystemExit(f"{pid}: Gate C Unit 2 must not change passage text or answers")
        if new.get("new_lexical_targets") != old.get("new_lexical_targets") or new.get("review_lexical_targets") != old.get("review_lexical_targets"):
            raise SystemExit(f"{pid}: lexical metadata drift")
        for key in ("status", "coverage_check", "linguistic_review", "pedagogical_review", "answer_key_check", "schema_check"):
            if new.get("quality", {}).get(key) != old.get("quality", {}).get(key):
                raise SystemExit(f"{pid}: quality flag {key} changed")
        if pid == "ar-a1-u02-p01":
            old_q = old["questions"]
            new_q = new["questions"]
            diffs = [(oq.get("id"), oq.get("prompt"), nq.get("prompt")) for oq, nq in zip(old_q, new_q) if oq != nq]
            if diffs != [("q9", OLD_PROMPT, NEW_PROMPT)]:
                raise SystemExit(f"p01: unexpected question changes: {diffs}")
        elif new != old:
            raise SystemExit(f"{pid}: clean PASS record changed unexpectedly")

    PATH.write_text("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": "C", "level": "A1", "unit": 2,
        "records_reviewed": 6, "qa_pairs_reviewed": 60,
        "records_repaired": 1, "fresh_findings": 1,
        "repaired": "ar-a1-u02-p01/question q9",
        "quality_promotion": False, "release_claim": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
