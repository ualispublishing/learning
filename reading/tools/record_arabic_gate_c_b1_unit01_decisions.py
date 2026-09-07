#!/usr/bin/env python3
"""Record clean Arabic Gate C B1 Unit 1 decisions."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
CANON=READING/'arabic/b1/passages.jsonl'; OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/b1_u01.json'
EXPECTED={
'ar-b1-u01-p01':'8bfe5e0f581f379b87e4d4365e0943e8f21a39c2043f0a2c05739afb403bc59e',
'ar-b1-u01-p02':'03a70c83181a6104046e0931616138cb3e2f5473ace5adf7737a1edfd8d028fa',
'ar-b1-u01-p03':'82dc234c1db29ee5a9f376167c1c9a8fe6b86457c690f29c6cdaf8217b25a7ec',
'ar-b1-u01-p04':'baa1d917abe4cefb41f3e5a7f8ec7aa8031c7d3a885e437bb059eb33bd4661d3',
'ar-b1-u01-p05':'3d799aa498b10ef686e294c9101dd98ee5e04b7c65724037da790152720cf508',
'ar-b1-u01-p06':'5831fe026b3071f68db7fd5f4df550650ae340a36ab964ca956115541535fd75'}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
 return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def main():
 raw=CANON.read_bytes(); rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; ids=[f'ar-b1-u01-p{i:02d}' for i in range(1,7)]; by={r['id']:r for r in rows}; hs={p:lh(by[p]) for p in ids}
 if hs!=EXPECTED: raise SystemExit('B1 Unit 1 learner-facing hash drift')
 dec=[{'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]} for p in ids]
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'B1','unit':1,'date':'2026-09-07','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/b1/passages.jsonl','canonical_sha256':sha(raw),'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; all six B1 Unit 1 records passed exact-current comprehension and answer-grounding review without learner-facing mutation.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc: raise SystemExit('existing B1 Unit 1 evidence drift')
  print('B1 Unit 1 clean evidence verified idempotently'); return
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'B1','unit':1,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'clean_passes':6,'release_claim':False},indent=2))
if __name__=='__main__':main()
