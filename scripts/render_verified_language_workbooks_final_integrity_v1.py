#!/usr/bin/env python3
"""Render and verify workbook v1.0 from source-locked final-integrity decisions.

Historical decision ledgers remain immutable provenance. During this guarded build only,
the script projects the effective final-integrity decisions into the historical ledger
paths so the existing renderer and verifier consume the exact source-locked rows. The
original files are restored byte-for-byte in a finally block before control returns.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import language_workbook_final_integrity_v1 as integrity

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
LANGUAGES = ("arabic", "french", "urdu")


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    review = integrity.write_review_outputs()
    if review["unresolved_rows"]:
        raise SystemExit(
            f"final integrity review incomplete: {review['unresolved_rows']} source-locked rows remain"
        )

    originals: dict[Path, bytes] = {}
    try:
        for language in LANGUAGES:
            path = CURATION / f"{language}_sentence_row_decisions.json"
            originals[path] = path.read_bytes()
            effective = integrity.effective_language(language)
            unresolved = [r for r in effective["rows"] if r.get("status") == integrity.REVIEW_REQUIRED]
            if unresolved:
                raise SystemExit(f"{language}: effective ledger still has {len(unresolved)} unresolved rows")
            path.write_text(json.dumps(effective, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        run([sys.executable, "scripts/build_language_workbooks_from_decisions_v1.py"])
        run([sys.executable, "scripts/verify_curated_workbook_production_v1.py"])
    finally:
        for path, raw in originals.items():
            path.write_bytes(raw)

    # Confirm restoration really happened; production commits must never rewrite provenance ledgers.
    for path, raw in originals.items():
        if path.read_bytes() != raw:
            raise SystemExit(f"historical decision ledger was not restored byte-for-byte: {path}")

    print("Final-integrity render and verification completed with historical ledgers restored.")


if __name__ == "__main__":
    main()
