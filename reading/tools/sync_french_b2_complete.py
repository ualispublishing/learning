#!/usr/bin/env python3
"""Advance durable project state from complete B2 generation integrity to C1 calibration."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';AUDIT=R/'reading/audit/french_b2_generation_integrity.json';STATUS=R/'reading/STATUS.json';TASKS=R/'reading/TASKS.md';HANDOFF=R/'reading/AGENT_HANDOFF.md'
def main():
 audit=json.loads(AUDIT.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if audit.get('status')!='PASS' or audit.get('passages')!=60 or audit.get('questions')!=600 or audit.get('answers')!=600 or audit.get('unique_new_target_forms')!=200 or audit.get('canonical_blob')!=blob:raise AssertionError('B2 generation-integrity audit/live blob mismatch')
 s=json.loads(STATUS.read_text(encoding='utf-8'));fr=s['french'];b=fr['b2_generation']
 # Permit either Unit08 or Unit09 synced durable status; the canonical audit is stronger.
 if b.get('last_sequence',0)>60:raise AssertionError('unexpected B2 durable state')
 s['updated']='2026-08-17';s['phase']='Arabic A1-C2 is formally approved. French A1, A2, B1 and B2 are generated; B1 and B2 generation-integrity are PASS. French C1 Unit 01 calibration is next.'
 fr['canonical_passages']=240;fr['questions']=2400;fr['answers']=2400;fr['levels']['b2']=60
 b['passages']=60;b['questions']=600;b['answers']=600;b['completed_units']=list(range(1,11));b['last_sequence']=60;b['canonical_blob']=blob;b['generation_integrity_status']='PASS';b['generation_integrity_artifact']='reading/audit/french_b2_generation_integrity.json';b['unique_new_targets']=200;b['checkpoint_sequences_zero_new']=[6,12,18,24,30,36,42,48,54,60]
 fr['next_target']='Calibrate French C1 Unit 01 / sequences 1-6 from the canonical C1 passage standard and topic/genre matrix. Derive the exact C1 word band and planning constraints from repository policy first; probe all remaining source vocabulary against A1-B2; choose a conservative fresh target load; generate P01-P05 plus zero-new P06; run a strict post-calibration review before setting a C1 production default.'
 s['next_actions']=['keep Arabic sealed unless canonical Arabic changes','do not broadly regenerate French A1-B2','extract/validate canonical C1 standards and topic matrix after the B2 integrity seal','calibrate French C1 Unit01 before setting the C1 production default','continue generation-first through C1-C2 before the final whole-French multi-pass audit','keep Urdu unchanged while French is active unless explicitly reprioritized']
 for p in ['reading/audit/french_b2_generation_integrity.json','reading/audit/french_c1_readiness.json']:
  if p not in s['important_files']:s['important_files'].append(p)
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 t=TASKS.read_text(encoding='utf-8')
 marker='## Urdu — QUEUED'
 if marker not in t:raise AssertionError('TASKS Urdu anchor missing')
 # Replace whatever current B2 immediate section remains with one authoritative completion section.
 starts=[x for x in ('#### Unit 08 — IMMEDIATE NEXT','#### Unit 09 — IMMEDIATE NEXT','#### Unit 10 — IMMEDIATE NEXT') if x in t]
 if starts:
  start=min(t.index(x) for x in starts);end=t.index('\n'+marker,start)
  block=f'''#### B2 — COMPLETE / GENERATION-INTEGRITY PASS\n- [x] 60 passages / 600 questions / 600 answers.\n- [x] 10 units; P01–P05 use 4 fresh targets each; all ten P06 checkpoints zero-new.\n- [x] 200 unique B2 deliberate target IDs/forms with zero A1–B1 collisions.\n- [x] Full B2 generation-integrity artifact: `reading/audit/french_b2_generation_integrity.json` = PASS.\n- [x] Canonical B2 blob: `{blob}`.\n- [x] Final whole-French multi-pass audit remains deferred until C1–C2 generation is complete.\n\n#### C1 Unit 01 — IMMEDIATE NEXT / CALIBRATION\n- [ ] Derive exact C1 word band and discourse/genre constraints from canonical repository policy.\n- [ ] Run an exhaustive remaining-vocabulary freshness probe against A1–B2.\n- [ ] Choose a conservative calibration target load; do not assume the B2 default carries forward.\n- [ ] Generate sequences 1–6 with P06 zero-new and 10 linked Q/A each.\n- [ ] Run strict language, pedagogy, source, exposure and structural review before setting the C1 default.\n\nRemaining French generation:\n- [ ] C1: 60 passages.\n- [ ] C2: 60 passages.\n'''
  t=t[:start]+block+t[end:]
 # Normalize active next line if a B2 one remains.
 import re
 t=re.sub(r'\*\*Generate French B2 Unit [0-9]+[^\n]*\*\*','**Calibrate French C1 Unit 01 from the canonical C1 standard and topic matrix after the B2 generation-integrity seal. Keep Arabic sealed.**',t,count=1)
 TASKS.write_text(t,encoding='utf-8')
 h=HANDOFF.read_text(encoding='utf-8')
 # Append a durable completion block rather than depending on a brittle current heading number.
 if '## French B2 — COMPLETE / GENERATION-INTEGRITY PASS' not in h:
  h += f'''\n\n## French B2 — COMPLETE / GENERATION-INTEGRITY PASS\n\n- Canonical B2 blob `{blob}`.\n- 60 passages / 600 questions / 600 answers.\n- 200 unique B2 deliberate targets; zero prior-level collisions.\n- checkpoints 6,12,18,24,30,36,42,48,54,60 are zero-new.\n- artifact `reading/audit/french_b2_generation_integrity.json` = PASS.\n- This is a generation seal, not the deferred final whole-French multi-pass audit.\n\n### Immediate frontier — French C1 Unit 01 calibration\n\nRead the canonical C1 passage standard and topic/genre matrix first. Derive the exact word band and production constraints; run an exhaustive freshness probe against all A1–B2 deliberate targets; choose a conservative calibration lexical load rather than copying B2 by assumption; generate sequences 1–6 with P06 zero-new and 10 linked Q/A; then run a strict post-calibration language/pedagogy/integrity review before setting the C1 production default.\n'''
 HANDOFF.write_text(h,encoding='utf-8')
 print(json.dumps({'status':'PASS','french_passages':240,'french_questions':2400,'b2_blob':blob,'next':'C1 Unit01 calibration'},ensure_ascii=False))
if __name__=='__main__':main()
