#!/usr/bin/env python3
"""Derive the active CEFR generation-plan subtree from canonical planning/status files.

This is generation infrastructure only. It does not validate passage quality or
perform any linguistic/pedagogical audit. Its purpose is to keep future agents
bound to the exact roadmap rather than guessing level themes from memory.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STATUS=ROOT/'reading'/'STATUS.json'
MATRIX=ROOT/'reading'/'planning'/'topic_genre_matrix.json'
OUT=ROOT/'reading'/'planning'/'ACTIVE_GENERATION_PLAN.json'
LEVELS=('A1','A2','B1','B2','C1','C2')


def norm_level(x):
    return str(x or '').strip().upper()


def active_level(status):
    # Prefer canonical generation counts when present; first level below 60 is active.
    for level in LEVELS:
        rec=status.get(f'arabic_{level.lower()}',{})
        if int(rec.get('passages',0) or 0)<60:
            return level
    return None


def collect_matches(node, target, path='$'):
    """Find subtrees that explicitly identify themselves with target level.

    Supports matrices keyed by level (e.g. {"C1": ...}) and record-oriented
    matrices (e.g. {"cefr":"C1", ...}) without hard-coding one schema.
    """
    matches=[]
    if isinstance(node,dict):
        # Direct level-keyed subtree.
        for k,v in node.items():
            if norm_level(k)==target:
                matches.append({'path':f'{path}.{k}','value':v,'match':'level_key'})
        # Record carrying an explicit level field.
        for field in ('cefr','level','proficiency_level'):
            if field in node and norm_level(node.get(field))==target:
                matches.append({'path':path,'value':node,'match':field})
                break
        for k,v in node.items():
            matches.extend(collect_matches(v,target,f'{path}.{k}'))
    elif isinstance(node,list):
        for i,v in enumerate(node):
            matches.extend(collect_matches(v,target,f'{path}[{i}]'))
    return matches


def dedupe(matches):
    seen=set(); out=[]
    for m in matches:
        signature=json.dumps(m['value'],ensure_ascii=False,sort_keys=True)
        if signature in seen:
            continue
        seen.add(signature); out.append(m)
    return out


def main():
    status=json.loads(STATUS.read_text(encoding='utf-8'))
    matrix=json.loads(MATRIX.read_text(encoding='utf-8'))
    level=active_level(status)
    matches=dedupe(collect_matches(matrix,level)) if level else []
    payload={
        'source_status':'reading/STATUS.json',
        'source_matrix':'reading/planning/topic_genre_matrix.json',
        'active_level':level,
        'generation_first':True,
        'formal_audits_deferred':True,
        'match_count':len(matches),
        'matches':matches,
        'notes':[
            'Derived artifact only; canonical roadmap remains topic_genre_matrix.json.',
            'Do not invent or rename unit themes when an exact roadmap match exists.',
            'Passage-quality audits remain deferred to the final multi-pass phase.'
        ]
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"active_level={level}; roadmap_matches={len(matches)}; wrote {OUT.relative_to(ROOT)}")

if __name__=='__main__':
    main()
