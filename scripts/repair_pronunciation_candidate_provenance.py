#!/usr/bin/env python3
"""Repair known derived pronunciation-candidate provenance defects fail-closed.

The linguistic adjudication is already complete. This script repairs only narrowly
verified candidate/ledger provenance fields, then scans all six 1,000-row datasets
for any remaining candidate-to-ledger drift before the normal finalizer runs.

Repairs are deliberately narrow, asserted against canonical/candidate evidence,
and idempotent. Any unexpected state fails rather than broadening the repair.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "audit" / "language-workbooks" / "v1.1-pronunciation"
CANDIDATES = BASE / "candidates"
LEDGERS = BASE / "row_by_row"
STAGE = ROOT / "audit" / "language-workbooks" / "v1.0" / "staging_v3" / "french_sentences.csv"
FRENCH_CANDIDATE = CANDIDATES / "french_sentences.csv"
FRENCH_LEDGER = LEDGERS / "french_sentences_0251_0300.csv"
ARABIC_LEDGER = LEDGERS / "arabic_sentences_0301_0350.csv"

FRENCH_RANK = 288
EXPECTED_TARGET = "Pouvez-vous signer ici, s'il vous plaît ?"
EXPECTED_ENGLISH = "Could you sign here, please?"
EXPECTED_LEVEL = "B"
EXPECTED_IPA_CANDIDATE = "puvˈevu sinjˈe isˈi, sil vu plˈɛ ?"
EXPECTED_HINT_CANDIDATE = "pohohvayvohoh sayaynyay ayaysayay, sayayl vohoh play ?"
FINAL_IPA = "/puve vu siɲe isi sil vu plɛ/"
FINAL_HINT = "poo-vay voo see-nyay ee-see seel voo pleh"
ISSUE = (
    "Canonical staging row confirms full sentence; repair candidate CSV provenance, "
    "normalize pouvez-vous without /z/, signer with /ɲ/, and remove artificial stresses."
)

ARABIC_RANK = 318
ARABIC_EXPECTED_TARGET = "نريد معرفة السبب."
ARABIC_EXPECTED_ENGLISH = "We want to know why."
ARABIC_EXPECTED_IPA_CANDIDATE = "nrˈiːd mˈaʕrifˌa ʔassˈabab."
ARABIC_EXPECTED_HINT_CANDIDATE = "nrayayd ma‘rayayfa ʔassabab."
ARABIC_FINAL_IPA = "/nuriːdu maʕrifat as-sabab/"
ARABIC_FINAL_HINT = "nurīdu maʿrifat as-sabab"
ARABIC_ISSUE = "Machine omits lexical vowels and fails to realize ta marbuta in construct مَعْرِفَةِ السَّبَب"

CONTROL_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]")
LANGS = ("arabic", "french", "urdu")
KINDS = ("vocab", "sentences")
PROVENANCE_FIELDS = ("target", "english", "ipa_candidate", "learner_hint_candidate")


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


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_line(values: list[str]) -> str:
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="")
    writer.writerow(values)
    return out.getvalue()


def replace_physical_row(path: Path, *, rank: int, first_rank: int, values: list[str]) -> bool:
    raw = path.read_text(encoding="utf-8-sig").splitlines()
    line_index = (rank - first_rank) + 1
    expected_lines = 1 + (50 if first_rank != 1 else 1000)
    if first_rank != 1 and len(raw) != expected_lines:
        fail(f"{path.name}: physical line count changed: {len(raw)}")
    if line_index >= len(raw) or not raw[line_index].startswith(f"{rank},"):
        fail(f"{path.name}: rank-{rank} physical-line invariant failed")
    repaired = csv_line(values)
    changed = raw[line_index] != repaired
    raw[line_index] = repaired
    path.write_text("\n".join(raw) + "\n", encoding="utf-8")
    return changed


def repair_french_288() -> dict:
    for path in (STAGE, FRENCH_CANDIDATE, FRENCH_LEDGER):
        if not path.exists():
            fail(f"missing required file: {path}")

    stage_rows = read_rows(STAGE)
    if len(stage_rows) != 1000:
        fail(f"staging row count changed: {len(stage_rows)}")
    stage = next((row for row in stage_rows if int(row["rank"]) == FRENCH_RANK), None)
    if stage is None:
        fail("canonical staging rank 288 missing")
    if clean(stage["target"]) != EXPECTED_TARGET:
        fail(f"unexpected canonical target: {clean(stage['target'])!r}")
    if clean(stage["english"]) != EXPECTED_ENGLISH or clean(stage["level"]) != EXPECTED_LEVEL:
        fail("unexpected canonical English/level at rank 288")
    source_hash = sha256(STAGE)

    raw = FRENCH_CANDIDATE.read_text(encoding="utf-8-sig").splitlines()
    matches = [i for i, line in enumerate(raw) if line.startswith(f"{FRENCH_RANK},")]
    if matches != [FRENCH_RANK]:
        fail(f"candidate rank-288 physical-line invariant failed: {matches}")
    repaired_candidate = csv_line([
        str(FRENCH_RANK), EXPECTED_TARGET, EXPECTED_ENGLISH, EXPECTED_LEVEL,
        EXPECTED_IPA_CANDIDATE, EXPECTED_HINT_CANDIDATE, source_hash,
    ])
    candidate_changed = raw[matches[0]] != repaired_candidate
    raw[matches[0]] = repaired_candidate
    FRENCH_CANDIDATE.write_text("\n".join(raw) + "\n", encoding="utf-8")

    candidate_rows = read_rows(FRENCH_CANDIDATE)
    if len(candidate_rows) != 1000 or [int(row["rank"]) for row in candidate_rows] != list(range(1, 1001)):
        fail("French sentence candidate shape changed after repair")
    cand = candidate_rows[FRENCH_RANK - 1]
    expected_candidate = {
        "target": EXPECTED_TARGET,
        "english": EXPECTED_ENGLISH,
        "level": EXPECTED_LEVEL,
        "ipa_candidate": EXPECTED_IPA_CANDIDATE,
        "learner_hint_candidate": EXPECTED_HINT_CANDIDATE,
        "source_sha256": source_hash,
    }
    for key, expected in expected_candidate.items():
        if cand.get(key) != expected:
            fail(f"candidate repair mismatch {key}: {cand.get(key)!r} != {expected!r}")

    ledger_changed = replace_physical_row(
        FRENCH_LEDGER,
        rank=FRENCH_RANK,
        first_rank=251,
        values=[
            str(FRENCH_RANK), "REPAIR", EXPECTED_TARGET, EXPECTED_ENGLISH,
            EXPECTED_IPA_CANDIDATE, EXPECTED_HINT_CANDIDATE, ISSUE, FINAL_IPA, FINAL_HINT,
        ],
    )
    ledger_rows = read_rows(FRENCH_LEDGER)
    led = ledger_rows[FRENCH_RANK - 251]
    if led.get("status") != "REPAIR" or led.get("target") != EXPECTED_TARGET or led.get("english") != EXPECTED_ENGLISH:
        fail("French rank 288 repaired ledger identity mismatch")
    if led.get("ipa_candidate") != EXPECTED_IPA_CANDIDATE or led.get("learner_hint_candidate") != EXPECTED_HINT_CANDIDATE:
        fail("French rank 288 repaired candidate pronunciation mismatch")
    if led.get("proposed_ipa") != FINAL_IPA or led.get("proposed_learner_hint") != FINAL_HINT or led.get(None):
        fail("French rank 288 repaired final adjudication mismatch")

    return {
        "rank": FRENCH_RANK,
        "canonical_stage_sha256": source_hash,
        "candidate_changed": candidate_changed,
        "ledger_changed": ledger_changed,
    }


def repair_arabic_318() -> dict:
    candidate_path = CANDIDATES / "arabic_sentences.csv"
    candidates = read_rows(candidate_path)
    if len(candidates) != 1000 or [int(r["rank"]) for r in candidates] != list(range(1, 1001)):
        fail("Arabic sentence candidate shape changed")
    cand = candidates[ARABIC_RANK - 1]
    expected = {
        "target": ARABIC_EXPECTED_TARGET,
        "english": ARABIC_EXPECTED_ENGLISH,
        "ipa_candidate": ARABIC_EXPECTED_IPA_CANDIDATE,
        "learner_hint_candidate": ARABIC_EXPECTED_HINT_CANDIDATE,
    }
    for key, value in expected.items():
        if cand.get(key) != value:
            fail(f"Arabic rank 318 candidate {key} changed: {cand.get(key)!r} != {value!r}")

    before = read_rows(ARABIC_LEDGER)[ARABIC_RANK - 301]
    if before.get("target") != ARABIC_EXPECTED_TARGET or before.get("english") != ARABIC_EXPECTED_ENGLISH:
        fail("Arabic rank 318 ledger identity changed")
    if before.get("ipa_candidate") != ARABIC_EXPECTED_IPA_CANDIDATE:
        fail("Arabic rank 318 ledger IPA candidate changed")
    if before.get("learner_hint_candidate") not in {
        ARABIC_EXPECTED_HINT_CANDIDATE,
        ARABIC_EXPECTED_HINT_CANDIDATE[:-1],
    }:
        fail(f"Arabic rank 318 unexpected learner-hint provenance: {before.get('learner_hint_candidate')!r}")
    if before.get("proposed_ipa") != ARABIC_FINAL_IPA or before.get("proposed_learner_hint") != ARABIC_FINAL_HINT:
        fail("Arabic rank 318 final adjudication unexpectedly differs")

    changed = replace_physical_row(
        ARABIC_LEDGER,
        rank=ARABIC_RANK,
        first_rank=301,
        values=[
            str(ARABIC_RANK), "REPAIR", ARABIC_EXPECTED_TARGET, ARABIC_EXPECTED_ENGLISH,
            ARABIC_EXPECTED_IPA_CANDIDATE, ARABIC_EXPECTED_HINT_CANDIDATE,
            ARABIC_ISSUE, ARABIC_FINAL_IPA, ARABIC_FINAL_HINT,
        ],
    )
    after = read_rows(ARABIC_LEDGER)[ARABIC_RANK - 301]
    for key, value in {
        "status": "REPAIR",
        **expected,
        "proposed_ipa": ARABIC_FINAL_IPA,
        "proposed_learner_hint": ARABIC_FINAL_HINT,
    }.items():
        if after.get(key) != value:
            fail(f"Arabic rank 318 repaired ledger mismatch {key}: {after.get(key)!r}")
    if after.get(None):
        fail("Arabic rank 318 repaired ledger still has overflow CSV fields")
    return {"rank": ARABIC_RANK, "ledger_changed": changed}


def collect_provenance_drifts() -> list[dict]:
    drifts: list[dict] = []
    for lang in LANGS:
        for kind in KINDS:
            candidate_path = CANDIDATES / f"{lang}_{kind}.csv"
            candidates = read_rows(candidate_path)
            if len(candidates) != 1000 or [int(r["rank"]) for r in candidates] != list(range(1, 1001)):
                fail(f"{lang}/{kind}: candidate ranks must be exactly 1..1000")
            by_rank = {int(r["rank"]): r for r in candidates}
            pattern = re.compile(rf"^{re.escape(lang)}_{re.escape(kind)}_(\d{{4}})_(\d{{4}})\.csv$")
            files = []
            for path in LEDGERS.glob(f"{lang}_{kind}_*.csv"):
                m = pattern.match(path.name)
                if m:
                    files.append((int(m.group(1)), int(m.group(2)), path))
            files.sort()
            if len(files) != 20:
                fail(f"{lang}/{kind}: expected 20 ledger files, found {len(files)}")
            rows: list[dict] = []
            for start, end, path in files:
                batch = read_rows(path)
                if [int(r["rank"]) for r in batch] != list(range(start, end + 1)):
                    fail(f"{lang}/{kind}: rank mismatch in {path.name}")
                rows.extend(batch)
            if len(rows) != 1000:
                fail(f"{lang}/{kind}: ledger coverage changed: {len(rows)}")
            for ledger in rows:
                rank = int(ledger["rank"])
                candidate = by_rank[rank]
                for field in PROVENANCE_FIELDS:
                    lv = ledger.get(field) or ""
                    cv = candidate.get(field) or ""
                    if lv != cv:
                        drifts.append({
                            "dataset": f"{lang}/{kind}",
                            "rank": rank,
                            "field": field,
                            "ledger": lv,
                            "candidate": cv,
                        })
    return drifts


def main() -> None:
    french = repair_french_288()
    arabic = repair_arabic_318()
    drifts = collect_provenance_drifts()
    result = {
        "gate": "PASS" if not drifts else "FAIL",
        "verified_repairs": {"french_sentences_288": french, "arabic_sentences_318": arabic},
        "remaining_provenance_drifts": drifts,
        "remaining_provenance_drift_count": len(drifts),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if drifts:
        fail(f"remaining candidate/ledger provenance drifts: {len(drifts)}")


if __name__ == "__main__":
    main()
