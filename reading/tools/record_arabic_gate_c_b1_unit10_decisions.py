#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'reading';C=R/'arabic/b1/passages.jsonl';O=R/'audit/arabic_gate_c_decisions_2026-09-05/b1_u10.json'
E={'ar-b1-u10-p01':'0332c1a96e2055d07c7ce382ac29f4d7ec100f347e5506fa0c691c4b17b33dd8','ar-b1-u10-p02':'e7b98d35d04d05a353828ac280b4c3e562f8b4d09602b5c81da1d637786ce8fc','ar-b1-u10-p03':'0573b1248232cd446e7004b8e1ea434ba7edd7346c0d7a731f003a4404b7857f','ar-b1-u10-p04':'71f605923d274d17ce419881305b19617a95c538922572321919a490549db6f7','ar-b1-u10-p05':'69efca82fba9bb87722a38413474d7a7c2617d54e6665a1a5602c34ce0136e98','ar-b1-u10-p06':'d271cd3250091ec679a34e6bc478249a16eee83525630ae3a1a0acfa8cb0c0f1'}
def s(b):return hashlib.sha256(b).hexdigest()
def p(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};h='naturalness' in '\n'.join(r.get('quality',{}).get('notes',[])).lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':h}
def lh(r):return s(json.dumps(p(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def main():
 raw=C.read_bytes();rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-b1-u10-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={i:lh(by[i]) for i in ids}
 if hs!=E:raise SystemExit('B1 Unit 10 learner-facing hash drift')
 d=[{'passage_id':i,'learner_facing_sha256':hs[i],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]} for i in ids]
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'B1','unit':10,'date':'2026-09-08','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/b1/passages.jsonl','canonical_sha256':s(raw),'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'decisions':d,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; all six B1 Unit 10 records passed exact-current comprehension and answer-grounding review without learner-facing mutation.'}
 if O.exists():
  if json.loads(O.read_text())!=doc:raise SystemExit('existing B1 Unit 10 evidence drift')
 else:O.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 print('B1 Unit 10 clean decisions recorded/verified')
if __name__=='__main__':main()
