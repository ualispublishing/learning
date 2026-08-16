#!/usr/bin/env python3
"""Synchronize current Arabic final-review state into reading/STATUS.json.

The synchronizer is artifact-driven and fail-closed. It does not hard-code old
blocker prose, does not require Pass 11 to use a fictitious PASS string, and can
record final approval only when a fresh Pass 12 says PASS/final_approval=true and
all required upstream gates are currently closed.

Once another language has become active after Arabic approval, a routine Arabic
audit rerun must not rewind the project phase/next-actions back to Arabic.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "reading/STATUS.json"
AUD = ROOT / "reading/audit"
FILES = {
    "pass01": AUD / "final_arabic_pass01_data_integrity.json",
    "pass02": AUD / "final_arabic_pass02_lexical_exposure_integrity.json",
    "pass03": AUD / "final_arabic_pass03_question_composition.json",
    "pass04": AUD / "final_arabic_pass04_answer_evidence_alignment.json",
    "pass05": AUD / "final_arabic_pass05_script_orthography_hygiene.json",
    "pass06": AUD / "final_arabic_pass06_lexical_source_identity.json",
    "pass07": AUD / "final_arabic_pass07_cefr_difficulty_calibration.json",
    "pass08": AUD / "final_arabic_pass08_continuity_duplicate_balance.json",
    "pass09": AUD / "final_arabic_pass09_fluency_checkpoint.json",
    "pass10": AUD / "final_arabic_pass10_adjudication.json",
    "pass11": AUD / "final_arabic_pass11_naturalness_review.json",
    "pass12": AUD / "final_arabic_pass12_adversarial_gate_falsification.json",
}


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def pass11_complete(artifact: dict) -> bool:
    return artifact.get("status") in {"PASS", "COMPLETE"} and artifact.get("totals", {}).get("levels_pending", 0) == 0


def blocker(gate: str, artifact: dict, reason: str) -> dict:
    return {"gate": gate, "status": artifact.get("status", "MISSING"), "reason": reason}


def main() -> None:
    status = load(STATUS)
    audits = {key: load(path) for key, path in FILES.items()}

    current_blockers: list[dict] = []
    if audits["pass03"].get("status") != "PASS":
        current_blockers.append(blocker(
            "pass03_question_composition", audits["pass03"],
            f"question-composition audit still has {audits['pass03'].get('totals', {}).get('review_flags', 'unknown')} review flags",
        ))
    if audits["pass04"].get("status") != "PASS":
        current_blockers.append(blocker(
            "pass04_answer_evidence_alignment", audits["pass04"],
            f"answer/evidence diagnostic still has {audits['pass04'].get('totals', {}).get('review_flags', 'unknown')} review flags requiring adjudication/remediation",
        ))
    if audits["pass07"].get("status") != "PASS":
        current_blockers.append(blocker(
            "pass07_cefr_difficulty", audits["pass07"], "CEFR/length diagnostic is not currently PASS",
        ))
    if not pass11_complete(audits["pass11"]):
        current_blockers.append(blocker(
            "pass11_manual_naturalness", audits["pass11"],
            "manual naturalness review is not complete across all six Arabic levels",
        ))
    if audits["pass10"].get("status") != "PASS_WITH_SOURCE_ADJUDICATION" or audits["pass10"].get("unresolved"):
        current_blockers.append(blocker(
            "pass10_source_adjudication", audits["pass10"], "source adjudication is not closed",
        ))

    p12 = audits["pass12"]
    p12_blocker_gates = {x.get("gate") for x in p12.get("final_approval_blockers", []) if isinstance(x, dict)}
    expected_current_gate_names = {x["gate"] for x in current_blockers}
    pass12_stale = (
        p12.get("status") != "PASS"
        and (
            "pass04_answer_evidence_alignment" not in p12_blocker_gates
            or any(
                gate in p12_blocker_gates
                for gate in {"pass07_cefr_difficulty", "pass11_manual_naturalness"}
                if gate not in expected_current_gate_names
            )
        )
    )

    final_approval = bool(
        not current_blockers
        and p12.get("status") == "PASS"
        and p12.get("final_approval") is True
    )

    pass_status = {key: artifact.get("status", "MISSING") for key, artifact in audits.items()}
    status["updated"] = date.today().isoformat()
    downstream_active = status.get("active_language") not in {None, "", "Arabic"}

    # Preserve a later language's active phase once Arabic is approved. If
    # Arabic ever loses approval, surface that regression regardless of the
    # downstream phase so it cannot be hidden.
    if not final_approval:
        status["phase"] = "Arabic A1-C2 final approval is no longer closed; resolve the current Arabic final-review regression before relying on approval."
    elif not downstream_active:
        status["phase"] = "Arabic A1-C2 final review is approved; proceed to the next language/project phase."

    status["approved_passages"] = 360 if final_approval else 0
    status["arabic_final_review"] = {
        "phase": "APPROVED" if final_approval else "CLOSING_MACHINE_GATES",
        "minimum_distinct_passes_required": 10,
        "distinct_passes_recorded": 12,
        "pass_status": pass_status,
        "current_upstream_blockers": current_blockers,
        "pass12_freshness": "STALE_RELATIVE_TO_CURRENT_UPSTREAM_STATE" if pass12_stale else "CURRENT_OR_NOT_PROVEN_STALE",
        "pass12_hard_regressions": p12.get("hard_regressions", []),
        "final_approval": final_approval,
    }

    if not final_approval:
        actions = []
        if audits["pass03"].get("status") != "PASS":
            actions.append("resolve current Pass 03 question-composition flags in one guarded batch and rerun Pass 03 + Pass 04")
        if audits["pass04"].get("status") != "PASS":
            actions.append("adjudicate Pass 04 diagnostics before editing content; repair only genuine answer/evidence defects")
        if pass12_stale:
            actions.append("repair/refresh Pass 12 after upstream gates close")
        actions.append("regenerate the full final audit suite sequentially immediately before the final Pass 12 attempt")
        status["next_actions"] = actions
    elif not downstream_active:
        status["next_actions"] = [
            "record/archive the completed Arabic final-review evidence",
            "determine the live French/Urdu canonical state before resuming their curriculum work",
        ]
    # If a downstream language is already active and Arabic remains approved,
    # leave that language's phase and next-actions untouched.

    arabic = status.setdefault("arabic", {})
    arabic["formal_final_approval"] = final_approval

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "upstream_blockers": len(current_blockers),
        "pass12_stale": pass12_stale,
        "pass11_complete": pass11_complete(audits["pass11"]),
        "final_approval": final_approval,
        "downstream_active": downstream_active,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
