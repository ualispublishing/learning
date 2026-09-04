#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 1 naturalness/Q&A repairs."""
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
EXPECTED_IDS = [f"ar-c1-u01-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (C1 Unit 1): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-c1-u01-p01": [
        (
            "وإذا كان هذا الربط ضعيفًا، فقد تصبح الحسابات دقيقة جدًا حول شيء لا يجيب عن السؤال الأصلي.",
            "وإذا كان هذا الربط ضعيفًا، فقد تكون الحسابات دقيقة جدًا مع أنها تقيس شيئًا لا يجيب عن السؤال الأصلي.",
        ),
    ],
    "ar-c1-u01-p02": [
        (
            "نُشر الرابط في مكتبات عامة ونوادٍ للقراءة وصفحات ثقافية، أي في أماكن يرتادها أشخاص مهتمون بالقراءة أكثر من المتوسط.",
            "نُشر الرابط في مكتبات عامة ونوادٍ للقراءة وصفحات ثقافية، أي في أماكن يرتادها أشخاص مهتمون بالقراءة بدرجة تفوق المتوسط.",
        ),
        (
            "العدد الكبير يقلل بعض أنواع الخطأ العشوائي، لكنه لا يصلح تلقائيًا انحياز الدخول إلى العينة.",
            "العدد الكبير يقلل بعض أنواع الخطأ العشوائي، لكنه لا يصحح تلقائيًا انحياز الدخول إلى العينة.",
        ),
    ],
    "ar-c1-u01-p03": [
        (
            "كتب قارئ متحمس أن «زيادة الرسائل ترفع الإنتاج»، لكن الباحث يوسف رأى أن الانتقال من العلاقة إلى السبب أسرع من الأدلة.",
            "كتب قارئ متحمس أن «زيادة الرسائل ترفع الإنتاج»، لكن الباحث يوسف رأى أن الانتقال من العلاقة إلى السبب أسرع مما تسمح به الأدلة.",
        ),
    ],
    "ar-c1-u01-p06": [
        (
            "وعندما ظهر ارتباط بين تلقي الملاحظات والنتيجة، كتبت ثلاثة تفسيرات سببية منافسة وحددت توقعًا يختلف بينها بدل اختيار القصة الأكثر راحة.",
            "وعندما ظهر ارتباط بين تلقي الملاحظات والنتيجة، كتبت ثلاثة تفسيرات سببية منافسة وحددت توقعًا يختلف من تفسير إلى آخر بدل اختيار القصة الأكثر راحة.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-c1-u01-p02": {
        "questions": {
            "q8": (
                "ما وظيفة «حتى» في القول إن القائمة الأوسع لا تمنع اختلاف غير المستجيبين عمن يجيب؟",
                "ما وظيفة «حتى» في القول إن استخدام القائمة الأوسع لا يمنع اختلاف غير المستجيبين عن المستجيبين؟",
            ),
        },
        "answers": {
            "q5": (
                "يحلل بوابة الدخول ومعدل الاستجابة وحساسية النتائج لغير المستجيبين، ويحدد العلاقات المستقرة عبر القنوات قبل توسيع النطاق إلى السكان.",
                "يحلل بوابة الدخول ومعدل الاستجابة وحساسية النتائج للافتراضات المتعلقة بغير المستجيبين، ويحدد العلاقات المستقرة عبر القنوات قبل توسيع النطاق إلى السكان.",
            ),
        },
    },
    "ar-c1-u01-p03": {
        "answers": {
            "q1": (
                "البيانات تظهر علاقة، لكن عوامل أخرى أو اتجاه السببية قد يفسرانها.",
                "البيانات تظهر علاقة، لكن قد تفسرها عوامل أخرى أو قد يكون اتجاه السببية معاكسًا.",
            ),
        },
    },
    "ar-c1-u01-p04": {
        "answers": {
            "q2": (
                "نوع المهمة والمجموعة وبعض ترتيب الخطوات مع إبقاء الفكرة الأساسية.",
                "نوع المهمة والمجموعة وترتيب الخطوات مع إبقاء الفكرة الأساسية.",
            ),
        },
    },
    "ar-c1-u01-p06": {
        "answers": {
            "q8": (
                "تقابل مشكلة في صياغة نطاق الادعاء بمشكلة أدلة فعلية، فتحدد متى يكفي تعديل اللغة ومتى يلزم جمع معلومات جديدة.",
                "تقارن بين مشكلة في صياغة نطاق الادعاء ومشكلة في الأدلة نفسها، فتحدد متى يكفي تعديل اللغة ومتى يلزم جمع معلومات جديدة.",
            ),
        },
    },
}

FINDING_META = {
    "ar-c1-u01-p01": [
        ("text", "naturalness_idiomaticity", "moderate", "دقيقة جدًا حول شيء is a calque-like measurement formulation; make the contrast explicit between precise calculations and measuring the wrong thing."),
    ],
    "ar-c1-u01-p02": [
        ("text", "naturalness_idiomaticity", "minor", "مهتمون بالقراءة أكثر من المتوسط is awkward because المتوسط does not directly modify people; express degree of interest instead."),
        ("text", "grammar_wording", "moderate", "لا يصلح ... انحياز uses the wrong verb; sample size does not automatically correct selection bias."),
        ("question q8", "assessment_wording", "moderate", "اختلاف غير المستجيبين عمن يجيب has malformed comparison/reference; contrast nonrespondents with respondents directly."),
        ("answer q5", "semantic_precision", "moderate", "حساسية النتائج لغير المستجيبين is imprecise; the sensitivity analysis concerns assumptions about nonrespondents."),
    ],
    "ar-c1-u01-p03": [
        ("text", "naturalness_idiomaticity", "moderate", "الانتقال ... أسرع من الأدلة is an incomplete comparison; use أسرع مما تسمح به الأدلة."),
        ("answer q1", "grammar_wording", "moderate", "عوامل أخرى أو اتجاه السببية قد يفسرانها mismatches a plural/disjunctive subject with a dual verb and blurs the reverse-causality alternative."),
    ],
    "ar-c1-u01-p04": [
        ("answer q2", "grammar_wording", "moderate", "بعض ترتيب الخطوات is malformed; the passage changes the task, group, and ordering of steps."),
    ],
    "ar-c1-u01-p05": [],
    "ar-c1-u01-p06": [
        ("text", "reference_clarity", "moderate", "توقعًا يختلف بينها leaves the comparison referent unclear; specify that the prediction differs from one causal explanation to another."),
        ("answer q8", "naturalness_idiomaticity", "moderate", "تقابل مشكلة ... بمشكلة is awkward for the contrast introduced by أما; state that the construction compares a scope-wording problem with an evidence problem."),
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
    if progress.get("fresh_records_reviewed") != 240:
        raise SystemExit(f"expected 240 reviewed before C1 Unit 1, got {progress.get('fresh_records_reviewed')!r}")
    if progress.get("levels_completed") != ["A1", "A2", "B1", "B2"]:
        raise SystemExit(f"unexpected completed-level frontier: {progress.get('levels_completed')!r}")
    if not (DECISION_DIR / "b2_u10.json").exists() or (DECISION_DIR / "c1_u01.json").exists():
        raise SystemExit("C1 Unit 1 decision frontier drift")

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    c1 = inventory.get("levels", {}).get("c1", {})
    if c1.get("canonical_sha256") != pre_sha or c1.get("fresh_review_status") != "NOT_YET_REVIEWED":
        raise SystemExit("C1 current inventory/hash frontier drift")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [row.get("sequence") for row in rows] != list(range(1, 61)):
        raise SystemExit("C1 corpus layout/sequence drift")
    if [rows[i].get("id") for i in range(0, 6)] != EXPECTED_IDS:
        raise SystemExit("C1 Unit 1 id/frontier drift")

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
    if total_findings != 10 or records_with_findings != 5:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")
    PATH.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"level":"C1","unit":1,"records_reviewed":6,"records_with_findings":records_with_findings,"fresh_findings":total_findings,"pre_repair_canonical_sha256":pre_sha,"post_repair_canonical_sha256":sha(PATH.read_bytes())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
