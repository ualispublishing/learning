#!/usr/bin/env python3
"""Curated wrapper for language workbook v1.0 generation.

The completed row-by-row sentence audit is authoritative. This builder does not
invent or independently re-derive edits. It will regenerate a language only when
all 1,000 ranks have an explicit row decision compiled from that audit and every
non-KEEP row has passed second-pass approval.

Allowed build-time states:
- KEEP: use the exact audited source pair unchanged.
- CORRECT_APPROVED: apply the approved pair recorded on that audited row.
- REPLACE_APPROVED: apply the approved replacement pair recorded on that audited row.

Any pending/native-review/missing state blocks regeneration.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE_PATH = HERE / "build_language_workbooks_v1.py"
CURATION_DIR = ROOT / "curation" / "language-workbooks" / "v1.0"

LANGUAGE_BY_CODE = {
    "ara": "arabic",
    "fra": "french",
    "urd": "urdu",
}

spec = importlib.util.spec_from_file_location("workbook_v1_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"Unable to load base builder: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ORIGINAL_PARSE_SENTENCES = base.parse_sentences


def _load_decisions(language: str) -> dict:
    path = CURATION_DIR / f"{language}_sentence_row_decisions.json"
    if not path.exists():
        raise SystemExit(
            f"Missing mandatory audited row-decision file: {path}. "
            "Run scripts/compile_sentence_row_decisions_v1.py first."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("language") != language or data.get("release") != "v1.0":
        raise SystemExit(f"Row-decision identity/version mismatch for {language}")
    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != 1000:
        raise SystemExit(f"{language} must have exactly 1000 row decisions")
    return data


def _check_source_row(language: str, raw_row: dict, decision: dict, rank: int) -> None:
    if int(decision.get("rank", -1)) != rank:
        raise SystemExit(f"{language} row-decision rank mismatch at {rank}")
    if raw_row.get("rank") != rank:
        raise SystemExit(f"{language} raw rank mismatch at {rank}")
    if raw_row.get("target") != decision.get("source_target"):
        raise SystemExit(
            f"{language} source target drift at rank {rank}; refusing audited rank-based curation"
        )
    if raw_row.get("english") != decision.get("source_english"):
        raise SystemExit(
            f"{language} source English drift at rank {rank}; refusing audited rank-based curation"
        )
    if raw_row.get("attribution") != decision.get("source_attribution"):
        raise SystemExit(
            f"{language} source attribution drift at rank {rank}; refusing regeneration"
        )


def _apply_approved_decisions(language: str, raw_rows: list[dict], data: dict) -> list[dict]:
    edited: list[dict] = []
    unresolved: list[tuple[int, str]] = []

    for rank, (raw_row, decision) in enumerate(zip(raw_rows, data["rows"]), start=1):
        _check_source_row(language, raw_row, decision, rank)
        status = decision.get("status")
        row = dict(raw_row)

        if status == "KEEP":
            pass
        elif status in {"CORRECT_APPROVED", "REPLACE_APPROVED"}:
            target = decision.get("approved_target")
            english = decision.get("approved_english")
            if not isinstance(target, str) or not target.strip():
                raise SystemExit(f"{language} rank {rank} has {status} without approved_target")
            if not isinstance(english, str) or not english.strip():
                raise SystemExit(f"{language} rank {rank} has {status} without approved_english")
            if not decision.get("approval_note"):
                raise SystemExit(f"{language} rank {rank} has {status} without approval_note")

            row["target"] = target.strip()
            row["english"] = english.strip()
            row["words"] = len(base.english_words(row["english"]))
            row["score"] = base.score_sentence(row["english"])
            row["level"] = (
                "A" if row["words"] <= 4 else
                "B" if row["words"] <= 8 else
                "C" if row["words"] <= 13 else
                "D"
            )
            notice = "Editorially adapted for learner accuracy; original source attribution retained"
            if notice not in row["attribution"]:
                row["attribution"] = f"{row['attribution']} | {notice}"
        else:
            unresolved.append((rank, str(status)))

        edited.append(row)

    if unresolved:
        preview = ", ".join(f"{rank}:{status}" for rank, status in unresolved[:25])
        raise SystemExit(
            f"{language} regeneration BLOCKED: {len(unresolved)} row decisions are unresolved. "
            f"First unresolved rows: {preview}"
        )

    if len({base.norm(r["target"]) for r in edited}) != len(edited):
        raise SystemExit(f"{language} curated target duplicate gate failed")
    return edited


def curated_parse_sentences(cfg):
    raw_rows, candidate_count, zip_hash = ORIGINAL_PARSE_SENTENCES(cfg)
    language = LANGUAGE_BY_CODE.get(cfg.get("code"))
    if language is None:
        return raw_rows, candidate_count, zip_hash

    data = _load_decisions(language)
    expected_hash = data.get("source_zip_sha256")
    if not expected_hash:
        raise SystemExit(f"{language} row decisions are missing the pinned source ZIP SHA-256")
    if zip_hash != expected_hash:
        raise SystemExit(
            f"{language} source ZIP changed from the fully audited source; "
            "refusing rank-based curation until the new source is re-audited"
        )

    return _apply_approved_decisions(language, raw_rows, data), candidate_count, zip_hash


base.parse_sentences = curated_parse_sentences


if __name__ == "__main__":
    base.main()
