#!/usr/bin/env python3
"""Independent semantic/POS fact checks for French and Urdu Top-1000 decks.

The script never edits learner decks. It triangulates existing English learner
meanings against English Wiktionary entries and Open Multilingual Wordnet where
available. Coverage gaps are reported as gaps, not errors. External service rate
limits are retried and, if exhausted, degrade to coverage gaps instead of aborting
an otherwise valid deck audit.
"""
from __future__ import annotations

import csv
import html
import json
import re
import time
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import wn

ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_RE = re.compile(r"(?m)^EN:\s*(.+?)\s*$")
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")
DEFINITION_RE = re.compile(r"(?m)^\(EN\)\s*(.+?)\s*$")
WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")
TEMPLATE_RE = re.compile(r"\{\{[^{}]*\}\}")
LINK_RE = re.compile(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]")
TAG_RE = re.compile(r"<[^>]+>")

STOP = {
    "a", "an", "the", "to", "of", "and", "or", "for", "as", "be", "is", "are",
    "was", "were", "with", "by", "from", "that", "which", "who", "whom", "this",
    "these", "those", "it", "he", "she", "they", "you", "i", "we", "one", "someone",
}
FUNCTION = {
    "in", "at", "on", "no", "not", "if", "from", "with", "about", "after", "before",
    "here", "there", "when", "where", "why", "how", "what", "who", "this", "that",
    "yes", "but", "all", "every", "some", "any", "than", "then", "also", "only",
    "until", "between", "among", "because", "without", "within", "outside", "and", "or",
}

CONFIG = {
    "french": {"file": "french_top1000.csv", "lang": "fr", "section": "French"},
    "urdu": {"file": "urdu_top1000.csv", "lang": "ur", "section": "Urdu"},
}


def tokens(text: str) -> set[str]:
    raw = {t for t in WORD_RE.findall((text or "").lower()) if len(t) > 1 and t not in STOP}
    out = set(raw)
    for t in list(raw):
        if len(t) > 4 and t.endswith("ies"): out.add(t[:-3] + "y")
        if len(t) > 4 and t.endswith("es"): out.add(t[:-2])
        if len(t) > 3 and t.endswith("s"): out.add(t[:-1])
        if len(t) > 5 and t.endswith("ing"): out.add(t[:-3])
        if len(t) > 4 and t.endswith("ed"): out.add(t[:-2])
    return out


def overlap(meaning: str, evidence: str):
    mt, et = tokens(meaning), tokens(evidence)
    if not mt or not et:
        return False, 0.0, ""
    hits = sorted(mt & et)
    if mt <= FUNCTION:
        score = len(hits) / max(1, len(mt))
        return bool(hits), score, ",".join(hits[:12])
    score = len(hits) / max(1, min(len(mt), 4))
    return score >= 0.25, score, ",".join(hits[:12])


def clean_wikitext(text: str) -> str:
    text = html.unescape(text or "")
    text = LINK_RE.sub(r"\1", text)
    for _ in range(5):
        text = TEMPLATE_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    text = re.sub(r"[^A-Za-z' -]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def section(raw: str, language: str) -> str:
    p = re.compile(rf"(?ms)^=={re.escape(language)}==\s*(.*?)(?=^==[^=]|\Z)")
    m = p.search(raw or "")
    return m.group(1) if m else ""


def fetch_wiki(titles: list[str]) -> dict[str, str]:
    endpoint = "https://en.wiktionary.org/w/api.php"
    found = {}
    batch_size = 20
    for start in range(0, len(titles), batch_size):
        batch = titles[start:start + batch_size]
        params = {
            "action": "query", "format": "json", "formatversion": "2", "prop": "revisions",
            "rvprop": "content", "rvslots": "main", "titles": "|".join(batch), "redirects": "1",
        }
        req = Request(endpoint + "?" + urlencode(params), headers={
            "User-Agent": "ualispublishing-learning-verifier/1.2 (educational lexical audit)"
        })
        data = None
        for attempt in range(6):
            try:
                with urlopen(req, timeout=45) as r:
                    data = json.load(r)
                break
            except HTTPError as exc:
                if exc.code != 429 and 500 > exc.code:
                    raise
                delay = min(60, 4 * (attempt + 1))
                print(f"Wiktionary batch {start}-{start+len(batch)-1} attempt {attempt+1}/6: HTTP {exc.code}; retrying in {delay}s")
                time.sleep(delay)
            except (URLError, TimeoutError) as exc:
                delay = min(60, 3 * (attempt + 1))
                print(f"Wiktionary batch {start}-{start+len(batch)-1} attempt {attempt+1}/6: {exc}; retrying in {delay}s")
                time.sleep(delay)
        if data is None:
            print(f"Wiktionary batch {start}-{start+len(batch)-1}: coverage unavailable after retries")
            continue
        for page in data.get("query", {}).get("pages", []):
            if page.get("missing"): continue
            revs = page.get("revisions") or []
            if not revs: continue
            content = revs[0].get("slots", {}).get("main", {}).get("content", "")
            found[page.get("title", "")] = content
        time.sleep(1.0)
    return found


def load_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"{path.name}: expected 1000 rows, found {len(rows)}")
    out = []
    for rank, row in enumerate(rows, 1):
        back = row.get("Back", "") or ""
        m = TRANSLATION_RE.search(back) or MEANING_RE.search(back)
        d = DEFINITION_RE.search(back)
        if not m:
            raise SystemExit(f"{path.name} rank {rank}: missing English learner meaning")
        meaning = m.group(1).strip()
        definition = d.group(1).strip() if d else ""
        out.append({"rank": rank, "front": row.get("Front", "").strip(), "meaning": meaning, "definition": definition})
    return out


def wordnet_for(lang: str):
    try:
        return wn.Wordnet(lang=lang)
    except Exception:
        return None


def wn_evidence(net, front: str, meaning: str):
    if net is None:
        return False, False, 0.0, "", 0
    try:
        syns = net.synsets(front)
    except Exception:
        return False, False, 0.0, "", 0
    if not syns:
        return False, False, 0.0, "", 0
    parts = []
    for syn in syns:
        definition = syn.definition()
        if definition: parts.append(definition)
        for lemma in syn.lemmas():
            parts.append(lemma)
    sem, score, hits = overlap(meaning, " ; ".join(parts))
    return True, sem, score, hits, len(syns)


def audit(name: str):
    cfg = CONFIG[name]
    rows = load_rows(ROOT / cfg["file"])
    wiki = fetch_wiki([r["front"] for r in rows])
    net = wordnet_for(cfg["lang"])
    details, counts = [], Counter()
    for row in rows:
        raw = wiki.get(row["front"], "")
        sec = section(raw, cfg["section"])
        wiki_exists = bool(raw)
        wiki_section = bool(sec)
        wikisem, wscore, whits = overlap(row["meaning"], clean_wikitext(sec)) if sec else (False, 0.0, "")
        wn_exists, wnsem, nscore, nhits, nsyn = wn_evidence(net, row["front"], row["meaning"])
        sem_sources = int(wikisem) + int(wnsem)
        structural = int(wiki_section) + int(wn_exists)
        if sem_sources == 2: status = "strong_confirm"
        elif sem_sources == 1: status = "confirm"
        elif structural: status = "review_semantics"
        else: status = "no_external_coverage"
        counts[status] += 1
        details.append({
            "rank": row["rank"], "front": row["front"], "english_translation": row["meaning"], "status": status,
            "wiktionary_page": int(wiki_exists), "wiktionary_language_section": int(wiki_section),
            "wiktionary_semantic_support": int(wikisem), "wiktionary_score": f"{wscore:.3f}", "wiktionary_hits": whits,
            "omw_entry": int(wn_exists), "omw_synsets": nsyn, "omw_semantic_support": int(wnsem),
            "omw_score": f"{nscore:.3f}", "omw_hits": nhits,
        })
    detail_path = ROOT / "audit" / f"{name}_top1000_external_verification.csv"
    summary_path = ROOT / "audit" / f"{name}_top1000_external_verification_summary.json"
    with detail_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(details[0])); w.writeheader(); w.writerows(details)
    summary = {
        "deck": cfg["file"], "rows_checked": 1000,
        "status_counts": dict(sorted(counts.items())),
        "wiktionary_language_sections": sum(d["wiktionary_language_section"] for d in details),
        "wiktionary_semantic_support": sum(d["wiktionary_semantic_support"] for d in details),
        "omw_entries": sum(d["omw_entry"] for d in details),
        "omw_semantic_support": sum(d["omw_semantic_support"] for d in details),
        "rows_with_any_external_semantic_support": sum(d["status"] in {"strong_confirm", "confirm"} for d in details),
        "rows_requiring_review": sum(d["status"] == "review_semantics" for d in details),
        "rows_without_external_coverage": sum(d["status"] == "no_external_coverage" for d in details),
        "policy": [
            "External sources confirm or flag; they never overwrite learner cards automatically.",
            "Coverage gaps, including exhausted external-service rate limits, are not treated as lexical errors.",
            "Rank/order remains untouched.",
        ],
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(name, json.dumps(summary, ensure_ascii=False))


def main():
    ROOT.joinpath("audit").mkdir(exist_ok=True)
    try:
        wn.download("omw:1.4")
    except Exception as exc:
        print("OMW download note:", exc)
    for name in ("french", "urdu"):
        audit(name)


if __name__ == "__main__":
    main()
