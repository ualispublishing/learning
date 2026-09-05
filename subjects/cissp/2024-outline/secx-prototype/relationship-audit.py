#!/usr/bin/env python3
"""Deterministic gate for reviewer-only SecX semantic relationship records."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent / "study-site"
QB = STUDY / "question-bank"
errors: list[str] = []

ALLOWED_TYPES = {
    "depends-on",
    "contrasts-with",
    "implemented-by",
    "mitigates",
    "measured-by",
    "evidenced-by",
    "practiced-by",
}
ALLOWED_STATUS = {"candidate", "rejected", "approved"}
APPROVAL_EVIDENCE = {"explicit-reviewed-statement", "manual-source-review"}
FORBIDDEN_PREFIXES = ("sub:", "source:", "study:", "due:", "coverage:", "page:", "facet:")


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


def status_verified(status: str) -> bool:
    return str(status or "").startswith("VERIFIED")


try:
    review = json.loads(read(ROOT / "RELATIONSHIP_REVIEW.json"))
    meta = parse_meta()
    chunks = [parse_chunk(f"data-d{i}.js") for i in range(1, 9)] + [parse_chunk("data-ai.js"), parse_chunk("data-precision.js")]
    manifest = json.loads(read(QB / "RELEASED_BATCHES.json"))
    base_ledger = json.loads(read(STUDY / "SEMANTIC_ITEM_AUDIT.json"))
    additions_ledger = json.loads(read(STUDY / "SEMANTIC_RELEASE_ADDITIONS.json"))
    next_html = read(ROOT / "next.html")
    runtime_text = "\n".join(read(ROOT / name) for name in (
        "index.html", "next-layer.js", "learner-registry.js", "learner-state.js",
        "due-review.js", "study-lens.js", "source-lens.js", "coverage-lens.js",
        "projection-search.js"
    ))
except (OSError, ValueError, RuntimeError) as exc:
    print("FAIL secx_relationship_audit")
    print("-", f"Parse/setup error: {exc}")
    sys.exit(1)

objectives = [o for chunk in chunks for o in chunk.get("objectives", [])]
high_cards = [c for chunk in chunks for c in chunk.get("high", [])]
base_questions = [q for chunk in chunks for q in chunk.get("questions", [])]
released_rows = []
for batch in manifest.get("released_batches", []):
    for rel in batch.get("files", []):
        path = STUDY / rel
        if path.is_file():
            released_rows.extend(read_jsonl(path))
released_standard = [q for q in released_rows if q.get("format") == "mcq"]
all_standard = base_questions + released_standard

objective_ids = {str(o.get("id")) for o in objectives}
review_card_ids = {f"OBJ-{oid}" for oid in objective_ids} | {str(c.get("id")) for c in high_cards}
scenario_ids = {str(q.get("id")) for q in all_standard}
endpoint_ids = objective_ids | review_card_ids | scenario_ids

verified_items = {}
verified_items.update(base_ledger.get("items") or {})
verified_items.update(additions_ledger.get("items") or {})

check(review.get("schema_version") == 1, "relationship review schema version must be 1")
check(review.get("scope") == "reviewer-only", "relationship registry must remain reviewer-only")
check(review.get("learner_runtime_loaded") is False, "relationship registry must declare learner_runtime_loaded=false")
check(review.get("publication_state") == "draft-only", "relationship registry must remain draft-only")
check(set(review.get("allowed_types") or []) == ALLOWED_TYPES, "relationship allowed_types drift from audited set")
relationships = review.get("relationships")
check(isinstance(relationships, list), "relationships must be a list")
relationships = relationships if isinstance(relationships, list) else []

seen_ids: set[str] = set()
seen_edges: set[tuple[str, str, str]] = set()
for idx, rel in enumerate(relationships):
    label = f"relationship[{idx}]"
    check(isinstance(rel, dict), f"{label} must be an object")
    if not isinstance(rel, dict):
        continue
    rid = str(rel.get("id") or "")
    from_id = str(rel.get("from_id") or "")
    to_id = str(rel.get("to_id") or "")
    rtype = str(rel.get("type") or "")
    status = str(rel.get("status") or "")
    release_state = str(rel.get("release_state") or "")
    evidence = rel.get("evidence") or {}
    rationale = str(rel.get("rationale") or "").strip()

    check(bool(re.fullmatch(r"REL-[A-Za-z0-9._-]+", rid)), f"{label} has invalid relationship ID {rid!r}")
    check(rid not in seen_ids, f"duplicate relationship ID: {rid}")
    seen_ids.add(rid)
    check(from_id in endpoint_ids, f"{rid or label} from_id is not a stable released endpoint: {from_id}")
    check(to_id in endpoint_ids, f"{rid or label} to_id is not a stable released endpoint: {to_id}")
    check(from_id != to_id, f"{rid or label} cannot self-link")
    check(not from_id.startswith(FORBIDDEN_PREFIXES) and not to_id.startswith(FORBIDDEN_PREFIXES), f"{rid or label} uses a temporary navigation ID")
    check(rtype in ALLOWED_TYPES, f"{rid or label} uses unsupported relationship type: {rtype}")
    check(status in ALLOWED_STATUS, f"{rid or label} uses unsupported review status: {status}")
    check(release_state == "draft", f"{rid or label} must remain release_state=draft in this prototype")
    check(bool(rationale), f"{rid or label} requires a rationale")
    edge = (from_id, to_id, rtype)
    check(edge not in seen_edges, f"duplicate relationship edge: {edge}")
    seen_edges.add(edge)

    for endpoint in (from_id, to_id):
        ledger_id = f"OBJ-{endpoint}" if endpoint in objective_ids else endpoint
        entry = verified_items.get(ledger_id) or {}
        check(status_verified(entry.get("status")), f"{rid or label} endpoint lacks verified item review: {endpoint}")

    check(isinstance(evidence, dict), f"{rid or label} evidence must be an object")
    kind = str(evidence.get("kind") or "") if isinstance(evidence, dict) else ""
    refs = evidence.get("references") if isinstance(evidence, dict) else None
    check(bool(kind), f"{rid or label} evidence.kind is required")
    check(isinstance(refs, list) and bool(refs), f"{rid or label} evidence.references must be a non-empty list")

    if status == "approved":
        check(kind in APPROVAL_EVIDENCE, f"{rid or label} approved relationship requires explicit reviewed evidence, not {kind!r}")
        check(bool(str(rel.get("reviewed_by") or "").strip()), f"{rid or label} approved relationship requires reviewed_by")
        reviewed_on = str(rel.get("reviewed_on") or "")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_on)), f"{rid or label} approved relationship requires reviewed_on YYYY-MM-DD")

check("RELATIONSHIP_REVIEW.json" not in next_html, "learner review page must not load reviewer-only relationship registry")
check("RELATIONSHIP_REVIEW.json" not in runtime_text, "learner runtime references reviewer-only relationship registry")
check("RELEASED_RELATIONSHIPS" not in runtime_text, "learner runtime unexpectedly contains an unaudited released-relationship channel")

candidate_count = sum(1 for r in relationships if isinstance(r, dict) and r.get("status") == "candidate")
approved_count = sum(1 for r in relationships if isinstance(r, dict) and r.get("status") == "approved")
rejected_count = sum(1 for r in relationships if isinstance(r, dict) and r.get("status") == "rejected")

if errors:
    print("FAIL secx_relationship_audit")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(
    "PASS secx_relationship_audit "
    f"stable_endpoints={len(endpoint_ids)} candidates={candidate_count} approved_draft={approved_count} rejected={rejected_count} "
    "learner_runtime_relationship_registry=NOT_LOADED"
)
