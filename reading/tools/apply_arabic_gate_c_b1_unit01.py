#!/usr/bin/env python3
"""Verify fresh Arabic Gate C B1 Unit 1 as a clean no-mutation batch."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/b1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/b1_u01.json'
EXPECTED_GIT_BLOB='4b0fce5abe01d3802f545e2e02ce4f1558e41f33'
EXPECTED_MANIFEST='99b97cd12b45da817c85ac001d1a222288c5478bdaf9a10b0ad8a431024247fd'
EXPECTED_HASHES={
'ar-b1-u01-p01':'8bfe5e0f581f379b87e4d4365e0943e8f21a39c2043f0a2c05739afb403bc59e',
'ar-b1-u01-p02':'03a70c83181a6104046e0931616138cb3e2f5473ace5adf7737a1edfd8d028fa',
'ar-b1-u01-p03':'82dc234c1db29ee5a9f376167c1c9a8fe6b86457c690f29c6cdaf8217b25a7ec',
'ar-b1-u01-p04':'baa1d917abe4cefb41f3e5a7f8ec7aa8031c7d3a885e437bb059eb33bd4661d3',
'ar-b1-u01-p05':'3d799aa498b10ef686e294c9101dd98ee5e04b7c65724037da790152720cf508',
'ar-b1-u01-p06':'5831fe026b3071f68db7fd5f4df550650ae340a36ab964ca956115541535fd75',
}

def blob(data:bytes)->str:return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])}; notes='\n'.join(r.get('quality',{}).get('notes',[])); hist='naturalness' in notes.lower()
 return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())

def main():
 if DECISION.exists(): raise SystemExit('duplicate Gate C B1 Unit 1 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']; c=r.get('comprehension_review_progress',{}); b=r.get('naturalness_review_progress',{}); d=r.get('latest_deterministic_gate',{})
 if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
 if (b.get('fresh_records_reviewed'),b.get('fresh_records_with_findings'),b.get('fresh_findings'))!=(360,308,560): raise SystemExit('Gate B frontier drift')
 if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(120,1200,77,142): raise SystemExit('Gate C frontier drift')
 if c.get('levels_completed')!=['A1','A2']: raise SystemExit('Gate C completed-level frontier drift')
 if d.get('open_findings')!=1080: raise SystemExit('deterministic frontier drift')
 raw=PATH.read_bytes()
 if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('B1 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]; ids=[f'ar-b1-u01-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(6)]!=ids: raise SystemExit('B1 Unit 1 id/order drift')
 for rec in rows[:6]:
  pid=rec['id']
  if lh(rec)!=EXPECTED_HASHES[pid]: raise SystemExit(f'{pid}: learner-facing hash drift')
  if len(rec.get('questions',[]))!=10 or len(rec.get('answer_key',[]))!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
  if {q.get('answer_id') for q in rec['questions']}!={a.get('id') for a in rec['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
  q=rec.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending': raise SystemExit(f'{pid}: quality boundary drift')
 print(json.dumps({'gate':'C','level':'B1','unit':1,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':0,'fresh_findings':0,'decision':'6 CLEAN PASS','canonical_sha256':sha(raw),'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
