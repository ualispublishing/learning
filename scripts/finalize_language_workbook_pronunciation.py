#!/usr/bin/env python3
"""Validate completed pronunciation ledgers and materialize audited sidecars.

This script is deliberately fail-closed.  It refuses to produce final pronunciation
files while any row is PENDING/HOLD, while a ledger drifts from its machine
candidate, or while any rank is missing/duplicated.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "audit" / "language-workbooks" / "v1.1-pronunciation"
CANDIDATES = BASE / "candidates"
LEDGERS = BASE / "row_by_row"
FINAL = BASE / "final"
MANIFEST = BASE / "final_manifest.json"
LANGS = ("arabic", "french", "urdu")
KINDS = ("vocab", "sentences")


def fail(message: str) -> None:
    raise SystemExit(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_candidate(lang: str, kind: str) -> tuple[Path, list[dict]]:
    path = CANDIDATES / f"{lang}_{kind}.csv"
    if not path.exists():
        fail(f"missing candidate file: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1000 or [int(row["rank"]) for row in rows] != list(range(1, 1001)):
        fail(f"{lang}/{kind}: candidate ranks must be exactly 1..1000")
    return path, rows


def load_ledgers(lang: str, kind: str) -> list[dict]:
    pattern = re.compile(rf"^{re.escape(lang)}_{re.escape(kind)}_(\d{{4}})_(\d{{4}})\.csv$")
    files = []
    for path in LEDGERS.glob(f"{lang}_{kind}_*.csv"):
        match = pattern.match(path.name)
        if match:
            files.append((int(match.group(1)), int(match.group(2)), path))
    files.sort()
    if len(files) != 20:
        fail(f"{lang}/{kind}: expected 20 ledger files, found {len(files)}")

    rows: list[dict] = []
    expected_start = 1
    for start, end, path in files:
        if start != expected_start or end != start + 49:
            fail(f"{lang}/{kind}: bad ledger range at {path.name}")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            batch = list(csv.DictReader(handle))
        expected_ranks = list(range(start, end + 1))
        if [int(row["rank"]) for row in batch] != expected_ranks:
            fail(f"{lang}/{kind}: rank mismatch in {path.name}")
        rows.extend(batch)
        expected_start = end + 1
    if expected_start != 1001:
        fail(f"{lang}/{kind}: ledger coverage incomplete")
    return rows


def materialize_dataset(lang: str, kind: str) -> dict:
    candidate_path, candidates = load_candidate(lang, kind)
    ledgers = load_ledgers(lang, kind)
    candidate_by_rank = {int(row["rank"]): row for row in candidates}
    final_rows: list[dict] = []
    repairs = 0

    for ledger in ledgers:
        rank = int(ledger["rank"])
        candidate = candidate_by_rank[rank]
        for field in ("target", "english", "ipa_candidate", "learner_hint_candidate"):
            if (ledger.get(field) or "") != (candidate.get(field) or ""):
                fail(f"DRIFT {lang}/{kind} rank {rank}: ledger {field} != candidate")

        status = (ledger.get("status") or "").strip().upper()
        if status in {"", "PENDING", "HOLD"}:
            fail(f"{lang}/{kind} rank {rank}: unresolved pronunciation status {status or '<blank>'}")
        if status not in {"PASS", "REPAIR"}:
            fail(f"{lang}/{kind} rank {rank}: invalid status {status!r}")

        proposed_ipa = (ledger.get("proposed_ipa") or "").strip()
        proposed_hint = (ledger.get("proposed_learner_hint") or "").strip()
        issue = (ledger.get("issue") or "").strip()

        if status == "PASS":
            if proposed_ipa or proposed_hint:
                fail(f"{lang}/{kind} rank {rank}: PASS row contains proposed pronunciation repair")
            ipa = candidate["ipa_candidate"]
            hint = candidate["learner_hint_candidate"]
        else:
            if not issue:
                fail(f"{lang}/{kind} rank {rank}: REPAIR requires an issue note")
            if not proposed_ipa and not proposed_hint:
                fail(f"{lang}/{kind} rank {rank}: REPAIR requires at least one proposed field")
            ipa = proposed_ipa or candidate["ipa_candidate"]
            hint = proposed_hint or candidate["learner_hint_candidate"]
            repairs += 1

        if not ipa.strip() or not hint.strip():
            fail(f"{lang}/{kind} rank {rank}: blank final pronunciation field")

        out = {
            "rank": rank,
            "target": candidate["target"],
            "english": candidate["english"],
            "ipa": ipa,
            "learner_hint": hint,
            "audit_status": status,
        }
        if kind == "vocab":
            out["pos"] = candidate.get("pos", "")
        else:
            out["level"] = candidate.get("level", "")
        final_rows.append(out)

    FINAL.mkdir(parents=True, exist_ok=True)
    output_path = FINAL / f"{lang}_{kind}_pronunciation.csv"
    fields = ["rank", "target", "english"]
    fields += ["pos"] if kind == "vocab" else ["level"]
    fields += ["ipa", "learner_hint", "audit_status"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(final_rows)

    return {
        "rows": 1000,
        "repairs": repairs,
        "candidate_sha256": sha256(candidate_path),
        "output_path": str(output_path.relative_to(ROOT)),
        "output_sha256": sha256(output_path),
    }


def main() -> None:
    manifest = {
        "version": "v1.1-pronunciation-final",
        "status": "AUDITED PRONUNCIATION SIDECARS — PDF BUILD STILL SEPARATE",
        "datasets": {},
    }
    for lang in LANGS:
        for kind in KINDS:
            manifest["datasets"][f"{lang}_{kind}"] = materialize_dataset(lang, kind)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
