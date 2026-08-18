#!/usr/bin/env python3
"""Sync STATUS/TASKS/HANDOFF after sealed C2 Unit N and prepared Unit N+1."""
from __future__ import annotations
import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C2=R/'reading/french/c2/passages.jsonl';AUD=R/'reading/audit';STATUS=R/'reading/STATUS.json';TASKS=R/'reading/TASKS.md';HANDOFF=R/'reading/AGENT_HANDOFF.md'
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def main():
 u=int(os.environ.get('C2_UNIT','0'))
 if not 1<=u<10:raise AssertionError('C2_UNIT current unit must be 1..9')
 nxt=u+1;lock=json.loads((AUD/f'french_c2_unit{u:02d}_frontier_lock.json').read_text());plan=json.loads((AUD/f'french_c2_unit{nxt:02d}_plan.json').read_text());probe=json.loads((AUD/f'french_c2_unit{nxt:02d}_target_probe.json').read_text());blob=h(C2);rows=[json.loads(x) for x in C2.read_text().splitlines() if x.strip()]
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=u*6 or lock.get('c2_canonical_blob')!=blob or len(rows)!=u*6:raise AssertionError('C2 current lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c2_source_blob')!=blob or probe.get('status')!='PASS' or probe.get('c2_source_blob')!=blob:raise AssertionError('C2 next plan/probe stale')
 s=json.loads(STATUS.read_text());fr=s['french'];fr['canonical_passages']=300+u*6;fr['questions']=3000+u*60;fr['answers']=3000+u*60;fr.setdefault('levels',{})['c2']=u*6;c=fr.setdefault('c2_generation',{});c.update({'status':'GENERATION_IN_PROGRESS_CALIBRATION_SEALED' if u==1 else 'GENERATION_IN_PROGRESS','passages':u*6,'questions':u*60,'answers':u*60,'completed_units':list(range(1,u+1)),'last_sequence':u*6,'canonical_blob':blob,'accepted_default_new_targets_per_standard_passage':lock.get('accepted_c2_default_new_targets_per_standard_passage',5),'accepted_default_is_hard_quota':False,'source_policy':'validated french_top3000.csv continuation rank > 1000','last_frontier_lock':f'reading/audit/french_c2_unit{u:02d}_frontier_lock.json','next_unit':nxt,'next_theme':plan['theme'],'next_genres':plan['genres'],'next_target_probe':f'reading/audit/french_c2_unit{nxt:02d}_target_probe.json','next_fresh_source_terms':probe['fresh_count']});fr['next_target']=f"Generate French C2 Unit {nxt:02d} ({plan['theme']}) from exact sealed C2 blob {blob}; retain 700-1200 words, advanced discourse, calibrated lexical default, 10 Q/A, and zero-new P06.";s['updated']='2026-08-17';s['phase']=f'Arabic sealed. French A1-C1 integrity sealed. French C2 Units01-{u:02d} sealed; Unit{nxt:02d} is next. Final French multi-pass audit remains deferred until C2 completion.'
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 t=TASKS.read_text();key=f'#### French C2 Unit {nxt:02d} — IMMEDIATE NEXT'
 if key not in t:t+=f"\n\n{key}\n- [x] Unit {u:02d} sealed on `{blob}`.\n- [ ] Theme: **{plan['theme']}**; genres: {', '.join(plan['genres'])}.\n- [ ] Select source-backed rank-1001+ targets from `{probe['fresh_count']}` fresh continuation terms.\n- [ ] 700–1,200 words; calibrated lexical default (not quota); 10 linked Q/A; P06 zero-new; strict post-unit audit/lock.\n"
 TASKS.write_text(t);hh=HANDOFF.read_text();key2=f'### French C2 Unit {nxt:02d} frontier'
 if key2 not in hh:hh+=f"\n\n{key2}\n- Unit {u:02d} sealed; canonical C2 blob `{blob}`.\n- Next canonical matrix theme: **{plan['theme']}**; genres: {', '.join(plan['genres'])}.\n- Fresh rank-1001+ continuation terms: {probe['fresh_count']}.\n- Do not weaken C2 word-band, source, exposure, review, linkage, reasoning, or zero-new checkpoint guards.\n"
 HANDOFF.write_text(hh);print(json.dumps({'status':'PASS','completed_unit':u,'next_unit':nxt,'c2_blob':blob,'next_theme':plan['theme']},ensure_ascii=False))
if __name__=='__main__':main()
