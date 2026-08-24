#!/usr/bin/env python3
"""Apply completed row-by-row language-workbook adjudications fail-closed.

The row ledgers are the source of truth for 6,000 individually reviewed rows:
3 x 1,000 sentences and 3 x 1,000 vocabulary entries.

Default mode is dry-run. With --write, all sources are validated in memory first;
nothing is written unless every language/content-type gate passes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
STAGE = AUDIT / "staging_v3"
SENT_LEDGER_DIR = AUDIT / "row_by_row"
VOCAB_LEDGER_DIR = AUDIT / "row_by_row_vocab"
REPORT = AUDIT / "ledger_repair_application.json"

LANGS = ("arabic", "french", "urdu")
SENT_FIELDS = ["rank", "level", "target", "english", "attribution", "words", "contributor"]
DIAC_AR = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.*?)\s*$")
POS_RE = re.compile(r"(?m)^Part of speech:\s*(.*?)\s*$")

# Exact Git blob IDs of the sources against which the completed ledgers were reviewed.
# A prior repaired blob recorded in REPORT is also accepted for idempotent reruns.
BASELINE_BLOBS = {
    "sentence": {
        "arabic": "3fb7fd5ae0051d5b8b0afbb96033698a793f958e",
        "french": "7c419dfeba156d65e48a1ea504041fce313ad03c",
        "urdu": "331237f1f567bbb267fae56891b6d2b036dcd73a",
    },
    "vocab": {
        "arabic": "a8dc009cc28c27624d69d517cd38479c5d418fbc",
        "french": "419d96467a78c205996358caaf4ae9ba1ac3caa9",
        "urdu": "f134225f117d94b40f66004bb09bd8c29e2b6560",
    },
}
EXPECTED_VOCAB_DISTINCT = {"arabic": 999, "french": 1000, "urdu": 1000}


def fail(msg: str) -> None:
    raise SystemExit(msg)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").replace("ـ", "")
    s = DIAC_AR.sub("", s)
    return re.sub(r"\s+", " ", s).strip().casefold()


def english_words(s: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", (s or "").casefold())


def band(n: int) -> str:
    return "A" if n <= 4 else "B" if n <= 8 else "C" if n <= 13 else "D"


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def prior_output_blob(kind: str, lang: str) -> str | None:
    if not REPORT.exists():
        return None
    try:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        return payload.get("sources", {}).get(kind, {}).get(lang, {}).get("output_git_blob")
    except Exception:
        return None


def ledger_pattern(lang: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(lang)}(?:_rows)?_(\d{{4}})_(\d{{4}})\.csv$")


def load_ledgers(directory: Path, lang: str, kind: str) -> list[dict]:
    pat = ledger_pattern(lang)
    files: list[tuple[int, int, Path]] = []
    for path in directory.glob("*.csv"):
        m = pat.match(path.name)
        if m:
            files.append((int(m.group(1)), int(m.group(2)), path))
    files.sort()
    if not files:
        fail(f"{kind}/{lang}: no row ledgers found in {directory}")

    merged: dict[int, dict] = {}
    expected_start = 1
    for start, end, path in files:
        if start != expected_start:
            fail(f"{kind}/{lang}: ledger gap/overlap before {path.name}; expected start {expected_start}")
        if end < start:
            fail(f"{kind}/{lang}: invalid range in {path.name}")
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        if [int(r["rank"]) for r in rows] != list(range(start, end + 1)):
            fail(f"{kind}/{lang}: {path.name} ranks do not exactly match filename range")
        for row in rows:
            rank = int(row["rank"])
            if rank in merged:
                fail(f"{kind}/{lang}: duplicate ledger rank {rank}")
            status = (row.get("status") or "").strip().upper()
            if status not in {"PASS", "REPAIR", "HOLD"}:
                fail(f"{kind}/{lang} rank {rank}: invalid status {status!r}")
            row["status"] = status
            merged[rank] = row
        expected_start = end + 1

    if expected_start != 1001 or sorted(merged) != list(range(1, 1001)):
        fail(f"{kind}/{lang}: ledger coverage must be exactly ranks 1..1000")
    holds = [rank for rank, row in merged.items() if row["status"] == "HOLD"]
    if holds:
        fail(f"{kind}/{lang}: unresolved HOLD rows block release: {holds[:30]}")
    for rank, row in merged.items():
        proposals = [
            (row.get("proposed_target") or "").strip(),
            (row.get("proposed_english") or "").strip(),
            (row.get("proposed_pos") or "").strip(),
        ]
        if row["status"] == "REPAIR" and not any(proposals):
            fail(f"{kind}/{lang} rank {rank}: REPAIR has no proposed change")
        if row["status"] == "PASS" and any(proposals):
            fail(f"{kind}/{lang} rank {rank}: PASS unexpectedly contains proposed change")
    return [merged[i] for i in range(1, 1001)]


def source_guard(kind: str, lang: str, raw: bytes) -> tuple[str, str]:
    current = git_blob_sha(raw)
    baseline = BASELINE_BLOBS[kind][lang]
    previous = prior_output_blob(kind, lang)
    allowed = {baseline}
    if previous:
        allowed.add(previous)
    if current not in allowed:
        fail(
            f"DRIFT: {kind}/{lang} source blob {current} is neither audited baseline "
            f"{baseline} nor prior repaired output {previous!r}"
        )
    return current, "baseline" if current == baseline else "prior_repaired"


def adapted_attribution(old: str) -> str:
    marker = "Editorially corrected after complete row-by-row linguistic audit."
    if marker in old:
        return old
    return f"{(old or '').strip()} {marker}".strip()


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


def read_sentence_source(lang: str) -> tuple[Path, bytes, list[dict]]:
    path = STAGE / f"{lang}_sentences.csv"
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames or []
    if fields != SENT_FIELDS:
        fail(f"sentence/{lang}: unexpected headers {fields!r}")
    if len(rows) != 1000:
        fail(f"sentence/{lang}: expected 1000 rows, got {len(rows)}")
    if [int(r["rank"]) for r in rows] != list(range(1, 1001)):
        fail(f"sentence/{lang}: ranks are not exactly 1..1000")
    return path, raw, rows


def plan_sentences(lang: str, ledger: list[dict]) -> dict:
    path, raw, rows = read_sentence_source(lang)
    input_blob, source_state = source_guard("sentence", lang, raw)
    by_rank = {int(r["rank"]): r for r in rows}
    applied: list[int] = []
    already: list[int] = []

    for item in ledger:
        rank = int(item["rank"])
        row = by_rank[rank]
        if item["status"] == "PASS":
            if item.get("target") and row["target"] != item["target"]:
                fail(f"DRIFT: sentence/{lang} PASS rank {rank} target changed")
            if item.get("english") and row["english"] != item["english"]:
                fail(f"DRIFT: sentence/{lang} PASS rank {rank} English changed")
            continue

        proposed_target = (item.get("proposed_target") or "").strip() or row["target"]
        proposed_english = (item.get("proposed_english") or "").strip() or row["english"]
        current_pair = (row["target"], row["english"])
        proposed_pair = (proposed_target, proposed_english)
        if current_pair == proposed_pair:
            already.append(rank)
        else:
            if source_state != "baseline":
                fail(f"DRIFT: sentence/{lang} rank {rank} differs from proposed inside prior repaired source")
            if item.get("target") and current_pair[0] != item["target"]:
                fail(f"DRIFT: sentence/{lang} rank {rank} target no longer matches audited original")
            if item.get("english") and current_pair[1] != item["english"]:
                fail(f"DRIFT: sentence/{lang} rank {rank} English no longer matches audited original")
            new_words = len(english_words(proposed_english))
            new_level = band(new_words)
            if new_level != row["level"]:
                fail(
                    f"BAND CHANGE BLOCKED: sentence/{lang} rank {rank}: "
                    f"{row['level']} -> {new_level}; proposed English={proposed_english!r}"
                )
            row["target"] = proposed_target
            row["english"] = proposed_english
            row["words"] = str(new_words)
            row["attribution"] = adapted_attribution(row.get("attribution", ""))
            applied.append(rank)

    target_dupes = duplicate_groups(rows, "target")
    english_dupes = duplicate_groups(rows, "english")
    if target_dupes:
        fail(f"sentence/{lang}: target uniqueness collision(s): {json.dumps(target_dupes[:10], ensure_ascii=False)}")
    if english_dupes:
        fail(f"sentence/{lang}: English uniqueness collision(s): {json.dumps(english_dupes[:10], ensure_ascii=False)}")

    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=SENT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output_raw = ("\ufeff" + buf.getvalue()).encode("utf-8")
    return {
        "path": path, "raw": output_raw, "input_git_blob": input_blob,
        "output_git_blob": git_blob_sha(output_raw), "source_state": source_state,
        "repairs_declared": sum(1 for x in ledger if x["status"] == "REPAIR"),
        "applied": applied, "already_applied": already,
        "target_unique": 1000, "english_unique": 1000,
    }


def vocab_rank(back: str) -> int:
    m = RANK_RE.search(back or "")
    return int(m.group(1)) if m else -1


def extract_one(rx: re.Pattern[str], back: str, label: str, lang: str, rank: int) -> str:
    matches = rx.findall(back or "")
    if len(matches) != 1:
        fail(f"vocab/{lang} rank {rank}: expected exactly one {label} line, found {len(matches)}")
    return re.sub(r"\s+", " ", matches[0]).strip()


def replace_one(rx: re.Pattern[str], back: str, label: str, value: str, lang: str, rank: int) -> str:
    matches = list(rx.finditer(back or ""))
    if len(matches) != 1:
        fail(f"vocab/{lang} rank {rank}: expected exactly one {label} line, found {len(matches)}")
    prefix = "Meaning: " if label == "Meaning" else "Part of speech: "
    return (back or "")[:matches[0].start()] + prefix + value + (back or "")[matches[0].end():]


def read_vocab_source(lang: str) -> tuple[Path, bytes, list[dict]]:
    path = ROOT / f"{lang}_top1000.csv"
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames or []
    if fields != ["Front", "Back"]:
        fail(f"vocab/{lang}: unexpected headers {fields!r}")
    if len(rows) != 1000:
        fail(f"vocab/{lang}: expected 1000 rows, got {len(rows)}")
    if [vocab_rank(r["Back"]) for r in rows] != list(range(1, 1001)):
        fail(f"vocab/{lang}: embedded ranks are not exactly 1..1000")
    return path, raw, rows


def vocab_duplicate_audit(lang: str, rows: list[dict]) -> tuple[int, list[dict], list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        rank = vocab_rank(row["Back"])
        meaning = extract_one(MEANING_RE, row["Back"], "Meaning", lang, rank).casefold()
        pos = extract_one(POS_RE, row["Back"], "Part of speech", lang, rank).casefold()
        groups[norm(row["Front"])].append({
            "rank": rank, "front": row["Front"], "meaning": meaning, "part_of_speech": pos
        })
    homographs, blocking = [], []
    for normalized, vals in groups.items():
        if not normalized or len(vals) < 2:
            continue
        meanings = [v["meaning"] for v in vals]
        poses = [v["part_of_speech"] for v in vals]
        item = {"normalized_front": normalized, "rows": vals}
        if all(meanings) and all(poses) and len(set(meanings)) == len(vals) and len(set(poses)) == len(vals):
            homographs.append(item)
        else:
            blocking.append(item)
    return len(groups), homographs, blocking


def plan_vocab(lang: str, ledger: list[dict]) -> dict:
    path, raw, rows = read_vocab_source(lang)
    input_blob, source_state = source_guard("vocab", lang, raw)
    by_rank = {vocab_rank(r["Back"]): r for r in rows}
    applied: list[int] = []
    already: list[int] = []

    for item in ledger:
        rank = int(item["rank"])
        row = by_rank[rank]
        current_meaning = extract_one(MEANING_RE, row["Back"], "Meaning", lang, rank)
        current_pos = extract_one(POS_RE, row["Back"], "Part of speech", lang, rank)
        if item["status"] == "PASS":
            continue

        proposed_target = (item.get("proposed_target") or "").strip() or row["Front"]
        proposed_meaning = (item.get("proposed_english") or "").strip() or current_meaning
        proposed_pos = (item.get("proposed_pos") or "").strip() or current_pos
        current = (row["Front"], current_meaning, current_pos)
        proposed = (proposed_target, proposed_meaning, proposed_pos)
        if current == proposed:
            already.append(rank)
            continue
        if source_state != "baseline":
            fail(f"DRIFT: vocab/{lang} rank {rank} differs from proposed inside prior repaired source")
        row["Front"] = proposed_target
        if current_meaning != proposed_meaning:
            row["Back"] = replace_one(MEANING_RE, row["Back"], "Meaning", proposed_meaning, lang, rank)
        if current_pos != proposed_pos:
            row["Back"] = replace_one(POS_RE, row["Back"], "Part of speech", proposed_pos, lang, rank)
        applied.append(rank)

    distinct, homographs, blocking = vocab_duplicate_audit(lang, rows)
    if blocking:
        fail(f"vocab/{lang}: blocking duplicate groups: {json.dumps(blocking[:10], ensure_ascii=False)}")
    if distinct != EXPECTED_VOCAB_DISTINCT[lang]:
        fail(f"vocab/{lang}: expected {EXPECTED_VOCAB_DISTINCT[lang]} normalized fronts, got {distinct}")
    if lang == "arabic":
        if len(homographs) != 1 or homographs[0]["normalized_front"] != norm("ما"):
            fail(f"vocab/arabic: expected sole intentional homograph ما, got {json.dumps(homographs, ensure_ascii=False)}")
    elif homographs:
        fail(f"vocab/{lang}: unexpected homograph groups: {json.dumps(homographs[:10], ensure_ascii=False)}")

    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=["Front", "Back"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output_raw = ("\ufeff" + buf.getvalue()).encode("utf-8")
    return {
        "path": path, "raw": output_raw, "input_git_blob": input_blob,
        "output_git_blob": git_blob_sha(output_raw), "source_state": source_state,
        "repairs_declared": sum(1 for x in ledger if x["status"] == "REPAIR"),
        "applied": applied, "already_applied": already,
        "distinct_normalized_fronts": distinct,
        "intentional_homographs": homographs,
        "blocking_duplicate_groups": 0,
    }


def public_result(plan: dict) -> dict:
    return {k: v for k, v in plan.items() if k not in {"path", "raw"}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    ledgers = {
        "sentence": {lang: load_ledgers(SENT_LEDGER_DIR, lang, "sentence") for lang in LANGS},
        "vocab": {lang: load_ledgers(VOCAB_LEDGER_DIR, lang, "vocab") for lang in LANGS},
    }
    plans = {
        "sentence": {lang: plan_sentences(lang, ledgers["sentence"][lang]) for lang in LANGS},
        "vocab": {lang: plan_vocab(lang, ledgers["vocab"][lang]) for lang in LANGS},
    }
    result = {
        "gate": "PASS_WRITE" if args.write else "PASS_DRY_RUN",
        "coverage": {"sentence_rows": 3000, "vocab_rows": 3000, "total_rows": 6000, "unresolved_holds": 0},
        "sources": {
            kind: {lang: public_result(plans[kind][lang]) for lang in LANGS}
            for kind in ("sentence", "vocab")
        },
    }
    if args.write:
        for kind in ("sentence", "vocab"):
            for lang in LANGS:
                plans[kind][lang]["path"].write_bytes(plans[kind][lang]["raw"])
        REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
