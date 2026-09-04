#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 6 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
EXPECTED_IDS = [f"ar-b2-u06-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (B2 Unit 6): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u06-p01": [
        (
            "إعدادات للجمهور الأول، اختيار للمحتوى، طلب اجتماعي لإعادة الاستخدام، وقبول أن بعض الآثار لا يمكن عكسها بالكامل بعد الانتشار.",
            "إعدادات للجمهور الأول، اختيار للمحتوى، طلب اجتماعي بعدم إعادة الاستخدام، وقبول أن بعض الآثار لا يمكن عكسها بالكامل بعد الانتشار.",
        ),
    ],
    "ar-b2-u06-p03": [
        (
            "لو كان لديها مفتاح احتياطي كامل، لتحسن الاسترجاع لكنه سيخلق جهة إضافية قادرة على فتح الملفات.",
            "لو كان لديها مفتاح احتياطي كامل، لأصبح الاسترجاع أسهل، لكنه كان سيخلق جهة إضافية قادرة على فتح الملفات.",
        ),
    ],
    "ar-b2-u06-p04": [
        (
            "أما في مدرسة صغيرة فكان تمثيل بعض الفئات يتكون من شخص أو شخصين فقط.",
            "أما في مدرسة صغيرة فكان تمثيل بعض الفئات مقتصرًا على شخص أو شخصين فقط.",
        ),
    ],
    "ar-b2-u06-p06": [
        (
            "ثم طبقت نور خريطة التدفق على مثال واحد: خدمة تعليمية تسمح بمشاركة تقدم الطالب مع معلمه.",
            "ثم طبقت نور خريطة التدفق على مثال واحد: خدمة تعليمية تسمح بمشاركة معلومات عن تقدم الطالب مع معلمه.",
        ),
        (
            "وأضافت سؤالًا عن التغيير بمرور الوقت: قد يكون استخدام مقبولًا اليوم أوسع غدًا إذا تغير الغرض أو الجمهور أو مدة الاحتفاظ.",
            "وأضافت سؤالًا عن التغيير بمرور الوقت: قد يصبح استخدام مقبول اليوم أوسع نطاقًا غدًا إذا تغير الغرض أو الجمهور أو مدة الاحتفاظ.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u06-p01": {
        "answers": {
            "q5": (
                "تستخدم إعداد الجمهور الأول، وتراجع المتابعين، وتختار نوع المحتوى والقناة، وتوضح توقع إعادة الاستخدام مع إدراك أن النسخ اللاحق لا يمكن منعه بالكامل.",
                "تستخدم إعداد الجمهور الأول، وتراجع المتابعين، وتختار نوع المحتوى والقناة، وتوضح توقعاتها بشأن عدم إعادة الاستخدام مع إدراك أن النسخ اللاحق لا يمكن منعه بالكامل.",
            ),
            "q10": (
                "قابل أو أعطى موافقة على فعل أو شرط.",
                "شخص يقبل فعلًا أو شرطًا ويعطي موافقته عليه.",
            ),
        },
    },
    "ar-b2-u06-p03": {
        "answers": {
            "q1": (
                "لأن تصميم الخدمة لا يجعلها تحتفظ بالمفتاح الذي يفتح المحتوى.",
                "لأن تصميم الخدمة لا يتضمن احتفاظ الشركة بالمفتاح الذي يفتح المحتوى.",
            ),
            "q4": (
                "تحمي المحتوى من مقدم الخدمة لكنها تجعل فقدان مفتاح المستخدم أكثر خطورة.",
                "تمنع مقدم الخدمة من فتح المحتوى، لكنها تجعل فقدان مفتاح المستخدم أكثر خطورة.",
            ),
            "q8": (
                "تجعل التعقيد شرطًا يربط قوة التصميم النظرية بإمكان تطبيقه وصيانته عمليًا.",
                "توضح أن التعقيد قد يجعل التصميم القوي نظريًا صعب التطبيق أو الصيانة عمليًا.",
            ),
        },
    },
    "ar-b2-u06-p04": {
        "answers": {
            "q1": (
                "لأن مجموع الخصائص في فئات صغيرة يمكن أن يسمح بتخمين هوية الأشخاص.",
                "لأن اجتماع الخصائص ضمن فئات صغيرة قد يسمح بتخمين هوية الأشخاص.",
            ),
            "q7": (
                "الأول حذف معرفًا مباشرًا، والثاني يقلل إمكانية استنتاج الشخص من بقية البيانات.",
                "الأول يعني حذف معرّف مباشر، والثاني يعني تقليل إمكانية استنتاج هوية الشخص من بقية البيانات.",
            ),
            "q8": (
                "تقدم معرفة خارجية كشرط يزيد قدرة التعرف حتى عندما لا يحتوي الجدول على اسم مباشر.",
                "توضح أن المعرفة الخارجية قد تزيد إمكان التعرف على الشخص حتى عندما لا يحتوي الجدول على اسم مباشر.",
            ),
        },
    },
    "ar-b2-u06-p05": {
        "answers": {
            "q2": (
                "عدم الربط، ربط مؤقت محمي، أو احتفاظ طويل لأبحاث لاحقة.",
                "عدم الربط، أو ربط مؤقت داخل بيئة محمية، أو الاحتفاظ بالصلة مدة أطول لأبحاث لاحقة.",
            ),
            "q6": (
                "تستبدل تخزينًا مفتوح الغرض بقرار جديد ومراجعة مستقلة عندما يظهر سؤال فعلي لاحقًا.",
                "ترفض الاحتفاظ بالصلة لغرض مفتوح، وتطلب قرارًا جديدًا ومراجعة مستقلة عندما يظهر سؤال بحثي فعلي لاحقًا.",
            ),
        },
    },
    "ar-b2-u06-p06": {
        "answers": {
            "q5": (
                "حدود متغيرة على تدفق المعلومات واستخدامها واستنتاجها وفق الغرض والسياق والمدة والجهات.",
                "مجموعة حدود متغيرة تضبط تدفق المعلومات واستخدامها وما يمكن استنتاجه منها وفق الغرض والسياق والمدة والجهات.",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u06-p01": [
        ("text", "semantic_precision", "major", "طلب اجتماعي لإعادة الاستخدام reverses the intended privacy request; it must be a request not to reuse/reshare the material."),
        ("answer q5", "assessment_alignment", "moderate", "توضح توقع إعادة الاستخدام conflicts with the passage's stated expectation of non-resharing; make the expectation explicit."),
        ("answer q10", "naturalness_idiomaticity", "moderate", "قابل أو أعطى موافقة is an unclear definition of موافق; define the consenting/agreeing person directly."),
    ],
    "ar-b2-u06-p02": [],
    "ar-b2-u06-p03": [
        ("text", "grammar_wording", "moderate", "The counterfactual begins with لو but shifts to a simple future سيخلق; keep both consequences in the counterfactual frame."),
        ("answer q1", "naturalness_idiomaticity", "moderate", "تصميم الخدمة لا يجعلها تحتفظ is an awkward causative construction; state that the design does not include company retention of the key."),
        ("answer q4", "semantic_precision", "moderate", "السرية تحمي المحتوى من مقدم الخدمة overstates the relation; it prevents the provider from opening the content."),
        ("answer q8", "naturalness_idiomaticity", "moderate", "تجعل التعقيد شرطًا يربط is a calque that obscures the operational point; state directly that complexity can make a theoretically strong design hard to apply or maintain."),
    ],
    "ar-b2-u06-p04": [
        ("text", "naturalness_idiomaticity", "moderate", "تمثيل الفئات يتكون من شخص أو شخصين is not idiomatic; representation can be limited to one or two people."),
        ("answer q1", "semantic_precision", "moderate", "مجموع الخصائص suggests arithmetic addition; the risk arises from the combination of attributes within small groups."),
        ("answer q7", "grammar_wording", "moderate", "الأول حذف معرفًا مباشرًا is malformed; define the first concept with يعني حذف معرّف مباشر."),
        ("answer q8", "naturalness_idiomaticity", "moderate", "تقدم معرفة خارجية كشرط يزيد قدرة التعرف is a calque; state directly that outside knowledge can increase the possibility of identification."),
    ],
    "ar-b2-u06-p05": [
        ("answer q2", "grammar_wording", "moderate", "احتفاظ طويل omits what is retained and makes the three-option list structurally uneven; name retention of the link for a longer period."),
        ("answer q6", "naturalness_idiomaticity", "moderate", "تستبدل تخزينًا مفتوح الغرض is an awkward construction; state that the policy rejects open-ended link retention and requires a new decision for a later research question."),
    ],
    "ar-b2-u06-p06": [
        ("text", "naturalness_idiomaticity", "moderate", "مشاركة تقدم الطالب مع معلمه is an awkward collocation; the service shares information about the student's progress with the teacher."),
        ("text", "grammar_wording", "moderate", "قد يكون استخدام مقبولًا اليوم أوسع غدًا is malformed comparative wording; state that an accepted use may become broader in scope later."),
        ("answer q5", "grammar_wording", "moderate", "حدود متغيرة على تدفق المعلومات is incomplete/awkward; define privacy as changing boundaries that regulate information flow, use, and inference."),
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
    if [rows[i].get("id") for i in range(30, 36)] != EXPECTED_IDS:
        raise SystemExit("B2 Unit 6 id/frontier drift")

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
    if total_findings != 16 or records_with_findings != 5:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")

    PATH.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({
        "level": "B2", "unit": 6, "records_reviewed": 6,
        "records_with_findings": records_with_findings, "fresh_findings": total_findings,
        "pre_repair_canonical_sha256": pre_sha,
        "post_repair_canonical_sha256": sha(PATH.read_bytes()),
        "word_counts": {pid: by_id[pid]["word_count"] for pid in EXPECTED_IDS},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
