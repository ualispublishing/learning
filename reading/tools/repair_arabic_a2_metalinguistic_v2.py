#!/usr/bin/env python3
"""Bounded Arabic A2 low-level metalinguistic remediation with inventory reconciliation.

The original inventory contains 83 candidates. Historical unit adjudications establish
80 confirmed repairs and 3 false positives. This runner binds both sets to current
canonical Q/A, applies only the 80 confirmed repairs, preserves the 3 exclusions, and
fails closed on any unexplained inventory or canonical drift.
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
INVENTORY_REF = "origin/audit/arabic-a2-formal-inventory-2026-08-21"
INVENTORY_PATH = "reading/audit/arabic_a2_formal_inventory_2026-08-21.json"
EXPECTED_SHA256 = "f495f15291380487411724471db0efdaeb3ecf333f4c57e3c278a7bb14a11c59"
EXPECTED_INVENTORY = 83
EXPECTED_REPAIRS = 80
EXPECTED_FALSE_POSITIVES = 3
FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}
EXPECTED_FP_KEYS = {
    ("ar-a2-u01-p02", "q4"),
    ("ar-a2-u09-p06", "q10"),
    ("ar-a2-u10-p06", "q9"),
}
UNIT_REFS = {
    **{u: f"origin/repair/arabic-a2-u{u:02d}-metalinguistic-2026-08-21" for u in range(1, 9)},
    9: "origin/repair/arabic-a2-u09-metalinguistic-2026-08-22",
    10: "origin/repair/arabic-a2-u10-manifest-2026-08-22",
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


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_text(args: list[str]) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def protected_snapshot(record: dict) -> dict:
    snap = copy.deepcopy(record)
    snap.pop("questions", None)
    snap.pop("answer_key", None)
    snap.pop("revision", None)
    if isinstance(snap.get("quality"), dict):
        snap["quality"].pop("notes", None)
    return snap


def load_unit_ledger(unit: int) -> tuple[str, str, dict]:
    ref = UNIT_REFS[unit]
    listing = git_text(["ls-tree", "-r", "--name-only", ref, "--", "reading/audit"])
    prefix = f"reading/audit/arabic_a2_u{unit:02d}_metalinguistic_repair_"
    matches = [x for x in listing.splitlines() if x.startswith(prefix) and x.endswith(".json")]
    if len(matches) != 1:
        raise SystemExit(f"Unit {unit}: expected one repair ledger, found {matches}")
    path = matches[0]
    return ref, path, json.loads(git_text(["show", f"{ref}:{path}"]))


def item_key(item: dict) -> tuple[str, str]:
    return item["passage_id"], item["question_id"]


def main() -> int:
    before_bytes = PATH.read_bytes()
    if sha256(before_bytes) != EXPECTED_SHA256:
        raise SystemExit("Arabic A2 canonical hash drifted; refusing remediation")

    raw_lines = PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    records = [json.loads(x) for x in raw_lines]
    if len(records) != 60 or [r.get("sequence") for r in records] != list(range(1, 61)):
        raise SystemExit("Arabic A2 record/sequence drift")
    if any(r.get("unit") != i // 6 + 1 for i, r in enumerate(records)):
        raise SystemExit("Arabic A2 unit-layout drift")
    by_id = {r["id"]: r for r in records}
    protected_before = {r["id"]: protected_snapshot(r) for r in records}

    inventory = json.loads(git_text(["show", f"{INVENTORY_REF}:{INVENTORY_PATH}"]))
    findings = inventory.get("findings", [])
    if inventory.get("finding_count") != EXPECTED_INVENTORY or len(findings) != EXPECTED_INVENTORY:
        raise SystemExit("Original A2 inventory is not exactly 83 candidates")
    inventory_keys = {item_key(x) for x in findings}
    if len(inventory_keys) != EXPECTED_INVENTORY:
        raise SystemExit("Original A2 inventory contains duplicate keys")

    repair_specs: list[tuple[int, dict]] = []
    fp_specs: list[tuple[int, dict]] = []
    source_ledgers = []
    for unit in range(1, 11):
        ref, path, ledger = load_unit_ledger(unit)
        if ledger.get("unit") != unit or ledger.get("passage_text_changed") not in (False, None):
            raise SystemExit(f"Unit {unit}: ledger scope drift")
        repairs = ledger.get("repairs", [])
        confirmed = ledger.get("confirmed_repairs", ledger.get("repairs_applied", len(repairs)))
        fps = ledger.get("adjudicated_false_positives", ledger.get("false_positives", []))
        if not isinstance(repairs, list) or confirmed != len(repairs) or not isinstance(fps, list):
            raise SystemExit(f"Unit {unit}: malformed adjudication ledger")
        expected_unit = int(inventory.get("by_unit", {}).get(str(unit), -1))
        ledger_inventory = ledger.get("inventory_candidates", len(repairs) + len(fps))
        if expected_unit < 0 or ledger_inventory != expected_unit or len(repairs) + len(fps) != expected_unit:
            raise SystemExit(f"Unit {unit}: inventory accounting mismatch")
        repair_specs.extend((unit, x) for x in repairs)
        fp_specs.extend((unit, x) for x in fps)
        source_ledgers.append({"unit": unit, "ref": ref, "artifact": path, "inventory": expected_unit, "repairs": len(repairs), "false_positives": len(fps)})

    repair_keys = {item_key(x) for _, x in repair_specs}
    fp_keys = {item_key(x) for _, x in fp_specs}
    if len(repair_specs) != EXPECTED_REPAIRS or len(repair_keys) != EXPECTED_REPAIRS:
        raise SystemExit(f"Historical adjudication yields {len(repair_specs)} repairs, expected 80")
    if len(fp_specs) != EXPECTED_FALSE_POSITIVES or fp_keys != EXPECTED_FP_KEYS:
        raise SystemExit(f"False-positive set mismatch: {sorted(fp_keys)}")
    if repair_keys & fp_keys or repair_keys | fp_keys != inventory_keys:
        raise SystemExit("80 repairs + 3 exclusions do not exactly partition the 83-item inventory")

    inventory_by_key = {item_key(x): x for x in findings}
    adjudicated_fps = []
    for unit, item in fp_specs:
        rid, qid = item_key(item)
        rec = by_id.get(rid)
        if rec is None or rec.get("unit") != unit:
            raise SystemExit(f"{rid}/{qid}: excluded record drift")
        q = next((x for x in rec["questions"] if x["id"] == qid), None)
        a = next((x for x in rec["answer_key"] if x["question_id"] == qid), None)
        inv = inventory_by_key[(rid, qid)]
        if not q or not a:
            raise SystemExit(f"{rid}/{qid}: excluded Q/A linkage missing")
        if nfc(q.get("prompt", "")) != nfc(item.get("prompt", inv.get("prompt", ""))) or q.get("type") != item.get("type", inv.get("type")):
            raise SystemExit(f"{rid}/{qid}: excluded question diverged")
        expected_answer = item.get("answer", inv.get("answer", ""))
        if nfc(a.get("answer", "")) != nfc(expected_answer):
            raise SystemExit(f"{rid}/{qid}: excluded answer diverged")
        adjudicated_fps.append({"unit": unit, "passage_id": rid, "question_id": qid, "type": q.get("type"), "prompt": nfc(q.get("prompt", "")), "answer": nfc(a.get("answer", "")), "reason": item.get("reason", "")})

    changed_records = set()
    changes = []
    for unit, item in repair_specs:
        rid, qid = item_key(item)
        rec = by_id.get(rid)
        if rec is None or rec.get("unit") != unit:
            raise SystemExit(f"{rid}/{qid}: repair record drift")
        q = next((x for x in rec["questions"] if x["id"] == qid), None)
        a = next((x for x in rec["answer_key"] if x["question_id"] == qid), None)
        if not q or not a:
            raise SystemExit(f"{rid}/{qid}: repair Q/A linkage missing")
        old, new = item["before"], item["after"]
        inv = inventory_by_key[(rid, qid)]
        if nfc(q.get("prompt", "")) != nfc(old.get("prompt", "")) or q.get("type") != old.get("type"):
            raise SystemExit(f"{rid}/{qid}: current question diverges from repair ledger")
        if nfc(a.get("answer", "")) != nfc(old.get("answer", "")):
            raise SystemExit(f"{rid}/{qid}: current answer diverges from repair ledger")
        if nfc(inv.get("prompt", "")) != nfc(old.get("prompt", "")) or inv.get("type") != old.get("type"):
            raise SystemExit(f"{rid}/{qid}: repair ledger no longer binds to original inventory")
        if new.get("type") in FORMAL_TYPES:
            raise SystemExit(f"{rid}/{qid}: replacement remains formal-label type")
        q["prompt"] = nfc(new["prompt"])
        q["type"] = new["type"]
        a["answer"] = nfc(new["answer"])
        a["explanation"] = nfc(new.get("explanation", a.get("explanation", "")))
        changed_records.add(rid)
        changes.append({"unit": unit, "passage_id": rid, "question_id": qid, "old_type": old.get("type"), "new_type": new.get("type"), "old_prompt": nfc(old.get("prompt", "")), "new_prompt": nfc(new.get("prompt", "")), "new_answer": nfc(new.get("answer", ""))})

    if len(changes) != EXPECTED_REPAIRS:
        raise SystemExit("Applied repair count is not 80")

    note = "2026-08-30 A2 low-level metalinguistic remediation: original 83-item inventory reconciled as 80 confirmed operational Q/A repairs plus 3 documented comprehension false positives; passage prose and lexical targets preserved."
    for rid in changed_records:
        rec = by_id[rid]
        rec.setdefault("quality", {}).setdefault("notes", [])
        if note not in rec["quality"]["notes"]:
            rec["quality"]["notes"].append(note)
        rec["revision"] = int(rec.get("revision", 0)) + 1
        if protected_snapshot(rec) != protected_before[rid]:
            raise SystemExit(f"{rid}: protected prose/target metadata changed")

    for rec in records:
        qs, ans = rec.get("questions", []), rec.get("answer_key", [])
        if len(qs) != 10 or len(ans) != 10:
            raise SystemExit(f"{rec['id']}: Q/A count drift")
        qids = {q.get("id") for q in qs}
        if qids != {f"q{i}" for i in range(1, 11)}:
            raise SystemExit(f"{rec['id']}: question id drift")
        if {a.get("question_id") for a in ans} != qids:
            raise SystemExit(f"{rec['id']}: answer linkage drift")

    formal_after = [
        {"passage_id": rec["id"], "question_id": q["id"], "type": q.get("type"), "prompt": nfc(q.get("prompt", ""))}
        for rec in records for q in rec["questions"] if q.get("type") in FORMAL_TYPES
    ]
    formal_after_keys = {(x["passage_id"], x["question_id"]) for x in formal_after}
    expected_formal_fp_keys = {key for key in fp_keys if inventory_by_key[key].get("type") in FORMAL_TYPES}
    if formal_after_keys != expected_formal_fp_keys:
        raise SystemExit(f"Unadjudicated formal-type labels remain: {formal_after}")

    explicit_unadjudicated = []
    for rec in records:
        for q in rec["questions"]:
            key = (rec["id"], q["id"])
            hits = [p.pattern for p in EXPLICIT_FORMAL_PATTERNS if p.search(nfc(q.get("prompt", "")))]
            if hits and key not in fp_keys:
                explicit_unadjudicated.append({"passage_id": rec["id"], "question_id": q["id"], "prompt": q.get("prompt"), "patterns": hits})
    if explicit_unadjudated := explicit_unadjudicated:
        raise SystemExit(f"Unadjudicated explicit formal-prompt patterns remain: {explicit_unadjudated[:10]}")

    out = list(raw_lines)
    for i, rec in enumerate(records):
        if rec["id"] in changed_records:
            out[i] = json.dumps(rec, ensure_ascii=False) + ("\n" if raw_lines[i].endswith("\n") else "")
    PATH.write_text("".join(out), encoding="utf-8")
    after_bytes = PATH.read_bytes()
    after_lines = after_bytes.splitlines(keepends=True)
    for i, original in enumerate(raw_lines):
        if records[i]["id"] not in changed_records and after_lines[i] != original.encode("utf-8"):
            raise SystemExit(f"Untargeted record {records[i]['id']} changed bytewise")
    if unicodedata.normalize("NFC", PATH.read_text(encoding="utf-8")) != PATH.read_text(encoding="utf-8"):
        raise SystemExit("A2 remediation reintroduced non-NFC text")

    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "level": "A2",
        "date": "2026-08-30",
        "status": "APPLIED_AND_REVIEWED_INTERNAL",
        "scope": "Bounded current-corpus reconciliation of the original 83-item A2 low-level metalinguistic inventory.",
        "source_sha256": EXPECTED_SHA256,
        "result_sha256": sha256(after_bytes),
        "original_inventory": {"artifact": INVENTORY_PATH, "ref": INVENTORY_REF, "candidates": EXPECTED_INVENTORY},
        "historical_reference_ledgers": source_ledgers,
        "inventory_accounting": {"candidates": EXPECTED_INVENTORY, "confirmed_repairs": EXPECTED_REPAIRS, "adjudicated_false_positives": EXPECTED_FALSE_POSITIVES, "accounted": EXPECTED_REPAIRS + EXPECTED_FALSE_POSITIVES},
        "repairs_applied": len(changes),
        "adjudicated_false_positive_count": len(adjudicated_fps),
        "adjudicated_false_positives": adjudicated_fps,
        "changed_passages": len(changed_records),
        "untargeted_records_byte_identical": True,
        "a2_questions_checked": 600,
        "a2_answers_checked": 600,
        "formal_type_labels_remaining": len(formal_after),
        "formal_type_labels_remaining_are_exact_adjudicated_false_positives": True,
        "unadjudicated_formal_type_labels_remaining": 0,
        "unadjudicated_explicit_formal_prompt_patterns_remaining": 0,
        "question_type_counts_after": dict(sorted(Counter(q["type"] for r in records for q in r["questions"]).items())),
        "repairs": changes,
        "quality_interpretation": "This closes only the historically inventoried A2 low-level candidate set. The two retained grammar_function labels are documented comprehension false positives, not unresolved grammar-label tasks. CEFR, naturalness, semantic educator, independent native/model-family, and blind review remain separate release requirements.",
        "release_claim": False,
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in audit.items() if k != "repairs"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
