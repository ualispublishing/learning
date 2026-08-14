#!/usr/bin/env python3
"""Repair the confirmed فعالية/ar-r2063 semantic mismatch.

Rank 2063 means effectiveness/efficiency, while A2 U07 P01 deliberately taught
فعالية as event/activity. The natural surface word may remain support vocabulary,
but the deliberate ranked target becomes unused rank 593 مناسبة = occasion/event.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl';PID='ar-a2-u07-p01';OLD='ar-r2063';NEW='ar-r593'
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];by={r['id']:r for r in rows};r=by[PID]
# Candidate rank 593 must be unused as a new/review target in A2 before repair.
assert not any(isinstance(t,dict) and t.get('id')==NEW for row in rows for t in [*row.get('new_lexical_targets',[]),*row.get('review_lexical_targets',[])]),(NEW,'already used')
# Every old-id use in A2 must be the false فعالية item or its downstream bookkeeping.
old_new=[(row['id'],t) for row in rows for t in row.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==OLD]
assert len(old_new)==1 and old_new[0][0]==PID and old_new[0][1].get('form')=='فعالية',old_new
old_review=[(row['id'],t) for row in rows for t in row.get('review_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==OLD]
old_q=[(row['id'],q.get('id')) for row in rows for q in row.get('questions',[]) if isinstance(q,dict) and OLD in (q.get('target_ids') or [])]
# No legitimate alternate-form use is permitted.
assert all(t.get('form')=='فعالية' for _,t in old_review),old_review

# Replace the deliberate target identity.
t=old_new[0][1]
t.update({'form':'مناسبة','lemma':'مناسبة','id':NEW,'intended_sense':'occasion; event','part_of_speech':'noun','source_rank':593,'source_lexicon':'arabic_top1000.csv','exposures_in_text':3})
# Introduce مناسبة naturally while retaining other natural uses of فعالية as support vocabulary.
old1='أعلن مركز الحي عن فعالية مفتوحة في الساحة يوم السبت.'
new1='أعلن مركز الحي عن مناسبة عامة في الساحة يوم السبت. تضم هذه المناسبة فعالية مفتوحة للزوار.'
old2='في يوم الفعالية وصلت نور مبكرًا ووقفت قرب المدخل.'
new2='في يوم المناسبة وصلت نور مبكرًا ووقفت قرب المدخل.'
assert r['text'].count(old1)==1 and r['text'].count(old2)==1
r['text']=r['text'].replace(old1,new1).replace(old2,new2)
assert r['text'].count('مناسبة')==3,r['text']
q={x['id']:x for x in r['questions']};a={x['question_id']:x for x in r['answer_key']}
for qid in ('q3','q6','q8','q9'):
    assert OLD in q[qid].get('target_ids',[]),(qid,q[qid])
q['q3']['prompt']='ماذا تعني «مناسبة» في بداية النص؟';q['q3']['target_ids']=[NEW];a['q3']['answer']='حدث منظم يجمع أشخاصًا أو أنشطة حول غرض معين.'
q['q6']['prompt']='ما معنى «مناسبة» في هذا السياق؟';q['q6']['target_ids']=[NEW];a['q6']['answer']='حدث أو وقت مخصص لشيء معين.'
q['q8']['prompt']='أيهما يشير إلى الحدث نفسه: مناسبة أم جمهور؟';q['q8']['target_ids']=[NEW,'ar-r975'];a['q8']['answer']='مناسبة.'
q['q9']['prompt']='أكمل: نظم المركز _____ ثقافية يوم الجمعة.';q['q9']['target_ids']=[NEW];a['q9']['answer']='مناسبة'
# Remove stale false-rank review bookkeeping and any old target refs elsewhere.
touched={PID}
for row in rows:
    before=len(row.get('review_lexical_targets',[]))
    row['review_lexical_targets']=[x for x in row.get('review_lexical_targets',[]) if not (isinstance(x,dict) and x.get('id')==OLD)]
    if len(row['review_lexical_targets'])!=before:touched.add(row['id'])
    for qq in row.get('questions',[]):
        if not isinstance(qq,dict) or not isinstance(qq.get('target_ids'),list):continue
        if row['id']!=PID and OLD in qq['target_ids']:
            qq['target_ids']=[tid for tid in qq['target_ids'] if tid!=OLD];touched.add(row['id'])
# Revision/notes.
for pid in touched:
    row=by[pid];row['word_count']=len(str(row.get('text','')).split());row['revision']=int(row.get('revision',1))+1
    notes=row.setdefault('quality',{}).setdefault('notes',[]);note='Final audit Pass 10 repair: removed false فعالية=event mapping to rank 2063 (effectiveness/efficiency); introduced source-backed مناسبة/ar-r593 for occasion/event. Natural فعالية usage may remain as support vocabulary.'
    if note not in notes:notes.append(note)
# Hard postconditions.
assert not any(isinstance(t,dict) and t.get('id')==OLD for row in rows for t in [*row.get('new_lexical_targets',[]),*row.get('review_lexical_targets',[])]),(OLD,'still lexical')
assert not any(OLD in (qq.get('target_ids') or []) for row in rows for qq in row.get('questions',[]) if isinstance(qq,dict)),(OLD,'still question ref')
new_hits=[(row['id'],t) for row in rows for t in row.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==NEW]
assert len(new_hits)==1 and new_hits[0][0]==PID,new_hits
PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
print(json.dumps({'passage_id':PID,'old_target_id':OLD,'new_target_id':NEW,'removed_review_uses':len(old_review),'removed_external_question_refs':len([x for x in old_q if x[0]!=PID]),'touched_passages':sorted(touched)},ensure_ascii=False))
