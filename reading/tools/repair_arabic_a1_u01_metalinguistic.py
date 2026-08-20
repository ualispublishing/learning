import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
REPORT = ROOT / "reading" / "audit" / "arabic_a1_u01_metalinguistic_repair_2026-08-20.json"
EXPECTED_BEFORE_SHA256 = "d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b"

# Bounded educator-policy repair for A1 Unit 01 only. Each replacement converts
# formal grammatical-label recall into operational form/use assessment while
# preserving the intended grammar or lexical target.
REPAIRS = {
    ("ar-a1-u01-p01", "q6"): {
        "old_prompt": "ما التصنيف النحوي الأدق لـ«هنا» في الاستعمال المكاني؟",
        "old_type": "grammar_category",
        "old_answer": "اسم إشارة للمكان القريب.",
        "prompt": "أنت واقف بجانب الباب. أي جملة أنسب: «الباب هنا» أم «الباب هناك»؟",
        "type": "grammar_choice",
        "answer": "الباب هنا.",
        "explanation": "«هنا» تستعمل للمكان القريب من المتكلم.",
    },
    ("ar-a1-u01-p02", "q7"): {
        "old_prompt": "ما وظيفة «بعد» في «بعد قليل»؟",
        "old_type": "grammar_category",
        "old_answer": "ظرف زمان يدل على وقت لاحق.",
        "prompt": "إذا كانت المدرسة لاحقًا، أي جملة صحيحة: «نذهب إلى المدرسة بعد قليل» أم «نذهب إلى المدرسة قبل قليل»؟",
        "type": "grammar_choice",
        "answer": "نذهب إلى المدرسة بعد قليل.",
        "explanation": "«بعد قليل» تدل على وقت لاحق.",
    },
    ("ar-a1-u01-p02", "q9"): {
        "old_prompt": "ما الكلمة التي تنفي الفعل في «لم تأخذ كل الكتب»؟",
        "old_type": "grammar_identification",
        "old_answer": "لم.",
        "prompt": "اختر الجملة الصحيحة لنفي فعل في الماضي: «لم تأخذ ليلى كل الكتب» أم «لا أخذت ليلى كل الكتب»؟",
        "type": "grammar_choice",
        "answer": "لم تأخذ ليلى كل الكتب.",
        "explanation": "«لم» مع الفعل المضارع تستعمل هنا لنفي حدث في الماضي.",
    },
    ("ar-a1-u01-p03", "q6"): {
        "old_prompt": "ما التصنيف النحوي الأدق لـ«هناك» في الاستعمال المكاني؟",
        "old_type": "grammar_category",
        "old_answer": "اسم إشارة للمكان البعيد.",
        "prompt": "إذا كانت الحديقة بعيدة عن المتكلم، أي جملة أنسب: «الحديقة هناك» أم «الحديقة هنا»؟",
        "type": "grammar_choice",
        "answer": "الحديقة هناك.",
        "explanation": "«هناك» تستعمل للمكان البعيد عن المتكلم.",
    },
    ("ar-a1-u01-p03", "q10"): {
        "old_prompt": "في «أريد»، من صاحب الفعل؟",
        "old_type": "person_form",
        "old_answer": "المتكلم المفرد: أنا.",
        "prompt": "أكمل عن نفسك: «أنا _____ أن أذهب إلى الحديقة.»",
        "type": "cloze_transfer",
        "answer": "أريد.",
        "explanation": "مع «أنا» نقول «أريد».",
        "target_ids": ["ar-r33"],
    },
    ("ar-a1-u01-p05", "q7"): {
        "old_prompt": "ماذا تدل «حتى» في «حتى المساء»؟",
        "old_type": "grammar_function",
        "old_answer": "تدل على الغاية أو نهاية المدة.",
        "prompt": "إذا كان البقاء ينتهي عند المساء، أي جملة أنسب: «بقيت في المكتبة حتى المساء» أم «بقيت في المكتبة بعد المساء»؟",
        "type": "grammar_choice",
        "answer": "بقيت في المكتبة حتى المساء.",
        "explanation": "«حتى المساء» تبين أن مدة البقاء تنتهي عند المساء.",
    },
    ("ar-a1-u01-p05", "q9"): {
        "old_prompt": "ما صيغة العدد في كلمة «كتابين»؟",
        "old_type": "grammar_identification",
        "old_answer": "المثنى.",
        "prompt": "اختر الصحيح في هذه الجملة: «أخذت ليلى كتابين» أم «أخذت ليلى كتابان»؟",
        "type": "grammar_choice",
        "answer": "أخذت ليلى كتابين.",
        "explanation": "بعد الفعل «أخذت» هنا تأتي الصيغة «كتابين».",
    },
    ("ar-a1-u01-p06", "q8"): {
        "old_prompt": "في «حتى المساء»، ماذا تحدد «حتى»؟",
        "old_type": "grammar_function",
        "old_answer": "نهاية المدة الزمنية.",
        "prompt": "إذا انتهت القراءة عند المساء، أي جملة أنسب: «قرأت ليلى حتى المساء» أم «قرأت ليلى بعد المساء»؟",
        "type": "grammar_choice",
        "answer": "قرأت ليلى حتى المساء.",
        "explanation": "«حتى المساء» تبين أن القراءة استمرت إلى المساء ثم انتهت عنده.",
    },
    ("ar-a1-u01-p06", "q10"): {
        "old_prompt": "ما وظيفة «أو» في «كتابًا واحدًا أو اثنين»؟",
        "old_type": "grammar_function",
        "old_answer": "حرف عطف يربط بين بديلين أو احتمالين.",
        "prompt": "عندما يكون أمامك خياران، أي جملة أنسب: «أقرأ كتابًا واحدًا أو اثنين» أم «أقرأ كتابًا واحدًا واثنين»؟",
        "type": "grammar_choice",
        "answer": "أقرأ كتابًا واحدًا أو اثنين.",
        "explanation": "«أو» تستعمل هنا للاختيار بين بديلين.",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before_hash = sha256(PATH)
    if before_hash != EXPECTED_BEFORE_SHA256:
        raise SystemExit(f"canonical hash drift: expected {EXPECTED_BEFORE_SHA256}, got {before_hash}")

    rows = [json.loads(x) for x in PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("A1 structural precondition failed")

    applied = []
    seen = set()
    for p in rows:
        pid = p["id"]
        answers = {a["question_id"]: a for a in p.get("answer_key", [])}
        changed_here = 0
        for q in p.get("questions", []):
            key = (pid, q.get("id"))
            spec = REPAIRS.get(key)
            if not spec:
                continue
            a = answers.get(q["id"])
            if a is None:
                raise SystemExit(f"missing answer for {key}")
            if q.get("prompt") != spec["old_prompt"] or q.get("type") != spec["old_type"] or a.get("answer") != spec["old_answer"]:
                raise SystemExit(f"repair precondition mismatch for {key}")

            before = {
                "prompt": q.get("prompt"),
                "type": q.get("type"),
                "target_ids": q.get("target_ids"),
                "answer": a.get("answer"),
                "explanation": a.get("explanation"),
            }
            q["prompt"] = spec["prompt"]
            q["type"] = spec["type"]
            if "target_ids" in spec:
                q["target_ids"] = spec["target_ids"]
            a["answer"] = spec["answer"]
            a["explanation"] = spec["explanation"]
            after = {
                "prompt": q.get("prompt"),
                "type": q.get("type"),
                "target_ids": q.get("target_ids"),
                "answer": a.get("answer"),
                "explanation": a.get("explanation"),
            }
            applied.append({"passage_id": pid, "question_id": q["id"], "before": before, "after": after})
            seen.add(key)
            changed_here += 1
        if changed_here:
            p["revision"] = int(p.get("revision", 0)) + 1

    missing = sorted(set(REPAIRS) - seen)
    if missing or len(applied) != 9:
        raise SystemExit(f"repair coverage mismatch: missing={missing}, applied={len(applied)}")

    # Fail closed on structural drift.
    for p in rows:
        qs = p.get("questions", [])
        ans = p.get("answer_key", [])
        if len(qs) != 10 or len(ans) != 10:
            raise SystemExit(f"10Q/10A violation in {p['id']}")
        qids = {q["id"] for q in qs}
        if {a["question_id"] for a in ans} != qids:
            raise SystemExit(f"answer linkage violation in {p['id']}")
        if any(q.get("type") in {"grammar_category", "grammar_function", "grammar_identification", "person_form"} for q in qs if p.get("unit") == 1):
            raise SystemExit(f"formal metalinguistic type remains in Unit 01: {p['id']}")

    PATH.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")
    after_hash = sha256(PATH)
    report = {
        "schema_version": 1,
        "date": "2026-08-20",
        "language": "ar",
        "level": "A1",
        "unit": 1,
        "status": "BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW",
        "policy": "reading/planning/TEN_QUESTION_STANDARD.md",
        "before_sha256": before_hash,
        "after_sha256": after_hash,
        "canonical_records": len(rows),
        "unit_records": 6,
        "repairs_applied": len(applied),
        "passage_text_changed": False,
        "questions_changed": True,
        "answers_changed": True,
        "repair_scope": "Only the nine independently scanned Unit 01 A1 formal-metalinguistic items were converted to operational form/use tasks.",
        "repairs": applied,
        "release_effect": "Arabic remains educator-blocked. This bounded repair is not release approval and requires independent semantic/educator re-review plus corpus-wide continuation."
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"repairs": len(applied), "before": before_hash, "after": after_hash}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
