#!/usr/bin/env python3
"""Apply second-pass approvals to compiled sentence row decisions.

Approval files may only resolve an existing audited row decision. They cannot add
new audit findings or change the source row. This keeps correction provenance
strictly tied to the completed row-by-row audit.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
APPROVAL_DIR = CURATION / "approvals"
RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
ALLOWED_TRANSITIONS = {
    "CORRECT_PENDING_SECOND_PASS": {"CORRECT_APPROVED"},
    "REPLACE_PENDING_SECOND_PASS": {"REPLACE_APPROVED"},
    "NATIVE_REVIEW": {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"},
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_language(language: str) -> dict:
    decision_path = CURATION / f"{language}_sentence_row_decisions.json"
    if not decision_path.exists():
        raise SystemExit(f"Missing decisions: {decision_path}")
    data = load_json(decision_path)
    rows = data.get("rows", [])
    if len(rows) != 1000:
        raise SystemExit(f"{language} decision file must contain 1000 rows")
    by_rank = {int(row["rank"]): row for row in rows}

    approval_files = sorted(APPROVAL_DIR.glob(f"{language}_*.json"))
    seen: set[int] = set()
    applied = 0

    for path in approval_files:
        approval_doc = load_json(path)
        if approval_doc.get("language") != language or approval_doc.get("release") != "v1.0":
            raise SystemExit(f"Approval identity/version mismatch: {path}")
        for approval in approval_doc.get("approvals", []):
            rank = int(approval["rank"])
            if rank in seen:
                raise SystemExit(f"Duplicate approval for {language} rank {rank}")
            seen.add(rank)
            row = by_rank.get(rank)
            if row is None:
                raise SystemExit(f"Approval references missing {language} rank {rank}")

            if approval.get("audit_fingerprint") != row.get("audit_fingerprint"):
                raise SystemExit(
                    f"Audit fingerprint mismatch for {language} rank {rank}; "
                    "the row/audit changed after approval was prepared"
                )
            if approval.get("source_target") != row.get("source_target"):
                raise SystemExit(f"Source target mismatch for {language} rank {rank}")
            if approval.get("source_english") != row.get("source_english"):
                raise SystemExit(f"Source English mismatch for {language} rank {rank}")

            current = row.get("status")
            requested = approval.get("approved_status")
            if current in RESOLVED:
                # Idempotent replay is allowed only for an identical prior approval.
                if current != requested:
                    raise SystemExit(f"Conflicting approval for resolved {language} rank {rank}")
                continue
            if requested not in ALLOWED_TRANSITIONS.get(current, set()):
                raise SystemExit(
                    f"Invalid transition for {language} rank {rank}: {current} -> {requested}"
                )

            note = approval.get("approval_note")
            if not isinstance(note, str) or not note.strip():
                raise SystemExit(f"Missing second-pass approval note for {language} rank {rank}")

            if requested == "KEEP":
                target = row["source_target"]
                english = row["source_english"]
            else:
                target = approval.get("approved_target")
                english = approval.get("approved_english")
                if not isinstance(target, str) or not target.strip():
                    raise SystemExit(f"Missing approved_target for {language} rank {rank}")
                if not isinstance(english, str) or not english.strip():
                    raise SystemExit(f"Missing approved_english for {language} rank {rank}")

            row["status"] = requested
            row["approved_target"] = target
            row["approved_english"] = english
            row["approval_note"] = note.strip()
            row["approval_source"] = str(path.relative_to(ROOT))
            applied += 1

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    data["status_counts"] = counts
    decision_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    unresolved = sum(v for k, v in counts.items() if k not in RESOLVED)
    return {"status_counts": counts, "unresolved_rows": unresolved, "approvals_applied": applied}


def main() -> None:
    summary = {"release": "v1.0", "languages": {}, "total_rows": 3000, "unresolved_rows": 0}
    for language in ("arabic", "french", "urdu"):
        info = apply_language(language)
        summary["languages"][language] = info
        summary["unresolved_rows"] += info["unresolved_rows"]
    (CURATION / "sentence_row_decision_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
