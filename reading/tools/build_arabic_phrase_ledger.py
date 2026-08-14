#!/usr/bin/env python3
"""Build a CEFR-neutral Arabic multiword-expression exposure ledger.

The canonical phrase bank remains the source of truth. This builder assigns stable
IDs by canonical CSV row order and deliberately does *not* infer CEFR level from
that order. Level eligibility is applied only from the explicit reviewed planning
artifact and is validated against the canonical phrase text.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "arabic_phrase_bank.csv"
REVIEW = ROOT / "reading" / "planning" / "arabic_phrase_a1_review.json"
OUTPUT = ROOT / "reading" / "ledgers" / "arabic_phrase_exposure.jsonl"
SUMMARY = ROOT / "reading" / "ledgers" / "arabic_phrase_exposure_summary.json"
VALID_DECISIONS = {"A1_eligible", "not_A1_current_review"}


def load_review() -> dict[str, dict[str, str]]:
    data = json.loads(REVIEW.read_text(encoding="utf-8"))
    decisions = data.get("decisions", [])
    if data.get("reviewed_count") != len(decisions):
        raise ValueError(
            f"reviewed_count={data.get('reviewed_count')} but decisions={len(decisions)}"
        )

    by_id: dict[str, dict[str, str]] = {}
    for item in decisions:
        pid = item.get("id")
        front = item.get("front")
        decision = item.get("decision")
        reason = item.get("reason")
        if not isinstance(pid, str) or not pid.startswith("ar-p"):
            raise ValueError(f"Invalid phrase review id: {pid!r}")
        if pid in by_id:
            raise ValueError(f"Duplicate phrase review id: {pid}")
        if not isinstance(front, str) or not front.strip():
            raise ValueError(f"Missing reviewed front for {pid}")
        if decision not in VALID_DECISIONS:
            raise ValueError(f"Invalid review decision for {pid}: {decision!r}")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"Missing review reason for {pid}")
        by_id[pid] = {
            "front": front.strip(),
            "decision": decision,
            "reason": reason.strip(),
        }

    eligible = sum(x["decision"] == "A1_eligible" for x in by_id.values())
    if data.get("a1_eligible_count") != eligible:
        raise ValueError(
            f"a1_eligible_count={data.get('a1_eligible_count')} but decisions contain {eligible}"
        )
    return by_id


def build() -> tuple[int, int]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    review = load_review()
    applied_review_ids: set[str] = set()

    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["Front", "Back"]:
            raise ValueError(f"Unexpected phrase-bank schema: {reader.fieldnames!r}")

        for source_row, row in enumerate(reader, start=1):
            front = (row.get("Front") or "").strip()
            if not front:
                raise ValueError(f"Empty Front at canonical phrase-bank row {source_row}")
            if front in seen:
                raise ValueError(f"Duplicate phrase front at row {source_row}: {front}")
            seen.add(front)

            phrase_id = f"ar-p{source_row:03d}"
            review_item = review.get(phrase_id)
            cefr_eligibility = "unreviewed"
            review_reason = None
            if review_item:
                if review_item["front"] != front:
                    raise ValueError(
                        f"Review/front mismatch for {phrase_id}: "
                        f"review={review_item['front']!r}, canonical={front!r}"
                    )
                cefr_eligibility = review_item["decision"]
                review_reason = review_item["reason"]
                applied_review_ids.add(phrase_id)

            rows.append(
                {
                    "id": phrase_id,
                    "language": "ar",
                    "kind": "multiword_expression",
                    "source": "arabic_phrase_bank.csv",
                    "source_row": source_row,
                    "front": front,
                    "cefr_eligibility": cefr_eligibility,
                    "a1_review_reason": review_reason,
                    "introduced_in": None,
                    "meaningful_contacts": 0,
                    "learner_successes": 0,
                    "learner_failures": 0,
                    "last_contact_passage": None,
                    "next_reinforcement_stage": "R0",
                }
            )

    missing = sorted(set(review) - applied_review_ids)
    if missing:
        raise ValueError(f"Review ids not found in canonical phrase bank: {missing}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    eligibility_counts: dict[str, int] = {}
    for row in rows:
        key = str(row["cefr_eligibility"])
        eligibility_counts[key] = eligibility_counts.get(key, 0) + 1

    summary = {
        "status": "PASS",
        "language": "ar",
        "source": "arabic_phrase_bank.csv",
        "review_source": "reading/planning/arabic_phrase_a1_review.json",
        "source_rows": len(rows),
        "ledger_rows": len(rows),
        "unique_fronts": len(seen),
        "id_namespace": "ar-pNNN",
        "cefr_policy": "source order does not imply learner level; only explicit review decisions are applied",
        "eligibility_counts": eligibility_counts,
        "reviewed_rows": len(review),
        "learner_success_assumed": False,
        "notes": [
            "The canonical phrase bank is not modified by this build.",
            "Unlisted phrase IDs remain unreviewed.",
            "A1_eligible is permission for deliberate beginner use, not a learner-mastery claim.",
            "not_A1_current_review is not a precise later-CEFR assignment.",
            "Phrase exposure is kept separate from the ranked ar-rNN single-word ledger.",
        ],
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(rows), len(seen)


if __name__ == "__main__":
    count, unique = build()
    print(f"built {count} Arabic phrase-ledger rows ({unique} unique fronts)")
