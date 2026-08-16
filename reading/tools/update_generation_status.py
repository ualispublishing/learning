#!/usr/bin/env python3
"""Synchronize generation counts without overwriting active final-review state.

This tool is generation bookkeeping only. Once Arabic A1-C2 generation is
complete and final-review state exists, it MUST NOT replace STATUS phase,
next-actions, audit statuses, or final-review blockers with historical
"audits deferred" text.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "reading" / "STATUS.json"
ARABIC_LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def level_path(level: str) -> Path:
    return ROOT / f"reading/arabic/{level}/passages.jsonl"


def main() -> None:
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    rows = {level: read_rows(level_path(level)) for level in ARABIC_LEVELS}
    counts = {level: len(values) for level, values in rows.items()}
    complete = all(counts[level] >= 60 for level in ARABIC_LEVELS)

    status["updated"] = date.today().isoformat()
    status["arabic"] = {
        **status.get("arabic", {}),
        "canonical_passages": sum(counts.values()),
        "levels": counts,
        "generation_state": "COMPLETE" if complete else "IN_PROGRESS",
        "questions_per_passage": 10,
        "total_questions": sum(len(r.get("questions", [])) for values in rows.values() for r in values),
        "total_answers": sum(len(r.get("answer_key", [])) for values in rows.values() for r in values),
        "formal_final_approval": bool(status.get("arabic_final_review", {}).get("final_approval", False)),
    }

    # Generation bookkeeping must not reopen a completed corpus or overwrite the
    # current final-review queue. Only supply a generation phase when generation
    # is actually incomplete.
    if not complete:
        active = next(level for level in ARABIC_LEVELS if counts[level] < 60)
        status["phase"] = (
            f"Generation-first Arabic production is incomplete: {active.upper()} has "
            f"{counts[active]}/60 canonical passages."
        )
        status["next_actions"] = [
            f"continue Arabic {active.upper()} generation from live canonical state",
            "preserve the generation-first policy and ten-question contract",
            "do not infer counts from historical task lists",
        ]
    elif "arabic_final_review" not in status:
        # Defensive fallback for an old STATUS file: do not claim audit results.
        status["phase"] = (
            "Arabic A1-C2 generation is complete. Determine final-review state "
            "from fresh audit artifacts before setting next actions."
        )
        status["next_actions"] = [
            "run the final-review status synchronizer against current audit artifacts"
        ]

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"arabic_counts": counts, "generation_complete": complete}, ensure_ascii=False))


if __name__ == "__main__":
    main()
