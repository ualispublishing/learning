#!/usr/bin/env python3
"""Naturalness-first final release profile with minimum progression coverage."""
from collections import Counter
import csv, json, re
import workbook_release_passes as p
import build_language_workbooks_v1_quality as q

base = p.base
MIN_BANDS = {"A":250,"B":350,"C":300,"D":40}
BASE_Q = {"A":75,"B":105,"C":90,"D":0}
QUESTION_TARGET = 300
CAP = 240


def key(r): return (-r["score"], r["words"], r["english"])


def select_external_v5(cfg):
    candidates, source_hash = q.load_external(cfg)
    selected=[]; seen_t=set(); seen_e=set(); contrib=Counter(); bands=Counter(); qbands=Counter()
    def ok(r):
        return contrib[r["contributor"]] < CAP and base.norm(r["target"]) not in seen_t and base.norm(r["english"]) not in seen_e
    def take(r):
        selected.append(r); seen_t.add(base.norm(r["target"])); seen_e.add(base.norm(r["english"]))
        contrib[r["contributor"]]+=1; b=q.band(r["words"]); bands[b]+=1
        if "?" in r["english"]: qbands[b]+=1
    for b, need in BASE_Q.items():
        got=0
        for r in sorted((x for x in candidates if "?" in x["english"] and q.band(x["words"])==b), key=key):
            if got>=need: break
            if ok(r): take(r); got+=1
        if got!=need: raise SystemExit(f"{cfg['name']}: baseline question coverage {b} {got}/{need}")
    need=QUESTION_TARGET-sum(qbands.values())
    for r in sorted((x for x in candidates if "?" in x["english"] and q.band(x["words"]) in {"A","B","C"}), key=key):
        if need<=0: break
        if ok(r): take(r); need-=1
    if need: raise SystemExit(f"{cfg['name']}: global question shortage {need}")
    statements=sorted((x for x in candidates if "?" not in x["english"]), key=key)
    for b, minimum in MIN_BANDS.items():
        for r in statements:
            if bands[b]>=minimum: break
            if q.band(r["words"])==b and ok(r): take(r)
        if bands[b]<minimum: raise SystemExit(f"{cfg['name']}: minimum band {b} {bands[b]}/{minimum}")
    for r in statements:
        if len(selected)>=1000: break
        if q.band(r["words"]) in {"A","B","C"} and ok(r): take(r)
    if len(selected)<1000:
        for r in sorted(candidates,key=key):
            if len(selected)>=1000: break
            if q.band(r["words"]) in {"A","B","C"} and ok(r): take(r)
    if len(selected)!=1000 or len(seen_t)!=1000 or len(seen_e)!=1000:
        raise SystemExit(f"{cfg['name']}: final count={len(selected)} target_unique={len(seen_t)} english_unique={len(seen_e)} bands={dict(bands)} top={contrib.most_common(3)}")
    if sum(qbands.values())!=QUESTION_TARGET: raise SystemExit(f"{cfg['name']}: question total {sum(qbands.values())}")
    selected.sort(key=lambda r: ({"A":0,"B":1,"C":2,"D":3}[q.band(r["words"])],r["words"],-r["score"],r["english"]))
    for i,r in enumerate(selected,1): r["rank"]=i; r["level"]=q.band(r["words"])
    top_name,top_count=contrib.most_common(1)[0]
    q.QUALITY_META[cfg["name"].casefold()]={
        "source_type":"ManyThings/Tatoeba CC BY 2.0 France","candidate_count":len(candidates),
        "target_unique":1000,"english_unique":1000,"question_count":300,"question_share":0.3,
        "top_contributor":top_name,"top_contributor_rows":top_count,"top_contributor_share":round(top_count/1000,3),
        "band_counts":dict(bands),"question_band_counts":dict(qbands),
        "selection_policy":"v5 minimum-progression-coverage naturalness-first"}
    return selected,len(candidates),source_hash


def corpus_audit_v5():
    blocked_ur=re.compile(r"تمھ|چاہیئے|چاہئیے|لئیے|لیئے|جائو|آئو|دکھائو|پہت|زیارہ|بیواقوف|مسلہ|بجھے|ڈھیڑ|تھورے|پہنج|کرے گے|رہے ہے|گئے ہے")
    audit={}
    for lang in ("arabic","french","urdu"):
        rows=p.read_stage(lang); targets=[base.norm(r["target"]) for r in rows]; english=[base.norm(r["english"]) for r in rows]
        questions=sum("?" in r["english"] for r in rows); bands=Counter(r["level"] for r in rows); problems=[]
        if len(rows)!=1000 or len(set(targets))!=1000 or len(set(english))!=1000: problems.append("count_or_uniqueness")
        if not 250<=questions<=350: problems.append("question_balance")
        if lang in ("arabic","french"):
            for b,m in MIN_BANDS.items():
                if bands[b]<m: problems.append(f"band_{b}_below_{m}")
            sel=json.loads((p.STAGE/f"{lang}_selection.json").read_text(encoding="utf-8"))
            if sel["quality"].get("top_contributor_share",1)>0.24: problems.append("source_concentration")
        if lang=="arabic" and any(q.AR_DIALECT.search(r["target"]) for r in rows): problems.append("arabic_dialect_marker")
        if lang=="urdu" and any(blocked_ur.search(r["target"]) for r in rows): problems.append("urdu_legacy_error_pattern")
        if any(len(r["target"])>180 or len(r["english"])>180 for r in rows): problems.append("excessive_length")
        sample=[]
        for b in ("A","B","C","D"):
            pool=[r for r in rows if r["level"]==b]; n=min(20,len(pool))
            if n:
                idxs=sorted({round(i*(len(pool)-1)/max(1,n-1)) for i in range(n)}); sample.extend(pool[i] for i in idxs)
        with (p.STAGE/f"{lang}_review_sample.csv").open("w",encoding="utf-8-sig",newline="") as f:
            fields=["rank","level","target","english","attribution"]; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for r in sample: w.writerow({k:r.get(k,"") for k in fields})
        audit[lang]={"rows":len(rows),"target_unique":len(set(targets)),"english_unique":len(set(english)),"question_count":questions,"band_counts":dict(bands),"sample_rows":len(sample),"problems":problems,"gate":"PASS" if not problems else "FAIL"}
        if problems: raise SystemExit(f"{lang}: corpus audit failed: {problems}")
    (p.STAGE/"corpus_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(audit,ensure_ascii=False,indent=2))

p.select_external_v3=select_external_v5
p.corpus_audit=corpus_audit_v5

if __name__=="__main__": p.main()
