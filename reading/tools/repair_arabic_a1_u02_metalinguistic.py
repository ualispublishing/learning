import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
REPORT = ROOT / "reading" / "audit" / "arabic_a1_u02_metalinguistic_repair_2026-08-20.json"
EXPECTED_BEFORE_SHA256 = "d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b"

REPAIRS = {
    ("ar-a1-u02-p01", "q7"): {
        "old_prompt": "ما العلاقة الزمنية التي تدل عليها «قبل»؟",
        "old_type": "grammar_function",
        "old_answer": "أن الحدث يحدث في وقت أسبق من حدث أو وقت آخر.",
        "prompt": "إذا كان الاستعداد يسبق الخروج، أي جملة أنسب: «أستعد قبل الخروج» أم «أستعد بعد الخروج»؟",
        "type": "grammar_choice",
        "answer": "أستعد قبل الخروج.",
        "explanation": "«قبل» تبين أن الاستعداد يحدث أولًا ثم يأتي الخروج.",
    },
    ("ar-a1-u02-p02", "q7"): {
        "old_prompt": "ما وظيفة «أولًا» في ترتيب الأحداث؟",
        "old_type": "grammar_category",
        "old_answer": "تدل على الحدث الذي يأتي قبل غيره.",
        "prompt": "دخلت ليلى الصف ثم فتحت دفترها. أي جملة تصف الترتيب الصحيح: «دخلت الصف أولًا» أم «فتحت الدفتر أولًا»؟",
        "type": "grammar_choice",
        "answer": "دخلت الصف أولًا.",
        "explanation": "«أولًا» تستعمل للحدث الذي يبدأ به الترتيب.",
    },
    ("ar-a1-u02-p03", "q7"): {
        "old_prompt": "ما وظيفة «سوف» قبل الفعل؟",
        "old_type": "grammar_function",
        "old_answer": "تدل على المستقبل.",
        "prompt": "اختر الجملة التي تتحدث عن المستقبل: «سوف نزور المكتبة غدًا» أم «زرنا المكتبة أمس»؟",
        "type": "grammar_choice",
        "answer": "سوف نزور المكتبة غدًا.",
        "explanation": "«سوف» مع الفعل هنا تشير إلى فعل سيحدث لاحقًا.",
    },
    ("ar-a1-u02-p04", "q6"): {
        "old_prompt": "ما التصنيف النحوي لكلمة «أيضا» في هذا الاستعمال؟",
        "old_type": "grammar_category",
        "old_answer": "ظرف",
        "prompt": "أي جملة تضيف الدفتر إلى الكتاب: «أريد كتابًا وأريد أيضًا دفترًا» أم «أريد كتابًا فقط»؟",
        "type": "grammar_choice",
        "answer": "أريد كتابًا وأريد أيضًا دفترًا.",
        "explanation": "«أيضًا» تضيف شيئًا آخر إلى ما ذُكر من قبل.",
    },
    ("ar-a1-u02-p05", "q7"): {
        "old_prompt": "ما نوع «كيف» في السؤال؟",
        "old_type": "grammar_category",
        "old_answer": "اسم استفهام يسأل عن الحال أو الطريقة.",
        "prompt": "إذا أردت السؤال عن طريقة الوصول، أي سؤال أنسب: «كيف نصل إلى المكتبة؟» أم «متى نصل إلى المكتبة؟»؟",
        "type": "grammar_choice",
        "answer": "كيف نصل إلى المكتبة؟",
        "explanation": "«كيف» تسأل هنا عن الطريقة.",
    },
    ("ar-a1-u02-p06", "q9"): {
        "old_prompt": "ماذا تسأل «كيف»؟",
        "old_type": "grammar_function",
        "old_answer": "تسأل عن الطريقة أو الحال.",
        "prompt": "إذا أردت السؤال عن طريقة ترتيب الوقت، أي سؤال أنسب: «كيف نرتب الوقت؟» أم «أين نرتب الوقت؟»؟",
        "type": "grammar_choice",
        "answer": "كيف نرتب الوقت؟",
        "explanation": "«كيف» تسأل هنا عن الطريقة التي يتم بها ترتيب الوقت.",
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
        answers = {a.get("question_id"): a for a in p.get("answer_key", [])}
        changed = 0
        for q in p.get("questions", []):
            key = (p.get("id"), q.get("id"))
            spec = REPAIRS.get(key)
            if not spec:
                continue
            a = answers.get(q.get("id"))
            if not a:
                raise SystemExit(f"missing answer for {key}")
            if q.get("prompt") != spec["old_prompt"] or q.get("type") != spec["old_type"] or a.get("answer") != spec["old_answer"]:
                raise SystemExit(f"repair precondition mismatch for {key}")
            before = {"prompt": q.get("prompt"), "type": q.get("type"), "answer": a.get("answer"), "explanation": a.get("explanation")}
            q["prompt"] = spec["prompt"]
            q["type"] = spec["type"]
            a["answer"] = spec["answer"]
            a["explanation"] = spec["explanation"]
            after = {"prompt": q.get("prompt"), "type": q.get("type"), "answer": a.get("answer"), "explanation": a.get("explanation")}
            applied.append({"passage_id": p["id"], "question_id": q["id"], "before": before, "after": after})
            seen.add(key)
            changed += 1
        if changed:
            p["revision"] = int(p.get("revision", 0)) + 1

    missing = sorted(set(REPAIRS) - seen)
    if missing or len(applied) != 6:
        raise SystemExit(f"repair coverage mismatch: missing={missing}, applied={len(applied)}")

    for p in rows:
        qs, ans = p.get("questions", []), p.get("answer_key", [])
        if len(qs) != 10 or len(ans) != 10:
            raise SystemExit(f"10Q/10A violation in {p['id']}")
        if {q.get("id") for q in qs} != {a.get("question_id") for a in ans}:
            raise SystemExit(f"answer linkage violation in {p['id']}")
        if p.get("unit") == 2 and any(q.get("type") in {"grammar_category", "grammar_function", "grammar_identification", "person_form"} for q in qs):
            raise SystemExit(f"formal metalinguistic type remains in Unit 02: {p['id']}")

    PATH.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")
    after_hash = sha256(PATH)
    report = {
        "schema_version": 1,
        "date": "2026-08-20",
        "language": "ar",
        "level": "A1",
        "unit": 2,
        "status": "BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW",
        "before_sha256": before_hash,
        "after_sha256": after_hash,
        "repairs_applied": len(applied),
        "passage_text_changed": False,
        "repair_scope": "Only six Unit 02 formal-metalinguistic items were converted to operational A1 use/form tasks.",
        "repairs": applied,
        "release_effect": "Arabic remains educator-blocked; this is not release approval."
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"repairs": len(applied), "before": before_hash, "after": after_hash}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
