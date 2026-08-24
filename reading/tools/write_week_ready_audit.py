#!/usr/bin/env python3
"""Write hash-bound evidence after the seven-session LANG-A1C2 queue validates."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
VALIDATOR = READING / "tools" / "validate_week_ready_queue.py"
QUEUE = READING / "planning" / "WEEK_READY_2026-08-24.json"
MATRIX = READING / "planning" / "topic_genre_matrix.json"
START = READING / "TOMORROW_START_2026-08-24.md"
OUT = READING / "audit" / "week_ready_2026-08-24.json"


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, check=True)
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    sessions = queue["sessions"]
    baseline = queue["pre_week_gate"]["required_state_after_urdu_a2_unit01_integration"]
    end = queue["end_of_week_expected_state"]

    evidence_files = [QUEUE, MATRIX, VALIDATOR, START]
    evidence = {
        path.relative_to(ROOT).as_posix(): {
            "git_blob": blob_sha(path),
            "sha256": sha256(path),
            "bytes": len(path.read_bytes()),
        }
        for path in evidence_files
    }

    payload = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "audited_on": "2026-08-23",
        "ready_from": queue["ready_from"],
        "timezone": queue["timezone"],
        "status": "PASS",
        "purpose": "Hash-bound evidence that the prepared seven-session Urdu A2 queue matches the canonical A2 roadmap and has internally consistent sequence/count arithmetic.",
        "not_a_release_promotion": True,
        "sessions": len(sessions),
        "units": [s["unit"] for s in sessions],
        "sequence_range": [sessions[0]["sequence_start"], sessions[-1]["sequence_end"]],
        "themes": [s["theme"] for s in sessions],
        "baseline_after_unit01_integration": baseline,
        "end_of_week_expected_state": end,
        "evidence_files": evidence,
        "validated_invariants": [
            "exactly seven sessions",
            "sessions map exactly to Urdu A2 Units 2-8",
            "session themes and genres exactly match reading/planning/topic_genre_matrix.json",
            "each session owns exactly six non-overlapping passage sequences",
            "project and Urdu before/after totals advance by exactly six per session",
            "next-unit and next-sequence frontiers are contiguous",
            "A2 standard word band remains 140-220 in the shared contract",
            "the ten-question contract remains visible in the session contract",
            "successful week ends at Urdu A2 Unit 9 / sequence 49",
        ],
        "precondition": "Unit 1 must first be integrated so main reaches project=786, Urdu=66, active Unit 2 / sequence 7 with continuation validation green; the week queue does not manufacture that state.",
        "failure_policy": "If any evidence file blob/hash changes, rerun this writer after validation; old PASS becomes historical evidence rather than current truth.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print("week-ready evidence: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
