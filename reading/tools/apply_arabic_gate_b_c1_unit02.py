#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 2 naturalness/Q&A repairs."""
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
EXPECTED_IDS = [f"ar-c1-u02-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (C1 Unit 2): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-c1-u02-p01": [
        (
            "كان سامر أكثر أعضاء الفريق لياقة من حيث الخبرة التقنية المباشرة، ولذلك توقع المدير أن يقدم الحكم النهائي وحده.",
            "كان سامر أكثر أعضاء الفريق لياقةً للمهمة من حيث الخبرة التقنية المباشرة، ولذلك توقع المدير أن يقدم الحكم النهائي وحده.",
        ),
    ],
    "ar-c1-u02-p03": [
        (
            "تغيرت التوصية من «اشتروا المنتج أ» إلى «المنتجان أ وب مناسبان، ويعتمد الاختيار على مقدار ما تمنحه المؤسسة للأتمتة مقابل سهولة النقل بين الأنظمة».",
            "تغيرت التوصية من «اشتروا المنتج أ» إلى «المنتجان أ وب مناسبان، ويعتمد الاختيار على مقدار الوزن الذي تمنحه المؤسسة للأتمتة مقابل سهولة النقل بين الأنظمة».",
        ),
    ],
    "ar-c1-u02-p05": [
        (
            "الجودة المهنية هنا هي حفظ ثبات كاف للتوقع والمساءلة، مع قناة صريحة تجعل التعلم من الحالات الصعبة قادرًا على تغيير القاعدة.",
            "الجودة المهنية هنا هي حفظ ثبات كاف للتوقع والمساءلة، مع قناة صريحة تتيح للتعلم من الحالات الصعبة أن يغير القاعدة.",
        ),
    ],
    "ar-c1-u02-p06": [
        (
            "أما ثبات القواعد فيحمي التوقع والمساءلة، لكنه يحتاج إلى استثناءات مكتوبة عندما تجعل الحالة خيارًا آخر أمثل بوضوح.",
            "أما ثبات القواعد فيحمي التوقع والمساءلة، لكنه يحتاج إلى استثناءات مكتوبة عندما يكون خيار آخر أمثل بوضوح في الحالة.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-c1-u02-p02": {
        "answers": {
            "q6": (
                "التأجيل لا ينتج معرفة جديدة، أما الاختبار المحدود فيتخذ قرارًا مؤقتًا مصممًا لجمع دليل.",
                "التأجيل لا ينتج معرفة جديدة، أما الاختبار المحدود فهو قرار مؤقت مصمم لجمع دليل.",
            ),
        },
    },
    "ar-c1-u02-p03": {
        "answers": {
            "q5": (
                "تتبع تعريف المشكلة والبدائل والمعايير والأوزان والعرض، وتعيد الحساب مستقلاً، فتحدد أين تتفق الوقائع وأين تدخل القيم أو المصالح في ترتيبها.",
                "تتبع تعريف المشكلة والبدائل والمعايير والأوزان والعرض، وتعيد الحساب بصورة مستقلة، فتحدد أين تتفق الوقائع وأين تدخل القيم أو المصالح في ترتيبها.",
            ),
        },
    },
    "ar-c1-u02-p04": {
        "answers": {
            "q1": (
                "لأن الأقسام تقيس نجاحًا مختلفًا وتحتاج إلى نموذج يجمع أبعاد القرار لا إلى ملف موحد فقط.",
                "لأن الأقسام تقيس أبعادًا مختلفة من النجاح وتحتاج إلى نموذج يجمع أبعاد القرار لا إلى ملف موحد فقط.",
            ),
        },
    },
    "ar-c1-u02-p06": {
        "answers": {
            "q8": (
                "تقابل حالتين تختلفان في مقدار الخطر وصعوبة الرجوع، فتبرر اختلاف مقدار المراجعة المطلوبة بينهما.",
                "تقارن بين حالتين تختلفان في مقدار الخطر وصعوبة الرجوع، فتبرر اختلاف مقدار المراجعة المطلوبة بينهما.",
            ),
        },
    },
}

FINDING_META = {
    "ar-c1-u02-p01": [
        ("text", "naturalness_idiomaticity", "moderate", "أكثر أعضاء الفريق لياقة من حيث الخبرة leaves the deliberate target لياقة without an idiomatic complement; specify suitability for the task while preserving the target."),
    ],
    "ar-c1-u02-p02": [
        ("answer q6", "semantic_precision", "moderate", "الاختبار المحدود فيتخذ قرارًا assigns the act of taking a decision to the test itself; describe the bounded test as the temporary evidence-generating decision."),
    ],
    "ar-c1-u02-p03": [
        ("text", "semantic_precision", "moderate", "مقدار ما تمنحه المؤسسة للأتمتة omits what is being assigned; the trade-off concerns the weight assigned to automation."),
        ("answer q5", "grammar_wording", "moderate", "وتعيد الحساب مستقلاً leaves the adverbial agreement/reference awkward after a feminine committee subject; use بصورة مستقلة."),
    ],
    "ar-c1-u02-p04": [
        ("answer q1", "semantic_precision", "moderate", "الأقسام تقيس نجاحًا مختلفًا suggests different successes rather than different dimensions of success; state the latter explicitly."),
    ],
    "ar-c1-u02-p05": [
        ("text", "naturalness_idiomaticity", "moderate", "تجعل التعلم ... قادرًا على تغيير القاعدة is an awkward agency construction; state that the channel enables learning from hard cases to change the rule."),
    ],
    "ar-c1-u02-p06": [
        ("text", "grammar_wording", "moderate", "تجعل الحالة خيارًا آخر أمثل reverses the predicate relation; the intended claim is that another option is clearly optimal in that case."),
        ("answer q8", "naturalness_idiomaticity", "moderate", "تقابل حالتين is awkward for the discourse function of بينما here; it compares two cases."),
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
    if progress.get("fresh_records_reviewed") != 246:
        raise SystemExit(f"expected 246 reviewed before C1 Unit 2, got {progress.get('fresh_records_reviewed')!r}")
    if progress.get("levels_completed") != ["A1", "A2", "B1", "B2"]:
        raise SystemExit(f"unexpected completed-level frontier: {progress.get('levels_completed')!r}")
    if not (DECISION_DIR / "c1_u01.json").exists() or (DECISION_DIR / "c1_u02.json").exists():
        raise SystemExit("C1 Unit 2 decision frontier drift")

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    c1 = inventory.get("levels", {}).get("c1", {})
    if c1.get("canonical_sha256") != pre_sha or c1.get("fresh_review_status") != "IN_PROGRESS":
        raise SystemExit("C1 current inventory/hash frontier drift")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 60 or [row.get("sequence") for row in rows] != list(range(1, 61)):
        raise SystemExit("C1 corpus layout/sequence drift")
    if [rows[i].get("id") for i in range(6, 12)] != EXPECTED_IDS:
        raise SystemExit("C1 Unit 2 id/frontier drift")

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
    if total_findings != 8 or records_with_findings != 6:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")
    PATH.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"level":"C1","unit":2,"records_reviewed":6,"records_with_findings":records_with_findings,"fresh_findings":total_findings,"pre_repair_canonical_sha256":pre_sha,"post_repair_canonical_sha256":sha(PATH.read_bytes())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
