#!/usr/bin/env python3
"""Build real learner-facing rank 1001-3000 continuation candidates.

The verified live top-1000 decks are immutable inputs. This script replaces the
placeholder continuation concept with 2,000 real, frequency-ranked lexical items
per language, excluding every live top-1000 front. Candidates are written under
audit/ and are never promoted by this script.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import build_french_urdu_core_candidates_v2 as fu
import build_arabic_top1000_precision as arprec
import refine_french_urdu_candidate_meanings_v4 as v4

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
AUDIT.mkdir(exist_ok=True)
TARGET = 2000
START_RANK = 1001
END_RANK = 3000
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")
BAD_GLOSS_FRAGMENT = re.compile(r"(?:\[[^\]]*\]|<[^>]*>|(?:^|\s)[a-z]+\+|\+[a-z]+)", re.I)


def read_fronts(path: Path, normalizer=lambda x: x) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return {normalizer((r.get("Front") or "").strip()) for r in csv.DictReader(f) if (r.get("Front") or "").strip()}


def clean_meaning(text: str) -> str:
    x = (text or "").replace("_", " ").strip()
    x = re.sub(r"\s+", " ", x)
    x = re.sub(r"\s*;\s*", "; ", x)
    return x.strip(" ;.")


def good_meaning(text: str) -> bool:
    x = clean_meaning(text)
    if not x or len(x) > 320:
        return False
    if BAD_GLOSS_FRAGMENT.search(x):
        return False
    return True


def write_outputs(language: str, rows: list[dict], rejected: list[dict]) -> None:
    evidence = AUDIT / f"{language}_top3000_continuation_evidence.csv"
    fields = list(rows[0]) if rows else ["rank", "front", "meaning", "pos", "frequency"]
    with evidence.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    candidate = AUDIT / f"{language}_top3000_candidate.csv"
    with candidate.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Front", "Back"])
        w.writeheader()
        for r in rows:
            lines = [
                f"Rank: {r['rank']}", "", f"Meaning: {r['meaning']}", "",
                f"Part of speech: {r.get('pos') or 'unspecified'}", "",
                f"Frequency evidence: {r.get('frequency', '')}", "", "Sources:",
                f"- {r.get('source', '')}",
                "- Continuation candidate; requires independent verification before promotion",
            ]
            if r.get("root"):
                lines[6:6] = [f"Root: {r['root']}", ""]
            w.writerow({"Front": r["front"], "Back": "\n".join(lines)})

    rej = AUDIT / f"{language}_top3000_rejections.csv"
    rfields = list(rejected[0]) if rejected else ["front", "frequency", "reason"]
    with rej.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rfields)
        w.writeheader(); w.writerows(rejected)

    fronts = [r["front"] for r in rows]
    summary = {
        "language": language,
        "continuation_rows": len(rows),
        "expected_rows": TARGET,
        "start_rank": START_RANK,
        "end_rank": END_RANK,
        "distinct_fronts": len(set(fronts)),
        "meaning_rows": sum(bool(r.get("meaning")) for r in rows),
        "rejected_rows": len(rejected),
        "structural_gate": "PASS" if len(rows) == TARGET and len(set(fronts)) == TARGET and all(r.get("meaning") for r in rows) else "FAIL",
        "status": "candidate_only_not_promoted",
    }
    (AUDIT / f"{language}_top3000_candidate_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["structural_gate"] != "PASS":
        raise SystemExit(f"{language}: unable to build {TARGET} safe continuation rows")


def build_french(args) -> None:
    kaikki = fu.load_kaikki(Path(args.kaikki), fu.norm_fr)
    excluded = read_fronts(ROOT / "french_top1000.csv", fu.norm_fr)
    curated = v4.v3.v2.base.FRENCH_SAFE
    grouped: dict[str, dict] = {}
    with Path(args.lexique).open(encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            lemma = fu.norm_fr(row.get("4_Lemme", ""))
            cgram = (row.get("5_Cgram") or "").strip()
            if not lemma or lemma in excluded or not cgram or cgram.upper().startswith("NAM"):
                continue
            if len(fu.FRENCH_LETTER_RE.findall(lemma)) < 2 or lemma.endswith("'") or " " in lemma:
                continue
            freq = fu.to_float(row.get("10_FreqMot"))
            rec = grouped.setdefault(lemma, {"freq_by_cgram": defaultdict(float)})
            rec["freq_by_cgram"][cgram] += freq

    ranked, rejected = [], []
    for lemma, meta in grouped.items():
        k = kaikki.get(lemma)
        if not k:
            rejected.append({"front": lemma, "frequency": 0, "reason": "no_kaikki_entry"}); continue
        compatible_cgrams, compatible_poses, frequency = set(), set(), 0.0
        for cgram, freq in meta["freq_by_cgram"].items():
            hit = fu.cgram_to_kaikki(cgram) & set(k["poses"])
            if hit:
                compatible_cgrams.add(cgram); compatible_poses |= hit; frequency += freq
        if frequency <= 0:
            rejected.append({"front": lemma, "frequency": 0, "reason": "lexique_kaikki_pos_mismatch"}); continue
        glosses = []
        for p in sorted(compatible_poses):
            glosses.extend(k["by_pos"].get(p, []))
        dictionary_meaning = fu.compact_meaning(glosses) or fu.compact_meaning(k["all_glosses"])
        meaning = clean_meaning(curated.get(lemma) or dictionary_meaning)
        if not good_meaning(meaning):
            rejected.append({"front": lemma, "frequency": frequency, "reason": "no_safe_learner_meaning"}); continue
        ranked.append({
            "front": lemma, "meaning": meaning, "pos": fu.human_fr_pos(compatible_cgrams),
            "frequency": f"{frequency:.6f}", "lexique_cgram": "|".join(sorted(compatible_cgrams)),
            "kaikki_pos": "|".join(sorted(k["poses"])), "kaikki_meaning": dictionary_meaning,
            "source": "Lexique 4 compatible-POS lemma frequency + Kaikki/Wiktextract lexical semantics",
        })
    ranked.sort(key=lambda r: (-float(r["frequency"]), r["front"]))
    rows = []
    for r in ranked:
        if len(rows) >= TARGET: break
        item = dict(r); item["rank"] = START_RANK + len(rows); rows.append(item)
    write_outputs("french", rows, rejected)


def build_urdu(args) -> None:
    excluded = read_fronts(ROOT / "urdu_top1000.csv", fu.norm_ur)
    freq_text = Path(args.urdu_freq_text).read_text(encoding="utf-8", errors="replace")
    wn_text = fu.norm_ur(Path(args.urdu_wordnet_text).read_text(encoding="utf-8", errors="replace"))
    closed_text = fu.norm_ur(Path(args.urdu_closed_text).read_text(encoding="utf-8", errors="replace"))
    ranked = fu.extract_urdu_freq(freq_text)
    readurdu = fu.read_readurdu(Path(args.readurdu))
    kaikki = fu.load_kaikki(Path(args.kaikki), fu.norm_ur)
    curated = v4.v3.v2.base.URDU_SAFE
    rows, rejected = [], []
    for word, freq in ranked:
        if word in excluded:
            continue
        in_wn = fu.inventory_contains(wn_text, word)
        in_closed = fu.inventory_contains(closed_text, word)
        has_read = word in readurdu
        has_k = word in kaikki
        if not (in_wn or in_closed or (has_read and has_k)):
            rejected.append({"front": word, "frequency": freq, "reason": "insufficient_lexical_support"}); continue
        rmeaning = clean_meaning(readurdu.get(word, {}).get("meaning", "")) if has_read else ""
        kmeaning = fu.compact_meaning(kaikki.get(word, {}).get("all_glosses", [])) if has_k else ""
        meaning = clean_meaning(curated.get(word) or rmeaning or kmeaning)
        if not good_meaning(meaning):
            rejected.append({"front": word, "frequency": freq, "reason": "no_safe_learner_meaning"}); continue
        rows.append({
            "rank": START_RANK + len(rows), "front": word, "meaning": meaning,
            "pos": "|".join(sorted(kaikki.get(word, {}).get("poses", set()))) or ("closed-class" if in_closed else "content word"),
            "frequency": freq, "cle_wordnet": in_wn, "cle_closed_class": in_closed,
            "readurdu_entry": has_read, "readurdu_meaning": rmeaning, "kaikki_entry": has_k, "kaikki_meaning": kmeaning,
            "source": "CLE Urdu 5,000 corpus frequency list + CLE lexical inventories; ReadUrdu/Kaikki semantics",
        })
        if len(rows) >= TARGET: break
    write_outputs("urdu", rows, rejected)


def build_arabic(args) -> None:
    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.morphology.database import MorphologyDB
    excluded = {arprec.undiac(x) for x in read_fronts(ROOT / "arabic_top1000.csv")}
    analyzer = Analyzer(MorphologyDB.builtin_db("calima-msa-r13", flags="a"), backoff="NONE", cache_size=30000)
    with Path(args.arabic_candidates).open(encoding="utf-8", newline="") as f:
        broad = list(csv.DictReader(f))
    rows, rejected, seen = [], [], set()
    for r in broad:
        front = arprec.undiac(r.get("front", "")).strip()
        if not front or front in excluded or front in seen:
            continue
        pos = (r.get("pos") or "").strip()
        analyses = [a for a in analyzer.analyze(front) if arprec.exact_lexical_match(front, a) and str(a.get("pos", "")) == pos]
        analyses.sort(key=arprec.score, reverse=True)
        meaning = ""
        root = ""
        for a in analyses:
            candidate = clean_meaning(str(a.get("stemgloss", "")))
            if good_meaning(candidate):
                meaning = candidate
                root = arprec.root_to_arabic(str(a.get("root", "")), pos, __import__("camel_tools.utils.charmap", fromlist=["CharMapper"]).CharMapper.builtin_mapper("bw2ar"))
                break
        if not meaning:
            rejected.append({"front": front, "frequency": r.get("frequency", ""), "reason": "no_safe_exact_calima_stemgloss"}); continue
        seen.add(front)
        rows.append({
            "rank": START_RANK + len(rows), "front": front, "meaning": meaning,
            "pos": pos, "root": root, "frequency": r.get("frequency", ""),
            "calima_exact_analyses": len(analyses),
            "source": "CAMeL MSA frequency lists + CALIMA-MSA MLE lexical ranking; exact CALIMA stem semantics",
        })
        if len(rows) >= TARGET: break
    write_outputs("arabic", rows, rejected)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=["arabic", "french", "urdu"], required=True)
    ap.add_argument("--arabic-candidates")
    ap.add_argument("--lexique")
    ap.add_argument("--kaikki")
    ap.add_argument("--urdu-freq-text")
    ap.add_argument("--urdu-wordnet-text")
    ap.add_argument("--urdu-closed-text")
    ap.add_argument("--readurdu")
    args = ap.parse_args()
    if args.language == "arabic":
        if not args.arabic_candidates: raise SystemExit("--arabic-candidates required")
        build_arabic(args)
    elif args.language == "french":
        if not args.lexique or not args.kaikki: raise SystemExit("--lexique and --kaikki required")
        build_french(args)
    else:
        required = [args.kaikki, args.urdu_freq_text, args.urdu_wordnet_text, args.urdu_closed_text, args.readurdu]
        if not all(required): raise SystemExit("Urdu requires Kaikki, frequency, WordNet, closed-class, and ReadUrdu sources")
        build_urdu(args)


if __name__ == "__main__":
    main()
