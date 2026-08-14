#!/usr/bin/env python3
"""Repair canonical metadata defects exposed by final Arabic Pass 01.

Repairs only:
1) topic-like labels stored in `domains`: preserve each label in `topics`, then
   map it to one of the four canonical CEFR-style domains;
2) six invalid review-stage R0 values: change to R1 (first valid review stage).

Passage text, questions, answers, lexical senses, and target IDs are untouched.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
VALID = {"personal", "public", "educational", "professional"}

DOMAIN_MAP = {
    # personal-context topics
    "relationships": "personal", "home": "personal", "memory": "personal",
    "health": "personal", "travel": "personal",

    # public/social contexts
    "community": "public", "society": "public", "social": "public",
    "institutions": "public", "law": "public", "governance": "public",
    "policy": "public", "rights": "public", "cities": "public",
    "climate": "public", "environment": "public", "media": "public",
    "public speech": "public", "security": "public", "transport": "public",
    "consumer": "public", "culture": "public", "arts": "public",
    "art": "public", "digital": "public", "communication": "public",

    # educational/analytic contexts
    "ethics": "educational", "science": "educational", "economics": "educational",
    "history": "educational", "education": "educational", "research": "educational",
    "literature": "educational", "language": "educational", "interpretation": "educational",
    "criticism": "educational", "philosophy": "educational", "translation": "educational",
    "historiography": "educational", "methods": "educational", "models": "educational",
    "rhetoric": "educational", "reasoning": "educational", "data": "educational",
    "evidence": "educational", "geography": "educational", "measurement": "educational",
    "statistics": "educational", "argumentation": "educational", "behavior": "educational",
    "biology": "educational", "epistemology": "educational", "knowledge": "educational",
    "laboratory": "educational", "narrative": "educational", "poetry": "educational",
    "sources": "educational", "style": "educational", "complex systems": "educational",
    "C2 synthesis": "educational", "future uncertainty": "educational",
    "mixed": "educational",

    # professional/organizational contexts
    "work": "professional", "design": "professional", "technology": "professional",
    "organizations": "professional", "operations": "professional",
    "decision making": "professional", "forecasting": "professional", "risk": "professional",
    "administration": "professional", "projects": "professional", "business": "professional",
    "cash flow": "professional", "collaboration": "professional", "contracts": "professional",
    "engineering": "professional", "implementation": "professional", "incentives": "professional",
    "investment": "professional", "management": "professional", "manufacturing": "professional",
    "markets": "professional", "monitoring": "professional", "negotiation": "professional",
    "planning": "professional", "procurement": "professional", "publication": "professional",
    "publishing": "professional", "systems": "professional", "trade": "professional",
    "procedure": "professional",
}


def main() -> None:
    # Discover all illegal labels before touching anything; refuse if the map is incomplete.
    observed_illegal: set[str] = set()
    total_r0 = 0
    loaded: dict[str, list[dict]] = {}
    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        loaded[level] = rows
        for row in rows:
            observed_illegal.update(str(d) for d in row.get("domains", []) if d not in VALID)
            total_r0 += sum(
                1 for t in row.get("review_lexical_targets", [])
                if isinstance(t, dict) and t.get("review_stage") == "R0"
            )
    missing_map = observed_illegal - set(DOMAIN_MAP)
    if missing_map:
        raise RuntimeError("Unmapped illegal domains: " + json.dumps(sorted(missing_map), ensure_ascii=False))
    if total_r0 != 6:
        raise RuntimeError(f"Expected exactly 6 R0 review stages from Pass 01, found {total_r0}")

    touched_rows = 0
    normalized_domain_values = 0
    r0_repairs = 0
    touched_by_level = Counter()

    for level, rows in loaded.items():
        changed_file = False
        for row in rows:
            changed = False
            domains = row.get("domains", []) if isinstance(row.get("domains"), list) else []
            invalid = [str(d) for d in domains if d not in VALID]
            valid_existing = [str(d) for d in domains if d in VALID]
            if invalid:
                topics = row.setdefault("topics", [])
                for label in invalid:
                    if label not in topics:
                        topics.append(label)
                mapped = [DOMAIN_MAP[label] for label in invalid]
                new_domains: list[str] = []
                for value in [*valid_existing, *mapped]:
                    if value not in new_domains:
                        new_domains.append(value)
                if not new_domains:
                    raise RuntimeError(f"No broad domain after normalization: {row.get('id')}")
                row["domains"] = new_domains
                normalized_domain_values += len(invalid)
                changed = True

            for target in row.get("review_lexical_targets", []):
                if isinstance(target, dict) and target.get("review_stage") == "R0":
                    target["review_stage"] = "R1"
                    r0_repairs += 1
                    changed = True

            if changed:
                row["revision"] = int(row.get("revision", 1)) + 1
                quality = row.setdefault("quality", {})
                notes = quality.setdefault("notes", [])
                note = "Final audit Pass 01 metadata repair: normalized broad domains and/or replaced invalid review stage R0 with R1; passage content and assessment content unchanged."
                if note not in notes:
                    notes.append(note)
                touched_rows += 1
                touched_by_level[level] += 1
                changed_file = True

        if changed_file:
            path = ROOT / f"reading/arabic/{level}/passages.jsonl"
            path.write_text(
                "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n",
                encoding="utf-8",
            )

    # Post-write hard guards.
    remaining_illegal = []
    remaining_r0 = []
    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            bad = [d for d in row.get("domains", []) if d not in VALID]
            if bad:
                remaining_illegal.append({"id": row.get("id"), "domains": bad})
            for target in row.get("review_lexical_targets", []):
                if isinstance(target, dict) and target.get("review_stage") == "R0":
                    remaining_r0.append({"id": row.get("id"), "target_id": target.get("id")})
    assert not remaining_illegal, remaining_illegal[:10]
    assert not remaining_r0, remaining_r0
    assert r0_repairs == 6, r0_repairs

    print(json.dumps({
        "observed_illegal_domain_labels": len(observed_illegal),
        "normalized_domain_values": normalized_domain_values,
        "R0_to_R1_repairs": r0_repairs,
        "touched_rows": touched_rows,
        "touched_by_level": dict(touched_by_level),
        "remaining_illegal_domains": 0,
        "remaining_R0": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
