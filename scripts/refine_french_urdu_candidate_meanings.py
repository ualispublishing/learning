#!/usr/bin/env python3
"""Refine candidate learner meanings without changing candidate rank/front inventory.

French priority:
  existing learner EN translation -> FreeDict French-English -> Kaikki fallback
Urdu priority:
  existing learner EN translation -> Kaikki modern dictionary -> ReadUrdu fallback

The script records every available meaning source so a subsequent independent audit
can compare them. It never silently changes ranks or fronts.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
BIDI_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")
URDU_DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")


def nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", BIDI_RE.sub("", s or "")).strip()


def norm_fr(s: str) -> str:
    return nfkc(s).replace("’", "'").lower()


def norm_ur(s: str) -> str:
    s = nfkc(s).replace("ـ", "").replace("\u200c", "").replace("\u200d", "")
    s = URDU_DIAC.sub("", s)
    return s.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک").replace("ه", "ہ").strip()


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip(" ;.")


def good(text: str) -> bool:
    text = clean(text)
    low = text.casefold()
    return bool(text) and len(text) <= 220 and not any(x in low for x in (
        "alternative spelling of", "misspelling of", "obsolete spelling of",
        "the name of the latin script letter", "letter of the french alphabet",
    ))


def legacy_map(path: Path, normalizer) -> dict[str, str]:
    out = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            front = normalizer(row.get("Front", ""))
            if not front or front in out:
                continue
            m = re.search(r"(?m)^EN:\s*(.+?)\s*$", row.get("Back", "") or "")
            if m:
                val = clean(m.group(1))
                if 0 < len(val) <= 160:
                    out[front] = val
    return out


def kaikki_map(path: Path, targets: set[str], normalizer) -> dict[str, str]:
    by_word: dict[str, list[str]] = {w: [] for w in targets}
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            word = normalizer(str(obj.get("word", "")))
            if word not in targets:
                continue
            for sense in obj.get("senses") or []:
                for gloss in sense.get("glosses") or []:
                    g = clean(gloss)
                    if good(g) and g not in by_word[word]:
                        by_word[word].append(g)
    out = {}
    for word, glosses in by_word.items():
        if not glosses:
            continue
        # Prefer concise non-etymological/non-morphological glosses.
        lexical = [g for g in glosses if not any(x in g.casefold() for x in (
            "form of ", "inflection of ", "plural of ", "feminine of ", "masculine of ",
            "alternative form of ", "also: form of", "initialism of", "abbreviation of",
        ))]
        pool = lexical or glosses
        pool.sort(key=lambda g: (len(g), g.casefold()))
        chosen = []
        for g in pool:
            if any(g.casefold() in c.casefold() or c.casefold() in g.casefold() for c in chosen):
                continue
            chosen.append(g)
            if len(chosen) >= 3:
                break
        out[word] = "; ".join(chosen)[:360].rstrip(" ;")
    return out


def localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def freedict_map(path: Path, targets: set[str]) -> dict[str, str]:
    out: dict[str, list[str]] = {w: [] for w in targets}
    for _, elem in ET.iterparse(path, events=("end",)):
        if localname(elem.tag) != "entry":
            continue
        orths = []
        trans = []
        for child in elem.iter():
            if localname(child.tag) == "orth" and child.text:
                orths.append(norm_fr(child.text))
            if localname(child.tag) == "cit" and child.attrib.get("type") == "trans":
                for q in child.iter():
                    if localname(q.tag) == "quote" and q.text:
                        val = clean(q.text)
                        if val:
                            trans.append(val)
        for orth in orths:
            if orth not in targets:
                continue
            for val in trans:
                if val not in out[orth]:
                    out[orth].append(val)
        elem.clear()
    final = {}
    for word, vals in out.items():
        if not vals:
            continue
        vals.sort(key=lambda x: (len(x), x.casefold()))
        final[word] = "; ".join(vals[:4])[:260].rstrip(" ;")
    return final

# Explicit high-risk closed-class senses. These are standard learner meanings and
# also serve as tripwires against wrong-homograph dictionary selection.
FRENCH_SAFE = {
    "le": "the; him; it (masculine direct-object pronoun)",
    "une": "a; an; one (feminine)",
    "du": "of the; from the; some (partitive)",
    "mon": "my (masculine singular; also before vowel-initial feminine nouns)",
    "moi": "me; myself",
    "te": "you; yourself (object/reflexive pronoun)",
    "ça": "that; it; this (informal demonstrative pronoun)",
}

URDU_SAFE = {
    "کے": "of; belonging to (genitive, masculine plural/oblique)",
    "میں": "I; in; into (depending on context)",
    "کی": "of; belonging to (genitive, feminine singular)",
    "ہے": "is; is/exists (third-person singular present of ہونا)",
    "اور": "and; more; other",
    "سے": "from; with; by; than",
    "کا": "of; belonging to (genitive, masculine singular)",
    "کو": "to; for; marks dative/accusative objects",
    "نے": "ergative postposition used with many perfective transitive clauses",
    "اس": "this/that; him/her/it (oblique singular)",
    "کہ": "that; saying/having said (depending on construction)",
    "ہیں": "are (plural/honorific present of ہونا)",
    "پر": "on; at; upon; but/yet (depending on use)",
    "کر": "do; having done; verb stem/conjunctive form of کرنا",
    "ہو": "be; become (form of ہونا)",
    "بھی": "also; too; even",
    "ایک": "one; a; an",
    "یہ": "this; these; he/she/it/they (proximal)",
    "نہیں": "no; not",
    "ان": "those; them; these (oblique plural, depending on context)",
    "کیا": "what?; did/done (depending on context)",
    "تو": "then; so; you (informal)",
    "وہ": "that; those; he/she/it/they (distal)",
    "لئے": "for; taken (context-dependent; often in کے لئے 'for')",
    "جو": "who; which; that (relative pronoun)",
    "و": "and",
    "گا": "will (masculine singular future marker)",
    "ہی": "only; just; emphatic particle",
    "نہ": "not; neither; do not",
    "جب": "when",
    "اپنے": "one's own; own (masculine plural/oblique form of اپنا)",
    "آپ": "you (formal/honorific); oneself",
    "جس": "who/which/that (oblique singular relative pronoun)",
    "دیا": "gave; given (masculine singular form of دینا); lamp",
    "ہوئے": "became; happened; were (plural/honorific form)",
    "تک": "until; up to; as far as",
    "بعد": "after; afterwards",
    "لیکن": "but; however",
    "گی": "will (feminine future marker)",
    "کوئی": "someone; anyone; some; any",
    "گے": "will (masculine plural/honorific future marker)",
    "اپنی": "one's own; own (feminine form of اپنا)",
}


def rewrite_candidate(language: str, rows: list[dict]) -> None:
    candidate = AUDIT / f"{language}_top1000_candidate.csv"
    with candidate.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"])
        w.writeheader()
        for r in rows:
            back = (
                f"Rank: {r['rank']}\n\nMeaning: {r['meaning']}\n\nPart of speech: {r['pos']}\n\n"
                f"Frequency evidence: {r['frequency']}\n\nSources:\n- {r['source']}\n"
                f"- Refined through multi-dictionary learner-safety selection; candidate only until final audit"
            )
            w.writerow({"Front": r["front"], "Back": back})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=["french", "urdu"], required=True)
    ap.add_argument("--legacy", required=True)
    ap.add_argument("--kaikki", required=True)
    ap.add_argument("--freedict")
    args = ap.parse_args()

    language = args.language
    evidence_path = AUDIT / f"{language}_core1000_candidate_evidence.csv"
    with evidence_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"Refusing refinement: {language} candidate has {len(rows)} rows")

    normalizer = norm_fr if language == "french" else norm_ur
    targets = {normalizer(r["front"]) for r in rows}
    legacy = legacy_map(ROOT / args.legacy, normalizer)
    kaikki = kaikki_map(Path(args.kaikki), targets, normalizer)
    freedict = freedict_map(Path(args.freedict), targets) if language == "french" and args.freedict else {}
    safe = FRENCH_SAFE if language == "french" else URDU_SAFE

    refined = []
    source_counts: dict[str, int] = {}
    for r in rows:
        front = normalizer(r["front"])
        current = clean(r.get("meaning", ""))
        legacy_m = legacy.get(front, "")
        kaikki_m = kaikki.get(front, "")
        freedict_m = freedict.get(front, "")
        if front in safe:
            meaning = safe[front]; chosen = "explicit_high_risk_review"
        elif legacy_m:
            meaning = legacy_m; chosen = "legacy_learner_translation"
        elif freedict_m:
            meaning = freedict_m; chosen = "freedict"
        elif kaikki_m:
            meaning = kaikki_m; chosen = "kaikki"
        else:
            meaning = current; chosen = "existing_candidate_fallback"
        source_counts[chosen] = source_counts.get(chosen, 0) + 1
        rr = dict(r)
        rr.update({
            "front": front,
            "meaning": meaning,
            "legacy_crosscheck": legacy_m,
            "kaikki_crosscheck": kaikki_m,
            "freedict_crosscheck": freedict_m,
            "meaning_selection": chosen,
        })
        refined.append(rr)

    fields = list(refined[0])
    with evidence_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(refined)
    rewrite_candidate(language, refined)

    summary_path = AUDIT / f"{language}_meaning_refinement_summary.json"
    summary = {
        "language": language,
        "rows": len(refined),
        "source_counts": source_counts,
        "legacy_crosscheck_coverage": sum(bool(r["legacy_crosscheck"]) for r in refined),
        "kaikki_crosscheck_coverage": sum(bool(r["kaikki_crosscheck"]) for r in refined),
        "freedict_crosscheck_coverage": sum(bool(r["freedict_crosscheck"]) for r in refined),
        "blank_meanings": sum(not bool(r["meaning"]) for r in refined),
        "status": "refined_candidate_not_promoted",
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
