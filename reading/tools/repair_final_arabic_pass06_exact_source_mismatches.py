#!/usr/bin/env python3
"""Repair Pass-06 mismatches with one exact canonical Front candidate.

Repairs are form-sensitive. If the newly corrected canonical ID was introduced
later under the same lexical form, that later occurrence is converted to a
review so the earlier A2 occurrence becomes the single true introduction.
Different-form uses of either old or proposed IDs are protected.
"""
from __future__ import annotations
import json,re,unicodedata
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
LEVEL_INDEX={level:i for i,level in enumerate(LEVELS)}
CAND=ROOT/'reading/audit/final_arabic_pass06_source_mismatch_candidates.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
def norm(s):
    s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا')
    return ''.join(DIAC.sub('',s).split())
def stage(n): return f'R{min(max(n,1),5)}'

data=json.loads(CAND.read_text(encoding='utf-8'))
items=[x for x in data['items'] if x.get('proposed_target_id')]
assert len(items)==19,len(items)
assert data['unresolved_count']==4,data['unresolved_count']
for x in items: assert len(x.get('candidates',[]))==1,x
new_ids=[x['proposed_target_id'] for x in items]
assert len(new_ids)==len(set(new_ids)),new_ids

loaded={}
ordered=[]
for level in LEVELS:
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    rows=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
    loaded[level]=rows
    for row in rows: ordered.append((LEVEL_INDEX[level],int(row.get('sequence',0) or 0),level,row))
ordered.sort(key=lambda x:(x[0],x[1],x[3].get('id','')))
order_by_pid={r['id']:(li,seq) for li,seq,_,r in ordered}

# Before touching data, prove any pre-existing proposed-ID introductions are the
# same normalized form and occur later than the bad introduction being fixed.
for x in items:
    nf=norm(x['form']); intro_order=order_by_pid[x['passage_id']]
    for use in x.get('proposed_id_existing_new_uses',[]):
        assert norm(use.get('form'))==nf,(x['form'],x['proposed_target_id'],use)
        assert order_by_pid[use['passage_id']]>intro_order,(x['passage_id'],use['passage_id'])

repairs=[];touched_rows=defaultdict(set);later_demotions=[]
for x in items:
    old_id=x['old_target_id'];new_id=x['proposed_target_id'];form=x['form'];nf=norm(form)
    new_rank=x['proposed_rank'];new_file=x['proposed_source_file']
    intro_changes=review_changes=q_changes=0;affected=set()

    # Correct the wrong-ID introduction and every form-matched review carrying
    # that old ID. Legitimate old-ID uses with another form remain untouched.
    for level,rows in loaded.items():
        for row in rows:
            pid=row['id']
            for t in row.get('new_lexical_targets',[]):
                if isinstance(t,dict) and t.get('id')==old_id and norm(t.get('form') or t.get('lemma'))==nf:
                    t['id']=new_id;t['source_rank']=new_rank;t['source_lexicon']=new_file
                    intro_changes+=1;affected.add(pid);touched_rows[level].add(pid)
            for t in row.get('review_lexical_targets',[]):
                if isinstance(t,dict) and t.get('id')==old_id and norm(t.get('form'))==nf:
                    t['id']=new_id;review_changes+=1;affected.add(pid);touched_rows[level].add(pid)
    assert intro_changes==1,(old_id,form,'intro_changes',intro_changes)

    # Question links follow the repaired lexical target only in passages that
    # actually carry the repaired form-matched target/review metadata.
    for level,rows in loaded.items():
        for row in rows:
            if row['id'] not in affected: continue
            for q in row.get('questions',[]):
                if not isinstance(q,dict) or not isinstance(q.get('target_ids'),list): continue
                before=list(q['target_ids']);q['target_ids']=[new_id if tid==old_id else tid for tid in q['target_ids']]
                if before!=q['target_ids']:q_changes+=1;touched_rows[level].add(row['id'])

    # A correct ID may already have been introduced later under this same form
    # (صحافة/ar-r1285 is the known case). Convert those later introductions to
    # reviews, preserving question links because they already use the right ID.
    for use in x.get('proposed_id_existing_new_uses',[]):
        pid=use['passage_id']; li,seq=order_by_pid[pid]
        level=use['level'];row=next(r for r in loaded[level] if r['id']==pid)
        hits=[t for t in row.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==new_id and norm(t.get('form') or t.get('lemma'))==nf]
        assert len(hits)==1,(pid,new_id,hits)
        prior_reviews=0
        for pli,pseq,_,prow in ordered:
            if (pli,pseq)>=(li,seq): break
            prior_reviews+=sum(1 for t in prow.get('review_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==new_id)
        row['new_lexical_targets']=[t for t in row.get('new_lexical_targets',[]) if t is not hits[0]]
        assert not any(isinstance(t,dict) and t.get('id')==new_id for t in row.get('review_lexical_targets',[])),(pid,new_id)
        assigned=stage(prior_reviews+1)
        row.setdefault('review_lexical_targets',[]).append({'form':hits[0].get('form'),'id':new_id,'representation':'running_text','review_stage':assigned})
        affected.add(pid);touched_rows[level].add(pid)
        later_demotions.append({'passage_id':pid,'target_id':new_id,'form':form,'review_stage':assigned,'prior_review_count':prior_reviews})

    repairs.append({'form':form,'old_target_id':old_id,'new_target_id':new_id,'new_rank':new_rank,'source_file':new_file,'introduction_changes':intro_changes,'review_id_changes':review_changes,'question_reference_changes':q_changes,'affected_passages':sorted(affected)})

# Revision/notes once per touched row.
for level,rows in loaded.items():
    if not touched_rows[level]:continue
    for row in rows:
        if row['id'] not in touched_rows[level]:continue
        row['revision']=int(row.get('revision',1))+1
        notes=row.setdefault('quality',{}).setdefault('notes',[])
        note='Final audit Pass 06 repair: corrected lexical rank/source identity by exact canonical ranked-deck Front match; later same-item introductions, where present, were converted to review. Reader text and answer content unchanged.'
        if note not in notes:notes.append(note)
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')

# Hard postconditions: no old ID remains under the mismatched form, and each
# proposed correct ID has exactly one new introduction corpus-wide.
for x in items:
    old_id=x['old_target_id'];new_id=x['proposed_target_id'];nf=norm(x['form'])
    old_form_hits=[];new_intro_hits=[]
    for level,rows in loaded.items():
        for row in rows:
            for t in row.get('new_lexical_targets',[]):
                if not isinstance(t,dict):continue
                tf=norm(t.get('form') or t.get('lemma'))
                if tf==nf and t.get('id')==old_id:old_form_hits.append(row['id']+':new')
                if t.get('id')==new_id:new_intro_hits.append((row['id'],tf))
            for t in row.get('review_lexical_targets',[]):
                if isinstance(t,dict) and norm(t.get('form'))==nf and t.get('id')==old_id:old_form_hits.append(row['id']+':review')
    assert not old_form_hits,(x['form'],old_id,old_form_hits)
    assert len(new_intro_hits)==1,(x['form'],new_id,new_intro_hits)
    assert new_intro_hits[0][1]==nf,(x['form'],new_intro_hits)

print(json.dumps({'repair_count':len(repairs),'touched_passages':sum(len(v) for v in touched_rows.values()),'later_duplicate_introductions_demoted':later_demotions,'repairs':repairs},ensure_ascii=False))
