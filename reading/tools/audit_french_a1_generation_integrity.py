#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/french/a1/passages.jsonl'; LEX=ROOT/'french_top1000.csv'
OUT=ROOT/'reading/audit/french_a1_generation_integrity.json'
OV={('fr-a1-u06-p04','jamais'),('fr-a1-u07-p04','droite')}
def deck():
 d={}
 with LEX.open(encoding='utf-8',newline='') as f:
  for r in csv.DictReader(f):
   b=r.get('Back') or '';x=(r.get('Front') or '').strip()
   a=re.search(r'Rank:\s*(\d+)',b);m=re.search(r'Meaning:\s*(.+)',b)
   if x and a and m:d[x]=(int(a.group(1)),m.group(1).strip())
 return d
def count(text,f):return len(re.findall(rf'(?<!\w){re.escape(f)}(?!\w)',text,flags=re.I|re.UNICODE))
def main():
 rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()];D=deck();bad=[];seen={};ovs=set()
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)):bad.append('passage/sequence continuity')
 if len({r.get('id') for r in rows})!=60:bad.append('duplicate passage id')
 for r in rows:
  pid=r['id'];wc=len(r['text'].split())
  if r.get('word_count')!=wc or not 90<=wc<=140:bad.append(f'{pid}: word count/band')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10:bad.append(f'{pid}: assessment count')
  amap={a.get('question_id'):a.get('id') for a in r.get('answer_key',[])}
  local={t.get('id') for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict)}
  for q in r.get('questions',[]):
   if amap.get(q.get('id'))!=q.get('answer_id'):bad.append(f'{pid}:{q.get("id")}: answer link')
   if any(x not in local for x in q.get('target_ids',[])):bad.append(f'{pid}:{q.get("id")}: undeclared target')
  if pid.endswith('-p06') and r.get('new_lexical_targets'):bad.append(f'{pid}: P06 new target')
  for t in r.get('new_lexical_targets',[]):
   key=t.get('id');form=t.get('form');lookup=t.get('source_lookup_form') or form
   if key in seen:bad.append(f'{pid}: duplicate new target {key}')
   seen[key]=(r['sequence'],form)
   if lookup not in D:bad.append(f'{pid}:{form}: source form missing');continue
   rank,sense=D[lookup];eid=f'fr-rank-{rank:04d}'
   if t.get('source_lexicon')!='french_top1000.csv' or t.get('source_rank')!=rank or key!=eid:bad.append(f'{pid}:{form}: source identity')
   adj=t.get('sense_adjudication');k=(pid,form)
   if adj:
    ovs.add(k)
    if k not in OV or adj.get('status')!='VERIFIED_OVERRIDE' or not adj.get('authority_url'):bad.append(f'{pid}:{form}: bad override')
   elif t.get('intended_sense')!=sense:bad.append(f'{pid}:{form}: unadjudicated sense drift')
   if count(r['text'],form)!=t.get('exposures_in_text'):bad.append(f'{pid}:{form}: exposure count')
 for r in rows:
  for t in r.get('review_lexical_targets',[]):
   x=seen.get(t.get('id'))
   if not x or x[0]>=r['sequence']:bad.append(f'{r["id"]}:{t.get("form")}: invalid review reference')
 if len(seen)!=100:bad.append(f'new target total {len(seen)} != 100')
 if ovs!=OV:bad.append(f'override set {sorted(ovs)}')
 units={str(u):{'passages':sum(r['unit']==u for r in rows),'new_targets':sum(len(r.get('new_lexical_targets',[])) for r in rows if r['unit']==u)} for u in range(1,11)}
 payload={'status':'PASS' if not bad else 'FAIL','scope':'French A1 generation milestone','passages':len(rows),'questions':sum(len(r['questions']) for r in rows),'answers':sum(len(r['answer_key']) for r in rows),'new_targets':len(seen),'verified_sense_overrides':[{'passage_id':p,'form':f} for p,f in sorted(ovs)],'units':units,'failures':bad,'coverage_note':'estimated_known_token_coverage remains unmeasured placeholder data; no percentage is inferred','full_final_audit_deferred':True}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':payload['status'],'failures':len(bad)},ensure_ascii=False))
 if bad:raise SystemExit(1)
if __name__=='__main__':main()
