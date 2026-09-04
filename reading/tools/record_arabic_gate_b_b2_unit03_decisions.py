#!/usr/bin/env python3
"""Record fresh Arabic Gate B B2 Unit 3 decisions from the rebuilt Gate B inventory."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
CANONICAL = READING / "arabic/b2/passages.jsonl"
INVENTORY = READING / "audit/arabic_gate_b_naturalness_inventory_2026-08-30.json"
DECISION_DIR = READING / "audit/arabic_gate_b_decisions_2026-08-30"
DECISION_PATH = DECISION_DIR / "b2_u03.json"
EXPECTED_IDS = [f"ar-b2-u03-p{i:02d}" for i in range(1, 7)]
EXPECTED_FINDINGS = 15
EXPECTED_WITH_FINDINGS = 5


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_meta():
    source = Path(__file__).with_name("apply_arabic_gate_b_b2_unit03.py")
    spec = importlib.util.spec_from_file_location("arabic_gate_b_b2_u03_meta", source)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load B2 Unit 3 repair metadata")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.FINDING_META


def main() -> None:
    raw = CANONICAL.read_bytes()
    canonical_sha = sha(raw)
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if (
        len(rows) != 60
        or [row.get("sequence") for row in rows] != list(range(1, 61))
        or [rows[i].get("id") for i in range(12, 18)] != EXPECTED_IDS
    ):
        raise SystemExit("B2 Unit 3 layout/id drift")

    for record in rows[12:18]:
        quality = record.get("quality", {})
        for field in ("linguistic_review", "pedagogical_review", "answer_key_check", "schema_check"):
            if quality.get(field) != "pass":
                raise SystemExit(f"{record.get('id')}: {field} is not pass")
        if quality.get("status") != "draft" or quality.get("coverage_check") != "pending":
            raise SystemExit(f"{record.get('id')}: unexpected release/coverage state")

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    b2 = inventory.get("levels", {}).get("b2", {})
    if (
        inventory.get("project_id") != "LANG-A1C2"
        or inventory.get("language") != "arabic"
        or (inventory.get("records"), inventory.get("questions"), inventory.get("answers"))
        != (360, 3600, 3600)
        or b2.get("canonical_sha256") != canonical_sha
    ):
        raise SystemExit("Gate B B2 inventory identity/scope/hash drift")

    hashes = b2.get("record_learner_facing_sha256", {})
    meta = load_meta()
    if (
        set(meta) != set(EXPECTED_IDS)
        or sum(len(meta[pid]) for pid in EXPECTED_IDS) != EXPECTED_FINDINGS
        or sum(bool(meta[pid]) for pid in EXPECTED_IDS) != EXPECTED_WITH_FINDINGS
    ):
        raise SystemExit("B2 Unit 3 finding metadata drift")

    decisions = []
    for pid in EXPECTED_IDS:
        learner_hash = hashes.get(pid)
        if not isinstance(learner_hash, str) or len(learner_hash) != 64:
            raise SystemExit(f"missing authoritative learner hash for {pid}")
        findings = [
            {
                "finding_id": f"{pid}-gB-{idx:02d}",
                "field": field,
                "dimension": dimension,
                "severity": severity,
                "status": "REPAIRED",
                "rationale": rationale,
            }
            for idx, (field, dimension, severity, rationale) in enumerate(meta[pid], 1)
        ]
        decisions.append(
            {
                "passage_id": pid,
                "learner_facing_sha256": learner_hash,
                "decision": "PASS_AFTER_REPAIR" if findings else "PASS",
                "finding_count": len(findings),
                "findings": findings,
            }
        )

    doc = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "level": "B2",
        "unit": 3,
        "date": "2026-09-04",
        "gate": "Gate B — passage-by-passage linguistic/naturalness audit",
        "canonical_path": "reading/arabic/b2/passages.jsonl",
        "canonical_sha256": canonical_sha,
        "records_reviewed": 6,
        "records_with_findings": EXPECTED_WITH_FINDINGS,
        "fresh_findings": EXPECTED_FINDINGS,
        "decisions": decisions,
        "quality_promotion": False,
        "release_claim": False,
        "guard": (
            "Learner-facing hashes come only from the freshly rebuilt authoritative Gate B inventory "
            "and are independently revalidated by the progress synchronizer. Legitimate B2 "
            "grammar-in-context/discourse analysis is retained; this internal Gate B pass does not "
            "constitute educator/publication release approval."
        ),
    }
    DECISION_DIR.mkdir(parents=True, exist_ok=True)
    DECISION_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "level": "B2",
                "unit": 3,
                "records_reviewed": 6,
                "records_with_findings": EXPECTED_WITH_FINDINGS,
                "fresh_findings": EXPECTED_FINDINGS,
                "canonical_sha256": canonical_sha,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
