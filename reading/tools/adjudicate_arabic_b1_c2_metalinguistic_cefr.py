#!/usr/bin/env python3
"""Fresh, hash-bound Arabic B1-C2 metalinguistic/CEFR candidate triage.

This is intentionally conservative. It does not edit canonical content and does not
infer release readiness. It distinguishes clearly grounded contextual function
questions from items needing manual review because their cue is absent/implicit or
the answer collapses to a bare grammatical label.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
INVENTORY = READING / "audit" / "arabic_metalinguistic_cefr_candidate_inventory_2026-08-30.json"
GATE0 = READING / "audit" / "post_generation_gate0_2026-08-30.json"
OUT = READING / "audit" / "arabic_b1_c2_metalinguistic_cefr_triage_2026-08-30.json"
LEVELS = ("b1", "b2", "c1", "c2")

BARE_LABELS = {
    "اسم", "فعل", "حرف", "صفة", "ضمير", "ظرف", "مصدر",
    "أداة شرط", "حرف جر", "حرف عطف", "أداة نفي", "أداة استفهام",
    "شرط", "نفي", "استدراك", "عطف", "سبب", "نتيجة", "توكيد",
}
LABEL_PREFIX = re.compile(r"^(?:هي|هو)?\s*(?:أداة|حرف|اسم|فعل|صفة|ضمير|ظرف|مصدر)\b")
GUILLEMETS = re.compile(r"«([^»]+)»")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def tokens(text: str) -> list[str]:
    return [x for x in re.split(r"\s+", text.strip()) if x]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def marker_grounding(prompt: str, passage: str) -> dict:
    quoted = [norm(x) for x in GUILLEMETS.findall(prompt)]
    if not quoted:
        return {"quoted": [], "grounded": True, "basis": "no_quoted_marker"}
    # A quoted full sentence/context counts as grounded if exact. For a short quoted
    # connector/phrase, exact occurrence in the passage is required.
    hits = [q for q in quoted if q in passage]
    return {
        "quoted": quoted,
        "matched_quotes": hits,
        "grounded": bool(hits),
        "basis": "at_least_one_exact_quote_in_passage" if hits else "no_exact_quote_in_passage",
    }


def answer_is_bare_label(answer: str) -> bool:
    a = norm(answer).rstrip(".؛،")
    if a in BARE_LABELS:
        return True
    if len(tokens(a)) <= 3 and LABEL_PREFIX.search(a):
        return True
    return False


def main() -> int:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    gate0 = json.loads(GATE0.read_text(encoding="utf-8"))
    if gate0.get("status") != "PASS":
        raise SystemExit("Gate 0 must be PASS")
    if inventory.get("questions") != 3600 or inventory.get("needs_adjudication") != 344:
        raise SystemExit("Fresh candidate inventory drifted")

    records = {}
    bindings = {}
    for level in LEVELS:
        path = READING / "arabic" / level / "passages.jsonl"
        rel = path.relative_to(ROOT).as_posix()
        gate = gate0["canonical_files"].get(rel)
        if not gate or gate.get("sha256") != sha256(path) or gate.get("git_blob") != git_blob(path):
            raise SystemExit(f"{level}: canonical hash differs from Gate 0")
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        if len(rows) != 60:
            raise SystemExit(f"{level}: expected 60 records")
        records[level] = {r["id"]: r for r in rows}
        bindings[level] = {"path": rel, "sha256": gate["sha256"], "git_blob": gate["git_blob"]}

    results = []
    counts = Counter()
    by_level = {level: Counter() for level in LEVELS}
    candidates = [x for x in inventory["candidates"] if x.get("status") == "needs_adjudication"]
    if len(candidates) != 344:
        raise SystemExit(f"Expected 344 current candidates, found {len(candidates)}")

    for c in candidates:
        level = c["level"].lower()
        if level not in records:
            raise SystemExit(f"Unexpected level: {c['level']}")
        rec = records[level].get(c["passage_id"])
        if rec is None:
            raise SystemExit(f"Missing passage {c['passage_id']}")
        q = next((x for x in rec.get("questions", []) if x.get("id") == c["question_id"]), None)
        if q is None or q.get("prompt") != c.get("prompt") or q.get("type") != c.get("type"):
            raise SystemExit(f"Candidate drift: {c['passage_id']}/{c['question_id']}")
        a = next((x for x in rec.get("answer_key", []) if x.get("question_id") == q["id"]), None)
        if a is None:
            raise SystemExit(f"Missing answer: {c['passage_id']}/{c['question_id']}")

        prompt = q.get("prompt", "")
        answer = a.get("answer", "")
        passage = rec.get("text", "")
        grounding = marker_grounding(prompt, passage)
        reasons = []
        if "الضمنية" in prompt or "ضمني" in prompt:
            reasons.append("implicit_marker_claim_requires_manual_grounding")
        if not grounding["grounded"]:
            reasons.append("quoted_marker_or_context_not_found_in_passage")
        if answer_is_bare_label(answer):
            reasons.append("answer_is_bare_grammatical_label")
        if len(tokens(answer)) < 4:
            reasons.append("answer_too_short_for_contextual_function_explanation")

        if reasons:
            decision = "MANUAL_REVIEW"
        else:
            decision = "RETAIN_CONTEXTUAL_FUNCTION_ANALYSIS"
        counts[decision] += 1
        by_level[level][decision] += 1
        results.append({
            "level": c["level"],
            "unit": c.get("unit"),
            "sequence": c.get("sequence"),
            "passage_id": c["passage_id"],
            "question_id": c["question_id"],
            "type": q.get("type"),
            "prompt": prompt,
            "answer": answer,
            "grounding": grounding,
            "decision": decision,
            "review_reasons": reasons,
        })

    report = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "levels": ["B1", "B2", "C1", "C2"],
        "date": "2026-08-30",
        "scope": "Fresh hash-bound triage of all 344 current B1-C2 candidates from the A1-C2 metalinguistic/CEFR inventory; no canonical edits.",
        "canonical_bindings": bindings,
        "candidate_count": len(results),
        "decision_counts": dict(counts),
        "by_level": {k: dict(v) for k, v in by_level.items()},
        "manual_review_count": counts["MANUAL_REVIEW"],
        "retained_contextual_count": counts["RETAIN_CONTEXTUAL_FUNCTION_ANALYSIS"],
        "criteria": {
            "retain": "Quoted cue/context is grounded in the exact passage (when quoted), answer is not a bare grammatical label, answer has contextual explanatory substance, and prompt makes no implicit-marker claim requiring human adjudication.",
            "manual_review": "Any grounding failure, implicit-marker claim, bare grammatical-label answer, or too-short answer.",
        },
        "historical_evidence_policy": "2026-08-23 B1-C2 audits may guide review but cannot supply current approval because their corpus bindings differ from current Gate 0.",
        "results": results,
        "quality_promotion": False,
        "release_claim": False,
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
