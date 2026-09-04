#!/usr/bin/env python3
"""Apply completed row-by-row workbook adjudications fail-closed.

The authoritative evidence is 6,000 individually reviewed rows:
3 x 1,000 sentence/translation rows and 3 x 1,000 vocabulary rows.

Default mode is a dry-run. --write is all-or-nothing at the planning stage: every
ledger/source/duplicate gate must pass in memory before any learner source is
written. Corrected sentence translations are re-banded from their corrected
English length; linguistic fidelity is never weakened merely to preserve a
pre-repair selector bucket.
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
VOCAB_INCREMENTAL_BASELINES = AUDIT / "vocab_incremental_repair_baselines.json"
LANGS = ("arabic", "french", "urdu")
SENT_FIELDS = ["rank", "level", "target", "english", "attribution", "words", "contributor"]
DIAC_AR = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
MEANING_RE = re.compile(r"(?m)^Meaning:[ \t]*(.*?)[ \t]*$")
POS_RE = re.compile(r"(?m)^Part of speech:[ \t]*(.*?)[ \t]*$")

# Exact Git blobs of the vocabulary decks that were reviewed row by row.
VOCAB_BASELINE_BLOBS = {
    "arabic": "a8dc009cc28c27624d69d517cd38479c5d418fbc",
    "french": "419d96467a78c205996358caaf4ae9ba1ac3caa9",
    "urdu": "f134225f117d94b40f66004bb09bd8c29e2b6560",
}
EXPECTED_VOCAB_DISTINCT = {"arabic": 999, "french": 1000, "urdu": 1000}


def fail(message: str) -> None:
    raise SystemExit(message)


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").replace("ـ", "")
    text = DIAC_AR.sub("", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def english_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", (text or "").casefold())


def band(word_count: int) -> str:
    return "A" if word_count <= 4 else "B" if word_count <= 8 else "C" if word_count <= 13 else "D"


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def prior_sentence_output_blob(lang: str) -> str | None:
    if not REPORT.exists():
        return None
    try:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        return payload.get("sources", {}).get("sentence", {}).get(lang, {}).get("output_git_blob")
    except Exception:
        return None


def prior_vocab_output_blob(lang: str) -> str | None:
    if not REPORT.exists():
        return None
    try:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        return payload.get("sources", {}).get("vocab", {}).get(lang, {}).get("output_git_blob")
    except Exception:
        return None


def incremental_vocab_round(lang: str) -> dict | None:
    if not VOCAB_INCREMENTAL_BASELINES.exists():
        return None
    try:
        payload = json.loads(VOCAB_INCREMENTAL_BASELINES.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"vocab incremental baseline manifest is unreadable: {exc}")
    if payload.get("schema_version") != 1:
        fail("vocab incremental baseline manifest: unsupported schema_version")
    entry = payload.get("vocab", {}).get(lang)
    if entry is None:
        return None
    blob = (entry.get("input_git_blob") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", blob):
        fail(f"vocab/{lang}: incremental baseline has invalid input_git_blob {blob!r}")
    ranks = entry.get("allowed_new_repair_ranks")
    if (
        not isinstance(ranks, list)
        or not ranks
        or any(not isinstance(rank, int) or rank < 1 or rank > 1000 for rank in ranks)
        or len(set(ranks)) != len(ranks)
    ):
        fail(f"vocab/{lang}: incremental baseline has invalid allowed_new_repair_ranks")
    expected_count = entry.get("expected_new_repair_count")
    if expected_count != len(ranks):
        fail(
            f"vocab/{lang}: incremental baseline expected_new_repair_count "
            f"{expected_count!r} does not equal rank count {len(ranks)}"
        )
    return {"input_git_blob": blob, "allowed_new_repair_ranks": set(ranks)}


def ledger_pattern(lang: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(lang)}(?:_rows)?_(\d{{4}})_(\d{{4}})\.csv$")


def load_ledgers(directory: Path, lang: str, kind: str) -> list[dict]:
    pattern = ledger_pattern(lang)
    files: list[tuple[int, int, Path]] = []
    for path in directory.glob("*.csv"):
        match = pattern.match(path.name)
        if match:
            files.append((int(match.group(1)), int(match.group(2)), path))
    files.sort()
    if not files:
        fail(f"{kind}/{lang}: no row ledgers found")

    merged: dict[int, dict] = {}
    expected_start = 1
    for start, end, path in files:
        if start != expected_start or end < start:
            fail(f"{kind}/{lang}: ledger gap/overlap at {path.name}; expected start {expected_start}")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        expected_ranks = list(range(start, end + 1))
        if [int(row["rank"]) for row in rows] != expected_ranks:
            fail(f"{kind}/{lang}: {path.name} ranks do not match its filename range")
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
            fail(f"{kind}/{lang} rank {rank}: PASS unexpectedly contains a proposed change")
    return [merged[rank] for rank in range(1, 1001)]


def sentence_source_guard(lang: str, raw: bytes) -> tuple[str, str]:
    manifest_path = STAGE / f"{lang}_selection.json"
    if not manifest_path.exists():
        fail(f"sentence/{lang}: missing corpus-selection manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest.get("csv_sha256")
    current_sha256 = hashlib.sha256(raw).hexdigest()
    current_blob = git_blob_sha(raw)
    if expected and current_sha256 == expected:
        return current_blob, "fresh_selected_baseline"
    previous = prior_sentence_output_blob(lang)
    if previous and current_blob == previous:
        return current_blob, "prior_repaired"
    fail(
        f"DRIFT: sentence/{lang} staged sha256 {current_sha256} / blob {current_blob} "
        f"matches neither fresh corpus-selection sha256 {expected!r} nor prior repaired output {previous!r}"
    )


def vocab_source_guard(lang: str, raw: bytes) -> tuple[str, str]:
    current = git_blob_sha(raw)
    baseline = VOCAB_BASELINE_BLOBS[lang]
    incremental = incremental_vocab_round(lang)
    previous = prior_vocab_output_blob(lang)
    if current == baseline:
        return current, "baseline"
    if incremental and current == incremental["input_git_blob"]:
        return current, "incremental_baseline"
    if previous and current == previous:
        return current, "prior_repaired"
    expected_incremental = incremental["input_git_blob"] if incremental else None
    fail(
        f"DRIFT: vocab/{lang} source blob {current} is not audited baseline {baseline}, "
        f"incremental round baseline {expected_incremental!r}, or prior repaired output {previous!r}"
    )


def adapted_attribution(old: str) -> str:
    marker = "Editorially corrected after complete row-by-row linguistic audit."
    if marker in (old or ""):
        return old
    return f"{(old or '').strip()} {marker}".strip()


def sentence_duplicate_groups(rows: list[dict], field: str) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[norm(row[field])].append(row)
    return [
        {
            "normalized": key,
            "rows": [
                {"rank": int(item["rank"]), "target": item["target"], "english": item["english"]}
                for item in values
            ],
        }
        for key, values in groups.items()
        if key and len(values) > 1
    ]


def csv_bytes(rows: list[dict], fields: list[str], original_raw: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in original_raw else "\n"
    had_bom = original_raw.startswith(b"\xef\xbb\xbf")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    text = buffer.getvalue()
    if had_bom:
        text = "\ufeff" + text
    return text.encode("utf-8")


def read_sentence_source(lang: str) -> tuple[Path, bytes, list[dict]]:
    path = STAGE / f"{lang}_sentences.csv"
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    if fields != SENT_FIELDS:
        fail(f"sentence/{lang}: unexpected headers {fields!r}")
    if len(rows) != 1000 or [int(row["rank"]) for row in rows] != list(range(1, 1001)):
        fail(f"sentence/{lang}: source must contain ranks 1..1000 exactly once")
    return path, raw, rows


def plan_sentences(lang: str, ledger: list[dict]) -> dict:
    path, raw, rows = read_sentence_source(lang)
    input_blob, source_state = sentence_source_guard(lang, raw)
    by_rank = {int(row["rank"]): row for row in rows}
    applied: list[int] = []
    already: list[int] = []
    rebanded: list[dict] = []

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

        if current_pair != proposed_pair:
            if item.get("target") and current_pair[0] != item["target"]:
                fail(f"DRIFT: sentence/{lang} rank {rank} target no longer matches audited original")
            if item.get("english") and current_pair[1] != item["english"]:
                fail(f"DRIFT: sentence/{lang} rank {rank} English no longer matches audited original")
            old_level = row["level"]
            new_words = len(english_words(proposed_english))
            new_level = band(new_words)
            row["target"] = proposed_target
            row["english"] = proposed_english
            row["words"] = str(new_words)
            row["level"] = new_level
            row["attribution"] = adapted_attribution(row.get("attribution", ""))
            if old_level != new_level:
                rebanded.append({"rank": rank, "from": old_level, "to": new_level, "words": new_words})
            applied.append(rank)
        else:
            already.append(rank)

    target_dupes = sentence_duplicate_groups(rows, "target")
    english_dupes = sentence_duplicate_groups(rows, "english")
    if target_dupes:
        fail(f"sentence/{lang}: target uniqueness collision(s): {json.dumps(target_dupes[:10], ensure_ascii=False)}")
    if english_dupes:
        fail(f"sentence/{lang}: English uniqueness collision(s): {json.dumps(english_dupes[:10], ensure_ascii=False)}")

    output_raw = csv_bytes(rows, SENT_FIELDS, raw)
    return {
        "path": path,
        "raw": output_raw,
        "input_git_blob": input_blob,
        "output_git_blob": git_blob_sha(output_raw),
        "source_state": source_state,
        "repairs_declared": sum(1 for item in ledger if item["status"] == "REPAIR"),
        "applied": applied,
        "already_applied": already,
        "rebanded": rebanded,
        "target_unique": 1000,
        "english_unique": 1000,
    }


def vocab_rank(back: str) -> int:
    match = RANK_RE.search(back or "")
    return int(match.group(1)) if match else -1


def extract_one(regex: re.Pattern[str], back: str, label: str, lang: str, rank: int) -> str:
    matches = regex.findall(back or "")
    if len(matches) != 1:
        fail(f"vocab/{lang} rank {rank}: expected one {label} line, found {len(matches)}")
    return matches[0].strip()


def replace_one(regex: re.Pattern[str], back: str, label: str, value: str, lang: str, rank: int) -> str:
    matches = list(regex.finditer(back or ""))
    if len(matches) != 1:
        fail(f"vocab/{lang} rank {rank}: expected one {label} line, found {len(matches)}")
    prefix = "Meaning: " if label == "Meaning" else "Part of speech: "
    match = matches[0]
    return (back or "")[: match.start()] + prefix + value + (back or "")[match.end() :]


def read_vocab_source(lang: str) -> tuple[Path, bytes, list[dict]]:
    path = ROOT / f"{lang}_top1000.csv"
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    if fields != ["Front", "Back"]:
        fail(f"vocab/{lang}: unexpected headers {fields!r}")
    if len(rows) != 1000 or [vocab_rank(row["Back"]) for row in rows] != list(range(1, 1001)):
        fail(f"vocab/{lang}: embedded ranks must be exactly 1..1000")
    if any(not norm(row["Front"]) for row in rows):
        fail(f"vocab/{lang}: blank normalized Front")
    return path, raw, rows


def vocab_duplicate_audit(lang: str, rows: list[dict]) -> tuple[int, list[dict], list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        rank = vocab_rank(row["Back"])
        meaning = extract_one(MEANING_RE, row["Back"], "Meaning", lang, rank).casefold()
        pos = extract_one(POS_RE, row["Back"], "Part of speech", lang, rank).casefold()
        groups[norm(row["Front"])].append(
            {"rank": rank, "front": row["Front"], "meaning": meaning, "part_of_speech": pos}
        )
    homographs: list[dict] = []
    blocking: list[dict] = []
    for normalized, values in groups.items():
        if len(values) < 2:
            continue
        meanings = [item["meaning"] for item in values]
        poses = [item["part_of_speech"] for item in values]
        group = {"normalized_front": normalized, "rows": values}
        if all(meanings) and all(poses) and len(set(meanings)) == len(values) and len(set(poses)) == len(values):
            homographs.append(group)
        else:
            blocking.append(group)
    return len(groups), homographs, blocking


def plan_vocab(lang: str, ledger: list[dict]) -> dict:
    path, raw, rows = read_vocab_source(lang)
    input_blob, source_state = vocab_source_guard(lang, raw)
    by_rank = {vocab_rank(row["Back"]): row for row in rows}
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
        if source_state == "incremental_baseline":
            incremental = incremental_vocab_round(lang)
            allowed = incremental["allowed_new_repair_ranks"] if incremental else set()
            if rank not in allowed:
                fail(
                    f"DRIFT: vocab/{lang} rank {rank} differs from its proposal but is not "
                    f"authorized by the exact incremental-round rank lock"
                )
        elif source_state != "baseline":
            fail(
                f"DRIFT: vocab/{lang} rank {rank} differs from its proposal inside "
                f"source state {source_state!r}"
            )

        row["Front"] = proposed_target
        if current_meaning != proposed_meaning:
            row["Back"] = replace_one(MEANING_RE, row["Back"], "Meaning", proposed_meaning, lang, rank)
        if current_pos != proposed_pos:
            row["Back"] = replace_one(POS_RE, row["Back"], "Part of speech", proposed_pos, lang, rank)
        applied.append(rank)

    if source_state == "incremental_baseline":
        incremental = incremental_vocab_round(lang)
        expected_applied = incremental["allowed_new_repair_ranks"] if incremental else set()
        actual_applied = set(applied)
        if actual_applied != expected_applied:
            fail(
                f"vocab/{lang}: incremental round must apply exactly "
                f"{sorted(expected_applied)}, got {sorted(actual_applied)}"
            )

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

    output_raw = csv_bytes(rows, ["Front", "Back"], raw)
    return {
        "path": path,
        "raw": output_raw,
        "input_git_blob": input_blob,
        "output_git_blob": git_blob_sha(output_raw),
        "source_state": source_state,
        "repairs_declared": sum(1 for item in ledger if item["status"] == "REPAIR"),
        "applied": applied,
        "already_applied": already,
        "distinct_normalized_fronts": distinct,
        "intentional_homographs": homographs,
        "blocking_duplicate_groups": 0,
    }


def public_result(plan: dict) -> dict:
    return {key: value for key, value in plan.items() if key not in {"path", "raw"}}


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
