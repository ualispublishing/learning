#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 4 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
EXPECTED_IDS = [f"ar-b2-u04-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (B2 Unit 4): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA idiom, semantic, and assessment-wording "
    "repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u04-p04": [
        (
            "لذلك أضاف الفريق إلى متابعة المشروع مؤشرًا عن استمرار النشاط لا مجرد وجود محل مؤقت.",
            "لذلك أضاف الفريق إلى متابعة المشروع مؤشرًا على استمرار النشاط لا مجرد وجود محل مؤقت.",
        ),
    ],
    "ar-b2-u04-p05": [
        (
            "أما التكوين الأكثر مرونة فدفع كلفة إضافية مقدمًا، لكنه سمح بتحريك أجزاء داخلية من دون تغيير الهيكل الأساسي.",
            "أما التكوين الأكثر مرونة فتطلّب كلفة إضافية مقدمًا، لكنه سمح بتحريك أجزاء داخلية من دون تغيير الهيكل الأساسي.",
        ),
    ],
    "ar-b2-u04-p06": [
        (
            "والميدان الذي يقيس نجاحه بعدد الزوار يعطي وزنًا أكبر لمن يأتي أحيانًا منه لمن يعيش مع أثر المكان كل يوم.",
            "والميدان الذي يقيس نجاحه بعدد الزوار يعطي وزنًا أكبر لمن يأتي أحيانًا مقارنةً بمن يعيش مع أثر المكان كل يوم.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u04-p03": {
        "answers": {
            "q8": (
                "تقر بتقليل الحجم المرئي ثم تبرز مكسبًا نظاميًا يجعل الحل الأصغر أكثر استدامة وقابلية للعمل.",
                "تقر بأن المساحة أصغر مما كان متخيّلًا، ثم تبرز أنها مع ذلك قابلة للاستخدام والصيانة.",
            ),
        },
    },
    "ar-b2-u04-p05": {
        "answers": {
            "q6": (
                "تقدم البديل المقابل وتوضح اختلاف توزيع الكلفة بين البداية والقدرة على التعديل لاحقًا.",
                "تقدم البديل المقابل، وتوضح أن الكلفة الأعلى في البداية تقابلها قدرة أكبر على التعديل لاحقًا.",
            ),
        },
    },
    "ar-b2-u04-p06": {
        "answers": {
            "q1": (
                "لأنه يجسد افتراضات عن المستخدمين والأولويات من خلال ما يجعله سهلًا أو صعبًا حتى من دون كتابة هذه الافتراضات.",
                "لأنه يجسد افتراضات عن المستخدمين والأولويات من خلال ما يجعل بعض الأفعال سهلةً أو صعبةً، حتى من دون كتابة هذه الافتراضات.",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u04-p01": [],
    "ar-b2-u04-p02": [],
    "ar-b2-u04-p03": [
        ("answer q8", "assessment_alignment", "moderate", "قابلية للعمل is a vague calque and does not match the passage contrast; answer directly with usability and maintainability."),
    ],
    "ar-b2-u04-p04": [
        ("text", "naturalness_idiomaticity", "minor", "The standard collocation is مؤشر على استمرار النشاط, not مؤشر عن استمرار النشاط."),
    ],
    "ar-b2-u04-p05": [
        ("text", "naturalness_idiomaticity", "moderate", "A configuration does not naturally دفع كلفة; state that the more flexible configuration required an additional upfront cost."),
        ("answer q6", "semantic_precision", "moderate", "The old answer contrasts cost distribution with an ability, unlike dimensions; state the actual tradeoff between higher initial cost and greater later adaptability."),
    ],
    "ar-b2-u04-p06": [
        ("text", "naturalness_idiomaticity", "moderate", "وزنًا أكبر ... منه لمن is an awkward comparative chain; use مقارنةً بمن for the resident comparison."),
        ("answer q1", "reference_clarity", "moderate", "ما يجعله سهلًا أو صعبًا has an unclear object pronoun; name the actions that the design makes easier or harder."),
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
    if [rows[i].get("id") for i in range(18, 24)] != EXPECTED_IDS:
        raise SystemExit("B2 Unit 4 id/frontier drift")

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
    if total_findings != 6 or records_with_findings != 4:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")

    PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(json.dumps({
        "level": "B2",
        "unit": 4,
        "records_reviewed": 6,
        "records_with_findings": records_with_findings,
        "fresh_findings": total_findings,
        "pre_repair_canonical_sha256": pre_sha,
        "post_repair_canonical_sha256": sha(PATH.read_bytes()),
        "word_counts": {pid: by_id[pid]["word_count"] for pid in EXPECTED_IDS},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
