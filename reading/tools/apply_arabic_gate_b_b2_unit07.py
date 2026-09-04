#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B2 Unit 7 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "arabic/b2/passages.jsonl"
EXPECTED_IDS = [f"ar-b2-u07-p{i:02d}" for i in range(1, 7)]
TOKEN = re.compile(r"\S+")
NOTE = (
    "2026-09-04 fresh Gate B naturalness review (B2 Unit 7): learner-facing prose/Q/A "
    "reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, "
    "and assessment-wording repairs applied; no educator/publication release claim."
)

TEXT_REPAIRS = {
    "ar-b2-u07-p01": [
        (
            "قارنت نور تجربتها بزائر قرأ البطاقة أولًا، فوجدت أنه لم يتخيل القراءة المريحة التي خطرت لها.",
            "قارنت نور تجربتها بزائر قرأ البطاقة أولًا، فوجدت أن القراءة المريحة التي خطرت لها لم تخطر له.",
        ),
    ],
    "ar-b2-u07-p04": [
        (
            "لكن المخرج اختار أن يقولها الممثل في همس وهو ينظر إلى الباب لا إلى الشخص أمامه.",
            "لكن المخرج اختار أن يقولها الممثل بهمس وهو ينظر إلى الباب لا إلى الشخص أمامه.",
        ),
    ],
}

QA_REPAIRS = {
    "ar-b2-u07-p01": {
        "answers": {
            "q6": (
                "تقر بقوة الإطار المؤسسي ثم تضع حدًا لها بإعادة سلطة الاختبار إلى تفاصيل العمل نفسه.",
                "تعترف بقوة الإطار المؤسسي، لكنها تحد من سلطته بالعودة إلى تفاصيل العمل نفسه لاختبار القراءة.",
            ),
        },
    },
    "ar-b2-u07-p03": {
        "answers": {
            "q1": (
                "لأن الإيقاع والصوت والتكوين الموسيقي يغيرون النبرة رغم ثبات الكلمات.",
                "لأن اختلاف الإيقاع والصوت والتكوين الموسيقي يغيّر النبرة رغم ثبات الكلمات.",
            ),
        },
    },
    "ar-b2-u07-p04": {
        "answers": {
            "q2": (
                "في همس وهو ينظر إلى الباب لا إلى الشخص أمامه.",
                "بهمس وهو ينظر إلى الباب لا إلى الشخص أمامه.",
            ),
        },
    },
}

FINDING_META = {
    "ar-b2-u07-p01": [
        ("text", "naturalness_idiomaticity", "moderate", "لم يتخيل القراءة ... التي خطرت لها is awkward for an interpretation that did not occur to the other viewer; use لم تخطر له."),
        ("answer q6", "naturalness_idiomaticity", "moderate", "تضع حدًا لها بإعادة سلطة الاختبار is a calque; state that the museum frame has real force but its authority is limited by testing the reading against the work itself."),
    ],
    "ar-b2-u07-p02": [],
    "ar-b2-u07-p03": [
        ("answer q1", "grammar_wording", "moderate", "يغيرون incorrectly treats coordinated nonhuman factors as human plural agents; recast with اختلاف as the singular causal subject."),
    ],
    "ar-b2-u07-p04": [
        ("text", "naturalness_idiomaticity", "minor", "The idiomatic manner phrase is يقولها بهمْس/بهمس, not في همس."),
        ("answer q2", "naturalness_idiomaticity", "minor", "The answer repeats the non-idiomatic في همس; use بهمْس/بهمس."),
    ],
    "ar-b2-u07-p05": [],
    "ar-b2-u07-p06": [],
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
    if [rows[i].get("id") for i in range(36, 42)] != EXPECTED_IDS:
        raise SystemExit("B2 Unit 7 id/frontier drift")

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
    if total_findings != 5 or records_with_findings != 3:
        raise SystemExit(f"finding metadata drift: findings={total_findings}, records={records_with_findings}")
    PATH.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"level":"B2","unit":7,"records_reviewed":6,"records_with_findings":records_with_findings,"fresh_findings":total_findings,"pre_repair_canonical_sha256":pre_sha,"post_repair_canonical_sha256":sha(PATH.read_bytes())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
