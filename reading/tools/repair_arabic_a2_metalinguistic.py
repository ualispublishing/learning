#!/usr/bin/env python3
"""Re-adjudicate and repair the historical Arabic A2 low-level metalinguistic set.

The ten historical per-unit repair ledgers are candidate/reference evidence only.
This script requires all 83 historical repair items and the single adjudicated
reading-comprehension false positive to still match current canonical Q/A after NFC
normalization. It applies only the 83 operational replacements. Passage prose and
lexical metadata are protected, untargeted records remain byte-identical, and the
legacy grammar_function label on the bound comprehension false positive is preserved.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "a2" / "passages.jsonl"
AUDIT = ROOT / "reading" / "audit" / "arabic_a2_metalinguistic_repair_2026-08-30.json"
EXPECTED_SHA256 = "f495f15291380487411724471db0efdaeb3ecf333f4c57e3c278a7bb14a11c59"
EXPECTED_REPAIRS = 83
EXPECTED_FORMAL_TYPED_BEFORE = 82
EXPECTED_ADJUDICATED_FALSE_POSITIVES = 1
FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}

BRANCHES = {
    unit: f"origin/repair/arabic-a2-u{unit:02d}-metalinguistic-{'2026-08-21' if unit <= 8 else '2026-08-22'}"
    for unit in range(1, 11)
}
LEDGER_PATH_OVERRIDES = {
    10: "reading/audit/manifests/arabic_a2_u10_metalinguistic_2026-08-22.json",
}
EXPLICIT_FORMAL_PATTERNS = [
    re.compile(p) for p in (
        r"التصنيف\s+النحوي",
        r"الوظيفة\s+النحوية",
        r"ما\s+وظيفة\s+«",
        r"ما\s+نوع\s+«",
        r"ما\s+نوع\s+كلمة",
        r"من\s+صاحب\s+الفعل",
        r"ما\s+صيغة\s+العدد",
        r"ما\s+الكلمة\s+التي\s+تنفي\s+الفعل",
    )
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def protected_snapshot(record: dict) -> dict:
    snap = copy.deepcopy(record)
    snap.pop("questions", None)
    snap.pop("answer_key", None)
    snap.pop("revision", None)
    if isinstance(snap.get("quality"), dict):
        snap["quality"].pop("notes", None)
    return snap


def git_text(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def load_unit_ledger(unit: int) -> tuple[str, str, dict]:
    ref = BRANCHES[unit]
    if unit in LEDGER_PATH_OVERRIDES:
        path = LEDGER_PATH_OVERRIDES[unit]
        ledger = json.loads(git_text(["show", f"{ref}:{path}"]))
        return ref, path, ledger

    listing = git_text(["ls-tree", "-r", "--name-only", ref, "--", "reading/audit"])
    prefix = f"reading/audit/arabic_a2_u{unit:02d}_metalinguistic_repair_"
    matches = [line for line in listing.splitlines() if line.startswith(prefix) and line.endswith(".json")]
    if len(matches) != 1:
        raise SystemExit(f"Unit {unit}: expected exactly one historical repair ledger, found {matches}")
    path = matches[0]
    ledger = json.loads(git_text(["show", f"{ref}:{path}"]))
    return ref, path, ledger


def main() -> int:
    before_bytes = PATH.read_bytes()
    if sha256(before_bytes) != EXPECTED_SHA256:
        raise SystemExit("Arabic A2 canonical hash drifted; refusing A2 remediation batch")

    raw_lines = PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    if len(raw_lines) != 60:
        raise SystemExit(f"Expected 60 Arabic A2 records, found {len(raw_lines)}")
    records = [json.loads(line) for line in raw_lines]
    if [r.get("sequence") for r in records] != list(range(1, 61)):
        raise SystemExit("Arabic A2 sequence drift")
    if any(r.get("unit") != (idx // 6) + 1 for idx, r in enumerate(records)):
        raise SystemExit("Arabic A2 unit layout drift")

    repair_specs = []
    false_positive_specs = []
    source_ledgers = []
    for unit in range(1, 11):
        ref, path, ledger = load_unit_ledger(unit)
        if ledger.get("unit") != unit:
            raise SystemExit(f"Unit {unit}: historical ledger unit mismatch")
        repairs = ledger.get("repairs")
        count = ledger.get("repairs_applied", len(repairs or []))
        if not isinstance(repairs, list) or count != len(repairs):
            raise SystemExit(f"Unit {unit}: historical repair count mismatch")
        if ledger.get("passage_text_changed") not in (False, None):
            raise SystemExit(f"Unit {unit}: historical ledger includes passage-text changes")
        false_positives = ledger.get("false_positives", [])
        if not isinstance(false_positives, list):
            raise SystemExit(f"Unit {unit}: false_positives must be a list when present")
        source_ledgers.append({
            "unit": unit,
            "ref": ref,
            "artifact": path,
            "repairs": count,
            "adjudicated_false_positives": len(false_positives),
        })
        for item in repairs:
            repair_specs.append((unit, item))
        for item in false_positives:
            false_positive_specs.append((unit, item))

    if len(repair_specs) != EXPECTED_REPAIRS:
        raise SystemExit(f"Historical A2 ledgers yield {len(repair_specs)} repair items, expected 83")
    if len(false_positive_specs) != EXPECTED_ADJUDICATED_FALSE_POSITIVES:
        raise SystemExit(
            f"Historical A2 ledgers yield {len(false_positive_specs)} adjudicated false positives, expected 1"
        )

    before_type_counts = Counter(item["before"].get("type") for _, item in repair_specs)
    formal_typed = sum(count for typ, count in before_type_counts.items() if typ in FORMAL_TYPES)
    if formal_typed != EXPECTED_FORMAL_TYPED_BEFORE:
        raise SystemExit(f"Expected 82 formal-typed A2 repair items, historical ledgers contain {formal_typed}")
    nonformal_candidates = [
        {
            "unit": unit,
            "passage_id": item["passage_id"],
            "question_id": item["question_id"],
            "type": item["before"].get("type"),
            "prompt": item["before"].get("prompt"),
        }
        for unit, item in repair_specs
        if item["before"].get("type") not in FORMAL_TYPES
    ]
    if len(nonformal_candidates) != 1:
        raise SystemExit(f"Expected exactly one prompt-pattern repair item outside formal types, found {nonformal_candidates}")

    record_by_id = {r["id"]: r for r in records}
    protected_before = {r["id"]: protected_snapshot(r) for r in records}
    repair_keys = {(item["passage_id"], item["question_id"]) for _, item in repair_specs}
    if len(repair_keys) != EXPECTED_REPAIRS:
        raise SystemExit("Historical A2 repair items contain duplicate passage/question keys")

    adjudicated_false_positives = []
    false_positive_keys = set()
    for unit, item in false_positive_specs:
        rid, qid = item["passage_id"], item["question_id"]
        key = (rid, qid)
        if key in repair_keys:
            raise SystemExit(f"{rid}/{qid}: item cannot be both repair and false positive")
        record = record_by_id.get(rid)
        if record is None or record.get("unit") != unit:
            raise SystemExit(f"{rid}/{qid}: false-positive current record missing or unit drifted")
        q_by_id = {q["id"]: q for q in record["questions"]}
        a_by_qid = {a["question_id"]: a for a in record["answer_key"]}
        if qid not in q_by_id or qid not in a_by_qid:
            raise SystemExit(f"{rid}/{qid}: false-positive Q/A linkage missing")
        q, ans = q_by_id[qid], a_by_qid[qid]
        if nfc(q.get("prompt", "")) != nfc(item.get("prompt", "")) or q.get("type") != item.get("type"):
            raise SystemExit(f"{rid}/{qid}: adjudicated false-positive question drifted")
        if nfc(ans.get("answer", "")) != nfc(item.get("answer", "")):
            raise SystemExit(f"{rid}/{qid}: adjudicated false-positive answer drifted")
        if q.get("type") not in FORMAL_TYPES:
            raise SystemExit(f"{rid}/{qid}: expected preserved legacy formal-type label")
        false_positive_keys.add(key)
        adjudicated_false_positives.append({
            "unit": unit,
            "passage_id": rid,
            "question_id": qid,
            "type": q.get("type"),
            "prompt": nfc(q.get("prompt", "")),
            "answer": nfc(ans.get("answer", "")),
            "reason": item.get("reason", ""),
        })

    changed_record_ids = set()
    changed = []
    for unit, item in repair_specs:
        rid, qid = item["passage_id"], item["question_id"]
        record = record_by_id.get(rid)
        if record is None or record.get("unit") != unit:
            raise SystemExit(f"{rid}/{qid}: current record missing or unit drifted")
        q_by_id = {q["id"]: q for q in record["questions"]}
        a_by_qid = {a["question_id"]: a for a in record["answer_key"]}
        if qid not in q_by_id or qid not in a_by_qid:
            raise SystemExit(f"{rid}/{qid}: Q/A linkage missing")
        q, ans = q_by_id[qid], a_by_qid[qid]
        old, new = item["before"], item["after"]
        if nfc(q.get("prompt", "")) != nfc(old.get("prompt", "")) or q.get("type") != old.get("type"):
            raise SystemExit(f"{rid}/{qid}: current question diverges from historical repair item")
        if nfc(ans.get("answer", "")) != nfc(old.get("answer", "")):
            raise SystemExit(f"{rid}/{qid}: current answer diverges from historical repair item")
        if new.get("type") in FORMAL_TYPES:
            raise SystemExit(f"{rid}/{qid}: proposed replacement remains a formal question type")

        q["prompt"] = nfc(new["prompt"])
        q["type"] = new["type"]
        ans["answer"] = nfc(new["answer"])
        ans["explanation"] = nfc(new.get("explanation", ans.get("explanation", "")))
        changed_record_ids.add(rid)
        changed.append({
            "unit": unit,
            "passage_id": rid,
            "question_id": qid,
            "old_type": old.get("type"),
            "new_type": new.get("type"),
            "old_prompt": nfc(old.get("prompt", "")),
            "new_prompt": nfc(new.get("prompt", "")),
            "new_answer": nfc(new.get("answer", "")),
        })

    if len(changed) != EXPECTED_REPAIRS:
        raise SystemExit(f"Applied {len(changed)} A2 repairs, expected 83")

    note = "2026-08-30 A2 low-level metalinguistic remediation: 83 historical repair items re-adjudicated against current canonical Q/A (NFC-equivalent matching) and rewritten as operational A2 tasks; one exact legacy-type reading-comprehension false positive preserved; prose/targets unchanged."
    for rid in changed_record_ids:
        record = record_by_id[rid]
        if note not in record["quality"].setdefault("notes", []):
            record["quality"]["notes"].append(note)
        record["revision"] = int(record.get("revision", 0)) + 1
        if protected_snapshot(record) != protected_before[rid]:
            raise SystemExit(f"{rid}: protected prose/target/metadata fields changed")

    for record in records:
        if len(record.get("questions", [])) != 10 or len(record.get("answer_key", [])) != 10:
            raise SystemExit(f"{record['id']}: Q/A count drift")
        qids = {q["id"] for q in record["questions"]}
        if qids != {f"q{i}" for i in range(1, 11)}:
            raise SystemExit(f"{record['id']}: question ID drift")
        if any(a["question_id"] not in qids for a in record["answer_key"]):
            raise SystemExit(f"{record['id']}: answer linkage drift")

    formal_after = [
        {"passage_id": r["id"], "question_id": q["id"], "type": q["type"], "prompt": nfc(q.get("prompt", ""))}
        for r in records
        for q in r["questions"]
        if q.get("type") in FORMAL_TYPES
    ]
    formal_after_keys = {(item["passage_id"], item["question_id"]) for item in formal_after}
    unresolved_formal = [
        item for item in formal_after if (item["passage_id"], item["question_id"]) not in false_positive_keys
    ]
    if unresolved_formal:
        raise SystemExit(f"Unadjudicated formal question types remain in A2: {unresolved_formal[:10]}")
    if formal_after_keys != false_positive_keys:
        raise SystemExit(
            f"Preserved formal-type bindings do not exactly equal adjudicated false positives: "
            f"formal={formal_after_keys}, false_positives={false_positive_keys}"
        )

    explicit_after = []
    for record in records:
        for q in record["questions"]:
            key = (record["id"], q["id"])
            prompt = nfc(q.get("prompt", ""))
            hits = [pat.pattern for pat in EXPLICIT_FORMAL_PATTERNS if pat.search(prompt)]
            if hits and key not in false_positive_keys:
                explicit_after.append({
                    "passage_id": record["id"],
                    "question_id": q["id"],
                    "type": q.get("type"),
                    "prompt": prompt,
                    "patterns": hits,
                })
    if explicit_after:
        raise SystemExit(f"Unadjudicated explicit formal prompt patterns remain in A2: {explicit_after[:10]}")

    out_lines = list(raw_lines)
    for idx, record in enumerate(records):
        if record["id"] not in changed_record_ids:
            continue
        newline = "\n" if raw_lines[idx].endswith("\n") else ""
        out_lines[idx] = json.dumps(record, ensure_ascii=False) + newline
    PATH.write_text("".join(out_lines), encoding="utf-8")
    after_bytes = PATH.read_bytes()
    after_lines = after_bytes.splitlines(keepends=True)
    for idx, original_line in enumerate(raw_lines):
        rid = records[idx]["id"]
        if rid not in changed_record_ids and after_lines[idx] != original_line.encode("utf-8"):
            raise SystemExit(f"Untargeted A2 record {rid} changed bytewise")
    if unicodedata.normalize("NFC", PATH.read_text(encoding="utf-8")) != PATH.read_text(encoding="utf-8"):
        raise SystemExit("A2 batch reintroduced non-NFC text")

    by_unit = Counter(item["unit"] for item in changed)
    type_counts_after = Counter(q["type"] for r in records for q in r["questions"])
    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "level": "A2",
        "units": list(range(1, 11)),
        "date": "2026-08-30",
        "status": "APPLIED_AND_REVIEWED_INTERNAL",
        "scope": "Current-corpus re-adjudication and bounded Q/A remediation of 83 historical A2 low-level repair items, with one exact historical reading-comprehension false positive preserved and revalidated.",
        "source_sha256": EXPECTED_SHA256,
        "result_sha256": sha256(after_bytes),
        "historical_reference_ledgers": source_ledgers,
        "historical_ledgers_used_as_reference_only": True,
        "repairs_applied": len(changed),
        "historical_adjudicated_false_positives_checked": len(adjudicated_false_positives),
        "repairs_by_unit": {str(k): v for k, v in sorted(by_unit.items())},
        "historical_candidate_type_counts_before": dict(sorted((str(k), v) for k, v in before_type_counts.items())),
        "nonformal_prompt_pattern_repair_item_before": nonformal_candidates,
        "changed_passages": len(changed_record_ids),
        "untargeted_records_byte_identical": True,
        "formal_type_labels_after_full_a2": len(formal_after),
        "adjudicated_comprehension_false_positives_after": len(adjudicated_false_positives),
        "adjudicated_false_positives": adjudicated_false_positives,
        "unresolved_metalinguistic_defects_after": 0,
        "explicit_formal_prompt_pattern_findings_after": 0,
        "a2_questions_checked": 600,
        "a2_answers_checked": 600,
        "question_type_counts_after": dict(sorted(type_counts_after.items())),
        "repairs": changed,
        "quality_interpretation": "Internal substantive Q/A remediation only. This closes the historically identified A2 repair set under current-corpus guards while preserving one explicitly adjudicated reading-comprehension false positive with a legacy type label; CEFR, naturalness, semantic educator, independent native/model/tool, and blind review remain separate release requirements.",
        "release_claim": False,
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in audit.items() if k != "repairs"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
