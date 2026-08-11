#!/usr/bin/env python3
"""Independent semantic audit for French/Urdu 1,000-entry candidates.

The audit distinguishes source *coverage* from source *agreement*. A row is only
considered verified when the learner meaning is supported by an independent
semantic source, or is an explicitly reviewed high-risk closed-class item.

French independent sources:
- Lexique 4 frequency/POS (structural)
- Kaikki/Wiktextract English meanings
- FreeDict French-English
- WOLF / Open Multilingual WordNet 2.0 translated to OMW English
- wordfreq corpus attestation

Urdu independent/partially independent sources:
- CLE 5,000 corpus frequency + WordNet/closed-class inventories (structural)
- legacy learner English translation
- Kaikki/Wiktextract
- ReadUrdu composite dictionary
- TUFS basic learner vocabulary + OMW English mapping when available
- wordfreq corpus attestation
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

from wordfreq import zipf_frequency

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
BIDI_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")
URDU_DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
STOP = {
    "a","an","the","to","of","in","on","at","for","from","by","with","and","or","as","is","are","was","were","be","been","being",
    "one","that","this","which","who","whom","something","someone","used","use","form","forms","person","thing","things","depending","context",
    "masculine","feminine","singular","plural","present","past","future","particle","pronoun","noun","verb","adjective","adverb","preposition","conjunction",
}


def nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", BIDI_RE.sub("", s or "")).strip()


def norm_fr(s: str) -> str:
    return nfkc(s).replace("’", "'").lower()


def norm_ur(s: str) -> str:
    s = nfkc(s).replace("ـ", "").replace("\u200c", "").replace("\u200d", "")
    s = URDU_DIAC.sub("", s)
    return s.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک").replace("ه", "ہ").strip()


def toks(text: str) -> set[str]:
    out = set()
    for t in WORD_RE.findall((text or "").lower()):
        t = t.strip("'-")
        if not t or t in STOP:
            continue
        # conservative English normalization for dictionary-overlap detection
        if len(t) > 5 and t.endswith("ies"):
            t = t[:-3] + "y"
        else:
            for suf in ("ingly", "ation", "ments", "ment", "ing", "ied", "ed", "es", "s"):
                if len(t) > len(suf) + 3 and t.endswith(suf):
                    t = t[:-len(suf)]
                    break
        if len(t) >= 2 and t not in STOP:
            out.add(t)
    return out


def agree(a: str, b: str) -> tuple[bool, str]:
    aa, bb = toks(a), toks(b)
    overlap = sorted(aa & bb)
    return bool(overlap), "|".join(overlap[:12])


def load_readurdu(path: Path | None) -> dict[str, str]:
    if not path or not path.exists():
        return {}
    obj = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    if not isinstance(obj, dict):
        return out
    for key, val in obj.items():
        k = norm_ur(str(key))
        eng = ""
        if isinstance(val, list) and len(val) > 1:
            eng = str(val[1] or "")
        elif isinstance(val, dict):
            eng = str(val.get("english") or val.get("meaning") or val.get("en") or "")
        elif isinstance(val, str):
            eng = val
        eng = re.sub(r"\s+", " ", eng).strip()
        if k and eng:
            out[k] = eng[:1000]
    return out


def split_tufs_lemmas(text: str, language: str) -> list[str]:
    normalizer = norm_fr if language == "french" else norm_ur
    vals = []
    for part in re.split(r"[;|]", text or ""):
        part = re.sub(r"\([^)]*\)", "", part).strip()
        if part:
            vals.append(normalizer(part))
    return [v for v in vals if v]


def load_tufs(path: Path | None, language: str) -> dict[str, set[str]]:
    if not path or not path.exists():
        return {}
    allowed = {"fr", "fra", "french"} if language == "french" else {"ur", "urd", "urdu"}
    out: dict[str, set[str]] = {}
    with path.open(encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            lang = (row.get("lang") or "").strip().casefold()
            if lang not in allowed:
                continue
            iids = set(re.findall(r"\d{8}-[nvars]", row.get("iids", "") or ""))
            for lemma in split_tufs_lemmas(row.get("lemma", ""), language):
                out.setdefault(lemma, set()).update(iids)
    return out


def omw_french_evidence(front: str, fr_wn, en_wn) -> str:
    evidence = []
    try:
        synsets = fr_wn.synsets(front)
    except Exception:
        return ""
    for ss in synsets:
        try:
            translated = ss.translate(lexicon="omw-en:2.0")
        except Exception:
            translated = []
        for ens in translated:
            try:
                evidence.extend(ens.lemmas())
                definition = ens.definition()
                if definition:
                    evidence.append(definition)
            except Exception:
                pass
    return "; ".join(dict.fromkeys(evidence))[:4000]


def tufs_english_evidence(iids: set[str], en_wn) -> str:
    evidence = []
    for iid in iids:
        ids = [f"omw-en-{iid}", iid]
        ss = None
        for sid in ids:
            try:
                ss = en_wn.synset(sid)
                break
            except Exception:
                pass
        if not ss:
            continue
        try:
            evidence.extend(ss.lemmas())
            definition = ss.definition()
            if definition:
                evidence.append(definition)
        except Exception:
            pass
    return "; ".join(dict.fromkeys(evidence))[:4000]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=["french", "urdu"], required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--readurdu")
    ap.add_argument("--tufs-vocab")
    args = ap.parse_args()

    language = args.language
    normalizer = norm_fr if language == "french" else norm_ur
    lang_code = "fr" if language == "french" else "ur"
    with (ROOT / args.evidence).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"Expected 1000 candidate rows, found {len(rows)}")

    readurdu = load_readurdu(Path(args.readurdu)) if args.readurdu else {}
    tufs = load_tufs(Path(args.tufs_vocab), language) if args.tufs_vocab else {}

    import wn
    en_wn = wn.Wordnet("omw-en:2.0")
    fr_wn = wn.Wordnet("omw-fr:2.0") if language == "french" else None

    audited = []
    for r in rows:
        front = normalizer(r.get("front", ""))
        meaning = r.get("meaning", "") or ""
        selection = r.get("meaning_selection", "") or ""
        legacy = r.get("legacy_crosscheck", r.get("legacy_meaning", "")) or ""
        kaikki = r.get("kaikki_crosscheck", r.get("kaikki_meaning", "")) or ""
        freedict = r.get("freedict_crosscheck", "") or ""
        readurdu_meaning = readurdu.get(front, "") if language == "urdu" else ""
        tufs_iids = tufs.get(front, set())
        tufs_ev = tufs_english_evidence(tufs_iids, en_wn) if tufs_iids else ""
        omw_ev = omw_french_evidence(front, fr_wn, en_wn) if language == "french" else ""

        semantic_sources = {}
        overlap_terms = {}
        for name, text in (
            ("legacy", legacy), ("kaikki", kaikki), ("freedict", freedict),
            ("readurdu", readurdu_meaning), ("omw", omw_ev), ("tufs_omw", tufs_ev),
        ):
            if not text:
                continue
            ok, terms = agree(meaning, text)
            semantic_sources[name] = ok
            if terms:
                overlap_terms[name] = terms

        positive = sorted([k for k, v in semantic_sources.items() if v])
        # Do not count a source as an independent crosscheck if it is the source from which
        # the candidate meaning was directly selected.
        selected_source_alias = {
            "legacy_learner_translation": "legacy",
            "freedict": "freedict",
            "kaikki": "kaikki",
            "existing_candidate_fallback": "readurdu" if language == "urdu" else "kaikki",
        }.get(selection)
        independent_positive = [p for p in positive if p != selected_source_alias]

        freq = float(r.get("frequency", "0") or 0)
        zipf = float(zipf_frequency(front, lang_code)) if front else 0.0
        explicit = selection == "explicit_high_risk_review"

        # A learner-facing meaning passes if it is explicitly reviewed for a high-risk
        # closed-class word, or if at least one independent semantic source agrees while
        # the form also has strong frequency/lexical support. Two agreeing independent
        # semantic sources are recorded as strong.
        if explicit:
            status = "verified_explicit_review"
        elif len(independent_positive) >= 2:
            status = "verified_strong"
        elif len(independent_positive) >= 1 and freq > 0 and zipf > 0:
            status = "verified"
        else:
            status = "review"

        audited.append({
            "rank": r.get("rank", ""),
            "front": front,
            "meaning": meaning,
            "meaning_selection": selection,
            "frequency": r.get("frequency", ""),
            "wordfreq_zipf": f"{zipf:.2f}",
            "legacy_agrees": semantic_sources.get("legacy", False),
            "kaikki_agrees": semantic_sources.get("kaikki", False),
            "freedict_agrees": semantic_sources.get("freedict", False),
            "readurdu_agrees": semantic_sources.get("readurdu", False),
            "omw_agrees": semantic_sources.get("omw", False),
            "tufs_entry": bool(tufs_iids or front in tufs),
            "tufs_omw_agrees": semantic_sources.get("tufs_omw", False),
            "independent_semantic_sources": "|".join(independent_positive),
            "overlap_terms": json.dumps(overlap_terms, ensure_ascii=False, sort_keys=True),
            "status": status,
        })

    fields = list(audited[0])
    out = AUDIT / f"{language}_core1000_semantic_audit.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(audited)
    review = [r for r in audited if r["status"] == "review"]
    q = AUDIT / f"{language}_core1000_semantic_review_queue.csv"
    with q.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(review)

    counts = {}
    for r in audited:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    summary = {
        "language": language,
        "rows": len(audited),
        "status_counts": counts,
        "review_rows": len(review),
        "wordfreq_attested": sum(float(r["wordfreq_zipf"]) > 0 for r in audited),
        "legacy_semantic_agreement": sum(bool(r["legacy_agrees"]) for r in audited),
        "kaikki_semantic_agreement": sum(bool(r["kaikki_agrees"]) for r in audited),
        "freedict_semantic_agreement": sum(bool(r["freedict_agrees"]) for r in audited),
        "readurdu_semantic_agreement": sum(bool(r["readurdu_agrees"]) for r in audited),
        "omw_semantic_agreement": sum(bool(r["omw_agrees"]) for r in audited),
        "tufs_form_coverage": sum(bool(r["tufs_entry"]) for r in audited),
        "tufs_omw_semantic_agreement": sum(bool(r["tufs_omw_agrees"]) for r in audited),
        "promotion_gate": "PASS" if not review else "REVIEW_REQUIRED",
    }
    (AUDIT / f"{language}_core1000_semantic_audit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
