#!/usr/bin/env python3
"""Deterministic audit for the SecX due-review learner-state branch."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent / "study-site"
errors: list[str] = []


def check(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def parse_meta():
    text = read(STUDY / "data-meta.js")
    prefix = "window.CISSP_META="
    marker = ";window.CISSP_CHUNKS=[];"
    if not text.startswith(prefix) or marker not in text:
        raise RuntimeError("Unexpected data-meta.js wrapper")
    return json.loads(text[len(prefix):text.index(marker)])


def parse_precision():
    text = read(STUDY / "data-precision.js")
    prefix = "window.CISSP_CHUNKS.push("
    suffix = ");"
    if not text.startswith(prefix) or not text.endswith(suffix):
        raise RuntimeError("Unexpected data-precision.js wrapper")
    return json.loads(text[len(prefix):-len(suffix)])


try:
    meta = parse_meta()
    precision = parse_precision()
    registry = read(ROOT / "learner-registry.js")
    learner = read(ROOT / "learner-state.js")
    due = read(ROOT / "due-review.js")
    next_html = read(ROOT / "next.html")
    smoke = read(ROOT / "browser-smoke.html")
except (OSError, ValueError, RuntimeError) as exc:
    print("FAIL secx_due_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

cards = precision.get("high", [])
expected = meta.get("meta", {}).get("card_count")
check(len(cards) == expected, f"released retrieval-card count drift: {len(cards)} != {expected}")
check(len({c.get('id') for c in cards}) == len(cards), "duplicate retrieval-card IDs")

check("window.CISSP_CHUNKS" in registry and ".flatMap" in registry and ".high" in registry, "released-card registry no longer derives from CISSP_CHUNKS.high")
check("window.SECX_RELEASED_CARDS=retrievalCards" in registry, "released-card registry export missing")
check("question-bank" not in registry.lower(), "released-card registry unexpectedly references question-bank data")

order = [
    next_html.find("data-precision.js"),
    next_html.find("learner-registry.js"),
    next_html.find("next-layer.js"),
    next_html.find("learner-state.js"),
    next_html.find("due-review.js"),
]
check(all(i >= 0 for i in order), "expanded page is missing a required runtime layer")
check(order == sorted(order) and len(set(order)) == len(order), "expanded page runtime load order is invalid")
check(next_html.count(".onload=") >= 4, "expanded page no longer gates dependent layers by load completion")

check("cissp_atlas_progress_v1" in learner and "cissp_atlas_progress_v1" in due, "due review is not tied to Atlas card progress")
check("cissp_secx_graph_state_v1" in learner, "graph-specific learner state key missing")
check("s.due<=today" in due, "due queue no longer filters by scheduled due date")
check("retrievalCards" in due, "due queue no longer uses released retrieval-card registry")
check("question-bank" not in due.lower(), "due queue unexpectedly references scenario/candidate question-bank files")
check("dueReviewLayout" in due and "level='due-reviews'" in due, "due-review local graph branch missing")
check("Review due" in due and "KeyR" not in due, "due-review button/shortcut source changed unexpectedly")
check("e.key==='r'||e.key==='R'" in due, "R keyboard shortcut for due review missing")
check("[data-sec-grade]" in due and "updateDueButton()" in due, "same-window grade does not refresh due queue/count")
check("dueCards().some" in due, "due branch does not reconcile a graded card against current due state")
check("correct" not in due.lower() and "mastery" not in due.lower(), "due-review view should not write or infer correctness/mastery")

check("#dueReviewBtn" in smoke, "browser smoke does not wait for due-review layer")
check("due:reviews" in smoke and "KeyR" in smoke, "browser smoke does not exercise due-review keyboard branch")
check("same-window grade" in smoke, "browser smoke does not verify same-window due-count update")

if errors:
    print("FAIL secx_due_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(f"PASS secx_due_audit released_cards={len(cards)} load_order=precision>registry>graph>learner>due source=Atlas-progress-only")
