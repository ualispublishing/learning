#!/usr/bin/env python3
"""Cross-source fact check for arabic_top1000.csv.

This verifier is deliberately read-only with respect to the learner deck. It uses
independent/public lexical sources to CONFIRM or FLAG reviewed meanings; it never
rewrites a card automatically.

Sources:
- Arabic WordNet (AWN v2) through Open Multilingual Wordnet / Wn
- Open English WordNet through shared Interlingual Index links
- English Wiktionary through the MediaWiki Action API

CALIMA-MSA remains the morphology validator in the separate learner-safety audit.
Qabas/Sina can be added as a fourth source when an API key is available.
"""
from __future__ import annotations

import csv
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
DETAIL = ROOT / "audit" / "arabic_top1000_external_verification.csv"
SUMMARY = ROOT / "audit" / "arabic_top1000_external_verification_summary.json"

DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")
POS_RE = re.compile(r"(?m)^Part of speech:\s*(.+?)\s*$")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
AR_SECTION_RE = re.compile(r"(?ms)^==Arabic==\s*(.*?)(?=^==[^=]|\Z)")
HEADING_RE = re.compile(r"(?m)^===+\s*([^=\n]+?)\s*===+\s*$")
TEMPLATE_RE = re.compile(r"\{\{[^{}]*\}\}")
TAG_RE = re.compile(r"<[^>]+>")
LINK_RE = re.compile(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]")
WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")

STOP = {
    "a", "an", "the", "to", "of", "and", "or", "for", "as", "be", "is", "are",
    "was", "were", "with", "by", "from", "that", "which", "who", "whom", "this",
    "these", "those", "it", "he", "she", "they", "you", "i", "we", "depending",
    "context", "form", "particle", "singular", "plural", "masculine", "feminine",
}

# Short function-word meanings need exact-token support and cannot use the same
# overlap threshold as content words.
FUNCTION_TOKENS = {
    "in", "at", "on", "upon", "over", "no", "not", "if", "indeed", "from", "with",
    "about", "after", "before", "here", "there", "when", "where", "why", "how", "what",
    "who", "whom", "whose", "this", "that", "these", "those", "yes", "but", "however",
    "all", "every", "each", "some", "any", "than", "then", "also", "only", "until",
    "toward", "towards", "between", "among", "because", "without", "within", "outside",
}

POS_HEADINGS = {
    "noun": {"noun", "proper noun"},
    "verb": {"verb"},
    "adjective": {"adjective"},
    "adverb": {"adverb"},
    "pronoun": {"pronoun", "demonstrative pronoun", "relative pronoun"},
    "preposition": {"preposition"},
    "postposition": {"postposition"},
    "conjunction": {"conjunction"},
    "particle": {"particle", "interjection", "conjunction", "preposition"},
    "interjection": {"interjection"},
    "numeral": {"numeral", "number"},
}


def undiac(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "").replace("ـ", "")
    return DIAC.sub("", text).strip()


def en_tokens(text: str) -> set[str]:
    toks = {t for t in WORD_RE.findall((text or "").lower()) if t not in STOP and len(t) > 1}
    # light normalization for common inflections
    out = set(toks)
    for t in list(toks):
        if len(t) > 4 and t.endswith("ies"):
            out.add(t[:-3] + "y")
        if len(t) > 4 and t.endswith("es"):
            out.add(t[:-2])
        if len(t) > 3 and t.endswith("s"):
            out.add(t[:-1])
        if len(t) > 5 and t.endswith("ing"):
            out.add(t[:-3])
        if len(t) > 4 and t.endswith("ed"):
            out.add(t[:-2])
    return out


def clean_wikitext(text: str) -> str:
    text = html.unescape(text or "")
    text = LINK_RE.sub(r"\1", text)
    # several passes remove many simple templates without pretending to fully parse Wiktionary
    for _ in range(4):
        text = TEMPLATE_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    text = re.sub(r"\{\||\|\}", " ", text)
    text = re.sub(r"[^A-Za-z' -]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def semantic_overlap(meaning: str, evidence: str) -> tuple[bool, float, str]:
    mt = en_tokens(meaning)
    et = en_tokens(evidence)
    if not mt or not et:
        return False, 0.0, ""
    hits = sorted(mt & et)
    # Function words are often one-word glosses. Exact support is meaningful there.
    if mt <= FUNCTION_TOKENS:
        score = len(hits) / max(1, len(mt))
        return bool(hits), score, ",".join(hits[:12])
    score = len(hits) / max(1, min(len(mt), 4))
    return score >= 0.25, score, ",".join(hits[:12])


def parse_rows() -> list[dict]:
    with DECK.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for i, row in enumerate(rows, 1):
        back = row.get("Back", "") or ""
        rankm, mm, pm = RANK_RE.search(back), MEANING_RE.search(back), POS_RE.search(back)
        if not rankm or int(rankm.group(1)) != i or not mm or not pm:
            raise SystemExit(f"Malformed learner deck at rank {i}")
        out.append({"rank": i, "front": undiac(row["Front"]), "meaning": mm.group(1).strip(), "pos": pm.group(1).strip()})
    if len(out) != 1000:
        raise SystemExit(f"Expected 1000 rows, found {len(out)}")
    return out


def fetch_wiktionary(titles: list[str]) -> dict[str, str]:
    endpoint = "https://en.wiktionary.org/w/api.php"
    found: dict[str, str] = {}
    # anonymous API limit is 50 titles/request; be deliberately polite
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        params = {
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "revisions", "rvprop": "content", "rvslots": "main",
            "titles": "|".join(batch), "redirects": "1",
        }
        req = Request(endpoint + "?" + urlencode(params), headers={"User-Agent": "ualispublishing-learning-verifier/1.0 (educational lexical audit)"})
        with urlopen(req, timeout=45) as r:
            data = json.load(r)
        for page in data.get("query", {}).get("pages", []):
            if page.get("missing"):
                continue
            revs = page.get("revisions") or []
            if not revs:
                continue
            content = revs[0].get("slots", {}).get("main", {}).get("content", "")
            found[undiac(page.get("title", ""))] = content
        time.sleep(0.15)
    return found


def canonical_pos(pos: str) -> set[str]:
    p = pos.lower()
    result = set()
    for key in POS_HEADINGS:
        if key in p:
            result.add(key)
    # common deck shorthand / compound labels
    if "relative" in p or "demonstrative" in p:
        result.add("pronoun")
    if not result:
        if "adj" in p: result.add("adjective")
        if "adv" in p: result.add("adverb")
        if "prep" in p: result.add("preposition")
        if "conj" in p: result.add("conjunction")
    return result


def wiktionary_evidence(raw: str, pos: str, meaning: str) -> dict:
    if not raw:
        return {"exists": False, "arabic_section": False, "pos_support": False, "semantic_support": False, "score": 0.0, "hits": ""}
    m = AR_SECTION_RE.search(raw)
    if not m:
        return {"exists": True, "arabic_section": False, "pos_support": False, "semantic_support": False, "score": 0.0, "hits": ""}
    section = m.group(1)
    headings = {h.strip().lower() for h in HEADING_RE.findall(section)}
    expected = canonical_pos(pos)
    allowed = set().union(*(POS_HEADINGS.get(p, {p}) for p in expected)) if expected else set()
    pos_support = not expected or bool(headings & allowed)
    clean = clean_wikitext(section)
    sem, score, hits = semantic_overlap(meaning, clean)
    return {"exists": True, "arabic_section": True, "pos_support": pos_support, "semantic_support": sem, "score": score, "hits": hits}


def build_awn_index():
    arb = wn.Wordnet("omw-arb:2.0")
    eng = wn.Wordnet("oewn:2025")
    idx = defaultdict(list)
    for word in arb.words():
        form = undiac(word.lemma())
        if form:
            idx[form].extend(word.synsets())
    # dedupe synsets per spelling
    for k, syns in list(idx.items()):
        seen = set(); uniq = []
        for s in syns:
            if s.id not in seen:
                seen.add(s.id); uniq.append(s)
        idx[k] = uniq
    return idx, eng


def awn_evidence(front: str, meaning: str, pos: str, idx, eng) -> dict:
    syns = idx.get(front, [])
    if not syns:
        return {"exists": False, "pos_support": False, "semantic_support": False, "score": 0.0, "hits": "", "synsets": 0}
    expected = canonical_pos(pos)
    wn_pos_map = {"noun": "n", "verb": "v", "adjective": "a", "adverb": "r"}
    expected_wn = {wn_pos_map[p] for p in expected if p in wn_pos_map}
    pos_support = not expected_wn or any(s.pos in expected_wn or (s.pos == "s" and "a" in expected_wn) for s in syns)
    evidence_parts = []
    for syn in syns:
        if syn.definition(): evidence_parts.append(syn.definition() or "")
        if syn.ili:
            for es in eng.synsets(ili=syn.ili):
                evidence_parts.extend(es.lemmas())
                if es.definition(): evidence_parts.append(es.definition() or "")
    evidence = " ; ".join(evidence_parts)
    sem, score, hits = semantic_overlap(meaning, evidence)
    return {"exists": True, "pos_support": pos_support, "semantic_support": sem, "score": score, "hits": hits, "synsets": len(syns)}


def classify(wk: dict, awn: dict) -> str:
    semantic_sources = int(wk["semantic_support"]) + int(awn["semantic_support"])
    structural_sources = int(wk["arabic_section"]) + int(awn["exists"])
    if semantic_sources == 2:
        return "strong_confirm"
    if semantic_sources == 1:
        return "confirm"
    if structural_sources >= 1:
        return "review_semantics"
    return "no_external_coverage"


def main() -> None:
    rows = parse_rows()
    print("Downloading/loading wordnets...")
    # wn.download is idempotent and will skip installed data in the runner cache/db.
    for spec in ("omw-arb:2.0", "oewn:2025"):
        try:
            wn.download(spec)
        except Exception as exc:
            # If already installed or index state differs, construction below is authoritative.
            print(f"wn.download({spec!r}) note: {exc}")
    awn_idx, eng = build_awn_index()
    print(f"Arabic WordNet normalized spellings indexed: {len(awn_idx)}")

    print("Fetching English Wiktionary pages in API batches...")
    wiki = fetch_wiktionary([r["front"] for r in rows])
    print(f"Wiktionary pages fetched: {len(wiki)}")

    details = []
    counts = Counter()
    for row in rows:
        wk = wiktionary_evidence(wiki.get(row["front"], ""), row["pos"], row["meaning"])
        awn = awn_evidence(row["front"], row["meaning"], row["pos"], awn_idx, eng)
        status = classify(wk, awn)
        counts[status] += 1
        details.append({
            "rank": row["rank"], "front": row["front"], "meaning": row["meaning"], "part_of_speech": row["pos"],
            "status": status,
            "wiktionary_page": int(wk["exists"]), "wiktionary_arabic_section": int(wk["arabic_section"]),
            "wiktionary_pos_support": int(wk["pos_support"]), "wiktionary_semantic_support": int(wk["semantic_support"]),
            "wiktionary_score": f"{wk['score']:.3f}", "wiktionary_hits": wk["hits"],
            "awn_entry": int(awn["exists"]), "awn_synsets": awn["synsets"], "awn_pos_support": int(awn["pos_support"]),
            "awn_semantic_support": int(awn["semantic_support"]), "awn_score": f"{awn['score']:.3f}", "awn_hits": awn["hits"],
        })

    DETAIL.parent.mkdir(parents=True, exist_ok=True)
    with DETAIL.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(details[0]))
        writer.writeheader(); writer.writerows(details)

    summary = {
        "deck": "arabic_top1000.csv",
        "rows_checked": len(rows),
        "method": "Reviewed learner meanings are cross-checked, never auto-replaced.",
        "sources": {
            "calima_msa": "separate learner-safety audit: morphology/root validation",
            "arabic_wordnet": "Open Multilingual Wordnet Arabic WordNet v2, mapped through ILI to Open English WordNet 2025",
            "wiktionary": "English Wiktionary, MediaWiki Action API, Arabic-language entry section",
            "qabas": "recommended fourth source; REST requires a Sina/Birzeit API key and is not counted in this run",
        },
        "status_counts": dict(sorted(counts.items())),
        "wiktionary_pages": sum(d["wiktionary_page"] for d in details),
        "wiktionary_semantic_support": sum(d["wiktionary_semantic_support"] for d in details),
        "awn_entries": sum(d["awn_entry"] for d in details),
        "awn_semantic_support": sum(d["awn_semantic_support"] for d in details),
        "rows_with_any_external_semantic_support": sum(d["status"] in {"strong_confirm", "confirm"} for d in details),
        "rows_requiring_human_followup": sum(d["status"] == "review_semantics" for d in details),
        "rows_without_external_coverage": sum(d["status"] == "no_external_coverage" for d in details),
        "policy": [
            "No external source can overwrite the learner deck automatically.",
            "A missing WordNet entry is not treated as an error because WordNet is content-word oriented.",
            "Wiktionary and WordNet agreement strengthens confidence; disagreement/coverage gaps are routed to review.",
            "The 1,000 rank/order and learner-facing meanings remain unchanged by this verifier.",
        ],
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
