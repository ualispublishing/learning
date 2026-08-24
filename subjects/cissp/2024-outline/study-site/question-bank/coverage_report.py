#!/usr/bin/env python3
"""Coverage and difficulty planner for CISSP Atlas question-bank expansion.

This report does not replace semantic/originality review. It answers a different
question: where should the next original questions be authored so the bank grows
without over-practicing already-dense objectives or drifting from the intended
F/E/S/B difficulty mix?

Usage:
  python question-bank/coverage_report.py
  python question-bank/coverage_report.py --released-only
  python question-bank/coverage_report.py --human
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

QB = Path(__file__).resolve().parent
ROOT = QB.parent
TARGET_TOTAL = 800
TARGET_DIFFICULTY = {"F": 120, "E": 480, "S": 160, "B": 40}
OBJECTIVE_MINIMUM = {"F": 1, "E": 4, "S": 1}


def parse_js_assignment(path: Path, prefix: str, suffix: str) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    if not (raw.startswith(prefix) and raw.endswith(suffix)):
        raise ValueError(f"Unexpected wrapper in {path.name}")
    return json.loads(raw[len(prefix):-len(suffix)])


def load_meta() -> dict:
    raw = (ROOT / "data-meta.js").read_text(encoding="utf-8").strip()
    end = raw.index(";window.CISSP_CHUNKS=[];")
    return json.loads(raw[len("window.CISSP_META="):end])


def load_coverage() -> dict[str, list[str]]:
    raw = (ROOT / "coverage-detail.js").read_text(encoding="utf-8").strip()
    marker = ";\nwindow.CISSP_AI_COVERAGE="
    return json.loads(raw[len("window.CISSP_COVERAGE="):raw.index(marker)])


def load_jsonl(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def load_base_questions() -> list[dict]:
    manifest = json.loads((QB / "RELEASED_QUESTION_CLASSIFICATION.json").read_text(encoding="utf-8"))
    out = []
    for qid, item in manifest["items"].items():
        out.append({
            "id": qid,
            "format": "mcq",
            "domain_primary": item["domain"],
            "objectives": [item["objective"]],
            "difficulty_tier": item["difficulty_tier"],
            "difficulty_score": item["difficulty_score"],
            "source": "base-56",
            "subtopics": [],
        })
    return out


def load_released_batches() -> tuple[list[dict], set[Path]]:
    manifest = json.loads((QB / "RELEASED_BATCHES.json").read_text(encoding="utf-8"))
    records: list[dict] = []
    paths: set[Path] = set()
    for batch in manifest.get("released_batches", []):
        for rel in batch.get("files", []):
            path = (ROOT / rel).resolve()
            paths.add(path)
            for row in load_jsonl(path):
                row = dict(row)
                row["source"] = f"released-{batch.get('batch_id','batch')}"
                records.append(row)
    return records, paths


def load_candidates(released_paths: set[Path]) -> list[dict]:
    out = []
    candidate_dir = QB / "candidates"
    if not candidate_dir.exists():
        return out
    for path in sorted(candidate_dir.glob("*.jsonl")):
        if path.resolve() in released_paths:
            continue
        for row in load_jsonl(path):
            row = dict(row)
            row["source"] = path.name
            out.append(row)
    return out


def question_tier_counts(records: list[dict]) -> dict[str, int]:
    c = Counter(r.get("difficulty_tier") for r in records)
    return {k: c.get(k, 0) for k in ("F", "E", "S", "B")}


def objective_counts(records: list[dict]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        if r.get("format", "mcq") != "mcq":
            continue
        tier = r.get("difficulty_tier")
        for oid in r.get("objectives", []):
            counts[oid][tier] += 1
            counts[oid]["total"] += 1
    return {
        oid: {"F": c.get("F", 0), "E": c.get("E", 0), "S": c.get("S", 0), "total": c.get("total", 0)}
        for oid, c in counts.items()
    }


def objective_deficits(all_objectives: list[str], counts: dict[str, dict[str, int]], domain_weights: dict[int, int]) -> list[dict]:
    rows = []
    for oid in all_objectives:
        c = counts.get(oid, {"F": 0, "E": 0, "S": 0, "total": 0})
        missing = {tier: max(0, minimum - c.get(tier, 0)) for tier, minimum in OBJECTIVE_MINIMUM.items()}
        deficit = sum(missing.values())
        domain = int(oid.split(".")[0])
        rows.append({
            "objective": oid,
            "domain": domain,
            "domain_weight": domain_weights[domain],
            "counts": c,
            "minimum_missing": missing,
            "deficit": deficit,
            "priority_score": deficit * 100 + domain_weights[domain] * 2 - c.get("total", 0),
        })
    rows.sort(key=lambda x: (-x["priority_score"], x["objective"]))
    return rows


def subtopic_report(coverage: dict[str, list[str]], enriched_records: list[dict]) -> dict:
    exposed = Counter()
    for r in enriched_records:
        for s in r.get("subtopics", []):
            exposed[s] += 1
    all_labels = [s for values in coverage.values() for s in values]
    unexposed = [s for s in all_labels if exposed[s] == 0]
    singleton = [s for s in all_labels if exposed[s] == 1]
    return {
        "coverage_labels": len(all_labels),
        "explicitly_tagged_exposed": len(all_labels) - len(unexposed),
        "explicitly_tagged_unexposed": len(unexposed),
        "single_exposure_labels": len(singleton),
        "unexposed_labels": unexposed,
        "note": "Base Q-001..Q-056 predate subtopic tagging, so this is an enriched-metadata planning signal, not proof that an untagged subtopic has never been practiced.",
    }


def build_report(include_candidates: bool) -> dict:
    meta = load_meta()
    coverage = load_coverage()
    base = load_base_questions()
    released_extra, released_paths = load_released_batches()
    candidates = load_candidates(released_paths) if include_candidates else []
    released = base + released_extra
    planning = released + candidates
    domain_weights = {d["num"]: d["weight"] for d in meta["domains"]}
    all_objectives = sorted(coverage, key=lambda x: (int(x.split(".")[0]), int(x.split(".")[1])))
    released_counts = objective_counts(released)
    planning_counts = objective_counts(planning)
    released_tiers = question_tier_counts(released)
    planning_tiers = question_tier_counts(planning)
    target_remaining = {k: max(0, TARGET_DIFFICULTY[k] - released_tiers[k]) for k in TARGET_DIFFICULTY}
    planning_target_remaining = {k: max(0, TARGET_DIFFICULTY[k] - planning_tiers[k]) for k in TARGET_DIFFICULTY}
    return {
        "schema_version": 1,
        "scope": "released+unreleased-candidates" if include_candidates else "released-only",
        "released": {
            "records": len(released),
            "standard_mcq": sum(r.get("format", "mcq") == "mcq" for r in released),
            "bellringers": sum(r.get("format") == "bellringer" for r in released),
            "difficulty": released_tiers,
        },
        "candidates_included": {
            "records": len(candidates),
            "difficulty": question_tier_counts(candidates),
            "files": sorted({r.get("source") for r in candidates}),
        },
        "planning_state": {
            "records": len(planning),
            "difficulty": planning_tiers,
            "target_800": TARGET_DIFFICULTY,
            "remaining_from_released": target_remaining,
            "remaining_if_all_current_candidates_promote": planning_target_remaining,
        },
        "objective_minimum_target": OBJECTIVE_MINIMUM,
        "released_objective_priority": objective_deficits(all_objectives, released_counts, domain_weights),
        "planning_objective_priority": objective_deficits(all_objectives, planning_counts, domain_weights),
        "enriched_subtopic_planning": subtopic_report(coverage, released_extra + candidates),
    }


def print_human(report: dict) -> None:
    print(f"scope={report['scope']}")
    print("released", report["released"])
    print("candidates", report["candidates_included"])
    print("planning", report["planning_state"])
    print("\nTop objective deficits after included candidates:")
    for row in report["planning_objective_priority"][:20]:
        c = row["counts"]
        m = row["minimum_missing"]
        print(f"  {row['objective']}: F{c['F']} E{c['E']} S{c['S']} total={c['total']} missing={m} priority={row['priority_score']}")
    s = report["enriched_subtopic_planning"]
    print(f"\nExplicit subtopic tags: {s['explicitly_tagged_exposed']}/{s['coverage_labels']} exposed; {s['explicitly_tagged_unexposed']} currently untagged by enriched records")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--released-only", action="store_true")
    ap.add_argument("--human", action="store_true")
    args = ap.parse_args()
    report = build_report(include_candidates=not args.released_only)
    if args.human:
        print_human(report)
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
