#!/usr/bin/env python3
"""Generate pronunciation candidates for the audited language-workbook corpus.

This is intentionally a *candidate* generator, not a linguistic certification step.
It must run only after ``apply_language_workbook_linguistic_repairs.py --write`` has
successfully materialized the 6,000 row-by-row adjudications in the runner.

Outputs are isolated under ``audit/language-workbooks/v1.1-pronunciation`` and do
not modify the learner-facing v1.0 release.  Every candidate row is copied into a
50-row PENDING ledger so pronunciation can be adjudicated individually before any
pronunciation-enhanced workbook is built.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path

from phonemizer import phonemize

ROOT = Path(__file__).resolve().parents[1]
V1_AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
STAGE = V1_AUDIT / "staging_v3"
OUT = ROOT / "audit" / "language-workbooks" / "v1.1-pronunciation"
CANDIDATES = OUT / "candidates"
LEDGERS = OUT / "row_by_row"
MANIFEST = OUT / "candidate_manifest.json"

LANGS = {
    "arabic": {"espeak": "ar", "vocab": ROOT / "arabic_top1000.csv"},
    "french": {"espeak": "fr-fr", "vocab": ROOT / "french_top1000.csv"},
    "urdu": {"espeak": "ur", "vocab": ROOT / "urdu_top1000.csv"},
}

CONTROL_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
MEANING_RE = re.compile(r"(?m)^Meaning:[ \t]*(.*?)[ \t]*$")
POS_RE = re.compile(r"(?m)^Part of speech:[ \t]*(.*?)[ \t]*$")


def fail(message: str) -> None:
    raise SystemExit(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = CONTROL_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def back_field(back: str, regex: re.Pattern[str]) -> str:
    match = regex.search(back or "")
    return clean(match.group(1)) if match else ""


def load_vocab(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for fallback_rank, row in enumerate(csv.DictReader(handle), 1):
            target = clean(row.get("Front") or "")
            back = row.get("Back") or ""
            rank_match = RANK_RE.search(back)
            rank = int(rank_match.group(1)) if rank_match else fallback_rank
            english = back_field(back, MEANING_RE)
            pos = back_field(back, POS_RE)
            if target and english:
                rows.append({"rank": rank, "target": target, "english": english, "pos": pos})
    rows.sort(key=lambda item: item["rank"])
    if len(rows) != 1000 or [row["rank"] for row in rows] != list(range(1, 1001)):
        fail(f"{path}: expected exactly ranks 1..1000")
    return rows


def load_sentences(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    normalized = [
        {
            "rank": int(row["rank"]),
            "target": clean(row["target"]),
            "english": clean(row["english"]),
            "level": clean(row.get("level") or ""),
        }
        for row in rows
    ]
    if len(normalized) != 1000 or [row["rank"] for row in normalized] != list(range(1, 1001)):
        fail(f"{path}: expected exactly ranks 1..1000")
    return normalized


# Longest/specific IPA sequences first.  This deliberately produces an accessible
# *candidate* hint, not an authoritative romanization.  Every hint is audited.
LEARNER_REPLACEMENTS = [
    ("t͡ʃ", "ch"), ("d͡ʒ", "j"), ("tʃ", "ch"), ("dʒ", "j"),
    ("ʃ", "sh"), ("ʒ", "zh"), ("θ", "th"), ("ð", "dh"),
    ("ɣ", "gh"), ("χ", "kh"), ("x", "kh"), ("ħ", "h"), ("ʕ", "‘"),
    ("ɽ", "r"), ("ɖ", "d"), ("ʈ", "t"), ("ɭ", "l"), ("ŋ", "ng"),
    ("ɲ", "ny"), ("ɟ", "gy"), ("ɡ", "g"), ("ɾ", "r"), ("ʁ", "r"),
    ("j", "y"), ("w", "w"), ("ɥ", "w"),
    ("ɑ̃", "an"), ("ɛ̃", "in"), ("ɔ̃", "on"), ("œ̃", "un"),
    ("ɑ", "a"), ("ɐ", "a"), ("ɒ", "o"), ("æ", "a"), ("ə", "uh"),
    ("ɪ", "i"), ("i", "ee"), ("ʊ", "u"), ("u", "oo"),
    ("ɛ", "e"), ("e", "ay"), ("ɔ", "o"), ("o", "oh"),
    ("œ", "eu"), ("ø", "eu"), ("ɜ", "er"), ("ɞ", "o"),
    ("ː", ""), ("ˑ", ""), ("ˈ", ""), ("ˌ", ""),
]


def learner_hint(ipa: str) -> str:
    value = ipa
    for source, replacement in LEARNER_REPLACEMENTS:
        value = value.replace(source, replacement)
    value = value.replace(" ", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -")


def phonemize_rows(rows: list[dict], language: str) -> list[dict]:
    texts = [row["target"] for row in rows]
    ipa_values = phonemize(
        texts,
        language=language,
        backend="espeak",
        strip=True,
        preserve_punctuation=True,
        with_stress=True,
        njobs=4,
    )
    if isinstance(ipa_values, str):
        ipa_values = [ipa_values]
    if len(ipa_values) != len(rows):
        fail(f"phonemizer row-count mismatch for {language}: {len(ipa_values)} != {len(rows)}")

    enriched: list[dict] = []
    for row, ipa_raw in zip(rows, ipa_values):
        ipa = clean(ipa_raw)
        hint = clean(learner_hint(ipa))
        if not ipa or not hint:
            fail(f"blank pronunciation candidate at rank {row['rank']} ({language})")
        enriched.append({**row, "ipa_candidate": ipa, "learner_hint_candidate": hint})
    return enriched


def write_candidate(path: Path, rows: list[dict], source_hash: str, kind: str) -> str:
    if kind == "vocab":
        fields = ["rank", "target", "english", "pos", "ipa_candidate", "learner_hint_candidate", "source_sha256"]
    else:
        fields = ["rank", "target", "english", "level", "ipa_candidate", "learner_hint_candidate", "source_sha256"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "source_sha256": source_hash})
    return sha256(path)


def init_ledgers(lang: str, kind: str, rows: list[dict], reset: bool) -> int:
    LEDGERS.mkdir(parents=True, exist_ok=True)
    created = 0
    for start in range(1, 1001, 50):
        end = start + 49
        path = LEDGERS / f"{lang}_{kind}_{start:04d}_{end:04d}.csv"
        if path.exists() and not reset:
            continue
        fields = [
            "rank", "status", "target", "english", "ipa_candidate",
            "learner_hint_candidate", "issue", "proposed_ipa", "proposed_learner_hint",
        ]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows[start - 1:end]:
                writer.writerow({
                    "rank": row["rank"],
                    "status": "PENDING",
                    "target": row["target"],
                    "english": row["english"],
                    "ipa_candidate": row["ipa_candidate"],
                    "learner_hint_candidate": row["learner_hint_candidate"],
                    "issue": "",
                    "proposed_ipa": "",
                    "proposed_learner_hint": "",
                })
        created += 1
    return created


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset-ledgers",
        action="store_true",
        help="Overwrite pronunciation ledgers. Use only before human pronunciation review begins.",
    )
    args = parser.parse_args()

    if args.reset_ledgers and LEDGERS.exists():
        shutil.rmtree(LEDGERS)

    CANDIDATES.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "v1.1-pronunciation-candidates",
        "status": "NOT RELEASED — MACHINE CANDIDATES REQUIRE ROW-BY-ROW AUDIT",
        "source_requirement": "6,000 repaired rows materialized by apply_language_workbook_linguistic_repairs.py --write",
        "datasets": {},
    }

    for lang, cfg in LANGS.items():
        vocab_path = cfg["vocab"]
        sentence_path = STAGE / f"{lang}_sentences.csv"
        if not vocab_path.exists() or not sentence_path.exists():
            fail(f"missing repaired source for {lang}")

        for kind, source_path, loader in (
            ("vocab", vocab_path, load_vocab),
            ("sentences", sentence_path, load_sentences),
        ):
            source_hash = sha256(source_path)
            rows = loader(source_path)
            enriched = phonemize_rows(rows, cfg["espeak"])
            candidate_path = CANDIDATES / f"{lang}_{kind}.csv"
            candidate_hash = write_candidate(candidate_path, enriched, source_hash, kind)
            ledger_count = init_ledgers(lang, kind, enriched, args.reset_ledgers)
            key = f"{lang}_{kind}"
            manifest["datasets"][key] = {
                "rows": len(enriched),
                "source_path": str(source_path.relative_to(ROOT)),
                "source_sha256": source_hash,
                "candidate_path": str(candidate_path.relative_to(ROOT)),
                "candidate_sha256": candidate_hash,
                "espeak_language": cfg["espeak"],
                "new_ledger_files": ledger_count,
            }

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
