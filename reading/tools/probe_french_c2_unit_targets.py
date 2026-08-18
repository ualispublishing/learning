#!/usr/bin/env python3
"""Exhaustively probe validated rank-1001+ French continuation for C2_UNIT=2..10."""
from __future__ import annotations
import csv,json,os,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';LEX3=R/'french_top3000.csv';AUD=R/'reading/audit'
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
def main():
 u=int(os.environ.get('C2_UNIT','0'))
 if not 2<=u<=10:raise AssertionError('C2_UNIT must be 2..10')
 plan=json.loads((AUD/f'french_c2_unit{u:02d}_plan.json').read_text());rows=load(C2);c2=h(C2);prev=u-1;lock=json.loads((AUD/f'french_c2_unit{prev:02d}_frontier_lock.json').read_text())
 if plan.get('status')!='PASS' or plan.get('c2_source_blob')!=c2 or lock.get('status')!='PASS' or lock.get('c2_canonical_blob')!=c2 or len(rows)!=prev*6:raise AssertionError('C2 plan/probe dependency mismatch')
 prior=load(A1)+load(A2)+load(B1)+load(B2)+load(C1)+rows;pids={t['id'] for r in prior for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};pforms={t['form'] for r in prior for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};fresh=[]
 with LEX3.open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   form=(row.get('Front') or '').strip();b=row.get('Back') or '';mr=re.search(r'Rank:\s*(\d+)',b);mm=re.search(r'Meaning:\s*(.+)',b);mp=re.search(r'Part of speech:\s*(.+)',b)
   if not form or not mr:continue
   rank=int(mr.group(1));tid=f'fr-rank-{rank:04d}'
   if rank<=1000:continue
   if tid in pids or form in pforms:continue
   fresh.append({'form':form,'status':'fresh','rank':rank,'id':tid,'meaning':mm.group(1).strip() if mm else None,'part_of_speech':mp.group(1).strip() if mp else None,'source_lexicon':'french_top3000.csv'})
 if len(fresh)<25:raise AssertionError(f'C2 advanced source continuation too small: {len(fresh)}')
 out={'status':'PASS','scope':f'French C2 Unit{u:02d} exhaustive advanced target probe','c1_canonical_blob':plan['c1_canonical_blob'],'c2_source_blob':c2,'theme':plan['theme'],'genres':plan['genres'],'word_band':[plan['c2_word_min'],plan['c2_word_max']],'durable_lexical_planning_band':plan['c2_lexical_planning_band'],'accepted_default_new_targets_per_standard_passage':plan['accepted_c2_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':False,'prior_deliberate_targets':len(pids),'fresh_count':len(fresh),'fresh':fresh,'source_policy':'french_top3000.csv rank > 1000 only'}
 (AUD/f'french_c2_unit{u:02d}_target_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','unit':u,'fresh_count':len(fresh),'theme':plan['theme']},ensure_ascii=False))
if __name__=='__main__':main()
