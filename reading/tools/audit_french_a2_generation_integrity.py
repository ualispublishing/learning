#!/usr/bin/env python3
"""Level-wide generation-integrity closeout for completed French A2.

This is not the deferred final language-wide multi-pass audit. It verifies the
mechanical and lexical invariants promised during guarded A2 generation.
"""
from __future__ import annotations
import json,re,subprocess
from collections import Counter,defaultdict
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_a2_unit03 as base

A1=base.A1
A2=base.CANON
SCHEMA=base.SCHEMA
OUT=Path("reading/audit/french_a2_generation_integrity.json")
EXPECTED_A1_BLOB="0493a2fa13e51b5997db05e91cdea4d8dc5e647b"
EXPECTED_A2_BLOB="d0a80b8866071f426019aa0ad143e1d270dba4de"

def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def main():
    failures=[]
    a1_blob=subprocess.check_output(["git","hash-object",str(A1)],text=True).strip()
    a2_blob=subprocess.check_output(["git","hash-object",str(A2)],text=True).strip()
    if a1_blob!=EXPECTED_A1_BLOB: failures.append(f"A1 blob drift: {a1_blob}")
    if a2_blob!=EXPECTED_A2_BLOB: failures.append(f"A2 blob drift: {a2_blob}")
    a1=rows(A1); a2=rows(A2); D=base.deck(); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    if len(a2)!=60: failures.append(f"passage_count={len(a2)}")
    if [r.get("sequence") for r in a2]!=list(range(1,61)): failures.append("sequence continuity")
    expected_ids=[f"fr-a2-u{u:02d}-p{p:02d}" for u in range(1,11) for p in range(1,7)]
    if [r.get("id") for r in a2]!=expected_ids: failures.append("id continuity")

    a1_new_ids={t.get("id") for r in a1 for t in r.get("new_lexical_targets",[]) if isinstance(t,dict) and t.get("id")}
    a1_new_forms={t.get("form") for r in a1 for t in r.get("new_lexical_targets",[]) if isinstance(t,dict) and t.get("form")}
    a2_new=[]; units=defaultdict(lambda:{"passages":0,"new_targets":0,"checkpoint_zero_new":False})
    qn=an=0
    for r in a2:
        rid=r.get("id","?"); u=r.get("unit"); units[u]["passages"]+=1
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: failures.append(f"{rid}: schema: {errs[0].message}")
        wc=len(r.get("text","").split())
        if r.get("word_count")!=wc: failures.append(f"{rid}: stored_word_count={r.get('word_count')} actual={wc}")
        if not 140<=wc<=220: failures.append(f"{rid}: word_band={wc}")
        qs=r.get("questions",[]); ans=r.get("answer_key",[]); qn+=len(qs); an+=len(ans)
        if len(qs)!=10 or len(ans)!=10: failures.append(f"{rid}: q/a count {len(qs)}/{len(ans)}")
        amap={a.get("question_id"):a.get("id") for a in ans}
        local={t.get("id") for fld in ("new_lexical_targets","review_lexical_targets") for t in r.get(fld,[]) if isinstance(t,dict) and t.get("id")}
        for q in qs:
            if amap.get(q.get("id"))!=q.get("answer_id"): failures.append(f"{rid}/{q.get('id')}: answer linkage")
            undeclared=[x for x in q.get("target_ids",[]) if x not in local]
            if undeclared: failures.append(f"{rid}/{q.get('id')}: undeclared targets {undeclared}")
        nts=r.get("new_lexical_targets",[]); units[u]["new_targets"]+=len(nts); a2_new.extend((rid,t) for t in nts)
        if r.get("sequence",0)%6==0:
            units[u]["checkpoint_zero_new"]=(len(nts)==0)
            if nts: failures.append(f"{rid}: checkpoint has new targets")
        for t in nts:
            f=t.get("form"); s=D.get(f)
            if not s: failures.append(f"{rid}: missing lexicon form {f}"); continue
            if t.get("source_rank")!=s["rank"]: failures.append(f"{rid}/{f}: rank identity")
            if t.get("id")!=base.tid(s["rank"]): failures.append(f"{rid}/{f}: id identity")
            if base.cnt(r.get("text",""),f)!=t.get("exposures_in_text"): failures.append(f"{rid}/{f}: exposure count")
        for t in r.get("review_lexical_targets",[]):
            if isinstance(t,dict) and t.get("representation") in {"running_text","summary"} and base.cnt(r.get("text",""),t.get("form",""))<1:
                failures.append(f"{rid}: invisible review {t.get('form')}")

    new_ids=[t.get("id") for _,t in a2_new]; new_forms=[t.get("form") for _,t in a2_new]
    if len(new_ids)!=100: failures.append(f"new_target_count={len(new_ids)}")
    if len(set(new_ids))!=100: failures.append("duplicate A2 new target ids")
    if len(set(new_forms))!=100: failures.append("duplicate A2 new target forms")
    overlap_ids=sorted(set(new_ids)&a1_new_ids); overlap_forms=sorted(set(new_forms)&a1_new_forms)
    if overlap_ids: failures.append(f"A1/A2 target id overlap: {overlap_ids}")
    if overlap_forms: failures.append(f"A1/A2 target form overlap: {overlap_forms}")
    if qn!=600 or an!=600: failures.append(f"level q/a totals={qn}/{an}")
    for u in range(1,11):
        m=units[u]
        if m["passages"]!=6 or m["new_targets"]!=10 or not m["checkpoint_zero_new"]:
            failures.append(f"unit {u} invariant: {m}")

    artifact={
      "status":"PASS" if not failures else "FAIL",
      "scope":"French A2 generation milestone",
      "canonical_blob":a2_blob,
      "passages":len(a2),"questions":qn,"answers":an,"new_targets":len(new_ids),
      "unique_new_target_ids":len(set(new_ids)),"unique_new_target_forms":len(set(new_forms)),
      "a1_cross_level_target_id_collisions":len(overlap_ids),"a1_cross_level_target_form_collisions":len(overlap_forms),
      "units":{str(u):units[u] for u in range(1,11)},
      "failures":failures,
      "coverage_note":"estimated_known_token_coverage remains unmeasured placeholder data; no percentage is inferred",
      "full_final_audit_deferred":True,
      "method_notes":[
        "Validated all 60 canonical A2 records against the passage schema and 140-220 word planning band.",
        "Rechecked source rank/id identity, exact stored exposure counts for every new A2 target, exact visibility of running-text/summary reviews, and local question target declarations.",
        "Rechecked A2 new-target uniqueness both within A2 and against all deliberate A1 new targets by source id and visible form.",
        "This is a generation-integrity closeout, not the deferred language-wide French final multi-pass approval audit."
      ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:artifact[k] for k in ("status","passages","questions","answers","new_targets","unique_new_target_ids","a1_cross_level_target_id_collisions")},ensure_ascii=False))
    if failures: raise SystemExit("; ".join(failures[:12]))

if __name__=="__main__": main()
