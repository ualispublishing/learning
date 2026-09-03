#!/usr/bin/env python3
"""Deterministic audit for the SecX learner-state study lens."""
from __future__ import annotations

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


try:
    production = read(STUDY / "app.js")
    registry = read(ROOT / "learner-registry.js")
    learner = read(ROOT / "learner-state.js")
    due = read(ROOT / "due-review.js")
    lens = read(ROOT / "study-lens.js")
    next_html = read(ROOT / "next.html")
    smoke = read(ROOT / "browser-smoke.html")
except OSError as exc:
    print("FAIL secx_study_lens_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

atlas_key = "cissp_atlas_progress_v1"
check(atlas_key in production and atlas_key in learner and atlas_key in lens, "study lens no longer derives from the shared Atlas progress record")
check("window.SECX_RELEASED_CARDS" in registry and "window.SECX_RELEASED_CARDS" in lens, "study lens no longer uses the released Atlas review-card registry")
check("question-bank" not in lens.lower(), "study lens must not derive learner queues from scenario/candidate question-bank data")
check("cissp_secx_graph_state_v1" not in lens, "study lens must not reinterpret graph visits or scenario exposure as review-stage state")

for mode in ("due", "new", "learning", "mature", "weak"):
    check(f"mode:'{mode}'" in lens or f"mode==='{mode}'" in lens, f"study lens missing {mode} queue")
check("s.due<=today" in lens, "due study queue no longer uses scheduled Atlas due date")
check("!progressState(c.id)" in lens, "new study queue no longer means ungraded Atlas card")
check("statusOf(c.id)==='learning'" in lens, "learning queue no longer uses Atlas review stage status")
check("statusOf(c.id)==='mature'" in lens, "mature queue no longer uses Atlas stage-4+ status")

check("Math.min(4,progressState(c.id)?.stage||0)" in lens, "objective review-score calculation drifted from Atlas stage cap")
check("/(cards.length*4)" in lens, "objective review-score denominator no longer matches Atlas stage score")
check("a.score-b.score||b.weight-a.weight" in lens, "lowest-domain tie-break no longer prioritizes lower score then higher exam weight")
check("Math.min(4,(cardState(c.id)?.stage||0))" in production, "production Atlas objective-score stage cap changed")
check("sort((a,b)=>a.score-b.score||b.weight-a.weight)" in production, "production Atlas weakest-domain tie-break changed")

check("review-stage score" in lens and "not proof of knowledge" in lens, "study lens no longer states the review-score evidence boundary")
check("Scenario answer exposure is not counted as retrieval mastery" in lens, "study lens no longer protects the scenario-exposure/mastery boundary")
check("localStorage.setItem" not in lens, "study lens should read learner state and delegate grading, not maintain a second progress store")
check("[data-sec-grade]" in lens, "study lens does not refresh after same-window Atlas grading")

order = [
    next_html.find("learner-registry.js"),
    next_html.find("next-layer.js"),
    next_html.find("learner-state.js"),
    next_html.find("due-review.js"),
    next_html.find("study-lens.js"),
]
check(all(i >= 0 for i in order), "expanded page missing a learner/study runtime layer")
check(order == sorted(order) and len(set(order)) == len(order), "study lens load order is invalid")
check("due.onload" in next_html, "study lens is not gated on due-review readiness")

check("#studyQueueBtn" in smoke, "browser smoke does not wait for study-lens readiness")
check("study:queue" in smoke and "KeyQ" in smoke, "browser smoke does not exercise the Q study-queue shortcut")
check("study:new" in smoke and "study:weak" in smoke, "browser smoke does not verify study queue facets")

if errors:
    print("FAIL secx_study_lens_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("PASS secx_study_lens_audit queues=due,new,learning,mature,weak scoring=Atlas-stage-compatible state=read-only-from-Atlas")
