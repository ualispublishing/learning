#!/usr/bin/env python3
"""Convert six verified same-item C1 reintroductions from new targets to reviews.

The target set comes from final Pass 02 plus the persisted comparison artifact.
Review stages are derived from prior canonical review occurrences: R1 for the
first review, then R2...R5, capped at R5. No passage/assessment text changes.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
AUDIT=ROOT/'reading/audit/final_arabic_pass02_lexical_exposure_integrity.json'
COMPARE=ROOT/'reading/audit/final_arabic_pass02_reintroduced_target_comparison.json'
EXPECTED={
    ('ar-c1-u04-p01','ar-r1940'),
    ('ar-c1-u06-p04','ar-r1469'),
    ('ar-c1-u07-p02','ar-r1916'),
    ('ar-c1-u07-p03','ar-r1879'),
    ('ar-c1-u09-p03','ar-r1929'),
    ('ar-c1-u09-p03','ar-r1880'),
}

def stage_for_count(n:int)->str:
    return f'R{min(max(n,1),5)}'

loaded={}
ordered=[]
for li,level in enumerate(LEVELS):
    path=ROOT/f'reading/arabic/{level}/passages.jsonl'
    rows=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    loaded[level]=rows
    for r in rows:
        ordered.append((li,int(r.get('sequence',0) or 0),level,r))
ordered.sort(key=lambda x:(x[0],x[1],x[3].get('id','')))

issues=json.loads(AUDIT.read_text(encoding='utf-8')).get('hard_issues',[])
actual={(x['passage_id'],x['target_id']) for x in issues if x.get('code')=='target_reintroduced_as_new'}
assert actual==EXPECTED,(actual,EXPECTED)
comp=json.loads(COMPARE.read_text(encoding='utf-8'))
assert comp.get('remaining_reintroduced_targets')==6
assert {(x['later_passage'],x['target_id']) for x in comp['comparisons']}==EXPECTED

# Explicitly reviewed as same lexical item despite contextual gloss/register expansion.
for x in comp['comparisons']:
    assert x['first']['id']==x['later']['id']==x['target_id']
    for k in ('form','lemma','part_of_speech','source_rank','source_lexicon','beyond_base','variety'):
        assert x['first'][k]==x['later'][k],(x['target_id'],k,x['first'][k],x['later'][k])

index={(r['id']):(li,seq,level,r) for li,seq,level,r in ordered}
repairs=[]
for later_pid,tid in sorted(EXPECTED):
    li,seq,level,row=index[later_pid]
    new_hits=[t for t in row.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==tid]
    assert len(new_hits)==1,(later_pid,tid,new_hits)
    target=new_hits[0]

    prior_review_count=0
    first_intro=None
    for pli,pseq,plevel,prow in ordered:
        if (pli,pseq)>=(li,seq):
            break
        for t in prow.get('new_lexical_targets',[]):
            if isinstance(t,dict) and t.get('id')==tid and first_intro is None:
                first_intro=prow['id']
        prior_review_count += sum(1 for t in prow.get('review_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==tid)
    assert first_intro is not None,(later_pid,tid)
    review_stage=stage_for_count(prior_review_count+1)

    row['new_lexical_targets']=[t for t in row.get('new_lexical_targets',[]) if not (isinstance(t,dict) and t.get('id')==tid)]
    reviews=row.setdefault('review_lexical_targets',[])
    assert not any(isinstance(t,dict) and t.get('id')==tid for t in reviews),(later_pid,tid,'already review in same passage')
    reviews.append({
        'form':target.get('form'),
        'id':tid,
        'representation':'running_text',
        'review_stage':review_stage,
    })
    repairs.append({'passage_id':later_pid,'target_id':tid,'first_introduction':first_intro,'prior_review_count':prior_review_count,'assigned_review_stage':review_stage})

# Increment each touched passage exactly once and annotate.
for pid in sorted({p for p,_ in EXPECTED}):
    row=index[pid][3]
    row['revision']=int(row.get('revision',1))+1
    notes=row.setdefault('quality',{}).setdefault('notes',[])
    note='Final audit Pass 02 repair: verified same ranked lexical items previously introduced at B2 were converted from C1 new targets to review targets; passage and assessment text unchanged.'
    if note not in notes: notes.append(note)

for level,rows in loaded.items():
    if any(r['id'] in {p for p,_ in EXPECTED} for r in rows):
        path=ROOT/f'reading/arabic/{level}/passages.jsonl'
        path.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')

# Post-condition: none of the six remains new; each is present once as review.
for pid,tid in EXPECTED:
    row=index[pid][3]
    assert not any(isinstance(t,dict) and t.get('id')==tid for t in row.get('new_lexical_targets',[]))
    assert sum(1 for t in row.get('review_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==tid)==1

print(json.dumps({'repairs':repairs,'repair_count':len(repairs)},ensure_ascii=False))
