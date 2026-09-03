#!/usr/bin/env python3
"""Deterministic audit for the SecX source-provenance lens."""
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
    source_lens = read(ROOT / "source-lens.js")
    next_html = read(ROOT / "next.html")
    smoke = read(ROOT / "source-browser-smoke.html")
    smoke_shell = read(ROOT / "source-browser-smoke.sh")
except (OSError, ValueError, RuntimeError) as exc:
    print("FAIL secx_source_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

meta_info = meta.get("meta", {})
sources = meta.get("sources") or {}
objectives = [o for chunk in chunks for o in chunk.get("objectives", [])]
high_cards = [c for chunk in chunks for c in chunk.get("high", [])]
review_cards = [
    {"id": f"OBJ-{o['id']}", "objective": o.get("id"), "source_ids": o.get("source_ids", [])}
    for o in objectives
] + high_cards
source_ids = set(sources)

check(len(source_ids) == meta_info.get("source_count"), f"source count drift: {len(source_ids)} != {meta_info.get('source_count')}")
check(len(review_cards) == meta_info.get("card_count"), f"review-card count drift: {len(review_cards)} != {meta_info.get('card_count')}")
check(all((sources[sid].get("title") or "").strip() for sid in source_ids), "source registry contains blank title")
check(all((sources[sid].get("role") or "").strip() for sid in source_ids), "source registry contains blank role")

for item in objectives:
    for sid in item.get("source_ids", []):
        check(sid in source_ids, f"objective {item.get('id')} references unknown source {sid}")
for card in review_cards:
    for sid in card.get("source_ids", []):
        check(sid in source_ids, f"review card {card.get('id')} references unknown source {sid}")

check("source_ids.includes(id)" in source_lens, "source lens no longer derives membership from exact source_ids")
check("Shared citation is not a semantic edge" in source_lens, "source lens lost explicit co-citation non-semantic warning")
check("source co-citation does not create a cross-card semantic edge" in source_lens.lower(), "card source view lost co-citation boundary")
check("question-bank" not in source_lens.lower(), "source lens unexpectedly discovers question-bank files")
check("localStorage" not in source_lens, "source lens should not read or write learner state")
check("similarity" not in source_lens.lower(), "source lens unexpectedly uses similarity logic")
check("source-lens.js" in next_html, "expanded review page does not load source lens")
check(next_html.find("study-lens.js") < next_html.find("source-lens.js"), "source lens must load after learner/study runtime layers")
check("study.onload" in next_html, "source lens load is not gated on study-lens completion")
check("sourceLensBtn" in smoke and "KeyS" in smoke, "source browser smoke does not exercise source-lens control/shortcut")
check("source:ISC2_OUTLINE" in smoke and "source-item:objective:1.1" in smoke, "source browser smoke does not verify an exact source_ids mapping")
check("--user-data-dir=" in smoke_shell, "source browser smoke does not isolate browser storage")

if errors:
    print("FAIL secx_source_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

objective_citations = sum(len(o.get("source_ids", [])) for o in objectives)
card_citations = sum(len(c.get("source_ids", [])) for c in review_cards)
print(f"PASS secx_source_audit sources={len(source_ids)} objectives={len(objectives)} review_cards={len(review_cards)} objective_source_refs={objective_citations} card_source_refs={card_citations} mapping=explicit-source_ids-only")
