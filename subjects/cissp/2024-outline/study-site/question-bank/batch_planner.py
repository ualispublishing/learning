#!/usr/bin/env python3
"""Recommend the next CISSP Atlas standard-question authoring slate.

This is a planning tool, not an automatic author or release gate. It consumes the
coverage report's released+candidate state, then proposes E/S objective targets
while respecting the same 35% primary-domain concentration rule as quality_gate.py.

Default 16-record slate: 12 Exam-calibrated + 4 Stretch, no Foundation+ filler.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter

from coverage_report import build_report, load_coverage

DEFAULT_SIZE = 16
EXAM_SHARE = 0.75
MAX_PRIMARY_DOMAIN_SHARE = 0.35


def desired_tiers(size: int) -> list[str]:
    exam = round(size * EXAM_SHARE)
    stretch = size - exam
    # Interleave stretch targets rather than stacking them at the end.
    out = []
    e_left, s_left = exam, stretch
    for i in range(size):
        remaining = size - i
        if s_left and (i + 1) % 4 == 0:
            out.append("S")
            s_left -= 1
        elif e_left:
            out.append("E")
            e_left -= 1
        else:
            out.append("S")
            s_left -= 1
    return out


def choose_targets(size: int) -> dict:
    report = build_report(include_candidates=True)
    coverage = load_coverage()
    rows = report["planning_objective_priority"]
    row_by_oid = {r["objective"]: r for r in rows}
    domain_cap = max(1, math.floor(size * MAX_PRIMARY_DOMAIN_SHARE))
    domain_counts = Counter()
    objective_counts = Counter()
    selected = []

    for tier in desired_tiers(size):
        ranked = sorted(
            rows,
            key=lambda r: (
                # Fill an explicit tier deficit first.
                -(1 if r["minimum_missing"].get(tier, 0) > 0 else 0),
                # Then prefer objectives with less of this tier already present.
                r["counts"].get(tier, 0),
                # Then the weighted overall deficit priority.
                -r["priority_score"],
                # Avoid repeatedly targeting the same objective in one batch.
                objective_counts[r["objective"]],
                r["objective"],
            ),
        )
        chosen = None
        for r in ranked:
            oid, domain = r["objective"], r["domain"]
            if domain_counts[domain] >= domain_cap:
                continue
            if objective_counts[oid] > 0:
                continue
            chosen = r
            break
        if chosen is None:
            # Only if unique-objective selection cannot fill the slate, allow a
            # second target for an objective while retaining the domain cap.
            for r in ranked:
                if domain_counts[r["domain"]] < domain_cap:
                    chosen = r
                    break
        if chosen is None:
            raise RuntimeError("Unable to construct a slate under the domain concentration cap")

        oid = chosen["objective"]
        domain_counts[chosen["domain"]] += 1
        objective_counts[oid] += 1
        labels = coverage.get(oid, [])
        selected.append({
            "slot": len(selected) + 1,
            "difficulty_tier": tier,
            "objective": oid,
            "domain": chosen["domain"],
            "domain_weight": chosen["domain_weight"],
            "current_counts": chosen["counts"],
            "minimum_missing_before_batch": chosen["minimum_missing"],
            "priority_score": chosen["priority_score"],
            "candidate_subtopic_pool": labels,
            "authoring_instruction": (
                "Choose a materially new decision point/scenario family from this objective; "
                "prefer a thin subtopic, derive the rule from the public scope/registered standards, "
                "and run the normal originality/semantic gate before promotion."
            ),
        })

    return {
        "schema_version": 1,
        "planning_scope": report["scope"],
        "size": size,
        "difficulty_target": dict(Counter(x["difficulty_tier"] for x in selected)),
        "maximum_primary_domain_share": MAX_PRIMARY_DOMAIN_SHARE,
        "maximum_primary_domain_records": domain_cap,
        "primary_domain_distribution": {str(k): v for k, v in sorted(domain_counts.items())},
        "planning_bank_state": report["planning_state"],
        "targets": selected,
        "boundary": (
            "This is an authoring recommendation only. It does not create questions, establish "
            "exam psychometric difficulty, satisfy semantic/originality review, or authorize release."
        ),
    }


def print_human(plan: dict) -> None:
    print(
        f"next_batch size={plan['size']} difficulty={plan['difficulty_target']} "
        f"domain_cap={plan['maximum_primary_domain_records']}"
    )
    print("primary_domains", plan["primary_domain_distribution"])
    for item in plan["targets"]:
        c = item["current_counts"]
        print(
            f"{item['slot']:02d}. {item['difficulty_tier']} D{item['domain']} "
            f"obj {item['objective']} current=F{c['F']}/E{c['E']}/S{c['S']} "
            f"priority={item['priority_score']}"
        )
        if item["candidate_subtopic_pool"]:
            print("    subtopics:", " | ".join(item["candidate_subtopic_pool"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=DEFAULT_SIZE)
    ap.add_argument("--human", action="store_true")
    args = ap.parse_args()
    if args.size < 4:
        raise SystemExit("--size must be at least 4")
    plan = choose_targets(args.size)
    if args.human:
        print_human(plan)
    else:
        print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
