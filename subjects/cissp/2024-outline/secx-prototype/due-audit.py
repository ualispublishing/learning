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


def parse_chunk(name: str):
    text = read(STUDY / name)
    prefix = "window.CISSP_CHUNKS.push("
    suffix = ");"
    if not text.startswith(prefix) or not text.endswith(suffix):
        raise RuntimeError(f"Unexpected {name} wrapper")
    return json.loads(text[len(prefix):-len(suffix)])


try:
    meta = parse_meta()
    chunks = [parse_chunk(f"data-d{i}.js") for i in range(1, 9)] + [parse_chunk("data-ai.js"), parse_chunk("data-precision.js")]
    registry = read(ROOT / "learner-registry.js")
    learner = read(ROOT / "learner-state.js")
    due = read(ROOT / "due-review.js")
    next_html = read(ROOT / "next.html")
    smoke = read(ROOT / "browser-smoke.html")
except (OSError, ValueError, RuntimeError) as exc:
    print("FAIL secx_due_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

objectives = [o for chunk in chunks for o in chunk.get("objectives", [])]
high_cards = [c for chunk in chunks for c in chunk.get("high", [])]
objective_card_ids = {f"OBJ-{o.get('id')}" for o in objectives}
high_card_ids = {str(c.get("id")) for c in high_cards}
layered_count = len(objectives) + len(high_cards)
expected = meta.get("meta", {}).get("card_count")

check(layered_count == expected, f"Atlas layered review-card count drift: {layered_count} != {expected}")
check(len(objective_card_ids) == len(objectives), "duplicate generated objective-card IDs")
check(len(high_card_ids) == len(high_cards), "duplicate high-yield review-card IDs")
check(not (objective_card_ids & high_card_ids), "generated objective-card IDs collide with high-yield IDs")

check("window.CISSP_CHUNKS" in registry and ".flatMap" in registry and ".high" in registry, "released-card registry no longer derives high-yield cards from CISSP_CHUNKS")
check("id:`OBJ-${o.id}`" in registry, "released-card registry no longer generates Atlas objective-card IDs")
check("...secxObjectives.map" in registry and "...secxHighCards.map" in registry, "released-card registry no longer combines objective and high-yield cards")
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
check("retrievalCards" in due, "due queue no longer uses Atlas review-card registry")
check("question-bank" not in due.lower(), "due queue unexpectedly references scenario/candidate question-bank files")
check("dueReviewLayout" in due and "level='due-reviews'" in due, "due-review local graph branch missing")
check("Review due" in due, "due-review button source changed unexpectedly")
check("e.key==='r'||e.key==='R'" in due, "R keyboard shortcut for due review missing")
check("[data-sec-grade]" in due and "updateDueButton()" in due, "same-window grade does not refresh due queue/count")
check("dueCards().some" in due, "due branch does not reconcile a graded card against current due state")
check("correct" not in due.lower() and "mastery" not in due.lower(), "due-review view should not write or infer correctness/mastery")

check("#dueReviewBtn" in smoke, "browser smoke does not wait for due-review layer")
check("due:reviews" in smoke and "KeyR" in smoke, "browser smoke does not exercise due-review keyboard branch")
check("same-window grade" in smoke, "browser smoke does not verify same-window due-count update")
check("SECX_RELEASED_CARDS" in smoke and "reviewCardCount===meta.card_count" in smoke, "browser smoke no longer reconciles learner registry to Atlas card_count")

if errors:
    print("FAIL secx_due_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(f"PASS secx_due_audit layered_review_cards={layered_count} objective_cards={len(objectives)} high_yield_cards={len(high_cards)} load_order=precision>registry>graph>learner>due source=Atlas-progress-only")
