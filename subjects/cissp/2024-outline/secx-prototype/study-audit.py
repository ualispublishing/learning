#!/usr/bin/env python3
"""Deterministic audit for the SecX learner-state study lens."""
from __future__ import annotations

import re
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
    continue_smoke = read(ROOT / "continue-browser-smoke.html")
except OSError as exc:
    print("FAIL secx_study_lens_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

atlas_key = "cissp_atlas_progress_v1"
check(atlas_key in production and atlas_key in learner, "shared Atlas progress record is missing from production or learner-state owner")
check("window.SECX_RELEASED_CARDS" in registry and "window.SECX_RELEASED_CARDS" in lens, "study lens no longer uses the released Atlas review-card registry")
check("question-bank" not in lens.lower(), "study lens must not derive learner queues from scenario/candidate question-bank data")
check("cissp_secx_graph_state_v1" not in lens, "study lens must not reinterpret graph visits or scenario exposure as review-stage state")

api_block = re.search(r"const learnerApi=Object\.freeze\(\{(.*?)\}\);", learner, re.S)
check(bool(api_block), "learner-state owner no longer exports a frozen read-only learner API")
if api_block:
    api_text = api_block.group(1)
    for token in ("progressKey:ATLAS_PROGRESS_KEY", "cardState", "cardStatus", "isDue", "isMature", "todayISO"):
        check(token in api_text, f"learner API missing read method/metadata: {token}")
    for forbidden in ("gradeCard", "saveAtlas", "setItem", "saveGraph"):
        check(forbidden not in api_text, f"learner API unexpectedly exposes mutation capability: {forbidden}")
check("Object.defineProperty(window,'SECX_LEARNER'" in learner, "learner API is not exported through SECX_LEARNER")
check("syncAtlas()" in learner and "atlasRaw" in learner, "learner API no longer resynchronizes same-window local-storage changes")
check("const learner=window.SECX_LEARNER" in due and "const learner=window.SECX_LEARNER" in lens, "Due/Study consumers no longer share SECX_LEARNER")
check("localStorage" not in due and "localStorage" not in lens, "Due/Study consumers must not parse or write Atlas storage directly")

for mode in ("due", "new", "learning", "mature", "weak"):
    check(f"mode:'{mode}'" in lens or f"mode==='{mode}'" in lens, f"study lens missing {mode} queue")
check("learner.isDue(c.id)" in lens, "due study queue no longer uses shared scheduled Atlas due semantics")
check("!progressState(c.id)" in lens, "new study queue no longer means ungraded Atlas card")
check("statusOf(c.id)==='learning'" in lens and "learner.cardStatus(id)" in lens, "learning queue no longer uses shared Atlas card status")
check("statusOf(c.id)==='mature'" in lens, "mature queue no longer uses Atlas stage-4+ status")

check("Math.min(4,progressState(c.id)?.stage||0)" in lens, "objective review-score calculation drifted from Atlas stage cap")
check("/(cards.length*4)" in lens, "objective review-score denominator no longer matches Atlas stage score")
check("a.score-b.score||b.weight-a.weight" in lens, "lowest-domain tie-break no longer prioritizes lower score then higher exam weight")
check("Math.min(4,(cardState(c.id)?.stage||0))" in production, "production Atlas objective-score stage cap changed")
check("sort((a,b)=>a.score-b.score||b.weight-a.weight)" in production, "production Atlas weakest-domain tie-break changed")

check("continueStudyBtn" in lens, "study lens is missing the visible Continue control")
check("function continuePlan()" in lens, "study lens is missing deterministic Continue planning")
continue_tokens = [
    "const due=cardsForMode('due')",
    "if(due.length)return{mode:'due'",
    "const learning=cardsForMode('learning')",
    "if(learning.length)return{mode:'learning'",
    "weakNew=fresh.filter(c=>c.domain_num===weak.num)",
    "if(weakNew.length)return{mode:'new'",
    "if(fresh.length)return{mode:'new'",
    "return{mode:'root',label:'Study',card:null}",
]
for token in continue_tokens:
    check(token in lens, f"Continue priority contract drifted: missing {token}")
check("pageForCard(plan.mode,plan.card?.id)" in lens, "Continue does not route to the page containing its selected review card")
check("studyCardLayout(plan.mode,plan.card?.id||null,true" in lens, "Continue does not reuse the existing Study card layout")
check("studyQueueLayout(true)" in lens, "Continue has no caught-up fallback to the existing Study Queue root")
check("continueButton.addEventListener('click',runContinue)" in lens, "Continue button does not invoke the learner-state routing helper")
check("refreshStudyControls()" in lens and "learner.progressKey" in lens, "Continue label does not refresh from the shared learner API")

check("review-stage score" in lens and "not proof of knowledge" in lens, "study lens no longer states the review-score evidence boundary")
check("Scenario answer exposure is not counted as retrieval mastery" in lens, "study lens no longer protects the scenario-exposure/mastery boundary")
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
check("continueStudyBtn" in continue_smoke, "Continue browser smoke does not wait for the visible Continue control")
check("study:list:due" in continue_smoke and "Continue · Due" in continue_smoke, "Continue browser smoke does not prove due-first routing")
check("study:list:learning" in continue_smoke and "Continue · Learning" in continue_smoke, "Continue browser smoke does not prove learning fallback")
check("Continue · New D1" in continue_smoke and "study:list:new" in continue_smoke, "Continue browser smoke does not prove weakest-domain new-card fallback")
check("Continue · Study" in continue_smoke and "study:queue" in continue_smoke, "Continue browser smoke does not prove caught-up Study Queue fallback")
check("SECX_LEARNER" in continue_smoke and "Object.isFrozen" in continue_smoke, "Continue browser smoke does not verify the read-only learner API")

if errors:
    print("FAIL secx_study_lens_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("PASS secx_study_lens_audit queues=due,new,learning,mature,weak continue=due>learning>weak-new>new>study-root scoring=Atlas-stage-compatible state=shared-read-only-learner-api")
