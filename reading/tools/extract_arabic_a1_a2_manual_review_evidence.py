#!/usr/bin/env python3
import json
import re
import subprocess
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A1 = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
A2 = ROOT / "reading" / "arabic" / "a2" / "passages.jsonl"
SOURCE = ROOT / "reading" / "audit" / "arabic_a1_a2_diagnostic_adjudication_2026-08-23.json"
OUTPUT = ROOT / "reading" / "audit" / "arabic_a1_a2_manual_review_evidence_2026-08-23.json"
EXPECTED = {
    "a1": "4723cb4c9974a9a9c84b6c030d9c1a30c0820500",
    "a2": "d6a10dddde14628c8e4a7ddb4db7781604852210",
}

DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
WORD_RE = re.compile(r"[\u0621-\u064A]+")
SENTENCE_SPLIT = re.compile(r"(?<=[.؟!۔])\s+")
PROCLITICS = ("و", "ف", "ب", "ك", "ل")
SUFFIXES = ("هما", "هم", "هن", "كما", "كم", "كن", "نا", "ها", "ه", "ك", "ي", "ات", "ون", "ين", "ان", "وا", "تم", "تن", "ت", "ن", "ا")
PREFIXES = ("أ", "ا", "ن", "ي", "ت")


def blob(path):
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def norm(s):
    s = unicodedata.normalize("NFKC", str(s or "")).replace("ـ", "")
    s = DIACRITICS.sub("", s).replace("ٱ", "ا")
    return s


def word_tokens(s):
    return WORD_RE.findall(norm(s))


def strip_variants(token):
    out = {token}
    frontier = {token}
    for _ in range(2):
        nxt = set()
        for x in frontier:
            for p in PROCLITICS:
                if x.startswith(p) and len(x) - len(p) >= 2:
                    nxt.add(x[len(p):])
            if x.startswith("ال") and len(x) > 4:
                nxt.add(x[2:])
        out |= nxt
        frontier = nxt
    expanded = set(out)
    for x in list(out):
        for suf in SUFFIXES:
            if x.endswith(suf) and len(x) - len(suf) >= 2:
                expanded.add(x[:-len(suf)])
        if len(x) >= 4 and x[0] in PREFIXES:
            expanded.add(x[1:])
    return {x for x in expanded if len(x) >= 2}


def shared_shape(a, b):
    aa = strip_variants(a)
    bb = strip_variants(b)
    direct = aa & bb
    if direct:
        return 100, sorted(direct)
    best = 0
    common_best = []
    for x in aa:
        for y in bb:
            common = "".join(ch for ch in x if ch in set(y))
            # conservative ranking only; never used to auto-resolve
            score = int(100 * (2 * len(set(x) & set(y))) / max(1, len(set(x)) + len(set(y))))
            if score > best:
                best = score
                common_best = [x, y, common]
    return best, common_best


def sentences(text):
    parts = [x.strip() for x in SENTENCE_SPLIT.split(str(text or "")) if x.strip()]
    return parts or [str(text or "")]


def target_index(rows):
    meta = {}
    intro = {}
    for row in rows:
        for t in row.get("new_lexical_targets", []):
            if isinstance(t, dict) and t.get("id"):
                meta.setdefault(t["id"], t)
                intro.setdefault(t["id"], {
                    "passage_id": row.get("id"),
                    "sequence": row.get("sequence"),
                    "unit": row.get("unit"),
                    "form": t.get("form"),
                    "lemma": t.get("lemma"),
                    "part_of_speech": t.get("part_of_speech"),
                    "intended_sense": t.get("intended_sense"),
                    "source_rank": t.get("source_rank"),
                })
    return meta, intro


def q_and_a(row, qid):
    q = next((q for q in row.get("questions", []) if q.get("id") == qid), None)
    a = next((a for a in row.get("answer_key", []) if a.get("question_id") == qid), None)
    return q, a


def local_targets(row):
    return {
        "new": [t for t in row.get("new_lexical_targets", []) if isinstance(t, dict)],
        "review": [t for t in row.get("review_lexical_targets", []) if isinstance(t, dict)],
    }


def candidate_evidence(text, form, max_tokens=12):
    form_n = norm(form)
    all_tokens = word_tokens(text)
    ranked = []
    seen = set()
    for tok in all_tokens:
        if tok in seen:
            continue
        seen.add(tok)
        score, shape = shared_shape(tok, form_n)
        if score >= 45:
            ranked.append({"token": tok, "score": score, "shared_shape": shape})
    ranked.sort(key=lambda x: (-x["score"], x["token"]))
    ranked = ranked[:max_tokens]
    candidate_set = {x["token"] for x in ranked}
    sentence_hits = []
    for sent in sentences(text):
        toks = set(word_tokens(sent))
        hits = sorted(toks & candidate_set)
        if hits:
            sentence_hits.append({"sentence": sent, "candidate_tokens": hits})
    return ranked, sentence_hits


def main():
    actual = {"a1": blob(A1), "a2": blob(A2)}
    if actual != EXPECTED:
        raise SystemExit(f"Unexpected corpus blobs: {actual}")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if source.get("unresolved_count") != 107:
        raise SystemExit(f"Expected 107 unresolved diagnostics, got {source.get('unresolved_count')}")

    levels = {"a1": load_jsonl(A1), "a2": load_jsonl(A2)}
    by_id = {level: {r["id"]: r for r in rows} for level, rows in levels.items()}
    meta = {}
    intro = {}
    for level, rows in levels.items():
        meta[level], intro[level] = target_index(rows)

    packet = []
    counts = defaultdict(int)
    for idx, unresolved in enumerate(source.get("unresolved", []), start=1):
        warning = unresolved.get("warning", {})
        pid = warning.get("passage_id")
        level = unresolved.get("level") or ("a1" if "-a1-" in str(pid) else "a2")
        row = by_id[level].get(pid)
        if row is None:
            raise SystemExit(f"Missing passage {pid}")
        tid = warning.get("target_id")
        tmeta = meta[level].get(tid, {})
        form = str(warning.get("form") or tmeta.get("form") or tmeta.get("lemma") or "")
        candidates, sentence_hits = candidate_evidence(row.get("text", ""), form)
        qid = warning.get("question_id")
        q, a = q_and_a(row, qid) if qid else (None, None)
        local = local_targets(row)
        item = {
            "review_id": f"AR12-{idx:03d}",
            "classification": unresolved.get("classification"),
            "warning_code": warning.get("code"),
            "level": level,
            "passage_id": pid,
            "unit": row.get("unit"),
            "sequence": row.get("sequence"),
            "title": row.get("title"),
            "target_id": tid,
            "target_form": form,
            "target_metadata": {
                "lemma": tmeta.get("lemma"),
                "part_of_speech": tmeta.get("part_of_speech"),
                "intended_sense": tmeta.get("intended_sense"),
                "source_rank": tmeta.get("source_rank"),
                "declared_exposures_in_text": tmeta.get("exposures_in_text"),
            },
            "introduction": intro[level].get(tid),
            "warning": warning,
            "full_text": row.get("text"),
            "surface_candidate_tokens": candidates,
            "candidate_sentence_hits": sentence_hits,
            "question_evidence": None if not qid else {
                "question": q,
                "answer": a,
                "target_id_is_locally_declared": tid in {t.get("id") for t in local["new"] + local["review"]},
                "local_new_targets": [{"id": t.get("id"), "form": t.get("form"), "lemma": t.get("lemma")} for t in local["new"]],
                "local_review_targets": [{"id": t.get("id"), "form": t.get("form"), "review_stage": t.get("review_stage"), "representation": t.get("representation")} for t in local["review"]],
            },
            "adjudication": {
                "status": "pending_manual_review",
                "decision": None,
                "evidence": None,
                "learner_text_change_required": None,
                "metadata_change_required": None,
            },
        }
        counts[item["classification"]] += 1
        packet.append(item)

    output = {
        "schema_version": 1,
        "date": "2026-08-23",
        "scope": "Arabic A1+A2 unresolved diagnostic manual-review evidence packet",
        "input_blobs": actual,
        "source_unresolved_count": source.get("unresolved_count"),
        "packet_count": len(packet),
        "classification_counts": dict(counts),
        "review_policy": [
            "Do not rewrite natural Arabic merely to create exact lemma-form surface matches.",
            "Resolve an inflection only when the sentence and target POS/sense support that exact lexical realization.",
            "For question-target linkage gaps, keep the target ID only when the question genuinely assesses that target; otherwise remove the incidental target ID.",
            "If a target is genuinely scheduled for review in a passage, add/repair review metadata only with a defensible review stage and representation.",
            "Exposure-count changes are metadata-only unless the learner text truly fails to realize the intended target sense.",
            "No quality promotion is permitted from this packet alone."
        ],
        "items": packet,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"packet_count": len(packet), "classifications": dict(counts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
