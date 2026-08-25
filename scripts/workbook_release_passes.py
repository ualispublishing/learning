#!/usr/bin/env python3
"""Time-boxed release passes for Arabic/French/Urdu workbook v1.0."""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter

import build_language_workbooks_v1 as base
import build_language_workbooks_v1_quality as q

STAGE = base.AUDIT / "staging_v3"
STAGE.mkdir(parents=True, exist_ok=True)
BAND_TOTALS = {"A": 300, "B": 400, "C": 260, "D": 40}
QUESTION_TARGET = 300
CONTRIBUTOR_CAP = 240
QUESTION_BAND_CAP = {"A": 150, "B": 200, "C": 120, "D": 10}


def _key(r):
    return (-r["score"], r["words"], r["english"])


def select_external_v3(cfg):
    candidates, source_hash = q.load_external(cfg)
    selected, seen_t, seen_e = [], set(), set()
    contributor_counts, band_counts, question_band_counts = Counter(), Counter(), Counter()

    def can_take(r):
        b = q.band(r["words"])
        return (band_counts[b] < BAND_TOTALS[b] and contributor_counts[r["contributor"]] < CONTRIBUTOR_CAP
                and base.norm(r["target"]) not in seen_t and base.norm(r["english"]) not in seen_e)

    def take(r):
        b = q.band(r["words"])
        selected.append(r)
        seen_t.add(base.norm(r["target"])); seen_e.add(base.norm(r["english"]))
        contributor_counts[r["contributor"]] += 1; band_counts[b] += 1
        if "?" in r["english"]: question_band_counts[b] += 1

    questions = sorted((r for r in candidates if "?" in r["english"]), key=_key)
    for r in questions:
        if sum(question_band_counts.values()) >= QUESTION_TARGET: break
        b = q.band(r["words"])
        if question_band_counts[b] >= QUESTION_BAND_CAP[b] or not can_take(r): continue
        take(r)
    if sum(question_band_counts.values()) < QUESTION_TARGET:
        for r in questions:
            if sum(question_band_counts.values()) >= QUESTION_TARGET: break
            if q.band(r["words"]) == "D" or not can_take(r): continue
            take(r)
    if sum(question_band_counts.values()) != QUESTION_TARGET:
        raise SystemExit(f"{cfg['name']}: could not satisfy global question target")

    statements = sorted((r for r in candidates if "?" not in r["english"]), key=_key)
    for b, total in BAND_TOTALS.items():
        for r in statements:
            if band_counts[b] >= total: break
            if q.band(r["words"]) == b and can_take(r): take(r)
    all_ranked = sorted(candidates, key=_key)
    for b, total in BAND_TOTALS.items():
        for r in all_ranked:
            if band_counts[b] >= total: break
            if q.band(r["words"]) == b and can_take(r): take(r)

    if len(selected) != 1000 or len(seen_t) != 1000 or len(seen_e) != 1000:
        raise SystemExit(f"{cfg['name']}: v3 count/uniqueness gate failed")
    if dict(band_counts) != BAND_TOTALS:
        raise SystemExit(f"{cfg['name']}: v3 band gate failed: {dict(band_counts)}")
    if sum("?" in r["english"] for r in selected) != QUESTION_TARGET:
        raise SystemExit(f"{cfg['name']}: v3 question gate failed")

    selected.sort(key=lambda r: ({"A":0,"B":1,"C":2,"D":3}[q.band(r["words"])], r["words"], -r["score"], r["english"]))
    for i, r in enumerate(selected, 1): r["rank"], r["level"] = i, q.band(r["words"])
    top_name, top_count = contributor_counts.most_common(1)[0]
    q.QUALITY_META[cfg["name"].casefold()] = {
        "source_type":"ManyThings/Tatoeba CC BY 2.0 France", "candidate_count":len(candidates),
        "target_unique":1000, "english_unique":1000, "question_count":QUESTION_TARGET,
        "question_share":0.3, "top_contributor":top_name, "top_contributor_rows":top_count,
        "top_contributor_share":round(top_count/1000,3), "band_counts":dict(band_counts),
        "question_band_counts":dict(question_band_counts), "selection_policy":"v3 global-question-balance naturalness-first"}
    return selected, len(candidates), source_hash


def select_language(lang, cfg):
    return q.controlled_urdu() if lang == "urdu" else select_external_v3(cfg)


def write_stage(lang, rows, source_hash):
    path = STAGE / f"{lang}_sentences.csv"
    fields = ["rank","level","target","english","attribution","words","contributor"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,"") for k in fields})
    payload = {"language":lang,"rows":len(rows),"source_hash":source_hash,"csv_sha256":base.sha256(path),"quality":q.QUALITY_META[lang]}
    (STAGE/f"{lang}_selection.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def corpus_select():
    q.QUALITY_META.clear(); summary = {}
    for lang, cfg in base.LANGS.items():
        rows, candidates, source_hash = select_language(lang, cfg); write_stage(lang, rows, source_hash)
        summary[lang] = {"rows":len(rows),"candidates":candidates,**q.QUALITY_META[lang]}
    (STAGE/"selection_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


def read_stage(lang):
    path = STAGE/f"{lang}_sentences.csv"
    if not path.exists(): raise SystemExit(f"missing staged corpus: {path}")
    with path.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
    for r in rows: r["rank"],r["words"],r["score"]=int(r["rank"]),int(r["words"]),0.0
    return rows


def corpus_audit():
    blocked_ur = re.compile(r"تمھ|چاہیئے|چاہئیے|لئیے|لیئے|جائو|آئو|دکھائو|پہت|زیارہ|بیواقوف|مسلہ|بجھے|ڈھیڑ|تھورے|پہنج|کرے گے|رہے ہے|گئے ہے")
    audit = {}
    for lang in ("arabic","french","urdu"):
        rows=read_stage(lang); targets=[base.norm(r["target"]) for r in rows]; english=[base.norm(r["english"]) for r in rows]
        questions=sum("?" in r["english"] for r in rows); bands=Counter(r["level"] for r in rows); problems=[]
        if len(rows)!=1000 or len(set(targets))!=1000 or len(set(english))!=1000: problems.append("count_or_uniqueness")
        if not 250<=questions<=350: problems.append("question_balance")
        if lang in ("arabic","french") and dict(bands)!=BAND_TOTALS: problems.append("band_balance")
        if lang=="arabic" and any(q.AR_DIALECT.search(r["target"]) for r in rows): problems.append("arabic_dialect_marker")
        if lang=="urdu" and any(blocked_ur.search(r["target"]) for r in rows): problems.append("urdu_legacy_error_pattern")
        if any(len(r["target"])>180 or len(r["english"])>180 for r in rows): problems.append("excessive_length")
        sample=[]
        for b in ("A","B","C","D"):
            pool=[r for r in rows if r["level"]==b]
            if not pool: continue
            n=min(20,len(pool)); idxs=sorted({round(i*(len(pool)-1)/max(1,n-1)) for i in range(n)})
            sample.extend(pool[i] for i in idxs)
        with (STAGE/f"{lang}_review_sample.csv").open("w",encoding="utf-8-sig",newline="") as f:
            fields=["rank","level","target","english","attribution"]; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for r in sample: w.writerow({k:r.get(k,"") for k in fields})
        audit[lang]={"rows":len(rows),"target_unique":len(set(targets)),"english_unique":len(set(english)),"question_count":questions,"band_counts":dict(bands),"sample_rows":len(sample),"problems":problems,"gate":"PASS" if not problems else "FAIL"}
        if problems: raise SystemExit(f"{lang}: corpus audit failed: {problems}")
    (STAGE/"corpus_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(audit,ensure_ascii=False,indent=2))


def staged_parse_sentences(cfg):
    lang=cfg["name"].casefold(); rows=read_stage(lang)
    sel=json.loads((STAGE/f"{lang}_selection.json").read_text(encoding="utf-8")); q.QUALITY_META[lang]=sel["quality"]
    return rows,len(rows),sel["source_hash"]


def build():
    if not (STAGE/"corpus_audit.json").exists(): raise SystemExit("corpus-audit pass must complete before build")
    q.QUALITY_META.clear(); base.parse_sentences=staged_parse_sentences; base.cover=q.quality_cover; base.sources_html=q.quality_sources_html
    base.LANGS["urdu"]["zip"]="internal://ualis/urdu-controlled-conversation-v1"; base.main(); q.post_process()


def release_audit():
    qa_path=base.AUDIT/"qa_summary.json"; manifest_path=base.OUT/"RELEASE_MANIFEST.json"
    if not qa_path.exists() or not manifest_path.exists(): raise SystemExit("missing final QA or release manifest")
    qa=json.loads(qa_path.read_text(encoding="utf-8")); problems=[]; pdfs=list(base.OUT.glob("*/*.pdf"))
    if len(pdfs)!=42: problems.append(f"pdf_count={len(pdfs)}")
    for lang in ("arabic","french","urdu"):
        z=qa.get(lang,{})
        if z.get("corpus_quality_gate")!="PASS": problems.append(f"{lang}_corpus_gate")
        if z.get("vocabulary_rows")!=1000 or z.get("sentence_rows")!=1000: problems.append(f"{lang}_row_count")
        if z.get("sentence_target_unique")!=1000 or z.get("sentence_english_unique")!=1000: problems.append(f"{lang}_uniqueness")
    if problems: raise SystemExit("release audit failed: "+", ".join(problems))
    result={"gate":"PASS","pdf_count":len(pdfs),"languages":["arabic","french","urdu"],"note":"Automated production-candidate release gates passed; independent native-speaker certification remains separate."}
    (base.AUDIT/"release_gate_v3.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(result,indent=2))


def main():
    modes={"corpus-select":corpus_select,"corpus-audit":corpus_audit,"build":build,"release-audit":release_audit}
    if len(sys.argv)!=2 or sys.argv[1] not in modes: raise SystemExit("usage: workbook_release_passes.py {corpus-select|corpus-audit|build|release-audit}")
    modes[sys.argv[1]]()

if __name__=="__main__": main()
