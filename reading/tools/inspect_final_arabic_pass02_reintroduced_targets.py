#!/usr/bin/env python3
"""Compare every remaining Pass-02 reintroduced-as-new target with its first introduction."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'reading/audit/final_arabic_pass02_lexical_exposure_integrity.json'
OUT=ROOT/'reading/audit/final_arabic_pass02_reintroduced_target_comparison.json'
LEVELS=('a1','a2','b1','b2','c1','c2')
rows={}
for level in LEVELS:
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r=json.loads(line); rows[r['id']]=r

def target(pid,tid):
    r=rows[pid]
    hits=[t for t in r.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==tid]
    assert len(hits)==1,(pid,tid,hits)
    return hits[0]

a=json.loads(AUDIT.read_text(encoding='utf-8'))
issues=[x for x in a.get('hard_issues',[]) if x.get('code')=='target_reintroduced_as_new']
comparisons=[]
for x in issues:
    tid=x['target_id']; first_pid=x['first_passage']; later_pid=x['passage_id']
    first=target(first_pid,tid); later=target(later_pid,tid)
    keys=('id','form','lemma','intended_sense','part_of_speech','source_rank','source_lexicon','beyond_base','variety','register')
    same={k:first.get(k)==later.get(k) for k in keys}
    comparisons.append({
        'target_id':tid,'first_passage':first_pid,'later_passage':later_pid,
        'first':{k:first.get(k) for k in keys},'later':{k:later.get(k) for k in keys},
        'same_by_field':same,'same_core_identity':all(same[k] for k in ('id','intended_sense','source_rank','source_lexicon')),
    })
payload={'remaining_reintroduced_targets':len(comparisons),'comparisons':comparisons,'all_same_core_identity':all(x['same_core_identity'] for x in comparisons)}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload,ensure_ascii=False))
