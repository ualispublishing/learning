#!/usr/bin/env python3
"""Cross-check learner Top-1000 decks against independent lexical resources.

This verifier is deliberately conservative. External sources never rewrite learner
cards. They provide independent form, POS, corpus, and semantic-support signals;
rows with weak or conflicting support are emitted to an explicit review queue.

Reproducible sources used by the workflow:
- Kaikki/Wiktextract English-Wiktionary language extracts (form/POS/English glosses)
- wordfreq (multi-corpus attestation only; never treated as a semantic authority)
- Arabic WordNet 4.0 (Arabic lexical coverage)
- existing CALIMA-MSA audit evidence (Arabic morphology coverage)
- Lexique 4 (French lexical/form coverage)
- Universal Dependencies Urdu UDTB (Urdu annotated form/lemma/POS coverage)
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from wordfreq import zipf_frequency
except Exception:  # pragma: no cover
    zipf_frequency = None

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
AUDIT.mkdir(exist_ok=True)

LANGS = {
    "arabic": {"code": "ar"},
    "french": {"code": "fr"},
    "urdu": {"code": "ur"},
}

STOP = {
    "a", "an", "the", "to", "of", "in", "on", "at", "for", "from", "by", "with", "and", "or", "as",
    "is", "are", "was", "were", "be", "been", "being", "used", "use", "word", "term", "one", "that", "this",
    "which", "who", "whom", "something", "someone", "often", "usually", "especially", "indicating", "expressing",
    "referring", "form", "forms", "particle", "pronoun", "noun", "verb", "adjective", "adverb", "preposition",
    "conjunction", "marker", "masculine", "feminine", "singular", "plural", "present", "past", "future", "case",
    "person", "thing", "things", "meaning", "means", "used", "having", "relating"
}
TOKEN_RE = re.compile(r"[a-z][a-z'-]*", re.I)
AR_DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def norm_unicode(s: str, language: str | None = None) -> str:
    s = unicodedata.normalize("NFKC", s or "").replace("ـ", "").strip()
    if language == "arabic":
        s = AR_DIAC.sub("", s)
    return s


def english_evidence(back: str) -> str:
    """Extract the learner-facing English semantic claim from old/new card formats."""
    m = re.search(r"(?m)^Meaning:\s*(.+?)\s*$", back or "")
    if m:
        return m.group(1).strip()
    parts: list[str] = []
    m = re.search(r"(?m)^EN:\s*(.+?)\s*$", back or "")
    if m:
        parts.append(m.group(1).strip())
    m = re.search(r"(?s)Definition:\s*\n\(EN\)\s*(.+?)(?:\n\n|$)", back or "")
    if m:
        parts.append(m.group(1).strip())
    return "; ".join(parts)


def token_set(text: str) -> set[str]:
    out: set[str] = set()
    for token in TOKEN_RE.findall((text or "").lower()):
        token = token.strip("'-")
        if not token or token in STOP or len(token) < 2:
            continue
        # Tiny overlap normalizer, not a linguistic stemmer.
        for suffix in ("ingly", "ation", "ments", "ment", "ing", "ied", "ed", "es", "s"):
            if len(token) > len(suffix) + 3 and token.endswith(suffix):
                token = token[:-len(suffix)]
                break
        if token and token not in STOP:
            out.add(token)
    return out


def load_kaikki(path: Path, targets: set[str], language: str) -> dict[str, dict]:
    """Stream a Kaikki JSONL extract and retain only target words and compact evidence."""
    evidence: dict[str, dict] = {t: {"exists": False, "poses": set(), "gloss_tokens": set()} for t in targets}
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            word = norm_unicode(str(obj.get("word", "")), language)
            if word not in targets:
                continue
            rec = evidence[word]
            rec["exists"] = True
            pos = obj.get("pos")
            if pos:
                rec["poses"].add(str(pos).lower())
            for sense in obj.get("senses") or []:
                for gloss in sense.get("glosses") or []:
                    rec["gloss_tokens"] |= token_set(str(gloss))
    return evidence


def load_arabic_wordnet(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    opener = gzip.open if path.suffix == ".gz" else open
    lemmas: set[str] = set()
    with opener(path, "rb") as f:
        for _, elem in ET.iterparse(f, events=("end",)):
            if elem.tag.rsplit("}", 1)[-1] == "Lemma":
                wf = elem.attrib.get("writtenForm") or elem.attrib.get("lemma")
                if wf:
                    lemmas.add(norm_unicode(wf, "arabic"))
            elem.clear()
    return lemmas


def load_camel_support() -> set[str]:
    path = AUDIT / "arabic_top1000_learner_safety_audit.csv"
    if not path.exists():
        return set()
    out: set[str] = set()
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                if int(row.get("camel_analysis_count", "0") or 0) > 0:
                    out.add(norm_unicode(row.get("front", ""), "arabic"))
            except ValueError:
                pass
    return out


def find_column(headers: list[str], candidates: tuple[str, ...]) -> str | None:
    folded = {h.casefold().strip(): h for h in headers if h}
    for candidate in candidates:
        if candidate.casefold() in folded:
            return folded[candidate.casefold()]
    return None


def load_lexique4(path: Path | None, targets: set[str]) -> tuple[set[str], dict[str, set[str]], str | None]:
    if not path or not path.exists():
        return set(), {}, None
    forms: set[str] = set()
    poses: dict[str, set[str]] = {}
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        headers = reader.fieldnames or []
        form_col = find_column(headers, ("ortho", "orthography", "word", "forme", "form", "graphie"))
        pos_col = find_column(headers, ("cgram", "grammatical_category", "pos", "categorie", "catgram"))
        if not form_col:
            return set(), {}, "No recognized surface-form column in Lexique4: " + ",".join(headers[:30])
        for row in reader:
            form = norm_unicode(row.get(form_col, ""), "french")
            if form not in targets:
                continue
            forms.add(form)
            if pos_col and row.get(pos_col):
                poses.setdefault(form, set()).add(str(row[pos_col]).strip().lower())
    return forms, poses, None


def load_urdu_ud(path: Path | None, targets: set[str]) -> tuple[set[str], dict[str, set[str]]]:
    if not path or not path.exists():
        return set(), {}
    forms: set[str] = set()
    poses: dict[str, set[str]] = {}
    for conllu in sorted(path.rglob("*.conllu")):
        with conllu.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line or line.startswith("#") or line.startswith("\n"):
                    continue
                cols = line.rstrip("\n").split("\t")
                if len(cols) < 4 or "-" in cols[0] or "." in cols[0]:
                    continue
                form = norm_unicode(cols[1], "urdu")
                lemma = norm_unicode(cols[2], "urdu")
                upos = cols[3].strip().lower()
                for candidate in (form, lemma):
                    if candidate in targets:
                        forms.add(candidate)
                        if upos:
                            poses.setdefault(candidate, set()).add(upos)
    return forms, poses


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=sorted(LANGS), required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--kaikki-jsonl", required=True)
    ap.add_argument("--arabic-wordnet")
    ap.add_argument("--lexique-tsv")
    ap.add_argument("--urdu-ud-dir")
    args = ap.parse_args()

    language = args.language
    code = LANGS[language]["code"]
    input_path = ROOT / args.input
    with input_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        if headers != ["Front", "Back"]:
            raise SystemExit(f"{args.input}: expected Front,Back header; got {headers!r}")
        rows = list(reader)

    normalized_fronts = [norm_unicode(r.get("Front", ""), language) for r in rows]
    targets = {f for f in normalized_fronts if f}
    kaikki = load_kaikki(Path(args.kaikki_jsonl), targets, language)
    awn = load_arabic_wordnet(Path(args.arabic_wordnet)) if language == "arabic" and args.arabic_wordnet else set()
    camel = load_camel_support() if language == "arabic" else set()
    lexique_forms, lexique_pos, lexique_problem = load_lexique4(Path(args.lexique_tsv), targets) if language == "french" and args.lexique_tsv else (set(), {}, None)
    urdu_ud_forms, urdu_ud_pos = load_urdu_ud(Path(args.urdu_ud_dir), targets) if language == "urdu" and args.urdu_ud_dir else (set(), {})

    results: list[dict] = []
    for rank, row in enumerate(rows, 1):
        front = normalized_fronts[rank - 1]
        expected = english_evidence(row.get("Back", ""))
        rec = kaikki.get(front, {"exists": False, "poses": set(), "gloss_tokens": set()})
        expected_tokens = token_set(expected)
        gloss_tokens: set[str] = rec["gloss_tokens"]
        overlap = sorted(expected_tokens & gloss_tokens)
        semantic = bool(overlap)

        freq_present = False
        zipf = 0.0
        if zipf_frequency is not None and front:
            try:
                zipf = float(zipf_frequency(front, code))
                freq_present = zipf > 0.0
            except Exception:
                pass

        awn_present = front in awn if awn else False
        camel_present = front in camel if camel else False
        lexique_present = front in lexique_forms if lexique_forms else False
        ud_present = front in urdu_ud_forms if urdu_ud_forms else False

        form_signals = [bool(rec["exists"]), freq_present]
        if language == "arabic":
            form_signals.extend([awn_present, camel_present])
        elif language == "french":
            form_signals.append(lexique_present)
        elif language == "urdu":
            form_signals.append(ud_present)
        support_count = sum(form_signals)

        if semantic and support_count >= 2:
            confidence = "strong"
        elif semantic:
            confidence = "moderate"
        elif rec["exists"] and gloss_tokens:
            confidence = "semantic_review"
        elif support_count >= 2:
            confidence = "form_only"
        else:
            confidence = "weak"

        results.append({
            "rank": rank,
            "front": front,
            "expected_english": expected,
            "kaikki_entry": bool(rec["exists"]),
            "kaikki_pos": "|".join(sorted(rec["poses"])),
            "kaikki_has_english_gloss": bool(gloss_tokens),
            "semantic_overlap": semantic,
            "semantic_overlap_terms": "|".join(overlap[:12]),
            "wordfreq_attested": freq_present,
            "wordfreq_zipf": f"{zipf:.2f}",
            "arabic_wordnet_entry": awn_present,
            "camel_analysis": camel_present,
            "lexique4_entry": lexique_present,
            "lexique4_pos": "|".join(sorted(lexique_pos.get(front, set()))),
            "urdu_ud_entry": ud_present,
            "urdu_ud_pos": "|".join(sorted(urdu_ud_pos.get(front, set()))),
            "support_count": support_count,
            "confidence": confidence,
        })

    fields = list(results[0]) if results else [
        "rank", "front", "expected_english", "kaikki_entry", "kaikki_pos", "kaikki_has_english_gloss",
        "semantic_overlap", "semantic_overlap_terms", "wordfreq_attested", "wordfreq_zipf", "arabic_wordnet_entry",
        "camel_analysis", "lexique4_entry", "lexique4_pos", "urdu_ud_entry", "urdu_ud_pos", "support_count", "confidence"
    ]
    out_csv = AUDIT / f"{language}_top1000_external_verification.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(results)

    review_classes = {"semantic_review", "form_only", "weak"}
    review = [r for r in results if r["confidence"] in review_classes]
    review_csv = AUDIT / f"{language}_top1000_external_review_queue.csv"
    with review_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(review)

    counts: dict[str, int] = {}
    for r in results:
        counts[r["confidence"]] = counts.get(r["confidence"], 0) + 1

    duplicates = sorted({front for front in normalized_fronts if front and normalized_fronts.count(front) > 1})
    summary = {
        "language": language,
        "input": args.input,
        "rows": len(results),
        "expected_rows": 1000,
        "row_count_problem": len(results) != 1000,
        "blank_front_rows": sum(not bool(f) for f in normalized_fronts),
        "duplicate_front_spellings": duplicates,
        "confidence_counts": counts,
        "kaikki_coverage": sum(bool(r["kaikki_entry"]) for r in results),
        "kaikki_rows_with_english_gloss": sum(bool(r["kaikki_has_english_gloss"]) for r in results),
        "wordfreq_attested": sum(bool(r["wordfreq_attested"]) for r in results),
        "arabic_wordnet_coverage": sum(bool(r["arabic_wordnet_entry"]) for r in results),
        "camel_analysis_coverage": sum(bool(r["camel_analysis"]) for r in results),
        "lexique4_coverage": sum(bool(r["lexique4_entry"]) for r in results),
        "urdu_ud_coverage": sum(bool(r["urdu_ud_entry"]) for r in results),
        "semantic_overlap_rows": sum(bool(r["semantic_overlap"]) for r in results),
        "review_queue_rows": len(review),
        "source_load_problems": [p for p in [lexique_problem] if p],
        "policy": [
            "External sources never silently rewrite learner cards.",
            "Kaikki/Wiktextract English gloss overlap is a verification and triage signal, not an oracle.",
            "wordfreq is used only as independent corpus attestation, never as a meaning authority.",
            "Arabic WordNet, CALIMA, Lexique4, and Urdu UD are independent language-specific support signals.",
            "Missing coverage is not treated as proof that a learner entry is wrong.",
            "Rows with weak or non-overlapping semantic support are queued for explicit review."
        ]
    }
    summary_path = AUDIT / f"{language}_top1000_external_verification_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
