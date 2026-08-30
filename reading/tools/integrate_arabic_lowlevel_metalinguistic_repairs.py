#!/usr/bin/env python3
"""Integrate and revalidate the historical Arabic A1/A2 metalinguistic unit repairs.

The historical repairs were intentionally left on 20 isolated branches. This tool
integrates them only when every branch proves to be an exact unit-local Q/A repair
against the historical candidate baseline, with zero formal-metalinguistic findings
in its own post-repair audit. Current NFC normalization is preserved.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
HIST_AUDIT_BRANCH = "audit/arabic-lowlevel-metalinguistic-2026-08-20"
HIST_CANDIDATE_PATH = "reading/audit/arabic_a1_a2_metalinguistic_candidate_audit_2026-08-20.json"
OUTPUT_REPAIR = READING / "audit" / "arabic_a1_a2_metalinguistic_integrated_repair_2026-08-30.json"
OUTPUT_POST = READING / "audit" / "arabic_a1_a2_metalinguistic_postrepair_2026-08-30.json"
FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_blob_text(text: str) -> str:
    data = text.encode("utf-8")
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def nfc(value):
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [nfc(x) for x in value]
    if isinstance(value, dict):
        return {nfc(k): nfc(v) for k, v in value.items()}
    return value


def git_show(ref: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"origin/{ref}:{path}"], cwd=ROOT, text=True, encoding="utf-8"
    )


def branch_paths(ref: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", f"origin/{ref}", "reading/audit"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def parse_jsonl(text: str) -> list[dict]:
    rows = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL line {lineno}: {exc}") from exc
    return rows


def answer_map(record: dict) -> dict[str, dict]:
    return {a.get("question_id"): a for a in record.get("answer_key", [])}


def strip_qa(record: dict) -> dict:
    return {k: v for k, v in record.items() if k not in {"questions", "answer_key"}}


def branch_for(level: str, unit: int) -> str:
    if level == "a1":
        return f"repair/arabic-a1-u{unit:02d}-metalinguistic-2026-08-20"
    day = "2026-08-21" if unit <= 8 else "2026-08-22"
    return f"repair/arabic-a2-u{unit:02d}-metalinguistic-{day}"


def main() -> int:
    source_audit = json.loads((READING / "audit" / "arabic_fresh_deterministic_revalidation_2026-08-30.json").read_text(encoding="utf-8"))
    if source_audit.get("structural_errors"):
        raise SystemExit("Fresh Arabic deterministic source has structural errors; refusing integration")
    if source_audit.get("finding_classes", {}).get("unicode_not_nfc", 0) != 0:
        raise SystemExit("Current Arabic corpus is not NFC-clean; refusing integration")

    historical = json.loads(git_show(HIST_AUDIT_BRANCH, HIST_CANDIDATE_PATH))
    if historical.get("status") != "CANDIDATE_AUDIT_DO_NOT_AUTOREPAIR":
        raise SystemExit("Historical candidate artifact has unexpected status")
    findings = historical.get("findings", [])
    if len(findings) != 146:
        raise SystemExit(f"Historical candidate count {len(findings)} != 146")
    expected_by_unit: dict[tuple[str, int], set[tuple[str, str]]] = {}
    for finding in findings:
        level = finding["level"].lower()
        seq = int(finding["sequence"])
        unit = (seq - 1) // 6 + 1
        expected_by_unit.setdefault((level, unit), set()).add((finding["passage_id"], finding["question_id"]))

    integrated_texts: dict[str, str] = {}
    repair_units = []
    total_changed_pairs = 0
    before_hashes = {}
    after_hashes = {}

    for level in ("a1", "a2"):
        canonical_path = f"reading/arabic/{level}/passages.jsonl"
        current_text = (ROOT / canonical_path).read_text(encoding="utf-8")
        historical_baseline_text = git_show(HIST_AUDIT_BRANCH, canonical_path)
        current_rows = parse_jsonl(current_text)
        baseline_rows = parse_jsonl(historical_baseline_text)
        if len(current_rows) != 60 or len(baseline_rows) != 60:
            raise SystemExit(f"{level.upper()}: expected exactly 60 rows")

        historical_bound = historical["bound_canonical_hashes"][level.upper()]
        if sha256_text(historical_baseline_text) != historical_bound:
            raise SystemExit(f"{level.upper()}: historical baseline no longer matches candidate audit hash")

        # The only allowed pre-integration drift from the historical baseline is NFC composition.
        normalized_historical = unicodedata.normalize("NFC", historical_baseline_text)
        if normalized_historical != current_text:
            raise SystemExit(f"{level.upper()}: current source differs from the historical candidate baseline beyond NFC normalization")
        if sha256_text(current_text) != source_audit["canonical_hashes"][level]["sha256"]:
            raise SystemExit(f"{level.upper()}: current source hash differs from fresh Arabic audit")

        before_hashes[level] = {
            "sha256": sha256_text(current_text),
            "git_blob": git_blob_text(current_text),
        }
        out_lines = current_text.splitlines(keepends=True)

        for unit in range(1, 11):
            ref = branch_for(level, unit)
            branch_text = git_show(ref, canonical_path)
            branch_rows = parse_jsonl(branch_text)
            if len(branch_rows) != 60:
                raise SystemExit(f"{ref}: canonical file does not contain 60 rows")

            # Find and validate the branch's own final post-repair audit.
            prefix = f"reading/audit/arabic_{level}_u{unit:02d}_metalinguistic_postrepair_"
            post_paths = [p for p in branch_paths(ref) if p.startswith(prefix) and p.endswith(".json")]
            if len(post_paths) != 1:
                raise SystemExit(f"{ref}: expected one postrepair audit, found {post_paths}")
            post = json.loads(git_show(ref, post_paths[0]))
            if post.get("formal_metalinguistic_finding_count") != 0 or not str(post.get("status", "")).startswith("PASS_DETERMINISTIC"):
                raise SystemExit(f"{ref}: postrepair audit is not a zero-finding deterministic PASS")
            if post.get("bound_sha256") != sha256_text(branch_text):
                raise SystemExit(f"{ref}: postrepair audit hash does not bind the branch canonical file")

            start = (unit - 1) * 6
            end = unit * 6
            changed_pairs: set[tuple[str, str]] = set()
            for idx in range(60):
                base = baseline_rows[idx]
                br = branch_rows[idx]
                if idx < start or idx >= end:
                    if br != base:
                        raise SystemExit(f"{ref}: changed record outside Unit {unit}: sequence {idx + 1}")
                    continue
                if nfc(strip_qa(br)) != nfc(strip_qa(base)):
                    raise SystemExit(f"{ref}: Unit {unit} changes fields beyond questions/answer_key at sequence {idx + 1}")

                bq = {q.get("id"): q for q in base.get("questions", [])}
                rq = {q.get("id"): q for q in br.get("questions", [])}
                ba = answer_map(base)
                ra = answer_map(br)
                if set(bq) != set(rq) or set(ba) != set(ra):
                    raise SystemExit(f"{ref}: Q/A IDs changed at {base.get('id')}")
                for qid in bq:
                    if nfc(bq[qid]) != nfc(rq[qid]) or nfc(ba[qid]) != nfc(ra[qid]):
                        changed_pairs.add((base.get("id"), qid))

            expected_pairs = expected_by_unit.get((level, unit), set())
            if changed_pairs != expected_pairs:
                missing = sorted(expected_pairs - changed_pairs)
                extra = sorted(changed_pairs - expected_pairs)
                raise SystemExit(f"{ref}: repair set differs from historical candidate set; missing={missing}, extra={extra}")

            # Apply only this branch's six unit lines, preserving current NFC normalization.
            branch_lines = branch_text.splitlines(keepends=True)
            for idx in range(start, end):
                out_lines[idx] = unicodedata.normalize("NFC", branch_lines[idx])

            total_changed_pairs += len(changed_pairs)
            repair_units.append({
                "level": level.upper(),
                "unit": unit,
                "branch": ref,
                "postrepair_audit": post_paths[0],
                "postrepair_status": post.get("status"),
                "changed_candidate_questions": len(changed_pairs),
            })

        integrated = "".join(out_lines)
        if unicodedata.normalize("NFC", integrated) != integrated:
            raise SystemExit(f"{level.upper()}: integrated output is not NFC normalized")
        rows = parse_jsonl(integrated)
        if [r.get("sequence") for r in rows] != list(range(1, 61)):
            raise SystemExit(f"{level.upper()}: sequence changed during integration")
        if any(len(r.get("questions", [])) != 10 or len(r.get("answer_key", [])) != 10 for r in rows):
            raise SystemExit(f"{level.upper()}: 10-question/10-answer contract changed")
        integrated_texts[level] = integrated
        after_hashes[level] = {
            "sha256": sha256_text(integrated),
            "git_blob": git_blob_text(integrated),
        }

    if total_changed_pairs != 146:
        raise SystemExit(f"Integrated changed candidate pairs {total_changed_pairs} != 146")

    # Full integrated A1/A2 scan: no historical candidate may survive unchanged and no formal type may remain.
    remaining_formal = []
    current_pairs = {}
    for level, text in integrated_texts.items():
        for record in parse_jsonl(text):
            amap = answer_map(record)
            for q in record.get("questions", []):
                key = (record.get("id"), q.get("id"))
                current_pairs[key] = (q, amap.get(q.get("id"), {}))
                if q.get("type") in FORMAL_TYPES:
                    remaining_formal.append({
                        "level": level.upper(),
                        "passage_id": record.get("id"),
                        "question_id": q.get("id"),
                        "question_type": q.get("type"),
                        "prompt": q.get("prompt"),
                    })
    if remaining_formal:
        raise SystemExit(f"Formal question types remain after integration: {remaining_formal[:5]}")

    surviving_historical = []
    for f in findings:
        key = (f["passage_id"], f["question_id"])
        q, a = current_pairs[key]
        if nfc(q.get("prompt")) == nfc(f.get("prompt")) and nfc(a.get("answer")) == nfc(f.get("answer")):
            surviving_historical.append(key)
    if surviving_historical:
        raise SystemExit(f"Historical metalinguistic candidates survived unchanged: {surviving_historical[:10]}")

    # Write canonical files only after every branch and combined guard has passed.
    for level, text in integrated_texts.items():
        (READING / "arabic" / level / "passages.jsonl").write_text(text, encoding="utf-8")

    repair = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "levels": ["A1", "A2"],
        "date": "2026-08-30",
        "status": "INTEGRATED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW",
        "historical_candidate_source": f"{HIST_AUDIT_BRANCH}:{HIST_CANDIDATE_PATH}",
        "historical_candidate_count": len(findings),
        "candidate_questions_changed": total_changed_pairs,
        "unit_repairs_integrated": len(repair_units),
        "repair_units": repair_units,
        "before_hashes": before_hashes,
        "after_hashes": after_hashes,
        "passage_text_changed": False,
        "non_qa_metadata_changed": False,
        "nfc_preserved": True,
        "guard": "Every historical branch was required to modify exactly its own unit's historical candidate Q/A pairs, no other canonical fields, and to carry a hash-bound zero-finding deterministic post-repair audit.",
        "release_claim": False,
    }
    OUTPUT_REPAIR.write_text(json.dumps(repair, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    type_counts = Counter()
    level_type_counts = {"A1": Counter(), "A2": Counter()}
    for level, text in integrated_texts.items():
        for record in parse_jsonl(text):
            for q in record.get("questions", []):
                type_counts[q.get("type")] += 1
                level_type_counts[level.upper()][q.get("type")] += 1
    post = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "levels": ["A1", "A2"],
        "date": "2026-08-30",
        "status": "PASS_DETERMINISTIC_A1_A2_METALINGUISTIC",
        "scope": {"records": 120, "questions": 1200, "answers": 1200},
        "bound_hashes": after_hashes,
        "historical_candidates_revalidated": len(findings),
        "historical_candidates_remaining_unchanged": 0,
        "formal_metalinguistic_question_type_count": 0,
        "formal_metalinguistic_findings": [],
        "question_type_counts": dict(sorted(type_counts.items())),
        "question_type_counts_by_level": {k: dict(sorted(v.items())) for k, v in level_type_counts.items()},
        "evidence_basis": "Fresh integration checks over all 20 isolated unit repairs plus their original hash-bound zero-finding post-repair audits; current output is NFC-normalized and all 146 historical candidates changed.",
        "limitations": "Deterministic/self-review evidence only. Independent native/professional, educator, model-family, and blind human review remain required.",
        "release_claim": False,
    }
    OUTPUT_POST.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"repair": repair, "postrepair": post}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
