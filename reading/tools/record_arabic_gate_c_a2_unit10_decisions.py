#!/usr/bin/env python3
"""Record six clean Arabic Gate C A2 Unit 10 PASS decisions without Gate B mutation."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];READING=ROOT/'reading';CANON=READING/'arabic/a2/passages.jsonl';OUT=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u10.json';GATE_B=READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u10.json'
EXPECTED_HASHES={'ar-a2-u10-p01':'35c4a8ea863ab554fcc7025a0782e23857474949ac9c32ae9e4e728c3051dc8d','ar-a2-u10-p02':'d5469e921c354d110cbda2255b9a656e9693c1ac5a50cc6136fcb39b19579713','ar-a2-u10-p03':'f30e1ed6d55e4b2ef52ce9665b4ded7bb0e4d984613f8eef88c13665c5c2d1c9','ar-a2-u10-p04':'8209d0441299bbe3d7c7fe85345a70d80efb978ddddba4ba3c5cc68b2de4408e','ar-a2-u10-p05':'d85a0250e1510ac71d971bb3050c29322e8a30475c7cd84a00728d403ca42bfd','ar-a2-u10-p06':'379bba0e31beb4f0b03f5a952aebfaab451f67e358ad5f8c9bdfb640239347db'}
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};notes='\n'.join(r.get('quality',{}).get('notes',[]));hist='naturalness' in notes.lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def main():
 raw=CANON.read_bytes();canon=sha(raw);rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u10-p{i:02d}' for i in range(1,7)];by={r['id']:r for r in rows};hs={p:lh(by[p]) for p in ids}
 if hs!=EXPECTED_HASHES:raise SystemExit('A2 Unit 10 learner-facing hash drift')
 g=json.loads(GATE_B.read_text());bd={d['passage_id']:d for d in g['decisions']}
 if any(bd[p]['learner_facing_sha256']!=EXPECTED_HASHES[p] for p in ids):raise SystemExit('A2 Unit 10 Gate B binding drift')
 dec=[{'passage_id':p,'learner_facing_sha256':hs[p],'decision':'PASS','qa_pairs_reviewed':10,'finding_count':0,'findings':[]} for p in ids]
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A2','unit':10,'date':'2026-09-07','gate':'Gate C — comprehension and answer-grounding audit','canonical_path':'reading/arabic/a2/passages.jsonl','canonical_sha256':canon,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'decisions':dec,'quality_promotion':False,'release_claim':False,'guard':'Fresh Gate C decisions bind by authoritative per-record Gate B packet hashes; this clean batch makes no learner-facing or Gate B mutation.'}
 if OUT.exists():
  if json.loads(OUT.read_text())!=doc:raise SystemExit('existing A2 Unit 10 evidence drift')
  print('A2 Unit 10 clean evidence verified idempotently');return
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'level':'A2','unit':10,'records_reviewed':6,'qa_pairs_reviewed':60,'records_with_findings':0,'fresh_findings':0,'clean_passes':6,'gate_b_mutation':False,'release_claim':False},indent=2))
if __name__=='__main__':main()
