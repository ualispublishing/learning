#!/usr/bin/env python3
"""Record Arabic Gate C A1 Unit 1 decisions and rebind Gate B after the repair.

The Gate C repair changes one learner-facing answer. This recorder therefore also
revalidates the affected wording for Gate B and refreshes the existing A1 Unit 1
Gate B hashes so both evidence streams bind to the same exact-current corpus.
It is intentionally idempotent so a rebase/regeneration pass can verify the exact
same evidence without creating duplicate decisions or revalidation entries.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
CANON = READING / "arabic/a1/passages.jsonl"
OUT = READING / "audit/arabic_gate_c_decisions_2026-09-05/a1_u01.json"
GATE_B = READING / "audit/arabic_gate_b_decisions_2026-08-30/a1_u01.json"
OLD_CANON_SHA = "bbc91220ddf54e0f26765570071bcd7b8e099613ddab0f8e5dba995e7569ed1c"
OLD_GATE_B_HASHES = {
    "ar-a1-u01-p01": "47bb8383fa776fef52b074fbee12d3d17ba32b93618683b8486e351735b8c5c7",
    "ar-a1-u01-p02": "8f372fe648ebc29a3ee291aef03b51140f0c171a9e4dff74d24e0a0b3bbcd56c",
    "ar-a1-u01-p03": "db8b249d70d529c34a7a2db24b7b291c3240be89dece568bb32c4dccb693866c",
    "ar-a1-u01-p04": "9f626a0e176e09696b84df528ffbd17dc3b78f035a0c63ba9d88df931d0896f3",
    "ar-a1-u01-p05": "d3b7cb444d9917395795941b60ec4ef8ae9450324d8f01dc72b90126200fd284",
    "ar-a1-u01-p06": "7cc0f20774fb9bd79e26e80fd3da63f1ba7db147228b3eefc1cf0a7919b7480f",
}
EXPECTED_NEW_ANSWER = "أن ليلى تطلب الإذن لأخذ كتاب."
REVALIDATION = {
    "date": "2026-09-05",
    "gate_c_artifact": "reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u01.json",
    "scope": ["ar-a1-u01-p04 answer q3"],
    "gate_b_language_recheck": "PASS",
    "reason": "Gate C repaired one contextual-sense answer; the replacement was rechecked for MSA grammar/naturalness and the Gate B learner-facing hash was rebound to exact-current content.",
    "release_claim": False,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def learner_payload(record: dict) -> dict:
    answers = {a.get("question_id"): a for a in record.get("answer_key", [])}
    qa = []
    for q in record.get("questions", []):
        a = answers.get(q.get("id"), {})
        qa.append({
            "question_id": q.get("id"),
            "type": q.get("type"),
            "prompt": q.get("prompt"),
            "answer": a.get("answer"),
            "explanation": a.get("explanation", ""),
        })
    return {
        "passage_id": record.get("id"),
        "unit": record.get("unit"),
        "sequence": record.get("sequence"),
        "cefr": record.get("cefr"),
        "title": record.get("title"),
        "genre": record.get("genre"),
        "text": record.get("text"),
        "qa": qa,
    }


def learner_hash(record: dict) -> str:
    raw = json.dumps(learner_payload(record), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(raw)


def verify_current_gate_b(gate_b: dict, canon_sha: str, current_hashes: dict[str, str], expected_ids: list[str]) -> None:
    if gate_b.get("canonical_sha256") != canon_sha:
        raise SystemExit("Gate B current canonical binding does not match Gate C repaired corpus")
    bdec = {d.get("passage_id"): d for d in gate_b.get("decisions", [])}
    if set(bdec) != set(expected_ids):
        raise SystemExit("unexpected A1 Unit 1 Gate B decision scope")
    for pid in expected_ids:
        if bdec[pid].get("learner_facing_sha256") != current_hashes[pid]:
            raise SystemExit(f"{pid}: Gate B current learner-facing hash mismatch")
    revals = gate_b.get("post_gate_c_revalidations", [])
    if revals.count(REVALIDATION) != 1:
        raise SystemExit("Gate B must contain exactly one matching post-Gate-C revalidation")


def main() -> None:
    raw = CANON.read_bytes()
    canon_sha = sha256_bytes(raw)
    if canon_sha == OLD_CANON_SHA:
        raise SystemExit("Gate C canonical repair did not occur")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    expected_ids = [f"ar-a1-u01-p{i:02d}" for i in range(1, 7)]
    if len(rows) != 60 or [rows[i].get("id") for i in range(6)] != expected_ids:
        raise SystemExit("A1 Unit 1 canonical layout drift")
    by_id = {r.get("id"): r for r in rows}
    p04_answers = {a.get("question_id"): a for a in by_id["ar-a1-u01-p04"].get("answer_key", [])}
    if p04_answers.get("q3", {}).get("answer") != EXPECTED_NEW_ANSWER:
        raise SystemExit("p04/q3 repair is not the reviewed Gate C answer")

    current_hashes = {pid: learner_hash(by_id[pid]) for pid in expected_ids}
    for pid in expected_ids:
        if pid != "ar-a1-u01-p04" and current_hashes[pid] != OLD_GATE_B_HASHES[pid]:
            raise SystemExit(f"{pid}: unexpected learner-facing drift outside Gate C repair")
    if current_hashes["ar-a1-u01-p04"] == OLD_GATE_B_HASHES["ar-a1-u01-p04"]:
        raise SystemExit("p04 learner-facing hash did not change")

    decisions = []
    for pid in expected_ids:
        if pid == "ar-a1-u01-p04":
            decisions.append({
                "passage_id": pid,
                "learner_facing_sha256": current_hashes[pid],
                "decision": "PASS_AFTER_REPAIR",
                "qa_pairs_reviewed": 10,
                "finding_count": 1,
                "findings": [{
                    "finding_id": f"{pid}-gC-01",
                    "field": "answer q3",
                    "dimension": "vocabulary_sense_grounding",
                    "severity": "major",
                    "status": "REPAIRED",
                    "rationale": "The question asks for the contextual meaning of «يمكن» in a permission request («هل يمكن أن آخذ كتابا؟»), but the key gave only generic possibility; repair the key to state that Leila is asking permission to take a book.",
                }],
            })
        else:
            decisions.append({
                "passage_id": pid,
                "learner_facing_sha256": current_hashes[pid],
                "decision": "PASS",
                "qa_pairs_reviewed": 10,
                "finding_count": 0,
                "findings": [],
            })

    doc = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "level": "A1",
        "unit": 1,
        "date": "2026-09-05",
        "gate": "Gate C — comprehension and answer-grounding audit",
        "canonical_path": "reading/arabic/a1/passages.jsonl",
        "canonical_sha256": canon_sha,
        "records_reviewed": 6,
        "qa_pairs_reviewed": 60,
        "records_with_findings": 1,
        "fresh_findings": 1,
        "decisions": decisions,
        "quality_promotion": False,
        "release_claim": False,
        "guard": "Fresh Gate C decisions bind to exact-current learner-facing hashes; this internal comprehension audit does not constitute educator/publication release approval.",
    }

    if OUT.exists():
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        if existing != doc:
            raise SystemExit("existing Gate C A1 Unit 1 evidence differs from exact-current regenerated evidence")
        verify_current_gate_b(json.loads(GATE_B.read_text(encoding="utf-8")), canon_sha, current_hashes, expected_ids)
        print(json.dumps({
            "gate_c_artifact": str(OUT.relative_to(ROOT)),
            "records_reviewed": 6,
            "qa_pairs_reviewed": 60,
            "records_with_findings": 1,
            "fresh_findings": 1,
            "gate_b_rebound": True,
            "canonical_sha256": canon_sha,
            "idempotent_verification": True,
            "quality_promotion": False,
            "release_claim": False,
        }, ensure_ascii=False, indent=2))
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    gate_b = json.loads(GATE_B.read_text(encoding="utf-8"))
    if gate_b.get("canonical_sha256") != OLD_CANON_SHA:
        raise SystemExit("A1 Unit 1 Gate B canonical binding is not the expected pre-Gate-C state")
    bdec = {d.get("passage_id"): d for d in gate_b.get("decisions", [])}
    if set(bdec) != set(expected_ids):
        raise SystemExit("unexpected A1 Unit 1 Gate B decision scope")
    for pid in expected_ids:
        if bdec[pid].get("learner_facing_sha256") != OLD_GATE_B_HASHES[pid]:
            raise SystemExit(f"{pid}: Gate B pre-rebind hash drift")
    gate_b["canonical_sha256"] = canon_sha
    for pid in expected_ids:
        bdec[pid]["learner_facing_sha256"] = current_hashes[pid]
    revals = gate_b.setdefault("post_gate_c_revalidations", [])
    if REVALIDATION in revals:
        raise SystemExit("unexpected duplicate Gate B post-Gate-C revalidation before first Gate C record")
    revals.append(REVALIDATION)
    GATE_B.write_text(json.dumps(gate_b, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "gate_c_artifact": str(OUT.relative_to(ROOT)),
        "records_reviewed": 6,
        "qa_pairs_reviewed": 60,
        "records_with_findings": 1,
        "fresh_findings": 1,
        "gate_b_rebound": True,
        "canonical_sha256": canon_sha,
        "idempotent_verification": False,
        "quality_promotion": False,
        "release_claim": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
