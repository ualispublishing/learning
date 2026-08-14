#!/usr/bin/env python3
"""Synchronize generation-only milestones in reading/STATUS.json.

This does not perform or claim quality audits. It counts canonical generated
passages and records the current generation-first production phase so handoffs do
not reopen already completed levels.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
STATUS=ROOT/"reading"/"STATUS.json"

def count(path):
    p=ROOT/path
    return sum(1 for line in p.read_text(encoding="utf-8").splitlines() if line.strip()) if p.exists() else 0

def units(path):
    p=ROOT/path
    if not p.exists():return []
    values=[]
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            u=json.loads(line).get("unit")
            if isinstance(u,int):values.append(u)
    return sorted(set(values))

def main():
    s=json.loads(STATUS.read_text(encoding="utf-8"))
    a1=count("reading/arabic/a1/passages.jsonl")
    a2=count("reading/arabic/a2/passages.jsonl")
    b1=count("reading/arabic/b1/passages.jsonl")
    fr=count("reading/french/a1/passages.jsonl")
    ur=count("reading/urdu/a1/passages.jsonl")
    total=a1+a2+b1+fr+ur
    b1_units=units("reading/arabic/b1/passages.jsonl")
    next_b1=(max(b1_units)+1) if b1_units else 1
    s["updated"]="2026-08-13"
    s["phase"]=(
        f"Generation-first passage production. Arabic A1 and A2 generation are complete at {a1} and {a2} canonical passages; "
        f"Arabic B1 generation is underway at {b1} passages across units {b1_units}. Formal audits remain deferred to the final 10+ pass review phase."
    )
    s["draft_passages"]=total
    s["arabic_a1"]={**s.get("arabic_a1",{}),"passages":a1,"units_generated":units("reading/arabic/a1/passages.jsonl"),"total_questions":a1*10,"total_answers":a1*10,"generation_state":"COMPLETE" if a1>=60 else "IN_PROGRESS","formal_final_approval":"DEFERRED; final corpus approval occurs in the later 10+ pass audit phase"}
    s["arabic_a2"]={"passages":a2,"units_generated":units("reading/arabic/a2/passages.jsonl"),"questions_per_passage":10,"total_questions":a2*10,"total_answers":a2*10,"generation_state":"COMPLETE" if a2>=60 else "IN_PROGRESS","formal_final_approval":"DEFERRED; final corpus approval occurs in the later 10+ pass audit phase"}
    s["arabic_b1"]={"passages":b1,"units_generated":b1_units,"questions_per_passage":10,"total_questions":b1*10,"total_answers":b1*10,"next_unit":next_b1,"generation_state":"IN_PROGRESS","formal_final_approval":"DEFERRED; final corpus approval occurs in the later 10+ pass audit phase"}
    s["cross_language_a1"]={**s.get("cross_language_a1",{}),"arabic_canonical_passages":a1,"french_canonical_passages":fr,"urdu_canonical_passages":ur,"formal_audit_state":"DEFERRED_UNTIL_GENERATION_PHASE_COMPLETE"}
    s["next_actions"]=[
        f"continue Arabic B1 generation from Unit {next_b1:02d} using longer multi-sentence inference, motive/reason, evidence, and wider reference chains",
        "continue generation unit by unit without routine mid-generation audits; fix only obvious severe or propagation-prone defects immediately",
        "keep ten questions and ten answers per canonical passage, with generation-stage formal quality fields pending",
        "after the designated generation corpus is complete, run at least 10 distinct final audit passes using different linguistic, pedagogical, lexical, structural, and adversarial approaches"
    ]
    files=s.setdefault("important_files",[])
    for f in ["reading/arabic/a2/passages.jsonl","reading/arabic/b1/passages.jsonl","reading/tools/update_generation_status.py"]:
        if f not in files:files.append(f)
    STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"status synchronized: total={total}, ar-a1={a1}, ar-a2={a2}, ar-b1={b1}, fr-a1={fr}, ur-a1={ur}")
if __name__=="__main__":main()
