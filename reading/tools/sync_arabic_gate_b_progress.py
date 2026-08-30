#!/usr/bin/env python3
"""Synchronize fresh Arabic Gate B decision artifacts into inventory/release evidence.

Every counted decision must match the exact learner-facing hash in the current Gate B
inventory. This script never promotes canonical quality metadata and never sets
educator_release_ready.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
INVENTORY_PATH = READING / "audit/arabic_gate_b_naturalness_inventory_2026-08-30.json"
DECISION_DIR = READING / "audit/arabic_gate_b_decisions_2026-08-30"
RELEASE_PATH = READING / "RELEASE_STATUS.json"
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")


def main() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    if inventory.get("project_id") != "LANG-A1C2" or inventory.get("language") != "arabic":
        raise SystemExit("unexpected Gate B inventory identity")
    if inventory.get("records") != 360:
        raise SystemExit("Gate B inventory must contain 360 Arabic records")

    seen = {}
    reviewed_by_level = {level: 0 for level in LEVELS}
    findings_by_level = {level: 0 for level in LEVELS}
    records_with_findings_by_level = {level: 0 for level in LEVELS}
    evidence_paths = []

    if DECISION_DIR.exists():
        for path in sorted(DECISION_DIR.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            if doc.get("project_id") != "LANG-A1C2" or doc.get("language") != "arabic":
                raise SystemExit(f"{path}: wrong project/language")
            level = str(doc.get("level", "")).lower()
            if level not in LEVELS:
                raise SystemExit(f"{path}: invalid level {level}")
            decisions = doc.get("decisions", [])
            if doc.get("records_reviewed") != len(decisions):
                raise SystemExit(f"{path}: records_reviewed mismatch")
            level_hashes = inventory["levels"][level]["record_learner_facing_sha256"]
            for decision in decisions:
                pid = decision.get("passage_id")
                if pid in seen:
                    raise SystemExit(f"duplicate Gate B decision for {pid}: {seen[pid]} and {path}")
                current_hash = level_hashes.get(pid)
                if not current_hash:
                    raise SystemExit(f"{path}: unknown passage {pid}")
                if decision.get("learner_facing_sha256") != current_hash:
                    raise SystemExit(f"{path}: stale learner-facing hash for {pid}")
                if decision.get("decision") not in {"PASS", "PASS_AFTER_REPAIR"}:
                    raise SystemExit(f"{path}: unresolved decision for {pid}")
                seen[pid] = path.as_posix()
                reviewed_by_level[level] += 1
                fc = int(decision.get("finding_count", 0) or 0)
                findings_by_level[level] += fc
                if fc:
                    records_with_findings_by_level[level] += 1
            if int(doc.get("fresh_findings", 0) or 0) != sum(
                int(d.get("finding_count", 0) or 0) for d in decisions
            ):
                raise SystemExit(f"{path}: finding count mismatch")
            evidence_paths.append(path.relative_to(ROOT).as_posix())

    total_reviewed = sum(reviewed_by_level.values())
    total_with_findings = sum(records_with_findings_by_level.values())
    total_findings = sum(findings_by_level.values())
    if total_reviewed > 360:
        raise SystemExit("Gate B reviewed count exceeds scope")

    for level in LEVELS:
        count = reviewed_by_level[level]
        block = inventory["levels"][level]
        block["fresh_records_reviewed"] = count
        block["fresh_records_with_findings"] = records_with_findings_by_level[level]
        block["fresh_findings"] = findings_by_level[level]
        block["fresh_review_status"] = (
            "NOT_YET_REVIEWED" if count == 0 else "COMPLETE" if count == 60 else "IN_PROGRESS"
        )

    inventory["fresh_records_reviewed"] = total_reviewed
    inventory["fresh_records_with_findings"] = total_with_findings
    inventory["fresh_findings"] = total_findings
    inventory["status"] = "COMPLETE_INTERNAL_REVIEW" if total_reviewed == 360 else "IN_PROGRESS"
    inventory["decision_artifacts"] = evidence_paths
    inventory["quality_promotion"] = False
    inventory["release_claim"] = False
    inventory["next_step"] = (
        "Gate B internal review complete; proceed to separate semantic educator/native/blind review gates."
        if total_reviewed == 360
        else "Continue fresh hash-bound passage-by-passage Gate B review in order; repair only exact-current learner-facing defects."
    )
    INVENTORY_PATH.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    arabic = release["languages"]["arabic"]
    if arabic.get("educator_release_ready") is not False:
        raise SystemExit("refusing to sync Gate B while educator_release_ready is not explicitly false")
    progress = arabic.setdefault("naturalness_review_progress", {})
    progress.update(
        {
            "status": "FRESH_GATE_B_INTERNAL_REVIEW_COMPLETE" if total_reviewed == 360 else "FRESH_GATE_B_INTERNAL_REVIEW_IN_PROGRESS",
            "records_in_scope": 360,
            "questions_in_scope": 3600,
            "answers_in_scope": 3600,
            "fresh_records_reviewed": total_reviewed,
            "fresh_records_with_findings": total_with_findings,
            "fresh_findings": total_findings,
            "levels_completed": [level.upper() for level in LEVELS if reviewed_by_level[level] == 60],
            "current_inventory": "reading/audit/arabic_gate_b_naturalness_inventory_2026-08-30.json",
            "decision_artifacts": evidence_paths,
            "review_order": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "guard": "Historical naturalness notes are context only; fresh review counts only exact-current learner-facing hash matches.",
        }
    )
    evidence = arabic.setdefault("latest_release_evidence", [])
    if not isinstance(evidence, list):
        raise SystemExit("Arabic latest_release_evidence is not a list")
    for path in evidence_paths:
        if path not in evidence:
            evidence.append(path)
    arabic["educator_release_ready"] = False
    release["updated"] = "2026-08-30"
    RELEASE_PATH.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "fresh_records_reviewed": total_reviewed,
                "fresh_records_with_findings": total_with_findings,
                "fresh_findings": total_findings,
                "by_level": {
                    level.upper(): {
                        "reviewed": reviewed_by_level[level],
                        "records_with_findings": records_with_findings_by_level[level],
                        "findings": findings_by_level[level],
                    }
                    for level in LEVELS
                },
                "educator_release_ready": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
