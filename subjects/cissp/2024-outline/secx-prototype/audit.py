#!/usr/bin/env python3
"""Deterministic integrity audit for the isolated SecX CISSP knowledge-web prototype."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent / "study-site"
QB = STUDY / "question-bank"
errors: list[str] = []


def check(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def parse_wrapped(path: Path, prefix: str, suffix: str):
    text = read(path)
    if not text.startswith(prefix) or not text.endswith(suffix):
        raise RuntimeError(f"Unexpected wrapper in {path.name}")
    return json.loads(text[len(prefix) : len(text) - len(suffix)])


def parse_meta():
    text = read(STUDY / "data-meta.js")
    prefix = "window.CISSP_META="
    marker = ";window.CISSP_CHUNKS=[];"
    if not text.startswith(prefix) or marker not in text:
        raise RuntimeError("Unexpected data-meta.js wrapper")
    return json.loads(text[len(prefix) : text.index(marker)])


def parse_chunk(name: str):
    return parse_wrapped(STUDY / name, "window.CISSP_CHUNKS.push(", ");")


def parse_coverage():
    text = read(STUDY / "coverage-detail.js")
    prefix = "window.CISSP_COVERAGE="
    marker = ";\nwindow.CISSP_AI_COVERAGE="
    if not text.startswith(prefix) or marker not in text or not text.endswith(";"):
        raise RuntimeError("Unexpected coverage-detail.js wrapper")
    i = text.index(marker)
    return json.loads(text[len(prefix) : i])


def read_jsonl(path: Path):
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{path.relative_to(STUDY)}:{line_no}: {exc}") from exc
    return rows


def q_objectives(q):
    values = q.get("objectives")
    if isinstance(values, list):
        return [str(x) for x in values if str(x)]
    value = q.get("objective")
    return [str(value)] if value else []


try:
    meta = parse_meta()
    domain_chunks = [parse_chunk(f"data-d{i}.js") for i in range(1, 9)]
    precision = parse_chunk("data-precision.js")
    coverage = parse_coverage()
    manifest = json.loads(read(QB / "RELEASED_BATCHES.json"))
except (OSError, ValueError, RuntimeError) as exc:
    print("FAIL secx_graph_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

meta_info = meta.get("meta", {})
sources = set((meta.get("sources") or {}).keys())
objectives = [o for chunk in domain_chunks for o in chunk.get("objectives", [])]
base_questions = [q for chunk in domain_chunks for q in chunk.get("questions", [])]
cards = list(precision.get("high", []))
objective_ids = {str(o.get("id")) for o in objectives}
objective_by_id = {str(o.get("id")): o for o in objectives}

check(len(objectives) == meta_info.get("objective_count"), f"objective count drift: {len(objectives)} != {meta_info.get('objective_count')}")
check(sum(len(v) for v in coverage.values()) == meta_info.get("subtopic_checks"), "subtopic mapping count drift")
check(len(cards) == meta_info.get("card_count"), f"retrieval-card count drift: {len(cards)} != {meta_info.get('card_count')}")
check(len(objective_ids) == len(objectives), "duplicate objective IDs")
check(len({c.get('id') for c in cards}) == len(cards), "duplicate retrieval-card IDs")

for objective_id, items in coverage.items():
    check(objective_id in objective_ids, f"coverage references unknown objective: {objective_id}")
    check(isinstance(items, list) and all(isinstance(x, str) and x.strip() for x in items), f"invalid subtopic list for {objective_id}")
    check(len(items) == len(set(items)), f"duplicate subtopic labels under {objective_id}")

for card in cards:
    cid = card.get("id")
    oid = str(card.get("objective") or "")
    check(oid in objective_ids, f"{cid} references unknown objective {oid}")
    obj = objective_by_id.get(oid, {})
    if obj:
        check(card.get("domain_num") == obj.get("domain_num"), f"{cid} domain/objective mismatch")
    for source_id in card.get("source_ids", []):
        check(source_id in sources, f"{cid} references unknown source {source_id}")

released_rows = []
seen_manifest_files: set[str] = set()
for batch in manifest.get("released_batches", []):
    for rel in batch.get("files", []):
        check(rel not in seen_manifest_files, f"release manifest repeats file: {rel}")
        seen_manifest_files.add(rel)
        check(rel.startswith("question-bank/candidates/"), f"released file outside expected question-bank candidates path: {rel}")
        path = STUDY / rel
        check(path.is_file(), f"released file missing: {rel}")
        if path.is_file():
            try:
                released_rows.extend(read_jsonl(path))
            except RuntimeError as exc:
                errors.append(str(exc))

released_standard = [q for q in released_rows if q.get("format") == "mcq"]
released_bellringers = [q for q in released_rows if q.get("format") == "bellringer"]
all_standard = base_questions + released_standard

check(len(all_standard) == meta_info.get("question_count"), f"standard-question count drift: {len(all_standard)} != {meta_info.get('question_count')}")
check(len(released_bellringers) == meta_info.get("bellringer_count"), f"Bellringer count drift: {len(released_bellringers)} != {meta_info.get('bellringer_count')}")
check(len(all_standard) + len(released_bellringers) == meta_info.get("question_bank_records"), "question-bank record total drift")
check(len({q.get('id') for q in all_standard}) == len(all_standard), "duplicate standard-question IDs across base + released manifest")

explicit_subtopic_edges = 0
questions_with_explicit_subtopic_edge = 0
for q in all_standard:
    qid = q.get("id")
    objectives_for_q = q_objectives(q)
    check(bool(objectives_for_q), f"{qid} has no objective mapping")
    for oid in objectives_for_q:
        check(oid in objective_ids, f"{qid} references unknown objective {oid}")
    for source_id in q.get("source_ids", []):
        check(source_id in sources, f"{qid} references unknown source {source_id}")
    matched = 0
    for oid in objectives_for_q:
        allowed = set(coverage.get(oid, []))
        for label in q.get("subtopics", []) or []:
            if label in allowed:
                explicit_subtopic_edges += 1
                matched += 1
    if matched:
        questions_with_explicit_subtopic_edge += 1

next_layer = read(ROOT / "next-layer.js")
index_html = read(ROOT / "index.html")
check("RELEASED_BATCHES.json" in next_layer, "expanded runtime does not reference released manifest")
check("fetch(`../study-site/${p}`" in next_layer, "expanded runtime release-file loading no longer derives from manifest paths")
check("question-bank/candidates/" not in next_layer, "expanded runtime hard-codes a candidate-file path instead of release manifest")
check("q.subtopics.includes(label)" in next_layer, "subtopic/scenario relationship is no longer exact-tag based")
check("Correct answer:" in next_layer and next_layer.count("Correct answer:") == 1, "scenario answer reveal text should have one controlled runtime definition")
check(re.search(r"practice:`Correct answer:", next_layer) is not None, "scenario answer is not confined to the application/practice layer")
check("depth>=4" in index_html and "info.practice" in index_html, "base disclosure renderer no longer gates application content at depth four")
check("similarity" not in next_layer.lower(), "expanded runtime unexpectedly contains similarity-based relationship logic")

if errors:
    print("FAIL secx_graph_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(
    "PASS secx_graph_audit "
    f"objectives={len(objectives)} "
    f"subtopics={sum(len(v) for v in coverage.values())} "
    f"cards={len(cards)} "
    f"standard_questions={len(all_standard)} "
    f"bellringers={len(released_bellringers)} "
    f"manifest_files={len(seen_manifest_files)} "
    f"explicit_subtopic_edges={explicit_subtopic_edges} "
    f"questions_with_explicit_subtopic_edge={questions_with_explicit_subtopic_edge}"
)
