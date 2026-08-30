#!/usr/bin/env python3
"""Re-adjudicate and repair Arabic A1 Units 3-10 formal-metalinguistic items.

Historical unit repair ledgers are read from their Git branches as candidate/reference
data only. Every historical before-prompt/type/answer must still match current
canonical content. Only the corresponding question prompt/type, answer/explanation,
record revision, and quality notes may change. Passage prose and lexical metadata are
protected. Units 1-2 remain byte-identical.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
AUDIT = ROOT / "reading" / "audit" / "arabic_a1_u03_u10_metalinguistic_repair_2026-08-30.json"
EXPECTED_SHA256 = "8bd13aa32de72cf1d3f12dc5848976b62288ec289e7535e20fdb78e1f1dbc131"
EXPECTED_REPAIRS = 48
EXPECTED_TOTAL_A1_FORMAL_BEFORE = 48  # Units 1-2 already remediated.
FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}

HISTORICAL = {
    unit: (
        f"origin/repair/arabic-a1-u{unit:02d}-metalinguistic-2026-08-20",
        f"reading/audit/arabic_a1_u{unit:02d}_metalinguistic_repair_2026-08-20.json",
    )
    for unit in range(3, 11)
}
EXPECTED_BY_UNIT = {3: 6, 4: 7, 5: 6, 6: 6, 7: 6, 8: 6, 9: 5, 10: 6}


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


def git_show(ref: str, path: str) -> dict:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"Could not read historical reference {ref}:{path}: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def main() -> int:
    before_bytes = PATH.read_bytes()
    if sha256(before_bytes) != EXPECTED_SHA256:
        raise SystemExit("Arabic A1 canonical hash drifted; refusing Units 3-10 batch")

    raw_lines = PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    if len(raw_lines) != 60:
        raise SystemExit(f"Expected 60 Arabic A1 records, found {len(raw_lines)}")
    records = [json.loads(line) for line in raw_lines]
    if [r.get("sequence") for r in records] != list(range(1, 61)):
        raise SystemExit("Arabic A1 sequence drift")

    formal_before = [
        (r["id"], q["id"], q["type"])
        for r in records[12:]
        for q in r.get("questions", [])
        if q.get("type") in FORMAL_TYPES
    ]
    if len(formal_before) != EXPECTED_TOTAL_A1_FORMAL_BEFORE:
        raise SystemExit(f"Expected 48 remaining formal-type questions in Units 3-10, found {len(formal_before)}")

    repair_specs = []
    historical_sources = []
    for unit, (ref, artifact_path) in HISTORICAL.items():
        ledger = git_show(ref, artifact_path)
        if ledger.get("unit") != unit or ledger.get("repairs_applied") != EXPECTED_BY_UNIT[unit]:
            raise SystemExit(f"Unit {unit}: historical ledger scope/count mismatch")
        if ledger.get("passage_text_changed") is not False:
            raise SystemExit(f"Unit {unit}: historical ledger is not question-only")
        historical_sources.append({"unit": unit, "ref": ref, "artifact": artifact_path, "repairs": ledger["repairs_applied"]})
        for item in ledger["repairs"]:
            repair_specs.append((unit, item))

    if len(repair_specs) != EXPECTED_REPAIRS:
        raise SystemExit(f"Historical ledgers yielded {len(repair_specs)} repairs, expected {EXPECTED_REPAIRS}")

    record_by_id = {r["id"]: r for r in records}
    protected_before = {r["id"]: protected_snapshot(r) for r in records[12:]}
    untouched_prefix = b"".join(line.encode("utf-8") for line in raw_lines[:12])
    changed_record_ids = set()
    changed = []

    for unit, item in repair_specs:
        rid = item["passage_id"]
        qid = item["question_id"]
        record = record_by_id.get(rid)
        if record is None or record.get("unit") != unit:
            raise SystemExit(f"{rid}/{qid}: current record missing or unit drifted")
        q_by_id = {q["id"]: q for q in record["questions"]}
        a_by_qid = {a["question_id"]: a for a in record["answer_key"]}
        if qid not in q_by_id or qid not in a_by_qid:
            raise SystemExit(f"{rid}/{qid}: Q/A linkage missing")
        q = q_by_id[qid]
        ans = a_by_qid[qid]
        old = item["before"]
        new = item["after"]
        if q.get("prompt") != old.get("prompt") or q.get("type") != old.get("type"):
            raise SystemExit(f"{rid}/{qid}: current question no longer matches historical candidate; refusing batch")
        if ans.get("answer") != old.get("answer"):
            raise SystemExit(f"{rid}/{qid}: current answer no longer matches historical candidate; refusing batch")
        if q.get("type") not in FORMAL_TYPES:
            raise SystemExit(f"{rid}/{qid}: candidate is no longer a formal metalinguistic type")
        if new.get("type") in FORMAL_TYPES:
            raise SystemExit(f"{rid}/{qid}: proposed replacement remains formal metalinguistic")

        q["prompt"] = new["prompt"]
        q["type"] = new["type"]
        ans["answer"] = new["answer"]
        ans["explanation"] = new.get("explanation", ans.get("explanation", ""))
        changed_record_ids.add(rid)
        changed.append({
            "unit": unit,
            "passage_id": rid,
            "question_id": qid,
            "old_type": old["type"],
            "new_type": new["type"],
            "old_prompt": old["prompt"],
            "new_prompt": new["prompt"],
            "new_answer": new["answer"],
        })

    if len(changed) != EXPECTED_REPAIRS:
        raise SystemExit(f"Applied {len(changed)} repairs, expected {EXPECTED_REPAIRS}")

    note = "2026-08-30 A1 Units 3-10 metalinguistic remediation: historical candidates re-adjudicated against current canonical Q/A; formal-label items converted to operational A1 tasks; prose/targets preserved."
    for rid in changed_record_ids:
        record = record_by_id[rid]
        if note not in record["quality"].setdefault("notes", []):
            record["quality"]["notes"].append(note)
        record["revision"] = int(record.get("revision", 0)) + 1
        if protected_snapshot(record) != protected_before[rid]:
            raise SystemExit(f"{rid}: protected prose/target/metadata fields changed")

    for record in records:
        if len(record.get("questions", [])) != 10 or len(record.get("answer_key", [])) != 10:
            raise SystemExit(f"{record['id']}: question/answer count drift")
        qids = {q["id"] for q in record["questions"]}
        if qids != {f"q{i}" for i in range(1, 11)}:
            raise SystemExit(f"{record['id']}: question IDs drift")
        if any(a["question_id"] not in qids for a in record["answer_key"]):
            raise SystemExit(f"{record['id']}: answer linkage drift")

    formal_after = [
        (r["id"], q["id"], q["type"], q.get("prompt"))
        for r in records
        for q in r.get("questions", [])
        if q.get("type") in FORMAL_TYPES
    ]
    if formal_after:
        raise SystemExit(f"Formal metalinguistic question types remain in A1: {formal_after[:10]}")

    out_lines = list(raw_lines)
    for idx, record in enumerate(records):
        if record["id"] not in changed_record_ids:
            continue
        newline = "\n" if raw_lines[idx].endswith("\n") else ""
        out_lines[idx] = json.dumps(record, ensure_ascii=False) + newline
    PATH.write_text("".join(out_lines), encoding="utf-8")
    after_bytes = PATH.read_bytes()
    after_lines = after_bytes.splitlines(keepends=True)
    if b"".join(after_lines[:12]) != untouched_prefix:
        raise SystemExit("Units 1-2 changed bytewise during Units 3-10 batch")

    for idx, original_line in enumerate(raw_lines[12:], start=12):
        rid = records[idx]["id"]
        if rid not in changed_record_ids and after_lines[idx] != original_line.encode("utf-8"):
            raise SystemExit(f"Untargeted record {rid} changed bytewise")

    by_unit = Counter(item["unit"] for item in changed)
    if dict(sorted(by_unit.items())) != EXPECTED_BY_UNIT:
        raise SystemExit(f"Applied unit distribution drift: {dict(sorted(by_unit.items()))}")

    type_counts_after = Counter(q["type"] for r in records for q in r["questions"])
    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "level": "A1",
        "units": list(range(3, 11)),
        "date": "2026-08-30",
        "status": "APPLIED_AND_REVIEWED_INTERNAL",
        "scope": "Current-corpus re-adjudication and bounded Q/A remediation of all remaining formal-metalinguistic A1 candidates in Units 3-10.",
        "source_sha256": EXPECTED_SHA256,
        "result_sha256": sha256(after_bytes),
        "historical_reference_ledgers": historical_sources,
        "historical_ledgers_used_as_reference_only": True,
        "repairs_applied": len(changed),
        "repairs_by_unit": {str(k): v for k, v in sorted(by_unit.items())},
        "changed_passages": len(changed_record_ids),
        "units_1_2_byte_identical": True,
        "untargeted_records_byte_identical": True,
        "formal_question_types_before_batch": len(formal_before),
        "formal_question_types_after_full_a1": 0,
        "a1_questions_checked": 600,
        "a1_answers_checked": 600,
        "question_type_counts_after": dict(sorted(type_counts_after.items())),
        "repairs": changed,
        "quality_interpretation": "Internal substantive Q/A remediation only. This closes the known A1 formal-type candidate class, not CEFR/naturalness/independent educator release review.",
        "release_claim": False,
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in audit.items() if k != "repairs"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
