#!/usr/bin/env python3
"""Build pronunciation-aided language workbooks from fully audited sidecars.

The v1.0 release remains immutable.  This builder reads the canonical v1.0 learner
corpus plus the fail-closed v1.1 pronunciation sidecars and writes a separate
sibling release at completed/languages/workbooks/v1.1-pronunciation.

It refuses to render when ranks, target text, English text, or sentence levels drift
between the canonical corpus and the finalized pronunciation audit.
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
PRON_BASE = ROOT / "audit" / "language-workbooks" / "v1.1-pronunciation"
FINAL = PRON_BASE / "final"
FINAL_MANIFEST = PRON_BASE / "final_manifest.json"
OUT = ROOT / "completed" / "languages" / "workbooks" / "v1.1-pronunciation"
AUDIT = PRON_BASE / "release"

LANGS = {
    "arabic": {
        "name": "Arabic",
        "target": "العربية",
        "dir": "rtl",
        "font": "Noto Naskh Arabic",
        "register": "Modern Standard Arabic (MSA)",
        "key": [
            ("ʕ", "a voiced throat sound (ع)"),
            ("ħ", "a deeper breathy h (ح)"),
            ("x", "kh, as in خ"),
            ("ɣ", "gh, as in غ"),
            ("q", "a deep q/k sound (ق)"),
            ("ː", "the preceding vowel is held longer"),
        ],
    },
    "french": {
        "name": "French",
        "target": "Français",
        "dir": "ltr",
        "font": "DejaVu Sans",
        "register": "contemporary standard French",
        "key": [
            ("ʁ", "the French r"),
            ("y", "French u: say ee with rounded lips"),
            ("ø / œ", "rounded vowel sounds heard in peu / peur"),
            ("ɑ̃ / ɛ̃ / ɔ̃", "nasal vowels; do not pronounce a final n"),
            ("ɥ", "a rounded y/w glide, as in puis"),
            ("ɲ", "ny, as in signer"),
        ],
    },
    "urdu": {
        "name": "Urdu",
        "target": "اردو",
        "dir": "rtl",
        "font": "Noto Nastaliq Urdu",
        "register": "standard Urdu in Nastaliq",
        "key": [
            ("ʈ / ɖ / ɽ", "retroflex t / d / r: tongue curls slightly back"),
            ("t̪ / d̪", "dental t / d: tongue touches the back of the teeth"),
            ("ʰ", "aspiration: a clear puff of air follows the consonant"),
            ("ɦ", "breathy h"),
            ("d͡ʒ / t͡ʃ", "j / ch sounds"),
            ("˜", "nasalized vowel when shown above a vowel"),
        ],
    },
}

FOUNDATIONS = {
    "arabic": [
        ("Writing system", "Arabic is written from right to left. Most letters join within words and change shape by position."),
        ("Vowels", "Long vowels are normally written; short vowels are often omitted in ordinary text. Use the pronunciation line as a reading aid, not as a substitute for learning Arabic script."),
        ("Pronunciation goal", "Use the learner hint for a first approximation, then compare it with the IPA. Arabic sounds such as ع, ح, خ, غ, and ق do not map perfectly to English spelling."),
    ],
    "french": [
        ("Writing and sound", "French spelling does not map one-to-one to pronunciation. Final consonants may be silent, and liaison depends on grammar and register."),
        ("Connected speech", "The sentence IPA reflects connected standard French, including required liaison and the deliberate absence of false liaison after finite verbs."),
        ("Pronunciation goal", "Use the learner hint to get started, then use the IPA to distinguish rounded and nasal vowels that English spelling cannot represent precisely."),
    ],
    "urdu": [
        ("Writing system", "Urdu is written from right to left in a Perso-Arabic script, commonly in Nastaliq. Short vowels are often unmarked."),
        ("Consonant contrasts", "Dental, retroflex, and aspirated consonants can distinguish words. The IPA line keeps these contrasts visible even when an English-style hint cannot."),
        ("Pronunciation goal", "Use the learner hint as scaffolding while learning the Urdu script. Homographs are pronounced according to the meaning used on that row."),
    ],
}


def fail(message: str) -> None:
    raise SystemExit(message)


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        fail(f"missing required file: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_ranks(rows: list[dict], label: str) -> None:
    try:
        ranks = [int(row["rank"]) for row in rows]
    except Exception as exc:
        fail(f"{label}: invalid rank column: {exc}")
    if len(rows) != 1000 or ranks != list(range(1, 1001)):
        fail(f"{label}: expected exactly ranks 1..1000, got {len(rows)} rows")


def merge_vocab(lang: str) -> list[dict]:
    canon_path = V1 / lang / f"{lang}_vocabulary_1000.csv"
    pron_path = FINAL / f"{lang}_vocab_pronunciation.csv"
    canon = read_csv(canon_path)
    pron = read_csv(pron_path)
    require_ranks(canon, f"{lang} canonical vocab")
    require_ranks(pron, f"{lang} pronunciation vocab")
    merged = []
    for c, p in zip(canon, pron):
        rank = int(c["rank"])
        if int(p["rank"]) != rank or c["target"] != p["target"] or c["english"] != p["english"]:
            fail(f"DRIFT {lang}/vocab rank {rank}")
        canon_pos = c.get("part_of_speech", "")
        pron_pos = p.get("pos", "")
        if canon_pos != pron_pos:
            fail(f"DRIFT {lang}/vocab rank {rank}: part of speech")
        if not p.get("ipa", "").strip() or not p.get("learner_hint", "").strip():
            fail(f"{lang}/vocab rank {rank}: blank pronunciation")
        merged.append({
            "rank": rank,
            "target": c["target"],
            "english": c["english"],
            "pos": canon_pos,
            "ipa": p["ipa"].strip(),
            "learner_hint": p["learner_hint"].strip(),
            "audit_status": p.get("audit_status", "").strip(),
        })
    return merged


def merge_sentences(lang: str) -> list[dict]:
    canon_path = V1 / lang / f"{lang}_sentence_bank_1000.csv"
    pron_path = FINAL / f"{lang}_sentences_pronunciation.csv"
    canon = read_csv(canon_path)
    pron = read_csv(pron_path)
    require_ranks(canon, f"{lang} canonical sentences")
    require_ranks(pron, f"{lang} pronunciation sentences")
    merged = []
    for c, p in zip(canon, pron):
        rank = int(c["rank"])
        if int(p["rank"]) != rank or c["target"] != p["target"] or c["english"] != p["english"]:
            fail(f"DRIFT {lang}/sentences rank {rank}")
        if c.get("level", "") != p.get("level", ""):
            fail(f"DRIFT {lang}/sentences rank {rank}: level")
        if not p.get("ipa", "").strip() or not p.get("learner_hint", "").strip():
            fail(f"{lang}/sentences rank {rank}: blank pronunciation")
        merged.append({
            "rank": rank,
            "level": c.get("level", ""),
            "target": c["target"],
            "english": c["english"],
            "attribution": c.get("attribution", ""),
            "ipa": p["ipa"].strip(),
            "learner_hint": p["learner_hint"].strip(),
            "audit_status": p.get("audit_status", "").strip(),
        })
    return merged


CSS = r'''
@page { size: Letter; margin: .50in .56in .58in; @bottom-center { content: counter(page); font: 8pt "DejaVu Sans"; color:#66737d; } }
@page :first { @bottom-center { content:none; } }
* { box-sizing:border-box; }
body { font-family:"DejaVu Sans", sans-serif; color:#18212b; font-size:9.55pt; line-height:1.32; }
h1,h2,h3 { break-after:avoid; color:#17324d; }
h1 { font-size:27pt; margin:0 0 .16in; }
h2 { font-size:17pt; border-bottom:1.4pt solid #b8c9d8; padding-bottom:4pt; margin:.16in 0 .10in; }
h3 { font-size:11.8pt; margin:.10in 0 .04in; }
.cover { break-after:page; padding-top:.92in; }
.kicker { text-transform:uppercase; letter-spacing:1.1pt; font-size:8.3pt; color:#5b7185; font-weight:700; }
.subtitle { font-size:12.5pt; color:#475c6e; max-width:6.4in; }
.claim { margin-top:.22in; padding:.15in .18in; background:#f2f6f9; border-left:4pt solid #7da1bd; }
.toc { break-after:page; }
.toc a { color:#17324d; text-decoration:none; }
.toc a::after { content:leader('.') target-counter(attr(href), page); }
.section-start { break-before:page; }
.target { font-family:var(--target-font); font-size:15.4pt; font-weight:600; line-height:1.48; overflow-wrap:anywhere; }
.rtl { direction:rtl; text-align:right; unicode-bidi:plaintext; }
.entry { break-inside:avoid; border:1px solid #d9e2ea; border-radius:5px; padding:6pt 8pt; margin:0 0 6pt; }
.entry .num { float:right; font-size:7.5pt; color:#6d7d89; font-family:"DejaVu Sans"; }
.rtl.entry .num { float:left; }
.meaning { margin-top:1.5pt; color:#34495a; direction:ltr; text-align:left; }
.pos { font-size:7.2pt; color:#6d7d89; direction:ltr; text-align:left; }
.pron { margin-top:3pt; padding:3pt 5pt; background:#f7f9fb; border-left:2pt solid #b8c9d8; direction:ltr; text-align:left; font-family:"DejaVu Sans", sans-serif; }
.ipa { font-size:8.2pt; }
.hint { font-size:8.2pt; margin-top:1pt; }
.plabel { font-size:6.8pt; font-weight:700; text-transform:uppercase; letter-spacing:.35pt; color:#637789; margin-right:5pt; }
.attrib { margin-top:2pt; font-size:6pt; color:#75828c; font-family:"DejaVu Sans"; direction:ltr; text-align:left; overflow-wrap:anywhere; }
.write { border-bottom:.7pt solid #bfcad2; height:15pt; margin-top:3pt; }
.vocab-grid { column-count:2; column-gap:9pt; }
.vocab-grid .entry { display:inline-block; width:100%; }
.note { font-size:8.2pt; color:#5c6d79; }
.license { font-size:8.3pt; }
.foundation-card { break-inside:avoid; padding:8pt 10pt; margin:0 0 7pt; background:#f6f8fa; border-left:3pt solid #7b9bb5; }
.keytable { width:100%; border-collapse:collapse; margin:.06in 0 .14in; }
.keytable td { border-bottom:1px solid #e0e6eb; padding:4pt 5pt; vertical-align:top; }
.keytable td:first-child { width:1.35in; font-family:"DejaVu Sans"; font-weight:600; }
'''


def cover(cfg: dict, segment: str) -> str:
    rtl = "rtl" if cfg["dir"] == "rtl" else ""
    return f'''<section class="cover"><div class="kicker">Version 1.1 · pronunciation-aided production candidate</div><h1>{esc(cfg['name'])} Workbook</h1><div class="target {rtl}" style="--target-font:'{cfg['font']}'">{esc(cfg['target'])}</div><p class="subtitle">The complete v1.0 learner corpus plus row-audited IPA and learner-friendly phonetic spelling for every vocabulary item and every practice sentence.</p><div class="claim"><strong>{esc(segment)}</strong><br>The IPA and learner hint are pronunciation aids, not replacement spellings. Read the target script first when possible; use the hint for orientation and the IPA for sound distinctions that English spelling cannot represent reliably.</div></section>'''


def foundations_html(lang: str, cfg: dict) -> str:
    cards = "".join(f'<div class="foundation-card"><h3>{esc(title)}</h3><p>{esc(text)}</p></div>' for title, text in FOUNDATIONS[lang])
    key = "".join(f'<tr><td>{esc(symbol)}</td><td>{esc(explain)}</td></tr>' for symbol, explain in cfg["key"])
    return f'''<section id="foundations"><h2>Pronunciation key & study aids</h2><p class="note">Target register: {esc(cfg['register'])}. Each learner row has two aids: <strong>IPA</strong>, the precise phonetic notation used by this release, and <strong>Say it</strong>, an approximate English-readable cue. Parenthetical notes such as “nasal” identify sounds that should not be read literally as English letters.</p><table class="keytable"><tr><td>/slashes/</td><td>IPA pronunciation; symbols describe sounds, not spelling.</td></tr><tr><td>Say it</td><td>Approximate learner cue. It is intentionally secondary to the IPA.</td></tr>{key}</table>{cards}<div class="foundation-card"><h3>Three-pass pronunciation routine</h3><p>1) Try the target text aloud. 2) Check the learner cue. 3) Check the IPA and repeat the target text without looking at the cue. When audio is added in a later product layer, use it as the final listening-and-shadowing check.</p></div></section>'''


def pron_html(row: dict) -> str:
    return f'''<div class="pron"><div class="ipa"><span class="plabel">IPA</span>{esc(row['ipa'])}</div><div class="hint"><span class="plabel">Say it</span>{esc(row['learner_hint'])}</div></div>'''


def vocab_html(rows: list[dict], cfg: dict, start: int, end: int) -> str:
    rtl = "rtl" if cfg["dir"] == "rtl" else ""
    entries = []
    for row in rows[start - 1:end]:
        entries.append(f'''<div class="entry {rtl}"><span class="num">{row['rank']}</span><div class="target" style="--target-font:'{cfg['font']}'">{esc(row['target'])}</div><div class="meaning">{esc(row['english'])}</div><div class="pos">{esc(row['pos'])}</div>{pron_html(row)}<div class="write"></div></div>''')
    return f'''<section id="vocab-{start}" class="section-start"><h2>Vocabulary {start}-{end}</h2><p class="note">Pronounce the target before revealing the aids. Then retrieve the meaning and write the target item from memory.</p><div class="vocab-grid">{''.join(entries)}</div></section>'''


def sentences_html(rows: list[dict], cfg: dict, start: int, end: int) -> str:
    rtl = "rtl" if cfg["dir"] == "rtl" else ""
    entries = []
    for row in rows[start - 1:end]:
        entries.append(f'''<div class="entry {rtl}"><span class="num">{row['rank']} · {esc(row['level'])}</span><div class="target" style="--target-font:'{cfg['font']}'">{esc(row['target'])}</div><div class="meaning">{esc(row['english'])}</div>{pron_html(row)}<div class="attrib">{esc(row['attribution'])}</div><div class="write"></div><div class="write"></div></div>''')
    return f'''<section id="sent-{start}" class="section-start"><h2>Practice sentences {start}-{end}</h2><p class="note">Read the full sentence aloud first. The sentence IPA reflects the audited phrase-level pronunciation, including connected-speech decisions where relevant.</p>{''.join(entries)}</section>'''


def sources_html(lang: str) -> str:
    sentence_note = "French and Arabic sentence rows retain their canonical v1.0 source attribution. Urdu sentence rows retain the original controlled-learner attribution recorded in v1.0."
    return f'''<section class="section-start license"><h2>Sources, pronunciation audit, and QA scope</h2><p><strong>Corpus:</strong> exactly the canonical v1.0 vocabulary and sentence rows; the builder fails on text or rank drift.</p><p><strong>Pronunciation:</strong> every one of the 2,000 {esc(lang.title())} learner rows was individually adjudicated in the v1.1 pronunciation ledgers before this PDF build. Homographs are pronounced according to the meaning on their row.</p><p><strong>Attribution:</strong> {esc(sentence_note)}</p><p><strong>Quality scope:</strong> automated release gates verify 1,000 vocabulary rows, 1,000 sentence rows, finalized IPA/hints, canonical alignment, PDF structure, and renderability. The release remains a production candidate rather than an absolute independent native-speaker certification claim.</p></section>'''


def document(body: str) -> str:
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'


def render_pdf(path: Path, body: str) -> dict:
    HTML(string=document(body), base_url=str(ROOT)).write_pdf(path)
    if path.stat().st_size < 10000:
        fail(f"PDF too small: {path}")
    reader = PdfReader(str(path))
    if not reader.pages:
        fail(f"PDF has no pages: {path}")
    replacement_pages = []
    near_empty_pages = []
    for index, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        if "\ufffd" in text:
            replacement_pages.append(index)
        if len(text.strip()) < 8:
            near_empty_pages.append(index)
    if replacement_pages:
        fail(f"replacement character detected in {path.name}: pages {replacement_pages[:8]}")
    return {
        "pages": len(reader.pages),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "near_empty_text_pages": near_empty_pages,
    }


def write_enriched_csv(path: Path, rows: list[dict], kind: str) -> None:
    if kind == "vocab":
        fields = ["rank", "target", "english", "part_of_speech", "ipa", "learner_hint", "audit_status"]
    else:
        fields = ["rank", "level", "target", "english", "ipa", "learner_hint", "attribution", "audit_status"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            if kind == "vocab":
                writer.writerow({
                    "rank": row["rank"], "target": row["target"], "english": row["english"],
                    "part_of_speech": row["pos"], "ipa": row["ipa"],
                    "learner_hint": row["learner_hint"], "audit_status": row["audit_status"],
                })
            else:
                writer.writerow({k: row.get(k, "") for k in fields})


def build_language(lang: str, cfg: dict) -> dict:
    target_dir = OUT / lang
    target_dir.mkdir(parents=True, exist_ok=True)
    vocab = merge_vocab(lang)
    sentences = merge_sentences(lang)
    if any(row["audit_status"] not in {"PASS", "REPAIR"} for row in vocab + sentences):
        fail(f"{lang}: unresolved audit status reached builder")

    write_enriched_csv(target_dir / f"{lang}_vocabulary_1000_with_pronunciation.csv", vocab, "vocab")
    write_enriched_csv(target_dir / f"{lang}_sentence_bank_1000_with_pronunciation.csv", sentences, "sentences")

    pieces: list[tuple[str, str]] = [("01_foundations_pronunciation_key", cover(cfg, "Foundations & pronunciation key") + foundations_html(lang, cfg) + sources_html(lang))]
    n = 2
    for a, b in ((1, 250), (251, 500), (501, 750), (751, 1000)):
        pieces.append((f"{n:02d}_vocabulary_{a:03d}-{b:04d}", cover(cfg, f"Vocabulary {a}-{b}") + vocab_html(vocab, cfg, a, b) + sources_html(lang)))
        n += 1
    for a in range(1, 1001, 125):
        b = min(1000, a + 124)
        pieces.append((f"{n:02d}_sentences_{a:03d}-{b:04d}", cover(cfg, f"Sentences {a}-{b}") + sentences_html(sentences, cfg, a, b) + sources_html(lang)))
        n += 1

    pdf_stats = {}
    for stem, body in pieces:
        path = target_dir / f"{stem}.pdf"
        pdf_stats[path.name] = render_pdf(path, body)

    toc = ['<section class="toc"><h2>Contents</h2><p><a href="#foundations">Pronunciation key & foundations</a></p>']
    for a, b in ((1, 250), (251, 500), (501, 750), (751, 1000)):
        toc.append(f'<p><a href="#vocab-{a}">Vocabulary {a}-{b}</a></p>')
    for a in range(1, 1001, 125):
        toc.append(f'<p><a href="#sent-{a}">Sentences {a}-{min(1000, a + 124)}</a></p>')
    toc.append('</section>')
    body = cover(cfg, "Complete master") + "".join(toc) + foundations_html(lang, cfg)
    for a, b in ((1, 250), (251, 500), (501, 750), (751, 1000)):
        body += vocab_html(vocab, cfg, a, b)
    for a in range(1, 1001, 125):
        body += sentences_html(sentences, cfg, a, min(1000, a + 124))
    body += sources_html(lang)
    master = target_dir / f"00_{lang}_complete_master_pronunciation.pdf"
    pdf_stats[master.name] = render_pdf(master, body)

    if len(pdf_stats) != 14:
        fail(f"{lang}: expected 14 PDFs, got {len(pdf_stats)}")

    qa = {
        "language": lang,
        "status": "PASS",
        "vocabulary_rows": len(vocab),
        "sentence_rows": len(sentences),
        "pronunciation_rows": len(vocab) + len(sentences),
        "audit_status_counts": dict(Counter(row["audit_status"] for row in vocab + sentences)),
        "blank_ipa": sum(not row["ipa"].strip() for row in vocab + sentences),
        "blank_learner_hints": sum(not row["learner_hint"].strip() for row in vocab + sentences),
        "canonical_vocab_sha256": sha256(V1 / lang / f"{lang}_vocabulary_1000.csv"),
        "canonical_sentence_sha256": sha256(V1 / lang / f"{lang}_sentence_bank_1000.csv"),
        "final_vocab_pronunciation_sha256": sha256(FINAL / f"{lang}_vocab_pronunciation.csv"),
        "final_sentence_pronunciation_sha256": sha256(FINAL / f"{lang}_sentences_pronunciation.csv"),
        "pdfs": pdf_stats,
    }
    if qa["blank_ipa"] or qa["blank_learner_hints"]:
        fail(f"{lang}: blank pronunciation survived release build")
    (AUDIT / f"{lang}_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


def main() -> None:
    if not FINAL_MANIFEST.exists():
        fail("missing final pronunciation manifest; run finalize_language_workbook_pronunciation.py first")
    final_manifest = json.loads(FINAL_MANIFEST.read_text(encoding="utf-8"))
    datasets = final_manifest.get("datasets", {})
    if set(datasets) != {f"{lang}_{kind}" for lang in LANGS for kind in ("vocab", "sentences")}:
        fail("final pronunciation manifest does not contain exactly six datasets")
    if any(int(info.get("rows", 0)) != 1000 for info in datasets.values()):
        fail("final pronunciation manifest row-count gate failed")

    if OUT.exists():
        shutil.rmtree(OUT)
    if AUDIT.exists():
        shutil.rmtree(AUDIT)
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)

    qa = {lang: build_language(lang, cfg) for lang, cfg in LANGS.items()}
    pdf_count = sum(len(info["pdfs"]) for info in qa.values())
    pronunciation_rows = sum(info["pronunciation_rows"] for info in qa.values())
    if pdf_count != 42 or pronunciation_rows != 6000:
        fail(f"release cross-gate failed: pdf_count={pdf_count}, pronunciation_rows={pronunciation_rows}")

    manifest = {
        "release": "v1.1-pronunciation",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "production_candidate",
        "source_release": "v1.0",
        "source_release_preserved": True,
        "pronunciation_rows": pronunciation_rows,
        "unresolved_pronunciation_rows": 0,
        "pdf_count": pdf_count,
        "languages": list(LANGS),
        "final_pronunciation_manifest_sha256": sha256(FINAL_MANIFEST),
        "language_qa": {lang: f"audit/language-workbooks/v1.1-pronunciation/release/{lang}_qa.json" for lang in LANGS},
        "note": "All learner rows contain audited IPA and learner-friendly pronunciation cues. Audio is not part of this release. Independent native-speaker editorial certification remains a separate assurance layer.",
    }
    (OUT / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (AUDIT / "release_gate.json").write_text(json.dumps({
        "gate": "PASS", "pronunciation_rows": pronunciation_rows, "unresolved": 0,
        "pdf_count": pdf_count, "languages": list(LANGS),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Language Workbooks v1.1 — Pronunciation Aids\n\n"
        "This folder is a separate sibling of `v1.0`; the original release is unchanged.\n\n"
        "Each language contains one complete master PDF, 13 tablet-friendly split PDFs, and pronunciation-enriched vocabulary/sentence CSVs. Every one of the 6,000 learner rows was adjudicated before finalization. Each row shows target text, English meaning, IPA, and an approximate learner-friendly `Say it` cue.\n\n"
        "The learner cue is deliberately secondary to IPA and target-script learning. Audio is planned as a later fidelity layer and is not claimed in v1.1. This remains a production candidate; independent native-speaker editorial certification is a separate assurance layer.\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
