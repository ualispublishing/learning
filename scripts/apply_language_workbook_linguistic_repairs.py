#!/usr/bin/env python3
"""Apply adjudicated language-workbook linguistic repairs fail-closed.

Consumes audit/language-workbooks/v1.0/linguistic_findings_batch_*.json and
applies exact, rank-bound current->proposed replacements to staged sentence
CSVs. Refuses drift, duplicate learner strings, or progression-band changes.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
STAGE = AUDIT / "staging_v3"
REPORT = AUDIT / "linguistic_repair_application.json"
LANGS = ("arabic", "french", "urdu")
FIELDS = ["rank", "level", "target", "english", "attribution", "words", "contributor"]
DIAC_AR = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").replace("ـ", "")
    s = DIAC_AR.sub("", s)
    return re.sub(r"\s+", " ", s).strip().casefold()


def english_words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", (s or "").casefold())


def band(n: int) -> str:
    return "A" if n <= 4 else "B" if n <= 8 else "C" if n <= 13 else "D"


def load_findings() -> dict[str, list[dict]]:
    merged = {lang: [] for lang in LANGS}
    paths = sorted(AUDIT.glob("linguistic_findings_batch_*.json"))
    if not paths:
        raise SystemExit("no linguistic findings manifests found")
    seen: set[tuple[str, int]] = set()
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for lang in LANGS:
            for item in payload.get(lang, []):
                key = (lang, int(item["rank"]))
                if key in seen:
                    raise SystemExit(f"duplicate repair declaration for {lang} rank {item['rank']}")
                seen.add(key)
                merged[lang].append(item)
    return merged


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"{path}: expected 1000 rows, got {len(rows)}")
    if [int(r["rank"]) for r in rows] != list(range(1, 1001)):
        raise SystemExit(f"{path}: ranks are not exactly 1..1000")
    return rows


def adapted_attribution(lang: str, old: str) -> str:
    if old.startswith("Editorially adapted for workbook correctness;") or old.endswith("Editorially corrected for translation fidelity."):
        return old
    if lang in ("arabic", "french"):
        return "Editorially adapted for workbook correctness; original source attribution: " + old
    return old.rstrip() + " Editorially corrected for translation fidelity."


def duplicate_groups(rows: list[dict], field: str) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[norm(row[field])].append(row)
    out = []
    for key, vals in groups.items():
        if key and len(vals) > 1:
            out.append({
                "normalized": key,
                "rows": [
                    {"rank": int(v["rank"]), "target": v["target"], "english": v["english"]}
                    for v in vals
                ],
            })
    return out


def apply_language(lang: str, findings: list[dict], write: bool) -> dict:
    path = STAGE / f"{lang}_sentences.csv"
    rows = read_rows(path)
    by_rank = {int(r["rank"]): r for r in rows}
    applied: list[int] = []
    already: list[int] = []

    for item in sorted(findings, key=lambda x: int(x["rank"])):
        rank = int(item["rank"])
        row = by_rank[rank]
        current_pair = (row["target"], row["english"])
        expected_pair = (item["current_target"], item["current_english"])
        proposed_pair = (item["proposed_target"], item["proposed_english"])

        if current_pair == proposed_pair:
            already.append(rank)
            continue
        if current_pair != expected_pair:
            raise SystemExit(
                f"DRIFT: {lang} rank {rank}: expected {expected_pair!r}, found {current_pair!r}"
            )

        new_words = len(english_words(item["proposed_english"]))
        old_level = row["level"]
        new_level = band(new_words)
        if new_level != old_level:
            raise SystemExit(
                f"BAND CHANGE BLOCKED: {lang} rank {rank}: {old_level} -> {new_level} "
                f"({new_words} English words); proposed English={item['proposed_english']!r}"
            )

        row["target"] = item["proposed_target"]
        row["english"] = item["proposed_english"]
        row["words"] = str(new_words)
        row["attribution"] = adapted_attribution(lang, row.get("attribution", ""))
        applied.append(rank)

    target_dupes = duplicate_groups(rows, "target")
    english_dupes = duplicate_groups(rows, "english")
    if target_dupes:
        raise SystemExit(f"{lang}: target uniqueness collision(s): {json.dumps(target_dupes[:10], ensure_ascii=False)}")
    if english_dupes:
        raise SystemExit(f"{lang}: English uniqueness collision(s): {json.dumps(english_dupes[:10], ensure_ascii=False)}")

    if write and applied:
        tmp = path.with_suffix(".csv.tmp")
        with tmp.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        tmp.replace(path)

    return {
        "declared": len(findings),
        "applied": applied,
        "already_applied": already,
        "target_unique": 1000,
        "english_unique": 1000,
        "write": write,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    findings = load_findings()
    result = {lang: apply_language(lang, findings[lang], args.write) for lang in LANGS}
    result["gate"] = "PASS_REPAIRS_APPLIED" if args.write else "PASS_DRY_RUN"
    if args.write:
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
