from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

INPUT = Path("reading/arabic/a2/passages.jsonl")
REPAIR_EVIDENCE = Path("reading/audit/arabic_a2_u08_metalinguistic_repair_2026-08-21.json")
POST_EVIDENCE = Path("reading/audit/arabic_a2_u08_metalinguistic_postrepair_2026-08-21.json")
EXPECTED_BEFORE_SHA256 = "f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c"

REPAIRS = {
    ("ar-a2-u08-p01", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «منطقة» في هذا الاستعمال؟", "before_type": "grammar_category", "before_answer": "اسم",
        "prompt": "للتحدث عن جزء محدد من الحديقة، أي عبارة أنسب: «منطقة قرب المقاعد» أم «مواد قرب المقاعد»؟", "type": "grammar_choice",
        "answer": "منطقة قرب المقاعد.", "explanation": "«منطقة» تشير إلى جزء محدد من المكان، بينما «مواد» تشير إلى الأشياء أو المكونات.",
    },
    ("ar-a2-u08-p01", "q7"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «مواد» في هذا الاستعمال؟", "before_type": "grammar_category", "before_answer": "اسم",
        "prompt": "إذا فصل الطلاب الورق والبلاستيك والمعدن، أي كلمة تجمع هذه الأنواع: «مواد» أم «منطقة»؟", "type": "contrast",
        "answer": "مواد.", "explanation": "الورق والبلاستيك والمعدن أنواع من المواد، لا أسماء لمناطق.",
    },
    ("ar-a2-u08-p02", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «استخدام» في هذا الاستعمال؟", "before_type": "grammar_category", "before_answer": "فعل ماضٍ",
        "prompt": "عند الحديث عن تقليل استهلاك الكهرباء، أي عبارة أنسب: «تقليل استخدام الكهرباء» أم «تقليل استخدم الكهرباء»؟", "type": "grammar_choice",
        "answer": "تقليل استخدام الكهرباء.", "explanation": "في هذا التركيب تأتي «استخدام» بعد «تقليل» للدلالة على الاستعمال نفسه.",
    },
    ("ar-a2-u08-p02", "q7"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «طاقة» في هذا الاستعمال؟", "before_type": "grammar_category", "before_answer": "اسم",
        "prompt": "إذا كان الهدف تقليل الهدر الكهربائي، أي تعبير أنسب: «توفير الطاقة» أم «توفير المنطقة»؟", "type": "grammar_choice",
        "answer": "توفير الطاقة.", "explanation": "«الطاقة» هي المورد الذي يمكن توفيره عند تقليل الاستهلاك غير الضروري.",
    },
    ("ar-a2-u08-p03", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «نمو» في هذا الاستعمال؟", "before_type": "grammar_category", "before_answer": "فعل ماضٍ",
        "prompt": "أكمل بما يناسب: «نراقب _____ النبات كل أسبوع»: «نمو» أم «ينمو»؟", "type": "grammar_choice",
        "answer": "نمو.", "explanation": "التركيب الطبيعي هنا هو «نراقب نمو النبات» عند الحديث عن عملية الزيادة والتطور.",
    },
    ("ar-a2-u08-p04", "q10"): {
        "before_prompt": "ماذا تعبر «ربما» في تفسير نور؟", "before_type": "grammar_function", "before_answer": "عن احتمال غير مؤكد لسبب انتقال الأشياء.",
        "prompt": "أي جملة تدل على أن نور غير متأكدة من سبب انتقال الأشياء: «ربما نقلتها العاصفة» أم «نقلتها العاصفة بالتأكيد»؟", "type": "contrast",
        "answer": "ربما نقلتها العاصفة.", "explanation": "«ربما» تعرض السبب على أنه احتمال، لا حقيقة مؤكدة.",
    },
    ("ar-a2-u08-p05", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «مجتمع» في هذا الاستعمال؟", "before_type": "grammar_category", "before_answer": "اسم",
        "prompt": "للتحدث عن حاجات السكان في المنطقة، أي عبارة أنسب: «احتياجات المجتمع» أم «احتياجات مجتمعًا»؟", "type": "grammar_choice",
        "answer": "احتياجات المجتمع.", "explanation": "التعبير الطبيعي هنا هو «احتياجات المجتمع» عند الإشارة إلى حاجات السكان بوصفهم مجموعة.",
    },
    ("ar-a2-u08-p06", "q10"): {
        "before_prompt": "ماذا تفعل «بعد ذلك» في ترتيب منهج نور؟", "before_type": "grammar_function", "before_answer": "تربط مرحلة المقارنة بالمرحلة التالية، وهي اقتراح تغيير محدد.",
        "prompt": "بعد أن تجمع نور المعلومات وتقارن ما يحدث، ما الخطوة التالية في منهجها؟", "type": "sequence",
        "answer": "تقترح تغييرًا محددًا يمكن متابعته.", "explanation": "النص يرتب الخطوات: الملاحظة، ثم جمع المعلومات والمقارنة، ثم اقتراح تغيير محدد.",
    },
}

FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}
FORMAL_PROMPT_MARKERS = ("التصنيف النحوي", "ما الوظيفة النحوية", "ما وظيفة «", "ماذا تصف «", "ماذا تعبر «", "ماذا تفعل «")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> None:
    raw = INPUT.read_bytes()
    before_sha256 = sha256_bytes(raw)
    if before_sha256 != EXPECTED_BEFORE_SHA256:
        raise SystemExit(f"FAIL CLOSED: expected {EXPECTED_BEFORE_SHA256}, got {before_sha256}")
    lines = raw.decode("utf-8").splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    before_text = {r["id"]: r.get("text") for r in records}
    applied, found = [], set()
    for r in records:
        if r.get("cefr") != "A2" or r.get("unit") != 8:
            continue
        qs = {q["id"]: q for q in r.get("questions", [])}
        ans = {a["question_id"]: a for a in r.get("answer_key", [])}
        for key, spec in REPAIRS.items():
            pid, qid = key
            if pid != r.get("id"):
                continue
            q, a = qs.get(qid), ans.get(qid)
            if q is None or a is None:
                raise SystemExit(f"Missing {pid}/{qid}")
            if (q.get("prompt"), q.get("type"), a.get("answer")) != (spec["before_prompt"], spec["before_type"], spec["before_answer"]):
                raise SystemExit(f"Source drift at {pid}/{qid}")
            before = {"prompt": q["prompt"], "type": q["type"], "answer": a["answer"]}
            q["prompt"], q["type"] = spec["prompt"], spec["type"]
            a["answer"], a["explanation"] = spec["answer"], spec["explanation"]
            applied.append({"passage_id": pid, "question_id": qid, "before": before, "after": {"prompt": q["prompt"], "type": q["type"], "answer": a["answer"], "explanation": a["explanation"]}})
            found.add(key)
    if found != set(REPAIRS):
        raise SystemExit(f"Repair inventory mismatch: missing={sorted(set(REPAIRS)-found)}")
    if any(r.get("text") != before_text[r["id"]] for r in records):
        raise SystemExit("Passage prose changed unexpectedly")
    INPUT.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in records) + "\n", encoding="utf-8")
    after_sha256 = sha256_bytes(INPUT.read_bytes())
    unit = [r for r in records if r.get("cefr") == "A2" and r.get("unit") == 8]
    questions = [q for r in unit for q in r.get("questions", [])]
    answers = [a for r in unit for a in r.get("answer_key", [])]
    if (len(unit), len(questions), len(answers)) != (6, 60, 60):
        raise SystemExit(f"Expected 6/60/60, got {len(unit)}/{len(questions)}/{len(answers)}")
    for r in unit:
        if {q["id"] for q in r["questions"]} != {a["question_id"] for a in r["answer_key"]}:
            raise SystemExit(f"Question/answer linkage mismatch in {r['id']}")
    findings = []
    for r in unit:
        for q in r["questions"]:
            p = q.get("prompt", "")
            if q.get("type") in FORMAL_TYPES or any(m in p for m in FORMAL_PROMPT_MARKERS):
                findings.append({"passage_id": r["id"], "question_id": q["id"], "type": q.get("type"), "prompt": p})
    counts = Counter(q.get("prompt", "") for q in questions)
    dups = sorted(p for p, n in counts.items() if p and n > 1)
    if findings:
        raise SystemExit(f"Residual metalinguistic findings: {findings}")
    if dups:
        raise SystemExit(f"Duplicate prompts: {dups}")
    repair = {"schema_version": 1, "date": "2026-08-21", "language": "ar", "level": "A2", "unit": 8, "status": "BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW", "before_sha256": before_sha256, "after_sha256": after_sha256, "inventory_candidates": len(REPAIRS), "confirmed_repairs": len(applied), "passage_text_changed": False, "repairs": applied, "release_effect": "Arabic remains educator-blocked; independent semantic/native/educator review required."}
    post = {"schema_version": 1, "date": "2026-08-21", "language": "ar", "level": "A2", "unit": 8, "bound_sha256": after_sha256, "scope": {"records": len(unit), "questions": len(questions), "answers": len(answers)}, "inventory_candidates": len(REPAIRS), "confirmed_repairs": len(applied), "passage_text_changed": False, "formal_metalinguistic_finding_count": len(findings), "findings": findings, "exact_duplicate_prompt_count": len(dups), "duplicate_prompts": dups, "question_type_counts": dict(sorted(Counter(q.get("type") for q in questions).items())), "status": "PASS_DETERMINISTIC_A2_UNIT08", "limitations": "Deterministic/self-review only; independent native/educator review remains required.", "release_effect": "Arabic remains educator-blocked."}
    REPAIR_EVIDENCE.write_text(json.dumps(repair, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    POST_EVIDENCE.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": post["status"], "before_sha256": before_sha256, "after_sha256": after_sha256, "repairs": len(applied), "records": len(unit), "questions": len(questions), "answers": len(answers)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
