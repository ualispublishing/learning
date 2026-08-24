#!/usr/bin/env python3
"""Quality gate for future CISSP Atlas question-bank candidates.

Usage:
  python question-bank/quality_gate.py
  python question-bank/quality_gate.py question-bank/candidates/batch-001.jsonl

With no candidate files, this validates that the current released bank can be loaded
and prints its baseline size. Candidate files are JSONL, one question/case per line.
"""
from __future__ import annotations

import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

QB = Path(__file__).resolve().parent
ROOT = QB.parent
CHUNK_FILES = [*(ROOT / f"data-d{i}.js" for i in range(1, 9)), ROOT / "data-ai.js", ROOT / "data-precision.js"]
EXACT_FAIL = 1.0
SEQ_FAIL = 0.90
SEQ_WARN = 0.82
JACCARD_FAIL = 0.72
JACCARD_WARN = 0.60
ALLOWED_TIERS = {"F", "E", "S", "B"}
TIER_RANGES = {"F": (35, 49), "E": (50, 69), "S": (70, 84), "B": (85, 100)}


def parse_chunk(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    pre, suf = "window.CISSP_CHUNKS.push(", ");"
    if not (raw.startswith(pre) and raw.endswith(suf)):
        raise ValueError(f"Invalid CISSP chunk wrapper: {path.name}")
    return json.loads(raw[len(pre):-len(suf)])


def load_current() -> tuple[list[dict], set[str], set[str]]:
    chunks = [parse_chunk(p) for p in CHUNK_FILES]
    current = sum((c.get("questions", []) for c in chunks), [])
    objectives = {o["id"] for c in chunks for o in c.get("objectives", [])}
    cover_raw = (ROOT / "coverage-detail.js").read_text(encoding="utf-8").strip()
    marker = ";\nwindow.CISSP_AI_COVERAGE="
    coverage = json.loads(cover_raw[len("window.CISSP_COVERAGE="):cover_raw.index(marker)])
    subtopics = {x for values in coverage.values() for x in values}
    return current, objectives, subtopics


def norm(text: str) -> str:
    text = text.lower().replace("’", "'")
    text = re.sub(r"\b(?:mr|ms|mrs|dr)\.?\s+[a-z]+\b", " person ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", " number ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def shingles(text: str, n: int = 3) -> set[tuple[str, ...]]:
    toks = norm(text).split()
    if len(toks) < n:
        return {tuple(toks)} if toks else set()
    return {tuple(toks[i:i+n]) for i in range(len(toks)-n+1)}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_jsonl(path: Path) -> list[dict]:
    out = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception as e:
            raise ValueError(f"{path}:{lineno}: invalid JSON: {e}") from e
        obj["_source_file"] = str(path)
        obj["_source_line"] = lineno
        out.append(obj)
    return out


def question_text(q: dict) -> str:
    if q.get("format", "mcq") == "bellringer":
        prompts = " ".join(str(x) for x in q.get("prompts", []))
        return f"{q.get('stem','')} {prompts}"
    return f"{q.get('stem','')} {' '.join(map(str, q.get('options', [])))}"


def structural_signature(q: dict) -> tuple:
    return (
        q.get("domain_primary"),
        tuple(sorted(q.get("objectives", []))),
        q.get("scenario_family"),
        q.get("decision_point"),
        q.get("correct_rule_id"),
        tuple(sorted(q.get("misconceptions", []))),
    )


def validate_candidate(q: dict, objectives: set[str], subtopics: set[str], errors: list[str], warnings: list[str]) -> None:
    qid = q.get("id", "<missing-id>")
    fmt = q.get("format", "mcq")
    required = ["id", "stem", "domain_primary", "objectives", "difficulty_tier", "difficulty_score", "scenario_family", "decision_point", "decision_verb", "correct_rule_id", "knowledge_atoms", "source_ids", "originality"]
    for k in required:
        if k not in q or q[k] in (None, "", []):
            errors.append(f"{qid}: missing required field {k}")
    if q.get("domain_primary") not in range(1, 9):
        errors.append(f"{qid}: domain_primary must be 1..8")
    bad_obj = [o for o in q.get("objectives", []) if o not in objectives]
    if bad_obj:
        errors.append(f"{qid}: unknown objective(s): {bad_obj}")
    unknown_subtopics = [s for s in q.get("subtopics", []) if s not in subtopics]
    if unknown_subtopics:
        warnings.append(f"{qid}: subtopic labels not found verbatim in coverage map: {unknown_subtopics}")
    tier = q.get("difficulty_tier")
    if tier not in ALLOWED_TIERS:
        errors.append(f"{qid}: difficulty_tier must be one of {sorted(ALLOWED_TIERS)}")
    elif isinstance(q.get("difficulty_score"), int):
        lo, hi = TIER_RANGES[tier]
        if not lo <= q["difficulty_score"] <= hi:
            errors.append(f"{qid}: difficulty_score {q['difficulty_score']} outside {tier} range {lo}-{hi}")
    else:
        errors.append(f"{qid}: difficulty_score must be an integer")
    orig = q.get("originality", {})
    if orig.get("origin") != "original-from-public-scope" or orig.get("no_external_question_seed") is not True:
        errors.append(f"{qid}: originality provenance must affirm original-from-public-scope and no external question seed")
    if fmt == "mcq":
        opts = q.get("options", [])
        if len(opts) != 4:
            errors.append(f"{qid}: MCQ must have exactly four options")
        if not isinstance(q.get("answer"), int) or not 0 <= q.get("answer", -1) < 4:
            errors.append(f"{qid}: MCQ answer index must be 0..3")
        dr = q.get("distractor_rationales", [])
        if len(dr) != 4 or any(not str(x).strip() for x in dr):
            errors.append(f"{qid}: MCQ requires four non-empty option rationales (including why the keyed option wins)")
        if tier in {"E", "S"} and len(set(norm(str(x)) for x in opts)) != 4:
            errors.append(f"{qid}: duplicate/near-identical option text")
    elif fmt == "bellringer":
        prompts = q.get("prompts", [])
        if tier != "B":
            errors.append(f"{qid}: bellringer format must use tier B")
        if not 4 <= len(prompts) <= 8:
            errors.append(f"{qid}: bellringer must contain 4..8 linked prompts")
        if len(set(q.get("domains_secondary", [])) | {q.get("domain_primary")}) < 3:
            errors.append(f"{qid}: bellringer should meaningfully span at least three domains")
        if len(q.get("knowledge_atoms", [])) < 8:
            errors.append(f"{qid}: bellringer should exercise at least eight knowledge atoms")
        if not q.get("rubric"):
            errors.append(f"{qid}: bellringer requires an explicit scoring/teaching rubric")
    else:
        errors.append(f"{qid}: unknown format {fmt}")


def main(argv: list[str]) -> int:
    current, objectives, subtopics = load_current()
    files = [Path(x) for x in argv[1:]]
    if not files:
        default_dir = QB / "candidates"
        files = sorted(default_dir.glob("*.jsonl")) if default_dir.exists() else []
    if not files:
        print(f"PASS baseline: released_questions={len(current)} candidates=0")
        return 0

    candidates = [q for f in files for q in load_jsonl(f)]
    errors: list[str] = []
    warnings: list[str] = []

    ids = [q.get("id") for q in candidates]
    if len(ids) != len(set(ids)):
        errors.append("Candidate IDs are duplicated within the batch")

    for q in candidates:
        validate_candidate(q, objectives, subtopics, errors, warnings)

    existing = [{"id": q["id"], "text": question_text(q), "struct": None} for q in current]
    accepted_so_far: list[dict] = []
    structural_seen: dict[tuple, str] = {}

    for q in candidates:
        qid = q.get("id", "<missing-id>")
        text = question_text(q)
        ntext = norm(text)
        qsh = shingles(text)
        for other in existing + accepted_so_far:
            otext = other["text"]
            onorm = norm(otext)
            if ntext == onorm:
                errors.append(f"{qid}: exact normalized duplicate of {other['id']}")
                continue
            seq = SequenceMatcher(None, ntext, onorm).ratio()
            jac = jaccard(qsh, shingles(otext))
            if seq >= SEQ_FAIL or jac >= JACCARD_FAIL:
                errors.append(f"{qid}: near-duplicate of {other['id']} (sequence={seq:.3f}, jaccard={jac:.3f})")
            elif seq >= SEQ_WARN or jac >= JACCARD_WARN:
                warnings.append(f"{qid}: similarity review vs {other['id']} (sequence={seq:.3f}, jaccard={jac:.3f})")

        sig = structural_signature(q)
        sibling = q.get("originality", {}).get("sibling_of")
        if sig in structural_seen and sibling != structural_seen[sig]:
            errors.append(f"{qid}: structural duplicate of {structural_seen[sig]} (same objective/scenario/decision/rule/misconceptions)")
        else:
            structural_seen.setdefault(sig, qid)
        accepted_so_far.append({"id": qid, "text": text, "struct": sig})

    for w in warnings:
        print("WARN", w)
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print(f"PASS released_questions={len(current)} candidates={len(candidates)} warnings={len(warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
