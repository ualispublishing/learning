#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 1 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
INVENTORY = READING / "audit/arabic_gate_b_naturalness_inventory_2026-08-30.json"
RELEASE = READING / "RELEASE_STATUS.json"
DECISION_DIR = READING / "audit/arabic_gate_b_decisions_2026-08-30"
EXPECTED_IDS = [f"ar-b2-u01-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-03 fresh Gate B naturalness review (B2 Unit 1): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, and "
    "assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u01-p02": [
        (
            "كما أن بعض أنواع الحشرات الملونة جذبت التصوير أكثر من الأنواع الصغيرة أو التي تظهر ليلًا.",
            "كما أن بعض أنواع الحشرات الملونة دفعت المشاركين إلى تصويرها أكثر من الأنواع الصغيرة أو التي تظهر ليلًا.",
        ),
        (
            "وفي الثانية حددت ساعات مراقبة ثابتة ومسارًا قصيرًا يسلكه المتطوع حتى إذا لم ير حشرة واحدة.",
            "وفي الثانية حددت ساعات مراقبة ثابتة ومسارًا قصيرًا يسلكه المتطوع حتى إن لم ير حشرة واحدة.",
        ),
    ],
    "ar-b2-u01-p03": [
        (
            "اقترح عضو في اللجنة إعطاء التمويل للمشروعين اللذين يتوقعان أكبر نتيجة مباشرة.",
            "اقترح عضو في اللجنة إعطاء التمويل للمشروعين اللذين يتوقعان أكبر أثر مباشر.",
        ),
        (
            "إمكانية التعلم حتى إذا لم تنجح الفرضية",
            "إمكانية التعلم حتى إن لم تنجح الفرضية",
        ),
    ],
    "ar-b2-u01-p04": [
        (
            "ما مقدار الاستعداد المعقول عندما توجد إمكانية لنتيجة كبيرة لكن الأدلة على احتمالها محدودة؟",
            "ما مقدار الاستعداد المعقول عندما توجد إمكانية لوقوع نتيجة كبيرة لكن الأدلة على احتمالها محدودة؟",
        ),
    ],
    "ar-b2-u01-p05": [
        (
            "إذا كانت البيانات تتضمن معلومات حساسة أو خطرًا على المشاركين، فلا تكون الشفافية مساوية لكشف كل مادة خام للجمهور.",
            "إذا كانت البيانات تتضمن معلومات حساسة أو كان نشرها يشكل خطرًا على المشاركين، فلا تكون الشفافية مساوية لكشف كل مادة خام للجمهور.",
        ),
    ],
    "ar-b2-u01-p06": [
        (
            "وعند الحديث عن الخطر يجب جمع إمكانية الحدث مع حجم أثره وتكلفة الاستعداد له.",
            "وعند الحديث عن الخطر يجب الجمع بين إمكانية وقوع الحدث وحجم أثره وتكلفة الاستعداد له.",
        ),
        (
            "ثم طلبت تمويلًا إضافيًا لأن البيانات المفتوحة أظهرت احتمال خطر في منطقة معينة.",
            "ثم طلبت تمويلًا إضافيًا لأن البيانات المفتوحة أشارت إلى احتمال وجود خطر في منطقة معينة.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u01-p01": {
        "answers": {
            "q6": (
                "تقدم حدًا لفكرة أن إضافة التفاصيل تحسن النموذج دائمًا، وتبين أن التعقيد الزائد قد يضعف القدرة على تفسير النتيجة.",
                "تبرز «لكن» قيدًا على فكرة أن إضافة التفاصيل تحسن النموذج دائمًا، وتبين أن التعقيد الزائد قد يضعف القدرة على تفسير النتيجة.",
            ),
        }
    },
    "ar-b2-u01-p02": {
        "answers": {
            "q5": (
                "يستخدم البيانات المفتوحة للاكتشاف وتوليد الأسئلة، ويستخدم المراقبة المنظمة للمقارنة بين مواقع وأوقات معروفة الفرص والرصد.",
                "يستخدم الفريق البيانات المفتوحة للاكتشاف وتوليد الأسئلة، ويستخدم المراقبة المنظمة للمقارنة بين مواقع وأوقات تكون فيها فرص الرصد معروفة.",
            ),
        },
        "questions": {
            "q8": (
                "ما وظيفة «حتى إذا» في تسجيل المسار ولو لم ير المتطوع حشرة واحدة؟",
                "ما وظيفة «حتى إن» في تسجيل المسار ولو لم ير المتطوع حشرة واحدة؟",
            ),
        },
    },
    "ar-b2-u01-p03": {
        "answers": {
            "q6": (
                "تقيم مفارقة مقصودة: ثبات الدليل العلمي لا يمنع تغير القرار عندما تتغير الموارد أو البدائل.",
                "تبرز مفارقة مقصودة: ثبات الدليل العلمي لا يمنع تغير القرار عندما تتغير الموارد أو البدائل.",
            ),
        },
    },
    "ar-b2-u01-p04": {
        "answers": {
            "q4": (
                "ينتقل من اختيار نص إلى سؤال أدق عن مقدار الاستعداد تحت احتمال غير مؤكد وأثر كبير.",
                "ينتقل من اختيار نص إلى سؤال أدق عن مقدار الاستعداد في ظل احتمال غير مؤكد وأثر كبير.",
            ),
            "q6": (
                "تبرز اختلاف قابلية الرجوع عن القرارات، فتضيف بعدًا عمليًا إلى مقارنة المخاطر والتكاليف.",
                "تبرز اختلاف القرارات في قابلية التراجع عنها، فتضيف بعدًا عمليًا إلى مقارنة المخاطر والتكاليف.",
            ),
        },
    },
    "ar-b2-u01-p05": {
        "answers": {
            "q1": (
                "هل تعني نشر النتيجة الأولية فورًا أم يمكن تأخيرها قليلًا حتى توضح حالتها وتفحص الأخطاء.",
                "هل تعني نشر النتيجة الأولية فورًا، أم يمكن تأخيرها قليلًا حتى يوضح الفريق حالتها ويفحص الأخطاء المحتملة؟",
            ),
        },
        "questions": {
            "q8": (
                "إلى ماذا تشير «المبدأ الذي حاولوا حمايته»؟",
                "إلى ماذا يشير «المبدأ الذي حاولوا حمايته»؟",
            ),
        },
    },
    "ar-b2-u01-p06": {
        "questions": {
            "q10": (
                "لماذا لا يعد الاعتراف ببداية «الاختيار» هزيمة للعلم؟",
                "لماذا لا يعد الاعتراف بالنقطة التي يبدأ عندها «الاختيار» هزيمة للعلم؟",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u01-p01": [
        (
            "answer q6",
            "grammar_function_wording",
            "minor",
            "Replace the unnatural تقدم حدًا wording with an explicit, idiomatic description of لكن as introducing a constraint on the preceding claim.",
        ),
    ],
    "ar-b2-u01-p02": [
        (
            "text",
            "naturalness_idiomaticity",
            "minor",
            "الحشرات ... جذبت التصوير is an unnatural collocation; state that the colorful insects prompted participants to photograph them more often.",
        ),
        (
            "answer q5",
            "naturalness_idiomaticity",
            "moderate",
            "معروفة الفرص والرصد is malformed; state directly that organized monitoring uses sites and times where observation opportunities are known.",
        ),
        (
            "text + question q8",
            "grammar_wording",
            "moderate",
            "The intended concessive meaning is ‘even if’; in this context حتى إن is appropriate, whereas حتى إذا normally introduces a when/until-when relation. Keep the assessment wording aligned with the repaired text.",
        ),
    ],
    "ar-b2-u01-p03": [
        (
            "text",
            "naturalness_idiomaticity",
            "minor",
            "أكبر نتيجة مباشرة is an awkward collocation for project impact; أكبر أثر مباشر expresses the intended comparison naturally.",
        ),
        (
            "text",
            "grammar_wording",
            "moderate",
            "The intended concessive meaning is ‘even if the hypothesis does not succeed’; use حتى إن rather than حتى إذا.",
        ),
        (
            "answer q6",
            "grammar_function_wording",
            "minor",
            "مع أن highlights a concession/contrast; تبرز مفارقة is idiomatic here, while تقيم مفارقة is not the natural collocation.",
        ),
    ],
    "ar-b2-u01-p04": [
        (
            "text",
            "naturalness_idiomaticity",
            "minor",
            "إمكانية لنتيجة is incomplete in this context; إضافة وقوع yields the natural construction إمكانية لوقوع نتيجة كبيرة while preserving the lexical target.",
        ),
        (
            "answer q4",
            "naturalness_idiomaticity",
            "minor",
            "Use the idiomatic في ظل احتمال غير مؤكد rather than تحت احتمال غير مؤكد.",
        ),
        (
            "answer q6",
            "naturalness_idiomaticity",
            "minor",
            "Recast اختلاف قابلية الرجوع عن القرارات as اختلاف القرارات في قابلية التراجع عنها for clearer standard MSA.",
        ),
    ],
    "ar-b2-u01-p05": [
        (
            "answer q1",
            "grammar_reference",
            "moderate",
            "The old coordination leaves the feminine result as the apparent subject of ‘examines the errors’; make the team the explicit subject of both actions.",
        ),
        (
            "question q8",
            "grammar_wording",
            "moderate",
            "The referent المبدأ is masculine, so the reference-resolution question must use يشير, not تشير.",
        ),
        (
            "text",
            "semantic_precision",
            "moderate",
            "Data can contain sensitive information, but the risk to participants arises from publication/disclosure; state that publishing the data may pose the risk instead of saying the data ‘contain a risk.’",
        ),
    ],
    "ar-b2-u01-p06": [
        (
            "text",
            "naturalness_idiomaticity",
            "minor",
            "Use the standard الجمع بين ... و... construction and clarify إمكانية وقوع الحدث while preserving the target concept.",
        ),
        (
            "text",
            "naturalness_idiomaticity",
            "minor",
            "أظهرت احتمال خطر is awkward; أشارت إلى احتمال وجود خطر is idiomatic and retains the intended evidential caution.",
        ),
        (
            "question q10",
            "assessment_clarity",
            "moderate",
            "بداية الاختيار is ambiguous; ask about recognizing the point at which choice begins, which is the distinction developed in the passage.",
        ),
    ],
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wc(text: str) -> int:
    return len(TOKEN.findall(text))


def target_counts(record: dict) -> dict[str, int]:
    text = str(record.get("text", "")).casefold()
    out: dict[str, int] = {}
    for target in record.get("new_lexical_targets", []):
        form = str(target.get("form", "")).strip()
        if not form:
            raise SystemExit(f"{record['id']}: blank target")
        out[str(target.get("id", form))] = text.count(form.casefold())
    return out


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected literal once, found {count}: {old}")
    return text.replace(old, new, 1)


def main() -> None:
    raw = PATH.read_bytes()
    actual = sha(raw)
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    b2 = inventory.get("levels", {}).get("b2", {})
    bound = b2.get("canonical_sha256")
    if not isinstance(bound, str) or len(bound) != 64 or actual != bound:
        raise SystemExit(
            f"B2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 1 review"
        )

    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    arabic = release.get("languages", {}).get("arabic", {})
    progress = arabic.get("naturalness_review_progress", {})
    if (
        arabic.get("release_state") != "REOPEN_REQUIRED"
        or arabic.get("educator_release_ready") is not False
        or progress.get("fresh_records_reviewed") != 180
        or progress.get("levels_completed") != ["A1", "A2", "B1"]
    ):
        raise SystemExit(
            "Arabic Gate B frontier drift: expected 180 reviewed with A1/A2/B1 complete and B2 Unit 1 next"
        )
    if not (DECISION_DIR / "b1_u10.json").exists() or (DECISION_DIR / "b2_u01.json").exists():
        raise SystemExit("B2 decision frontier drift: B1 Unit 10 must exist and B2 Unit 1 must not")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if (
        len(rows) != 60
        or [row.get("sequence") for row in rows] != list(range(1, 61))
        or [rows[i].get("id") for i in range(0, 6)] != EXPECTED_IDS
    ):
        raise SystemExit("B2 Unit 1 layout/id drift")

    by_id = {row["id"]: row for row in rows}
    before_targets = {pid: target_counts(by_id[pid]) for pid in EXPECTED_IDS}

    for pid in EXPECTED_IDS:
        record = by_id[pid]
        text = record["text"]
        for old, new in TEXT_REPAIRS.get(pid, []):
            text = replace_once(text, old, new, f"{pid} text")
        record["text"] = text

        questions = {q["id"]: q for q in record.get("questions", [])}
        answers = {a["question_id"]: a for a in record.get("answer_key", [])}
        edits = QA_REPAIRS.get(pid, {})
        for qid, (old, new) in edits.get("questions", {}).items():
            if questions[qid].get("prompt") != old:
                raise SystemExit(
                    f"{pid}/{qid}: question drift: {questions[qid].get('prompt')!r}"
                )
            questions[qid]["prompt"] = new
        for qid, (old, new) in edits.get("answers", {}).items():
            if answers[qid].get("answer") != old:
                raise SystemExit(
                    f"{pid}/{qid}: answer drift: {answers[qid].get('answer')!r}"
                )
            answers[qid]["answer"] = new

        record["word_count"] = wc(record["text"])
        if not 350 <= record["word_count"] <= 550:
            raise SystemExit(f"{pid}: word count {record['word_count']} outside B2 band")
        if target_counts(record) != before_targets[pid]:
            raise SystemExit(f"{pid}: lexical target occurrence drift")
        if len(record.get("questions", [])) != 10 or len(record.get("answer_key", [])) != 10:
            raise SystemExit(f"{pid}: 10Q/10A invariant failed")
        answers_by_id = {a["id"]: a for a in record["answer_key"]}
        for question in record["questions"]:
            answer = answers_by_id.get(question.get("answer_id"))
            if not answer or answer.get("question_id") != question.get("id"):
                raise SystemExit(f"{pid}/{question.get('id')}: answer linkage drift")

        record["revision"] = int(record.get("revision", 0) or 0) + 1
        quality = record.setdefault("quality", {})
        if quality.get("status") != "draft" or quality.get("coverage_check") != "pending":
            raise SystemExit(f"{pid}: unexpected release/coverage state")
        for field in ("linguistic_review", "pedagogical_review", "answer_key_check", "schema_check"):
            quality[field] = "pass"
        if NOTE not in quality.setdefault("notes", []):
            quality["notes"].append(NOTE)

    total_findings = sum(len(FINDING_META[pid]) for pid in EXPECTED_IDS)
    records_with_findings = sum(bool(FINDING_META[pid]) for pid in EXPECTED_IDS)
    if total_findings != 16 or records_with_findings != 6:
        raise SystemExit(
            f"finding metadata drift: findings={total_findings}, records={records_with_findings}"
        )

    PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "level": "B2",
                "unit": 1,
                "records_reviewed": 6,
                "records_with_findings": records_with_findings,
                "fresh_findings": total_findings,
                "pre_repair_canonical_sha256": actual,
                "post_repair_canonical_sha256": sha(PATH.read_bytes()),
                "word_counts": {pid: by_id[pid]["word_count"] for pid in EXPECTED_IDS},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
