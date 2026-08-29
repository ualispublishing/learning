#!/usr/bin/env python3
"""Decision-ledger workbook build with truthful per-language provenance semantics.

This wraps the v1 decision-ledger renderer without changing its historical behavior.
The older QA field ``sentence_attribution_rows`` specifically counted Tatoeba/CC-BY
attribution. That is valid for Arabic and French, but Urdu v1.0 is an audited UALIS
controlled-original corpus whose decision rows carry UALIS provenance instead.

The v2 release gate therefore distinguishes:
- source provenance: required for every production row; and
- licensed external attribution: required exactly where the decision ledger says the
  row is external Tatoeba/CC-BY material.
"""
from __future__ import annotations

import json
from pathlib import Path

import build_language_workbooks_from_decisions_v1 as legacy

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
OUT = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
LANGUAGES = ("arabic", "french", "urdu")


def is_external_tatoeba(attr: str) -> bool:
    value = attr or ""
    return "CC-BY 2.0" in value and "tatoeba.org" in value


def is_ualis_controlled(attr: str) -> bool:
    return (attr or "").strip().startswith("Original controlled learner sentence — UALIS Publishing v1.0.")


def provenance_profile(language: str) -> dict:
    rows = legacy.DECISIONS[language]["rows"]
    attrs = [(row.get("source_attribution") or "").strip() for row in rows]
    if len(attrs) != 1000 or any(not attr for attr in attrs):
        raise SystemExit(f"{language}: every decision row must have nonblank source provenance")
    external = sum(is_external_tatoeba(attr) for attr in attrs)
    controlled = sum(is_ualis_controlled(attr) for attr in attrs)
    if external == 1000:
        mode = "external_tatoeba_cc_by_2_0_france"
        source_type = "ManyThings/Tatoeba CC BY 2.0 France; final row-audited decision corpus"
        source_locator = legacy.base.LANGS[language]["zip"]
    elif controlled == 1000:
        mode = "ualis_controlled_original"
        source_type = "UALIS Publishing original controlled learner sentence corpus; final row-audited decision corpus"
        source_locator = f"internal://ualis/language-workbooks/v1.0/{language}-controlled-originals"
    else:
        raise SystemExit(
            f"{language}: unsupported mixed provenance profile external={external}, controlled={controlled}"
        )
    return {
        "mode": mode,
        "source_type": source_type,
        "source_locator": source_locator,
        "provenance_rows": len(attrs),
        "licensed_external_attribution_rows": external,
        "ualis_controlled_original_rows": controlled,
    }


PROFILES = {language: provenance_profile(language) for language in LANGUAGES}


def truthful_sources_with_pronunciation() -> str:
    pronunciation = legacy.pronunciation
    return '''<section class="section-start license"><h2>Sources, licensing, and QA scope</h2>
<p><strong>Vocabulary:</strong> drawn from this repository's canonical audited top-1,000 deck for the language. Repository source and audit records remain the source of truth.</p>
<p><strong>Sentence provenance:</strong> Arabic and French sentence pairs originate from the ManyThings bilingual exports of the Tatoeba Project and retain their supplied sentence-level attribution under CC BY 2.0 France. Urdu v1.0 uses UALIS Publishing original controlled learner sentences; those rows carry UALIS source provenance and are not represented as third-party Tatoeba quotations.</p>
<p><strong>Editorial curation:</strong> the sentence corpus is rendered from the versioned v1.0 row-decision ledger for each language. KEEP rows retain the audited pair exactly; approved corrections retain the row's original source provenance and are marked as editorial adaptations.</p>
<p><strong>Pronunciation foundations:</strong> broad-IPA and articulatory guidance was cross-checked against Karin C. Ryding, <em>A Reference Grammar of Modern Standard Arabic</em>; Bernard Tranel, <em>The Sounds of French</em>; Saleem et al., <em>Urdu Consonantal and Vocalic Sounds</em>; and the Omniglot Urdu-script reference. These are broad learner reference targets, not a claim of one accent-free realization.</p>
<p><strong>Quality scope:</strong> release gates check canonical dataset integrity, exact row-decision alignment, duplicate handling, source provenance, applicable external-license attribution, PDF structure, font support, and renderability. These controls materially reduce release risk but do not substitute for independent native-speaker certification; no absolute error-free claim is made.</p>
</section>'''


def corrected_enrich_and_gate() -> None:
    legacy.pronunciation.write_qa()
    pronunciation_qa = legacy.pronunciation.audit_payload()
    release_problems: list[str] = []
    enriched: dict[str, dict] = {}

    for language in LANGUAGES:
        qpath = AUDIT / f"{language}_qa.json"
        q = json.loads(qpath.read_text(encoding="utf-8"))
        decisions = legacy.DECISIONS[language]
        status_counts = legacy.DECISION_META[language]["status_counts"]
        profile = PROFILES[language]

        rendered_provenance = sum(bool((row.get("attribution") or "").strip()) for row in legacy.FINAL_ROWS[language])
        rendered_external = sum(is_external_tatoeba(row.get("attribution") or "") for row in legacy.FINAL_ROWS[language])

        checks = {
            "vocabulary_rows": q.get("vocabulary_rows") == 1000,
            "sentence_rows": q.get("sentence_rows") == 1000,
            "target_unique": q.get("sentence_target_unique") == 1000,
            "english_unique": q.get("sentence_english_unique") == 1000,
            "provenance_rows": rendered_provenance == 1000,
            "licensed_external_attribution_rows": rendered_external == profile["licensed_external_attribution_rows"],
            "legacy_external_attribution_metric": q.get("sentence_attribution_rows") == profile["licensed_external_attribution_rows"],
            "source_hash": q.get("sentence_source_zip_sha256") == decisions.get("source_zip_sha256"),
            "pdf_count": len(q.get("pdfs", {})) == 14,
            "pdf_nonempty_pages": all(
                item.get("pages", 0) >= 1 and item.get("bytes", 0) >= 10000
                for item in q.get("pdfs", {}).values()
            ),
            "all_decisions_resolved": sum(status_counts.values()) == 1000
            and set(status_counts).issubset(legacy.RESOLVED),
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            release_problems.append(f"{language}: {', '.join(failed)}")

        q["sentence_build_basis"] = "final v1.0 row-decision ledger"
        q["sentence_candidates_after_hard_filters"] = None
        q["sentence_candidate_metric_scope"] = (
            "Not recomputed during decision-ledger rendering; exactly 1000 resolved audited rows are eligible."
        )
        q["sentence_source_type"] = profile["source_type"]
        q["sentence_source_url"] = profile["source_locator"]
        q["sentence_provenance_mode"] = profile["mode"]
        q["sentence_provenance_rows"] = rendered_provenance
        q["sentence_licensed_external_attribution_rows"] = rendered_external
        q["sentence_ualis_controlled_original_rows"] = profile["ualis_controlled_original_rows"]
        q["sentence_attribution_rows_metric_scope"] = (
            "Legacy field: counts only rows whose attribution contains Tatoeba CC-BY 2.0 metadata; "
            "use sentence_provenance_rows for the all-source provenance gate."
        )
        if profile["mode"] == "ualis_controlled_original":
            q["sentence_source_hash_role"] = (
                "Pinned decision-ledger source identity retained for reproducibility; it does not imply "
                "that the controlled-original Urdu rows are Tatoeba quotations."
            )
        q["sentence_question_share"] = round(q.get("sentence_question_count", 0) / 1000, 3)
        q["curation_release"] = legacy.RELEASE
        q["curation_status_counts"] = status_counts
        q["curation_adapted_rows"] = legacy.DECISION_META[language]["adapted_rows"]
        q["curation_unresolved_rows"] = 0
        q["curation_decision_sha256"] = legacy.base.sha256(CURATION / f"{language}_sentence_row_decisions.json")
        q["pronunciation_foundations"] = pronunciation_qa["status"]
        q["corpus_quality_checks"] = checks
        q["corpus_quality_gate"] = "PASS" if not failed else "FAIL"
        qpath.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        enriched[language] = q

    if pronunciation_qa.get("status") != "PASS":
        release_problems.append("pronunciation guide QA is not PASS")
    if set(pronunciation_qa.get("languages", [])) != set(LANGUAGES):
        release_problems.append("pronunciation language set mismatch")

    pdfs = sorted(OUT.glob("*/*.pdf"))
    if len(pdfs) != 42:
        release_problems.append(f"pdf_count={len(pdfs)}")

    (AUDIT / "qa_summary.json").write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = [
        "# Language Workbooks v1.0 - final curated automated QA",
        "",
        "All 3,000 sentence ranks have resolved, source-locked v1.0 editorial decisions. Production is rendered directly from those ledgers.",
        "",
    ]
    for language, q in enriched.items():
        report.extend([
            f"## {language.title()}",
            f"- Vocabulary: {q['vocabulary_rows']} entries.",
            f"- Sentences: {q['sentence_rows']} rows; {q['sentence_target_unique']} unique target strings; {q['sentence_english_unique']} unique English strings.",
            f"- Source provenance retained: {q['sentence_provenance_rows']}/{q['sentence_rows']} rows.",
            f"- Licensed external Tatoeba attribution: {q['sentence_licensed_external_attribution_rows']}/{q['sentence_rows']} rows.",
            f"- UALIS controlled-original rows: {q['sentence_ualis_controlled_original_rows']}/{q['sentence_rows']} rows.",
            f"- Editorial decisions: {q['curation_status_counts']}; unresolved: 0.",
            f"- Pronunciation foundations: {q['pronunciation_foundations']}.",
            f"- PDFs: {len(q['pdfs'])} (1 master + 13 split PDFs).",
            f"- Corpus/release checks: {q['corpus_quality_gate']}.",
            "",
        ])
    report.extend([
        "Automated and source-locked editorial gates materially reduce release risk, but independent native-speaker certification remains a separate standard for any absolute error-free commercial claim.",
        "",
    ])
    (AUDIT / "QA_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    readme = """# Language Workbooks v1.0

Production-candidate workbooks for Arabic, French, and Urdu. Each language includes one complete master PDF, 13 split PDFs, a 1,000-entry vocabulary companion CSV, and a 1,000-sentence companion CSV.

Vocabulary comes from the repository's audited top-1,000 learner decks. Arabic and French sentence pairs originate from the ManyThings bilingual exports of the Tatoeba Project and retain supplied sentence-level attribution under CC BY 2.0 France. Urdu v1.0 uses UALIS Publishing original controlled learner sentences; those rows retain UALIS source provenance and are not represented as third-party Tatoeba quotations.

The v1.0 production sentence corpus is fixed by a versioned 1,000-row source-locked decision ledger per language. KEEP rows remain exact. Approved corrections preserve the source provenance and are explicitly marked as editorial adaptations.

Each language includes a source-backed pronunciation quick-start in Foundations using broad IPA and articulatory guidance. Sentence drills remain in normal target-language spelling rather than introducing ad-hoc romanization.

The production build checks row counts, target/English uniqueness, all-row source provenance, applicable external-license attribution, pronunciation-guide integrity, PDF structure, and exact production-to-decision alignment. Independent native-speaker certification remains separate from these automated and editorial controls; no absolute error-free claim is made.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    manifest_path = OUT / "RELEASE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["release"] = legacy.RELEASE
    manifest["status"] = "production_candidate"
    manifest["build_basis"] = "source-locked final-integrity v1.0 row-decision ledgers"
    manifest["sentence_curation"] = {
        "total_rows": 3000,
        "unresolved_rows": 0,
        "languages": {
            language: {
                "rows": 1000,
                "status_counts": legacy.DECISION_META[language]["status_counts"],
                "decision_sha256": enriched[language]["curation_decision_sha256"],
                "source_zip_sha256": legacy.DECISIONS[language]["source_zip_sha256"],
                "provenance_mode": PROFILES[language]["mode"],
                "provenance_rows": enriched[language]["sentence_provenance_rows"],
                "licensed_external_attribution_rows": enriched[language]["sentence_licensed_external_attribution_rows"],
                "ualis_controlled_original_rows": enriched[language]["sentence_ualis_controlled_original_rows"],
            }
            for language in LANGUAGES
        },
    }
    manifest["pronunciation_foundations"] = {
        "status": pronunciation_qa["status"],
        "guide_sha256": pronunciation_qa["guide_sha256"],
        "scope": pronunciation_qa["scope"],
        "references_rendered": True,
    }
    manifest["source_policy"] = (
        "All final sentence rows retain explicit source provenance. Arabic and French retain "
        "Tatoeba/CC-BY attribution; Urdu v1.0 is a UALIS Publishing controlled-original corpus. "
        "Approved editorial adaptations remain marked without changing source ownership."
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    gate = {
        "release": legacy.RELEASE,
        "gate": "FAIL" if release_problems else "PASS",
        "pdf_count": len(pdfs),
        "languages": list(LANGUAGES),
        "sentence_rows": 3000,
        "unresolved_editorial_rows": 0,
        "provenance_rows": sum(q["sentence_provenance_rows"] for q in enriched.values()),
        "licensed_external_attribution_rows": sum(q["sentence_licensed_external_attribution_rows"] for q in enriched.values()),
        "ualis_controlled_original_rows": sum(q["sentence_ualis_controlled_original_rows"] for q in enriched.values()),
        "pronunciation_gate": pronunciation_qa["status"],
        "decision_ledgers": {language: enriched[language]["curation_decision_sha256"] for language in LANGUAGES},
        "problems": release_problems,
        "note": (
            "Final production candidate rendered from fully resolved source-locked decisions with "
            "truthful per-language provenance semantics. Independent native-speaker certification remains separate."
        ),
    }
    (AUDIT / "release_gate_v3.json").write_text(
        json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if release_problems:
        raise SystemExit("curated release gate failed: " + "; ".join(release_problems))
    print(json.dumps(gate, ensure_ascii=False, indent=2))


def main() -> None:
    legacy.sources_with_pronunciation = truthful_sources_with_pronunciation
    legacy.enrich_and_gate = corrected_enrich_and_gate
    legacy.main()


if __name__ == "__main__":
    main()
