#!/usr/bin/env python3
"""Repair Arabic A1 Unit 2 formal-metalinguistic questions on current canonical data."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
AUDIT = ROOT / "reading" / "audit" / "arabic_a1_u02_metalinguistic_repair_2026-08-30.json"
EXPECTED_SHA256 = "940975ffccbdaf2f685dfbdd6c87caa334c89cb33df1458efd43ec5b103ddecc"
FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}

REPAIRS = {
    ("ar-a1-u02-p01", "q7"): {
        "old_type": "grammar_function", "old_prompt": "ما العلاقة الزمنية التي تدل عليها «قبل»؟",
        "new_question": {"answer_id": "a7", "id": "q7", "prompt": "إذا كان الاستعداد يسبق الخروج، أي جملة أنسب: «أستعد قبل الخروج» أم «أستعد بعد الخروج»؟", "type": "grammar_choice"},
        "new_answer": "أستعد قبل الخروج.", "new_explanation": "«قبل» تبين أن الاستعداد يحدث أولًا ثم يأتي الخروج."
    },
    ("ar-a1-u02-p02", "q7"): {
        "old_type": "grammar_category", "old_prompt": "ما وظيفة «أولًا» في ترتيب الأحداث؟",
        "new_question": {"answer_id": "a7", "id": "q7", "prompt": "دخلت ليلى الصف ثم فتحت دفترها. أي جملة تصف الترتيب الصحيح: «دخلت الصف أولًا» أم «فتحت الدفتر أولًا»؟", "type": "grammar_choice"},
        "new_answer": "دخلت الصف أولًا.", "new_explanation": "«أولًا» تستعمل للحدث الذي يبدأ به الترتيب."
    },
    ("ar-a1-u02-p03", "q7"): {
        "old_type": "grammar_function", "old_prompt": "ما وظيفة «سوف» قبل الفعل؟",
        "new_question": {"answer_id": "a7", "id": "q7", "prompt": "اختر الجملة التي تتحدث عن المستقبل: «سوف نزور المكتبة غدًا» أم «زرنا المكتبة أمس»؟", "type": "grammar_choice"},
        "new_answer": "سوف نزور المكتبة غدًا.", "new_explanation": "«سوف» مع الفعل هنا تشير إلى فعل سيحدث لاحقًا."
    },
    ("ar-a1-u02-p04", "q6"): {
        "old_type": "grammar_category", "old_prompt": "ما التصنيف النحوي لكلمة «أيضا» في هذا الاستعمال؟",
        "new_question": {"answer_id": "a6", "id": "q6", "prompt": "أي جملة تضيف الدفتر إلى الكتاب: «أريد كتابًا وأريد أيضًا دفترًا» أم «أريد كتابًا فقط»؟", "type": "grammar_choice"},
        "new_answer": "أريد كتابًا وأريد أيضًا دفترًا.", "new_explanation": "«أيضًا» تضيف شيئًا آخر إلى ما ذُكر من قبل."
    },
    ("ar-a1-u02-p05", "q7"): {
        "old_type": "grammar_category", "old_prompt": "ما نوع «كيف» في السؤال؟",
        "new_question": {"answer_id": "a7", "id": "q7", "prompt": "إذا أردت السؤال عن طريقة الوصول، أي سؤال أنسب: «كيف نصل إلى المكتبة؟» أم «متى نصل إلى المكتبة؟»؟", "type": "grammar_choice"},
        "new_answer": "كيف نصل إلى المكتبة؟", "new_explanation": "«كيف» تسأل هنا عن الطريقة."
    },
    ("ar-a1-u02-p06", "q9"): {
        "old_type": "grammar_function", "old_prompt": "ماذا تسأل «كيف»؟",
        "new_question": {"answer_id": "a9", "id": "q9", "prompt": "إذا أردت السؤال عن طريقة ترتيب الوقت، أي سؤال أنسب: «كيف نرتب الوقت؟» أم «أين نرتب الوقت؟»؟", "type": "grammar_choice"},
        "new_answer": "كيف نرتب الوقت؟", "new_explanation": "«كيف» تسأل هنا عن الطريقة التي يتم بها ترتيب الوقت."
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def protected_snapshot(record: dict) -> dict:
    snap = copy.deepcopy(record)
    snap.pop("questions", None)
    snap.pop("answer_key", None)
    snap.pop("revision", None)
    if isinstance(snap.get("quality"), dict):
        snap["quality"].pop("notes", None)
    return snap


def main() -> int:
    before = PATH.read_bytes()
    if sha256(before) != EXPECTED_SHA256:
        raise SystemExit("Arabic A1 canonical hash drifted; refusing Unit 2 repair")
    raw_lines = PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    if len(raw_lines) != 60:
        raise SystemExit(f"Expected 60 records, found {len(raw_lines)}")
    records = [json.loads(line) for line in raw_lines]
    if [r.get("sequence") for r in records] != list(range(1, 61)):
        raise SystemExit("Arabic A1 sequence drift")
    protected_before = {r["id"]: protected_snapshot(r) for r in records[6:12]}
    untouched_prefix = b"".join(line.encode("utf-8") for line in raw_lines[:6])
    untouched_suffix = b"".join(line.encode("utf-8") for line in raw_lines[12:])

    changed = []
    for record in records[6:12]:
        rid = record["id"]
        if record.get("unit") != 2:
            raise SystemExit(f"{rid}: sequences 7-12 are no longer Unit 2")
        q_by_id = {q["id"]: q for q in record["questions"]}
        a_by_qid = {a["question_id"]: a for a in record["answer_key"]}
        for qid in [qid for (pid, qid) in REPAIRS if pid == rid]:
            spec = REPAIRS[(rid, qid)]
            q = q_by_id[qid]
            a = a_by_qid[qid]
            if q.get("type") != spec["old_type"] or q.get("prompt") != spec["old_prompt"]:
                raise SystemExit(f"{rid}/{qid}: source question drifted")
            record["questions"][record["questions"].index(q)] = spec["new_question"]
            a["answer"] = spec["new_answer"]
            a["explanation"] = spec["new_explanation"]
            changed.append({"passage_id": rid, "question_id": qid, "old_type": spec["old_type"], "new_type": "grammar_choice", "new_prompt": spec["new_question"]["prompt"], "new_answer": spec["new_answer"]})
        note = "2026-08-30 A1 Unit 2 metalinguistic remediation: formal-label item(s) rewritten as operational A1 use/form tasks; source prose and targets preserved."
        if note not in record["quality"].setdefault("notes", []):
            record["quality"]["notes"].append(note)
        record["revision"] = int(record.get("revision", 0)) + 1
        if protected_snapshot(record) != protected_before[rid]:
            raise SystemExit(f"{rid}: protected prose/target/metadata fields changed")

    if len(changed) != 6:
        raise SystemExit(f"Expected 6 repairs, got {len(changed)}")
    for record in records[6:12]:
        if len(record["questions"]) != 10 or len(record["answer_key"]) != 10:
            raise SystemExit(f"{record['id']}: Q/A count drift")
        qids = {q["id"] for q in record["questions"]}
        if qids != {f"q{i}" for i in range(1, 11)}:
            raise SystemExit(f"{record['id']}: question IDs drift")
        if any(a["question_id"] not in qids for a in record["answer_key"]):
            raise SystemExit(f"{record['id']}: answer linkage drift")
        formal = [(q["id"], q["type"]) for q in record["questions"] if q.get("type") in FORMAL_TYPES]
        if formal:
            raise SystemExit(f"{record['id']}: formal types remain: {formal}")

    out_lines = list(raw_lines)
    for idx in range(6, 12):
        newline = "\n" if raw_lines[idx].endswith("\n") else ""
        out_lines[idx] = json.dumps(records[idx], ensure_ascii=False) + newline
    PATH.write_text("".join(out_lines), encoding="utf-8")
    after_bytes = PATH.read_bytes()
    after_lines = after_bytes.splitlines(keepends=True)
    if b"".join(after_lines[:6]) != untouched_prefix or b"".join(after_lines[12:]) != untouched_suffix:
        raise SystemExit("Records outside Unit 2 changed bytewise")

    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "level": "A1",
        "unit": 2,
        "date": "2026-08-30",
        "status": "APPLIED_AND_REVIEWED_INTERNAL",
        "scope": "Six Unit 2 formal-metalinguistic questions re-adjudicated against current canonical data and converted to operational A1 tasks; no passage prose or lexical-target changes.",
        "historical_reference_only": "repair/arabic-a1-u02-metalinguistic-2026-08-20:reading/audit/arabic_a1_u02_metalinguistic_repair_2026-08-20.json",
        "source_sha256": EXPECTED_SHA256,
        "result_sha256": sha256(after_bytes),
        "passages_in_scope": 6,
        "questions_repaired": 6,
        "repairs": changed,
        "post_repair_formal_question_types_in_unit": 0,
        "records_outside_unit_byte_identical": True,
        "quality_interpretation": "Internal bounded remediation only; independent native/educator/model-family/blind review remains required.",
        "release_claim": False,
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
