#!/usr/bin/env python3
"""Deterministic audit for the SecX explicit coverage lens."""
from __future__ import annotations

import json
import sys
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


def parse_coverage():
    text = read(STUDY / "coverage-detail.js")
    prefix = "window.CISSP_COVERAGE="
    marker = ";\nwindow.CISSP_AI_COVERAGE="
    if not text.startswith(prefix) or marker not in text:
        raise RuntimeError("Unexpected coverage-detail.js wrapper")
    return json.loads(text[len(prefix):text.index(marker)])


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
    chunks = [parse_chunk(f"data-d{i}.js") for i in range(1, 9)] + [parse_chunk("data-ai.js"), parse_chunk("data-precision.js")]
    coverage = parse_coverage()
    manifest = json.loads(read(QB / "RELEASED_BATCHES.json"))
    lens = read(ROOT / "coverage-lens.js")
    next_layer = read(ROOT / "next-layer.js")
    next_html = read(ROOT / "next.html")
    smoke = read(ROOT / "coverage-browser-smoke.html")
    smoke_shell = read(ROOT / "coverage-browser-smoke.sh")
except (OSError, ValueError, RuntimeError) as exc:
    print("FAIL secx_coverage_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

meta_info = meta.get("meta", {})
objectives = [o for chunk in chunks for o in chunk.get("objectives", [])]
base_questions = [q for chunk in chunks for q in chunk.get("questions", [])]
high_cards = [c for chunk in chunks for c in chunk.get("high", [])]
objective_ids = {str(o.get("id")) for o in objectives}
review_cards = [{"id": f"OBJ-{o['id']}", "objective": o.get("id")} for o in objectives] + high_cards

released_rows = []
manifest_files: list[str] = []
for batch in manifest.get("released_batches", []):
    for rel in batch.get("files", []):
        manifest_files.append(rel)
        path = STUDY / rel
        check(path.is_file(), f"released manifest file missing: {rel}")
        if path.is_file():
            try:
                released_rows.extend(read_jsonl(path))
            except RuntimeError as exc:
                errors.append(str(exc))

released_standard = [q for q in released_rows if q.get("format") == "mcq"]
all_standard = base_questions + released_standard

check(len(objectives) == meta_info.get("objective_count"), "objective count drift")
check(sum(len(v) for v in coverage.values()) == meta_info.get("subtopic_checks"), "subtopic count drift")
check(len(review_cards) == meta_info.get("card_count"), "review-card count drift")
check(len(all_standard) == meta_info.get("question_count"), "released standard-question count drift")
check(len(set(manifest_files)) == len(manifest_files), "release manifest repeats a file")

scenario_counts = {oid: 0 for oid in objective_ids}
tagged_subtopics = {oid: set() for oid in objective_ids}
for q in all_standard:
    for oid in q_objectives(q):
        check(oid in objective_ids, f"{q.get('id')} references unknown objective {oid}")
        if oid not in objective_ids:
            continue
        scenario_counts[oid] += 1
        allowed = set(coverage.get(oid, []))
        for label in q.get("subtopics", []) or []:
            if label in allowed:
                tagged_subtopics[oid].add(label)

objective_without_scenarios = sum(1 for oid in objective_ids if scenario_counts[oid] == 0)
subtopics_with_exact_tag = sum(len(v) for v in tagged_subtopics.values())
subtopics_total = sum(len(v) for v in coverage.values())
practice_exposure_gaps = subtopics_total - subtopics_with_exact_tag
expected_gap_ids = {
    f"coverage:gap:{oid}:{index}"
    for oid, labels in coverage.items()
    for index, label in enumerate(labels)
    if label not in tagged_subtopics.get(oid, set())
}

check("RELEASED_BATCHES.json" in next_layer, "central released-bank loader does not use release manifest")
check("fetch(`../study-site/${p}`" in next_layer, "central released-bank loader no longer loads manifest-listed files")
check("window.SECX_RELEASED_QUESTIONS" in next_layer and "window.SECX_RELEASED_BANK_STATE" in next_layer, "central released-scenario registry export missing")
check("secx:released-bank" in next_layer, "central released-bank readiness event missing")
check("SECX_RELEASED_QUESTIONS" in lens and "SECX_RELEASED_BANK_STATE" in lens, "coverage lens does not consume shared released-scenario registry")
check("coverageQuestions=window.SECX_RELEASED_QUESTIONS" in lens, "coverage lens does not use shared released scenario records directly")
check("secx:released-bank" in lens, "coverage lens does not refresh from shared bank readiness event")
check("RELEASED_BATCHES.json" not in lens, "coverage lens duplicates release-manifest loading")
check("fetch(" not in lens, "coverage lens performs an independent network fetch")
check("question-bank/candidates/" not in lens, "coverage lens hard-codes candidate paths")
check("q.subtopics.includes(label)" in lens, "coverage lens exact scenario-tag coverage logic missing")
check("SECX_COVERAGE_SNAPSHOT" in lens, "coverage lens does not expose deterministic count snapshot")
check("practice_exposure_gaps" in lens, "coverage snapshot does not expose exact-tag practice gap count")
check("function gapRecords()" in lens, "coverage lens has no exact-tag gap registry")
check("coverage:gap:${record.objective}:${record.index}" in lens, "coverage gap nodes do not use stable projection ids derived from objective/index")
check("window.coverageGapLayout" in lens and "level='coverage-gaps'" in lens, "coverage lens has no paged practice exposure gap view")
check("n?.id==='coverage:root'" in lens and "coverageGapLayout(null,true,0)" in lens, "coverage root Enter does not open practice exposure gaps")
check("SecX › Coverage › Practice exposure gaps" in lens, "coverage gap breadcrumb missing")
check("level==='coverage-gaps'" in lens and "coverageLayout('coverage:root',true)" in lens, "coverage gap Escape hierarchy missing")
check("Practice exposure counts do not measure learner mastery" in lens, "coverage lens lost mastery-boundary warning")
check("exact-tag practice-exposure gap" in lens, "coverage gap detail does not preserve exact-tag exposure terminology")
check("not evidence that the subtopic is missing from the curriculum" in lens, "coverage gap detail lost curriculum-omission boundary")
check("not learner weakness" in lens, "coverage gap detail lost learner-state boundary")
check("localStorage" not in lens, "coverage lens should not read or write learner state")
check("cissp_atlas_progress_v1" not in lens and "cissp_secx_graph_state_v1" not in lens, "coverage lens is coupled to learner state")
check("RELATIONSHIP_REVIEW" not in lens, "coverage lens accesses reviewer semantic relationships")
for forbidden in ("similarityScore", "levenshtein", "fuzzyMatch", "cosineSimilarity", "semanticDistance", "relationshipScore"):
    check(forbidden not in lens, f"coverage lens contains inferred-relationship helper: {forbidden}")
check("coverage-lens.js" in next_html, "expanded page does not load coverage lens")
check(next_html.find("source-lens.js") < next_html.find("coverage-lens.js"), "coverage lens must load after source lens")
check("sources.onload" in next_html, "coverage lens load is not gated on source-lens completion")
check("RELATIONSHIP_REVIEW.json" not in next_html, "reviewer relationship registry is learner-loaded")
check("coverageLensBtn" in smoke and "KeyC" in smoke, "coverage browser smoke does not exercise coverage control/shortcut")
check("coverage:d1" in smoke and "coverage:objective:1.1" in smoke, "coverage browser smoke does not verify domain/objective traversal")
check("coverage:gaps" in smoke and "coverage-gap" in smoke, "coverage browser smoke does not verify practice exposure gap traversal")
check("practice_exposure_gaps" in smoke, "coverage browser smoke does not validate deterministic gap total")
check("SECX_RELEASED_BANK_STATE" in smoke, "coverage browser smoke does not wait for shared released-bank readiness")
check("--user-data-dir=" in smoke_shell, "coverage browser smoke does not isolate browser storage")

if errors:
    print("FAIL secx_coverage_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(
    "PASS secx_coverage_audit "
    f"objectives={len(objectives)} "
    f"subtopics={subtopics_total} "
    f"review_cards={len(review_cards)} "
    f"standard_questions={len(all_standard)} "
    f"subtopics_with_exact_scenario_tag={subtopics_with_exact_tag} "
    f"practice_exposure_gaps={practice_exposure_gaps} "
    f"gap_projection_ids={len(expected_gap_ids)} "
    f"objectives_without_scenarios={objective_without_scenarios} "
    "mapping=explicit-counts-and-gaps-only shared_bank=single-release-boundary"
)
