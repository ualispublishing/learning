#!/usr/bin/env python3
"""Repair one known derived pronunciation-candidate provenance defect fail-closed.

French sentence rank 288 is clean in the audited v1.0 staging corpus but was
structurally corrupted in the derived machine candidate CSV.  The linguistic
adjudication is already complete; this script repairs only the candidate/ledger
provenance fields so the normal finalizer can verify candidate-to-ledger alignment.

The repair is deliberately narrow, asserted against the canonical staging row,
and idempotent.  Any unexpected state fails rather than broadening the repair.
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
STAGE = ROOT / "audit" / "language-workbooks" / "v1.0" / "staging_v3" / "french_sentences.csv"
CANDIDATE = ROOT / "audit" / "language-workbooks" / "v1.1-pronunciation" / "candidates" / "french_sentences.csv"
LEDGER = ROOT / "audit" / "language-workbooks" / "v1.1-pronunciation" / "row_by_row" / "french_sentences_0251_0300.csv"
RANK = 288

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
CONTROL_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]")


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


def write_rows(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    for path in (STAGE, CANDIDATE, LEDGER):
        if not path.exists():
            fail(f"missing required file: {path}")

    stage_rows = read_rows(STAGE)
    if len(stage_rows) != 1000:
        fail(f"staging row count changed: {len(stage_rows)}")
    stage = next((row for row in stage_rows if int(row["rank"]) == RANK), None)
    if stage is None:
        fail("canonical staging rank 288 missing")
    stage_target = clean(stage["target"])
    if stage_target != EXPECTED_TARGET:
        fail(f"unexpected canonical target: {stage_target!r}")
    if clean(stage["english"]) != EXPECTED_ENGLISH or clean(stage["level"]) != EXPECTED_LEVEL:
        fail("unexpected canonical English/level at rank 288")
    source_hash = sha256(STAGE)

    # The malformed candidate row may not parse into seven logical fields. Repair
    # exactly its one physical CSV record, then reparse the complete file.
    raw = CANDIDATE.read_text(encoding="utf-8-sig").splitlines()
    matches = [i for i, line in enumerate(raw) if line.startswith(f"{RANK},")]
    if matches != [RANK]:
        # Header is physical line 0, rank N should be line N in this 1-row-per-record file.
        fail(f"candidate rank-288 physical-line invariant failed: {matches}")
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="")
    writer.writerow([
        str(RANK), EXPECTED_TARGET, EXPECTED_ENGLISH, EXPECTED_LEVEL,
        EXPECTED_IPA_CANDIDATE, EXPECTED_HINT_CANDIDATE, source_hash,
    ])
    repaired_line = out.getvalue()
    changed_candidate = raw[matches[0]] != repaired_line
    raw[matches[0]] = repaired_line
    CANDIDATE.write_text("\n".join(raw) + "\n", encoding="utf-8")

    candidate_rows = read_rows(CANDIDATE)
    if len(candidate_rows) != 1000:
        fail(f"candidate row count after repair: {len(candidate_rows)}")
    ranks = [int(row["rank"]) for row in candidate_rows]
    if ranks != list(range(1, 1001)):
        fail("candidate ranks are not exactly 1..1000 after repair")
    cand = candidate_rows[RANK - 1]
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

    # The ledger row itself was also written with unquoted commas in the issue text,
    # so DictReader can shift the final adjudication columns before this repair runs.
    # Repair exactly rank 288's physical record first, then validate the parsed ledger.
    ledger_raw = LEDGER.read_text(encoding="utf-8-sig").splitlines()
    ledger_line_index = (RANK - 251) + 1  # header is line 0; rank 251 is line 1.
    if len(ledger_raw) != 51:
        fail(f"French 251-300 pronunciation ledger physical line count changed: {len(ledger_raw)}")
    if not ledger_raw[ledger_line_index].startswith(f"{RANK},"):
        fail("French rank-288 ledger physical-line invariant failed")
    ledger_out = io.StringIO(newline="")
    ledger_writer = csv.writer(ledger_out, lineterminator="")
    ledger_writer.writerow([
        str(RANK), "REPAIR", EXPECTED_TARGET, EXPECTED_ENGLISH,
        EXPECTED_IPA_CANDIDATE, EXPECTED_HINT_CANDIDATE, ISSUE, FINAL_IPA, FINAL_HINT,
    ])
    repaired_ledger_line = ledger_out.getvalue()
    changed_ledger_line = ledger_raw[ledger_line_index] != repaired_ledger_line
    ledger_raw[ledger_line_index] = repaired_ledger_line
    LEDGER.write_text("\n".join(ledger_raw) + "\n", encoding="utf-8")

    ledger_rows = read_rows(LEDGER)
    if len(ledger_rows) != 50 or [int(r["rank"]) for r in ledger_rows] != list(range(251, 301)):
        fail("French 251-300 pronunciation ledger shape changed")
    led = ledger_rows[RANK - 251]
    if led.get("status") not in {"REPAIR", "HOLD"}:
        fail(f"unexpected pre-repair ledger status: {led.get('status')!r}")
    if led.get("proposed_ipa") not in {"", FINAL_IPA} or led.get("proposed_learner_hint") not in {"", FINAL_HINT}:
        fail("rank 288 final adjudication unexpectedly differs")

    before = dict(led)
    led.update({
        "status": "REPAIR",
        "target": EXPECTED_TARGET,
        "english": EXPECTED_ENGLISH,
        "ipa_candidate": EXPECTED_IPA_CANDIDATE,
        "learner_hint_candidate": EXPECTED_HINT_CANDIDATE,
        "issue": ISSUE,
        "proposed_ipa": FINAL_IPA,
        "proposed_learner_hint": FINAL_HINT,
    })
    fields = [
        "rank", "status", "target", "english", "ipa_candidate",
        "learner_hint_candidate", "issue", "proposed_ipa", "proposed_learner_hint",
    ]
    write_rows(LEDGER, ledger_rows, fields)

    ledger_check = read_rows(LEDGER)
    row = ledger_check[RANK - 251]
    if any(row[key] != value for key, value in {
        "status": "REPAIR", "target": EXPECTED_TARGET, "english": EXPECTED_ENGLISH,
        "ipa_candidate": EXPECTED_IPA_CANDIDATE,
        "learner_hint_candidate": EXPECTED_HINT_CANDIDATE,
        "proposed_ipa": FINAL_IPA, "proposed_learner_hint": FINAL_HINT,
    }.items()):
        fail("ledger verification failed after repair")

    print(json.dumps({
        "gate": "PASS",
        "rank": RANK,
        "canonical_stage_sha256": source_hash,
        "candidate_changed": changed_candidate,
        "ledger_changed": changed_ledger_line or before != led,
        "candidate_rows": len(candidate_rows),
        "ledger_rows": len(ledger_rows),
        "unresolved_rank_288": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
