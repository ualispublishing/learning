#!/usr/bin/env python3
"""Resolve Pass-06 exact source mismatches to candidate canonical ranks.

This is read-only diagnostic output. It requires an exact normalized match in
one of the canonical ranked CSV Front fields and reports collisions before any
canonical passage repair is attempted.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
AUDIT=ROOT/'reading/audit/final_arabic_pass06_lexical_source_identity.json'
OUT=ROOT/'reading/audit/final_arabic_pass06_source_mismatch_candidates.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
RANK_RE=re.compile(r'\bRank:\s*(\d+)')
def norm(s):
    s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا')
    s=DIAC.sub('',s)
    return ''.join(s.split())
front_index=defaultdict(list)
rank_data={}
for name in ('arabic_top1000.csv','arabic_top3000.csv'):
    with (ROOT/name).open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            m=RANK_RE.search(row.get('Back','') or '')
            if not m: continue
            rank=int(m.group(1));front=row.get('Front','')
            rank_data[rank]={'rank':rank,'front':front,'source_file':name}
            front_index[norm(front)].append(rank_data[rank])
rows={}
new_by_id=defaultdict(list);review_by_id=defaultdict(list);question_refs=defaultdict(list)
for level in LEVELS:
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    for line in p.read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        r=json.loads(line);rows[r['id']]=r
        for t in r.get('new_lexical_targets',[]):
            if isinstance(t,dict) and t.get('id'):new_by_id[t['id']].append({'passage_id':r['id'],'level':level,'form':t.get('form'),'sense':t.get('intended_sense')})
        for t in r.get('review_lexical_targets',[]):
            if isinstance(t,dict) and t.get('id'):review_by_id[t['id']].append({'passage_id':r['id'],'level':level,'form':t.get('form'),'stage':t.get('review_stage')})
        for q in r.get('questions',[]):
            for tid in q.get('target_ids',[]) if isinstance(q,dict) and isinstance(q.get('target_ids'),list) else []:
                question_refs[tid].append({'passage_id':r['id'],'question_id':q.get('id'),'level':level})
a=json.loads(AUDIT.read_text(encoding='utf-8'))
warns=[x for x in a.get('warnings',[]) if x.get('code')=='target_form_lemma_not_exactly_source_front']
items=[];unresolved=[]
for w in warns:
    form=w['form'];lemma=w.get('lemma') or form;old_id=w['target_id'];pid=w['passage_id']
    candidates=front_index.get(norm(form),[]) or front_index.get(norm(lemma),[])
    entry={'passage_id':pid,'level':w['level'],'old_target_id':old_id,'old_rank':w['source_rank'],'form':form,'lemma':lemma,'old_source_front':w['source_front'],'candidates':candidates,'old_id_other_new_uses':new_by_id.get(old_id,[]),'old_id_review_uses':review_by_id.get(old_id,[]),'old_id_question_refs':question_refs.get(old_id,[])}
    if len(candidates)==1:
        cand=candidates[0];new_id=f"ar-r{cand['rank']}";entry['proposed_target_id']=new_id;entry['proposed_rank']=cand['rank'];entry['proposed_source_file']=cand['source_file'];entry['proposed_id_existing_new_uses']=new_by_id.get(new_id,[]);entry['proposed_id_existing_review_uses']=review_by_id.get(new_id,[]);entry['proposed_id_question_refs']=question_refs.get(new_id,[])
    else: unresolved.append(entry)
    items.append(entry)
payload={'mismatch_count':len(warns),'exact_unique_candidate_count':sum(1 for x in items if x.get('proposed_target_id')),'unresolved_count':len(unresolved),'items':items,'unresolved':unresolved}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'mismatch_count':payload['mismatch_count'],'exact_unique_candidate_count':payload['exact_unique_candidate_count'],'unresolved_count':payload['unresolved_count']},ensure_ascii=False))
