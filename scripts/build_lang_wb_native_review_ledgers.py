#!/usr/bin/env python3
"""Build human-review worksheets for the LANG-WB v1.0 production candidate.

The generated ledgers are reviewer aids only. They deliberately leave every
review field blank and never infer PASS/HOLD/FAIL. Final certification still
requires review of the complete rendered master workbook and an immutable
FINAL_NATIVE_SIGNOFF_TEMPLATE.json-derived record.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
OUT = AUDIT / "native-review-ledgers"
MANIFEST = RELEASE / "RELEASE_MANIFEST.json"

LANGUAGES: dict[str, dict[str, str]] = {
    "arabic": {
        "master": "00_arabic_complete_master.pdf",
        "vocabulary": "arabic_vocabulary_1000.csv",
        "sentences": "arabic_sentence_bank_1000.csv",
    },
    "french": {
        "master": "00_french_complete_master.pdf",
        "vocabulary": "french_vocabulary_1000.csv",
        "sentences": "french_sentence_bank_1000.csv",
    },
    "urdu": {
        "master": "00_urdu_complete_master.pdf",
        "vocabulary": "urdu_vocabulary_1000.csv",
        "sentences": "urdu_sentence_bank_1000.csv",
    },
}

LEDGER_FIELDS = [
    "item_type",
    "rank",
    "level",
    "target",
    "english",
    "part_of_speech",
    "attribution",
    "review_outcome",
    "defect_type",
    "reviewer_notes",
    "proposed_correction",
]


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate_source_rows(lang: str, vocabulary: list[dict[str, str]], sentences: list[dict[str, str]]) -> None:
    require(len(vocabulary) == 1000, f"{lang}: vocabulary row count is {len(vocabulary)}, expected 1000")
    require(len(sentences) == 1000, f"{lang}: sentence row count is {len(sentences)}, expected 1000")

    for name, rows in (("vocabulary", vocabulary), ("sentences", sentences)):
        ranks = [r.get("rank", "") for r in rows]
        require(ranks == [str(i) for i in range(1, 1001)], f"{lang}: {name} ranks are not exactly 1..1000")
        require(all(r.get("target", "").strip() for r in rows), f"{lang}: blank target in {name}")
        require(all(r.get("english", "").strip() for r in rows), f"{lang}: blank English in {name}")

    require(all("part_of_speech" in r for r in vocabulary), f"{lang}: vocabulary schema missing part_of_speech")
    require(all("level" in r and "attribution" in r for r in sentences), f"{lang}: sentence schema missing level/attribution")


def ledger_rows(vocabulary: list[dict[str, str]], sentences: list[dict[str, str]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for row in vocabulary:
        result.append(
            {
                "item_type": "vocabulary",
                "rank": row["rank"],
                "level": "",
                "target": row["target"],
                "english": row["english"],
                "part_of_speech": row.get("part_of_speech", ""),
                "attribution": "",
                "review_outcome": "",
                "defect_type": "",
                "reviewer_notes": "",
                "proposed_correction": "",
            }
        )
    for row in sentences:
        result.append(
            {
                "item_type": "sentence",
                "rank": row["rank"],
                "level": row.get("level", ""),
                "target": row["target"],
                "english": row["english"],
                "part_of_speech": "",
                "attribution": row.get("attribution", ""),
                "review_outcome": "",
                "defect_type": "",
                "reviewer_notes": "",
                "proposed_correction": "",
            }
        )
    return result


def write_ledger(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    require(MANIFEST.exists(), f"missing release manifest: {MANIFEST}")
    manifest: dict[str, Any] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("release") == "v1.0", "unexpected release manifest")
    require(manifest.get("status") == "production_candidate", "ledger generator expects production_candidate status")

    OUT.mkdir(parents=True, exist_ok=True)
    bindings: dict[str, Any] = {
        "schema": "lang-wb-native-review-ledgers-v1",
        "release": "v1.0",
        "release_status": manifest.get("status"),
        "release_manifest_path": str(MANIFEST.relative_to(ROOT)),
        "release_manifest_git_blob_sha": git_blob_sha(MANIFEST),
        "review_fields_prefilled": False,
        "languages": {},
        "note": (
            "These ledgers are structured human-review aids only. Blank review fields must be completed by a qualified reviewer. "
            "The complete rendered master workbook, including Foundations/headings/instructional text, remains mandatory review scope."
        ),
    }

    manifest_langs = manifest.get("sentence_curation", {}).get("languages", {})
    for lang, names in LANGUAGES.items():
        base = RELEASE / lang
        master = base / names["master"]
        vocabulary_path = base / names["vocabulary"]
        sentence_path = base / names["sentences"]
        for path in (master, vocabulary_path, sentence_path):
            require(path.exists(), f"{lang}: missing {path}")

        vocabulary = read_rows(vocabulary_path)
        sentences = read_rows(sentence_path)
        validate_source_rows(lang, vocabulary, sentences)
        rows = ledger_rows(vocabulary, sentences)
        ledger_path = OUT / f"{lang}_native_review_ledger.csv"
        write_ledger(ledger_path, rows)

        decision_sha = (manifest_langs.get(lang) or {}).get("decision_sha256")
        require(bool(decision_sha), f"{lang}: release manifest missing decision_sha256")
        bindings["languages"][lang] = {
            "ledger_path": str(ledger_path.relative_to(ROOT)),
            "ledger_rows": len(rows),
            "vocabulary_rows": len(vocabulary),
            "sentence_rows": len(sentences),
            "master_workbook_path": str(master.relative_to(ROOT)),
            "master_workbook_git_blob_sha": git_blob_sha(master),
            "vocabulary_csv_path": str(vocabulary_path.relative_to(ROOT)),
            "vocabulary_csv_git_blob_sha": git_blob_sha(vocabulary_path),
            "sentence_csv_path": str(sentence_path.relative_to(ROOT)),
            "sentence_csv_git_blob_sha": git_blob_sha(sentence_path),
            "sentence_decision_sha256": decision_sha,
        }

    binding_path = OUT / "CANDIDATE_BINDINGS.json"
    binding_path.write_text(json.dumps(bindings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(bindings, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
