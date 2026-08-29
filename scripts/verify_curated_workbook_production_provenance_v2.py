#!/usr/bin/env python3
"""Verify final workbook production with source-aware provenance semantics."""
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
        return decision["source_target"].strip(), decision["source_english"].strip()
    target = decision.get("approved_target")
    english = decision.get("approved_english")
    if not isinstance(target, str) or not target.strip():
        raise SystemExit(f"rank {decision.get('rank')}: approved target missing")
    if not isinstance(english, str) or not english.strip():
        raise SystemExit(f"rank {decision.get('rank')}: approved English missing")
    return target.strip(), english.strip()


def external_tatoeba(attr: str) -> bool:
    value = attr or ""
    return "CC-BY 2.0" in value and "tatoeba.org" in value


def verify_language(language: str, qa: dict) -> dict:
    decisions = load_json(CURATION / f"{language}_sentence_row_decisions.json")
    production = load_csv(OUT / language / f"{language}_sentence_bank_1000.csv")
    drows = decisions.get("rows")
    if not isinstance(drows, list) or len(drows) != 1000:
        raise SystemExit(f"{language}: decision row count is not 1000")
    if len(production) != 1000:
        raise SystemExit(f"{language}: production row count is {len(production)}, expected 1000")

    status_counts = Counter()
    adapted = 0
    expected_external = 0
    for rank, (decision, prod) in enumerate(zip(drows, production), start=1):
        if int(decision.get("rank", -1)) != rank:
            raise SystemExit(f"{language}: decision rank drift at {rank}")
        if int(prod.get("rank", -1)) != rank:
            raise SystemExit(f"{language}: production rank drift at {rank}")

        status = decision.get("status")
        status_counts[status] += 1
        target, english = desired(decision)
        if (prod.get("target"), prod.get("english")) != (target, english):
            raise SystemExit(f"{language} rank {rank}: production CSV does not match final decision")

        source_attr = (decision.get("source_attribution") or "").strip()
        prod_attr = (prod.get("attribution") or "").strip()
        if not source_attr:
            raise SystemExit(f"{language} rank {rank}: decision source provenance is blank")
        if not prod_attr.startswith(source_attr):
            raise SystemExit(f"{language} rank {rank}: source provenance was not retained")
        if external_tatoeba(source_attr):
            expected_external += 1
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
        "sentence_provenance_rows": 1000,
        "sentence_licensed_external_attribution_rows": expected_external,
        "curation_unresolved_rows": 0,
        "pronunciation_foundations": "PASS",
    }
    for key, expected in required_qa.items():
        if language_qa.get(key) != expected:
            raise SystemExit(
                f"{language}: QA field {key!r} is {language_qa.get(key)!r}, expected {expected!r}"
            )

    if language_qa.get("sentence_source_zip_sha256") != decisions.get("source_zip_sha256"):
        raise SystemExit(f"{language}: QA source identity hash does not match final decision ledger")
    if language_qa.get("curation_status_counts") != dict(sorted(status_counts.items())):
        raise SystemExit(f"{language}: QA curation status counts drifted from decision ledger")

    pdfs = sorted((OUT / language).glob("*.pdf"))
    if len(pdfs) != 14:
        raise SystemExit(f"{language}: expected 14 PDFs, found {len(pdfs)}")
    if any(p.stat().st_size < 10000 for p in pdfs):
        raise SystemExit(f"{language}: undersized PDF found")

    return {
        "gate": "PASS",
        "decision_rows": 1000,
        "production_rows": 1000,
        "status_counts": dict(sorted(status_counts.items())),
        "adapted_rows": adapted,
        "target_unique": 1000,
        "english_unique": 1000,
        "provenance_rows": 1000,
        "licensed_external_attribution_rows": expected_external,
        "pdf_count": 14,
    }


def main() -> None:
    qa = load_json(AUDIT / "qa_summary.json")
    pronunciation = load_json(AUDIT / "pronunciation_qa.json")
    release = load_json(AUDIT / "release_gate_v3.json")
    manifest = load_json(OUT / "RELEASE_MANIFEST.json")

    if pronunciation.get("status") != "PASS":
        raise SystemExit("pronunciation QA is not PASS")
    if release.get("gate") != "PASS" or release.get("pdf_count") != 42:
        raise SystemExit("release gate is not PASS with exactly 42 PDFs")
    if release.get("unresolved_editorial_rows") != 0:
        raise SystemExit("release gate reports unresolved editorial rows")
    if release.get("provenance_rows") != 3000:
        raise SystemExit("release gate does not report 3000 provenance rows")
    if manifest.get("release") != "v1.0" or manifest.get("status") != "production_candidate":
        raise SystemExit("release manifest identity/status mismatch")
    curation = manifest.get("sentence_curation", {})
    if curation.get("total_rows") != 3000 or curation.get("unresolved_rows") != 0:
        raise SystemExit("release manifest curation counts are not 3000/0")

    languages = {language: verify_language(language, qa) for language in LANGUAGES}
    all_pdfs = sorted(OUT.glob("*/*.pdf"))
    if len(all_pdfs) != 42:
        raise SystemExit(f"expected 42 total PDFs, found {len(all_pdfs)}")

    result = {
        "release": "v1.0",
        "gate": "PASS",
        "unresolved_editorial_rows": 0,
        "production_rows_aligned_to_final_decisions": 3000,
        "source_provenance_rows": 3000,
        "licensed_external_attribution_rows": sum(
            item["licensed_external_attribution_rows"] for item in languages.values()
        ),
        "pdf_count": 42,
        "pronunciation_gate": "PASS",
        "release_gate": "PASS",
        "languages": languages,
        "claim_scope": (
            "All final row decisions are represented exactly in production sentence CSVs, with "
            "source provenance retained on every row and external license attribution retained where "
            "applicable. Automated corpus, pronunciation, PDF-count, and release gates pass. "
            "Independent native-speaker certification remains separate."
        ),
    }
    path = AUDIT / "production_decision_alignment.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
