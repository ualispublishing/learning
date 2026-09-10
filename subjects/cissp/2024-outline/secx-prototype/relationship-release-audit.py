#!/usr/bin/env python3
"""Promotion gate for SecX prototype-released semantic relationships."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT / "RELATIONSHIP_REVIEW.json"
RELEASE = ROOT / "RELEASED_RELATIONSHIPS.json"
NEXT = ROOT / "next.html"
RUNTIME_FILES = (
    "index.html",
    "learner-registry.js",
    "next-layer.js",
    "learner-state.js",
    "due-review.js",
    "study-lens.js",
    "source-lens.js",
    "coverage-lens.js",
    "projection-search.js",
)
errors: list[str] = []


def check(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


try:
    review = load(REVIEW)
    release = load(RELEASE)
    next_html = NEXT.read_text(encoding="utf-8")
    runtime = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in RUNTIME_FILES)
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
check(release.get("learner_runtime_loaded") is False, "promotion-stage artifact must remain learner_runtime_loaded=false until runtime integration is separately gated")
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

check("RELEASED_RELATIONSHIPS.json" not in next_html, "promotion-stage release artifact must not yet be learner-loaded by next.html")
check("RELEASED_RELATIONSHIPS.json" not in runtime, "promotion-stage release artifact must not yet be referenced by learner runtime")
check("SECX_RELEASED_RELATIONSHIPS" not in runtime, "promotion stage must not silently publish a runtime relationship channel")

if errors:
    print("FAIL secx_relationship_release_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(
    "PASS secx_relationship_release_audit "
    f"approved={len(approved)} prototype_released={len(released)} learner_runtime_loaded=false "
    "review_copy=exact publication_scope=secx-review-prototype"
)
