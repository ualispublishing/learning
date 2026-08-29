#!/usr/bin/env python3
"""Fail-closed final human sign-off gate for LANG-WB v1.0.

This is intentionally separate from the automated production-candidate release
pipeline. Production-candidate builds may pass without native-speaker sign-off;
promotion beyond production_candidate may not.
"""
from __future__ import annotations

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


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def reviewer_complete(record: dict[str, Any]) -> bool:
    reviewer = record.get("reviewer") or {}
    required = (
        "name_or_identifier",
        "native_or_near_native_status",
        "qualification_basis",
    )
    return all(str(reviewer.get(k, "")).strip() for k in required)


def validate_signoff(
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
    if record.get("review_outcome") != "PASS":
        problems.append("review_outcome")
    if not str(record.get("review_completed_utc", "")).strip():
        problems.append("review_completed_utc")
    if not reviewer_complete(record):
        problems.append("reviewer_qualification")

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

    scope = record.get("scope_attestation") or {}
    for field in REQUIRED_SCOPE_FIELDS:
        if scope.get(field) is not True:
            problems.append(f"scope:{field}")

    if record.get("defects") not in ([], None):
        problems.append("defects_not_empty")
    if record.get("holds") not in ([], None):
        problems.append("holds_not_empty")
    if not str(record.get("attestation", "")).strip():
        problems.append("attestation")
    if not str(record.get("pass_condition_acknowledged", "")).strip():
        problems.append("pass_condition_acknowledged")
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
    overall: dict[str, Any] = {
        "release": "v1.0",
        "gate": "HOLD",
        "manifest_status": manifest.get("status"),
        "release_manifest_git_blob_sha": manifest_blob,
        "languages": {},
        "problems": [],
        "note": "PASS means all three independent full-content human sign-offs bind to the current production candidate. It is not generated from automated linguistic inference.",
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
            "matching_pass_signoff": None,
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
        if not signoffs:
            lang_result["problems"].append("no_signoff_files")
        for path in signoffs:
            try:
                record = load_json(path)
                problems = validate_signoff(
                    record,
                    lang=lang,
                    expected_master_path=master_rel,
                    expected_master_blob=master_blob,
                    expected_decision_sha=expected_decision,
                    expected_manifest_blob=manifest_blob,
                )
            except Exception as exc:  # fail closed on malformed reviewer record
                problems = [f"parse_error:{type(exc).__name__}:{exc}"]
            lang_result["checked_signoffs"].append(
                {"path": str(path.relative_to(ROOT)), "problems": problems}
            )
            if not problems:
                lang_result["matching_pass_signoff"] = str(path.relative_to(ROOT))

        if lang_result["matching_pass_signoff"]:
            lang_result["gate"] = "PASS"
        else:
            lang_result["problems"].append("no_current_candidate_PASS_signoff")
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
