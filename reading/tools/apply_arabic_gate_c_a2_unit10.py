#!/usr/bin/env python3
"""Validate the clean Arabic Gate C A2 Unit 10 frontier without canonical mutation."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];READING=ROOT/'reading';PATH=READING/'arabic/a2/passages.jsonl';DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u10.json'
EXPECTED_GIT_BLOB='ab58a51ece0edecbb550ead955befda55c714dee';EXPECTED_MANIFEST='4a4877e33e432cae0802f59d6b037fd8a6635a50b28501c8bcc25ae5d2bd1e19'
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 if DECISION.exists():raise SystemExit('duplicate Gate C A2 Unit 10 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text())
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST:raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic'];c=r['comprehension_review_progress']
 if r['release_state']!='REOPEN_REQUIRED' or r['educator_release_ready'] is not False:raise SystemExit('release boundary drift')
 if (c['fresh_records_reviewed'],c['fresh_qa_pairs_reviewed'],c['fresh_records_with_findings'],c['fresh_findings'])!=(114,1140,77,142) or c['levels_completed']!=['A1']:raise SystemExit('Gate C frontier drift')
 if r['latest_deterministic_gate']['open_findings']!=1080:raise SystemExit('deterministic frontier drift')
 raw=PATH.read_bytes()
 if blob(raw)!=EXPECTED_GIT_BLOB:raise SystemExit('A2 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u10-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(54,60)]!=ids:raise SystemExit('A2 Unit 10 id/order drift')
 for rec in rows[54:60]:
  pid=rec['id']
  if len(rec.get('questions',[]))!=10 or len(rec.get('answer_key',[]))!=10:raise SystemExit(f'{pid}: 10Q/10A drift')
  if {q['answer_id'] for q in rec['questions']}!={a['id'] for a in rec['answer_key']}:raise SystemExit(f'{pid}: linkage drift')
  q=rec.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending':raise SystemExit(f'{pid}: protected quality frontier drift')
  for k in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if q.get(k)!='pass':raise SystemExit(f'{pid}: Gate B quality state drift: {k}')
 print(json.dumps({'gate':'C','level':'A2','unit':10,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':0,'fresh_findings':0,'clean_passes':6,'canonical_mutation':False,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
