#!/usr/bin/env python3
"""Verify fresh Arabic Gate C B1 Unit 2 as a clean no-mutation batch."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];READING=ROOT/'reading';PATH=READING/'arabic/b1/passages.jsonl';DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/b1_u02.json'
EXPECTED_GIT_BLOB='4b0fce5abe01d3802f545e2e02ce4f1558e41f33';EXPECTED_MANIFEST='94a0aa2de77c0bc9b9ae4c27d13fd5f8baf984f0135e33a0e4d2db893cdcfd79'
EXPECTED={'ar-b1-u02-p01':'cafd9cb4bbe4aaba95a3313b5cec171e922eb844df68a6293aabf20dfb3ad97a','ar-b1-u02-p02':'62585fde94f00203bbea94a3e0c5f0aeae0d5cfa756938639426bedb1362e632','ar-b1-u02-p03':'11c45062f621518be307ee925b6640369a72f89e127b057ebcfe649eb77ecc16','ar-b1-u02-p04':'743c07371df9721dec467ec2102479d8d31b884161c88161b5be182abb40ea89','ar-b1-u02-p05':'e35a0e237c5f965e1ca8b8b8dc50c4c5dce30679b0738072842f77d1a3a5decf','ar-b1-u02-p06':'3743799f4288c5daf6632b158e28ff065921ca053d6ae94e79991bb1be7617a9'}
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def sha(b):return hashlib.sha256(b).hexdigest()
def payload(r):
 a={x.get('question_id'):x for x in r.get('answer_key',[])};hist='naturalness' in '\n'.join(r.get('quality',{}).get('notes',[])).lower();return {'passage_id':r.get('id'),'unit':r.get('unit'),'sequence':r.get('sequence'),'cefr':r.get('cefr'),'title':r.get('title'),'genre':r.get('genre'),'text':r.get('text'),'qa':[{'question_id':q.get('id'),'type':q.get('type'),'prompt':q.get('prompt'),'answer':a.get(q.get('id'),{}).get('answer'),'explanation':a.get(q.get('id'),{}).get('explanation','')} for q in r.get('questions',[])],'historical_naturalness_note_present':hist}
def lh(r):return sha(json.dumps(payload(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def main():
 if DECISION.exists():raise SystemExit('duplicate Gate C B1 Unit 2 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text());r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic'];c=r['comprehension_review_progress'];b=r['naturalness_review_progress'];d=r['latest_deterministic_gate']
 if m['aggregate_sha256']!=EXPECTED_MANIFEST:raise SystemExit('state manifest drift')
 if r['release_state']!='REOPEN_REQUIRED' or r['educator_release_ready'] is not False:raise SystemExit('release boundary drift')
 if (b['fresh_records_reviewed'],b['fresh_records_with_findings'],b['fresh_findings'])!=(360,308,560):raise SystemExit('Gate B frontier drift')
 if (c['fresh_records_reviewed'],c['fresh_qa_pairs_reviewed'],c['fresh_records_with_findings'],c['fresh_findings'])!=(126,1260,77,142) or c['levels_completed']!=['A1','A2']:raise SystemExit('Gate C frontier drift')
 if d['open_findings']!=1080:raise SystemExit('deterministic frontier drift')
 raw=PATH.read_bytes()
 if blob(raw)!=EXPECTED_GIT_BLOB:raise SystemExit('B1 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-b1-u02-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(6,12)]!=ids:raise SystemExit('B1 Unit 2 id/order drift')
 for rec in rows[6:12]:
  if lh(rec)!=EXPECTED[rec['id']]:raise SystemExit(f"{rec['id']}: learner-facing hash drift")
  if len(rec['questions'])!=10 or len(rec['answer_key'])!=10:raise SystemExit(f"{rec['id']}: 10Q/10A drift")
  if {q['answer_id'] for q in rec['questions']}!={a['id'] for a in rec['answer_key']}:raise SystemExit(f"{rec['id']}: linkage drift")
  if rec['quality'].get('status')!='draft' or rec['quality'].get('coverage_check')!='pending':raise SystemExit(f"{rec['id']}: quality boundary drift")
 print(json.dumps({'gate':'C','level':'B1','unit':2,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':0,'fresh_findings':0,'decision':'6 CLEAN PASS','canonical_sha256':sha(raw),'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
