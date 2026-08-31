#!/usr/bin/env python3
"""Record fresh Arabic Gate B A1 Unit 1 decisions from authoritative rebuilt inventory.

This runs only after build_arabic_gate_b_naturalness_review.py. It deliberately does
not compute learner-facing hashes itself; it consumes the hashes produced by the
Gate B packet builder, then sync_arabic_gate_b_progress.py independently verifies
them against the same current inventory.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
CANONICAL = READING / "arabic/a1/passages.jsonl"
INVENTORY = READING / "audit/arabic_gate_b_naturalness_inventory_2026-08-30.json"
DECISION_DIR = READING / "audit/arabic_gate_b_decisions_2026-08-30"
DECISION_PATH = DECISION_DIR / "a1_u01.json"
EXPECTED_POST_REPAIR_SHA256 = "bbc91220ddf54e0f26765570071bcd7b8e099613ddab0f8e5dba995e7569ed1c"
EXPECTED_IDS = [f"ar-a1-u01-p{i:02d}" for i in range(1, 7)]
EXPECTED_FINDINGS = 18


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_repair_metadata():
    source = Path(__file__).with_name("apply_arabic_gate_b_a1_unit01.py")
    spec = importlib.util.spec_from_file_location("arabic_gate_b_a1_u01_meta", source)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load A1 Unit 1 Gate B repair metadata")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.FINDING_META


def main() -> None:
    raw = CANONICAL.read_bytes()
    canonical_sha = sha256_bytes(raw)
    if canonical_sha != EXPECTED_POST_REPAIR_SHA256:
        raise SystemExit(
            f"A1 post-repair canonical drift: expected {EXPECTED_POST_REPAIR_SHA256}, got {canonical_sha}"
        )

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("A1 canonical layout drift while recording Gate B decisions")
    if [rows[i].get("id") for i in range(6)] != EXPECTED_IDS:
        raise SystemExit("A1 Unit 1 id/layout drift while recording Gate B decisions")

    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if inv.get("project_id") != "LANG-A1C2" or inv.get("language") != "arabic":
        raise SystemExit("unexpected Gate B inventory identity")
    if inv.get("records") != 360 or inv.get("questions") != 3600 or inv.get("answers") != 3600:
        raise SystemExit("Gate B inventory corpus totals drift")
    a1 = inv.get("levels", {}).get("a1", {})
    if a1.get("canonical_sha256") != canonical_sha:
        raise SystemExit("Gate B inventory is not bound to the repaired A1 canonical file")
    hashes = a1.get("record_learner_facing_sha256", {})

    finding_meta = load_repair_metadata()
    if set(finding_meta) != set(EXPECTED_IDS):
        raise SystemExit("A1 Unit 1 finding metadata scope drift")
    total_findings = sum(len(finding_meta[pid]) for pid in EXPECTED_IDS)
    if total_findings != EXPECTED_FINDINGS:
        raise SystemExit(f"expected {EXPECTED_FINDINGS} findings, got {total_findings}")

    decisions = []
    for pid in EXPECTED_IDS:
        learner_hash = hashes.get(pid)
        if not isinstance(learner_hash, str) or len(learner_hash) != 64:
            raise SystemExit(f"missing/invalid authoritative learner-facing hash for {pid}")
        findings = []
        for idx, (field, dimension, severity, rationale) in enumerate(finding_meta[pid], 1):
            findings.append(
                {
                    "finding_id": f"{pid}-gB-{idx:02d}",
                    "field": field,
                    "dimension": dimension,
                    "severity": severity,
                    "status": "REPAIRED",
                    "rationale": rationale,
                }
            )
        decisions.append(
            {
                "passage_id": pid,
                "learner_facing_sha256": learner_hash,
                "decision": "PASS_AFTER_REPAIR",
                "finding_count": len(findings),
                "findings": findings,
            }
        )

    doc = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "level": "A1",
        "unit": 1,
        "date": "2026-08-30",
        "gate": "Gate B — passage-by-passage linguistic/naturalness audit",
        "canonical_path": "reading/arabic/a1/passages.jsonl",
        "canonical_sha256": canonical_sha,
        "records_reviewed": len(decisions),
        "records_with_findings": sum(1 for d in decisions if d["finding_count"]),
        "fresh_findings": sum(d["finding_count"] for d in decisions),
        "decisions": decisions,
        "quality_promotion": False,
        "release_claim": False,
        "guard": "Learner-facing hashes are copied from the freshly rebuilt authoritative Gate B inventory and revalidated by sync_arabic_gate_b_progress.py.",
    }
    if doc["records_reviewed"] != 6 or doc["records_with_findings"] != 6 or doc["fresh_findings"] != EXPECTED_FINDINGS:
        raise SystemExit("A1 Unit 1 decision aggregate drift")

    DECISION_DIR.mkdir(parents=True, exist_ok=True)
    DECISION_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "level": "A1",
                "unit": 1,
                "records_reviewed": doc["records_reviewed"],
                "records_with_findings": doc["records_with_findings"],
                "fresh_findings": doc["fresh_findings"],
                "canonical_sha256": canonical_sha,
                "hash_source": "fresh Gate B inventory",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
