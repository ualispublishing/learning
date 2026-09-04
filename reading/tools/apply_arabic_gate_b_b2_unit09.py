#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 9 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
EXPECTED_IDS = [f"ar-b2-u09-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (B2 Unit 9): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u09-p01": [
        (
            "ثم تأتي مرحلة تحويل الاقتراح إلى بند يمكن تطبيقه وعقوبته ومراجعته.",
            "ثم تأتي مرحلة تحويل الاقتراح إلى بند يمكن تطبيقه وإنفاذه ومراجعته.",
        ),
        (
            "كل خطوة ترجمة بين لغة مختلفة: الباحث يسأل ما الذي يحدث، وصانع التوصية يسأل ما الذي قد يساعد، وكاتب البند يحدد من يلزم بماذا ومتى.",
            "كل خطوة ترجمة إلى لغة مختلفة: الباحث يسأل ما الذي يحدث، وصانع التوصية يسأل ما الذي قد يساعد، وكاتب البند يحدد من يلزم بماذا ومتى.",
        ),
    ],
    "ar-b2-u09-p02": [
        (
            "في الأول كان معظم الطلبات يعالج في الوقت المطلوب، وفي الثاني تراكم التأخير، وفي الثالث كان المواطنون يعيدون إرسال الطلبات لأن الإرشادات غير واضحة.",
            "في الأول كانت معظم الطلبات تُعالج في الوقت المطلوب، وفي الثاني تراكم التأخير، وفي الثالث كان المواطنون يعيدون إرسال الطلبات لأن الإرشادات غير واضحة.",
        ),
        (
            "عندها أصبح من المعقول سؤال هل الهدف الزمني نفسه واقعي وفاعل في تحسين الخدمة أم أنه يفرض معيارًا لا تعكسه القدرة المتاحة.",
            "عندها أصبح من المعقول أن نسأل هل الهدف الزمني نفسه واقعي وفاعل في تحسين الخدمة أم أنه يفرض معيارًا لا تعكسه القدرة المتاحة.",
        ),
    ],
    "ar-b2-u09-p04": [
        (
            "لم يكن التعويض مالًا، بل تعديلًا يحقق تقليل العبء على طرف محدد من دون إزالة الهدف الأساسي.",
            "لم يكن التعويض مالًا، بل تعديلًا يحقق تقليلًا للعبء على طرف محدد من دون إزالة الهدف الأساسي.",
        ),
        (
            "ناقشت اللجنة كذلك من يتحمل كلفة التعديل؛ فتح المدخل الجانبي يحتاج إلى تنظيم صغير تدفعه المدينة، بينما يلتزم المتجر بموعد محدد.",
            "ناقشت اللجنة كذلك من يتحمل كلفة التعديل؛ فتح المدخل الجانبي يحتاج إلى تعديل بسيط تتحمل المدينة تكلفته، بينما يلتزم المتجر بموعد محدد.",
        ),
        (
            "اعتبروا هذا نوعًا من تعويض موزع بين الطرفين.",
            "اعتبروا هذا نوعًا من التعويض الموزع بين الطرفين.",
        ),
    ],
    "ar-b2-u09-p05": [
        (
            "التدريب قد يفتح خيارات أطول، مثل اكتساب مهارة أو الوصول إلى وظيفة تسمح بترقية لاحقة، لكنه لا يضمن نتيجة لكل شخص ويحتاج إلى وقت قبل أن يظهر أثره.",
            "التدريب قد يفتح خيارات طويلة الأمد، مثل اكتساب مهارة أو الوصول إلى وظيفة تسمح بترقية لاحقة، لكنه لا يضمن نتيجة لكل شخص ويحتاج إلى وقت قبل أن يظهر أثره.",
        ),
        (
            "صمم الفريق مسارًا يجمع حدًا من المساعدة المباشرة مع خيارات تدريب مختلفة، ثم قاس نتيجتين: الاستقرار القصير وقدرة المشاركين على الوصول إلى فرص جديدة بعد مدة.",
            "صمم الفريق مسارًا يجمع حدًا من المساعدة المباشرة مع خيارات تدريب مختلفة، ثم قاس نتيجتين: الاستقرار قصير المدى وقدرة المشاركين على الوصول إلى فرص جديدة بعد مدة.",
        ),
        (
            "وجدوا أن النقل أو التوقيت يمثل عائقًا في بعض الحالات، فقدموا خيارات أبعد عن المسار الموحد.",
            "وجدوا أن النقل أو التوقيت يمثل عائقًا في بعض الحالات، فقدموا خيارات تبتعد عن المسار الموحد.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u09-p01": {
        "answers": {
            "q8": (
                "تقدم ظهور الأثر كشرط يعيد فتح المرحلة المناسبة بدل نسبة المشكلة إلى سلسلة القرار كلها.",
                "تجعل ظهور الأثر شرطًا يعيد فتح المرحلة المناسبة بدل نسبة المشكلة إلى سلسلة القرار كلها.",
            ),
        },
    },
    "ar-b2-u09-p05": {
        "answers": {
            "q2": (
                "الاستقرار القصير والوصول إلى فرص جديدة بعد مدة.",
                "الاستقرار قصير المدى والوصول إلى فرص جديدة بعد مدة.",
            ),
            "q5": (
                "يتابع الدعم والاستقرار والتدريب والأجر وساعات العمل والقدرة على تغيير الوظيفة، ويميز الاختيار من عوائق الوصول بدل فرض مسار واحد.",
                "يتابع الدعم والاستقرار والتدريب والأجر وساعات العمل والقدرة على تغيير الوظيفة، ويميز بين الاختيار وعوائق الوصول بدل فرض مسار واحد.",
            ),
        },
    },
    "ar-b2-u09-p06": {
        "questions": {
            "q8": (
                "ما وظيفة تسجيل ما الذي سيجعل نور تقترح تعديل القاعدة بدل تعديل التنفيذ مسبقًا؟",
                "ما فائدة أن تسجل نور مسبقًا ما الذي سيجعلها تقترح تعديل القاعدة بدل تعديل التنفيذ؟",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u09-p01": [
        ("text", "grammar_wording", "moderate", "وعقوبته makes the provision itself the object of punishment; use إنفاذه for the binding-rule stage."),
        ("text", "grammar_wording", "minor", "ترجمة بين لغة مختلفة has the wrong prepositional relation; each stage is a translation into a different language/register."),
        ("answer q8", "naturalness_idiomaticity", "minor", "تقدم ظهور الأثر كشرط is a calque-like formulation; state directly that إذا makes appearance of the effect a condition for reopening the relevant stage."),
    ],
    "ar-b2-u09-p02": [
        ("text", "grammar_wording", "moderate", "كان معظم الطلبات يعالج has broken agreement; use كانت معظم الطلبات تُعالج."),
        ("text", "grammar_wording", "minor", "أصبح من المعقول سؤال هل is malformed; use أصبح من المعقول أن نسأل هل."),
    ],
    "ar-b2-u09-p03": [],
    "ar-b2-u09-p04": [
        ("text", "naturalness_idiomaticity", "minor", "يحقق تقليل العبء needs the governed masdar construction تقليلًا للعبء."),
        ("text", "semantic_precision", "moderate", "تنظيم صغير تدفعه المدينة is unclear and makes the city 'pay' an organization; state that the side entrance requires a small modification whose cost the city bears."),
        ("text", "grammar_wording", "minor", "نوعًا من تعويض موزع is an awkward indefinite construction; use نوعًا من التعويض الموزع."),
    ],
    "ar-b2-u09-p05": [
        ("text", "naturalness_idiomaticity", "minor", "خيارات أطول is not idiomatic for durable future options; use خيارات طويلة الأمد."),
        ("text", "naturalness_idiomaticity", "minor", "الاستقرار القصير is an awkward duration label; use الاستقرار قصير المدى."),
        ("text", "naturalness_idiomaticity", "moderate", "خيارات أبعد عن المسار الموحد is spatially calqued; use خيارات تبتعد عن المسار الموحد."),
        ("answer q2", "naturalness_idiomaticity", "minor", "The answer repeats الاستقرار القصير; use الاستقرار قصير المدى."),
        ("answer q5", "grammar_wording", "moderate", "يميز الاختيار من عوائق الوصول has the wrong coordination; use يميز بين الاختيار وعوائق الوصول."),
    ],
    "ar-b2-u09-p06": [
        ("question q8", "assessment_wording", "moderate", "ما وظيفة تسجيل ما الذي سيجعل... is syntactically heavy and unclear; ask directly about the benefit of recording the revision trigger in advance."),
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
    if [rows[i].get("id") for i in range(48, 54)] != EXPECTED_IDS:
        raise SystemExit("B2 Unit 9 id/frontier drift")

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
                raise SystemExit(f"{pid}/{qid}: answer drift")
            answers[qid]["answer"] = new

        record["word_count"] = wc(record["text"])
        if not 350 <= record["word_count"] <= 550:
            raise SystemExit(f"{pid}: word count {record['word_count']} outside B2 band")
        if target_counts(record) != before_targets[pid]:
            raise SystemExit(f"{pid}: lexical target occurrence drift")
        if len(record.get("questions", [])) != 10 or len(record.get("answer_key", [])) != 10:
            raise SystemExit(f"{pid}: 10Q/10A invariant failed")
        answers_by_id = {a["id"]: a for a in record["answer_key"]}
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
    if total_findings != 14 or records_with_findings != 5:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")
    PATH.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"level":"B2","unit":9,"records_reviewed":6,"records_with_findings":records_with_findings,"fresh_findings":total_findings,"pre_repair_canonical_sha256":pre_sha,"post_repair_canonical_sha256":sha(PATH.read_bytes())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
