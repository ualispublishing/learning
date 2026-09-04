#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 5 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
EXPECTED_IDS = [f"ar-b2-u05-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (B2 Unit 5): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u05-p03": [
        (
            "صمم طلاب في مدينة خيالية مشروعًا صغيرًا لحديقة تعليمية في منطقة صحراء.",
            "صمم طلاب في مدينة خيالية مشروعًا صغيرًا لحديقة تعليمية عند حافة صحراء.",
        ),
    ],
    "ar-b2-u05-p05": [
        (
            "أراد فريق توسيع النوع نفسه من المظلات إلى كل الشارع فورًا.",
            "أراد فريق تعميم النوع نفسه من المظلات على امتداد الشارع فورًا.",
        ),
    ],
    "ar-b2-u05-p06": [
        (
            "قالت إن الاعتراف بعدم اليقين لا يمنع الفعل؛ يمنعنا من إخفاء الافتراضات التي يجب أن يظل القرار قادرًا على مراجعتها.",
            "قالت إن الاعتراف بعدم اليقين لا يمنع الفعل؛ بل يمنعنا من إخفاء الافتراضات التي يجب أن تبقى قابلة للمراجعة عند اتخاذ القرار.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u05-p03": {
        "questions": {
            "q1": (
                "لماذا لا يعلن الطلاب نباتًا واحدًا الأفضل؟",
                "لماذا لا يعلن الطلاب أن نباتًا واحدًا هو الأفضل؟",
            ),
        },
        "answers": {
            "q3": (
                "لأن حلًا يعمل تقنيًا قد يفشل عمليًا إذا احتاج موارد أو عملًا لا يمكن استمرارها.",
                "لأن حلًا يعمل تقنيًا قد يفشل عمليًا إذا احتاج إلى موارد أو جهد لا يمكن توفيرهما باستمرار.",
            ),
            "q7": (
                "دليل البداية يبرر تجربة أوسع، والضمان العام يدعي نجاحًا خارج الظروف التي اختبرت.",
                "الدليل المبدئي يبرر تجربة أوسع، أما الضمان العام فيدعي نجاحًا خارج ظروف التجربة الأصلية.",
            ),
        },
    },
    "ar-b2-u05-p04": {
        "questions": {
            "q1": (
                "لماذا ترفض الباحثة الرقم ذي المنزلتين؟",
                "لماذا ترفض الباحثة عرض رقم بمنزلتين عشريتين؟",
            ),
        },
    },
    "ar-b2-u05-p05": {
        "questions": {
            "q1": (
                "لماذا لا يكرر الفريق المظلة نفسها في كل الشارع؟",
                "لماذا لا يكرر الفريق المظلة نفسها على امتداد الشارع كله؟",
            ),
        },
        "answers": {
            "q6": (
                "تثبت قابلية انتقال وظيفة عامة ثم تضع حدًا على نقل التفاصيل الهندسية نفسها بين السياقات.",
                "توضح أن وظيفة عامة قد تنتقل بين المواقع، ثم تحد من تعميم التفاصيل الهندسية نفسها بين السياقات.",
            ),
        },
    },
    "ar-b2-u05-p06": {
        "answers": {
            "q5": (
                "يمكن الفعل مع إظهار الحدود وبناء قرارات مرنة بدل انتظار يقين كامل أو إخفاء الجهل.",
                "يمكن اتخاذ قرار مع إظهار حدود المعرفة وبناء خيارات مرنة بدل انتظار يقين كامل أو إخفاء ما نجهله.",
            ),
            "q8": (
                "تقدم غياب معيار المراجعة كشرط يكشف أن المرونة المعلنة ليست مرتبطة فعليًا بمعلومات جديدة.",
                "توضح أن غياب معيار للمراجعة يكشف أن المرونة المعلنة ليست مرتبطة فعليًا بمعلومات جديدة.",
            ),
            "q10": (
                "لأن بعض المعلومات والحدود معروفة ويمكن تصميم فعل مرن يحترم ما بقي مجهولًا.",
                "لأن بعض المعلومات والحدود معروفة، ويمكن تصميم استجابة مرنة تراعي ما بقي مجهولًا.",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u05-p01": [],
    "ar-b2-u05-p02": [],
    "ar-b2-u05-p03": [
        ("text", "naturalness_idiomaticity", "moderate", "في منطقة صحراء is not idiomatic MSA; place the garden at the edge of a desert while preserving the lexical target."),
        ("question q1", "grammar_wording", "moderate", "يعلن الطلاب نباتًا واحدًا الأفضل is malformed; announce a clause with أن ... هو الأفضل."),
        ("answer q3", "grammar_wording", "moderate", "احتاج requires إلى here, and استمرارها cannot cleanly refer to mixed resources/work; use resources or effort that cannot be provided continuously."),
        ("answer q7", "naturalness_idiomaticity", "minor", "دليل البداية and الظروف التي اختبرت are awkward; contrast preliminary evidence with a general guarantee beyond the original experimental conditions."),
    ],
    "ar-b2-u05-p04": [
        ("question q1", "grammar_wording", "moderate", "The object phrase الرقم ذي المنزلتين has the wrong case form for ذو; recast the question as عرض رقم بمنزلتين عشريتين."),
    ],
    "ar-b2-u05-p05": [
        ("text", "naturalness_idiomaticity", "moderate", "توسيع ... إلى كل الشارع is a faulty collocation; use تعميم ... على امتداد الشارع."),
        ("question q1", "naturalness_idiomaticity", "minor", "في كل الشارع is awkward for distribution along a street; use على امتداد الشارع كله."),
        ("answer q6", "semantic_precision", "moderate", "تثبت قابلية انتقال overclaims what repeated local tests show; state that the general function may transfer while engineering details still require contextual limits."),
    ],
    "ar-b2-u05-p06": [
        ("text", "reference_clarity", "moderate", "The decision itself should not be the agent that reviews assumptions; keep assumptions explicitly reviewable when the decision is made."),
        ("answer q5", "naturalness_idiomaticity", "moderate", "يمكن الفعل is an awkward calque; state directly that a decision can be taken while limits remain visible."),
        ("answer q8", "naturalness_idiomaticity", "minor", "تقدم غياب معيار المراجعة كشرط is a calque; state directly what absence of a review criterion reveals."),
        ("answer q10", "naturalness_idiomaticity", "moderate", "تصميم فعل مرن is not an idiomatic collocation; use تصميم استجابة مرنة."),
    ],
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wc(text: str) -> int:
    return len(TOKEN.findall(text))


def target_counts(record: dict) -> dict[str, int]:
    forms: list[str] = []
    for field in ("new_lexical_targets", "review_lexical_targets"):
        for item in record.get(field, []):
            form = item.get("form")
            if isinstance(form, str) and form and form not in forms:
                forms.append(form)
    text = record.get("text", "")
    return {form: text.count(form) for form in forms}


def main() -> None:
    raw = PATH.read_bytes()
    pre_sha = sha(raw)
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [row.get("sequence") for row in rows] != list(range(1, 61)):
        raise SystemExit("B2 corpus layout/sequence drift")
    if [rows[i].get("id") for i in range(24, 30)] != EXPECTED_IDS:
        raise SystemExit("B2 Unit 5 id/frontier drift")

    by_id = {row["id"]: row for row in rows}
    before_targets = {pid: target_counts(by_id[pid]) for pid in EXPECTED_IDS}

    for pid in EXPECTED_IDS:
        record = by_id[pid]
        quality = record.get("quality", {})
        if quality.get("status") != "draft" or quality.get("coverage_check") != "pending":
            raise SystemExit(f"{pid}: unexpected release/coverage state")
        for field in ("linguistic_review", "pedagogical_review", "answer_key_check", "schema_check"):
            if quality.get(field) != "pending":
                raise SystemExit(f"{pid}: expected pending {field}, got {quality.get(field)!r}")

        for old, new in TEXT_REPAIRS.get(pid, []):
            if record.get("text", "").count(old) != 1:
                raise SystemExit(f"{pid}: text repair source drift: {old!r}")
            record["text"] = record["text"].replace(old, new, 1)

        questions = {q["id"]: q for q in record.get("questions", [])}
        answers = {a["question_id"]: a for a in record.get("answer_key", [])}
        repair = QA_REPAIRS.get(pid, {})
        for qid, (old, new) in repair.get("questions", {}).items():
            if qid not in questions or questions[qid].get("prompt") != old:
                raise SystemExit(f"{pid}/{qid}: question drift")
            questions[qid]["prompt"] = new
        for qid, (old, new) in repair.get("answers", {}).items():
            if qid not in answers or answers[qid].get("answer") != old:
                raise SystemExit(f"{pid}/{qid}: answer drift: {answers.get(qid, {}).get('answer')!r}")
            answers[qid]["answer"] = new

        record["word_count"] = wc(record["text"])
        if not 350 <= record["word_count"] <= 550:
            raise SystemExit(f"{pid}: word count {record['word_count']} outside B2 band")
        if target_counts(record) != before_targets[pid]:
            raise SystemExit(f"{pid}: lexical target occurrence drift")
        if len(record.get("questions", [])) != 10 or len(record.get("answer_key", [])) != 10:
            raise SystemExit(f"{pid}: 10Q/10A invariant failed")
        answers_by_id = {a["id"]: a for a in record["answer_key"]}
        if set(questions) != {f"q{i}" for i in range(1, 11)}:
            raise SystemExit(f"{pid}: question id invariant failed")
        for q in record["questions"]:
            aid = q.get("answer_id")
            if aid not in answers_by_id or answers_by_id[aid].get("question_id") != q.get("id"):
                raise SystemExit(f"{pid}: question/answer linkage drift at {q.get('id')}")

        record["revision"] = int(record.get("revision", 0) or 0) + 1
        quality = record.setdefault("quality", {})
        for field in ("linguistic_review", "pedagogical_review", "answer_key_check", "schema_check"):
            quality[field] = "pass"
        if NOTE not in quality.setdefault("notes", []):
            quality["notes"].append(NOTE)

    total_findings = sum(len(FINDING_META[pid]) for pid in EXPECTED_IDS)
    records_with_findings = sum(bool(FINDING_META[pid]) for pid in EXPECTED_IDS)
    if total_findings != 12 or records_with_findings != 4:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")

    PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(json.dumps({
        "level": "B2",
        "unit": 5,
        "records_reviewed": 6,
        "records_with_findings": records_with_findings,
        "fresh_findings": total_findings,
        "pre_repair_canonical_sha256": pre_sha,
        "post_repair_canonical_sha256": sha(PATH.read_bytes()),
        "word_counts": {pid: by_id[pid]["word_count"] for pid in EXPECTED_IDS},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
