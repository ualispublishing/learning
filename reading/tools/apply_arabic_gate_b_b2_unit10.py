#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 10 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
EXPECTED_IDS = [f"ar-b2-u10-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (B2 Unit 10): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u10-p02": [
        (
            "أعادت نور صياغة التوتر: معيار واحد واضح قد يكون سهل التطبيق لكنه قابل للتحسين على حساب الهدف، ومعايير كثيرة قد تلتقط الهدف أفضل لكنها تزيد التكلفة والاختلاف في الحكم.",
            "أعادت نور صياغة التوتر: معيار واحد واضح قد يكون سهل التطبيق لكنه قابل للتحسين على حساب الهدف، ومعايير كثيرة قد تعكس الهدف بصورة أفضل لكنها تزيد التكلفة والاختلاف في الحكم.",
        ),
        (
            "كما دربت المراجعين على أمثلة مشتركة وقارنت أحكامهم حتى لا تتحول دقة القياس إلى اختلاف غير مرئي بين الأشخاص.",
            "كما دربت المراجعين على أمثلة مشتركة وقارنت أحكامهم حتى لا يصبح اختلاف المراجعين مصدرًا خفيًا يضعف دقة القياس.",
        ),
        (
            "قالت نور إن القاعدة الجيدة قد تفسد إذا نجح الناس في تحسين المؤشر من دون تحسين الهدف. ولهذا فالمراجعة ليست اتهامًا للمستخدمين؛ هي اعتراف بأن أي آلية حافز تغير البيئة التي تحاول قياسها.",
            "قالت نور إن القاعدة الجيدة قد تفسد إذا نجح الناس في تحسين المؤشر من دون تحسين الهدف. ولهذا فالمراجعة ليست اتهامًا للمستخدمين؛ هي اعتراف بأن أي آلية للحوافز تغير البيئة التي تحاول قياسها.",
        ),
    ],
    "ar-b2-u10-p03": [
        (
            "التصميم المتين ليس الذي يتنبأ بكل شيء، بل الذي لا ينهار عندما يكون بعض التنبؤ خطأ.",
            "التصميم المتين ليس الذي يتنبأ بكل شيء، بل الذي لا ينهار عندما تخطئ بعض التوقعات.",
        ),
    ],
    "ar-b2-u10-p05": [
        (
            "الوثائق التاريخية تستطيع أن تخبرنا أن سجلات بعض الفئات أقل بقاء، ويمكن للمؤرخ استخدام أدلة غير مباشرة لتقدير نشاطهم.",
            "الوثائق التاريخية تستطيع أن تخبرنا أن سجلات بعض الفئات أقل احتمالًا للبقاء، ويمكن للمؤرخ استخدام أدلة غير مباشرة لتقدير نشاطهم.",
        ),
        (
            "هذا لا يجعلها أقل قيمة؛ يمكن أن تجعل الزائر يشعر بالفجوة ويسأل من لم يكتب التاريخ.",
            "هذا لا يجعلها أقل قيمة؛ يمكن أن تجعل الزائر يشعر بالفجوة ويتساءل عمن لم يكتب التاريخ.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u10-p02": {
        "answers": {
            "q1": (
                "تتكيف الفرق لزيادة الرقم بطرق لا تزيد بالضرورة جودة أو معنى المشاركة.",
                "تتكيف الفرق لزيادة الرقم بطرق لا تحسن بالضرورة جودة المشاركة أو معناها.",
            ),
        },
    },
    "ar-b2-u10-p04": {
        "answers": {
            "q2": (
                "توسيع دقة الموقع بعد الاختيار، إحصاء مجمع محدود المدة، وموافقة منفصلة للتحليل التفصيلي.",
                "تقليل دقة الموقع بعد الاختيار، إحصاء مجمع محدود المدة، وموافقة منفصلة للتحليل التفصيلي.",
            ),
            "q5": (
                "جمع أقل قدر من التفصيل والمدة اللازمة لقرار أو غرض معلن.",
                "جمع أقل قدر لازم من التفاصيل، والاحتفاظ بها لأقصر مدة لازمة، لغرض أو قرار معلن.",
            ),
        },
    },
    "ar-b2-u10-p05": {
        "answers": {
            "q1": (
                "تجعل تمثيلًا فنيًا معاصرًا يبدو كأنه صوت تاريخي مباشر لمن لم تترك أصواتهم سجلات كافية.",
                "تجعل تمثيلًا فنيًا معاصرًا يبدو كأنه صوت تاريخي مباشر لأشخاص لا تتوافر من أصواتهم سجلات تاريخية كافية.",
            ),
            "q6": (
                "سجل أو مادة من سياق الدراسة تستخدم بوصفها دليلًا تاريخيًا ضمن حدود منشئها وبقائها.",
                "سجل أو مادة من سياق الدراسة تستخدم بوصفها دليلًا تاريخيًا ضمن حدود طريقة إنشائها وبقائها.",
            ),
        },
    },
    "ar-b2-u10-p06": {
        "answers": {
            "q5": (
                "الحفاظ على بنية الحجة وحدودها بما يسمح بموافقة أو اعتراض أو تعليق حكم مبرر.",
                "الحفاظ على بنية الحجة وحدودها بما يسمح بالموافقة أو الاعتراض أو تعليق الحكم على نحو مبرر.",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u10-p01": [],
    "ar-b2-u10-p02": [
        ("text", "naturalness_idiomaticity", "moderate", "تلتقط الهدف أفضل is a calque-like comparative; state that multiple criteria may represent the goal more faithfully."),
        ("text", "semantic_precision", "moderate", "دقة القياس لا تتحول إلى اختلاف بين الأشخاص; the actual risk is hidden reviewer variation becoming a source of measurement error."),
        ("text", "naturalness_idiomaticity", "minor", "آلية حافز is an awkward policy collocation; use آلية للحوافز."),
        ("answer q1", "grammar_wording", "moderate", "لا تزيد ... جودة أو معنى المشاركة has faulty valency/coordination; use لا تحسن ... جودة المشاركة أو معناها."),
    ],
    "ar-b2-u10-p03": [
        ("text", "grammar_wording", "moderate", "يكون بعض التنبؤ خطأ is malformed; express that some expectations may turn out to be wrong."),
    ],
    "ar-b2-u10-p04": [
        ("answer q2", "semantic_precision", "moderate", "توسيع دقة الموقع reverses the privacy operation described in the passage; broadening the location reduces precision."),
        ("answer q5", "grammar_wording", "moderate", "أقل قدر من التفصيل والمدة اللازمة incorrectly coordinates detail and duration under one quantity phrase; state minimum necessary detail and shortest necessary retention separately."),
    ],
    "ar-b2-u10-p05": [
        ("text", "naturalness_idiomaticity", "moderate", "سجلات بعض الفئات أقل بقاء is not idiomatic for archival survival probability; use أقل احتمالًا للبقاء."),
        ("text", "reference_clarity", "moderate", "يسأل من لم يكتب التاريخ reads as asking a person; the intended meaning is wondering who did not get to write history."),
        ("answer q1", "semantic_precision", "moderate", "أصواتهم لا تترك سجلات literally; state that insufficient historical records of those voices are available."),
        ("answer q6", "reference_clarity", "minor", "حدود منشئها is ambiguous between creator and creation; specify limits imposed by how the source was created and preserved."),
    ],
    "ar-b2-u10-p06": [
        ("answer q5", "grammar_wording", "moderate", "تعليق حكم مبرر can mean suspending an already justified judgment; the intended claim is that agreement, objection, or suspension of judgment should itself be justified."),
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
    if [rows[i].get("id") for i in range(54, 60)] != EXPECTED_IDS:
        raise SystemExit("B2 Unit 10 id/frontier drift")

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
    if total_findings != 12 or records_with_findings != 5:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")
    PATH.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"level":"B2","unit":10,"records_reviewed":6,"records_with_findings":records_with_findings,"fresh_findings":total_findings,"pre_repair_canonical_sha256":pre_sha,"post_repair_canonical_sha256":sha(PATH.read_bytes())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
