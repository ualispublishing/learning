#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[2]
C1=R/'reading/french/c1/passages.jsonl'; C2=R/'reading/french/c2/passages.jsonl'
LOCK=R/'reading/audit/french_c2_unit06_frontier_lock.json'
PLAN=R/'reading/audit/french_c2_unit07_plan.json'
PROBE=R/'reading/audit/french_c2_unit07_target_probe.json'
OUT=R/'reading/audit/french_c2_unit07_target_selection.json'

SELECTION=[
 ('p01_language','langue'),('p01_translation','traduction'),('p01_translate','traduire'),('p01_expression','expression'),('p01_adaptation','adaptation'),
 ('p02_ear','oreille'),('p02_french','français'),('p02_local','local'),('p02_sensitive','sensible'),('p02_delicate','délicat'),
 ('p03_origin','origine'),('p03_tradition','tradition'),('p03_culture','culture'),('p03_village','village'),('p03_neighbor','voisin'),
 ('p04_essay','essai'),('p04_model','modèle'),('p04_quality','qualité'),('p04_explanation','explication'),('p04_emotion','émotion'),
 ('p05_exchange','échange'),('p05_transmit','transmettre'),('p05_opportunity','occasion'),('p05_gather','réunir'),('p05_community','communauté')]

def h(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()

def main():
 l=json.loads(LOCK.read_text(encoding='utf-8')); p=json.loads(PLAN.read_text(encoding='utf-8')); q=json.loads(PROBE.read_text(encoding='utf-8')); c1=h(C1); c2=h(C2)
 if l.get('status')!='PASS' or l.get('last_sequence')!=36 or l.get('c1_canonical_blob')!=c1 or l.get('c2_canonical_blob')!=c2:
  raise AssertionError('C2 Unit06 lock/live mismatch')
 if p.get('status')!='PASS' or p.get('c2_source_blob')!=c2 or q.get('status')!='PASS' or q.get('c2_source_blob')!=c2:
  raise AssertionError('C2 Unit07 plan/probe stale')
 fresh={x['form']:x for x in q['fresh']}; sel=[]; seen=set()
 for slot,f in SELECTION:
  if f not in fresh: raise AssertionError(f'C2 Unit07 target not fresh/source-backed: {f}')
  x=fresh[f]
  if x.get('rank',0)<=1000 or x.get('source_lexicon')!='french_top3000.csv': raise AssertionError(f'advanced source invalid: {f}')
  if f in seen: raise AssertionError(f'duplicate target: {f}')
  seen.add(f); y=dict(x); y.update({'slot':slot,'semantic_fallback':False,'pedagogical_content_word':True}); sel.append(y)
 groups={k:[x['form'] for x in sel if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(sel)!=25 or any(len(v)!=5 for v in groups.values()): raise AssertionError(f'Unit07 target structure failure: {groups}')
 OUT.write_text(json.dumps({'status':'PASS','scope':'French C2 Unit07 pedagogical target selection','c1_canonical_blob':c1,'c2_source_blob':c2,'theme':p['theme'],'genres':p['genres'],'word_band':[p['c2_word_min'],p['c2_word_max']],'new_targets_per_standard_passage':l['accepted_c2_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'selected_count':25,'selected':sel,'passage_groups':groups,'source_policy':'validated french_top3000.csv continuation rank > 1000','semantic_fallback_count':0,'pedagogical_filter':'translation mechanics and equivalence; sound/register; cultural origin/tradition; comparative criticism; cross-community transmission and reception','copyright_policy':'original examples only; no reproduced literary passages'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':'PASS','selected_count':25,'groups':groups},ensure_ascii=False))
if __name__=='__main__': main()
