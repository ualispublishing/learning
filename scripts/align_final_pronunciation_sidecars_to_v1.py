#!/usr/bin/env python3
"""Align finalized pronunciation sidecar display text to canonical v1.0 safely.

Pronunciation candidates intentionally normalize Unicode whitespace for phonemizer
stability. Canonical learner text can retain typographic display differences. After
the fail-closed pronunciation finalizer validates all 6,000 adjudications, this gate
first reports every normalized semantic drift across all datasets, then (only when
that preflight is clean) restores exact canonical v1.0 display fields without
changing IPA, learner hints, or audit status.
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


def paths_for(lang: str, kind: str) -> tuple[Path, Path, str, str, list[str]]:
    if kind == "vocab":
        return (
            V1 / lang / f"{lang}_vocabulary_1000.csv",
            FINAL / f"{lang}_vocab_pronunciation.csv",
            "pos",
            "part_of_speech",
            ["rank", "target", "english", "pos", "ipa", "learner_hint", "audit_status"],
        )
    return (
        V1 / lang / f"{lang}_sentence_bank_1000.csv",
        FINAL / f"{lang}_sentences_pronunciation.csv",
        "level",
        "level",
        ["rank", "target", "english", "level", "ipa", "learner_hint", "audit_status"],
    )


def collect_normalized_drifts() -> list[dict]:
    drifts: list[dict] = []
    for lang in LANGS:
        for kind in ("vocab", "sentences"):
            canonical_path, final_path, extra_final, extra_canon, _ = paths_for(lang, kind)
            if not canonical_path.exists() or not final_path.exists():
                fail(f"missing canonical/final file for {lang}/{kind}")
            canonical = rows(canonical_path)
            final = rows(final_path)
            exact_ranks(canonical, f"canonical {lang}/{kind}")
            exact_ranks(final, f"final {lang}/{kind}")
            for c, f in zip(canonical, final):
                rank = int(c["rank"])
                if int(f["rank"]) != rank:
                    drifts.append({"dataset": f"{lang}/{kind}", "rank": rank, "field": "rank", "canonical": c["rank"], "final": f["rank"]})
                    continue
                comparisons = (
                    ("target", c.get("target", ""), f.get("target", "")),
                    ("english", c.get("english", ""), f.get("english", "")),
                    (extra_final, c.get(extra_canon, ""), f.get(extra_final, "")),
                )
                for field, cv, fv in comparisons:
                    if normalized(cv) != normalized(fv):
                        drifts.append({
                            "dataset": f"{lang}/{kind}",
                            "rank": rank,
                            "field": field,
                            "canonical": cv,
                            "final": fv,
                        })
                if not f.get("ipa", "").strip() or not f.get("learner_hint", "").strip():
                    drifts.append({"dataset": f"{lang}/{kind}", "rank": rank, "field": "pronunciation_blank", "canonical": "nonblank", "final": "blank"})
                if f.get("audit_status", "") not in {"PASS", "REPAIR"}:
                    drifts.append({"dataset": f"{lang}/{kind}", "rank": rank, "field": "audit_status", "canonical": "PASS|REPAIR", "final": f.get("audit_status", "")})
    return drifts


def align(lang: str, kind: str) -> dict:
    canonical_path, final_path, extra_final, extra_canon, fields = paths_for(lang, kind)
    canonical = rows(canonical_path)
    final = rows(final_path)
    exact_ranks(canonical, f"canonical {lang}/{kind}")
    exact_ranks(final, f"final {lang}/{kind}")

    display_changes = 0
    for c, f in zip(canonical, final):
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

    drifts = collect_normalized_drifts()
    if drifts:
        print(json.dumps({
            "gate": "FAIL",
            "rows_scanned": 6000,
            "normalized_drift_count": len(drifts),
            "normalized_drifts": drifts,
        }, ensure_ascii=False, indent=2))
        fail(f"canonical v1 normalized display drifts: {len(drifts)}")

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
