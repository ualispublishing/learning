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


def git_blob_sha_bytes(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def git_blob_sha(path: Path) -> str:
    return git_blob_sha_bytes(path.read_bytes())


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_state_manifest(manifest: dict, status: dict, continuation: dict, errors: list[str]) -> None:
    require(manifest.get("project_id") == "LANG-A1C2", "STATE_MANIFEST project_id must be LANG-A1C2", errors)
    require(manifest.get("branch_expected") == "main", "STATE_MANIFEST branch_expected must remain main", errors)

    state_files = manifest.get("state_files", {})
    require(isinstance(state_files, dict) and bool(state_files), "STATE_MANIFEST state_files must be a non-empty mapping", errors)

    aggregate_lines: list[str] = []
    actual_total_bytes = 0
    for name, record in state_files.items():
        path = ROOT / name
        require(path.exists(), f"STATE_MANIFEST tracked file missing: {name}", errors)
        if not path.exists():
            continue
        data = path.read_bytes()
        actual_blob = git_blob_sha_bytes(data)
        actual_size = len(data)
        expected_blob = record.get("git_blob")
        expected_size = record.get("bytes")
        require(actual_blob == expected_blob, f"STATE_MANIFEST blob drift: {name}: live {actual_blob} != pinned {expected_blob}", errors)
        require(actual_size == expected_size, f"STATE_MANIFEST byte-size drift: {name}: live {actual_size} != pinned {expected_size}", errors)
        aggregate_lines.append(f"{name}\0{actual_blob}\0{actual_size}")
        actual_total_bytes += actual_size

    actual_aggregate = hashlib.sha256("\n".join(sorted(aggregate_lines)).encode("utf-8")).hexdigest()
    require(len(state_files) == manifest.get("state_file_count"), "STATE_MANIFEST state_file_count mismatch", errors)
    require(actual_total_bytes == manifest.get("state_file_bytes"), "STATE_MANIFEST state_file_bytes mismatch", errors)
    require(actual_aggregate == manifest.get("aggregate_sha256"), "STATE_MANIFEST aggregate_sha256 mismatch", errors)

    snapshot = manifest.get("production_snapshot", {})
    require(snapshot.get("canonical_passages") == status["current"]["canonical_passages"], "STATE_MANIFEST production total differs from STATUS", errors)
    require(snapshot.get("remaining_generation_passages") == status["current"]["remaining_generation_passages"], "STATE_MANIFEST remaining-generation total differs from STATUS", errors)
    require(snapshot.get("active_language") == status["current"]["active_language"], "STATE_MANIFEST active language differs from STATUS", errors)
    require(snapshot.get("active_level") == status["current"]["active_level"], "STATE_MANIFEST active level differs from STATUS", errors)
    require(snapshot.get("arabic_passages") == status["languages"]["arabic"]["canonical_passages"], "STATE_MANIFEST Arabic total differs from STATUS", errors)
    require(snapshot.get("french_passages") == status["languages"]["french"]["canonical_passages"], "STATE_MANIFEST French total differs from STATUS", errors)
    require(snapshot.get("urdu_passages") == status["languages"]["urdu"]["canonical_passages"], "STATE_MANIFEST Urdu total differs from STATUS", errors)

    anchor = manifest.get("canonical_anchor", {})
    require(anchor.get("urdu_a1_path") == continuation["production"]["urdu"]["a1_canonical_path"], "STATE_MANIFEST Urdu A1 path differs from CONTINUATION", errors)
    require(anchor.get("urdu_a1_git_blob") == continuation["production"]["urdu"]["a1_git_blob"], "STATE_MANIFEST Urdu A1 blob differs from CONTINUATION", errors)


def main() -> int:
    continuation = load_json(READING / "CONTINUATION.json")
    status = load_json(READING / "STATUS.json")
    release = load_json(READING / "RELEASE_STATUS.json")
    plan = load_json(READING / "planning" / "ACTIVE_GENERATION_PLAN.json")
    integrity = load_json(READING / "audit" / "urdu_a1_final_integrity_2026-08-23.json")
    router = load_json(ROOT / "PROJECT_TRACKS.json")
    manifest = load_json(READING / "STATE_MANIFEST.json")

    errors: list[str] = []

    for name, data in (
        ("CONTINUATION", continuation),
        ("STATUS", status),
        ("RELEASE_STATUS", release),
        ("ACTIVE_GENERATION_PLAN", plan),
        ("STATE_MANIFEST", manifest),
    ):
        require(data.get("project_id") == "LANG-A1C2", f"{name}: project_id must be LANG-A1C2", errors)

    require(status.get("state_type") == "PRODUCTION_STATUS_ONLY", "STATUS must remain production-only; release claims belong in RELEASE_STATUS", errors)
    require(release.get("state_type") == "RELEASE_EVIDENCE_ONLY", "RELEASE_STATUS must remain release-evidence-only; live production counts belong in STATUS", errors)
    require(release.get("production_status_source") == "reading/STATUS.json", "RELEASE_STATUS must point to STATUS for live production state", errors)
    require(continuation.get("state_contract", {}).get("production_and_release_are_separate") is True, "CONTINUATION must preserve production/release separation", errors)
    require(continuation.get("state_contract", {}).get("fail_closed_on_state_bundle_drift") is True, "CONTINUATION must fail closed on state-bundle drift", errors)
    require(continuation.get("state_contract", {}).get("state_manifest") == "reading/STATE_MANIFEST.json", "CONTINUATION must name STATE_MANIFEST.json", errors)

    authority = continuation.get("authority_by_domain", {})
    for domain in (
        "project_routing_and_scope",
        "production_facts",
        "release_readiness",
        "active_generation_frontier",
        "state_bundle_integrity",
        "durable_rules",
        "history",
    ):
        require(bool(authority.get(domain)), f"CONTINUATION authority_by_domain missing {domain}", errors)

    validate_state_manifest(manifest, status, continuation, errors)

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
    active_cont = (continuation["active_frontier"]["production"]["language"], continuation["active_frontier"]["production"]["level"])
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

    require(continuation.get("release", {}).get("source") == "reading/RELEASE_STATUS.json", "CONTINUATION cached release summary must identify RELEASE_STATUS as its source", errors)
    for language in LANGUAGES:
        language_release = release["languages"][language]
        cached_release = continuation["release"][language]
        ready = language_release.get("educator_release_ready")
        open_classes = language_release.get("open_release_classes", [])
        require(isinstance(ready, bool), f"{language}: educator_release_ready must be boolean", errors)
        require(cached_release.get("educator_release_ready") == ready, f"{language}: CONTINUATION cached educator_release_ready differs from RELEASE_STATUS", errors)
        require(cached_release.get("release_state") == language_release.get("release_state"), f"{language}: CONTINUATION cached release_state differs from RELEASE_STATUS", errors)
        require(not (ready and open_classes), f"{language}: educator_release_ready=true is inconsistent with unresolved open_release_classes", errors)

    require(not release["languages"]["urdu"]["educator_release_ready"], "Urdu cannot be educator-release-ready while its cited A1 integrity evidence has quality_promotion=false", errors)
    require(not (release["languages"]["french"]["latest_deterministic_gate"].get("status") == "FAIL" and release["languages"]["french"]["educator_release_ready"]), "French cannot be educator-release-ready while the cited deterministic gate is FAIL", errors)

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
    require("reading/STATE_MANIFEST.json" in a1c2.get("start_here", []), "PROJECT_TRACKS: LANG-A1C2 start_here must include STATE_MANIFEST", errors)
    require(a1c2.get("validation_command") == "python reading/tools/validate_continuation_state.py", "PROJECT_TRACKS: LANG-A1C2 validation command drifted", errors)
    require(wb.get("new_chat_prefix") == "LANG-WB — CONTINUE", "PROJECT_TRACKS: LANG-WB new-chat prefix drifted", errors)
    require("reading/" in set(wb.get("explicit_exclusions", [])), "PROJECT_TRACKS: LANG-WB must exclude reading/", errors)
    require({"completed/languages/workbooks/v1.0/", "audit/language-workbooks/v1.0/", "curation/language-workbooks/v1.0/"}.issubset(set(a1c2.get("explicit_exclusions", []))), "PROJECT_TRACKS: LANG-A1C2 must exclude all workbook roots", errors)

    if errors:
        print("LANG-A1C2 continuation validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("LANG-A1C2 continuation validation: PASS")
    print(f"state bundle: {manifest['state_file_count']} files, {manifest['state_file_bytes']} bytes, sha256 {manifest['aggregate_sha256']}")
    print(f"canonical passages: {actual_total} (Arabic {actual['arabic']}, French {actual['french']}, Urdu {actual['urdu']})")
    print(f"active frontier: {active_plan[0]} {active_plan[1]}")
    print("release evidence is decoupled from live production counts")
    print("Urdu A1 pinned integrity baseline: exact blob match; 0 hard errors; 0 warnings; quality_promotion=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
