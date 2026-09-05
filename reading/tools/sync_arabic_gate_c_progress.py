#!/usr/bin/env python3
"""Synchronize fresh Arabic Gate C comprehension/answer-grounding evidence.

Every counted decision must match the exact current learner-facing hash. This tool
records internal semantic-review progress only; it never promotes quality metadata,
release state, or educator readiness.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
DECISION_DIR = READING / "audit/arabic_gate_c_decisions_2026-09-05"
RELEASE_PATH = READING / "RELEASE_STATUS.json"
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
NAME_RE = re.compile(r"^(a1|a2|b1|b2|c1|c2)_u(\d{2})\.json$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def learner_payload(record: dict) -> dict:
    answers = {a.get("question_id"): a for a in record.get("answer_key", [])}
    return {
        "passage_id": record.get("id"),
        "unit": record.get("unit"),
        "sequence": record.get("sequence"),
        "cefr": record.get("cefr"),
        "title": record.get("title"),
        "genre": record.get("genre"),
        "text": record.get("text"),
        "qa": [
            {
                "question_id": q.get("id"),
                "type": q.get("type"),
                "prompt": q.get("prompt"),
                "answer": answers.get(q.get("id"), {}).get("answer"),
                "explanation": answers.get(q.get("id"), {}).get("explanation", ""),
            }
            for q in record.get("questions", [])
        ],
    }


def learner_hash(record: dict) -> str:
    raw = json.dumps(learner_payload(record), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(raw)


def load_current() -> tuple[dict[str, dict], dict[str, str]]:
    records: dict[str, dict] = {}
    canonical_shas: dict[str, str] = {}
    for level in LEVELS:
        path = READING / f"arabic/{level}/passages.jsonl"
        raw = path.read_bytes()
        canonical_shas[level] = sha256_bytes(raw)
        rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
        if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
            raise SystemExit(f"{level}: unexpected canonical layout")
        for record in rows:
            pid = record.get("id")
            if pid in records:
                raise SystemExit(f"duplicate Arabic passage id {pid}")
            records[pid] = record
    if len(records) != 360:
        raise SystemExit("Arabic Gate C current corpus must contain 360 records")
    return records, canonical_shas


def main() -> None:
    release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    arabic = release.get("languages", {}).get("arabic", {})
    if arabic.get("release_state") != "REOPEN_REQUIRED" or arabic.get("educator_release_ready") is not False:
        raise SystemExit("Arabic release must remain blocked while syncing Gate C")
    natural = arabic.get("naturalness_review_progress", {})
    if natural.get("status") != "FRESH_GATE_B_INTERNAL_REVIEW_COMPLETE" or natural.get("fresh_records_reviewed") != 360:
        raise SystemExit("Gate B exact-current completion is required before Gate C progress")

    current, canonical_shas = load_current()
    seen: dict[str, str] = {}
    reviewed_by_level = {level: 0 for level in LEVELS}
    qa_by_level = {level: 0 for level in LEVELS}
    findings_by_level = {level: 0 for level in LEVELS}
    records_with_findings_by_level = {level: 0 for level in LEVELS}
    units_by_level: dict[str, list[int]] = {level: [] for level in LEVELS}
    evidence_paths: list[str] = []

    if DECISION_DIR.exists():
        for path in sorted(DECISION_DIR.glob("*.json")):
            m = NAME_RE.match(path.name)
            if not m:
                raise SystemExit(f"unexpected Gate C decision filename: {path.name}")
            filename_level, filename_unit = m.group(1), int(m.group(2))
            doc = json.loads(path.read_text(encoding="utf-8"))
            level = str(doc.get("level", "")).lower()
            unit = int(doc.get("unit", 0) or 0)
            if level != filename_level or unit != filename_unit or not 1 <= unit <= 10:
                raise SystemExit(f"{path}: level/unit identity mismatch")
            if doc.get("project_id") != "LANG-A1C2" or doc.get("language") != "arabic":
                raise SystemExit(f"{path}: wrong project/language")
            if doc.get("quality_promotion") is not False or doc.get("release_claim") is not False:
                raise SystemExit(f"{path}: Gate C evidence must explicitly deny promotion/release claim")
            if doc.get("canonical_sha256") != canonical_shas[level]:
                raise SystemExit(f"{path}: stale level canonical hash")
            decisions = doc.get("decisions", [])
            if doc.get("records_reviewed") != len(decisions):
                raise SystemExit(f"{path}: records_reviewed mismatch")
            expected_ids = [f"ar-{level}-u{unit:02d}-p{i:02d}" for i in range(1, 7)]
            if [d.get("passage_id") for d in decisions] != expected_ids:
                raise SystemExit(f"{path}: decision order/scope mismatch")
            unit_qa = 0
            unit_findings = 0
            unit_with_findings = 0
            for decision in decisions:
                pid = decision.get("passage_id")
                if pid in seen:
                    raise SystemExit(f"duplicate Gate C decision for {pid}: {seen[pid]} and {path}")
                record = current.get(pid)
                if not record:
                    raise SystemExit(f"{path}: unknown current passage {pid}")
                if decision.get("learner_facing_sha256") != learner_hash(record):
                    raise SystemExit(f"{path}: stale learner-facing hash for {pid}")
                if decision.get("decision") not in {"PASS", "PASS_AFTER_REPAIR"}:
                    raise SystemExit(f"{path}: unresolved Gate C decision for {pid}")
                qac = int(decision.get("qa_pairs_reviewed", 0) or 0)
                if qac != 10:
                    raise SystemExit(f"{path}: each reviewed passage must cover all 10 Q/A pairs")
                fc = int(decision.get("finding_count", 0) or 0)
                if fc != len(decision.get("findings", [])):
                    raise SystemExit(f"{path}: finding count mismatch for {pid}")
                seen[pid] = path.as_posix()
                unit_qa += qac
                unit_findings += fc
                if fc:
                    unit_with_findings += 1
            if int(doc.get("qa_pairs_reviewed", 0) or 0) != unit_qa or unit_qa != 60:
                raise SystemExit(f"{path}: qa_pairs_reviewed mismatch")
            if int(doc.get("fresh_findings", 0) or 0) != unit_findings:
                raise SystemExit(f"{path}: fresh_findings mismatch")
            if int(doc.get("records_with_findings", 0) or 0) != unit_with_findings:
                raise SystemExit(f"{path}: records_with_findings mismatch")
            reviewed_by_level[level] += len(decisions)
            qa_by_level[level] += unit_qa
            findings_by_level[level] += unit_findings
            records_with_findings_by_level[level] += unit_with_findings
            units_by_level[level].append(unit)
            evidence_paths.append(path.relative_to(ROOT).as_posix())

    for level in LEVELS:
        units = sorted(units_by_level[level])
        if units and units != list(range(1, max(units) + 1)):
            raise SystemExit(f"{level}: Gate C units are not contiguous from Unit 1")
        if reviewed_by_level[level] != len(units) * 6 or qa_by_level[level] != len(units) * 60:
            raise SystemExit(f"{level}: Gate C unit/review totals disagree")

    total_reviewed = sum(reviewed_by_level.values())
    total_qa = sum(qa_by_level.values())
    total_findings = sum(findings_by_level.values())
    total_with_findings = sum(records_with_findings_by_level.values())
    if total_reviewed > 360 or total_qa > 3600:
        raise SystemExit("Gate C progress exceeds Arabic scope")

    progress = arabic.setdefault("comprehension_review_progress", {})
    progress.update({
        "status": "FRESH_GATE_C_INTERNAL_REVIEW_COMPLETE" if total_reviewed == 360 else "FRESH_GATE_C_INTERNAL_REVIEW_IN_PROGRESS",
        "records_in_scope": 360,
        "qa_pairs_in_scope": 3600,
        "fresh_records_reviewed": total_reviewed,
        "fresh_qa_pairs_reviewed": total_qa,
        "fresh_records_with_findings": total_with_findings,
        "fresh_findings": total_findings,
        "review_order": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "levels_completed": [level.upper() for level in LEVELS if reviewed_by_level[level] == 60],
        "decision_artifacts": evidence_paths,
        "guard": "Gate C is a fresh internal comprehension/answer-grounding audit bound to exact-current learner-facing hashes; it does not substitute for independent educator/native/blind release gates.",
        "next_step": (
            "Gate C internal review complete; continue only with separate CEFR/pedagogy and independent release gates."
            if total_reviewed == 360
            else "Continue ordered fresh Gate C review unit by unit; repair only exact-current answerability, grounding, ambiguity, reference, inference, summary, and contextual-sense defects."
        ),
    })
    evidence = arabic.setdefault("latest_release_evidence", [])
    if not isinstance(evidence, list):
        raise SystemExit("Arabic latest_release_evidence is not a list")
    for item in evidence_paths:
        if item not in evidence:
            evidence.append(item)
    arabic["educator_release_ready"] = False
    if arabic.get("release_state") != "REOPEN_REQUIRED":
        raise SystemExit("refusing to alter Arabic release state during Gate C sync")
    release["updated"] = "2026-09-05"
    RELEASE_PATH.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "fresh_records_reviewed": total_reviewed,
        "fresh_qa_pairs_reviewed": total_qa,
        "fresh_records_with_findings": total_with_findings,
        "fresh_findings": total_findings,
        "by_level": {
            level.upper(): {
                "reviewed": reviewed_by_level[level],
                "qa_pairs_reviewed": qa_by_level[level],
                "records_with_findings": records_with_findings_by_level[level],
                "findings": findings_by_level[level],
            }
            for level in LEVELS
        },
        "educator_release_ready": False,
        "release_state": "REOPEN_REQUIRED",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
