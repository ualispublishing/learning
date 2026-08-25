#!/usr/bin/env python3
"""Deterministic release audit for CISSP Atlas.

Runtime data files are JavaScript wrappers around JSON-like payloads. The audit
parses them as data without executing JavaScript and normalizes only bare integer
object keys used by the AI coverage map.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QB = ROOT / "question-bank"
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def read(path):
    return path.read_text(encoding="utf-8").strip()


def decode_jsonish(payload, label):
    try:
        return json.loads(payload)
    except json.JSONDecodeError as first_error:
        normalized = re.sub(r"(?m)^(\s*)(\d+)\s*:", r'\1"\2":', payload)
        if normalized == payload:
            raise RuntimeError(f"{label} is not valid JSON-compatible data: {first_error}") from first_error
        try:
            return json.loads(normalized)
        except json.JSONDecodeError as second_error:
            raise RuntimeError(
                f"{label} is not valid JSON-compatible JavaScript data: {second_error}"
            ) from second_error


def parse_meta():
    raw = read(ROOT / "data-meta.js")
    prefix = "window.CISSP_META="
    marker = ";window.CISSP_CHUNKS=[];"
    if not raw.startswith(prefix) or marker not in raw:
        raise RuntimeError("data-meta.js wrapper invalid")
    return decode_jsonish(raw[len(prefix):raw.index(marker)], "data-meta.js")


def parse_chunk(name):
    raw = read(ROOT / name)
    prefix, suffix = "window.CISSP_CHUNKS.push(", ");"
    if not raw.startswith(prefix) or not raw.endswith(suffix):
        raise RuntimeError(f"{name} wrapper invalid")
    return decode_jsonish(raw[len(prefix):-len(suffix)], name)


def parse_coverage():
    raw = read(ROOT / "coverage-detail.js")
    first_prefix = "window.CISSP_COVERAGE="
    marker = ";\nwindow.CISSP_AI_COVERAGE="
    if not raw.startswith(first_prefix) or marker not in raw or not raw.endswith(";"):
        raise RuntimeError("coverage-detail.js wrapper invalid")
    split = raw.index(marker)
    coverage = decode_jsonish(raw[len(first_prefix):split], "CISSP coverage")
    ai = decode_jsonish(raw[split + len(marker):-1], "CISSP AI coverage")
    return coverage, ai


def load_jsonl(path):
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{path.relative_to(ROOT)}:{line_no} invalid JSONL: {exc}"
            ) from exc
    return rows


try:
    meta = parse_meta()
    chunks = [parse_chunk(f"data-d{i}.js") for i in range(1, 9)] + [
        parse_chunk("data-ai.js"),
        parse_chunk("data-precision.js"),
    ]
    coverage, ai = parse_coverage()
    release = json.loads(read(ROOT / "RELEASE_STATUS.json"))
    semantic = json.loads(read(ROOT / "SEMANTIC_ITEM_AUDIT.json"))
    release_manifest = json.loads(read(QB / "RELEASED_BATCHES.json"))
except (OSError, ValueError, RuntimeError, AssertionError) as exc:
    print("FAIL")
    print(f"- Parse/setup error: {exc}")
    sys.exit(1)

objectives = sum((c["objectives"] for c in chunks), [])
high = sum((c["high"] for c in chunks), [])
base_questions = sum((c["questions"] for c in chunks), [])

released = []
released_paths = set()
for batch_info in release_manifest.get("released_batches", []):
    batch = []
    for rel in batch_info.get("files", []):
        check(rel not in released_paths, f"Released file listed more than once: {rel}")
        released_paths.add(rel)
        path = ROOT / rel
        check(path.is_file(), f"Released file missing: {rel}")
        if path.is_file():
            try:
                batch += load_jsonl(path)
            except RuntimeError as exc:
                errors.append(str(exc))
    for review_rel in batch_info.get("review_files", []):
        review_path = ROOT / review_rel
        check(review_path.is_file(), f"Release review file missing: {review_rel}")
        if review_path.is_file():
            try:
                review = json.loads(read(review_path))
                check(
                    str(review.get("status", "")).startswith("SEMANTIC_REVIEWED_"),
                    f"Release review is not semantically reviewed: {review_rel}",
                )
            except ValueError as exc:
                errors.append(f"{review_rel} invalid JSON: {exc}")
    released += batch
    dist = Counter(x.get("difficulty_tier") for x in batch)
    batch_id = batch_info.get("batch_id")
    check(len(batch) == batch_info.get("records"), f"{batch_id} record count drift")
    check(
        sum(x.get("format") == "mcq" for x in batch) == batch_info.get("standard_mcq"),
        f"{batch_id} MCQ count drift",
    )
    check(
        sum(x.get("format") == "bellringer" for x in batch) == batch_info.get("bellringers"),
        f"{batch_id} Bellringer count drift",
    )
    check(
        {k: dist.get(k, 0) for k in ("F", "E", "S", "B")} == batch_info.get("difficulty"),
        f"{batch_id} difficulty drift",
    )
    check(batch_info.get("semantic_review") == "PASS", f"{batch_id} semantic release gate missing")
    check(batch_info.get("originality_preflight") == "PASS", f"{batch_id} originality gate missing")

released_mcq = [x for x in released if x.get("format") == "mcq"]
bellringers = [x for x in released if x.get("format") == "bellringer"]
all_questions = base_questions + released_mcq

expected_counts = {1: 12, 2: 6, 3: 10, 4: 3, 5: 6, 6: 5, 7: 15, 8: 5}
expected_weights = {1: 16, 2: 10, 3: 13, 4: 13, 5: 13, 6: 12, 7: 13, 8: 10}

# Public blueprint structure and official weights.
check(len(meta["domains"]) == 8, "Expected 8 domains")
check(sum(d["weight"] for d in meta["domains"]) == 100, "Weights !=100")
check({d["num"]: d["weight"] for d in meta["domains"]} == expected_weights, "Official weights drift")
for domain, count in expected_counts.items():
    check(sum(o["domain_num"] == domain for o in objectives) == count, f"D{domain} objective count wrong")

ids = [o["id"] for o in objectives]
check(len(ids) == 62 and len(ids) == len(set(ids)), "Objective IDs incomplete/duplicate")
for domain, count in expected_counts.items():
    check(all(f"{domain}.{i}" in ids for i in range(1, count + 1)), f"D{domain} missing objective ID")

# Coverage layers.
check(set(coverage) == set(ids), "Subtopic coverage keys must exactly match objectives")
check(
    all(isinstance(v, list) and v and all(isinstance(x, str) and x.strip() for x in v) for v in coverage.values()),
    "Invalid subtopic coverage",
)
check(set(ai) == {str(i) for i in range(1, 9)}, "AI coverage must include all domains")
check(all(isinstance(v, list) and v for v in ai.values()), "Empty AI coverage domain")

# Cards, source mappings, and teaching content.
for o in objectives:
    check(bool(o.get("direct", "").strip()) and bool(o.get("trap", "").strip()), f"Objective {o['id']} missing content")
    check(all(s in meta["sources"] for s in o.get("source_ids", [])), f"Objective {o['id']} source invalid")
for h in high:
    check(h["objective"] in ids, f"Card {h['id']} objective invalid")
    check(
        bool(h.get("front", "").strip()) and bool(h.get("direct", "").strip()) and bool(h.get("trap", "").strip()),
        f"Card {h['id']} missing content",
    )
    check(all(s in meta["sources"] for s in h.get("source_ids", [])), f"Card {h['id']} source invalid")

# Base and released question integrity.
for q in base_questions:
    check(q["objective"] in ids, f"Base question {q['id']} objective invalid")
    check(len(q["options"]) == 4 and isinstance(q["answer"], int) and 0 <= q["answer"] < 4, f"Base question {q['id']} answer/options invalid")
    check(bool(q.get("stem", "").strip()) and bool(q.get("explanation", "").strip()), f"Base question {q['id']} content missing")

for q in released:
    qid = q.get("id")
    check(all(o in ids for o in q.get("objectives", [])), f"Released record {qid} objective invalid")
    check(all(s in meta["sources"] for s in q.get("source_ids", [])), f"Released record {qid} source invalid")
    check(str(q.get("review_status", "")).startswith("SEMANTIC_REVIEWED_"), f"Released record {qid} not semantically reviewed")
    originality = q.get("originality", {})
    check(
        originality.get("origin") == "original-from-public-scope"
        and originality.get("no_external_question_seed") is True,
        f"Released record {qid} originality provenance invalid",
    )
    if q.get("format") == "mcq":
        check(
            len(q.get("options", [])) == 4
            and isinstance(q.get("answer"), int)
            and 0 <= q["answer"] < 4
            and len(q.get("distractor_rationales", [])) == 4,
            f"Released MCQ {qid} invalid",
        )
    elif q.get("format") == "bellringer":
        check(
            q.get("difficulty_tier") == "B"
            and 4 <= len(q.get("prompts", [])) <= 8
            and bool(q.get("rubric")),
            f"Bellringer {qid} invalid",
        )
    else:
        check(False, f"Released record {qid} format invalid")

check(len({h["id"] for h in high}) == len(high), "Duplicate high-card ID")
check(len({q["id"] for q in all_questions}) == len(all_questions), "Duplicate standard-question ID")
check(len({q["id"] for q in released}) == len(released), "Duplicate released-batch ID")

computed_cards = 62 + len(high)
subtopics = sum(len(v) for v in coverage.values())
ai_areas = sum(len(v) for v in ai.values())
sources = len(meta["sources"])
standard_count = len(all_questions)
bellringer_count = len(bellringers)
bank_count = standard_count + bellringer_count
semantic_count = len(semantic.get("items", {}))
released_dist_total = Counter(q.get("difficulty_tier") for q in all_questions + bellringers)

check(computed_cards == 140, "Runtime cards !=140")
check(len(base_questions) == 56, "Base question baseline !=56")
check(standard_count >= 159, "Released standard MCQs fell below v1.4 floor")
check(bellringer_count >= 1, "Released Bellringers fell below v1.4 floor")
check(bank_count >= 160, "Question-bank records fell below v1.4 floor")
check(sources == 20, "Source count !=20")
check(subtopics == 344, "Subtopic count !=344")
check(ai_areas == 33, "AI area count !=33")
for domain in range(1, 9):
    check(
        sum((q.get("domain_num") if "domain_num" in q else q.get("domain_primary")) == domain for q in all_questions) >= 9,
        f"D{domain} standard-question coverage too low",
    )
    check(sum(h["domain_num"] == domain and h["id"].startswith("PX-") for h in high) == 4, f"D{domain} precision cards !=4")
    check(sum(h["domain_num"] == domain and h["id"].startswith("AI-") for h in high) == 1, f"D{domain} AI cards !=1")

# Metadata and release-ledger consistency.
cal_raw = read(ROOT / "data-question-calibration.js")
check(all(f'"Q-{i:03d}"' in cal_raw for i in range(1, 57)), "Base difficulty calibration incomplete")
mm = meta["meta"]
release_version = release.get("release")
check(release_version == mm.get("version") == semantic.get("release"), "Release version drift across ledgers")
check(mm.get("audited_on") == "2026-08-24", "Metadata audit date drift")
check(
    mm.get("objective_count") == 62
    and mm.get("subtopic_checks") == subtopics
    and mm.get("ai_coverage_areas") == ai_areas
    and mm.get("card_count") == computed_cards,
    "Metadata knowledge counts drift",
)
check(
    mm.get("question_count") == standard_count
    and mm.get("bellringer_count") == bellringer_count
    and mm.get("question_bank_records") == bank_count
    and mm.get("semantic_items_reviewed") == semantic_count,
    "Metadata bank counts drift",
)
check(mm.get("source_count") == sources and mm.get("domain_weight_total") == 100, "Metadata source/weight drift")

rs = release.get("scope", {})
check(release.get("project_id") == "CISSP-ATLAS" and release.get("status") == "READY_FOR_STUDY", "Release identity/state drift")
check(
    rs.get("domains") == 8
    and rs.get("numbered_objectives") == 62
    and rs.get("subtopic_checks") == subtopics
    and rs.get("ai_coverage_areas") == ai_areas
    and rs.get("layered_cards") == computed_cards
    and rs.get("standard_scenario_questions") == standard_count
    and rs.get("bellringers") == bellringer_count
    and rs.get("question_bank_records") == bank_count
    and rs.get("semantic_items_reviewed") == semantic_count
    and rs.get("sources") == sources
    and rs.get("official_weight_total_percent") == 100,
    "Release scope drift",
)
scope_dist = rs.get("released_difficulty_distribution", {})
check(
    scope_dist == {k: released_dist_total.get(k, 0) for k in ("F", "E", "S", "B")},
    "Release difficulty distribution drift",
)

expected_semantic = {
    *(f"OBJ-{o['id']}" for o in objectives),
    *(h["id"] for h in high),
    *(q["id"] for q in base_questions),
    *(q["id"] for q in released),
}
sem_items = semantic.get("items", {})
allowed = {"VERIFIED", "VERIFIED_AFTER_CORRECTION", "VERIFIED_WITH_SOURCE_SCOPE_NOTE"}
check(semantic.get("audit_date") == "2026-08-24", "Semantic audit date drift")
check(set(sem_items) == expected_semantic, f"Semantic coverage mismatch expected {len(expected_semantic)} got {len(sem_items)}")
check(len(expected_semantic) >= 300, "Semantic item count fell below v1.4 floor")
check(all(v.get("status") in allowed for v in sem_items.values()), "Semantic audit contains unreviewed status")
ss = semantic.get("scope", {})
check(
    ss.get("objective_cards") == 62
    and ss.get("high_yield_cards") == 38
    and ss.get("ai_cards") == 8
    and ss.get("precision_cards") == 32
    and ss.get("standard_questions") == standard_count
    and ss.get("bellringers") == bellringer_count
    and ss.get("total_items") == semantic_count,
    "Semantic scope drift",
)
summary = semantic.get("summary", {})
check(
    summary.get("verified", 0)
    + summary.get("verified_after_correction", 0)
    + summary.get("verified_with_source_scope_note", 0)
    == semantic_count,
    "Semantic summary count drift",
)
check(
    summary.get("answer_key_reversals") == 0
    and summary.get("material_factual_errors_remaining") == 0,
    "Semantic summary reports unresolved error",
)

# Browser shell and runtime wiring.
html = read(ROOT / "index.html")
release_label = ".".join(str(release_version).split(".")[:2])
required = ["data-meta.js"] + [f"data-d{i}.js" for i in range(1, 9)] + [
    "data-ai.js",
    "data-precision.js",
    "coverage-detail.js",
    "data-question-calibration.js",
    "bootstrap.js",
    "styles.css",
    "mobile-fix.css",
    "enhancements.css",
    'id="today"',
    'id="learn"',
    'id="practice"',
    'id="blueprint"',
    'id="progress"',
    'id="sources"',
    'id="quizDifficulty"',
    'id="startBellringer"',
    f"<option>{standard_count}</option>",
    f"RELEASE v{release_label}",
]
check(all(x in html for x in required), "HTML shell/assets/release controls incomplete")
check("Weighted mixed domains" not in html, "Misleading weighted-mix wording present")

bootstrap = read(ROOT / "bootstrap.js")
app = read(ROOT / "app.js")
enh = read(ROOT / "enhancements.js")
check(
    "RELEASED_BATCHES.json" in bootstrap
    and "CISSP_BELLRINGERS" in bootstrap
    and "import('./app.js')" in bootstrap,
    "Bootstrap release loading incomplete",
)
check("CISSP_CHUNKS.flatMap" in app and "D.cards=" in app, "App runtime assembly missing")
check(
    "startCalibratedQuiz" in enh
    and "startBellringer" in enh
    and "data-conf" in enh
    and "distractor_rationales" in enh
    and "addSubtopicSearch" in enh,
    "Enhanced practice workflow incomplete",
)
check((QB / "quality_gate.py").exists() and (QB / "QUESTION_BANK_EXPANSION_PLAN.md").exists(), "Question-bank quality system incomplete")

if errors:
    print("FAIL")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("PASS")
print(
    f"release={release_version} status=READY_FOR_STUDY domains=8 objectives=62 "
    f"subtopic_checks={subtopics} ai_areas={ai_areas} cards={computed_cards} "
    f"standard_questions={standard_count} bellringers={bellringer_count} "
    f"bank_records={bank_count} sources={sources} semantic_items={semantic_count} "
    f"released_difficulty={dict(sorted(released_dist_total.items()))} weights=100%"
)
