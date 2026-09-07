#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'reading';C=R/'arabic/b1/passages.jsonl';O=R/'audit/arabic_gate_c_decisions_2026-09-05/b1_u05.json'
E={'ar-b1-u05-p01':'26bd5d63a5e332bfaad0a58638a1b40ff642e2b3a242fbf688de4fa874cd9911','ar-b1-u05-p02':'69cee041bb52beb4f5ac0e173b596b5a4d08ea51e5bac7be15a43d2c9716e5a4','ar-b1-u05-p03':'3dfac523843eb1ca203b4f0d6436abd26c404e4175b5fa72478972780f7d2e17','ar-b1-u05-p04':'a6c1fb7977014771ccafa9d51c823f05b025b29c41783dbff9e430d1943dabe1','ar-b1-u05-p05':'334ca196806fc6debe7212b06d1b97d5676f00c71ef254ceb3fcfde729fcad1d','ar-b1-u05-p06':'cab2555aca270b7a3595ce498c39f62907a9865f8a1123d22d5bb92a436a758b'}
def s(b):return hashlib.sha256(b).hexdigest()
def p(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};h='naturalness' in '\n'.join(r.get('quality',{}).get('notes',[])).lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':h}
def lh(r):return s(json.dumps(p(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def main():
 raw=C.read_bytes();rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-b1-u05-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={i:lh(by[i]) for i in ids}
 if hs!=E:raise SystemExit('B1 Unit 5 learner-facing hash drift')
 d=[{'passage_id':i,'learner_facing_sha256':hs[i],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]} for i in ids]
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'B1','unit':5,'date':'2026-09-07','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/b1/passages.jsonl','canonical_sha256':s(raw),'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'decisions':d,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; all six B1 Unit 5 records passed exact-current comprehension and answer-grounding review without learner-facing mutation.'}
 if O.exists():
  if json.loads(O.read_text())!=doc:raise SystemExit('existing B1 Unit 5 evidence drift')
 else:O.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 print('B1 Unit 5 clean decisions recorded/verified')
if __name__=='__main__':main()
