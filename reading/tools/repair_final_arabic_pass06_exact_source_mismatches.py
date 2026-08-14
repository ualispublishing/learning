#!/usr/bin/env python3
"""Repair only Pass-06 mismatches with one exact canonical Front candidate.

The repair is form-sensitive: an old wrong rank ID is changed only where its
associated target/review form exactly matches the mismatched lexical form. This
protects legitimate uses of the old rank elsewhere. Question target references
are updated only inside passages whose lexical target metadata was repaired.
"""
from __future__ import annotations
import json,re,unicodedata
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
CAND=ROOT/'reading/audit/final_arabic_pass06_source_mismatch_candidates.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
def norm(s):
    s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا')
    return ''.join(DIAC.sub('',s).split())

data=json.loads(CAND.read_text(encoding='utf-8'))
items=[x for x in data['items'] if x.get('proposed_target_id')]
assert len(items)==19,len(items)
assert data['unresolved_count']==4,data['unresolved_count']
for x in items:
    assert len(x.get('candidates',[]))==1,x
    # If the corrected ID is already a deliberate new target elsewhere, this
    # needs chronology adjudication rather than a blind ID replacement.
    assert not x.get('proposed_id_existing_new_uses'),(x['proposed_target_id'],x['proposed_id_existing_new_uses'])

# Multiple bad IDs could in theory map to one correct ID; guard uniqueness here.
new_ids=[x['proposed_target_id'] for x in items]
assert len(new_ids)==len(set(new_ids)),new_ids

loaded={}
for level in LEVELS:
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    loaded[level]=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]

repairs=[]
touched_rows=defaultdict(set)
for x in items:
    old_id=x['old_target_id']; new_id=x['proposed_target_id']; form=x['form']; nf=norm(form)
    new_rank=x['proposed_rank']; new_file=x['proposed_source_file']
    intro_changes=review_changes=q_changes=0
    affected_passages=set()

    for level,rows in loaded.items():
        for row in rows:
            pid=row['id']
            for t in row.get('new_lexical_targets',[]):
                if isinstance(t,dict) and t.get('id')==old_id and norm(t.get('form') or t.get('lemma'))==nf:
                    t['id']=new_id;t['source_rank']=new_rank;t['source_lexicon']=new_file
                    intro_changes+=1;affected_passages.add(pid);touched_rows[level].add(pid)
            for t in row.get('review_lexical_targets',[]):
                if isinstance(t,dict) and t.get('id')==old_id and norm(t.get('form'))==nf:
                    t['id']=new_id
                    review_changes+=1;affected_passages.add(pid);touched_rows[level].add(pid)

    assert intro_changes==1,(old_id,form,'intro_changes',intro_changes)

    # Questions in passages carrying this repaired lexical item follow the ID.
    for level,rows in loaded.items():
        for row in rows:
            if row['id'] not in affected_passages: continue
            for q in row.get('questions',[]):
                if not isinstance(q,dict) or not isinstance(q.get('target_ids'),list):continue
                before=list(q['target_ids'])
                q['target_ids']=[new_id if tid==old_id else tid for tid in q['target_ids']]
                if q['target_ids']!=before:
                    q_changes+=1;touched_rows[level].add(row['id'])

    repairs.append({'form':form,'old_target_id':old_id,'new_target_id':new_id,'new_rank':new_rank,'source_file':new_file,'introduction_changes':intro_changes,'review_changes':review_changes,'question_reference_changes':q_changes,'affected_passages':sorted(affected_passages)})

# Revision/notes exactly once per touched row.
for level,rows in loaded.items():
    if not touched_rows[level]:continue
    for row in rows:
        if row['id'] not in touched_rows[level]:continue
        row['revision']=int(row.get('revision',1))+1
        notes=row.setdefault('quality',{}).setdefault('notes',[])
        note='Final audit Pass 06 repair: corrected lexical target rank/source IDs by exact canonical ranked-deck Front match; reader text and answer content unchanged.'
        if note not in notes:notes.append(note)
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')

# Hard postconditions: each repaired form now has exactly one new target at the
# proposed ID, and none remains as the old ID under that same form.
for x in items:
    old_id=x['old_target_id'];new_id=x['proposed_target_id'];nf=norm(x['form'])
    old_form_hits=[];new_form_hits=[]
    for level,rows in loaded.items():
        for row in rows:
            for t in row.get('new_lexical_targets',[]):
                if not isinstance(t,dict):continue
                if norm(t.get('form') or t.get('lemma'))!=nf:continue
                if t.get('id')==old_id:old_form_hits.append(row['id'])
                if t.get('id')==new_id:new_form_hits.append(row['id'])
            for t in row.get('review_lexical_targets',[]):
                if isinstance(t,dict) and norm(t.get('form'))==nf and t.get('id')==old_id:
                    old_form_hits.append(row['id']+':review')
    assert not old_form_hits,(x['form'],old_id,old_form_hits)
    assert len(new_form_hits)==1,(x['form'],new_id,new_form_hits)

print(json.dumps({'repair_count':len(repairs),'touched_passages':sum(len(v) for v in touched_rows.values()),'repairs':repairs},ensure_ascii=False))
