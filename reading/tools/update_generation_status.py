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
ARABIC_LEVELS=("a1","a2","b1","b2","c1","c2")
LEVEL_LABEL={x:x.upper() for x in ARABIC_LEVELS}


def count(path):
    p=ROOT/path
    return sum(1 for line in p.read_text(encoding="utf-8").splitlines() if line.strip()) if p.exists() else 0


def units(path):
    p=ROOT/path
    if not p.exists():
        return []
    values=[]
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            u=json.loads(line).get("unit")
            if isinstance(u,int):
                values.append(u)
    return sorted(set(values))


def level_path(level):
    return f"reading/arabic/{level}/passages.jsonl"


def state_for(n):
    return "COMPLETE" if n>=60 else ("IN_PROGRESS" if n>0 else "NEXT")


def next_unit_for(level):
    us=units(level_path(level))
    if len(us)>=10:
        return None
    return (max(us)+1) if us else 1


def main():
    s=json.loads(STATUS.read_text(encoding="utf-8"))
    counts={level:count(level_path(level)) for level in ARABIC_LEVELS}
    unit_sets={level:units(level_path(level)) for level in ARABIC_LEVELS}
    fr=count("reading/french/a1/passages.jsonl")
    ur=count("reading/urdu/a1/passages.jsonl")
    total=sum(counts.values())+fr+ur

    active_level=next((level for level in ARABIC_LEVELS if counts[level]<60),None)
    completed=[LEVEL_LABEL[level] for level in ARABIC_LEVELS if counts[level]>=60]

    s["updated"]="2026-08-14"
    if active_level:
        n=counts[active_level]
        us=unit_sets[active_level]
        if n:
            phase_tail=f"Arabic {LEVEL_LABEL[active_level]} generation is underway at {n} passages across units {us}."
        else:
            phase_tail=f"Arabic {LEVEL_LABEL[active_level]} generation is next."
        completed_text=", ".join(completed) if completed else "no Arabic levels"
        s["phase"]=(
            f"Generation-first passage production. Completed Arabic generation levels: {completed_text}. "
            f"{phase_tail} Formal audits remain deferred to the final 10+ pass review phase."
        )
    else:
        s["phase"]=(
            "Generation-first Arabic A1-C2 passage production is complete. Formal audits remain deferred "
            "to the final 10+ pass review phase."
        )

    s["draft_passages"]=total

    # Preserve detailed A1 evidence already stored while synchronizing generation counts.
    for level in ARABIC_LEVELS:
        key=f"arabic_{level}"
        existing=s.get(key,{})
        record={
            **existing,
            "passages":counts[level],
            "units_generated":unit_sets[level],
            "questions_per_passage":10,
            "total_questions":counts[level]*10,
            "total_answers":counts[level]*10,
            "generation_state":state_for(counts[level]),
            "formal_final_approval":"DEFERRED; final corpus approval occurs in the later 10+ pass audit phase",
        }
        next_unit=next_unit_for(level)
        if next_unit is None:
            record.pop("next_unit",None)
        elif level==active_level:
            record["next_unit"]=next_unit
        else:
            record.pop("next_unit",None)
        s[key]=record

    s["cross_language_a1"]={
        **s.get("cross_language_a1",{}),
        "arabic_canonical_passages":counts["a1"],
        "french_canonical_passages":fr,
        "urdu_canonical_passages":ur,
        "formal_audit_state":"DEFERRED_UNTIL_GENERATION_PHASE_COMPLETE",
    }

    if active_level:
        nu=next_unit_for(active_level)
        action=(
            f"continue Arabic {LEVEL_LABEL[active_level]} generation from Unit {nu:02d}"
            if counts[active_level]>0
            else f"begin Arabic {LEVEL_LABEL[active_level]} Unit 01 generation"
        )
        s["next_actions"]=[
            action+" using the roadmap's increasing discourse, inference, genre, and reference-chain demands",
            "continue generation unit by unit without routine mid-generation audits; fix only obvious severe or propagation-prone defects immediately",
            "keep ten questions and ten answers per canonical passage, with generation-stage formal quality fields pending",
            "after the designated generation corpus is complete, run at least 10 distinct final audit passes using different linguistic, pedagogical, lexical, structural, and adversarial approaches",
        ]
    else:
        s["next_actions"]=[
            "begin the planned final 10+ pass audit phase only after confirming the full designated generation corpus is complete",
            "keep audit passes independent and use different linguistic, pedagogical, lexical, structural, factual, continuity, and adversarial approaches",
        ]

    files=s.setdefault("important_files",[])
    for level in ARABIC_LEVELS:
        p=level_path(level)
        if (ROOT/p).exists() and p not in files:
            files.append(p)
    tool_path="reading/tools/update_generation_status.py"
    if tool_path not in files:
        files.append(tool_path)

    STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    counts_text=", ".join(f"ar-{k}={v}" for k,v in counts.items())
    print(f"status synchronized: total={total}, {counts_text}, fr-a1={fr}, ur-a1={ur}, active={active_level}")


if __name__=="__main__":
    main()
