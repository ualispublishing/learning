#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'reading';C=R/'arabic/b1/passages.jsonl';O=R/'audit/arabic_gate_c_decisions_2026-09-05/b1_u03.json'
E={'ar-b1-u03-p01':'50b6eeccc474c9e5bcd5a23c2bd4d717d1cd66a80e85f68d26a569ca14e8a4c4','ar-b1-u03-p02':'fb1d314c804aff39e5f340c7ccb04ba47dbf0b53e5e582e5057ef474634c4e60','ar-b1-u03-p03':'887cf2d9e22d8a7024a7d2dc82ace69395e2f64fe4ad2a060a60c4a8404a0ff2','ar-b1-u03-p04':'5b40cade89972bc8ad1c6c9db284b4bc9e541c1df5aec76c0612fb67fe379ae1','ar-b1-u03-p05':'9da990f6be1a5318a3cfa79cd395fb1cc93e28d854daddbeafd89257f9b8e2d4','ar-b1-u03-p06':'1776773878c8a54c36e67c8f7d48d852cc5705dfed07e46b28d6c5ccbfa8fc15'}
def s(b):return hashlib.sha256(b).hexdigest()
def p(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};h='naturalness' in '\n'.join(r.get('quality',{}).get('notes',[])).lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':h}
def lh(r):return s(json.dumps(p(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def main():
 raw=C.read_bytes();rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-b1-u03-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={i:lh(by[i]) for i in ids}
 if hs!=E:raise SystemExit('B1 Unit 3 learner-facing hash drift')
 d=[{'passage_id':i,'learner_facing_sha256':hs[i],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]} for i in ids]
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'B1','unit':3,'date':'2026-09-07','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/b1/passages.jsonl','canonical_sha256':s(raw),'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'decisions':d,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; all six B1 Unit 3 records passed exact-current comprehension and answer-grounding review without learner-facing mutation.'}
 if O.exists():
  if json.loads(O.read_text())!=doc:raise SystemExit('existing B1 Unit 3 evidence drift')
 else:O.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 print('B1 Unit 3 clean decisions recorded/verified')
if __name__=='__main__':main()
