import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
OUT = ROOT / "reading" / "audit" / "arabic_a1_u01_metalinguistic_postrepair_2026-08-20.json"
EXPECTED_SHA256 = "2eaaed7b175282e5c201d552730bcb75b838f4264c4abee73031052953cc5aea"
FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}
PATTERNS = [
    ("explicit_grammar_classification", re.compile(r"التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+كلمة|ما\s+نوع\s+«")),
    ("explicit_grammar_function", re.compile(r"الوظيفة\s+النحوية|ما\s+وظيفة\s+كلمة|ما\s+وظيفة\s+«|ما\s+الدور\s+النحوي")),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    bound = sha256(PATH)
    if bound != EXPECTED_SHA256:
        raise SystemExit(f"postrepair hash drift: expected {EXPECTED_SHA256}, got {bound}")
    rows = [json.loads(x) for x in PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    unit = [p for p in rows if p.get("unit") == 1]
    if len(unit) != 6 or [p.get("sequence") for p in unit] != list(range(1, 7)):
        raise SystemExit("Unit 01 scope/sequence regression")

    findings = []
    duplicate_prompts = []
    type_counts = Counter()
    for p in unit:
        qs = p.get("questions", [])
        ans = p.get("answer_key", [])
        if len(qs) != 10 or len(ans) != 10:
            findings.append({"passage_id": p["id"], "kind": "question_answer_cardinality"})
        qids = {q.get("id") for q in qs}
        if {a.get("question_id") for a in ans} != qids:
            findings.append({"passage_id": p["id"], "kind": "answer_linkage"})
        seen = {}
        for q in qs:
            qtype = q.get("type")
            type_counts[qtype] += 1
            prompt = (q.get("prompt") or "").strip()
            if qtype in FORMAL_TYPES:
                findings.append({"passage_id": p["id"], "question_id": q.get("id"), "kind": "formal_question_type", "type": qtype, "prompt": prompt})
            for name, pat in PATTERNS:
                if pat.search(prompt):
                    findings.append({"passage_id": p["id"], "question_id": q.get("id"), "kind": name, "type": qtype, "prompt": prompt})
            key = re.sub(r"\s+", " ", prompt)
            if key in seen:
                duplicate_prompts.append({"passage_id": p["id"], "question_ids": [seen[key], q.get("id")], "prompt": prompt})
            else:
                seen[key] = q.get("id")

    out = {
        "schema_version": 1,
        "date": "2026-08-20",
        "language": "ar",
        "level": "A1",
        "unit": 1,
        "bound_sha256": bound,
        "scope": {"records": len(unit), "questions": sum(len(p.get("questions", [])) for p in unit), "answers": sum(len(p.get("answer_key", [])) for p in unit)},
        "formal_metalinguistic_finding_count": len(findings),
        "findings": findings,
        "exact_duplicate_prompt_count": len(duplicate_prompts),
        "duplicate_prompts": duplicate_prompts,
        "question_type_counts": dict(type_counts),
        "status": "PASS_DETERMINISTIC_UNIT01" if not findings and not duplicate_prompts else "FAIL",
        "limitations": "Deterministic/self-review evidence only. This does not satisfy independent native or educator semantic review.",
        "release_effect": "Arabic remains educator-blocked."
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "findings": len(findings), "duplicates": len(duplicate_prompts)}, ensure_ascii=False, indent=2))
    if out["status"] != "PASS_DETERMINISTIC_UNIT01":
        raise SystemExit("Unit 01 deterministic postrepair audit failed")


if __name__ == "__main__":
    main()
