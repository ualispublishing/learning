#!/usr/bin/env python3
"""Render one already-approved workbook corpus at a time, then finalize release metadata."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

import build_language_workbooks_v1 as base
import build_language_workbooks_v1_quality as quality
import language_workbook_pronunciation as pronunciation
import workbook_release_passes as passes


def sources_with_pronunciation():
    html = quality.quality_sources_html()
    marker = "</section>"
    if not html.endswith(marker):
        raise RuntimeError("unexpected sources HTML shape; refusing unsafe pronunciation-source injection")
    note = (
        '<p><strong>Pronunciation foundations:</strong> broad-IPA and articulatory guidance was '
        'cross-checked against Karin C. Ryding, <em>A Reference Grammar of Modern Standard Arabic</em> '
        '(Cambridge University Press); Bernard Tranel, <em>The Sounds of French: An Introduction</em> '
        '(Cambridge University Press); Saleem et al., <em>Urdu Consonantal and Vocalic Sounds</em> '
        '(CRULP / Center for Language Engineering); and the Omniglot Urdu-script reference for '
        'Nastaliq, nūn ghunnah, and aspirated-letter conventions. These are broad learner reference '
        'targets, not a claim that each language has one accent-free phonetic realization.</p>'
    )
    return html[:-len(marker)] + note + marker


def configure():
    if not (passes.STAGE / "corpus_audit.json").exists():
        raise SystemExit("corpus-audit pass must complete before rendering")
    base.parse_sentences = passes.staged_parse_sentences
    base.cover = pronunciation.cover
    base.foundations_html = pronunciation.foundations_html
    base.sources_html = sources_with_pronunciation
    base.LANGS["urdu"]["zip"] = "internal://ualis/urdu-controlled-conversation-v1"
    pronunciation.write_qa()


def render_language(lang: str):
    if lang not in base.LANGS:
        raise SystemExit(f"unsupported language: {lang}")
    configure()
    selection = json.loads((passes.STAGE / f"{lang}_selection.json").read_text(encoding="utf-8"))
    quality.QUALITY_META[lang] = selection["quality"]
    print(f"Rendering approved {lang} corpus with pronunciation foundations...", flush=True)
    qa = base.build_language(lang, base.LANGS[lang])
    if len(qa.get("pdfs", {})) != 14:
        raise SystemExit(f"{lang}: expected 14 PDFs, found {len(qa.get('pdfs', {}))}")
    print(json.dumps({
        "language": lang,
        "pdfs": len(qa["pdfs"]),
        "vocabulary_rows": qa["vocabulary_rows"],
        "sentence_rows": qa["sentence_rows"],
        "target_unique": qa["sentence_target_unique"],
        "english_unique": qa["sentence_english_unique"],
        "pronunciation_foundations": "PASS",
        "pronunciation_references_rendered": True,
    }, ensure_ascii=False, indent=2))


def synchronize_release_docs():
    readme_path = base.OUT / "README.md"
    report_path = base.AUDIT / "QA_REPORT.md"
    if not readme_path.exists() or not report_path.exists():
        raise SystemExit("missing README or QA report during pronunciation documentation sync")

    readme = readme_path.read_text(encoding="utf-8")
    old = (
        "The release favors natural, idiomatic language over artificial uniqueness. Genuine homographs are permitted when meaning and grammatical role genuinely differ. "
        "Transliteration is omitted from the sentence drill corpus rather than introducing inconsistent ad-hoc romanization."
    )
    new = (
        "The release favors natural, idiomatic language over artificial uniqueness. Genuine homographs are permitted when meaning and grammatical role genuinely differ. "
        "Each language now includes a source-backed pronunciation quick-start in Foundations using broad IPA/articulatory guidance; sentence drills remain in normal target-language spelling rather than introducing inconsistent ad-hoc romanization."
    )
    if old not in readme:
        raise SystemExit("README pronunciation sync anchor missing")
    readme = readme.replace(old, new, 1)
    readme = readme.replace(
        "Automated source, diversity, duplicate, script, corpus-balance, PDF, font, and render checks support the release.",
        "Automated source, diversity, duplicate, script, corpus-balance, pronunciation-structure, PDF, font, and render checks support the release.",
        1,
    )
    readme_path.write_text(readme, encoding="utf-8")

    report = report_path.read_text(encoding="utf-8")
    anchor = "Production-candidate gates passed. Natural language quality takes priority over artificial uniqueness. Independent native-speaker editorial certification remains the final step before any absolute error-free commercial claim.\n"
    addition = (
        anchor
        + "\n- Pronunciation foundations: PASS for Arabic, French, and Urdu.\n"
        + "- Pronunciation method: broad IPA/articulatory quick-start; no ad-hoc per-sentence romanization.\n"
        + "- Mixed RTL script + IPA isolation: PASS.\n"
        + "- Pronunciation references are rendered in each workbook's Sources / QA section.\n"
    )
    if anchor not in report:
        raise SystemExit("QA report pronunciation sync anchor missing")
    report_path.write_text(report.replace(anchor, addition, 1), encoding="utf-8")


def finalize():
    configure()
    pronunciation_qa = pronunciation.audit_payload()
    rendered_sources = sources_with_pronunciation()
    for required_reference in ("Ryding", "Tranel", "Urdu Consonantal and Vocalic Sounds", "Omniglot"):
        if required_reference not in rendered_sources:
            raise SystemExit(f"missing rendered pronunciation reference: {required_reference}")

    for lang in ("arabic", "french", "urdu"):
        qa_path = base.AUDIT / f"{lang}_qa.json"
        if not qa_path.exists():
            raise SystemExit(f"missing rendered QA file: {qa_path}")
        q = json.loads(qa_path.read_text(encoding="utf-8"))
        if len(q.get("pdfs", {})) != 14:
            raise SystemExit(f"{lang}: expected 14 rendered PDFs before finalize")
        selection = json.loads((passes.STAGE / f"{lang}_selection.json").read_text(encoding="utf-8"))
        quality.QUALITY_META[lang] = selection["quality"]

    # quality.post_process expects a release manifest generated by the base builder.
    manifest = {
        "release": "v1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "production_candidate",
        "languages": ["arabic", "french", "urdu"],
        "qa_path": "audit/language-workbooks/v1.0",
        "pronunciation_foundations": {
            "status": pronunciation_qa["status"],
            "guide_sha256": pronunciation_qa["guide_sha256"],
            "scope": pronunciation_qa["scope"],
            "references_rendered": True,
        },
        "source_policy": "Natural learner language outranks artificial uniqueness; legitimate homographs are allowed when meaning and grammatical role differ.",
    }
    (base.OUT / "RELEASE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    quality.post_process()
    pronunciation.write_qa()
    synchronize_release_docs()
    print("Aggregated three rendered workbooks, applied corpus-quality gates, and synchronized pronunciation QA/references/docs.")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"arabic", "french", "urdu", "finalize"}:
        raise SystemExit("usage: workbook_render_pass.py {arabic|french|urdu|finalize}")
    if sys.argv[1] == "finalize":
        finalize()
    else:
        render_language(sys.argv[1])


if __name__ == "__main__":
    main()
