#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'reading';C=R/'arabic/b1/passages.jsonl';O=R/'audit/arabic_gate_c_decisions_2026-09-05/b1_u09.json'
E={'ar-b1-u09-p01':'33a3f2fc4a33cf5da4e2a08e946218ca823b8863c67fd054d4537fa8784318de','ar-b1-u09-p02':'7bfa281615359a47783e9b9714bed8ae3e7dbf2e0e5ed30232cafc5ab3650690','ar-b1-u09-p03':'a3a95a333c9982e038f087735a29fdb08245dbf4daead07b8df1e8f7e6bceafb','ar-b1-u09-p04':'b615f16f805fdb7a8c54e2c263d4c119d0292b9634edcd1c00d1733e8b635d58','ar-b1-u09-p05':'ace3795d1c13753746dc62c36bd9393b2a34155ea4aefe0255fd29ab0efc23ee','ar-b1-u09-p06':'978f66497e31dcbd94a35759b8626babad97d75debd99349cf7a2c77e841f8bf'}
def s(b):return hashlib.sha256(b).hexdigest()
def p(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};h='naturalness' in '\n'.join(r.get('quality',{}).get('notes',[])).lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':h}
def lh(r):return s(json.dumps(p(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def main():
 raw=C.read_bytes();rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-b1-u09-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={i:lh(by[i]) for i in ids}
 if hs!=E:raise SystemExit('B1 Unit 9 learner-facing hash drift')
 d=[{'passage_id':i,'learner_facing_sha256':hs[i],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]} for i in ids]
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'B1','unit':9,'date':'2026-09-08','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/b1/passages.jsonl','canonical_sha256':s(raw),'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'decisions':d,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; all six B1 Unit 9 records passed exact-current comprehension and answer-grounding review without learner-facing mutation.'}
 if O.exists():
  if json.loads(O.read_text())!=doc:raise SystemExit('existing B1 Unit 9 evidence drift')
 else:O.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 print('B1 Unit 9 clean decisions recorded/verified')
if __name__=='__main__':main()
