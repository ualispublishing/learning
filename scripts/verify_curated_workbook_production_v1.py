#!/usr/bin/env python3
"""Verify rendered workbook production artifacts match final v1.0 row decisions."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
STAGE = AUDIT / "staging_v3"
OUT = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
LANGUAGES = ("arabic", "french", "urdu")
RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
DIAC_AR = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ـ", "")
    value = DIAC_AR.sub("", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"missing required CSV: {path}")
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def desired(decision: dict) -> tuple[str, str]:
    status = decision.get("status")
    if status not in RESOLVED:
        raise SystemExit(f"rank {decision.get('rank')}: unresolved status {status!r}")
    if status == "KEEP":
        return decision["source_target"], decision["source_english"]
    target = decision.get("approved_target")
    english = decision.get("approved_english")
    if not isinstance(target, str) or not target.strip():
        raise SystemExit(f"rank {decision.get('rank')}: approved target missing")
    if not isinstance(english, str) or not english.strip():
        raise SystemExit(f"rank {decision.get('rank')}: approved English missing")
    return target.strip(), english.strip()


def verify_language(language: str, qa: dict) -> dict:
    decisions = load_json(CURATION / f"{language}_sentence_row_decisions.json")
    staged = load_csv(STAGE / f"{language}_sentences.csv")
    production = load_csv(OUT / language / f"{language}_sentence_bank_1000.csv")

    drows = decisions.get("rows")
    if not isinstance(drows, list) or len(drows) != 1000:
        raise SystemExit(f"{language}: decision row count is not 1000")
    if len(staged) != 1000 or len(production) != 1000:
        raise SystemExit(
            f"{language}: row count mismatch decisions=1000 stage={len(staged)} production={len(production)}"
        )

    status_counts = Counter()
    adapted = 0
    for rank, (decision, stage, prod) in enumerate(zip(drows, staged, production), start=1):
        if int(decision.get("rank", -1)) != rank:
            raise SystemExit(f"{language}: decision rank drift at {rank}")
        if int(stage.get("rank", -1)) != rank or int(prod.get("rank", -1)) != rank:
            raise SystemExit(f"{language}: staged/production rank drift at {rank}")

        status = decision.get("status")
        status_counts[status] += 1
        target, english = desired(decision)
        if (stage.get("target"), stage.get("english")) != (target, english):
            raise SystemExit(f"{language} rank {rank}: staging does not match final decision")
        if (prod.get("target"), prod.get("english")) != (target, english):
            raise SystemExit(f"{language} rank {rank}: production CSV does not match final decision")

        source_attr = (decision.get("source_attribution") or "").strip()
        stage_attr = (stage.get("attribution") or "").strip()
        prod_attr = (prod.get("attribution") or "").strip()
        if not source_attr or not stage_attr.startswith(source_attr) or not prod_attr.startswith(source_attr):
            raise SystemExit(f"{language} rank {rank}: source attribution was not retained")
        if status != "KEEP":
            adapted += 1

    if len({norm(r["target"]) for r in production}) != 1000:
        raise SystemExit(f"{language}: production target uniqueness failed")
    if len({norm(r["english"]) for r in production}) != 1000:
        raise SystemExit(f"{language}: production English uniqueness failed")

    language_qa = qa.get(language, {})
    required_qa = {
        "status": "PASS",
        "corpus_quality_gate": "PASS",
        "vocabulary_rows": 1000,
        "sentence_rows": 1000,
        "sentence_target_unique": 1000,
        "sentence_english_unique": 1000,
    }
    for key, expected in required_qa.items():
        if language_qa.get(key) != expected:
            raise SystemExit(
                f"{language}: QA field {key!r} is {language_qa.get(key)!r}, expected {expected!r}"
            )

    pdfs = sorted((OUT / language).glob("*.pdf"))
    if len(pdfs) != 14:
        raise SystemExit(f"{language}: expected 14 PDFs, found {len(pdfs)}")
    if any(p.stat().st_size <= 0 for p in pdfs):
        raise SystemExit(f"{language}: zero-byte PDF found")

    return {
        "gate": "PASS",
        "decision_rows": 1000,
        "staged_rows": 1000,
        "production_rows": 1000,
        "status_counts": dict(sorted(status_counts.items())),
        "adapted_rows": adapted,
        "target_unique": 1000,
        "english_unique": 1000,
        "pdf_count": 14,
    }


def main() -> None:
    sync = load_json(AUDIT / "curated_staging_sync.json")
    corpus = load_json(STAGE / "corpus_audit.json")
    qa = load_json(AUDIT / "qa_summary.json")
    pronunciation = load_json(AUDIT / "pronunciation_qa.json")
    release = load_json(AUDIT / "release_gate_v3.json")
    manifest = load_json(OUT / "RELEASE_MANIFEST.json")

    if sync.get("gate") != "PASS" or sync.get("unresolved_rows") != 0:
        raise SystemExit("curated staging sync did not pass cleanly")
    for language in LANGUAGES:
        if corpus.get(language, {}).get("gate") != "PASS":
            raise SystemExit(f"{language}: corpus audit is not PASS")
    if pronunciation.get("status") != "PASS":
        raise SystemExit("pronunciation QA is not PASS")
    if release.get("gate") != "PASS" or release.get("pdf_count") != 42:
        raise SystemExit("release gate is not PASS with exactly 42 PDFs")
    if manifest.get("release") != "v1.0" or manifest.get("status") != "production_candidate":
        raise SystemExit("release manifest identity/status mismatch")

    languages = {language: verify_language(language, qa) for language in LANGUAGES}
    all_pdfs = sorted(OUT.glob("*/*.pdf"))
    if len(all_pdfs) != 42:
        raise SystemExit(f"expected 42 total PDFs, found {len(all_pdfs)}")

    result = {
        "release": "v1.0",
        "gate": "PASS",
        "unresolved_editorial_rows": 0,
        "production_rows_aligned_to_final_decisions": 3000,
        "pdf_count": 42,
        "pronunciation_gate": "PASS",
        "release_gate": "PASS",
        "languages": languages,
        "claim_scope": (
            "All final row decisions are represented exactly in staged and production sentence CSVs, "
            "with automated corpus, pronunciation, PDF-count, and release gates passing. "
            "Independent native-speaker certification remains a separate claim."
        ),
    }
    path = AUDIT / "production_decision_alignment.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
