#!/usr/bin/env python3
"""Promotion/runtime gate for SecX prototype-released semantic relationships."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT / "RELATIONSHIP_REVIEW.json"
RELEASE = ROOT / "RELEASED_RELATIONSHIPS.json"
RUNTIME_DATA = ROOT / "released-relationships.js"
NEXT = ROOT / "next.html"
LENS = ROOT / "relationship-lens.js"
errors: list[str] = []


def check(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_runtime_rows(path: Path):
    text = path.read_text(encoding="utf-8").strip()
    prefix = "window.SECX_RELEASED_RELATIONSHIPS=Object.freeze("
    suffix = ");"
    if not text.startswith(prefix) or not text.endswith(suffix):
        raise ValueError("unexpected released-relationships.js wrapper")
    return json.loads(text[len(prefix):-len(suffix)])


try:
    review = load(REVIEW)
    release = load(RELEASE)
    runtime_rows = load_runtime_rows(RUNTIME_DATA)
    next_html = NEXT.read_text(encoding="utf-8")
    lens = LENS.read_text(encoding="utf-8")
except (OSError, ValueError) as exc:
    print("FAIL secx_relationship_release_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

check(review.get("scope") == "reviewer-only", "source relationship registry must remain reviewer-only")
check(review.get("publication_state") == "draft-only", "source relationship registry must remain draft-only")
check(review.get("learner_runtime_loaded") is False, "review registry must remain learner_runtime_loaded=false")

check(release.get("schema_version") == 1, "released relationship schema version must be 1")
check(release.get("scope") == "secx-review-prototype", "released relationship scope must remain secx-review-prototype")
check(release.get("publication_state") == "prototype-released", "released relationship publication_state must be prototype-released")
check(release.get("learner_runtime_loaded") is True, "released relationship artifact must declare learner_runtime_loaded=true after runtime integration")
check(release.get("review_registry") == "RELATIONSHIP_REVIEW.json", "released artifact must name the reviewer registry")

review_rows = review.get("relationships") if isinstance(review.get("relationships"), list) else []
release_rows = release.get("relationships") if isinstance(release.get("relationships"), list) else []
approved = {str(row.get("id")): row for row in review_rows if isinstance(row, dict) and row.get("status") == "approved"}
released = {str(row.get("id")): row for row in release_rows if isinstance(row, dict)}

check(bool(approved), "at least one approved draft relationship is required for promotion")
check(len(released) == len(release_rows), "released relationship IDs must be unique")
check(set(released) == set(approved), f"released relationship IDs must exactly match approved draft IDs: approved={sorted(approved)} released={sorted(released)}")

COPY_FIELDS = ("from_id", "to_id", "type", "rationale", "evidence", "reviewed_by", "reviewed_on")
for rid, rel in released.items():
    source = approved.get(rid) or {}
    check(source.get("release_state") == "draft", f"{rid} source review must still be release_state=draft")
    for field in COPY_FIELDS:
        check(rel.get(field) == source.get(field), f"{rid} released {field} must exactly match approved review record")

check(runtime_rows == release_rows, "released-relationships.js must exactly mirror RELEASED_RELATIONSHIPS.json relationships")
check(next_html.count("released-relationships.js") == 1, "next.html must load released relationship runtime data exactly once")
check(next_html.count("relationship-lens.js") == 1, "next.html must load relationship lens exactly once")
check(next_html.index("released-relationships.js") < next_html.index("relationship-lens.js"), "released relationship data must load before relationship lens")
check("relationships.onload=readyExpanded" in next_html, "expanded ready state must wait for relationship lens load")
check("RELATIONSHIP_REVIEW.json" not in next_html, "reviewer relationship registry must never be learner-loaded")
check("RELATIONSHIP_REVIEW.json" not in lens, "relationship lens must not reference reviewer relationship registry")
check("SECX_RELEASED_RELATIONSHIPS" in lens, "relationship lens must consume only the released runtime relationship channel")
check("localStorage.setItem" not in lens, "relationship lens must not write learner or graph localStorage")
check("relationshipLensBtn" in lens and "relationshipsLayout" in lens, "relationship lens navigation surface is incomplete")

if errors:
    print("FAIL secx_relationship_release_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(
    "PASS secx_relationship_release_audit "
    f"approved={len(approved)} prototype_released={len(released)} learner_runtime_loaded=true "
    "review_copy=exact runtime_copy=exact reviewer_registry=NOT_LOADED"
)
