#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 3 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/c1/passages.jsonl"
RELEASE = READING / "RELEASE_STATUS.json"
INVENTORY = READING / "audit/arabic_gate_b_naturalness_inventory_2026-08-30.json"
DECISION_DIR = READING / "audit/arabic_gate_b_decisions_2026-08-30"
EXPECTED_IDS = [f"ar-c1-u03-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (C1 Unit 3): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-c1-u03-p01": [
        (
            "حافظ المؤشر على وتيرة عالية، لكن معنى الإغلاق تغير.",
            "بقيت وتيرة المؤشر مرتفعة، لكن معنى الإغلاق تغير.",
        ),
    ],
    "ar-c1-u03-p04": [
        (
            "قاعدة الحجز الجديدة نافعت المستخدمين المنتظمين لكنها صعبت الوصول على مجموعات تستخدم المكان بصورة غير متكررة.",
            "قاعدة الحجز الجديدة أفادت المستخدمين المنتظمين لكنها صعّبت وصول مجموعات تستخدم المكان بصورة غير متكررة.",
        ),
    ],
    "ar-c1-u03-p06": [
        (
            "عندما يتحول رقم إلى عتبة للمكافأة قد تتغير وتيرة العمل حول الرقم.",
            "عندما يتحول رقم إلى عتبة للمكافأة قد تتغير وتيرة العمل استجابةً لهذا الرقم.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-c1-u03-p01": {
        "answers": {
            "q5": (
                "تقارن الفترات قبل الحافز وبعده، وتفصل زمن الرد عن الحل والعودة وجودة العينة، وتراقب تغير العلاقة بين الرقم والنتائج الأخرى مع تكيف الفرق.",
                "تقارن الفترات قبل الحافز وبعده، وتفصل زمن الرد عن زمن الحل وإعادة فتح الحالات وجودة عينة المراجعة، وتراقب تغير العلاقة بين الرقم والنتائج الأخرى مع تكيف الفرق.",
            ),
        },
    },
    "ar-c1-u03-p02": {
        "answers": {
            "q5": (
                "تقيس الطلب بعد اكتمال الملفات والإلغاء والانتظار، وتجرب قواعد إعادة التوزيع والمعلومات، ثم تفصل نقص القدرة عن الوقت المهدور والطلب الوقائي.",
                "تقيس الطلب بعد اكتمال الملفات، والإلغاءات، وأوقات الانتظار، وتجرب قواعد إعادة التوزيع والمعلومات، ثم تفصل نقص القدرة عن الوقت المهدور والطلب الوقائي.",
            ),
        },
    },
    "ar-c1-u03-p03": {
        "answers": {
            "q4": (
                "كشف الأنماط النظامية من دون إلغاء مساحة الحكم أو معاملة كل استثناء كاتهام.",
                "كشف الأنماط المتكررة من دون إلغاء مساحة الحكم أو معاملة كل استثناء كاتهام.",
            ),
            "q5": (
                "تستخدم علامات متعددة للمراجعة وتناسب التدقيق مع الأثر، وتوضح أسباب القرار، وتسجل أنماط التكيف لتعرف متى ينبغي إصلاح المسار الأساسي نفسه.",
                "تستخدم علامات متعددة للمراجعة وتجعل التدقيق متناسبًا مع الأثر، وتوضح أسباب القرار، وتسجل أنماط التكيف لتعرف متى ينبغي إصلاح المسار الأساسي نفسه.",
            ),
        },
    },
    "ar-c1-u03-p04": {
        "answers": {
            "q5": (
                "تربط المدخلات بقرارات وأسباب معلنة، وتنوي قنوات الوصول، وتستخدم تجارب موجهة، ثم تدخل خبرة المتأثرين في تعريف المؤشرات وتفسير النتائج.",
                "تربط المدخلات بقرارات وأسباب معلنة، وتنوّع قنوات الوصول، وتستخدم تجارب موجهة، ثم تدخل خبرة المتأثرين في تعريف المؤشرات وتفسير النتائج.",
            ),
        },
    },
    "ar-c1-u03-p05": {
        "answers": {
            "q1": (
                "ربط التمويل بعدد الساعات جعل النشاط المسجل أكثر جاذبية من النتيجة الأصلية.",
                "ربط التمويل بعدد الساعات جعل النشاط المسجل أكثر جاذبية من تحقيق الغاية الأصلية.",
            ),
            "q5": (
                "يعيد تاريخ كل مقياس من التخطيط إلى التقييم ثم الحافز، ويفصل النشاط عن النتيجة، ويعيد تصميم التمويل والمراجعة حول الغاية الأصلية.",
                "يعيد بناء تاريخ كل مقياس من التخطيط إلى التقييم ثم الحافز، ويفصل النشاط عن النتيجة، ويعيد تصميم التمويل والمراجعة حول الغاية الأصلية.",
            ),
        },
    },
}

FINDING_META = {
    "ar-c1-u03-p01": [
        ("text", "naturalness_idiomaticity", "moderate", "حافظ المؤشر على وتيرة عالية assigns pace directly to the indicator in an awkward way; retain the lexical target وتيرة while making it the head of the construction."),
        ("answer q5", "semantic_precision", "moderate", "الحل والعودة وجودة العينة compresses three distinct checks into ambiguous nouns; name solution time, case reopening, and review-sample quality explicitly."),
    ],
    "ar-c1-u03-p02": [
        ("answer q5", "grammar_wording", "moderate", "الطلب بعد اكتمال الملفات والإلغاء والانتظار uses mismatched abstract nouns; use parallel references to completed files, cancellations, and waiting times."),
    ],
    "ar-c1-u03-p03": [
        ("answer q4", "semantic_precision", "moderate", "الأنماط النظامية is ambiguous here; the report is meant to reveal recurring patterns across exceptions."),
        ("answer q5", "grammar_wording", "moderate", "وتناسب التدقيق مع الأثر is malformed; make the audit level explicitly proportional to impact."),
    ],
    "ar-c1-u03-p04": [
        ("text", "grammar_wording", "moderate", "نافعت ... صعبت الوصول على is non-idiomatic institutional MSA; state that the rule benefited regular users while making access harder for intermittent groups."),
        ("answer q5", "grammar_wording", "moderate", "وتنوي قنوات الوصول is a malformed verb form; the intended action is to diversify access channels."),
    ],
    "ar-c1-u03-p05": [
        ("answer q1", "semantic_precision", "moderate", "أكثر جاذبية من النتيجة الأصلية compares recorded activity with an unclear 'original result'; the contrast is with achieving the institution's original purpose."),
        ("answer q5", "grammar_wording", "moderate", "يعيد تاريخ كل مقياس omits the construction required for reconstructing a metric's history; use يعيد بناء تاريخ."),
    ],
    "ar-c1-u03-p06": [
        ("text", "naturalness_idiomaticity", "moderate", "وتيرة العمل حول الرقم is awkward; preserve the lexical target while expressing that work pace changes in response to the target number."),
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
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    arabic = release.get("languages", {}).get("arabic", {})
    progress = arabic.get("naturalness_review_progress", {})
    if arabic.get("release_state") != "REOPEN_REQUIRED" or arabic.get("educator_release_ready") is not False:
        raise SystemExit("Arabic release gate drift")
    if progress.get("fresh_records_reviewed") != 252:
        raise SystemExit(f"expected 252 reviewed before C1 Unit 3, got {progress.get('fresh_records_reviewed')!r}")
    if progress.get("levels_completed") != ["A1", "A2", "B1", "B2"]:
        raise SystemExit(f"unexpected completed-level frontier: {progress.get('levels_completed')!r}")
    if not (DECISION_DIR / "c1_u02.json").exists() or (DECISION_DIR / "c1_u03.json").exists():
        raise SystemExit("C1 Unit 3 decision frontier drift")

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    c1 = inventory.get("levels", {}).get("c1", {})
    if c1.get("canonical_sha256") != pre_sha or c1.get("fresh_review_status") != "IN_PROGRESS":
        raise SystemExit("C1 current inventory/hash frontier drift")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [row.get("sequence") for row in rows] != list(range(1, 61)):
        raise SystemExit("C1 corpus layout/sequence drift")
    if [rows[i].get("id") for i in range(12, 18)] != EXPECTED_IDS:
        raise SystemExit("C1 Unit 3 id/frontier drift")

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
        if not 500 <= record["word_count"] <= 800:
            raise SystemExit(f"{pid}: word count {record['word_count']} outside C1 band")
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
    if total_findings != 10 or records_with_findings != 6:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")
    PATH.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"level":"C1","unit":3,"records_reviewed":6,"records_with_findings":records_with_findings,"fresh_findings":total_findings,"pre_repair_canonical_sha256":pre_sha,"post_repair_canonical_sha256":sha(PATH.read_bytes())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
