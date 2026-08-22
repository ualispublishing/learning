import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
OUT = READING / "audit" / "french_review_stage_timing_audit_2026-08-19.json"
LEVELS = ["a1", "a2", "b1", "b2", "c1", "c2"]
# Mandatory standard describes these as default heuristic windows, not hard laws.
WINDOWS = {"R1": (1, 2), "R2": (4, 6), "R3": (10, 14), "R4": (25, 35)}
EXPECTED_HASHES = {
    "a1": "1cdb31ecb8b987c50051bb6f8fa5b2f7fda812cb3004c81ab8697f832fceacba",
    "a2": "8fcd71903e6a495a2abaac8d436232b4b7ee00ae5ac0bce4d273aa4a134b3c15",
    "b1": "7b1013fa606761bc7cc69fdaf67c66a0efcc9c91c478b1c8a5f8523458f9451b",
    "b2": "bfa64c472a93d572d65fbe0217283b9d53bbb0a8d88fee7ea3a3aef1c7993942",
    "c1": "dead8e5d6e6e60a7c6c5185996159670e6077ea2d5da31860de168674050b39a",
    "c2": "c161c4551a6ce0222850778c02ed0662e00bb60e5386d5dc0b4f31a92cb9f277",
}

def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def rows(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]

def main():
    corpus=[]; hashes={}
    for lev in LEVELS:
        p=READING/"french"/lev/"passages.jsonl"
        h=sha256(p); hashes[lev.upper()]=h
        if h != EXPECTED_HASHES[lev]: raise SystemExit(f"hash drift {lev}: {h}")
        rr=rows(p)
        if len(rr)!=60: raise SystemExit(f"{lev}: {len(rr)} records")
        corpus.extend(rr)
    idx={p["id"]: i+1 for i,p in enumerate(corpus)}
    introduced={}
    reviews=[]
    duplicate_intros=[]
    for p in corpus:
        for t in p.get("new_lexical_targets",[]):
            tid=t.get("id")
            if tid in introduced:
                duplicate_intros.append({"target_id":tid,"first":introduced[tid]["passage_id"],"again":p["id"]})
            else:
                introduced[tid]={"passage_id":p["id"],"global_index":idx[p["id"]],"level":p["cefr"],"form":t.get("form")}
        for r in p.get("review_lexical_targets",[]):
            reviews.append((p,r))
    findings=[]; counts=Counter(); per_stage=defaultdict(lambda: Counter(total=0,in_window=0,early=0,late=0,no_intro=0,not_numeric=0))
    histories=defaultdict(list)
    for p,r in reviews:
        tid=r.get("id"); stage=r.get("review_stage"); rec=per_stage[stage]; rec["total"]+=1
        intro=introduced.get(tid)
        base={"target_id":tid,"form":r.get("form"),"review_passage_id":p["id"],"review_global_index":idx[p["id"]],"review_stage":stage,"representation":r.get("representation")}
        if not intro:
            rec["no_intro"]+=1; counts["review_without_declared_intro"]+=1
            findings.append({**base,"kind":"review_without_declared_intro","severity":"major"}); continue
        distance=idx[p["id"]]-intro["global_index"]
        hist={**base,"intro_passage_id":intro["passage_id"],"intro_global_index":intro["global_index"],"distance_passages":distance}
        histories[tid].append(hist)
        if stage in WINDOWS:
            lo,hi=WINDOWS[stage]
            hist["default_window"]=[lo,hi]
            if distance < lo:
                rec["early"]+=1; counts[f"{stage}_earlier_than_default_min"]+=1
                findings.append({**hist,"kind":"stage_earlier_than_default_min","severity":"review_required","note":"Default windows are heuristics; semantic/pedagogical adjudication required before metadata repair."})
            elif distance > hi:
                rec["late"]+=1; counts[f"{stage}_later_than_default_max"]+=1
                findings.append({**hist,"kind":"stage_later_than_default_max","severity":"review_required","note":"Late review can be pedagogically valid; do not auto-repair."})
            else: rec["in_window"]+=1
        else:
            rec["not_numeric"]+=1
    # Detect stage-number decreases independently, but contextualize them using actual distances.
    order={"R1":1,"R2":2,"R3":3,"R4":4,"R5":5,"long_term":6}
    regressions=[]
    for tid,h in histories.items():
        prev=None
        for e in h:
            n=order.get(e["review_stage"])
            if prev and n is not None and prev[0] is not None and n < prev[0]:
                regressions.append({"target_id":tid,"prior":prev[1],"current":e,"kind":"numeric_stage_decrease","interpretation":"Candidate only. Compare both distances with default timing windows; an earlier prematurely high label can create a false regression."})
            prev=(n,e)
    out={
      "schema_version":1,"date":"2026-08-19","language":"fr","status":"CANDIDATE_AUDIT_REQUIRES_ADJUDICATION",
      "bound_canonical_hashes":hashes,
      "standard_basis":"docs/READING_PASSAGE_STANDARD.md section 10: R1 +1–2, R2 +4–6, R3 +10–14, R4 +25–35; intervals explicitly called heuristics; R5 next-level bridge/later checkpoint.",
      "method":{"distance":"Global passage count after first declared introduction across A1→C2 canonical order.","important":"Window mismatches are candidates, not automatic defects. Earlier-than-minimum stage labels are especially useful for detecting premature stage metadata; late reviews can be intentional."},
      "summary":{"declared_target_ids":len(introduced),"review_events":len(reviews),"duplicate_introductions":len(duplicate_intros),"candidate_findings":len(findings),"numeric_stage_decreases":len(regressions),"finding_counts":dict(counts),"per_stage":{k:dict(v) for k,v in per_stage.items()}},
      "duplicate_introductions":duplicate_intros,"numeric_stage_decreases":regressions,"timing_candidates":findings,
      "decision":{"may_auto_repair_review_stage":False,"may_claim_chronology_pass":False,"next":"Adjudicate early-stage candidates first, beginning with the two source-v1 R3→R2 cases; repair metadata only when stage label is unsupported by the curriculum timing/context."}
    }
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out["summary"],ensure_ascii=False,indent=2))
if __name__=="__main__": main()
