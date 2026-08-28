#!/usr/bin/env python3
"""Synchronize fully resolved v1.0 sentence decisions into staging_v3.

This bridge is intentionally strict and idempotent. For every rank it accepts
only the audited source pair or the final approved pair already in place. Any
other staged text is treated as drift and blocks the production rebuild.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
STAGE = AUDIT / "staging_v3"
RELEASE = "v1.0"
LANGUAGES = ("arabic", "french", "urdu")
RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
FIELDS = ["rank", "level", "target", "english", "attribution", "words", "contributor"]
EDITORIAL_MARKER = "Editorially adapted for learner accuracy; original source attribution retained"
DIAC_AR = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ـ", "")
    value = DIAC_AR.sub("", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def english_words(value: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", (value or "").casefold())


def band(word_count: int) -> str:
    return "A" if word_count <= 4 else "B" if word_count <= 8 else "C" if word_count <= 13 else "D"


def with_editorial_marker(attribution: str) -> str:
    attribution = (attribution or "").strip()
    if EDITORIAL_MARKER in attribution:
        return attribution
    if not attribution:
        raise SystemExit("approved row has blank source attribution")
    return f"{attribution} | {EDITORIAL_MARKER}"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_stage(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"missing staged corpus: {path}")
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise SystemExit(f"{path.name}: unexpected columns {reader.fieldnames!r}")
        return list(reader)


def write_stage(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def desired_pair(decision: dict, status: str) -> tuple[str, str, str]:
    source_target = decision.get("source_target")
    source_english = decision.get("source_english")
    source_attr = decision.get("source_attribution")
    if not all(isinstance(v, str) and v.strip() for v in (source_target, source_english, source_attr)):
        raise SystemExit(f"rank {decision.get('rank')}: incomplete audited source identity")

    if status == "KEEP":
        return source_target, source_english, source_attr

    target = decision.get("approved_target")
    english = decision.get("approved_english")
    if not isinstance(target, str) or not target.strip():
        raise SystemExit(f"rank {decision.get('rank')}: {status} missing approved_target")
    if not isinstance(english, str) or not english.strip():
        raise SystemExit(f"rank {decision.get('rank')}: {status} missing approved_english")
    if not decision.get("approval_note"):
        raise SystemExit(f"rank {decision.get('rank')}: {status} missing approval_note")
    return target.strip(), english.strip(), with_editorial_marker(source_attr)


def sync_language(language: str) -> dict:
    decision_path = CURATION / f"{language}_sentence_row_decisions.json"
    stage_path = STAGE / f"{language}_sentences.csv"
    selection_path = STAGE / f"{language}_selection.json"

    decisions = load_json(decision_path)
    selection = load_json(selection_path)
    rows = load_stage(stage_path)

    if decisions.get("release") != RELEASE or decisions.get("language") != language:
        raise SystemExit(f"{language}: decision identity/release mismatch")
    decision_rows = decisions.get("rows")
    if not isinstance(decision_rows, list) or len(decision_rows) != 1000:
        raise SystemExit(f"{language}: expected exactly 1000 decisions")
    if len(rows) != 1000:
        raise SystemExit(f"{language}: expected exactly 1000 staged rows")
    if selection.get("language") != language or selection.get("rows") != 1000:
        raise SystemExit(f"{language}: staged selection identity/row mismatch")

    source_hash = decisions.get("source_zip_sha256")
    if not source_hash or selection.get("source_hash") != source_hash:
        raise SystemExit(
            f"{language}: staged source hash does not match audited decision source "
            f"({selection.get('source_hash')} != {source_hash})"
        )

    before_hash = sha256(stage_path)
    changed = 0
    already_desired = 0
    status_counts = Counter()

    for expected_rank, (row, decision) in enumerate(zip(rows, decision_rows), start=1):
        try:
            staged_rank = int(row.get("rank", -1))
            decision_rank = int(decision.get("rank", -1))
        except (TypeError, ValueError):
            raise SystemExit(f"{language}: invalid rank at position {expected_rank}")
        if staged_rank != expected_rank or decision_rank != expected_rank:
            raise SystemExit(
                f"{language}: rank drift at position {expected_rank}: "
                f"stage={staged_rank}, decision={decision_rank}"
            )

        status = decision.get("status")
        if status not in RESOLVED:
            raise SystemExit(f"{language} rank {expected_rank}: unresolved status {status!r}")
        status_counts[status] += 1

        source = (
            (decision.get("source_target") or "").strip(),
            (decision.get("source_english") or "").strip(),
            (decision.get("source_attribution") or "").strip(),
        )
        desired = desired_pair(decision, status)
        current = (
            (row.get("target") or "").strip(),
            (row.get("english") or "").strip(),
            (row.get("attribution") or "").strip(),
        )

        # For approved rows, permit an already-applied pair whose attribution still
        # equals the audited source attribution; normalize it to the stable marker.
        desired_text = desired[:2]
        if current == desired:
            already_desired += 1
        elif current[:2] == desired_text and current[2] in {source[2], desired[2]}:
            row["attribution"] = desired[2]
            if current[2] != desired[2]:
                changed += 1
            else:
                already_desired += 1
        elif current == source:
            row["target"], row["english"], row["attribution"] = desired
            if desired != source:
                changed += 1
            else:
                already_desired += 1
        else:
            raise SystemExit(
                f"{language} rank {expected_rank}: staged row drift; current pair is "
                "neither the audited source nor the final approved pair"
            )

        words = len(english_words(row["english"]))
        row["words"] = str(words)
        row["level"] = band(words)
        row["rank"] = str(expected_rank)
        row["contributor"] = (row.get("contributor") or "").strip()

    targets = [norm(r["target"]) for r in rows]
    english = [norm(r["english"]) for r in rows]
    if len(set(targets)) != 1000:
        raise SystemExit(f"{language}: curated staged target uniqueness gate failed")
    if len(set(english)) != 1000:
        raise SystemExit(f"{language}: curated staged English uniqueness gate failed")

    write_stage(stage_path, rows)
    after_hash = sha256(stage_path)

    bands = Counter(r["level"] for r in rows)
    question_bands = Counter(r["level"] for r in rows if "?" in r["english"])
    question_count = sum(question_bands.values())

    quality = selection.setdefault("quality", {})
    quality["target_unique"] = 1000
    quality["english_unique"] = 1000
    quality["question_count"] = question_count
    quality["question_share"] = round(question_count / 1000, 3)
    quality["band_counts"] = dict(sorted(bands.items()))
    quality["question_band_counts"] = dict(sorted(question_bands.items()))
    selection["csv_sha256"] = after_hash
    selection["curation_release"] = RELEASE
    selection["curation_decision_sha256"] = sha256(decision_path)
    selection["curation_status"] = "all_resolved"
    selection["curation_applied_changes"] = changed
    selection_path.write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "language": language,
        "gate": "PASS",
        "rows": 1000,
        "status_counts": dict(sorted(status_counts.items())),
        "changes_applied_this_run": changed,
        "rows_already_at_desired_pair": already_desired,
        "target_unique": 1000,
        "english_unique": 1000,
        "question_count": question_count,
        "band_counts": dict(sorted(bands.items())),
        "source_zip_sha256": source_hash,
        "decision_sha256": sha256(decision_path),
        "staging_csv_sha256_before": before_hash,
        "staging_csv_sha256_after": after_hash,
    }


def main() -> None:
    results = {language: sync_language(language) for language in LANGUAGES}
    payload = {
        "release": RELEASE,
        "gate": "PASS",
        "languages": results,
        "total_rows": sum(r["rows"] for r in results.values()),
        "unresolved_rows": 0,
        "policy": (
            "Strict idempotent sync: every staged row must equal either its audited "
            "source identity or its final approved identity; all other drift blocks."
        ),
    }
    out = AUDIT / "curated_staging_sync.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
