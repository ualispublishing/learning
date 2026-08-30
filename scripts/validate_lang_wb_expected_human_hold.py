#!/usr/bin/env python3
"""Validate that a LANG-WB promotion-gate HOLD is the expected human-review hold.

The production candidate is allowed to remain on HOLD while one or more valid
human reviews are missing, FAIL, HOLD, or stale after a candidate change. A HOLD
caused by malformed sign-offs, missing release inputs, ambiguous/future review
timestamps, or a manifest status other than production_candidate is not healthy
and must fail CI.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

LANGUAGES = ("arabic", "french", "urdu")
ALLOWED_FIXED_LANGUAGE_HOLD_PROBLEMS = {
    "no_signoff_files",
    "no_current_candidate_signoff",
}
ALLOWED_NONPASS_OUTCOMES = {"FAIL", "HOLD"}


def allowed_language_hold_problem(text: str) -> bool:
    if text in ALLOWED_FIXED_LANGUAGE_HOLD_PROBLEMS:
        return True
    prefix = "latest_current_candidate_outcome:"
    if text.startswith(prefix):
        return text[len(prefix) :] in ALLOWED_NONPASS_OUTCOMES
    return False


def validate(report: dict[str, Any]) -> list[str]:
    problems: list[str] = []

    if report.get("manifest_status") != "production_candidate":
        problems.append(f"manifest_status:{report.get('manifest_status')!r}")

    report_gate = report.get("gate")
    if report_gate not in {"HOLD", "PASS"}:
        problems.append(f"unexpected_gate:{report_gate!r}")

    top = report.get("problems")
    if not isinstance(top, list):
        problems.append("top_level_problems_not_list")
        top = []
    for item in top:
        text = str(item)
        if not text.startswith("language_signoff_hold:"):
            problems.append(f"unexpected_top_level_problem:{text}")

    languages = report.get("languages")
    if not isinstance(languages, dict):
        problems.append("languages_not_object")
        return problems

    for lang in LANGUAGES:
        state = languages.get(lang)
        if not isinstance(state, dict):
            problems.append(f"{lang}:missing_language_state")
            continue

        lang_problems = state.get("problems")
        if not isinstance(lang_problems, list):
            problems.append(f"{lang}:problems_not_list")
            lang_problems = []
        for item in lang_problems:
            text = str(item)
            if not allowed_language_hold_problem(text):
                problems.append(f"{lang}:unexpected_hold_problem:{text}")

        latest = state.get("latest_current_candidate_signoff")
        if isinstance(latest, dict):
            outcome = latest.get("review_outcome")
            latest_problems = latest.get("problems")
            if not isinstance(latest_problems, list):
                problems.append(f"{lang}:latest_problems_not_list")
                latest_problems = []
            if latest_problems:
                problems.append(
                    f"{lang}:invalid_latest_current_candidate_signoff:"
                    + ",".join(str(p) for p in latest_problems)
                )
            if outcome not in {"PASS", "FAIL", "HOLD"}:
                problems.append(f"{lang}:invalid_latest_review_outcome:{outcome!r}")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "report",
        nargs="?",
        default="audit/language-workbooks/v1.0/final_human_promotion_gate.json",
    )
    args = parser.parse_args()
    path = Path(args.report)

    result: dict[str, Any] = {
        "schema": "lang-wb-expected-human-hold-validation-v1",
        "report": str(path),
        "gate": "FAIL",
        "problems": [],
    }
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        result["problems"] = validate(report)
    except Exception as exc:
        result["problems"] = [f"parse_error:{type(exc).__name__}:{exc}"]

    if not result["problems"]:
        result["gate"] = "PASS"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
