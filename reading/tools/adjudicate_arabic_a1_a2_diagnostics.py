#!/usr/bin/env python3
import json
import re
import subprocess
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A1 = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
A2 = ROOT / "reading" / "arabic" / "a2" / "passages.jsonl"
INPUT_REPORT = ROOT / "reading" / "audit" / "arabic_a1_a2_integrated_repair_audit_2026-08-23.json"
OUTPUT = ROOT / "reading" / "audit" / "arabic_a1_a2_diagnostic_adjudication_2026-08-23.json"
EXPECTED = {
    "a1": "4723cb4c9974a9a9c84b6c030d9c1a30c0820500",
    "a2": "d6a10dddde14628c8e4a7ddb4db7781604852210",
}

DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
NONWORD = re.compile(r"[^\u0621-\u064A\u0660-\u0669A-Za-z0-9]+")
PROCLITICS = ("و", "ف", "ب", "ك", "ل")
NOMINAL_SUFFIXES = ("هما", "هم", "هن", "كما", "كم", "كن", "نا", "ها", "ه", "ك", "ي")
VERB_PREFIXES = ("أ", "ا", "ن", "ي", "ت")
VERB_SUFFIXES = ("ون", "ين", "ان", "وا", "نا", "تم", "تن", "ن", "ت", "ا")


def git_blob(path):
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def norm(s):
    s = unicodedata.normalize("NFKC", str(s or "")).replace("ـ", "")
    s = DIACRITICS.sub("", s).replace("ٱ", "ا")
    s = NONWORD.sub(" ", s)
    return " ".join(s.split())


def tokens(s):
    return norm(s).split()


def strip_proclitics(tok):
    out = {tok}
    frontier = {tok}
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
    return out


def strip_nominal_suffixes(tok):
    out = {tok}
    for suf in NOMINAL_SUFFIXES:
        if tok.endswith(suf) and len(tok) - len(suf) >= 2:
            out.add(tok[:-len(suf)])
    if tok.endswith("ات") and len(tok) > 4:
        out.add(tok[:-2])
    if tok.endswith(("ون", "ين", "ان")) and len(tok) > 4:
        out.add(tok[:-2])
    return out


def clitic_equivalent(a, b):
    aa = set()
    bb = set()
    for x in strip_proclitics(a):
        aa |= strip_nominal_suffixes(x)
    for x in strip_proclitics(b):
        bb |= strip_nominal_suffixes(x)
    return bool(aa & bb)


def verb_cores(tok):
    vals = {tok}
    if len(tok) >= 4 and tok[0] in VERB_PREFIXES:
        vals.add(tok[1:])
    expanded = set(vals)
    for x in vals:
        for suf in VERB_SUFFIXES:
            if x.endswith(suf) and len(x) - len(suf) >= 3:
                expanded.add(x[:-len(suf)])
    return {x for x in expanded if len(x) >= 3}


def probable_verb_variant(a, b):
    return bool(verb_cores(a) & verb_cores(b))


def target_metadata(rows):
    meta = {}
    intro = {}
    for row in rows:
        for t in row.get("new_lexical_targets", []):
            if not isinstance(t, dict) or not t.get("id"):
                continue
            meta.setdefault(t["id"], t)
            intro.setdefault(t["id"], {"sequence": row.get("sequence"), "passage_id": row.get("id"), "form": t.get("form"), "lemma": t.get("lemma"), "part_of_speech": t.get("part_of_speech")})
    return meta, intro


def local_target_ids(row):
    return {t.get("id") for t in row.get("new_lexical_targets", []) if isinstance(t, dict)} | {t.get("id") for t in row.get("review_lexical_targets", []) if isinstance(t, dict)}


def classify_surface(text, form, pos):
    f = norm(form)
    toks = tokens(text)
    exact = sum(1 for t in toks if t == f)
    clitic = sum(1 for t in toks if t != f and clitic_equivalent(t, f))
    verb = 0
    if "verb" in str(pos or "").lower() or (len(f) >= 4 and f[:1] in VERB_PREFIXES):
        verb = sum(1 for t in toks if t != f and not clitic_equivalent(t, f) and probable_verb_variant(t, f))
    return {"exact": exact, "clitic_or_nominal_variant": clitic, "probable_verb_variant": verb, "combined_conservative": exact + clitic, "combined_with_probable_verb": exact + clitic + verb}


def main():
    actual = {"a1": git_blob(A1), "a2": git_blob(A2)}
    if actual != EXPECTED:
        raise SystemExit(f"Unexpected Arabic corpus blobs: {actual}")
    source = json.loads(INPUT_REPORT.read_text(encoding="utf-8"))
    if source.get("hard_errors"):
        raise SystemExit("Integrated report still contains hard errors")

    levels = {"a1": load_jsonl(A1), "a2": load_jsonl(A2)}
    indexes = {level: {r["id"]: r for r in rows} for level, rows in levels.items()}
    metadata = {}
    intros = {}
    for level, rows in levels.items():
        metadata[level], intros[level] = target_metadata(rows)

    details = []
    classes = Counter()
    code_counts = Counter()
    unresolved = []

    for w in source.get("warnings", []):
        code = w.get("code")
        code_counts[code] += 1
        pid = w.get("passage_id", "")
        level = "a1" if "-a1-" in pid else "a2"
        row = indexes[level].get(pid)
        item = {"warning": w, "level": level}
        if row is None:
            item["classification"] = "unresolved_missing_passage"
            unresolved.append(item)
            classes[item["classification"]] += 1
            details.append(item)
            continue

        tid = w.get("target_id")
        meta = metadata[level].get(tid, {})
        intro = intros[level].get(tid)
        item["target_intro"] = intro

        if code == "question_target_not_declared_in_passage_targets":
            if intro and intro.get("sequence") is not None and row.get("sequence") is not None and intro["sequence"] <= row["sequence"]:
                item["classification"] = "confirmed_local_target_linkage_metadata_gap"
                item["reason"] = "Question targets a known same-level lexical ID introduced no later than this passage, but the passage does not declare it in new/review target metadata."
            else:
                item["classification"] = "unresolved_question_target_identity"
                item["reason"] = "Question target is not locally declared and no valid prior/same-sequence introduction was established."
            unresolved.append(item)

        elif code in {"new_target_form_not_exactly_found_in_text", "declared_exposure_count_differs_from_exact_surface_count", "running_text_review_target_no_exact_surface"}:
            form = str(w.get("form") or meta.get("form") or meta.get("lemma") or "")
            evidence = classify_surface(row.get("text", ""), form, meta.get("part_of_speech"))
            item["surface_evidence"] = evidence
            declared = w.get("declared_exposures", w.get("declared"))
            if code == "declared_exposure_count_differs_from_exact_surface_count" and isinstance(declared, int):
                if evidence["combined_conservative"] == declared:
                    item["classification"] = "resolved_clitic_or_nominal_surface_count"
                elif evidence["combined_with_probable_verb"] == declared and evidence["probable_verb_variant"]:
                    item["classification"] = "needs_manual_inflection_confirmation"
                    unresolved.append(item)
                else:
                    item["classification"] = "unresolved_exposure_count_contract"
                    unresolved.append(item)
            elif evidence["exact"] > 0:
                item["classification"] = "resolved_exact_after_normalization"
            elif evidence["clitic_or_nominal_variant"] > 0:
                item["classification"] = "resolved_clitic_or_nominal_surface_presence"
            elif evidence["probable_verb_variant"] > 0:
                item["classification"] = "needs_manual_inflection_confirmation"
                unresolved.append(item)
            else:
                item["classification"] = "unresolved_no_conservative_surface_evidence"
                unresolved.append(item)
        else:
            item["classification"] = "unresolved_unknown_warning_code"
            unresolved.append(item)

        classes[item["classification"]] += 1
        details.append(item)

    by_unit = Counter()
    for item in unresolved:
        pid = item.get("warning", {}).get("passage_id", "")
        m = re.search(r"ar-(a1|a2)-u(\d{2})", pid)
        if m:
            by_unit[f"{m.group(1)}-u{m.group(2)}"] += 1

    report = {
        "schema_version": 1,
        "date": "2026-08-23",
        "scope": "Arabic A1+A2 integrated diagnostic warning adjudication",
        "input_blobs": actual,
        "source_warning_count": len(source.get("warnings", [])),
        "source_warning_code_counts": dict(code_counts),
        "classification_counts": dict(classes),
        "resolved_count": len(details) - len(unresolved),
        "unresolved_count": len(unresolved),
        "unresolved_by_unit": dict(by_unit),
        "policy": {
            "exact_surface": "Unicode-normalized exact tokens",
            "conservative_resolution": "Exact form plus detachable proclitic/definite-article and conservative nominal suffix variants may resolve surface diagnostics.",
            "verb_variants": "Prefix/suffix-based verb matches are evidence only and remain unresolved until manual linguistic confirmation.",
            "target_linkage": "A question target absent from local target metadata is treated as a metadata gap when the same ID has a valid same-level introduction at or before the passage.",
            "no_quality_promotion": True
        },
        "unresolved": unresolved,
        "details": details,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_warnings": report["source_warning_count"],
        "resolved": report["resolved_count"],
        "unresolved": report["unresolved_count"],
        "classes": report["classification_counts"],
        "unresolved_by_unit": report["unresolved_by_unit"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
