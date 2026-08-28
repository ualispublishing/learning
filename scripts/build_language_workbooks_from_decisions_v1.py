#!/usr/bin/env python3
"""Render language workbooks directly from the final v1.0 row-decision ledgers.

The decision ledgers are the production source of truth. This avoids re-running an
older selector or staging corpus that may no longer describe the audited rows.
Every rendered sentence is either the exact audited source pair (KEEP) or the
explicit approved pair recorded for that rank.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import build_language_workbooks_v1 as base
import language_workbook_pronunciation as pronunciation

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
OUT = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
RELEASE = "v1.0"
LANGUAGE_BY_CODE = {"ara": "arabic", "fra": "french", "urd": "urdu"}
LANGUAGES = ("arabic", "french", "urdu")
RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
EDITORIAL_MARKER = "Editorially adapted for learner accuracy; original source attribution retained"
ORIGINAL_SOURCES_HTML = base.sources_html


def load_decisions(language: str) -> dict:
    path = CURATION / f"{language}_sentence_row_decisions.json"
    if not path.exists():
        raise SystemExit(f"missing final decision ledger: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("release") != RELEASE or data.get("language") != language:
        raise SystemExit(f"{language}: decision ledger identity/release mismatch")
    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != 1000:
        raise SystemExit(f"{language}: final decision ledger must contain exactly 1000 rows")
    return data


DECISIONS = {language: load_decisions(language) for language in LANGUAGES}


def marked_attribution(source: str) -> str:
    source = (source or "").strip()
    if not source:
        raise SystemExit("blank source attribution in final decision ledger")
    if EDITORIAL_MARKER in source:
        return source
    return f"{source} | {EDITORIAL_MARKER}"


def rows_from_decisions(language: str) -> tuple[list[dict], dict]:
    data = DECISIONS[language]
    rows = []
    status_counts = Counter()

    for rank, decision in enumerate(data["rows"], start=1):
        if int(decision.get("rank", -1)) != rank:
            raise SystemExit(f"{language}: decision rank drift at {rank}")
        status = decision.get("status")
        if status not in RESOLVED:
            raise SystemExit(f"{language} rank {rank}: unresolved status {status!r}")
        status_counts[status] += 1

        source_target = decision.get("source_target")
        source_english = decision.get("source_english")
        source_attr = decision.get("source_attribution")
        if not all(isinstance(x, str) and x.strip() for x in (source_target, source_english, source_attr)):
            raise SystemExit(f"{language} rank {rank}: incomplete audited source identity")

        if status == "KEEP":
            target = source_target.strip()
            english = source_english.strip()
            attribution = source_attr.strip()
        else:
            target = decision.get("approved_target")
            english = decision.get("approved_english")
            if not isinstance(target, str) or not target.strip():
                raise SystemExit(f"{language} rank {rank}: {status} missing approved_target")
            if not isinstance(english, str) or not english.strip():
                raise SystemExit(f"{language} rank {rank}: {status} missing approved_english")
            if not decision.get("approval_note"):
                raise SystemExit(f"{language} rank {rank}: {status} missing approval_note")
            target = target.strip()
            english = english.strip()
            attribution = marked_attribution(source_attr)

        words = len(base.english_words(english))
        rows.append(
            {
                "rank": rank,
                "level": "A" if words <= 4 else "B" if words <= 8 else "C" if words <= 13 else "D",
                "target": target,
                "english": english,
                "attribution": attribution,
                "score": base.score_sentence(english),
                "words": words,
            }
        )

    if len({base.norm(r["target"]) for r in rows}) != 1000:
        raise SystemExit(f"{language}: final decision target uniqueness gate failed")
    if len({base.norm(r["english"]) for r in rows}) != 1000:
        raise SystemExit(f"{language}: final decision English uniqueness gate failed")

    return rows, {
        "status_counts": dict(sorted(status_counts.items())),
        "adapted_rows": status_counts["CORRECT_APPROVED"] + status_counts["REPLACE_APPROVED"],
    }


FINAL_ROWS = {}
DECISION_META = {}
for _language in LANGUAGES:
    FINAL_ROWS[_language], DECISION_META[_language] = rows_from_decisions(_language)


def decision_parse_sentences(cfg):
    language = LANGUAGE_BY_CODE.get(cfg.get("code"))
    if language is None:
        raise SystemExit(f"unsupported workbook language code: {cfg.get('code')!r}")
    data = DECISIONS[language]
    return [dict(row) for row in FINAL_ROWS[language]], 1000, data["source_zip_sha256"]


def sources_with_pronunciation():
    html = ORIGINAL_SOURCES_HTML()
    marker = "</section>"
    if not html.endswith(marker):
        raise RuntimeError("unexpected sources HTML shape; refusing unsafe source-note injection")
    note = (
        "<p><strong>Editorial curation:</strong> the sentence corpus is rendered from "
        "the versioned v1.0 row-decision ledger for this language. KEEP rows retain the "
        "audited pair exactly; approved corrections/replacements retain the original "
        "sentence attribution and are marked as editorial adaptations.</p>"
        "<p><strong>Pronunciation foundations:</strong> broad-IPA and articulatory guidance "
        "was cross-checked against Karin C. Ryding, <em>A Reference Grammar of Modern "
        "Standard Arabic</em>; Bernard Tranel, <em>The Sounds of French</em>; Saleem et al., "
        "<em>Urdu Consonantal and Vocalic Sounds</em>; and the Omniglot Urdu-script reference. "
        "These are broad learner reference targets, not a claim of one accent-free realization.</p>"
    )
    return html[:-len(marker)] + note + marker


def enrich_and_gate() -> None:
    pronunciation.write_qa()
    pronunciation_qa = pronunciation.audit_payload()
    qa_summary = json.loads((AUDIT / "qa_summary.json").read_text(encoding="utf-8"))
    release_problems = []
    enriched = {}

    for language in LANGUAGES:
        qpath = AUDIT / f"{language}_qa.json"
        q = json.loads(qpath.read_text(encoding="utf-8"))
        decisions = DECISIONS[language]
        expected_hash = decisions.get("source_zip_sha256")
        status_counts = DECISION_META[language]["status_counts"]

        checks = {
            "vocabulary_rows": q.get("vocabulary_rows") == 1000,
            "sentence_rows": q.get("sentence_rows") == 1000,
            "target_unique": q.get("sentence_target_unique") == 1000,
            "english_unique": q.get("sentence_english_unique") == 1000,
            "attribution_rows": q.get("sentence_attribution_rows") == 1000,
            "source_hash": q.get("sentence_source_zip_sha256") == expected_hash,
            "pdf_count": len(q.get("pdfs", {})) == 14,
            "pdf_nonempty_pages": all(
                item.get("pages", 0) >= 1 and item.get("bytes", 0) >= 10000
                for item in q.get("pdfs", {}).values()
            ),
            "all_decisions_resolved": sum(status_counts.values()) == 1000
            and set(status_counts).issubset(RESOLVED),
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            release_problems.append(f"{language}: {', '.join(failed)}")

        q["sentence_build_basis"] = "final v1.0 row-decision ledger"
        q["sentence_candidates_after_hard_filters"] = None
        q["sentence_candidate_metric_scope"] = (
            "Not recomputed during decision-ledger rendering; exactly 1000 resolved audited rows are eligible."
        )
        q["sentence_source_type"] = "ManyThings/Tatoeba CC BY 2.0 France; final row-audited decision corpus"
        q["sentence_question_share"] = round(q.get("sentence_question_count", 0) / 1000, 3)
        q["curation_release"] = RELEASE
        q["curation_status_counts"] = status_counts
        q["curation_adapted_rows"] = DECISION_META[language]["adapted_rows"]
        q["curation_unresolved_rows"] = 0
        q["curation_decision_sha256"] = base.sha256(
            CURATION / f"{language}_sentence_row_decisions.json"
        )
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
        "All 3,000 sentence ranks have resolved v1.0 editorial decisions. The production build is rendered directly from those ledgers rather than from an older selector or staging snapshot.",
        "",
    ]
    for language, q in enriched.items():
        report.extend(
            [
                f"## {language.title()}",
                f"- Vocabulary: {q['vocabulary_rows']} entries.",
                f"- Sentences: {q['sentence_rows']} rows; {q['sentence_target_unique']} unique target strings; {q['sentence_english_unique']} unique English strings.",
                f"- Licensed sentence attribution retained: {q['sentence_attribution_rows']}/{q['sentence_rows']} rows.",
                f"- Editorial decisions: {q['curation_status_counts']}; unresolved: 0.",
                f"- Pronunciation foundations: {q['pronunciation_foundations']}.",
                f"- PDFs: {len(q['pdfs'])} (1 master + 13 split PDFs).",
                f"- Corpus/release checks: {q['corpus_quality_gate']}.",
                "",
            ]
        )
    report.extend(
        [
            "Automated gates materially reduce release risk, but independent native-speaker certification remains a separate standard for any absolute error-free commercial claim.",
            "",
        ]
    )
    (AUDIT / "QA_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    readme = """# Language Workbooks v1.0

Production-candidate workbooks for Arabic, French, and Urdu. Each language includes one complete master PDF, 13 split PDFs, a 1,000-entry vocabulary companion CSV, and a 1,000-sentence companion CSV.

Vocabulary comes from the repository's audited top-1,000 learner decks. Sentence pairs originate from the ManyThings bilingual exports of the Tatoeba Project and retain supplied sentence-level attribution under CC BY 2.0 France. The v1.0 production sentence corpus is fixed by a versioned 1,000-row decision ledger per language: KEEP rows remain exact, while approved corrections or replacements preserve the source attribution and are marked as editorial adaptations.

Each language includes a source-backed pronunciation quick-start in Foundations using broad IPA and articulatory guidance. Sentence drills remain in normal target-language spelling rather than introducing ad-hoc romanization.

The production build is generated directly from the final row-decision ledgers and checked for row counts, target/English uniqueness, source attribution, source-hash provenance, pronunciation-guide integrity, PDF structure, and exact production-to-decision alignment. Independent native-speaker certification remains separate from these automated and editorial controls; no absolute error-free claim is made.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    manifest_path = OUT / "RELEASE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["release"] = RELEASE
    manifest["status"] = "production_candidate"
    manifest["build_basis"] = "final v1.0 row-decision ledgers"
    manifest["sentence_curation"] = {
        "total_rows": 3000,
        "unresolved_rows": 0,
        "languages": {
            language: {
                "rows": 1000,
                "status_counts": DECISION_META[language]["status_counts"],
                "decision_sha256": enriched[language]["curation_decision_sha256"],
                "source_zip_sha256": DECISIONS[language]["source_zip_sha256"],
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
        "Final sentence rows are rendered from the audited decision ledgers; source attribution "
        "is retained for all rows and approved editorial adaptations are explicitly marked."
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    gate = {
        "release": RELEASE,
        "gate": "FAIL" if release_problems else "PASS",
        "pdf_count": len(pdfs),
        "languages": list(LANGUAGES),
        "sentence_rows": 3000,
        "unresolved_editorial_rows": 0,
        "pronunciation_gate": pronunciation_qa["status"],
        "decision_ledgers": {
            language: enriched[language]["curation_decision_sha256"] for language in LANGUAGES
        },
        "problems": release_problems,
        "note": (
            "Final production candidate rendered directly from fully resolved row-decision ledgers. "
            "Independent native-speaker certification remains separate."
        ),
    }
    (AUDIT / "release_gate_v3.json").write_text(
        json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if release_problems:
        raise SystemExit("curated release gate failed: " + "; ".join(release_problems))
    print(json.dumps(gate, ensure_ascii=False, indent=2))


def main() -> None:
    base.parse_sentences = decision_parse_sentences
    base.cover = pronunciation.cover
    base.foundations_html = pronunciation.foundations_html
    base.sources_html = sources_with_pronunciation
    pronunciation.write_qa()
    base.main()
    enrich_and_gate()


if __name__ == "__main__":
    main()
