#!/usr/bin/env python3
"""Generic durable-state sync for completed C1 Units 03-09.

Set C1_UNIT=current completed unit. Requires its lock plus next-unit plan/probe.
Unit10 is intentionally excluded because it must transition through a full C1
integrity seal before C2 calibration.
"""
from __future__ import annotations
import json,os,subprocess
from pathlib import Path
U=int(os.environ.get('C1_UNIT','0'))
if not 2<=U<=9:raise SystemExit('C1_UNIT must be completed unit 2..9')
N=U+1;R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/f'reading/audit/french_c1_unit{U:02d}_frontier_lock.json';PLAN=R/f'reading/audit/french_c1_unit{N:02d}_plan.json';PROBE=R/f'reading/audit/french_c1_unit{N:02d}_target_probe.json';STATUS=R/'reading/STATUS.json';TASKS=R/'reading/TASKS.md';HANDOFF=R/'reading/AGENT_HANDOFF.md'
def show(v):return v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,sort_keys=True)
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip();need=U*6
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=need or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'C1 Unit{U:02d} lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1blob or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1blob:raise AssertionError(f'C1 Unit{N:02d} plan/probe stale')
 theme=show(plan.get('theme'));genres=show(plan.get('genres'));default=int(lock['accepted_c1_default_new_targets_per_standard_passage']);lo,hi=plan['c1_word_min'],plan['c1_word_max'];total=240+need
 s=json.loads(STATUS.read_text(encoding='utf-8'));fr=s['french'];fr['canonical_passages']=total;fr['questions']=total*10;fr['answers']=total*10;fr.setdefault('levels',{})['c1']=need;c=fr.setdefault('c1_generation',{});c.update({'status':f'unit{U:02d}_generation_pass','passages':need,'questions':need*10,'answers':need*10,'completed_units':list(range(1,U+1)),'last_sequence':need,'canonical_blob':c1blob,f'unit{U:02d}_frontier_lock':f'reading/audit/french_c1_unit{U:02d}_frontier_lock.json',f'unit{U:02d}_generation_review':f'reading/audit/french_c1_unit{U:02d}_generation_review.json','accepted_default_new_targets_per_standard_passage':default,'accepted_default_is_hard_quota':False,f'unit{N:02d}_plan':f'reading/audit/french_c1_unit{N:02d}_plan.json',f'unit{N:02d}_target_probe':f'reading/audit/french_c1_unit{N:02d}_target_probe.json'});fr['next_target']=f'Generate French C1 Unit {N:02d} / sequences {need+1}-{need+6} against exact C1 blob {c1blob}. Canonical theme: {theme}; genres: {genres}. Default {default} fresh targets per P01-P05, not a hard quota; P06 zero-new. Preserve word band {lo}-{hi}, 10 linked Q/A, source/exposure identity, exact reviews and C1 reasoning quality.';s['phase']=f'Arabic remains sealed. French A1-B2 generation integrity is sealed; French C1 Units 01-{U:02d} are canonical and guarded. C1 Unit {N:02d} is next.';s['updated']='2026-08-17';s['next_actions']=['keep Arabic sealed unless canonical Arabic changes',f'generate French C1 Unit {N:02d} against exact Unit{U:02d} frontier lock','preserve the calibrated C1 default as a default, not quota','continue C1 generation-first through Unit10','defer final whole-French multi-pass audit until C2 generation completes']
 for p in [f'reading/audit/french_c1_unit{U:02d}_generation_review.json',f'reading/audit/french_c1_unit{U:02d}_frontier_lock.json',f'reading/audit/french_c1_unit{N:02d}_plan.json',f'reading/audit/french_c1_unit{N:02d}_target_probe.json']:
  if p not in s.setdefault('important_files',[]):s['important_files'].append(p)
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 t=TASKS.read_text(encoding='utf-8');block=f'''\n\n#### C1 Unit {U:02d} — COMPLETE / GENERATION PASS\n- [x] Sequences {(U-1)*6+1}–{need} canonical; 6 passages / 60 Q / 60 A.\n- [x] Strict generation review and frontier lock PASS.\n- [x] Canonical C1 blob `{c1blob}`.\n\n#### C1 Unit {N:02d} — IMMEDIATE NEXT\n- Theme: **{theme}**.\n- Genres: **{genres}**.\n- [ ] Generate sequences {need+1}–{need+6} against `{c1blob}`.\n- [ ] Default `{default}` fresh targets in P01–P05, not a hard quota; P06 zero-new.\n- [ ] Preserve `{lo}–{hi}` words, 10 linked Q/A and all source/review/C1-quality guards.\n'''
 key=f'#### C1 Unit {U:02d} — COMPLETE / GENERATION PASS'
 if key not in t:
  marker='## Urdu — QUEUED';t=t.replace('\n'+marker,block+'\n'+marker,1) if marker in t else t+block
 TASKS.write_text(t,encoding='utf-8')
 h=HANDOFF.read_text(encoding='utf-8');hkey=f'## French C1 Unit {U:02d} — COMPLETE / CURRENT LOCK'
 if hkey not in h:h+=f'''\n\n{hkey}\n\n- Canonical C1 blob `{c1blob}`; {need} C1 passages / {need*10} Q / {need*10} A.\n- Unit{U:02d} strict review and frontier lock PASS.\n- calibrated default remains `{default}`, not a hard quota.\n\n### Immediate frontier — French C1 Unit {N:02d}\nTheme: **{theme}**. Genres: **{genres}**. Generate sequences {need+1}–{need+6} against `{c1blob}` with `{lo}–{hi}` words, 10 linked Q/A, exact source/review guards and C1 reasoning requirements.\n'''
 HANDOFF.write_text(h,encoding='utf-8');print(json.dumps({'status':'PASS','completed_unit':U,'c1_passages':need,'c1_blob':c1blob,'next_unit':N,'next_theme':theme,'fresh_remaining':probe.get('fresh_count')},ensure_ascii=False))
if __name__=='__main__':main()
