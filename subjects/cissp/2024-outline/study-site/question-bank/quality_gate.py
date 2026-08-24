#!/usr/bin/env python3
"""CISSP Atlas question-bank quality/originality gate.

Default validates the immutable released corpus plus every unreleased candidate.
Use --released-only for deployment of an already-audited release: candidate drafts
are ignored, but the complete released bank still receives structural/originality checks.

Candidate batches of 16+ records are checked independently so a strong combined
candidate pool cannot hide a weak individual batch.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

QB = Path(__file__).resolve().parent
ROOT = QB.parent
CHUNK_FILES = [
    *(ROOT / f"data-d{i}.js" for i in range(1, 9)),
    ROOT / "data-ai.js",
    ROOT / "data-precision.js",
]

SEQ_FAIL, SEQ_WARN = .90, .82
JACCARD_FAIL, JACCARD_WARN = .72, .60
ALLOWED_TIERS = {"F", "E", "S", "B"}
TIER_RANGES = {"F": (35, 49), "E": (50, 69), "S": (70, 84), "B": (85, 100)}
REVIEW_PREFIX = "SEMANTIC_REVIEWED_"
MIN_BATCH_FOR_MIX_RULES = 16
MIN_EXAM_CALIBRATED_SHARE = .50
MAX_BELLRINGER_SHARE = .10
MAX_PRIMARY_DOMAIN_SHARE = .35


def parse_chunk(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    pre, suf = "window.CISSP_CHUNKS.push(", ");"
    if not (raw.startswith(pre) and raw.endswith(suf)):
        raise ValueError(f"Invalid CISSP chunk wrapper: {path.name}")
    return json.loads(raw[len(pre):-len(suf)])


def load_jsonl(path: Path) -> list[dict]:
    out = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
        obj["_source_file"] = str(path)
        obj["_source_line"] = lineno
        out.append(obj)
    return out


def load_meta() -> dict:
    raw = (ROOT / "data-meta.js").read_text(encoding="utf-8").strip()
    end = raw.index(";window.CISSP_CHUNKS=[];")
    return json.loads(raw[len("window.CISSP_META="):end])


def load_scope():
    chunks = [parse_chunk(p) for p in CHUNK_FILES]
    base = sum((c.get("questions", []) for c in chunks), [])
    objectives = {o["id"] for c in chunks for o in c.get("objectives", [])}
    raw = (ROOT / "coverage-detail.js").read_text(encoding="utf-8").strip()
    marker = ";\nwindow.CISSP_AI_COVERAGE="
    coverage = json.loads(raw[len("window.CISSP_COVERAGE="):raw.index(marker)])
    meta = load_meta()
    subtopics = {x for values in coverage.values() for x in values}
    return base, objectives, subtopics, set(meta["sources"]), meta


def released_manifest() -> dict:
    path = QB / "RELEASED_BATCHES.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"released_batches": []}


def released_records():
    manifest = released_manifest()
    records, paths = [], []
    for batch in manifest.get("released_batches", []):
        for rel in batch.get("files", []):
            path = ROOT / rel
            paths.append(path.resolve())
            records.extend(load_jsonl(path))
    return records, set(paths), manifest


def norm(text: str) -> str:
    text = text.lower().replace("’", "'")
    text = re.sub(r"\b(?:mr|ms|mrs|dr)\.?\s+[a-z]+\b", " person ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", " number ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def shingles(text: str, n: int = 3):
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


def question_text(q: dict) -> str:
    if q.get("format", "mcq") == "bellringer":
        return f"{q.get('stem', '')} {' '.join(map(str, q.get('prompts', [])))}"
    return f"{q.get('stem', '')} {' '.join(map(str, q.get('options', [])))}"


def structural_signature(q: dict):
    return (
        q.get("domain_primary"),
        tuple(sorted(q.get("objectives", []))),
        q.get("scenario_family"),
        q.get("decision_point"),
        q.get("correct_rule_id"),
        tuple(sorted(q.get("misconceptions", []))),
    )


def validate_record(q, objectives, subtopics, sources, errors):
    qid = q.get("id", "<missing-id>")
    fmt = q.get("format", "mcq")
    required = [
        "id", "format", "stem", "domain_primary", "domains_secondary", "objectives",
        "subtopics", "difficulty_tier", "difficulty_score", "scenario_family",
        "decision_point", "decision_verb", "correct_rule_id", "knowledge_atoms",
        "misconceptions", "source_ids", "originality", "review_status",
    ]
    for key in required:
        if key not in q or q[key] in (None, ""):
            errors.append(f"{qid}: missing required field {key}")

    if not isinstance(q.get("objectives"), list) or not q.get("objectives"):
        errors.append(f"{qid}: objectives must be non-empty list")
    if not isinstance(q.get("knowledge_atoms"), list) or not q.get("knowledge_atoms"):
        errors.append(f"{qid}: knowledge_atoms must be non-empty list")
    if q.get("domain_primary") not in range(1, 9):
        errors.append(f"{qid}: domain_primary must be 1..8")

    bad = [o for o in q.get("objectives", []) if o not in objectives]
    if bad:
        errors.append(f"{qid}: unknown objective(s): {bad}")
    bad = [s for s in q.get("subtopics", []) if s not in subtopics]
    if bad:
        errors.append(f"{qid}: unknown subtopic label(s): {bad}")
    bad = [s for s in q.get("source_ids", []) if s not in sources]
    if bad:
        errors.append(f"{qid}: unknown source ID(s): {bad}")

    if not str(q.get("review_status", "")).startswith(REVIEW_PREFIX):
        errors.append(f"{qid}: missing semantic-review status")

    tier, score = q.get("difficulty_tier"), q.get("difficulty_score")
    if tier not in ALLOWED_TIERS:
        errors.append(f"{qid}: invalid difficulty tier")
    elif not isinstance(score, int) or not TIER_RANGES[tier][0] <= score <= TIER_RANGES[tier][1]:
        errors.append(f"{qid}: difficulty score outside {tier} range")

    orig = q.get("originality", {})
    if orig.get("origin") != "original-from-public-scope" or orig.get("no_external_question_seed") is not True:
        errors.append(f"{qid}: invalid originality provenance")
    if "sibling_of" not in orig:
        errors.append(f"{qid}: originality.sibling_of must be explicit")

    if fmt == "mcq":
        if len(q.get("options", [])) != 4:
            errors.append(f"{qid}: MCQ must have four options")
        if not isinstance(q.get("answer"), int) or not 0 <= q.get("answer", -1) < 4:
            errors.append(f"{qid}: answer index must be 0..3")
        rats = q.get("distractor_rationales", [])
        if len(rats) != 4 or any(not str(x).strip() for x in rats):
            errors.append(f"{qid}: four option rationales required")
        if not str(q.get("explanation", "")).strip():
            errors.append(f"{qid}: explanation required")
        if tier in {"E", "S"} and len({norm(str(x)) for x in q.get("options", [])}) != 4:
            errors.append(f"{qid}: duplicate option text")
    elif fmt == "bellringer":
        prompts = q.get("prompts", [])
        if tier != "B":
            errors.append(f"{qid}: Bellringer must use B tier")
        if not 4 <= len(prompts) <= 8:
            errors.append(f"{qid}: Bellringer must have 4..8 prompts")
        if len(set(q.get("domains_secondary", [])) | {q.get("domain_primary")}) < 3:
            errors.append(f"{qid}: Bellringer must span at least three domains")
        if len(q.get("knowledge_atoms", [])) < 8:
            errors.append(f"{qid}: Bellringer requires >=8 knowledge atoms")
        if not q.get("rubric"):
            errors.append(f"{qid}: Bellringer rubric required")
    else:
        errors.append(f"{qid}: unknown format {fmt}")


def validate_batch_mix(path: Path, batch: list[dict], errors):
    if len(batch) < MIN_BATCH_FOR_MIX_RULES:
        return
    dist = Counter(q.get("difficulty_tier") for q in batch)
    if dist["E"] < len(batch) * MIN_EXAM_CALIBRATED_SHARE:
        errors.append(f"{path.name}: Exam-calibrated items must be >=50% of the batch")
    if dist["B"] > len(batch) * MAX_BELLRINGER_SHARE:
        errors.append(f"{path.name}: Bellringers exceed 10% of the batch")

    standard = [q for q in batch if q.get("format", "mcq") == "mcq"]
    if standard:
        domains = Counter(q.get("domain_primary") for q in standard)
        domain, count = max(domains.items(), key=lambda x: x[1])
        if count / len(standard) > MAX_PRIMARY_DOMAIN_SHARE:
            errors.append(
                f"{path.name}: D{domain} is {count}/{len(standard)} primary-domain items "
                f"({count/len(standard):.1%}); max allowed is {MAX_PRIMARY_DOMAIN_SHARE:.0%}"
            )


def similarity_check(records, against, errors, warnings, structural=True):
    seen = {}
    against = list(against)
    for q in records:
        qid = q.get("id", "<missing-id>")
        text = question_text(q)
        ntext = norm(text)
        qsh = shingles(text)
        for other in against:
            if other.get("id") == qid:
                continue
            otext = question_text(other)
            onorm = norm(otext)
            if ntext == onorm:
                errors.append(f"{qid}: exact normalized duplicate of {other.get('id')}")
                continue
            seq = SequenceMatcher(None, ntext, onorm).ratio()
            jac = jaccard(qsh, shingles(otext))
            if seq >= SEQ_FAIL or jac >= JACCARD_FAIL:
                errors.append(
                    f"{qid}: near-duplicate of {other.get('id')} "
                    f"(sequence={seq:.3f}, jaccard={jac:.3f})"
                )
            elif seq >= SEQ_WARN or jac >= JACCARD_WARN:
                warnings.append(
                    f"{qid}: similarity review vs {other.get('id')} "
                    f"(sequence={seq:.3f}, jaccard={jac:.3f})"
                )

        if structural:
            sig = structural_signature(q)
            sibling = q.get("originality", {}).get("sibling_of")
            if sig in seen and sibling != seen[sig]:
                errors.append(f"{qid}: structural duplicate of {seen[sig]}")
            else:
                seen.setdefault(sig, qid)
        against.append(q)


def main(argv: list[str]) -> int:
    released_only = "--released-only" in argv[1:]
    file_args = [x for x in argv[1:] if x != "--released-only"]

    base, objectives, subtopics, sources, meta = load_scope()
    released, released_paths, manifest = released_records()
    errors, warnings = [], []

    for q in released:
        validate_record(q, objectives, subtopics, sources, errors)

    if len({q.get("id") for q in released}) != len(released):
        errors.append("Released batch IDs are duplicated")
    base_ids = {q["id"] for q in base}
    if any(q.get("id") in base_ids for q in released):
        errors.append("Released batch ID collides with base bank")

    similarity_check(
        released,
        [{"id": q["id"], "format": "mcq", "stem": q["stem"], "options": q["options"]} for q in base],
        errors,
        warnings,
    )

    std = [q for q in released if q.get("format") == "mcq"]
    bells = [q for q in released if q.get("format") == "bellringer"]
    if len(base) + len(std) != meta["meta"].get("question_count"):
        errors.append("Metadata standard-question count drift")
    if len(bells) != meta["meta"].get("bellringer_count"):
        errors.append("Metadata Bellringer count drift")
    if len(base) + len(released) != meta["meta"].get("question_bank_records"):
        errors.append("Metadata bank-record count drift")

    for batch_meta in manifest.get("released_batches", []):
        batch = []
        for rel in batch_meta.get("files", []):
            batch.extend(load_jsonl(ROOT / rel))
        dist = Counter(q.get("difficulty_tier") for q in batch)
        if (
            len(batch) != batch_meta.get("records")
            or sum(q.get("format") == "mcq" for q in batch) != batch_meta.get("standard_mcq")
            or sum(q.get("format") == "bellringer" for q in batch) != batch_meta.get("bellringers")
        ):
            errors.append(f"{batch_meta.get('batch_id')}: release count drift")
        if {k: dist.get(k, 0) for k in ("F", "E", "S", "B")} != batch_meta.get("difficulty"):
            errors.append(f"{batch_meta.get('batch_id')}: difficulty distribution drift")

    candidates = []
    if not released_only:
        if file_args:
            files = [Path(x).resolve() for x in file_args]
        else:
            candidate_dir = QB / "candidates"
            files = [
                p.resolve()
                for p in sorted(candidate_dir.glob("*.jsonl"))
                if p.resolve() not in released_paths
            ] if candidate_dir.exists() else []

        file_batches = [(path, load_jsonl(path)) for path in files]
        for path, batch in file_batches:
            validate_batch_mix(path, batch, errors)
        candidates = [q for _, batch in file_batches for q in batch]

        if len({q.get("id") for q in candidates}) != len(candidates):
            errors.append("Candidate IDs duplicated within candidate set")
        current_ids = base_ids | {q.get("id") for q in released}
        if any(q.get("id") in current_ids for q in candidates):
            errors.append("Candidate ID collides with released bank")
        for q in candidates:
            validate_record(q, objectives, subtopics, sources, errors)

        similarity_check(candidates, base + released, errors, warnings)

    for warning in warnings:
        print("WARN", warning)
    if errors:
        for error in errors:
            print("FAIL", error)
        return 1

    dist = Counter(q.get("difficulty_tier") for q in candidates)
    mode = "released-only" if released_only else "released+candidate"
    print(
        f"PASS mode={mode} released_mcq={len(base)+len(std)} "
        f"released_bellringers={len(bells)} candidates={len(candidates)} "
        f"F={dist['F']} E={dist['E']} S={dist['S']} B={dist['B']} "
        f"warnings={len(warnings)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
