#!/usr/bin/env python3
"""Apply second-pass approvals to compiled sentence row decisions.

Approval files may only resolve an existing audited row decision. They cannot add
new findings or silently substitute a different rationale. Each approval must
point back to exact evidence either already attached to that rank by the compiled
row-by-row audit or recorded in an explicit second-pass amendment ledger.

Standalone amendment ledgers are accepted only from the controlled v1.0 audit
directory and must exactly match the approval's language, release, source hash,
rank, and cited recommendation/action/issue. This preserves provenance without
requiring second-pass evidence to be copied into the compiled row before the
approval workflow can consume it.

For CORRECT_APPROVED, an approval may provide only the side that changes. The
omitted side is inherited exactly from the audited source row, preventing needless
manual retyping. At least one side must actually change. REPLACE_APPROVED must
provide both sides because it is a new learner pair.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
APPROVAL_DIR = CURATION / "approvals"
AUDIT_DIR = ROOT / "audit" / "language-workbooks" / "v1.0"
RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
ALLOWED_TRANSITIONS = {
    "CORRECT_PENDING_SECOND_PASS": {"CORRECT_APPROVED"},
    "REPLACE_PENDING_SECOND_PASS": {"REPLACE_APPROVED"},
    "NATIVE_REVIEW": {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"},
}
_AMENDMENT_CACHE: dict[tuple[str, str, str], dict | None] = {}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_matches(items: list[dict], basis: dict, *, require_ledger: str | None) -> bool:
    """Return True only for an exact cited evidence value."""
    checks = (
        ("recommended", "recommended"),
        ("recommended_action", "recommended_action"),
        ("observed", "observed"),
        ("issue", "issue"),
    )
    selected = [(basis_key, item_key) for basis_key, item_key in checks if basis_key in basis]
    if len(selected) != 1:
        return False
    basis_key, item_key = selected[0]
    wanted = basis[basis_key]
    return any(
        (require_ledger is None or item.get("ledger") == require_ledger)
        and item.get(item_key) == wanted
        for item in items
    )


def load_amendment_ledger(ledger: str, language: str, source_zip_sha256: str) -> dict | None:
    """Load a controlled standalone amendment ledger after strict identity checks."""
    if not isinstance(ledger, str) or not ledger.endswith(".json"):
        return None
    if Path(ledger).name != ledger:
        return None

    key = (ledger, language, source_zip_sha256)
    if key in _AMENDMENT_CACHE:
        return _AMENDMENT_CACHE[key]

    path = AUDIT_DIR / ledger
    if not path.is_file():
        _AMENDMENT_CACHE[key] = None
        return None

    doc = load_json(path)
    if doc.get("release") != "v1.0":
        raise SystemExit(f"Amendment ledger release mismatch: {path}")
    if doc.get("language") != language:
        raise SystemExit(f"Amendment ledger language mismatch: {path}")
    if doc.get("source_zip_sha256") != source_zip_sha256:
        raise SystemExit(f"Amendment ledger source hash mismatch: {path}")
    if not isinstance(doc.get("amendments"), list):
        raise SystemExit(f"Malformed amendment ledger (missing amendments list): {path}")

    _AMENDMENT_CACHE[key] = doc
    return doc


def audit_basis_matches(
    row: dict,
    basis: dict,
    *,
    language: str,
    source_zip_sha256: str,
) -> bool:
    if not isinstance(basis, dict):
        return False
    ledger = basis.get("ledger")
    if not isinstance(ledger, str) or not ledger:
        return False

    # First accept exact evidence already compiled onto the row.
    row_evidence = list(row.get("confirmed_findings", [])) + list(row.get("editorial_flags", []))
    if evidence_matches(row_evidence, basis, require_ledger=ledger):
        return True

    # If the cited ledger is an explicit standalone second-pass amendment file,
    # resolve the same rank there. No fuzzy matching or cross-rank fallback is allowed.
    amendment_doc = load_amendment_ledger(ledger, language, source_zip_sha256)
    if amendment_doc is None:
        return False

    rank = int(row["rank"])
    matches = [item for item in amendment_doc["amendments"] if int(item.get("rank", -1)) == rank]
    if len(matches) != 1:
        return False
    amendment = matches[0]
    amendment_evidence = list(amendment.get("confirmed_findings", [])) + list(
        amendment.get("editorial_flags", [])
    )
    return evidence_matches(amendment_evidence, basis, require_ledger=None)


def apply_language(language: str) -> dict:
    decision_path = CURATION / f"{language}_sentence_row_decisions.json"
    if not decision_path.exists():
        raise SystemExit(f"Missing decisions: {decision_path}")
    data = load_json(decision_path)
    rows = data.get("rows", [])
    if len(rows) != 1000:
        raise SystemExit(f"{language} decision file must contain 1000 rows")
    by_rank = {int(row["rank"]): row for row in rows}
    source_zip_sha256 = data.get("source_zip_sha256")
    if not isinstance(source_zip_sha256, str) or not source_zip_sha256:
        raise SystemExit(f"Missing source hash in {decision_path}")

    approval_files = sorted(APPROVAL_DIR.glob(f"{language}_*.json"))
    seen: set[int] = set()
    applied = 0

    for path in approval_files:
        approval_doc = load_json(path)
        if approval_doc.get("language") != language or approval_doc.get("release") != "v1.0":
            raise SystemExit(f"Approval identity/version mismatch: {path}")
        if approval_doc.get("source_zip_sha256") != source_zip_sha256:
            raise SystemExit(f"Approval source hash mismatch: {path}")

        for approval in approval_doc.get("approvals", []):
            rank = int(approval["rank"])
            if rank in seen:
                raise SystemExit(f"Duplicate approval for {language} rank {rank}")
            seen.add(rank)
            row = by_rank.get(rank)
            if row is None:
                raise SystemExit(f"Approval references missing {language} rank {rank}")

            if "source_target" in approval and approval["source_target"] != row.get("source_target"):
                raise SystemExit(f"Source target mismatch for {language} rank {rank}")
            if "source_english" in approval and approval["source_english"] != row.get("source_english"):
                raise SystemExit(f"Source English mismatch for {language} rank {rank}")
            if not audit_basis_matches(
                row,
                approval.get("audit_basis"),
                language=language,
                source_zip_sha256=source_zip_sha256,
            ):
                raise SystemExit(
                    f"Approval for {language} rank {rank} is not tied to its exact audited recommendation/flag"
                )

            current = row.get("status")
            expected = approval.get("expected_status")
            requested = approval.get("approved_status")
            if expected and current != expected and current not in RESOLVED:
                raise SystemExit(
                    f"Expected {language} rank {rank} to be {expected}, found {current}"
                )
            if current in RESOLVED:
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
            elif requested == "CORRECT_APPROVED":
                target = approval.get("approved_target", row["source_target"])
                english = approval.get("approved_english", row["source_english"])
                if not isinstance(target, str) or not target.strip():
                    raise SystemExit(f"Invalid approved_target for {language} rank {rank}")
                if not isinstance(english, str) or not english.strip():
                    raise SystemExit(f"Invalid approved_english for {language} rank {rank}")
                target = target.strip()
                english = english.strip()
                if target == row["source_target"] and english == row["source_english"]:
                    raise SystemExit(f"No-op CORRECT_APPROVED for {language} rank {rank}")
            else:  # REPLACE_APPROVED
                target = approval.get("approved_target")
                english = approval.get("approved_english")
                if not isinstance(target, str) or not target.strip():
                    raise SystemExit(f"Missing approved_target for replacement {language} rank {rank}")
                if not isinstance(english, str) or not english.strip():
                    raise SystemExit(f"Missing approved_english for replacement {language} rank {rank}")
                target = target.strip()
                english = english.strip()

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
