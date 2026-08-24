#!/usr/bin/env python3
"""Apply the audited pre-merge polish to Urdu A2 Unit 1.

Fail-closed guarantees:
- exact reviewed source Git blob required;
- exactly six Unit 1 records / sequences 1-6 required;
- every replacement must match exactly once in its intended record;
- no IDs, question/answer counts, or deliberate target identities may drift;
- lexical exposure counts and word counts are recomputed from final text;
- fluency passage remains new-target-free.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "urdu" / "a2" / "passages.jsonl"
AUDIT = ROOT / "reading" / "audit" / "urdu_a2_u01_quality_pass_2026-08-23.json"
EXPECTED_SOURCE_BLOB = "2c8fbecc734bfd12f0ee647fb7bb42c93462f5bf"

REPLACEMENTS = {
    "ur-a2-u01-p01": [
        (
            "اسے سب سے پہلے روزمرہ کی ضروری جگہیں سمجھنے کی فکر ہوئی۔",
            "اس نے سب سے پہلے روزمرہ کی ضروری جگہوں اور خدمات کو جاننے کا فیصلہ کیا۔",
            "Replace an awkward 'understand places / worry' collocation with natural goal-setting language.",
        ),
    ],
    "ur-a2-u01-p02": [
        (
            "سارہ نے درخواست کا نمبر اپنے فون میں لکھ لیا اور گھر کے دروازے کے پاس پانی سے بچنے کے لیے ایک نشان رکھ دیا۔",
            "سارہ نے درخواست کا نمبر اپنے فون میں لکھ لیا اور نل کے قریب ایک نشان رکھ دیا تاکہ کوئی جمع پانی میں پھسل نہ جائے۔",
            "Make the temporary warning action concrete and pragmatically natural.",
        ),
        (
            "سارہ نے محسوس کیا کہ واضح تفصیلات دینے سے چھوٹی درخواست بھی جلد سمجھی جا سکتی ہے۔",
            "سارہ نے محسوس کیا کہ واضح تفصیلات دینے سے مرمت کی درخواست بھی جلد سمجھی جا سکتی ہے۔",
            "Replace the unnatural collocation 'small request' with the specific repair-request meaning.",
        ),
    ],
    "ur-a2-u01-p03": [
        (
            "اس نے نئی رسید بنائی، درست رقم واپس کی اور معذرت کی۔",
            "اس نے درست قیمت کے ساتھ نئی رسید بنائی، اضافی رقم واپس کی اور معذرت کی۔",
            "Clarify that the overcharge difference, not the whole 'correct amount', is refunded while preserving the target درست.",
        ),
    ],
    "ur-a2-u01-p04": [
        (
            "اس نے متبادل راستہ بتایا اور سارہ نے پارک کے کنارے سے جانے کا راستہ طے کیا۔",
            "اس نے متبادل راستہ بتایا اور سارہ نے طے کیا کہ وہ پارک کے کنارے والے راستے سے جائے گی۔",
            "Disambiguate طے کرنا='decide' from راستہ طے کرنا='traverse a route'.",
        ),
        (
            "گھر پہنچ کر اس نے نقشے پر نیا راستہ نشان زد کیا اور اگلے سفر کا منصوبہ طے کر لیا۔",
            "گھر پہنچ کر اس نے نقشے پر نیا راستہ نشان زد کیا اور اگلے سفر کا وقت طے کر لیا۔",
            "Use a highly natural fixed-time collocation for the deliberate طے target sense.",
        ),
    ],
    "ur-a2-u01-p05": [
        (
            "سارہ نے شکایت نہیں کی، بلکہ صرف یہ جاننا چاہا کہ کام کا ریکارڈ بند ہو گیا ہے یا نہیں۔",
            "سارہ نے شکایت نہیں کی، بلکہ صرف یہ جاننا چاہا کہ پچھلی درخواست مکمل قرار دی گئی ہے یا نہیں۔",
            "Replace bureaucratic/opaque 'work record closed' wording with a clear service-request completion state.",
        ),
    ],
    "ur-a2-u01-p06": [
        (
            "اگر کسی مسئلے کی درخواست دینی ہو تو وہ پہلے جگہ اور مسئلے کی تفصیلات لکھ لیتی تھی۔",
            "اگر کسی مسئلے کے حل کی درخواست دینی ہو تو وہ پہلے جگہ اور مسئلے کی تفصیلات لکھ لیتی تھی۔",
            "Repair the collocation to 'request a solution to a problem'.",
        ),
        (
            "اگر قیمت یا رسید میں فرق نظر آئے تو وہ شکایت کرنے سے پہلے پیغام اور رسید دونوں دیکھتی تھی تاکہ بات درست ہو۔",
            "اگر قیمت یا رسید میں فرق نظر آئے تو وہ شکایت کرنے سے پہلے پیغام اور رسید دونوں دیکھتی تھی تاکہ اسے یقین ہو کہ بات درست معلومات پر مبنی ہے۔",
            "Clarify that verification establishes an evidence-based complaint rather than making 'the matter correct'.",
        ),
    ],
}

QUESTION_REPLACEMENTS = {
    "ur-a2-u01-p06": [
        (
            "اگر کسی مسئلے کی درخواست دینی _____ تو پہلے جگہ کی تفصیلات لکھ لیں۔",
            "اگر کسی مسئلے کے حل کی درخواست دینی _____ تو پہلے جگہ کی تفصیلات لکھ لیں۔",
        ),
    ],
}

QUALITY_NOTE = (
    "Pre-merge Urdu A2 Unit 1 reader-first quality pass applied 2026-08-23: "
    "naturalness, semantic precision, target-sense disambiguation, and service-scenario wording polished; "
    "formal release gates remain pending."
)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def load_records(raw: bytes) -> list[dict]:
    records = []
    for line_no, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at line {line_no}: {exc}") from exc
    return records


def replace_exact(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exact source phrase once, found {count}: {old}")
    return text.replace(old, new, 1)


def validate_record(record: dict) -> None:
    rid = record["id"]
    if record.get("language") != "ur" or record.get("cefr") != "A2" or record.get("unit") != 1:
        raise SystemExit(f"{rid}: unexpected language/level/unit")
    questions = record.get("questions", [])
    answers = record.get("answer_key", [])
    if len(questions) != 10 or len(answers) != 10:
        raise SystemExit(f"{rid}: expected exactly 10 questions and 10 answers")
    qids = {q.get("id") for q in questions}
    aids = {a.get("id") for a in answers}
    if qids != {f"q{i}" for i in range(1, 11)}:
        raise SystemExit(f"{rid}: question IDs drifted: {sorted(qids)}")
    if aids != {f"a{i}" for i in range(1, 11)}:
        raise SystemExit(f"{rid}: answer IDs drifted: {sorted(aids)}")
    for i in range(1, 11):
        q = next(x for x in questions if x["id"] == f"q{i}")
        a = next(x for x in answers if x["id"] == f"a{i}")
        if q.get("answer_id") != a["id"] or a.get("question_id") != q["id"]:
            raise SystemExit(f"{rid}: q/a linkage drift at {i}")
    if record.get("passage_type") == "fluency":
        if record.get("new_lexical_targets"):
            raise SystemExit(f"{rid}: fluency passage unexpectedly has new lexical targets")
        if record.get("speed_training", {}).get("new_word_policy") != "none":
            raise SystemExit(f"{rid}: fluency new_word_policy must remain none")


def main() -> int:
    raw_before = PATH.read_bytes()
    before_blob = git_blob_sha(raw_before)
    if before_blob != EXPECTED_SOURCE_BLOB:
        raise SystemExit(
            f"source blob drift: live {before_blob}, expected reviewed {EXPECTED_SOURCE_BLOB}; refusing to patch"
        )

    records = load_records(raw_before)
    expected_ids = [f"ur-a2-u01-p{i:02d}" for i in range(1, 7)]
    ids = [r.get("id") for r in records]
    sequences = [r.get("sequence") for r in records]
    if ids != expected_ids:
        raise SystemExit(f"record IDs drifted: {ids}")
    if sequences != list(range(1, 7)):
        raise SystemExit(f"sequence drift: {sequences}")

    changes: list[dict] = []
    target_ids_before = {
        r["id"]: [t["id"] for t in r.get("new_lexical_targets", [])] for r in records
    }

    for record in records:
        rid = record["id"]
        for old, new, reason in REPLACEMENTS.get(rid, []):
            record["text"] = replace_exact(record["text"], old, new, f"{rid}/text")
            changes.append({"record_id": rid, "field": "text", "before": old, "after": new, "reason": reason})

        for old, new in QUESTION_REPLACEMENTS.get(rid, []):
            matched = [q for q in record["questions"] if old in q.get("prompt", "")]
            if len(matched) != 1:
                raise SystemExit(f"{rid}/questions: expected one prompt containing {old!r}, found {len(matched)}")
            matched[0]["prompt"] = replace_exact(matched[0]["prompt"], old, new, f"{rid}/{matched[0]['id']}")
            changes.append({
                "record_id": rid,
                "field": f"questions.{matched[0]['id']}.prompt",
                "before": old,
                "after": new,
                "reason": "Keep the operational grammar item aligned with the repaired natural service-request collocation.",
            })

        if rid in REPLACEMENTS or rid in QUESTION_REPLACEMENTS:
            record["revision"] = int(record.get("revision", 0)) + 1
            notes = record.setdefault("quality", {}).setdefault("notes", [])
            if QUALITY_NOTE not in notes:
                notes.append(QUALITY_NOTE)

        record["word_count"] = len(record["text"].split())
        for target in record.get("new_lexical_targets", []):
            occurrences = record["text"].count(target["form"])
            if occurrences < 1:
                raise SystemExit(f"{rid}: deliberate target {target['id']} / {target['form']} disappeared from text")
            target["exposures_in_text"] = occurrences
        validate_record(record)

    if len(changes) != 10:
        raise SystemExit(f"expected exactly 10 audited replacements, applied {len(changes)}")

    target_ids_after = {
        r["id"]: [t["id"] for t in r.get("new_lexical_targets", [])] for r in records
    }
    if target_ids_after != target_ids_before:
        raise SystemExit("new lexical target identities changed unexpectedly")

    final_text = "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in records) + "\n"
    final_bytes = final_text.encode("utf-8")
    after_blob = git_blob_sha(final_bytes)
    if after_blob == before_blob:
        raise SystemExit("quality pass produced no blob change")

    PATH.write_bytes(final_bytes)

    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "urdu",
        "cefr": "A2",
        "unit": 1,
        "reviewed_on": "2026-08-23",
        "status": "PASS_AFTER_BOUNDED_REMEDIATION",
        "scope": "Reader-first pre-merge naturalness, semantic precision, deliberate-target sense clarity, q/a linkage, passage counts, and fluency new-word policy.",
        "not_a_release_promotion": True,
        "source_git_blob": before_blob,
        "result_git_blob": after_blob,
        "passages": 6,
        "questions": sum(len(r["questions"]) for r in records),
        "answers": sum(len(r["answer_key"]) for r in records),
        "changes_applied": changes,
        "postconditions": {
            "ids": [r["id"] for r in records],
            "sequences": [r["sequence"] for r in records],
            "new_target_ids_unchanged": True,
            "fluency_new_targets": len(records[-1]["new_lexical_targets"]),
            "fluency_new_word_policy": records[-1]["speed_training"]["new_word_policy"],
            "target_exposures": {
                r["id"]: {t["id"]: t["exposures_in_text"] for t in r.get("new_lexical_targets", [])}
                for r in records
            },
            "word_counts": {r["id"]: r["word_count"] for r in records},
            "revisions": {r["id"]: r["revision"] for r in records},
        },
        "remaining_limits": [
            "Formal corpus-wide linguistic, pedagogical, CEFR/coverage, schema, answer-key, independent/native, and educator-release gates remain pending by policy.",
            "This pass does not change reading/RELEASE_STATUS.json."
        ],
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("Urdu A2 Unit 1 quality pass: PASS_AFTER_BOUNDED_REMEDIATION")
    print(f"source blob: {before_blob}")
    print(f"result blob: {after_blob}")
    print(f"changes: {len(changes)}")
    print(f"passages/questions/answers: 6/{audit['questions']}/{audit['answers']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
