#!/usr/bin/env python3
"""Fail-closed consistency checks for the LANG-A1C2 live handoff state."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
LANGUAGES = ("arabic", "french", "urdu")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def canonical_count(language: str) -> int:
    total = 0
    for level in LEVELS:
        path = READING / language / level / "passages.jsonl"
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as f:
            for line_no, raw in enumerate(f, 1):
                if not raw.strip():
                    continue
                try:
                    json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise AssertionError(f"Invalid JSONL: {path}:{line_no}: {exc}") from exc
                total += 1
    return total


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    continuation = load_json(READING / "CONTINUATION.json")
    status = load_json(READING / "STATUS.json")
    release = load_json(READING / "RELEASE_STATUS.json")
    plan = load_json(READING / "planning" / "ACTIVE_GENERATION_PLAN.json")
    integrity = load_json(READING / "audit" / "urdu_a1_final_integrity_2026-08-23.json")
    router = load_json(ROOT / "PROJECT_TRACKS.json")

    errors: list[str] = []

    for name, data in (
        ("CONTINUATION", continuation),
        ("STATUS", status),
        ("RELEASE_STATUS", release),
        ("ACTIVE_GENERATION_PLAN", plan),
    ):
        require(data.get("project_id") == "LANG-A1C2", f"{name}: project_id must be LANG-A1C2", errors)

    require(
        status.get("state_type") == "PRODUCTION_STATUS_ONLY",
        "STATUS must remain production-only; release claims belong in RELEASE_STATUS",
        errors,
    )
    require(
        release.get("state_type") == "RELEASE_EVIDENCE_ONLY",
        "RELEASE_STATUS must remain release-evidence-only; live production counts belong in STATUS",
        errors,
    )
    require(
        release.get("production_status_source") == "reading/STATUS.json",
        "RELEASE_STATUS must point to STATUS for live production state",
        errors,
    )
    require(
        continuation.get("state_contract", {}).get("production_and_release_are_separate") is True,
        "CONTINUATION must preserve production/release separation",
        errors,
    )

    actual = {language: canonical_count(language) for language in LANGUAGES}
    actual_total = sum(actual.values())

    for language in LANGUAGES:
        expected_status = status["languages"][language]["canonical_passages"]
        expected_cont = continuation["production"][language]["canonical_passages"]
        require(actual[language] == expected_status, f"{language}: canonical count {actual[language]} != STATUS {expected_status}", errors)
        require(actual[language] == expected_cont, f"{language}: canonical count {actual[language]} != CONTINUATION {expected_cont}", errors)

    require(actual_total == status["current"]["canonical_passages"], f"total canonical count {actual_total} != STATUS total", errors)
    require(actual_total == continuation["production"]["canonical_passages"], f"total canonical count {actual_total} != CONTINUATION total", errors)

    active_status = (status["current"]["active_language"], status["current"]["active_level"])
    active_cont = (
        continuation["active_frontier"]["production"]["language"],
        continuation["active_frontier"]["production"]["level"],
    )
    active_plan = (plan["active_language"], plan["active_level"])
    require(active_status == active_cont == active_plan, f"active frontier disagreement: STATUS={active_status}, CONTINUATION={active_cont}, PLAN={active_plan}", errors)

    urdu_a1 = READING / "urdu" / "a1" / "passages.jsonl"
    require(urdu_a1.exists(), "Urdu A1 canonical file is missing", errors)
    if urdu_a1.exists():
        actual_blob = git_blob_sha(urdu_a1)
        pinned = continuation["production"]["urdu"]["a1_git_blob"]
        release_scope = release["languages"]["urdu"]["evidence_scope_at_latest_release_review"]
        release_integrity = release["languages"]["urdu"]["a1_integrity_evidence"]

        require(actual_blob == pinned, f"Urdu A1 blob drift: live {actual_blob} != pinned {pinned}", errors)
        require(plan["previous_level_anchor"]["git_blob"] == pinned, "ACTIVE_GENERATION_PLAN Urdu A1 anchor differs from CONTINUATION", errors)
        require(status["languages"]["urdu"]["a1"]["git_blob"] == pinned, "STATUS Urdu A1 anchor differs from CONTINUATION", errors)
        require(release_scope["bound_git_blob"] == pinned, "RELEASE_STATUS Urdu A1 evidence scope differs from CONTINUATION", errors)
        require(release_integrity["bound_git_blob"] == pinned, "RELEASE_STATUS Urdu A1 integrity anchor differs from CONTINUATION", errors)
        require(integrity.get("input_git_blob_sha_expected") == pinned, "Urdu A1 integrity expected blob differs from CONTINUATION", errors)
        require(integrity.get("input_git_blob_sha_actual") == pinned, "Urdu A1 integrity actual blob differs from CONTINUATION", errors)
        require(release_scope.get("levels") == ["A1"], "Urdu release evidence scope must remain explicitly A1-only until new release evidence changes it", errors)
        require(release_scope.get("canonical_passages") == 60, "Urdu A1 release evidence scope must record the 60-passage reviewed corpus", errors)

    require(integrity.get("passage_count") == 60, "Urdu A1 integrity passage_count must be 60", errors)
    require(integrity.get("question_count") == 600, "Urdu A1 integrity question_count must be 600", errors)
    require(integrity.get("answer_count") == 600, "Urdu A1 integrity answer_count must be 600", errors)
    require(integrity.get("hard_error_count") == 0, "Urdu A1 integrity audit has hard errors", errors)
    require(integrity.get("warning_count") == 0, "Urdu A1 integrity audit has warnings", errors)
    require(integrity.get("all_130_clozes_reconstructed") is True, "Urdu A1 cloze reconstruction gate is not fully green", errors)
    require(integrity.get("quality_promotion") is False, "Urdu A1 integrity artifact unexpectedly promotes quality", errors)
    require(release["languages"]["urdu"]["a1_integrity_evidence"].get("quality_promotion") is False, "RELEASE_STATUS must preserve Urdu A1 quality_promotion=false", errors)

    for language in LANGUAGES:
        language_release = release["languages"][language]
        ready = language_release.get("educator_release_ready")
        open_classes = language_release.get("open_release_classes", [])
        require(isinstance(ready, bool), f"{language}: educator_release_ready must be boolean", errors)
        require(not (ready and open_classes), f"{language}: educator_release_ready=true is inconsistent with unresolved open_release_classes", errors)

    require(
        not release["languages"]["urdu"]["educator_release_ready"],
        "Urdu cannot be educator-release-ready while its cited A1 integrity evidence has quality_promotion=false",
        errors,
    )
    require(
        not (
            release["languages"]["french"]["latest_deterministic_gate"].get("status") == "FAIL"
            and release["languages"]["french"]["educator_release_ready"]
        ),
        "French cannot be educator-release-ready while the cited deterministic gate is FAIL",
        errors,
    )

    expected_scope_exclusions = {
        "completed/languages/workbooks/v1.0/",
        "audit/language-workbooks/v1.0/",
        "curation/language-workbooks/v1.0/",
        "progress/",
    }
    actual_exclusions = set(continuation["scope_guard"]["explicitly_out_of_scope"])
    require(expected_scope_exclusions.issubset(actual_exclusions), "CONTINUATION scope guard no longer excludes the workbook/progress tracks", errors)

    tracks = router.get("tracks", {})
    a1c2 = tracks.get("LANG-A1C2", {})
    wb = tracks.get("LANG-WB", {})
    require(a1c2.get("canonical_root") == "reading/", "PROJECT_TRACKS: LANG-A1C2 must route to reading/", errors)
    require(a1c2.get("new_chat_prefix") == "LANG-A1C2 — CONTINUE", "PROJECT_TRACKS: LANG-A1C2 new-chat prefix drifted", errors)
    require(wb.get("new_chat_prefix") == "LANG-WB — CONTINUE", "PROJECT_TRACKS: LANG-WB new-chat prefix drifted", errors)
    require("reading/" in set(wb.get("explicit_exclusions", [])), "PROJECT_TRACKS: LANG-WB must exclude reading/", errors)
    require(
        {
            "completed/languages/workbooks/v1.0/",
            "audit/language-workbooks/v1.0/",
            "curation/language-workbooks/v1.0/",
        }.issubset(set(a1c2.get("explicit_exclusions", []))),
        "PROJECT_TRACKS: LANG-A1C2 must exclude all workbook roots",
        errors,
    )

    if errors:
        print("LANG-A1C2 continuation validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("LANG-A1C2 continuation validation: PASS")
    print(f"canonical passages: {actual_total} (Arabic {actual['arabic']}, French {actual['french']}, Urdu {actual['urdu']})")
    print(f"active frontier: {active_plan[0]} {active_plan[1]}")
    print("release evidence is decoupled from live production counts")
    print("Urdu A1 pinned integrity baseline: exact blob match; 0 hard errors; 0 warnings; quality_promotion=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
