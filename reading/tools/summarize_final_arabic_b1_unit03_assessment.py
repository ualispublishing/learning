#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'reading/arabic/b1/passages.jsonl';OUT=ROOT/'reading/audit/final_arabic_b1_unit03_assessment_summary.json'
rows=[]
for line in SRC.read_text(encoding='utf-8').splitlines():
    if not line.strip():continue
    r=json.loads(line)
    if r.get('unit')!=3:continue
    ans={a.get('question_id'):a.get('answer') for a in r.get('answer_key',[]) if isinstance(a,dict)}
    rows.append({'id':r['id'],'title':r.get('title'),'word_count':r.get('word_count'),'new_targets':[{k:t.get(k) for k in ('id','form','lemma','intended_sense','part_of_speech')} for t in r.get('new_lexical_targets',[])],'review_targets':[{k:t.get(k) for k in ('id','form','review_stage')} for t in r.get('review_lexical_targets',[])],'question_types':[q.get('type') for q in r.get('questions',[])],'questions':[{'id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'target_ids':q.get('target_ids',[]),'answer':ans.get(q.get('id'))} for q in r.get('questions',[])]})
assert len(rows)==6
OUT.write_text(json.dumps({'level':'B1','unit':3,'passages':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'word_counts':{r['id']:r['word_count'] for r in rows},'question_types':{r['id']:r['question_types'] for r in rows}},ensure_ascii=False))
