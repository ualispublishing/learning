#!/usr/bin/env python3
"""Record fresh Arabic Gate B A1 Unit 2 decisions from the rebuilt Gate B inventory."""
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
DECISION_PATH = DECISION_DIR / "a1_u02.json"
EXPECTED_IDS = [f"ar-a1-u02-p{i:02d}" for i in range(1, 7)]
EXPECTED_FINDINGS = 12


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_finding_meta():
    source = Path(__file__).with_name("apply_arabic_gate_b_a1_unit02.py")
    spec = importlib.util.spec_from_file_location("arabic_gate_b_a1_u02_meta", source)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load A1 Unit 2 Gate B repair metadata")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.FINDING_META


def main() -> None:
    raw = CANONICAL.read_bytes()
    canonical_sha = sha256_bytes(raw)
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("A1 canonical layout drift while recording Unit 2 decisions")
    if [rows[i].get("id") for i in range(6, 12)] != EXPECTED_IDS:
        raise SystemExit("A1 Unit 2 id/layout drift while recording decisions")
    for record in rows[6:12]:
        quality = record.get("quality", {})
        for field in ("linguistic_review", "pedagogical_review", "answer_key_check", "schema_check"):
            if quality.get(field) != "pass":
                raise SystemExit(f"{record.get('id')}: {field} is not pass after substantive Unit 2 review")
        if quality.get("status") != "draft" or quality.get("coverage_check") != "pending":
            raise SystemExit(f"{record.get('id')}: unexpected release/coverage state")

    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if inv.get("project_id") != "LANG-A1C2" or inv.get("language") != "arabic":
        raise SystemExit("unexpected Gate B inventory identity")
    if (inv.get("records"), inv.get("questions"), inv.get("answers")) != (360, 3600, 3600):
        raise SystemExit("Gate B inventory corpus totals drift")
    a1 = inv.get("levels", {}).get("a1", {})
    if a1.get("canonical_sha256") != canonical_sha:
        raise SystemExit("Gate B inventory is not bound to current repaired A1 canonical file")
    hashes = a1.get("record_learner_facing_sha256", {})

    finding_meta = load_finding_meta()
    if set(finding_meta) != set(EXPECTED_IDS):
        raise SystemExit("A1 Unit 2 finding metadata scope drift")
    if sum(len(finding_meta[pid]) for pid in EXPECTED_IDS) != EXPECTED_FINDINGS:
        raise SystemExit("A1 Unit 2 finding count drift")

    decisions = []
    for pid in EXPECTED_IDS:
        learner_hash = hashes.get(pid)
        if not isinstance(learner_hash, str) or len(learner_hash) != 64:
            raise SystemExit(f"missing authoritative learner-facing hash for {pid}")
        findings = [
            {
                "finding_id": f"{pid}-gB-{idx:02d}",
                "field": field,
                "dimension": dimension,
                "severity": severity,
                "status": "REPAIRED",
                "rationale": rationale,
            }
            for idx, (field, dimension, severity, rationale) in enumerate(finding_meta[pid], 1)
        ]
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
        "unit": 2,
        "date": "2026-08-31",
        "gate": "Gate B — passage-by-passage linguistic/naturalness audit",
        "canonical_path": "reading/arabic/a1/passages.jsonl",
        "canonical_sha256": canonical_sha,
        "records_reviewed": 6,
        "records_with_findings": 6,
        "fresh_findings": EXPECTED_FINDINGS,
        "decisions": decisions,
        "quality_promotion": False,
        "release_claim": False,
        "guard": "Learner-facing hashes come only from the freshly rebuilt authoritative Gate B inventory and are independently revalidated by the progress synchronizer.",
    }
    if sum(d["finding_count"] for d in decisions) != EXPECTED_FINDINGS:
        raise SystemExit("A1 Unit 2 decision aggregate drift")
    DECISION_DIR.mkdir(parents=True, exist_ok=True)
    DECISION_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"level":"A1","unit":2,"records_reviewed":6,"fresh_findings":EXPECTED_FINDINGS,"canonical_sha256":canonical_sha,"hash_source":"fresh Gate B inventory"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
