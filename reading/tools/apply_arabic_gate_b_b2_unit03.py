#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 3 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
EXPECTED_IDS = [f"ar-b2-u03-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (B2 Unit 3): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u03-p01": [
        (
            "من كتب ساعات أكثر قد يكون قد أصلح خطأ سببه غيره، ومن ساعد زملاءه قد يقل إنتاجه الفردي لكنه يرفع نتيجة المجموعة.",
            "من سجّل ساعات أكثر قد يكون قد أصلح خطأ سببه غيره، ومن ساعد زملاءه قد يقل إنتاجه الفردي لكنه يرفع نتيجة المجموعة.",
        ),
        (
            "اتفق الفريق لذلك على وصف الأعمال الإضافية أولًا قبل تحويلها إلى نسب مالية، وعلى السماح لكل عضو بتفسير عبء لم يكن ظاهرًا للآخرين.",
            "اتفق الفريق لذلك على وصف الأعمال الإضافية أولًا، ثم تحويلها إلى نسب مالية، وعلى السماح لكل عضو بتفسير عبء لم يكن ظاهرًا للآخرين.",
        ),
    ],
    "ar-b2-u03-p04": [
        (
            "الإلغاء يفرض عبئًا على المشاركين والمنظمين وقد يشجع رسائل غير موثوقة على تعطيل أنشطة لاحقة.",
            "الإلغاء يفرض عبئًا على المشاركين والمنظمين وقد يشجع أصحاب الرسائل غير الموثوقة على محاولة تعطيل أنشطة لاحقة.",
        ),
    ],
    "ar-b2-u03-p05": [
        (
            "قال بعض الأعضاء إن توسيع القاعدة سيقلل دقتها ويجعل الصندوق المخصص يذهب إلى حالات أبعد عن هدفه.",
            "قال بعض الأعضاء إن توسيع القاعدة سيقلل دقتها ويجعل أموال الصندوق المخصص تذهب إلى حالات أبعد عن هدفه.",
        ),
        (
            "قاعدة واسعة قد تستهلك المورد على من ليسوا ضمن الهدف، وقاعدة ضيقة قد تحمي المورد لكنها تترك أشخاصًا مقصودين أصلًا خارجها.",
            "قاعدة واسعة قد تستهلك المورد في دعم من ليسوا ضمن الهدف، وقاعدة ضيقة قد تحمي المورد لكنها تترك أشخاصًا مقصودين أصلًا خارجها.",
        ),
    ],
    "ar-b2-u03-p06": [
        (
            "وتطلب من الفائزين نشر صور عن أعمالهم.",
            "وتطلب من الفائزين نشر صور لأعمالهم.",
        ),
        (
            "وإذا ظهرت هوية شخص في مادة النشر، فهل موافقته على المشروع تعني موافقة على كل جمهور؟",
            "وإذا كانت هوية شخص ظاهرة في مادة النشر، فهل موافقته على المشروع تعني موافقة على كل جمهور؟",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u03-p01": {
        "answers": {
            "q3": (
                "لأن المرض والمهام ونوع العمل والمساعدة قد تجعل ساعة شخص مختلفة في أثرها عن ساعة آخر.",
                "لأن المرض والمهام ونوع العمل والمساعدة قد تجعل ساعة شخص مختلفة في أثرها عن ساعة شخص آخر.",
            ),
        },
    },
    "ar-b2-u03-p03": {
        "answers": {
            "q1": (
                "الحفاظ على قاعدة متسقة للجميع مقابل تصحيح حالات تثبت أن الأداة أو شروط الوصول أضرتها خطأ.",
                "الحفاظ على قاعدة متسقة للجميع مقابل تصحيح حالات تثبت أن الأداة أو شروط الوصول أضرت بها على نحو غير مقصود.",
            ),
            "q3": (
                "ليعرف هل هي حالات نادرة أم نمط يكشف عيبًا متكررًا في النظام.",
                "ليعرف ما إذا كانت حالات نادرة أم نمطًا يكشف عيبًا متكررًا في النظام.",
            ),
            "q6": (
                "تمنع الأغلبية من إخفاء أقلية ذات قيمة تشخيصية وتوضح أن عدد الحالات الصغير قد يكشف خللًا نظاميًا متكررًا.",
                "توضح أن كثرة الاعتراضات التي لم تغير النتيجة لا ينبغي أن تحجب أقلية ذات قيمة تشخيصية، وأن عددًا قليلًا من الحالات قد يكشف خللًا نظاميًا متكررًا.",
            ),
        },
    },
    "ar-b2-u03-p04": {
        "answers": {
            "q1": (
                "لأن الدليل غير واضح ويمكن تخفيض الخطر بخطوات أقل نهائية مع الاستعداد للتغيير.",
                "لأن الدليل غير واضح ويمكن خفض الخطر بإجراءات أقل حسمًا وقابلة للتراجع مع الاستعداد للتغيير.",
            ),
            "q5": (
                "يربط شدة القيد بقوة الدليل وحجم الضرر وعبء القرار، ويستخدم إجراءات قابلة للتراجع مع نقاط معلنة للانتقال إلى إلغاء أقوى.",
                "يربط شدة القيد بقوة الدليل وحجم الضرر وعبء القرار، ويستخدم إجراءات قابلة للتراجع مع نقاط معلنة للانتقال إلى الإلغاء الكامل.",
            ),
        },
    },
    "ar-b2-u03-p05": {
        "answers": {
            "q9": (
                "مدى مطابقة القياس أو الحكم أو القاعدة لما تريد تمثيله من دون أخطاء كثيرة.",
                "مدى مطابقة القياس أو الحكم أو القاعدة لما يُراد تمثيله من دون أخطاء كثيرة.",
            ),
        },
    },
    "ar-b2-u03-p06": {
        "answers": {
            "q6": (
                "مدى مطابقة القاعدة أو القياس للهدف المقصود وتقليل أخطاء الإدخال والاستبعاد.",
                "مدى مطابقة القاعدة أو القياس للهدف المقصود، مع تقليل أخطاء الإدخال والاستبعاد.",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u03-p01": [
        ("text", "naturalness_idiomaticity", "minor", "كتب ساعات is not idiomatic for logged/worked hours; use سجّل ساعات."),
        ("text", "grammar_wording", "minor", "أولًا قبل is redundant sequencing; use أولًا، ثم for a clear ordered procedure."),
        ("answer q3", "grammar_wording", "moderate", "عن ساعة آخر leaves آخر without its required noun; use ساعة شخص آخر."),
    ],
    "ar-b2-u03-p02": [],
    "ar-b2-u03-p03": [
        ("answer q1", "grammar_wording", "moderate", "أضرتها خطأ is malformed; state that the tool/access conditions harmed the cases unintentionally."),
        ("answer q3", "grammar_wording", "minor", "Use ما إذا كانت ... أم نمطًا for the indirect alternative question and correct case."),
        ("answer q6", "semantic_precision", "moderate", "The old wording makes a majority literally hide a minority; state that numerous unchanged appeals should not obscure a diagnostically valuable minority."),
    ],
    "ar-b2-u03-p04": [
        ("text", "semantic_precision", "moderate", "رسائل cannot themselves be encouraged; identify the senders as the agents who may be encouraged to attempt later disruption."),
        ("answer q1", "naturalness_idiomaticity", "moderate", "خطوات أقل نهائية is a calque; use less decisive, reversible measures."),
        ("answer q5", "naturalness_idiomaticity", "minor", "إلغاء أقوى is not idiomatic; the escalation point is full cancellation."),
    ],
    "ar-b2-u03-p05": [
        ("text", "naturalness_idiomaticity", "moderate", "A fund does not يذهب إلى حالات; its funds can go to cases beyond the target."),
        ("text", "naturalness_idiomaticity", "moderate", "تستهلك المورد على is a faulty collocation; use تستهلك المورد في دعم."),
        ("answer q9", "grammar_wording", "minor", "The definition needs an impersonal relative construction: لما يُراد تمثيله."),
    ],
    "ar-b2-u03-p06": [
        ("text", "naturalness_idiomaticity", "minor", "The idiomatic collocation is صور لأعمالهم, not صور عن أعمالهم."),
        ("text", "naturalness_idiomaticity", "minor", "ظهرت هوية شخص is awkward; preserve the target noun while stating that the person's identity is visible in the publication material."),
        ("answer q6", "grammar_wording", "minor", "Coordinate the definition cleanly by linking error reduction with مع rather than leaving an unintegrated verbal noun phrase."),
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
    if [rows[i].get("id") for i in range(12, 18)] != EXPECTED_IDS:
        raise SystemExit("B2 Unit 3 id/frontier drift")

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
    if total_findings != 15 or records_with_findings != 5:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")

    PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "level": "B2",
                "unit": 3,
                "records_reviewed": 6,
                "records_with_findings": records_with_findings,
                "fresh_findings": total_findings,
                "pre_repair_canonical_sha256": pre_sha,
                "post_repair_canonical_sha256": sha(PATH.read_bytes()),
                "word_counts": {pid: by_id[pid]["word_count"] for pid in EXPECTED_IDS},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
