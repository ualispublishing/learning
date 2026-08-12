#!/usr/bin/env python3
"""Third-pass independent semantic verification for arabic_top1000.csv.

This verifier does not rewrite learner cards. It triangulates every Arabic front
and its explicit English learner meaning against:
  1) Arabic WordNet v2 (OMW 2.0),
  2) Arabic WordNet 4.x aligned to Open English WordNet 2024,
  3) the Arabic section of English Wiktionary.

CALIMA remains the morphology source in the deck; this script is deliberately
independent of the deck-building semantic tables. Any disagreement is emitted
for human review rather than silently "fixed".
"""
from __future__ import annotations

import csv
import gzip
import html
import json
import re
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import wn

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "arabic_top1000.csv"
AUDIT = ROOT / "audit"
DETAIL = AUDIT / "arabic_top1000_external_precision.csv"
SUMMARY = AUDIT / "arabic_top1000_external_precision_summary.json"
REVIEW = AUDIT / "arabic_top1000_external_precision_review.csv"
AWN4_GZ = ROOT / "audit" / "awn4.xml.gz"

MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")
POS_RE = re.compile(r"(?m)^Part of speech:\s*(.+?)\s*$")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")
LINK_RE = re.compile(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]")
TEMPLATE_RE = re.compile(r"\{\{[^{}]*\}\}")
TAG_RE = re.compile(r"<[^>]+>")

STOP = {
    "a", "an", "the", "to", "of", "and", "or", "for", "as", "be", "is", "are",
    "was", "were", "with", "by", "from", "that", "which", "who", "whom", "this",
    "these", "those", "it", "he", "she", "they", "you", "i", "we", "one", "someone",
    "something", "person", "thing", "used", "form", "depending", "vocalization",
}
FUNCTION_POS_HINTS = {
    "preposition", "particle", "pronoun", "demonstrative", "conjunction", "interrogative",
    "relative", "vocative", "negation", "subordinator", "conditional", "quantifier",
}


def norm_ar(text: str) -> str:
    x = unicodedata.normalize("NFC", text or "").replace("ـ", "")
    x = DIAC.sub("", x)
    # Normalize alef/hamza variants only for lookup; preserve original deck fronts.
    return x.replace("ٱ", "ا").strip()


def en_tokens(text: str) -> set[str]:
    raw = {t for t in WORD_RE.findall((text or "").lower()) if len(t) > 1 and t not in STOP}
    out = set(raw)
    for t in list(raw):
        if len(t) > 4 and t.endswith("ies"): out.add(t[:-3] + "y")
        if len(t) > 4 and t.endswith("es"): out.add(t[:-2])
        if len(t) > 3 and t.endswith("s"): out.add(t[:-1])
        if len(t) > 5 and t.endswith("ing"): out.add(t[:-3])
        if len(t) > 4 and t.endswith("ed"): out.add(t[:-2])
    return out


def semantic_overlap(meaning: str, evidence: str):
    mt, et = en_tokens(meaning), en_tokens(evidence)
    if not mt or not et:
        return False, 0.0, ""
    hits = sorted(mt & et)
    # Conservative: one substantive shared content word is evidence, not proof.
    score = len(hits) / max(1, min(4, len(mt)))
    return bool(hits), score, ",".join(hits[:16])


def wiki_clean(text: str) -> str:
    text = html.unescape(text or "")
    text = LINK_RE.sub(r"\1", text)
    for _ in range(6):
        text = TEMPLATE_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    text = re.sub(r"[^A-Za-z' -]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def arabic_section(raw: str) -> str:
    m = re.search(r"(?ms)^==Arabic==\s*(.*?)(?=^==[^=]|\Z)", raw or "")
    return m.group(1) if m else ""


def wiki_definition_evidence(section: str) -> str:
    # Restrict evidence to definition lines (# ...) and POS headings. This avoids
    # false semantic support from etymology/category boilerplate.
    lines = []
    for line in (section or "").splitlines():
        s = line.strip()
        if s.startswith("#") and not s.startswith(("#*", "#:", "##")):
            lines.append(s.lstrip("# "))
    return wiki_clean("\n".join(lines))


def fetch_wiktionary(fronts: list[str]) -> dict[str, str]:
    endpoint = "https://en.wiktionary.org/w/api.php"
    found: dict[str, str] = {}
    for start in range(0, len(fronts), 50):
        batch = fronts[start:start + 50]
        params = {
            "action": "query", "format": "json", "formatversion": "2", "prop": "revisions",
            "rvprop": "content", "rvslots": "main", "titles": "|".join(batch), "redirects": "1",
        }
        req = Request(endpoint + "?" + urlencode(params), headers={
            "User-Agent": "ualispublishing-learning-arabic-audit/2.0 (educational lexical verification)"
        })
        try:
            with urlopen(req, timeout=45) as r:
                data = json.load(r)
        except Exception as exc:
            print(f"Wiktionary batch {start}: {exc}")
            continue
        for page in data.get("query", {}).get("pages", []):
            if page.get("missing"): continue
            revs = page.get("revisions") or []
            if not revs: continue
            content = revs[0].get("slots", {}).get("main", {}).get("content", "")
            found[page.get("title", "")] = content
        time.sleep(0.12)
    return found


def load_deck():
    with DECK.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"Expected 1000 rows, found {len(rows)}")
    out = []
    for rank, row in enumerate(rows, 1):
        front = (row.get("Front") or "").strip()
        back = row.get("Back") or ""
        mm, pm, rm = MEANING_RE.search(back), POS_RE.search(back), RANK_RE.search(back)
        if not mm or not pm or not rm:
            raise SystemExit(f"rank {rank}: missing Meaning/POS/Rank metadata")
        if int(rm.group(1)) != rank:
            raise SystemExit(f"rank {rank}: embedded rank is {rm.group(1)}")
        out.append({
            "rank": rank,
            "front": front,
            "norm": norm_ar(front),
            "meaning": mm.group(1).strip(),
            "pos": pm.group(1).strip(),
        })
    return out


def pos_family(card_pos: str) -> set[str]:
    p = card_pos.lower()
    fam = set()
    if "verb" in p: fam.add("v")
    if "noun" in p: fam.add("n")
    if "adjective" in p: fam.update({"a", "s"})
    if "adverb" in p: fam.add("r")
    return fam


def is_function(card_pos: str) -> bool:
    p = card_pos.lower()
    return any(h in p for h in FUNCTION_POS_HINTS) and not pos_family(card_pos)


def build_wn_index(net, target_norms: set[str]):
    index = defaultdict(list)
    for word in net.words():
        key = norm_ar(word.lemma())
        if key not in target_norms:
            continue
        for sense in word.senses():
            syn = sense.synset()
            index[key].append(syn)
    # de-duplicate by synset id
    for key in list(index):
        uniq = {}
        for syn in index[key]: uniq[syn.id] = syn
        index[key] = list(uniq.values())
    return index


def english_evidence(synsets, english_net):
    parts = []
    pos = set()
    ilis = set()
    for syn in synsets:
        pos.add(syn.pos)
        if syn.ili:
            ilis.add(syn.ili)
            for ens in english_net.synsets(ili=syn.ili):
                parts.extend(ens.lemmas())
                d = ens.definition()
                if d: parts.append(d)
    return " ; ".join(parts), pos, len(ilis)


def main():
    AUDIT.mkdir(exist_ok=True)
    rows = load_deck()
    targets = {r["norm"] for r in rows}

    # Two independently constructed Arabic wordnets + OEWN for aligned English semantics.
    wn.download("omw-arb:2.0")
    wn.download("oewn:2024")
    if not AWN4_GZ.exists():
        raise SystemExit("AWN4 file missing: workflow must download audit/awn4.xml.gz")
    try:
        wn.add(str(AWN4_GZ))
    except Exception as exc:
        # wn.add is persistent and may report an already-installed lexicon.
        print("AWN4 add note:", exc)

    awn2 = wn.Wordnet("omw-arb:2.0", expand="")
    awn4 = wn.Wordnet("awn4:4.0", expand="")
    eng = wn.Wordnet("oewn:2024")
    idx2 = build_wn_index(awn2, targets)
    idx4 = build_wn_index(awn4, targets)

    wiki_raw = fetch_wiktionary([r["front"] for r in rows])
    details = []
    counts = Counter()

    for r in rows:
        norm = r["norm"]
        syn2, syn4 = idx2.get(norm, []), idx4.get(norm, [])
        ev2, pos2, ili2 = english_evidence(syn2, eng)
        ev4, pos4, ili4 = english_evidence(syn4, eng)
        s2, score2, hits2 = semantic_overlap(r["meaning"], ev2)
        s4, score4, hits4 = semantic_overlap(r["meaning"], ev4)

        raw = wiki_raw.get(r["front"], "")
        sec = arabic_section(raw)
        wev = wiki_definition_evidence(sec)
        sw, scorew, hitsw = semantic_overlap(r["meaning"], wev)

        fam = pos_family(r["pos"])
        pos2_ok = not fam or not pos2 or bool(fam & pos2)
        pos4_ok = not fam or not pos4 or bool(fam & pos4)

        semantic_sources = int(s2) + int(s4) + int(sw)
        structural_sources = int(bool(syn2)) + int(bool(syn4)) + int(bool(sec))
        pos_disagreements = int(not pos2_ok) + int(not pos4_ok)

        # A row is flagged only on actual contradictory evidence, not mere coverage gaps.
        if pos_disagreements >= 2:
            status = "review_pos"
        elif structural_sources >= 2 and semantic_sources == 0 and not is_function(r["pos"]):
            status = "review_semantics"
        elif semantic_sources >= 2:
            status = "strong_confirm"
        elif semantic_sources == 1:
            status = "confirm"
        elif structural_sources:
            status = "structural_only"
        else:
            status = "no_external_coverage"
        counts[status] += 1

        details.append({
            "rank": r["rank"], "front": r["front"], "meaning": r["meaning"], "card_pos": r["pos"],
            "status": status,
            "awn2_entry": int(bool(syn2)), "awn2_synsets": len(syn2), "awn2_ilis": ili2,
            "awn2_pos": ",".join(sorted(pos2)), "awn2_semantic_support": int(s2),
            "awn2_score": f"{score2:.3f}", "awn2_hits": hits2,
            "awn4_entry": int(bool(syn4)), "awn4_synsets": len(syn4), "awn4_ilis": ili4,
            "awn4_pos": ",".join(sorted(pos4)), "awn4_semantic_support": int(s4),
            "awn4_score": f"{score4:.3f}", "awn4_hits": hits4,
            "wiktionary_arabic_section": int(bool(sec)), "wiktionary_semantic_support": int(sw),
            "wiktionary_score": f"{scorew:.3f}", "wiktionary_hits": hitsw,
            "pos_disagreements": pos_disagreements,
        })

    fields = list(details[0])
    with DETAIL.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(details)
    review_rows = [d for d in details if d["status"].startswith("review_")]
    with REVIEW.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(review_rows)

    summary = {
        "deck": "arabic_top1000.csv",
        "rows_checked": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "awn2_entries": sum(d["awn2_entry"] for d in details),
        "awn2_semantic_support": sum(d["awn2_semantic_support"] for d in details),
        "awn4_entries": sum(d["awn4_entry"] for d in details),
        "awn4_semantic_support": sum(d["awn4_semantic_support"] for d in details),
        "wiktionary_arabic_sections": sum(d["wiktionary_arabic_section"] for d in details),
        "wiktionary_semantic_support": sum(d["wiktionary_semantic_support"] for d in details),
        "rows_with_2plus_semantic_sources": sum((d["awn2_semantic_support"] + d["awn4_semantic_support"] + d["wiktionary_semantic_support"]) >= 2 for d in details),
        "review_rows": len(review_rows),
        "review_ranks": [d["rank"] for d in review_rows],
        "policy": [
            "External sources only confirm or flag; they never overwrite learner meanings.",
            "Coverage gaps are not counted as errors.",
            "A semantic review flag requires at least two structural sources but zero semantic support for an open-class item.",
            "A POS review flag requires both Arabic WordNets to contradict the card's open-class POS family.",
            "All flagged rows require explicit human resolution before claiming this pass clean.",
        ],
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
