#!/usr/bin/env python3
"""Align finalized pronunciation sidecar display text to canonical v1.0 safely.

Pronunciation candidates intentionally normalize Unicode whitespace for phonemizer
stability.  Canonical French learner text can retain typographic narrow no-break
spaces before punctuation.  After the fail-closed pronunciation finalizer has
validated all 6,000 adjudications, this gate verifies normalized semantic identity
and restores the *exact canonical v1.0 display fields* without changing IPA,
learner hints, or audit status.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
BASE = ROOT / "audit" / "language-workbooks" / "v1.1-pronunciation"
FINAL = BASE / "final"
MANIFEST = BASE / "final_manifest.json"
LANGS = ("arabic", "french", "urdu")


def fail(message: str) -> None:
    raise SystemExit(message)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value or "")).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def exact_ranks(data: list[dict], label: str) -> None:
    try:
        ranks = [int(row["rank"]) for row in data]
    except Exception as exc:
        fail(f"{label}: invalid rank: {exc}")
    if len(data) != 1000 or ranks != list(range(1, 1001)):
        fail(f"{label}: expected exactly ranks 1..1000")


def align(lang: str, kind: str) -> dict:
    if kind == "vocab":
        canonical_path = V1 / lang / f"{lang}_vocabulary_1000.csv"
        final_path = FINAL / f"{lang}_vocab_pronunciation.csv"
        extra_final = "pos"
        extra_canon = "part_of_speech"
        fields = ["rank", "target", "english", "pos", "ipa", "learner_hint", "audit_status"]
    else:
        canonical_path = V1 / lang / f"{lang}_sentence_bank_1000.csv"
        final_path = FINAL / f"{lang}_sentences_pronunciation.csv"
        extra_final = extra_canon = "level"
        fields = ["rank", "target", "english", "level", "ipa", "learner_hint", "audit_status"]

    if not canonical_path.exists() or not final_path.exists():
        fail(f"missing canonical/final file for {lang}/{kind}")
    canonical = rows(canonical_path)
    final = rows(final_path)
    exact_ranks(canonical, f"canonical {lang}/{kind}")
    exact_ranks(final, f"final {lang}/{kind}")

    display_changes = 0
    for c, f in zip(canonical, final):
        rank = int(c["rank"])
        if int(f["rank"]) != rank:
            fail(f"rank drift {lang}/{kind} {rank}")
        if normalized(c["target"]) != normalized(f["target"]):
            fail(f"target drift {lang}/{kind} rank {rank}: {c['target']!r} vs {f['target']!r}")
        if normalized(c["english"]) != normalized(f["english"]):
            fail(f"English drift {lang}/{kind} rank {rank}")
        if normalized(c.get(extra_canon, "")) != normalized(f.get(extra_final, "")):
            fail(f"metadata drift {lang}/{kind} rank {rank}: {extra_final}")
        if not f.get("ipa", "").strip() or not f.get("learner_hint", "").strip():
            fail(f"blank pronunciation {lang}/{kind} rank {rank}")
        if f.get("audit_status", "") not in {"PASS", "REPAIR"}:
            fail(f"unresolved audit status {lang}/{kind} rank {rank}")

        canonical_extra = c.get(extra_canon, "")
        if f["target"] != c["target"] or f["english"] != c["english"] or f.get(extra_final, "") != canonical_extra:
            display_changes += 1
        f["target"] = c["target"]
        f["english"] = c["english"]
        f[extra_final] = canonical_extra

    with final_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(final)

    reread = rows(final_path)
    exact_ranks(reread, f"aligned {lang}/{kind}")
    for c, f in zip(canonical, reread):
        if c["target"] != f["target"] or c["english"] != f["english"] or c.get(extra_canon, "") != f.get(extra_final, ""):
            fail(f"exact canonical display alignment failed {lang}/{kind} rank {c['rank']}")
    return {
        "rows": 1000,
        "canonical_display_changes": display_changes,
        "output_path": str(final_path.relative_to(ROOT)),
        "output_sha256": sha256(final_path),
    }


def main() -> None:
    if not MANIFEST.exists():
        fail("missing final pronunciation manifest")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    datasets = manifest.get("datasets", {})
    expected = {f"{lang}_{kind}" for lang in LANGS for kind in ("vocab", "sentences")}
    if set(datasets) != expected:
        fail("final manifest does not contain exactly six pronunciation datasets")

    results = {}
    for lang in LANGS:
        for kind in ("vocab", "sentences"):
            key = f"{lang}_{kind}"
            result = align(lang, kind)
            results[key] = result
            datasets[key]["output_sha256"] = result["output_sha256"]
            datasets[key]["canonical_display_alignment"] = True
            datasets[key]["canonical_display_changes"] = result["canonical_display_changes"]

    manifest["canonical_v1_display_alignment"] = {
        "gate": "PASS",
        "rows": 6000,
        "normalized_drift": 0,
        "datasets": results,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["canonical_v1_display_alignment"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
