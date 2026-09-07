#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'reading';C=R/'arabic/b1/passages.jsonl';O=R/'audit/arabic_gate_c_decisions_2026-09-05/b1_u04.json'
E={'ar-b1-u04-p01':'e551a8502f68e13850ecfa893341170bcab4e7ca6107d220fe7ed89e5d3c73d6','ar-b1-u04-p02':'46dd4a0f9a41f0966fd3037fa8252efc032ce3e29ed4f4a22128dcd0c30fe9c2','ar-b1-u04-p03':'0ac6e6dc183d67876f3d4376329e587f98a70c1d9f5ed6cb8cc2242f88ad9edb','ar-b1-u04-p04':'eee8cb16d4f12be503dc28562012d3e43b3b6e05343437f497061e26e64e54b6','ar-b1-u04-p05':'77199ae36bf00d9a60ed77d470200c650a6a85c3b36815dadde2675b4a234e46','ar-b1-u04-p06':'8a6e80418b2b698243bd8f05608c86d7807aa60dfe28af4dacd710a66ce28064'}
def s(b):return hashlib.sha256(b).hexdigest()
def p(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};h='naturalness' in '\n'.join(r.get('quality',{}).get('notes',[])).lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':h}
def lh(r):return s(json.dumps(p(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def main():
 raw=C.read_bytes();rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-b1-u04-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={i:lh(by[i]) for i in ids}
 if hs!=E:raise SystemExit('B1 Unit 4 learner-facing hash drift')
 d=[{'passage_id':i,'learner_facing_sha256':hs[i],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]} for i in ids]
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'B1','unit':4,'date':'2026-09-07','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/b1/passages.jsonl','canonical_sha256':s(raw),'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'decisions':d,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; all six B1 Unit 4 records passed exact-current comprehension and answer-grounding review without learner-facing mutation.'}
 if O.exists():
  if json.loads(O.read_text())!=doc:raise SystemExit('existing B1 Unit 4 evidence drift')
 else:O.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 print('B1 Unit 4 clean decisions recorded/verified')
if __name__=='__main__':main()
