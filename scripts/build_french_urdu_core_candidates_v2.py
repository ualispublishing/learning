#!/usr/bin/env python3
"""Build precision French/Urdu core-1000 candidates without promoting them.

French
- Recomputes lemma frequency from Lexique 4 surface frequencies instead of trusting
  FreqLemme blindly (this avoids a few POS-association anomalies in the source).
- Requires Lexique POS to agree with a Kaikki/Wiktextract lexical entry.
- Prefers the existing deck's concise English translation when available, while
  retaining Kaikki as an independent dictionary check/source of fallback meanings.

Urdu
- Parses CLE's 5,000-word corpus frequency list after Unicode compatibility and
  bidirectional-control normalization.
- Prefers entries supported by CLE Urdu WordNet or CLE closed-class inventories.
- Uses the open ReadUrdu composite dictionary for English meanings, with Kaikki
  fallback where available.

Outputs remain audit candidates only. Promotion is a separate gated operation.
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

BIDI_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")
URDU_DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
URDU_CHAR = r"\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF"
URDUISH = re.compile(rf"^[{URDU_CHAR}\s]+$")
FRENCH_LETTER_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿŒœÆæÇçÉéÈèÊêËëÀàÂâÄäÙùÛûÜüÔôÖöÎîÏïŸÿ]")


def nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", BIDI_RE.sub("", s or "")).strip()


def norm_fr(s: str) -> str:
    return nfkc(s).replace("’", "'").lower()


def norm_ur(s: str) -> str:
    s = nfkc(s).replace("ـ", "").replace("\u200c", "").replace("\u200d", "")
    s = URDU_DIAC.sub("", s)
    return s.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک").replace("ه", "ہ").strip()


def to_float(x: str) -> float:
    try:
        return float((x or "0").replace(",", "."))
    except ValueError:
        return 0.0


def clean_gloss(g: str) -> str:
    g = re.sub(r"\s+", " ", str(g or "")).strip(" ;.")
    return g


def good_gloss(g: str) -> bool:
    low = g.lower()
    bad = (
        "form of ", "plural of ", "feminine of ", "masculine of ",
        "alternative spelling of ", "alternative form of ", "inflection of ",
        "misspelling of ", "obsolete spelling of ", "nonstandard spelling of ",
        "eye dialect of ", "pronunciation spelling of ", "initialism of ",
        "abbreviation of ", "the name of the latin script letter",
        "letter of the french alphabet",
    )
    return bool(g) and len(g) <= 220 and not any(x in low for x in bad)


def compact_meaning(glosses: list[str]) -> str:
    clean = []
    for g in glosses:
        g = clean_gloss(g)
        if good_gloss(g) and g not in clean:
            clean.append(g)
    if not clean:
        return ""
    # Concise senses first, but keep distinct meanings rather than morphological notes.
    clean.sort(key=lambda x: (len(x), x.casefold()))
    chosen: list[str] = []
    for g in clean:
        gl = g.casefold()
        if any(gl in c.casefold() or c.casefold() in gl for c in chosen):
            continue
        chosen.append(g)
        if len(chosen) >= 3:
            break
    return "; ".join(chosen)[:420].rstrip(" ;")


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
            pos = str(obj.get("pos") or "").lower()
            rec = out.setdefault(word, {"poses": set(), "all_glosses": [], "by_pos": defaultdict(list)})
            if pos:
                rec["poses"].add(pos)
            for sense in obj.get("senses") or []:
                for gloss in sense.get("glosses") or []:
                    gloss = clean_gloss(gloss)
                    if not good_gloss(gloss):
                        continue
                    if gloss not in rec["all_glosses"]:
                        rec["all_glosses"].append(gloss)
                    if pos and gloss not in rec["by_pos"][pos]:
                        rec["by_pos"][pos].append(gloss)
    return out


def load_legacy_english(path: Path, normalizer) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            front = normalizer(row.get("Front", ""))
            if not front or front in out:
                continue
            back = row.get("Back", "") or ""
            m = re.search(r"(?m)^EN:\s*(.+?)\s*$", back)
            if m:
                val = re.sub(r"\s+", " ", m.group(1)).strip()
                if 0 < len(val) <= 160:
                    out[front] = val
    return out


def cgram_to_kaikki(cgram: str) -> set[str]:
    c = (cgram or "").upper()
    if c.startswith("ART"):
        return {"article", "det"}
    if c.startswith("ADJ"):
        return {"adj", "det"} if any(x in c for x in (":DEM", ":POS", ":IND")) else {"adj"}
    if c.startswith("ADV"):
        return {"adv"}
    if c.startswith("AUX") or c.startswith("VER"):
        return {"verb"}
    if c.startswith("CON"):
        return {"conj"}
    if c.startswith("NOM"):
        return {"noun"}
    if c.startswith("PRE"):
        return {"prep"}
    if c.startswith("PRO"):
        return {"pron"}
    if c.startswith("ONO"):
        return {"intj"}
    return set()


def human_fr_pos(cgrams: set[str]) -> str:
    mapping = {
        "ART": "article/determiner", "ADJ": "adjective", "ADV": "adverb",
        "AUX": "auxiliary verb", "CON": "conjunction", "NOM": "noun",
        "PRE": "preposition", "PRO": "pronoun", "VER": "verb", "ONO": "interjection",
    }
    vals = []
    for c in sorted(cgrams):
        vals.append(mapping.get(c.upper().split(":", 1)[0], c.lower()))
    return " / ".join(dict.fromkeys(vals)) or "unspecified"


def build_french(args) -> None:
    kaikki = load_kaikki(Path(args.kaikki), norm_fr)
    legacy = load_legacy_english(Path(args.legacy_french), norm_fr) if args.legacy_french else {}

    grouped: dict[str, dict] = {}
    with Path(args.lexique).open(encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            lemma = norm_fr(row.get("4_Lemme", ""))
            cgram = (row.get("5_Cgram") or "").strip()
            if not lemma or not cgram or cgram.upper().startswith("NAM"):
                continue
            # Elision fragments and one-letter alphabetic tokens are not useful standalone cards.
            if len(FRENCH_LETTER_RE.findall(lemma)) < 2 or lemma.endswith("'"):
                continue
            if " " in lemma:
                continue
            freq = to_float(row.get("10_FreqMot"))
            rec = grouped.setdefault(lemma, {"freq_by_cgram": defaultdict(float), "surface_rows": 0})
            rec["freq_by_cgram"][cgram] += freq
            rec["surface_rows"] += 1

    ranked = []
    rejected = []
    for lemma, meta in grouped.items():
        k = kaikki.get(lemma)
        if not k:
            rejected.append({"front": lemma, "frequency": 0, "reason": "no_kaikki_lexical_entry"})
            continue
        compatible_cgrams = set()
        compatible_freq = 0.0
        compatible_poses = set()
        for cgram, freq in meta["freq_by_cgram"].items():
            target = cgram_to_kaikki(cgram)
            hit = target & set(k["poses"])
            if hit:
                compatible_cgrams.add(cgram)
                compatible_freq += freq
                compatible_poses |= hit
        if compatible_freq <= 0:
            rejected.append({"front": lemma, "frequency": 0, "reason": "lexique_kaikki_pos_mismatch"})
            continue

        glosses = []
        for p in sorted(compatible_poses):
            glosses.extend(k["by_pos"].get(p, []))
        dictionary_meaning = compact_meaning(glosses) or compact_meaning(k["all_glosses"])
        legacy_meaning = legacy.get(lemma, "")
        meaning = legacy_meaning or dictionary_meaning
        if not meaning:
            rejected.append({"front": lemma, "frequency": compatible_freq, "reason": "no_clean_meaning"})
            continue
        ranked.append({
            "front": lemma,
            "meaning": meaning,
            "legacy_meaning": legacy_meaning,
            "kaikki_meaning": dictionary_meaning,
            "pos": human_fr_pos(compatible_cgrams),
            "frequency": compatible_freq,
            "lexique_cgram": "|".join(sorted(compatible_cgrams)),
            "kaikki_pos": "|".join(sorted(k["poses"])),
            "source": "Lexique 4 recomputed compatible-POS lemma frequency + Kaikki/Wiktextract; legacy EN translation preferred where available",
        })

    ranked.sort(key=lambda r: (-r["frequency"], r["front"]))
    selected = []
    for r in ranked[:1000]:
        r = dict(r)
        r["rank"] = len(selected) + 1
        selected.append(r)
    write_candidate("french", selected, rejected)


def extract_urdu_freq(text: str) -> list[tuple[str, int]]:
    pairs: list[tuple[str, int]] = []
    seen = set()
    for raw in text.splitlines():
        line = nfkc(raw)
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        # CLE tables are visually Word | Frequency; after bidi normalization either side order can occur.
        m = re.match(r"^(\d{2,})\s+(.+)$", line)
        if m:
            freq, word = int(m.group(1)), m.group(2)
        else:
            m = re.match(r"^(.+?)\s+(\d{2,})$", line)
            if not m:
                continue
            word, freq = m.group(1), int(m.group(2))
        word = norm_ur(word)
        if not word or not URDUISH.fullmatch(word) or len(word) > 45:
            continue
        if word in seen:
            continue
        seen.add(word)
        pairs.append((word, freq))
    pairs.sort(key=lambda x: -x[1])
    return pairs


def inventory_contains(normalized_text: str, word: str) -> bool:
    return bool(re.search(rf"(?<![{URDU_CHAR}]){re.escape(word)}(?![{URDU_CHAR}])", normalized_text))


def read_readurdu(path: Path) -> dict[str, dict]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    if not isinstance(obj, dict):
        return out
    for key, val in obj.items():
        k = norm_ur(str(key))
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
        elif isinstance(val, str):
            eng = val
        eng = clean_gloss(eng)
        if eng:
            out[k] = {"meaning": eng[:420].rstrip(" ;"), "devanagari": dev}
    return out


def build_urdu(args) -> None:
    freq_text = Path(args.urdu_freq_text).read_text(encoding="utf-8", errors="replace")
    wn_text = norm_ur(Path(args.urdu_wordnet_text).read_text(encoding="utf-8", errors="replace"))
    closed_text = norm_ur(Path(args.urdu_closed_text).read_text(encoding="utf-8", errors="replace"))
    ranked = extract_urdu_freq(freq_text)
    readurdu = read_readurdu(Path(args.readurdu))
    kaikki = load_kaikki(Path(args.kaikki), norm_ur)

    selected = []
    rejected = []
    for word, freq in ranked:
        in_wn = inventory_contains(wn_text, word)
        in_closed = inventory_contains(closed_text, word)
        # Strong lexical preference: CLE lexeme or closed-class inventory. If CLE's PDF
        # extraction misses an entry, require two alternate signals (ReadUrdu + Kaikki).
        alternate_double = word in readurdu and word in kaikki
        if not (in_wn or in_closed or alternate_double):
            rejected.append({"front": word, "frequency": freq, "reason": "insufficient_lexical_support"})
            continue

        meaning = ""
        semantic_source = ""
        if word in readurdu:
            meaning = readurdu[word]["meaning"]
            semantic_source = "ReadUrdu composite dictionary"
        if not meaning and word in kaikki:
            meaning = compact_meaning(kaikki[word]["all_glosses"])
            semantic_source = "Kaikki/Wiktextract"
        if not meaning:
            rejected.append({"front": word, "frequency": freq, "reason": "no_clean_dictionary_meaning"})
            continue

        kposes = sorted(kaikki.get(word, {}).get("poses", set()))
        selected.append({
            "rank": len(selected) + 1,
            "front": word,
            "meaning": meaning,
            "pos": "|".join(kposes) or ("closed-class" if in_closed else "content word"),
            "frequency": freq,
            "cle_wordnet": in_wn,
            "cle_closed_class": in_closed,
            "readurdu_entry": word in readurdu,
            "kaikki_entry": word in kaikki,
            "semantic_source": semantic_source,
            "source": "CLE Urdu 5,000 corpus frequency list + CLE lexical inventories; ReadUrdu/Kaikki semantics",
        })
        if len(selected) == 1000:
            break

    write_candidate("urdu", selected, rejected, extra_summary={"parsed_frequency_rows": len(ranked)})


def write_candidate(language: str, selected: list[dict], rejected: list[dict], extra_summary: dict | None = None) -> None:
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
                f"- Candidate only; requires independent verification before promotion"
            )
            w.writerow({"Front": r["front"], "Back": back})

    rej = AUDIT / f"{language}_core_candidate_rejections.csv"
    with rej.open("w", encoding="utf-8", newline="") as f:
        rfields = list(rejected[0]) if rejected else ["front", "frequency", "reason"]
        w = csv.DictWriter(f, fieldnames=rfields)
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
    if extra_summary:
        summary.update(extra_summary)
    (AUDIT / f"{language}_core1000_candidate_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=["french", "urdu"], required=True)
    ap.add_argument("--lexique")
    ap.add_argument("--kaikki", required=True)
    ap.add_argument("--legacy-french")
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
