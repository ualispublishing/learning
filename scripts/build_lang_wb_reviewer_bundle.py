#!/usr/bin/env python3
"""Build one self-contained LANG-WB v1.0 reviewer handoff bundle.

The bundle is a transport/review aid only. It contains the exact current master
workbook, a blank 2,000-row review ledger, a deterministic candidate binding,
an intentionally incomplete sign-off draft, review instructions, and checksums.
It never fills or infers a human PASS/HOLD/FAIL decision.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import build_lang_wb_native_review_ledgers as ledgers
import prepare_lang_wb_native_signoff_draft as signoff_draft

ROOT = ledgers.ROOT
RELEASE = ledgers.RELEASE
AUDIT = ledgers.AUDIT
DEFAULT_OUTPUT_ROOT = Path(tempfile.gettempdir()) / "lang-wb-reviewer-bundles"
ISSUES = {"arabic": 114, "french": 115, "urdu": 116}
DOCS = {
    "REVIEWER_ONBOARDING.md": AUDIT / "REVIEWER_ONBOARDING.md",
    "FINAL_NATIVE_REVIEW_PACKET.md": AUDIT / "FINAL_NATIVE_REVIEW_PACKET.md",
    "CORRECTNESS_STANDARD.md": AUDIT / "CORRECTNESS_STANDARD.md",
    "NATIVE_SIGNOFF_README.md": AUDIT / "native-signoffs" / "README.md",
    "PR_CHECKLIST.md": ROOT / ".github" / "PULL_REQUEST_TEMPLATE" / "lang-wb-native-signoff.md",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def current_language_inputs(language: str) -> tuple[dict[str, Any], list[dict[str, str]]]:
    manifest = json.loads(ledgers.MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("release") == "v1.0", "unexpected release manifest release")
    require(
        manifest.get("status") == "production_candidate",
        f"reviewer bundles require production_candidate status, got {manifest.get('status')!r}",
    )

    names = ledgers.LANGUAGES[language]
    base = RELEASE / language
    master = base / names["master"]
    vocabulary_path = base / names["vocabulary"]
    sentence_path = base / names["sentences"]
    for path in (master, vocabulary_path, sentence_path):
        require(path.exists(), f"{language}: missing {path}")

    vocabulary = ledgers.read_rows(vocabulary_path)
    sentences = ledgers.read_rows(sentence_path)
    ledgers.validate_source_rows(language, vocabulary, sentences)
    review_rows = ledgers.ledger_rows(vocabulary, sentences)
    require(len(review_rows) == 2000, f"{language}: reviewer ledger must contain 2000 rows")

    decision_sha = (
        manifest.get("sentence_curation", {})
        .get("languages", {})
        .get(language, {})
        .get("decision_sha256")
    )
    require(bool(decision_sha), f"{language}: release manifest missing decision_sha256")

    binding = {
        "schema": "lang-wb-reviewer-bundle-binding-v1",
        "release": "v1.0",
        "release_status": manifest.get("status"),
        "language": language,
        "repository_commit_sha": git_head(),
        "parent_tracker": "https://github.com/ualispublishing/learning/issues/106",
        "language_review_issue": f"https://github.com/ualispublishing/learning/issues/{ISSUES[language]}",
        "master_workbook_path": str(master.relative_to(ROOT)),
        "master_workbook_git_blob_sha": ledgers.git_blob_sha(master),
        "master_workbook_sha256": sha256_file(master),
        "vocabulary_csv_path": str(vocabulary_path.relative_to(ROOT)),
        "vocabulary_csv_git_blob_sha": ledgers.git_blob_sha(vocabulary_path),
        "vocabulary_csv_sha256": sha256_file(vocabulary_path),
        "sentence_csv_path": str(sentence_path.relative_to(ROOT)),
        "sentence_csv_git_blob_sha": ledgers.git_blob_sha(sentence_path),
        "sentence_csv_sha256": sha256_file(sentence_path),
        "sentence_decision_sha256": decision_sha,
        "release_manifest_path": str(ledgers.MANIFEST.relative_to(ROOT)),
        "release_manifest_git_blob_sha": ledgers.git_blob_sha(ledgers.MANIFEST),
        "release_manifest_sha256": sha256_file(ledgers.MANIFEST),
        "review_ledger_rows": len(review_rows),
        "human_review_fields_prefilled": False,
        "note": (
            "This binding identifies the source material used to build the reviewer bundle. "
            "It is not a linguistic sign-off or release authorization."
        ),
    }
    return binding, review_rows


def write_ledger(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ledgers.LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def reviewer_readme(language: str) -> str:
    issue = ISSUES[language]
    display = language.capitalize()
    return f"""# {display} LANG-WB v1.0 reviewer bundle

This package is a **review aid for the production candidate**, not a pre-approved or human-certified release.
No human review outcome is prefilled anywhere in the bundle.

Operational tracker: https://github.com/ualispublishing/learning/issues/{issue}
Parent release tracker: https://github.com/ualispublishing/learning/issues/106

## Contents

- `MASTER_WORKBOOK.pdf` — complete rendered {display} master workbook; review all learner-facing pages.
- `{language}_REVIEW_LEDGER.csv` — 2,000 blank-adjudication rows: 1,000 vocabulary + 1,000 sentence rows.
- `CANDIDATE_BINDING.json` — exact current source/artifact identifiers used to build this bundle.
- `{language}_SIGNOFF_DRAFT.json` — current-candidate-bound but intentionally incomplete human sign-off draft.
- `REVIEWER_ONBOARDING.md` — concise start-to-finish procedure.
- `FINAL_NATIVE_REVIEW_PACKET.md` — canonical full-content review and sign-off rules.
- `CORRECTNESS_STANDARD.md` — learner-facing correctness dimensions.
- `NATIVE_SIGNOFF_README.md` — immutable record and filename rules.
- `PR_CHECKLIST.md` — focused sign-off pull-request checklist.
- `BUNDLE_MANIFEST.json` and `CHECKSUMS.sha256` — transport/integrity evidence for this package.

## Required workflow

1. Read `REVIEWER_ONBOARDING.md`, `FINAL_NATIVE_REVIEW_PACKET.md`, and `CORRECTNESS_STANDARD.md`.
2. Review every row in `{language}_REVIEW_LEDGER.csv`; set `review_outcome` yourself to `PASS`, `FAIL`, or `HOLD` and add notes/corrections where needed.
3. Review the complete `MASTER_WORKBOOK.pdf`, including Foundations, pronunciation guidance, headings, instructions, and other material outside the CSV rows.
4. Do not turn uncertainty into PASS. Preserve FAIL/HOLD findings for remediation.
5. After the required full-content review, complete the human-only fields in `{language}_SIGNOFF_DRAFT.json` truthfully.
6. Submit a **new immutable** sign-off JSON whose filename begins `{language}_` under `audit/language-workbooks/v1.0/native-signoffs/` in the repository.
7. Repository CI independently validates the submitted record and final three-language release state.

A reviewer may complete only this language. Arabic, French, and Urdu are certified independently.
"""


def build_bundle(language: str, output_root: Path, make_zip: bool = True) -> tuple[Path, Path | None]:
    binding, review_rows = current_language_inputs(language)
    names = ledgers.LANGUAGES[language]
    source_master = RELEASE / language / names["master"]

    output_root.mkdir(parents=True, exist_ok=True)
    bundle_dir = output_root / f"{language}_lang_wb_v1.0_reviewer_bundle"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)

    shutil.copy2(source_master, bundle_dir / "MASTER_WORKBOOK.pdf")
    write_ledger(bundle_dir / f"{language}_REVIEW_LEDGER.csv", review_rows)
    (bundle_dir / "CANDIDATE_BINDING.json").write_text(
        json.dumps(binding, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    draft = signoff_draft.build_draft(language)
    (bundle_dir / f"{language}_SIGNOFF_DRAFT.json").write_text(
        json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    for output_name, source in DOCS.items():
        require(source.exists(), f"missing reviewer document: {source}")
        shutil.copy2(source, bundle_dir / output_name)

    (bundle_dir / "README.md").write_text(reviewer_readme(language), encoding="utf-8")

    payload_files = sorted(
        p for p in bundle_dir.iterdir() if p.is_file() and p.name not in {"BUNDLE_MANIFEST.json", "CHECKSUMS.sha256"}
    )
    bundle_manifest = {
        "schema": "lang-wb-reviewer-bundle-v1",
        "release": "v1.0",
        "release_status": "production_candidate",
        "language": language,
        "repository_commit_sha": binding.get("repository_commit_sha"),
        "human_certification_present": False,
        "human_review_fields_prefilled": False,
        "files": [
            {"name": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)} for p in payload_files
        ],
        "note": (
            "This package contains review inputs and an incomplete sign-off draft only. "
            "It does not itself establish a human PASS."
        ),
    }
    (bundle_dir / "BUNDLE_MANIFEST.json").write_text(
        json.dumps(bundle_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    checksum_targets = sorted(p for p in bundle_dir.iterdir() if p.is_file() and p.name != "CHECKSUMS.sha256")
    (bundle_dir / "CHECKSUMS.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.name}\n" for p in checksum_targets), encoding="utf-8"
    )

    zip_path: Path | None = None
    if make_zip:
        zip_path = output_root / f"{language}_lang_wb_v1.0_reviewer_bundle.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(bundle_dir.iterdir()):
                if path.is_file():
                    zf.write(path, arcname=f"{bundle_dir.name}/{path.name}")

    return bundle_dir, zip_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=ledgers.LANGUAGES)
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help=f"Output directory root (default: {DEFAULT_OUTPUT_ROOT})",
    )
    parser.add_argument("--no-zip", action="store_true", help="Build the directory without a ZIP archive.")
    args = parser.parse_args()

    bundle_dir, zip_path = build_bundle(
        args.language, Path(args.output_root).expanduser().resolve(), make_zip=not args.no_zip
    )
    print(
        json.dumps(
            {
                "language": args.language,
                "bundle_directory": str(bundle_dir),
                "zip": str(zip_path) if zip_path else None,
                "human_certification_present": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
