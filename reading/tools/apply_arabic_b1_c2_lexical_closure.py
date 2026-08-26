#!/usr/bin/env python3
import copy
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "b1": ROOT / "reading" / "arabic" / "b1" / "passages.jsonl",
    "b2": ROOT / "reading" / "arabic" / "b2" / "passages.jsonl",
    "c1": ROOT / "reading" / "arabic" / "c1" / "passages.jsonl",
    "c2": ROOT / "reading" / "arabic" / "c2" / "passages.jsonl",
}
EXPECTED = {
    "b1": "8cb5a2d31c128896e4f9a7952ad4e7aa94823c1a",
    "b2": "62beb2ff83ad0cbd23d72d8e6bfc5e2e79da54e4",
    "c1": "c91f5b194394403187e3dc0480a5eab4814e03a5",
    "c2": "b8e78e2a8dce942e87ef627a8436f1c8571f9d43",
}
ADJ = ROOT / "reading" / "audit" / "arabic_b1_c2_lexical_diagnostic_adjudication_2026-08-23.json"
REPORT = ROOT / "reading" / "audit" / "arabic_b1_c2_lexical_closure_2026-08-23.json"


def blob(path):
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def load(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def dump(path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")


def wc(text):
    return len(re.findall(r"\S+", str(text)))


def sc(text):
    return sum(str(text).count(x) for x in (".", "؟", "!", "۔"))


def q_and_a(row, qid):
    q = next((q for q in row.get("questions", []) if q.get("id") == qid), None)
    a = next((a for a in row.get("answer_key", []) if a.get("question_id") == qid), None)
    if not q or not a:
        raise RuntimeError(f"{row.get('id')} missing Q/A {qid}")
    return q, a


def set_pending(row, note):
    qm = row.setdefault("quality", {})
    qm["status"] = "draft"
    for gate in ("answer_key_check", "coverage_check", "linguistic_review", "pedagogical_review", "schema_check"):
        qm[gate] = "pending"
    notes = qm.setdefault("notes", [])
    if note not in notes:
        notes.append(note)


def main():
    actual = {level: blob(path) for level, path in FILES.items()}
    if actual != EXPECTED:
        raise SystemExit(f"Unexpected B1-C2 input blobs: {actual}")

    rows = {level: load(path) for level, path in FILES.items()}
    idx = {level: {r["id"]: r for r in level_rows} for level, level_rows in rows.items()}
    adj = json.loads(ADJ.read_text(encoding="utf-8"))

    false_reviews = [
        d for d in adj.get("decisions", [])
        if d.get("decision") == "UNRESOLVED_FALSE_RUNNING_TEXT_REVIEW"
    ]
    if len(false_reviews) != 45:
        raise RuntimeError(f"Expected 45 adjudicated false running-text reviews, found {len(false_reviews)}")

    removed = []
    for d in false_reviews:
        level = d.get("level")
        diagnostic = d.get("diagnostic", {})
        pid = diagnostic.get("passage_id")
        tid = diagnostic.get("target_id")
        form = diagnostic.get("form")
        row = idx[level].get(pid)
        if row is None:
            raise RuntimeError(f"Missing passage for false review: {level} {pid}")
        reviews = row.get("review_lexical_targets", [])
        matches = [(i, t) for i, t in enumerate(reviews) if isinstance(t, dict) and t.get("id") == tid]
        if len(matches) != 1:
            raise RuntimeError(f"{pid} {tid}: expected exactly one review target, got {len(matches)}")
        i, target = matches[0]
        if target.get("representation") != "running_text":
            raise RuntimeError(f"{pid} {tid}: expected running_text, got {target.get('representation')}")
        if form and target.get("form") != form:
            raise RuntimeError(f"{pid} {tid}: form drift {target.get('form')!r} != {form!r}")
        removed_target = reviews.pop(i)
        removed.append({"level": level, "passage_id": pid, "target_id": tid, "removed": removed_target})
        row["revision"] = int(row.get("revision") or 0) + 1
        set_pending(row, "False running-text review metadata removed 2026-08-23 after Arabic morphology-aware lexical adjudication; final advanced-level validation pending.")

    # C1 ar-r2991 أسس: natural passive/inflected realization occurs twice as أُسست/أسست; metadata said 1.
    c1 = idx["c1"]["ar-c1-u03-p05"]
    t = next((t for t in c1.get("new_lexical_targets", []) if t.get("id") == "ar-r2991"), None)
    if not t:
        raise RuntimeError("Missing C1 ar-r2991 in ar-c1-u03-p05")
    if t.get("form") != "أسس" or t.get("exposures_in_text") != 1:
        raise RuntimeError(f"Unexpected C1 ar-r2991 precondition: {t}")
    c1_text_normalized = c1.get("text", "").replace("ُ", "").replace("َ", "").replace("ِ", "").replace("ّ", "").replace("ْ", "")
    if c1_text_normalized.count("أسست") != 2:
        raise RuntimeError(f"Expected exactly two أسست realizations, found {c1_text_normalized.count('أسست')}")
    t["exposures_in_text"] = 2
    c1["revision"] = int(c1.get("revision") or 0) + 1
    set_pending(c1, "Advanced Arabic lexical exposure metadata corrected 2026-08-23: ar-r2991 أسس is realized twice as the passive/inflected surface أسست/أُسست.")

    # C2 ar-r2250 بساطة: valid possessive inflection بساطتها. No corpus mutation.
    c2_simp = idx["c2"]["ar-c2-u01-p02"]
    simp = next((t for t in c2_simp.get("new_lexical_targets", []) if t.get("id") == "ar-r2250"), None)
    if not simp or simp.get("form") != "بساطة" or simp.get("exposures_in_text") != 1:
        raise RuntimeError(f"Unexpected C2 بساطة target precondition: {simp}")
    if c2_simp.get("text", "").count("بساطتها") != 1:
        raise RuntimeError("Expected exactly one natural possessive realization بساطتها")

    # C2 ar-r1955 كيمياء: genuinely ungrounded noun target. Introduce the noun naturally and align q2.
    c2_chem = idx["c2"]["ar-c2-u03-p02"]
    chem = next((t for t in c2_chem.get("new_lexical_targets", []) if t.get("id") == "ar-r1955"), None)
    if not chem or chem.get("form") != "كيمياء" or chem.get("exposures_in_text") != 1:
        raise RuntimeError(f"Unexpected C2 كيمياء target precondition: {chem}")
    old_sentence = "اكتشف الفريق أن معايرة المصنع تفترض تركيبًا كيميائيًا مختلفًا للسائل؛ خاصية بصرية تتغير مع التركيب فتدفع الحساس إلى قراءة أعلى رغم أن الإشارة الخام مستقرة."
    new_sentence = "اكتشف الفريق أن معايرة المصنع لا تراعي كيمياء السائل الفعلية؛ فخاصية بصرية تتغير مع التركيب فتدفع الحساس إلى قراءة أعلى رغم أن الإشارة الخام مستقرة."
    if c2_chem.get("text", "").count(old_sentence) != 1:
        raise RuntimeError("C2 chemistry source sentence precondition mismatch")
    if "كيمياء" in c2_chem.get("text", ""):
        raise RuntimeError("C2 chemistry noun unexpectedly already present before repair")
    c2_chem["text"] = c2_chem["text"].replace(old_sentence, new_sentence, 1)
    q2, a2 = q_and_a(c2_chem, "q2")
    if q2.get("prompt") != "ما سبب الانحياز؟":
        raise RuntimeError(f"Unexpected C2 chemistry q2 prompt: {q2.get('prompt')}")
    old_answer = "معايرة تفترض تركيبًا كيميائيًا مختلفًا يؤثر في الإشارة البصرية."
    new_answer = "المعايرة لا تراعي كيمياء السائل الفعلية، فينشأ انحياز في الإشارة البصرية."
    if a2.get("answer") != old_answer:
        raise RuntimeError(f"Unexpected C2 chemistry q2 answer: {a2.get('answer')}")
    a2["answer"] = new_answer
    if c2_chem["text"].count("كيمياء") != 1:
        raise RuntimeError(f"Expected exactly one كيمياء after repair, found {c2_chem['text'].count('كيمياء')}")
    c2_chem["word_count"] = wc(c2_chem["text"])
    c2_chem["sentence_count"] = sc(c2_chem["text"])
    c2_chem["revision"] = int(c2_chem.get("revision") or 0) + 1
    set_pending(c2_chem, "Advanced Arabic lexical grounding repaired 2026-08-23: noun target كيمياء is now naturally realized in the passage and q2 is aligned to the repaired causal statement.")

    # Ensure every target removed from running_text is now absent as such, but preserve other review representations.
    for entry in removed:
        row = idx[entry["level"]][entry["passage_id"]]
        lingering = [t for t in row.get("review_lexical_targets", []) if t.get("id") == entry["target_id"] and t.get("representation") == "running_text"]
        if lingering:
            raise RuntimeError(f"Lingering false running_text review: {entry}")

    for level, path in FILES.items():
        dump(path, rows[level])

    outputs = {level: blob(path) for level, path in FILES.items()}
    report = {
        "schema_version": 1,
        "date": "2026-08-23",
        "scope": "Arabic B1-C2 lexical closure after semantic remainder repair",
        "input_blobs": actual,
        "output_blobs": outputs,
        "source_lexical_adjudication": {
            "source_diagnostics": adj.get("source_diagnostics"),
            "resolved_count": adj.get("resolved_count"),
            "unresolved_count_before_closure": adj.get("unresolved_count"),
        },
        "removed_false_running_text_reviews_count": len(removed),
        "removed_false_running_text_reviews": removed,
        "new_target_repairs": [
            {"passage_id": "ar-c1-u03-p05", "target_id": "ar-r2991", "action": "exposures_in_text 1 -> 2", "evidence": "two passive/inflected أسست/أُسست realizations"},
            {"passage_id": "ar-c2-u01-p02", "target_id": "ar-r2250", "action": "no corpus change", "evidence": "بساطة is naturally realized once as possessive بساطتها"},
            {"passage_id": "ar-c2-u03-p02", "target_id": "ar-r1955", "action": "natural noun realization added and q2 aligned", "evidence": "كيمياء now occurs exactly once in passage text"},
        ],
        "quality_promotion": False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "removed_false_reviews": len(removed),
        "output_blobs": outputs,
        "c1_ar_r2991_exposures": t.get("exposures_in_text"),
        "c2_ar_r2250_surface": "بساطتها",
        "c2_ar_r1955_occurrences": c2_chem["text"].count("كيمياء"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
