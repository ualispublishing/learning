#!/usr/bin/env python3
"""Build non-promoted 1,000-entry French/Urdu core candidates from lexical sources.

French: Lexique 4 lemma frequencies + Kaikki English-Wiktionary meanings.
Urdu: CLE 5,000 frequency list, filtered through CLE Urdu WordNet/closed-class
      inventories, with meanings from the open ReadUrdu composite dictionary and
      Kaikki as a secondary source.

Nothing in this script overwrites the learner decks. It only writes audit candidates.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
AUDIT.mkdir(exist_ok=True)

LATINISH = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿŒœÆæÇçÉéÈèÊêËëÀàÂâÄäÙùÛûÜüÔôÖöÎîÏïŸÿ'’\-]+$")
URDU_CHAR = r"\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF"
URDUISH = re.compile(rf"^[{URDU_CHAR}\s‌‍]+$")
URDU_DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")


def nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").strip()


def norm_fr(s: str) -> str:
    return nfkc(s).replace("’", "'").lower()


def norm_ur(s: str) -> str:
    s = nfkc(s).replace("ـ", "").replace("\u200c", "").replace("\u200d", "")
    s = URDU_DIAC.sub("", s)
    # Common Arabic-codepoint spellings normalized to Urdu codepoints.
    return s.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک").replace("ه", "ہ").strip()


def to_float(x: str) -> float:
    try:
        return float((x or "0").replace(",", "."))
    except ValueError:
        return 0.0


def clean_gloss(g: str) -> str:
    g = re.sub(r"\s+", " ", str(g or "")).strip(" ;.")
    g = re.sub(r"\([^)]*IPA[^)]*\)", "", g).strip()
    return g


def good_gloss(g: str) -> bool:
    low = g.lower()
    bad = (
        "form of ", "plural of ", "feminine of ", "masculine of ", "alternative spelling of ",
        "alternative form of ", "inflection of ", "misspelling of ", "obsolete spelling of ",
        "nonstandard spelling of ", "eye dialect of ", "pronunciation spelling of ",
    )
    return bool(g) and len(g) <= 220 and not any(x in low for x in bad)


def load_kaikki(path: Path, normalizer) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            word = normalizer(str(obj.get("word", "")))
            if not word:
                continue
            rec = out.setdefault(word, {"pos": set(), "glosses": []})
            if obj.get("pos"):
                rec["pos"].add(str(obj["pos"]).lower())
            for sense in obj.get("senses") or []:
                for gloss in sense.get("glosses") or []:
                    gloss = clean_gloss(gloss)
                    if good_gloss(gloss) and gloss not in rec["glosses"]:
                        rec["glosses"].append(gloss)
    return out


def compact_meaning(glosses: list[str]) -> str:
    if not glosses:
        return ""
    # Prefer concise lexicographic senses. Keep at most three distinct senses.
    ordered = sorted(glosses, key=lambda g: (len(g), g.lower()))
    chosen: list[str] = []
    for g in ordered:
        if any(g.lower() in x.lower() or x.lower() in g.lower() for x in chosen):
            continue
        chosen.append(g)
        if len(chosen) >= 3:
            break
    text = "; ".join(chosen)
    return text[:420].rstrip(" ;")


def human_fr_pos(cgrams: set[str], kaikki_pos: set[str]) -> str:
    mapping = {
        "nom": "noun", "ver": "verb", "adj": "adjective", "adv": "adverb", "pro": "pronoun",
        "art": "article/determiner", "det": "determiner", "pre": "preposition", "con": "conjunction",
        "aux": "auxiliary verb", "ono": "interjection/onomatopoeia", "num": "numeral",
    }
    vals = []
    for c in sorted(cgrams):
        key = c.strip().lower()[:3]
        vals.append(mapping.get(key, c.strip().lower()))
    if not vals:
        vals = sorted(kaikki_pos)
    return " / ".join(dict.fromkeys(vals)) or "unspecified"


def build_french(args) -> None:
    kaikki = load_kaikki(Path(args.kaikki), norm_fr)
    grouped: dict[str, dict] = {}
    with Path(args.lexique).open(encoding="utf-8-sig", errors="replace", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            lemma = norm_fr(row.get("4_Lemme", ""))
            if not lemma or " " in lemma or not LATINISH.fullmatch(lemma):
                continue
            cgram = (row.get("5_Cgram") or "").strip()
            # NAM = proper name in Lexique; keep learner core lexical rather than name-heavy.
            if cgram.upper().startswith("NAM"):
                continue
            freq = to_float(row.get("12_FreqLemme") or row.get("11_FreqOrtho") or row.get("10_FreqMot"))
            rec = grouped.setdefault(lemma, {"freq": 0.0, "cgram": set()})
            rec["freq"] = max(rec["freq"], freq)
            if cgram:
                rec["cgram"].add(cgram)

    ranked = sorted(grouped.items(), key=lambda kv: (-kv[1]["freq"], kv[0]))
    selected = []
    rejected = []
    for lemma, meta in ranked:
        k = kaikki.get(lemma)
        meaning = compact_meaning(k["glosses"]) if k else ""
        if not meaning:
            rejected.append({"front": lemma, "frequency": meta["freq"], "reason": "no_clean_kaikki_gloss"})
            continue
        selected.append({
            "rank": len(selected) + 1,
            "front": lemma,
            "meaning": meaning,
            "pos": human_fr_pos(meta["cgram"], k["pos"]),
            "frequency": meta["freq"],
            "lexique_cgram": "|".join(sorted(meta["cgram"])),
            "kaikki_pos": "|".join(sorted(k["pos"])),
            "source": "Lexique 4 lemma frequency + Kaikki/Wiktextract English gloss",
        })
        if len(selected) == 1000:
            break
    write_candidate("french", selected, rejected)


def extract_urdu_freq(text: str) -> list[tuple[str, int]]:
    pairs: list[tuple[str, int]] = []
    seen = set()
    # pdftotext may put RTL cells before or after the frequency column.
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        m = re.match(r"^(\d{2,})\s+(.+)$", line)
        if m:
            freq, word = int(m.group(1)), m.group(2)
        else:
            m = re.match(r"^(.+?)\s+(\d{2,})$", line)
            if not m:
                continue
            word, freq = m.group(1), int(m.group(2))
        word = norm_ur(word)
        if not word or not URDUISH.fullmatch(word) or len(word) > 40:
            continue
        if word in seen:
            continue
        seen.add(word)
        pairs.append((word, freq))
    pairs.sort(key=lambda x: -x[1])
    return pairs


def inventory_contains(text: str, word: str) -> bool:
    # Exact-script boundary in the CLE WordNet/closed-class text extraction.
    ntext = norm_ur(text)
    return bool(re.search(rf"(?<![{URDU_CHAR}]){re.escape(word)}(?![{URDU_CHAR}])", ntext))


def read_readurdu(path: Path) -> dict[str, dict]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for key, val in obj.items():
        k = norm_ur(key)
        if not k:
            continue
        eng = ""
        dev = ""
        if isinstance(val, list):
            if val:
                dev = str(val[0] or "")
            if len(val) > 1:
                eng = str(val[1] or "")
        elif isinstance(val, dict):
            dev = str(val.get("devanagari") or val.get("dev") or "")
            eng = str(val.get("english") or val.get("meaning") or val.get("en") or "")
        eng = clean_gloss(eng)
        if eng:
            out[k] = {"meaning": eng[:420].rstrip(" ;"), "devanagari": dev}
    return out


def build_urdu(args) -> None:
    freq_text = Path(args.urdu_freq_text).read_text(encoding="utf-8", errors="replace")
    wn_text = Path(args.urdu_wordnet_text).read_text(encoding="utf-8", errors="replace")
    closed_text = Path(args.urdu_closed_text).read_text(encoding="utf-8", errors="replace")
    ranked = extract_urdu_freq(freq_text)
    readurdu = read_readurdu(Path(args.readurdu))
    kaikki = load_kaikki(Path(args.kaikki), norm_ur)

    selected = []
    rejected = []
    for word, freq in ranked:
        # Build a lexeme-oriented core: content lexemes must be in CLE Urdu WordNet;
        # function/closed-class items may instead be in CLE's closed-class inventory.
        in_wn = inventory_contains(wn_text, word)
        in_closed = inventory_contains(closed_text, word)
        if not (in_wn or in_closed):
            rejected.append({"front": word, "frequency": freq, "reason": "not_in_CLE_lexeme_or_closed_inventory"})
            continue
        meaning = ""
        semantic_source = ""
        if word in readurdu:
            meaning = readurdu[word]["meaning"]
            semantic_source = "ReadUrdu composite (curated/Platts/Wiktionary)"
        if (not meaning or len(meaning) < 2) and word in kaikki:
            meaning = compact_meaning(kaikki[word]["glosses"])
            semantic_source = "Kaikki/Wiktextract"
        if not meaning:
            rejected.append({"front": word, "frequency": freq, "reason": "no_clean_dictionary_meaning"})
            continue
        selected.append({
            "rank": len(selected) + 1,
            "front": word,
            "meaning": meaning,
            "pos": "|".join(sorted(kaikki.get(word, {}).get("pos", set()))) or ("closed-class" if in_closed else "content word"),
            "frequency": freq,
            "cle_wordnet": in_wn,
            "cle_closed_class": in_closed,
            "kaikki_entry": word in kaikki,
            "semantic_source": semantic_source,
            "source": "CLE Urdu 5000 frequency rank + CLE Urdu WordNet/closed-class lexical filter",
        })
        if len(selected) == 1000:
            break
    write_candidate("urdu", selected, rejected)


def write_candidate(language: str, selected: list[dict], rejected: list[dict]) -> None:
    evidence = AUDIT / f"{language}_core1000_candidate_evidence.csv"
    fields = list(selected[0]) if selected else ["rank", "front", "meaning", "pos", "frequency"]
    with evidence.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(selected)

    candidate = AUDIT / f"{language}_top1000_candidate.csv"
    with candidate.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"])
        w.writeheader()
        for r in selected:
            back = (
                f"Rank: {r['rank']}\n\n"
                f"Meaning: {r['meaning']}\n\n"
                f"Part of speech: {r['pos']}\n\n"
                f"Frequency evidence: {r['frequency']}\n\n"
                f"Sources:\n- {r['source']}\n"
                f"- Learner candidate only; requires independent verification before promotion"
            )
            w.writerow({"Front": r["front"], "Back": back})

    rej = AUDIT / f"{language}_core_candidate_rejections.csv"
    with rej.open("w", encoding="utf-8", newline="") as f:
        fields_r = list(rejected[0]) if rejected else ["front", "frequency", "reason"]
        w = csv.DictWriter(f, fieldnames=fields_r)
        w.writeheader(); w.writerows(rejected)

    fronts = [r["front"] for r in selected]
    summary = {
        "language": language,
        "candidate_rows": len(selected),
        "distinct_fronts": len(set(fronts)),
        "duplicates": sorted({x for x in fronts if fronts.count(x) > 1}),
        "meaning_rows": sum(bool(r.get("meaning")) for r in selected),
        "rejected_before_fill": len(rejected),
        "promotion_ready_structurally": len(selected) == 1000 and len(set(fronts)) == 1000 and all(r.get("meaning") for r in selected),
        "status": "candidate_only_not_promoted",
    }
    (AUDIT / f"{language}_core1000_candidate_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=["french", "urdu"], required=True)
    ap.add_argument("--lexique")
    ap.add_argument("--kaikki", required=True)
    ap.add_argument("--urdu-freq-text")
    ap.add_argument("--urdu-wordnet-text")
    ap.add_argument("--urdu-closed-text")
    ap.add_argument("--readurdu")
    args = ap.parse_args()
    if args.language == "french":
        if not args.lexique:
            raise SystemExit("--lexique required for French")
        build_french(args)
    else:
        required = [args.urdu_freq_text, args.urdu_wordnet_text, args.urdu_closed_text, args.readurdu]
        if not all(required):
            raise SystemExit("Urdu requires frequency/WordNet/closed-class text and ReadUrdu dictionary")
        build_urdu(args)


if __name__ == "__main__":
    main()
