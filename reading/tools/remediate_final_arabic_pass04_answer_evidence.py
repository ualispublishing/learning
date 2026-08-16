#!/usr/bin/env python3
"""Repair the nine genuine Arabic Pass 04 answer/evidence weaknesses.

The Pass 04 manual adjudication reduced 30 raw surface candidates to nine real
precision problems: one A2 reference answer and eight C2 literal-detail answers
whose generic/template wording did not identify the passage-specific evidence or
tradeoff strongly enough.

This script changes answer text only. Passage prose, questions, IDs, lexical
schedules, target metadata, word counts, review state, and every unselected
answer are immutable. Fail closed on any source drift.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# (level, passage_id, question_id) -> exact source guard + replacement answer.
REPAIRS = {
    ("a2", "ar-a2-u10-p06", "q7"): {
        "prompt": "إلى ماذا تشير «هذه المهارات» في الجملة الأخيرة؟",
        "old": "إلى مجموعة مهارات القراءة العملية المذكورة في الخدمات والخطط والذاكرة والشراء والتعلم والسفر والأخبار والبيئة والثقافة.",
        "new": "إلى مهارات تحديد الفكرة الرئيسية، وربط السبب بالنتيجة، وتتبع المرجع عبر الجمل، ومقارنة ما قيل أولًا بما ظهر لاحقًا.",
    },
    ("c2", "ar-c2-u08-p03", "q2"): {
        "prompt": "ما نوع الدليل الذي يفحصه النص؟",
        "old": "مصادر أو آثار من الأرشيف الخيالي.",
        "new": "آثار مادية في القاعة، وسجلات الصيانة، وصور التوثيق، وروايات الزوار التي تكشف طبقات البناء والترميم.",
    },
    ("c2", "ar-c2-u08-p05", "q2"): {
        "prompt": "ما نوع الدليل الذي يفحصه النص؟",
        "old": "مصادر أو آثار من الأرشيف الخيالي.",
        "new": "خطوط زمنية للموارد والتحالفات والأسعار والثقة المؤسسية، مع القرارات المعلنة وبيانات التنفيذ والذاكرة العامة.",
    },
    ("c2", "ar-c2-u08-p06", "q2"): {
        "prompt": "ما نوع الدليل الذي يفحصه النص؟",
        "old": "مصادر أو آثار من الأرشيف الخيالي.",
        "new": "مذكرات مدير، ودفاتر أجور، وصورة لمبنى، وتقارير حرس، وكتاب يركز على يوم إعلان الإضراب.",
    },
    ("c2", "ar-c2-u09-p01", "q2"): {
        "prompt": "ما المفاضلة التي يعرضها النص؟",
        "old": "فائدة تشغيلية تقابلها مخاطرة أو قيد أو فقدان خيار.",
        "new": "زيادة السرعة وتقليل العمل اليدوي مقابل ارتفاع قبول مواعيد غير مناسبة وازدياد كلفة الاعتراض على الخيار الافتراضي.",
    },
    ("c2", "ar-c2-u09-p03", "q2"): {
        "prompt": "ما المفاضلة التي يعرضها النص؟",
        "old": "فائدة تشغيلية تقابلها مخاطرة أو قيد أو فقدان خيار.",
        "new": "زيادة الإشراف والمعلومات والخبرات لتحسين اكتشاف الأخطاء مقابل ارتفاع الحمل المعرفي وخطر توزيع المسؤولية أو ضعف الانتباه.",
    },
    ("c2", "ar-c2-u09-p04", "q2"): {
        "prompt": "ما المفاضلة التي يعرضها النص؟",
        "old": "فائدة تشغيلية تقابلها مخاطرة أو قيد أو فقدان خيار.",
        "new": "الحفاظ على مسؤوليات محلية واضحة مقابل الحاجة إلى مالك للنظام الكلي يراقب تفاعل المكونات والمخاطر العابرة للفرق.",
    },
    ("c2", "ar-c2-u09-p05", "q2"): {
        "prompt": "ما المفاضلة التي يعرضها النص؟",
        "old": "فائدة تشغيلية تقابلها مخاطرة أو قيد أو فقدان خيار.",
        "new": "التوسع السريع بعد نجاح التجربة وخفض وقت العمل مقابل احتمال آثار ممتدة وإغلاق بدائل مستقبلية يصعب الرجوع عنها.",
    },
    ("c2", "ar-c2-u09-p06", "q2"): {
        "prompt": "ما المفاضلة التي يعرضها النص؟",
        "old": "فائدة تشغيلية تقابلها مخاطرة أو قيد أو فقدان خيار.",
        "new": "تيسير العمل ورفع الأداء مقابل خطر انتقال سلطة القرار، وتوزع المسؤولية، وصعوبة الرجوع إذا أصبح الخطأ عالي الأثر.",
    },
}


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_rows(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def answer_map(row: dict) -> dict[str, dict]:
    return {
        str(answer.get("question_id")): answer
        for answer in row.get("answer_key", [])
        if isinstance(answer, dict)
    }


def question_map(row: dict) -> dict[str, dict]:
    return {
        str(question.get("id")): question
        for question in row.get("questions", [])
        if isinstance(question, dict)
    }


def projection_without_selected_answers(row: dict, selected_qids: set[str]) -> dict:
    result = copy.deepcopy(row)
    for answer in result.get("answer_key", []):
        if str(answer.get("question_id")) in selected_qids:
            answer.pop("answer", None)
    return result


def main() -> None:
    by_level = {"a2": 0, "c2": 0}
    changed = 0

    for level in ("a2", "c2"):
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        rows = read_rows(path)
        if len(rows) != 60:
            raise AssertionError(f"{level}: expected 60 passages, got {len(rows)}")
        before = copy.deepcopy(rows)
        row_by_id = {str(row.get("id")): row for row in rows}
        selected_by_pid: dict[str, set[str]] = {}

        for (repair_level, pid, qid), spec in REPAIRS.items():
            if repair_level != level:
                continue
            row = row_by_id.get(pid)
            if row is None:
                raise AssertionError(f"{level}: missing passage {pid}")
            if len(row.get("questions", [])) != 10 or len(row.get("answer_key", [])) != 10:
                raise AssertionError(f"{pid}: expected 10 questions and 10 answers")

            q = question_map(row).get(qid)
            a = answer_map(row).get(qid)
            if q is None or a is None:
                raise AssertionError(f"{pid}: missing linked question/answer {qid}")
            if q.get("prompt") != spec["prompt"]:
                raise AssertionError(
                    f"{pid} {qid}: prompt drift; expected {spec['prompt']!r}, got {q.get('prompt')!r}"
                )
            if a.get("answer") != spec["old"]:
                raise AssertionError(
                    f"{pid} {qid}: answer drift; expected {spec['old']!r}, got {a.get('answer')!r}"
                )

            a["answer"] = spec["new"]
            selected_by_pid.setdefault(pid, set()).add(qid)
            changed += 1
            by_level[level] += 1

        before_by_id = {str(row.get("id")): row for row in before}
        after_by_id = {str(row.get("id")): row for row in rows}
        for pid, old in before_by_id.items():
            new = after_by_id[pid]
            selected_qids = selected_by_pid.get(pid)
            if not selected_qids:
                if old != new:
                    raise AssertionError(f"{pid}: unselected record changed")
                continue
            if projection_without_selected_answers(old, selected_qids) != projection_without_selected_answers(new, selected_qids):
                raise AssertionError(f"{pid}: mutation outside selected answer text")

        write_rows(path, rows)

    if changed != 9 or by_level != {"a2": 1, "c2": 8}:
        raise AssertionError(f"expected 9 repairs (A2=1, C2=8), got changed={changed}, by_level={by_level}")

    print(json.dumps({"answers_repaired": changed, "by_level": by_level}, ensure_ascii=False))


if __name__ == "__main__":
    main()
