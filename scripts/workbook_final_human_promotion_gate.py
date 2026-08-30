#!/usr/bin/env python3
"""Fail-closed final human sign-off gate for LANG-WB v1.0.

This is intentionally separate from the automated production-candidate release
pipeline. Production-candidate builds may pass without native-speaker sign-off;
promotion beyond production_candidate may not.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
SIGNOFF_DIR = AUDIT / "native-signoffs"
MANIFEST_PATH = RELEASE / "RELEASE_MANIFEST.json"
OUT_PATH = AUDIT / "final_human_promotion_gate.json"
LANGUAGES = ("arabic", "french", "urdu")
MASTER_NAMES = {
    "arabic": "00_arabic_complete_master.pdf",
    "french": "00_french_complete_master.pdf",
    "urdu": "00_urdu_complete_master.pdf",
}
REQUIRED_SCOPE_FIELDS = (
    "complete_master_workbook_reviewed",
    "all_learner_facing_vocabulary_reviewed",
    "all_learner_facing_sentences_and_translations_reviewed",
    "all_prompts_answers_explanations_and_headings_reviewed",
    "pronunciation_foundations_reviewed",
    "grammar_morphology_spelling_and_orthography_reviewed",
    "naturalness_idiom_and_register_reviewed",
    "pedagogical_and_progression_appropriateness_reviewed",
    "script_punctuation_or_diacritic_hygiene_reviewed",
)
ALLOWED_REVIEW_OUTCOMES = ("PASS", "FAIL", "HOLD")
MAX_FUTURE_CLOCK_SKEW = timedelta(minutes=10)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_review_time(value: Any) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("empty review_completed_utc")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("review_completed_utc must include timezone")
    return parsed.astimezone(timezone.utc)


def reviewer_complete(record: dict[str, Any]) -> bool:
    reviewer = record.get("reviewer") or {}
    required = (
        "name_or_identifier",
        "native_or_near_native_status",
        "qualification_basis",
    )
    return all(str(reviewer.get(k, "")).strip() for k in required)


def binding_problems(
    record: dict[str, Any],
    *,
    lang: str,
    expected_master_path: str,
    expected_master_blob: str,
    expected_decision_sha: str,
    expected_manifest_blob: str,
) -> list[str]:
    problems: list[str] = []
    if record.get("schema") != "lang-wb-native-signoff-v1":
        problems.append("schema")
    if record.get("release") != "v1.0":
        problems.append("release")
    if record.get("language") != lang:
        problems.append("language")

    binding = record.get("candidate_binding") or {}
    if binding.get("master_workbook_path") != expected_master_path:
        problems.append("master_workbook_path")
    if binding.get("master_workbook_git_blob_sha") != expected_master_blob:
        problems.append("master_workbook_git_blob_sha")
    if binding.get("sentence_decision_sha256") != expected_decision_sha:
        problems.append("sentence_decision_sha256")
    if binding.get("release_manifest_path") != "completed/languages/workbooks/v1.0/RELEASE_MANIFEST.json":
        problems.append("release_manifest_path")
    if binding.get("release_manifest_git_blob_sha") != expected_manifest_blob:
        problems.append("release_manifest_git_blob_sha")
    return problems


def validate_signoff_record(
    record: dict[str, Any],
    *,
    lang: str,
    expected_master_path: str,
    expected_master_blob: str,
    expected_decision_sha: str,
    expected_manifest_blob: str,
    candidate_generated_at: datetime | None = None,
    now_utc: datetime | None = None,
) -> list[str]:
    """Validate one current-candidate human record for its declared outcome."""
    problems = binding_problems(
        record,
        lang=lang,
        expected_master_path=expected_master_path,
        expected_master_blob=expected_master_blob,
        expected_decision_sha=expected_decision_sha,
        expected_manifest_blob=expected_manifest_blob,
    )

    outcome = record.get("review_outcome")
    if outcome not in ALLOWED_REVIEW_OUTCOMES:
        problems.append("review_outcome")

    try:
        reviewed_at = parse_review_time(record.get("review_completed_utc"))
        if candidate_generated_at is not None and reviewed_at < candidate_generated_at:
            problems.append("review_before_candidate_generated")
        if now_utc is not None and reviewed_at > now_utc + MAX_FUTURE_CLOCK_SKEW:
            problems.append("review_timestamp_in_future")
    except ValueError as exc:
        problems.append(f"review_completed_utc:{exc}")

    if not reviewer_complete(record):
        problems.append("reviewer_qualification")

    scope = record.get("scope_attestation")
    if not isinstance(scope, dict):
        problems.append("scope_attestation")
        scope = {}
    for field in REQUIRED_SCOPE_FIELDS:
        if field not in scope or not isinstance(scope.get(field), bool):
            problems.append(f"scope:{field}:missing_or_not_boolean")

    defects = record.get("defects")
    holds = record.get("holds")
    if not isinstance(defects, list):
        problems.append("defects_not_list")
        defects = []
    if not isinstance(holds, list):
        problems.append("holds_not_list")
        holds = []

    if not str(record.get("attestation", "")).strip():
        problems.append("attestation")

    if outcome == "PASS":
        for field in REQUIRED_SCOPE_FIELDS:
            if scope.get(field) is not True:
                problems.append(f"scope:{field}:PASS_requires_true")
        if defects:
            problems.append("PASS_defects_not_empty")
        if holds:
            problems.append("PASS_holds_not_empty")
        if not str(record.get("pass_condition_acknowledged", "")).strip():
            problems.append("pass_condition_acknowledged")
    elif outcome == "FAIL":
        if not defects:
            problems.append("FAIL_requires_defects")
    elif outcome == "HOLD":
        if not holds:
            problems.append("HOLD_requires_holds")

    return problems


def validate_pass_signoff(
    record: dict[str, Any],
    *,
    lang: str,
    expected_master_path: str,
    expected_master_blob: str,
    expected_decision_sha: str,
    expected_manifest_blob: str,
) -> list[str]:
    """Backward-compatible PASS-specific wrapper used by external checks/tests."""
    problems = validate_signoff_record(
        record,
        lang=lang,
        expected_master_path=expected_master_path,
        expected_master_blob=expected_master_blob,
        expected_decision_sha=expected_decision_sha,
        expected_manifest_blob=expected_manifest_blob,
    )
    if record.get("review_outcome") != "PASS" and "review_outcome" not in problems:
        problems.append("review_outcome")
    return problems


def candidate_signoffs(lang: str) -> list[Path]:
    if not SIGNOFF_DIR.exists():
        return []
    return sorted(SIGNOFF_DIR.glob(f"{lang}_*.json"))


def main() -> None:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"missing release manifest: {MANIFEST_PATH}")

    manifest = load_json(MANIFEST_PATH)
    manifest_blob = git_blob_sha(MANIFEST_PATH)
    manifest_langs = manifest.get("sentence_curation", {}).get("languages", {})
    try:
        candidate_generated_at = parse_review_time(manifest.get("generated_utc"))
    except ValueError as exc:
        raise SystemExit(f"invalid manifest generated_utc: {exc}")
    now_utc = datetime.now(timezone.utc)

    overall: dict[str, Any] = {
        "release": "v1.0",
        "gate": "HOLD",
        "manifest_status": manifest.get("status"),
        "candidate_generated_utc": manifest.get("generated_utc"),
        "release_manifest_git_blob_sha": manifest_blob,
        "languages": {},
        "problems": [],
        "note": "PASS means all three independent full-content human sign-offs bind to the current production candidate. The latest unambiguous structurally valid review for a current candidate controls; an older PASS cannot override a newer valid FAIL or HOLD.",
    }

    if manifest.get("status") != "production_candidate":
        overall["problems"].append(
            f"expected production_candidate before promotion, got {manifest.get('status')!r}"
        )

    for lang in LANGUAGES:
        master_rel = f"completed/languages/workbooks/v1.0/{lang}/{MASTER_NAMES[lang]}"
        master_path = ROOT / master_rel
        lang_result: dict[str, Any] = {
            "gate": "HOLD",
            "latest_current_candidate_signoff": None,
            "checked_signoffs": [],
            "problems": [],
        }
        if not master_path.exists():
            lang_result["problems"].append(f"missing_master:{master_rel}")
            overall["languages"][lang] = lang_result
            continue

        expected_decision = (manifest_langs.get(lang) or {}).get("decision_sha256")
        if not expected_decision:
            lang_result["problems"].append("missing_manifest_decision_sha256")
            overall["languages"][lang] = lang_result
            continue

        master_blob = git_blob_sha(master_path)
        signoffs = candidate_signoffs(lang)
        current_records: list[tuple[datetime, Path, dict[str, Any]]] = []
        malformed_files: list[str] = []
        if not signoffs:
            lang_result["problems"].append("no_signoff_files")

        for path in signoffs:
            rel = str(path.relative_to(ROOT))
            try:
                record = load_json(path)
            except Exception as exc:  # a sign-off file must never be silently ignored
                problem = f"parse_error:{type(exc).__name__}:{exc}"
                malformed_files.append(rel)
                lang_result["checked_signoffs"].append({"path": rel, "problems": [problem]})
                continue

            bind_problems = binding_problems(
                record,
                lang=lang,
                expected_master_path=master_rel,
                expected_master_blob=master_blob,
                expected_decision_sha=expected_decision,
                expected_manifest_blob=manifest_blob,
            )
            entry: dict[str, Any] = {"path": rel, "binding_problems": bind_problems}
            if bind_problems:
                entry["current_candidate"] = False
                lang_result["checked_signoffs"].append(entry)
                continue

            entry["current_candidate"] = True
            entry["review_completed_utc"] = record.get("review_completed_utc")
            entry["review_outcome"] = record.get("review_outcome")
            record_problems = validate_signoff_record(
                record,
                lang=lang,
                expected_master_path=master_rel,
                expected_master_blob=master_blob,
                expected_decision_sha=expected_decision,
                expected_manifest_blob=manifest_blob,
                candidate_generated_at=candidate_generated_at,
                now_utc=now_utc,
            )
            if record_problems:
                entry["problems"] = record_problems
                lang_result["problems"].append(
                    f"invalid_current_candidate_signoff:{rel}:" + ",".join(record_problems)
                )
            else:
                reviewed_at = parse_review_time(record.get("review_completed_utc"))
                current_records.append((reviewed_at, path, record))
            lang_result["checked_signoffs"].append(entry)

        if malformed_files:
            lang_result["problems"].append("malformed_signoff_files:" + ",".join(malformed_files))

        if current_records:
            current_records.sort(key=lambda item: item[0])
            latest_time = current_records[-1][0]
            latest_records = [item for item in current_records if item[0] == latest_time]
            if len(latest_records) != 1:
                lang_result["problems"].append(
                    "ambiguous_latest_review_timestamp:" + ",".join(
                        str(item[1].relative_to(ROOT)) for item in latest_records
                    )
                )
            else:
                _, latest_path, latest_record = latest_records[0]
                latest_rel = str(latest_path.relative_to(ROOT))
                outcome = latest_record.get("review_outcome")
                lang_result["latest_current_candidate_signoff"] = {
                    "path": latest_rel,
                    "review_completed_utc": latest_record.get("review_completed_utc"),
                    "review_outcome": outcome,
                    "problems": [],
                }
                if outcome == "PASS" and not lang_result["problems"]:
                    lang_result["gate"] = "PASS"
                else:
                    lang_result["problems"].append(f"latest_current_candidate_outcome:{outcome}")
        else:
            lang_result["problems"].append("no_current_candidate_signoff")

        overall["languages"][lang] = lang_result

    failed = [lang for lang in LANGUAGES if overall["languages"].get(lang, {}).get("gate") != "PASS"]
    if failed:
        overall["problems"].append("language_signoff_hold:" + ",".join(failed))
    if not overall["problems"]:
        overall["gate"] = "PASS"

    OUT_PATH.write_text(json.dumps(overall, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(overall, ensure_ascii=False, indent=2))
    if overall["gate"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
