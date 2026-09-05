#!/usr/bin/env python3
"""Deterministic preflight for assumptions used by the SecX expanded browser smoke."""
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


def parse_meta() -> dict:
    text = read(STUDY / "data-meta.js")
    prefix = "window.CISSP_META="
    marker = ";window.CISSP_CHUNKS=[];"
    if not text.startswith(prefix) or marker not in text:
        raise RuntimeError("Unexpected data-meta.js wrapper")
    return json.loads(text[len(prefix):text.index(marker)])


def parse_chunk(name: str) -> dict:
    text = read(STUDY / name)
    prefix = "window.CISSP_CHUNKS.push("
    suffix = ");"
    if not text.startswith(prefix) or not text.endswith(suffix):
        raise RuntimeError(f"Unexpected {name} wrapper")
    return json.loads(text[len(prefix):-len(suffix)])


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{path.relative_to(STUDY)}:{line_no}: {exc}") from exc
    return rows


def q_objectives(q: dict) -> list[str]:
    values = q.get("objectives")
    if isinstance(values, list):
        return [str(x) for x in values if str(x)]
    value = q.get("objective")
    return [str(value)] if value else []


try:
    meta = parse_meta()
    chunks = [parse_chunk(f"data-d{i}.js") for i in range(1, 9)] + [
        parse_chunk("data-ai.js"),
        parse_chunk("data-precision.js"),
    ]
    manifest = json.loads(read(QB / "RELEASED_BATCHES.json"))
    smoke = read(ROOT / "browser-smoke.html")
except (OSError, ValueError, RuntimeError) as exc:
    print("FAIL secx_browser_fixtures_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

meta_info = meta.get("meta", {})
domains = meta.get("domains") or []
objectives = [o for chunk in chunks for o in chunk.get("objectives", [])]
high_cards = [c for chunk in chunks for c in chunk.get("high", [])]
base_questions = [q for chunk in chunks for q in chunk.get("questions", [])]
objective_by_id = {str(o.get("id")): o for o in objectives}
objective_ids = set(objective_by_id)

released_rows: list[dict] = []
seen_files: set[str] = set()
try:
    for batch in manifest.get("released_batches", []):
        for rel in batch.get("files", []):
            check(rel not in seen_files, f"release manifest repeats file {rel}")
            seen_files.add(rel)
            path = STUDY / rel
            check(path.is_file(), f"released file missing: {rel}")
            if path.is_file():
                released_rows.extend(read_jsonl(path))
except (OSError, RuntimeError) as exc:
    print("FAIL secx_browser_fixtures_audit")
    print("-", f"Released-bank parse error: {exc}")
    sys.exit(1)

released_standard = [q for q in released_rows if q.get("format") == "mcq"]
runtime_questions = [*base_questions, *released_standard]

# The browser smoke enters D1, opens objective 1.9, then chooses the first
# high-yield card and first runtime scenario mapped there. Mirror those exact
# runtime-order assumptions so drift fails before Chromium starts.
o19 = objective_by_id.get("1.9")
check(o19 is not None, "browser fixture objective 1.9 is missing")
if o19:
    check(o19.get("domain_num") == 1, "objective 1.9 is no longer in D1")
    check(bool(str(o19.get("label") or "").strip()), "objective 1.9 label is empty")

d1 = next((d for d in domains if d.get("num") == 1), None)
check(len(domains) == 8, f"browser root assumption drift: expected 8 domains, found {len(domains)}")
check(d1 is not None, "D1 metadata is missing")
if d1:
    check(d1.get("name") == "Security and Risk Management", "D1 title no longer matches browser breadcrumb fixture")
    max_weight = max((d.get("weight", 0) for d in domains), default=0)
    max_weight_domains = [d.get("num") for d in domains if d.get("weight", 0) == max_weight]
    check(d1.get("weight") == max_weight, "D1 is no longer the highest-weight zero-score tie-break domain")
    check(max_weight_domains == [1], f"D1 is no longer the unique highest-weight tie-break domain: {max_weight_domains}")

cards_19 = [c for c in high_cards if str(c.get("objective")) == "1.9"]
check(bool(cards_19), "objective 1.9 has no high-yield retrieval card for the browser card branch")
first_card = cards_19[0] if cards_19 else None
if first_card:
    check(bool(str(first_card.get("id") or "").strip()), "first objective 1.9 card has no stable ID")
    check(bool(str(first_card.get("front") or "").strip()), "first objective 1.9 card has no retrieval prompt")

scenarios_19 = [q for q in runtime_questions if "1.9" in q_objectives(q)]
check(bool(scenarios_19), "objective 1.9 has no runtime released scenario for the browser scenario branch")
first_scenario = scenarios_19[0] if scenarios_19 else None
if first_scenario:
    options = first_scenario.get("options") or []
    answer = first_scenario.get("answer")
    check(bool(str(first_scenario.get("id") or "").strip()), "first objective 1.9 scenario has no stable ID")
    check(bool(str(first_scenario.get("stem") or "").strip()), "first objective 1.9 scenario has no stem")
    check(isinstance(options, list) and len(options) >= 2, "first objective 1.9 scenario lacks browser-testable options")
    check(isinstance(answer, int) and 0 <= answer < len(options), "first objective 1.9 scenario lacks a valid keyed answer")

# Search smoke relies on C-472 being in the same released runtime registry and
# on its first explicit objective being routable by scenarioLayout().
c472_matches = [q for q in runtime_questions if str(q.get("id")) == "C-472"]
check(len(c472_matches) == 1, f"expected exactly one runtime scenario C-472, found {len(c472_matches)}")
c472 = c472_matches[0] if len(c472_matches) == 1 else None
c472_objectives = q_objectives(c472) if c472 else []
if c472:
    check(bool(c472_objectives), "C-472 has no explicit objective for search routing")
    check(all(oid in objective_ids for oid in c472_objectives), f"C-472 references unknown objective(s): {c472_objectives}")
    check(c472_objectives[0] in objective_ids, "C-472 first objective is not routable by scenario search")

objective_card_ids = [f"OBJ-{o.get('id')}" for o in objectives]
high_card_ids = [str(c.get("id")) for c in high_cards]
registry_ids = [*objective_card_ids, *high_card_ids]
check(len(runtime_questions) == meta_info.get("question_count"), f"runtime standard-question count drift: {len(runtime_questions)} != {meta_info.get('question_count')}")
check(len(registry_ids) == meta_info.get("card_count"), f"layered review registry count drift: {len(registry_ids)} != {meta_info.get('card_count')}")
check(len(registry_ids) == len(set(registry_ids)), "layered review registry IDs are not unique")

smoke_tokens = [
    "'1.9'",
    "'facet:1.9:cards'",
    "'facet:1.9:scenarios'",
    "'C-472'",
    "'study:weak'",
    "reviewCardCount===meta.card_count",
]
for token in smoke_tokens:
    check(token in smoke, f"browser smoke fixture contract changed without updating preflight: missing {token}")

if errors:
    print("FAIL secx_browser_fixtures_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(
    "PASS secx_browser_fixtures_audit "
    f"objective=1.9 domain=D1 "
    f"high_cards_1.9={len(cards_19)} first_card={first_card.get('id') if first_card else 'none'} "
    f"scenarios_1.9={len(scenarios_19)} first_scenario={first_scenario.get('id') if first_scenario else 'none'} "
    f"search=C-472 objective={c472_objectives[0] if c472_objectives else 'none'} "
    f"review_registry={len(registry_ids)} runtime_questions={len(runtime_questions)} weak_tie=D1"
)
