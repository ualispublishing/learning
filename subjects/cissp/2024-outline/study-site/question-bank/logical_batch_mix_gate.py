#!/usr/bin/env python3
"""Validate composition rules across logical CISSP batches, including sharded files."""
from __future__ import annotations

import collections
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
CANDIDATES = ROOT / "candidates"
BATCH_RE = re.compile(r"^(batch-\d+)(?:-[a-z]+)?\.jsonl$", re.IGNORECASE)


def load_jsonl(path: pathlib.Path) -> list[dict]:
    records: list[dict] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            records.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"FAIL {path.name}:{line_no}: invalid JSON: {exc}") from exc
    return records


def logical_name(path: pathlib.Path) -> str:
    match = BATCH_RE.match(path.name)
    if not match:
        raise SystemExit(f"FAIL unsupported candidate filename for logical-batch grouping: {path.name}")
    return match.group(1).lower()


def validate(name: str, records: list[dict]) -> list[str]:
    errors: list[str] = []
    n = len(records)
    if n < 16:
        return errors

    dist = collections.Counter(r.get("difficulty_tier") for r in records)
    if dist["E"] < n * 0.50:
        errors.append(f"{name}: Exam-calibrated items must be >=50% of the batch ({dist['E']}/{n})")
    if dist["B"] > n * 0.10:
        errors.append(f"{name}: Bellringer-tier items exceed 10% of the batch ({dist['B']}/{n})")

    standard = [r for r in records if r.get("format", "mcq") == "mcq"]
    if standard:
        counts = collections.Counter(r.get("domain_primary") for r in standard)
        domain, count = counts.most_common(1)[0]
        cap = math.floor(len(standard) * 0.35)
        if count > cap:
            errors.append(
                f"{name}: D{domain} is {count}/{len(standard)} primary-domain items "
                f"({count/len(standard):.1%}); max allowed is 35%"
            )
    return errors


def main() -> int:
    grouped: dict[str, list[dict]] = collections.defaultdict(list)
    files = sorted(CANDIDATES.glob("*.jsonl"))
    if not files:
        print("PASS logical_batch_mix batches=0 files=0")
        return 0

    for path in files:
        grouped[logical_name(path)].extend(load_jsonl(path))

    errors: list[str] = []
    checked = 0
    for name in sorted(grouped, key=lambda x: int(x.split("-")[1])):
        records = grouped[name]
        if len(records) >= 16:
            checked += 1
            errors.extend(validate(name, records))

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    print(f"PASS logical_batch_mix batches={checked} files={len(files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
