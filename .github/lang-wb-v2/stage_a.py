#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / ".github" / "lang-wb-v2"
PAYLOAD = json.loads((TMP / "payload.json").read_text(encoding="utf-8"))
FIELDS = ["rank","status","note","proposed_target","proposed_english","proposed_pos"]

def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()

def write_csv(path: Path, rows: list[dict], raw: bytes) -> None:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    bom = raw.startswith(b"\xef\xbb\xbf")
    out = io.StringIO(newline="")
    w = csv.DictWriter(out, fieldnames=FIELDS, lineterminator=newline)
    w.writeheader()
    w.writerows(rows)
    text = out.getvalue()
    if bom:
        text = "\ufeff" + text
    path.write_bytes(text.encode("utf-8"))

changed_total = 0
for spec in PAYLOAD["patches"]:
    path = ROOT / spec["path"]
    raw = path.read_bytes()
    actual = blob_sha(raw)
    if actual != spec["expected_blob"]:
        raise SystemExit(f"DRIFT {spec['path']}: expected {spec['expected_blob']} got {actual}")
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if (reader.fieldnames or []) != FIELDS:
            raise SystemExit(f"HEADER DRIFT {spec['path']}: {reader.fieldnames}")
    by_rank = {int(r["rank"]): r for r in rows}
    before = {int(r["rank"]): dict(r) for r in rows}
    expected_changed=[]
    for patch in spec["rows"]:
        rank=int(patch["rank"])
        if rank not in by_rank:
            raise SystemExit(f"MISSING RANK {spec['path']} {rank}")
        replacement={k:(patch.get(k) or "") for k in FIELDS}
        replacement["rank"]=str(rank)
        by_rank[rank].update(replacement)
        expected_changed.append(rank)
    actual_changed=[rank for rank in sorted(by_rank) if by_rank[rank] != before[rank]]
    if actual_changed != sorted(expected_changed):
        raise SystemExit(f"CHANGE SET MISMATCH {spec['path']}: expected {sorted(expected_changed)} got {actual_changed}")
    write_csv(path, rows, raw)
    changed_total += len(actual_changed)

if changed_total != 50:
    raise SystemExit(f"EXPECTED 50 LEDGER ROW CHANGES, GOT {changed_total}")

runner_dst = ROOT / "scripts" / "apply_language_workbook_linguistic_repairs.py"
runner_raw = runner_dst.read_bytes()
if blob_sha(runner_raw) != PAYLOAD["expected_runner_blob"]:
    raise SystemExit(
        f"RUNNER DRIFT expected {PAYLOAD['expected_runner_blob']} got {blob_sha(runner_raw)}"
    )
shutil.copyfile(TMP / "runner.proposed.py", runner_dst)

baseline_dst = ROOT / "audit" / "language-workbooks" / "v1.0" / "vocab_incremental_repair_baselines.json"
if baseline_dst.exists():
    raise SystemExit("baseline manifest unexpectedly already exists; rebase required")
shutil.copyfile(TMP / "vocab_incremental_repair_baselines.json", baseline_dst)

print(json.dumps({
    "status":"PASS_STAGE_A_PREP",
    "ledger_files":len(PAYLOAD["patches"]),
    "ledger_rows_changed":changed_total,
    "runner_installed":str(runner_dst.relative_to(ROOT)),
    "baseline_installed":str(baseline_dst.relative_to(ROOT)),
}, indent=2))
