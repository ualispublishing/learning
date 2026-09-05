#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 2 decisions and rebind affected Gate B evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
CANON = READING / "arabic/a1/passages.jsonl"
OUT = READING / "audit/arabic_gate_c_decisions_2026-09-05/a1_u02.json"
GATE_B = READING / "audit/arabic_gate_b_decisions_2026-08-30/a1_u02.json"
OLD_GATE_B_HASHES = {
    "ar-a1-u02-p01": "ee818e3fed88d1b712409db5a3778c329abdea0ed92881f5bf505162156901f7",
    "ar-a1-u02-p02": "66490225ea2e10231f1287b67d5efb06477f11813ea81e791d55714cfebd777d",
    "ar-a1-u02-p03": "dbefbdd6fdba739d31566c6ac9a3e84b39695dc82dc78fbfa4e5f316989778f1",
    "ar-a1-u02-p04": "251db0bfd0a1ad67980db2e8855e692290cae7468507b11d678e0689b1be40c8",
    "ar-a1-u02-p05": "ca99c0dadb4db643a43c614a3e7bce56bd4844c7d93e18d82c684a2b09e2408b",
    "ar-a1-u02-p06": "edb2ae3ad728da96369583a34f950aeb627da147052da00c66e0dd86709945e0",
}
OLD_PROMPT = "أكمل: أغسل يدي _____ الطعام."
NEW_PROMPT = "أكمل بما يدل على الزمن الأسبق: أغسل يدي _____ الطعام."
REVALIDATION = {
    "date": "2026-09-05",
    "gate_c_artifact": "reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u02.json",
    "scope": ["ar-a1-u02-p01 question q9"],
    "gate_b_language_recheck": "PASS",
    "reason": "Gate C constrained one ambiguous transfer prompt so the keyed قبل is uniquely defensible; the replacement was rechecked for A1 MSA wording and Gate B was rebound to exact-current learner-facing content.",
    "release_claim": False,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def learner_payload(record: dict) -> dict:
    answers = {a.get("question_id"): a for a in record.get("answer_key", [])}
    notes = "\n".join(record.get("quality", {}).get("notes", []))
    has_hist = "naturalness review" in notes.lower() or "naturalness" in notes.lower()
    return {
        "passage_id": record.get("id"), "unit": record.get("unit"),
        "sequence": record.get("sequence"), "cefr": record.get("cefr"),
        "title": record.get("title"), "genre": record.get("genre"),
        "text": record.get("text"),
        "qa": [{
            "question_id": q.get("id"), "type": q.get("type"), "prompt": q.get("prompt"),
            "answer": answers.get(q.get("id"), {}).get("answer"),
            "explanation": answers.get(q.get("id"), {}).get("explanation", ""),
        } for q in record.get("questions", [])],
        "historical_naturalness_note_present": has_hist,
    }


def learner_hash(record: dict) -> str:
    return sha256_bytes(json.dumps(learner_payload(record), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def build_doc(rows: list[dict], canon_sha: str) -> tuple[dict, dict[str, str]]:
    expected_ids = [f"ar-a1-u02-p{i:02d}" for i in range(1, 7)]
    by_id = {r.get("id"): r for r in rows}
    current_hashes = {pid: learner_hash(by_id[pid]) for pid in expected_ids}
    q9 = {q.get("id"): q for q in by_id["ar-a1-u02-p01"].get("questions", [])}.get("q9", {})
    if q9.get("prompt") != NEW_PROMPT:
        raise SystemExit("p01/q9 reviewed Gate C prompt is not present")
    for pid in expected_ids:
        if pid == "ar-a1-u02-p01":
            if current_hashes[pid] == OLD_GATE_B_HASHES[pid]:
                raise SystemExit("p01 learner-facing hash did not change")
        elif current_hashes[pid] != OLD_GATE_B_HASHES[pid]:
            raise SystemExit(f"{pid}: unexpected learner-facing drift outside Gate C repair")

    decisions = []
    for pid in expected_ids:
        if pid == "ar-a1-u02-p01":
            decisions.append({
                "passage_id": pid, "learner_facing_sha256": current_hashes[pid],
                "decision": "PASS_AFTER_REPAIR", "qa_pairs_reviewed": 10,
                "finding_count": 1,
                "findings": [{
                    "finding_id": f"{pid}-gC-01", "field": "question q9",
                    "dimension": "competing_answer_ambiguity", "severity": "major",
                    "status": "REPAIRED",
                    "rationale": "The original cloze «أغسل يدي _____ الطعام» admits both قبل and بعد as grammatical, plausible answers, so the keyed قبل was not unique. Constrain the prompt to the earlier-time relation while preserving the target and keyed answer.",
                }],
            })
        else:
            decisions.append({
                "passage_id": pid, "learner_facing_sha256": current_hashes[pid],
                "decision": "PASS", "qa_pairs_reviewed": 10,
                "finding_count": 0, "findings": [],
            })
    doc = {
        "schema_version": 1, "project_id": "LANG-A1C2", "language": "arabic",
        "level": "A1", "unit": 2, "date": "2026-09-05",
        "gate": "Gate C — comprehension and answer-grounding audit",
        "canonical_path": "reading/arabic/a1/passages.jsonl", "canonical_sha256": canon_sha,
        "records_reviewed": 6, "qa_pairs_reviewed": 60,
        "records_with_findings": 1, "fresh_findings": 1,
        "decisions": decisions, "quality_promotion": False, "release_claim": False,
        "guard": "Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; the level SHA records the review-time snapshot and does not replace exact-current record validation.",
    }
    return doc, current_hashes


def verify_gate_b(gate_b: dict, current_hashes: dict[str, str]) -> None:
    expected_ids = [f"ar-a1-u02-p{i:02d}" for i in range(1, 7)]
    bdec = {d.get("passage_id"): d for d in gate_b.get("decisions", [])}
    if set(bdec) != set(expected_ids):
        raise SystemExit("unexpected A1 Unit 2 Gate B scope")
    for pid in expected_ids:
        if bdec[pid].get("learner_facing_sha256") != current_hashes[pid]:
            raise SystemExit(f"{pid}: Gate B current learner-facing hash mismatch")
    if gate_b.get("post_gate_c_revalidations", []).count(REVALIDATION) != 1:
        raise SystemExit("Gate B Unit 2 must contain exactly one matching post-Gate-C revalidation")


def main() -> None:
    raw = CANON.read_bytes()
    canon_sha = sha256_bytes(raw)
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("Arabic A1 layout drift")
    doc, current_hashes = build_doc(rows, canon_sha)

    if OUT.exists():
        if json.loads(OUT.read_text(encoding="utf-8")) != doc:
            raise SystemExit("existing Gate C Unit 2 evidence differs from exact-current regenerated evidence")
        verify_gate_b(json.loads(GATE_B.read_text(encoding="utf-8")), current_hashes)
        print(json.dumps({"unit": 2, "idempotent_verification": True, "records_reviewed": 6, "qa_pairs_reviewed": 60, "fresh_findings": 1, "release_claim": False}, ensure_ascii=False, indent=2))
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    gate_b = json.loads(GATE_B.read_text(encoding="utf-8"))
    if gate_b.get("project_id") != "LANG-A1C2" or gate_b.get("level") != "A1" or gate_b.get("unit") != 2:
        raise SystemExit("unexpected Gate B Unit 2 identity")
    bdec = {d.get("passage_id"): d for d in gate_b.get("decisions", [])}
    if set(bdec) != set(OLD_GATE_B_HASHES):
        raise SystemExit("unexpected Gate B Unit 2 decision scope")
    for pid, old_hash in OLD_GATE_B_HASHES.items():
        if bdec[pid].get("learner_facing_sha256") != old_hash:
            raise SystemExit(f"{pid}: Gate B pre-rebind hash drift")
    gate_b["canonical_sha256"] = canon_sha
    for pid, new_hash in current_hashes.items():
        bdec[pid]["learner_facing_sha256"] = new_hash
    revals = gate_b.setdefault("post_gate_c_revalidations", [])
    if REVALIDATION in revals:
        raise SystemExit("duplicate Unit 2 post-Gate-C revalidation before first record")
    revals.append(REVALIDATION)
    GATE_B.write_text(json.dumps(gate_b, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"unit": 2, "idempotent_verification": False, "records_reviewed": 6, "qa_pairs_reviewed": 60, "records_with_findings": 1, "fresh_findings": 1, "canonical_sha256": canon_sha, "release_claim": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
