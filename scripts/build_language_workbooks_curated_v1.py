#!/usr/bin/env python3
"""Curated wrapper for language workbook v1.0 generation.

This wrapper deliberately refuses to regenerate Urdu learner artifacts while the
Urdu sentence curation layer is still blocked. Once the curation file is moved
to `approved_for_regeneration`, only explicitly approved overrides are applied.
The raw Tatoeba/ManyThings attribution is retained and an adaptation notice is
added to edited learner pairs.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE_PATH = HERE / "build_language_workbooks_v1.py"
CURATION_PATH = ROOT / "curation" / "language-workbooks" / "v1.0" / "urdu_sentence_curation.json"

spec = importlib.util.spec_from_file_location("workbook_v1_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"Unable to load base builder: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ORIGINAL_PARSE_SENTENCES = base.parse_sentences


def _load_urdu_curation() -> dict:
    if not CURATION_PATH.exists():
        raise SystemExit(f"Missing mandatory Urdu curation file: {CURATION_PATH}")
    data = json.loads(CURATION_PATH.read_text(encoding="utf-8"))
    if data.get("language") != "urdu" or data.get("release") != "v1.0":
        raise SystemExit("Urdu curation identity/version mismatch")
    return data


def _check_expected(row: dict, override: dict) -> None:
    rank = override["rank"]
    if row.get("rank") != rank:
        raise SystemExit(f"Urdu curation rank mismatch at {rank}")
    if row.get("target") != override.get("expected_target"):
        raise SystemExit(
            f"Urdu source target drift at rank {rank}; refusing to apply a rank-based edit"
        )
    if row.get("english") != override.get("expected_english"):
        raise SystemExit(
            f"Urdu source English drift at rank {rank}; refusing to apply a rank-based edit"
        )


def _apply_approved_overrides(rows: list[dict], data: dict) -> list[dict]:
    edited = [dict(r) for r in rows]
    approved = data.get("approved_overrides", [])
    seen = set()
    for override in approved:
        rank = int(override["rank"])
        if rank in seen or not 1 <= rank <= len(edited):
            raise SystemExit(f"Invalid or duplicate approved Urdu override rank: {rank}")
        seen.add(rank)
        row = edited[rank - 1]
        _check_expected(row, override)
        row["target"] = override["target"]
        row["english"] = override["english"]
        row["words"] = len(base.english_words(row["english"]))
        row["score"] = base.score_sentence(row["english"])
        row["level"] = "A" if row["words"] <= 4 else "B" if row["words"] <= 8 else "C" if row["words"] <= 13 else "D"
        notice = "Editorially adapted for learner accuracy; original source attribution retained"
        if notice not in row["attribution"]:
            row["attribution"] = f"{row['attribution']} | {notice}"

    if len({base.norm(r["target"]) for r in edited}) != len(edited):
        raise SystemExit("Urdu curated target duplicate gate failed")
    return edited


def curated_parse_sentences(cfg):
    rows, candidate_count, zip_hash = ORIGINAL_PARSE_SENTENCES(cfg)
    if cfg.get("code") != "urd":
        return rows, candidate_count, zip_hash

    data = _load_urdu_curation()
    expected_hash = data.get("source", {}).get("manythings_zip_sha256")
    if not expected_hash:
        raise SystemExit("Urdu curation is missing its pinned source ZIP SHA-256")
    if zip_hash != expected_hash:
        raise SystemExit(
            "Urdu ManyThings source ZIP changed from the fully audited source; "
            "refusing rank-based curation until the new source is re-audited"
        )

    # Candidate edits are deliberately checked against the audited source even
    # before approval. This catches upstream/ranking drift early.
    for candidate in data.get("candidate_overrides", []):
        rank = int(candidate["rank"])
        if not 1 <= rank <= len(rows):
            raise SystemExit(f"Invalid Urdu candidate override rank: {rank}")
        _check_expected(rows[rank - 1], candidate)

    if data.get("release_gate") != "ALLOW_REGENERATION" or data.get("status") != "approved_for_regeneration":
        raise SystemExit(
            "Urdu sentence curation is intentionally BLOCKED. Complete second-pass "
            "verification, resolve every blocker, promote only verified edits to "
            "approved_overrides, then set status=approved_for_regeneration and "
            "release_gate=ALLOW_REGENERATION."
        )

    unresolved = data.get("unresolved_blockers", [])
    if unresolved:
        raise SystemExit(f"Urdu curation still has unresolved blockers: {unresolved}")
    return _apply_approved_overrides(rows, data), candidate_count, zip_hash


base.parse_sentences = curated_parse_sentences


if __name__ == "__main__":
    base.main()
