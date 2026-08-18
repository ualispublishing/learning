#!/usr/bin/env python3
"""Curated C2 Unit01 targets from the validated rank-1001+ continuation."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';READY=R/'reading/audit/french_c2_readiness.json';PROBE=R/'reading/audit/french_c2_unit01_target_probe.json';OUT=R/'reading/audit/french_c2_unit01_target_selection.json'
SELECTION=[
 ('p01_real','réel'),('p01_reality','réalité'),('p01_term','terme'),('p01_thought','pensée'),('p01_identity','identité'),
 ('p02_necessary','nécessaire'),('p02_importance','importance'),('p02_depend','dépendre'),('p02_opposite','contraire'),('p02_weak','faible'),
 ('p03_judge','juger'),('p03_justice','justice'),('p03_intention','intention'),('p03_consider','considérer'),('p03_claim','prétendre'),
 ('p04_represent','représenter'),('p04_link','lien'),('p04_connect','lier'),('p04_identify','identifier'),('p04_main','principal'),
 ('p05_certainly','certainement'),('p05_support','soutenir'),('p05_confirm','confirmer'),('p05_resolve','résoudre'),('p05_useful','utile')]
def main():
 ready=json.loads(READY.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));c1=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip()
 if ready.get('status')!='PASS' or ready.get('c1_canonical_blob')!=c1 or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1:raise AssertionError('C2 readiness/probe not locked to live C1')
 if ready.get('c2_word_min')!=700 or ready.get('c2_word_max')!=1200:raise AssertionError('unexpected C2 word band')
 band=ready.get('c2_lexical_planning_band');
 if not isinstance(band,list) or band[1]<5:raise AssertionError('C2 lexical standard does not support conservative 5-target calibration')
 fresh={x['form']:x for x in probe['fresh']};sel=[];seen=set()
 for slot,f in SELECTION:
  if f not in fresh:raise AssertionError(f'C2 Unit01 curated target not fresh/source-backed: {f}')
  x=fresh[f]
  if x.get('rank',0)<=1000 or x.get('source_lexicon')!='french_top3000.csv':raise AssertionError(f'C2 target must come from validated continuation: {f}')
  if f in seen:raise AssertionError(f'duplicate C2 target: {f}')
  seen.add(f);y=dict(x);y.update({'slot':slot,'semantic_fallback':False,'pedagogical_content_word':True});sel.append(y)
 groups={k:[x['form'] for x in sel if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(sel)!=25 or any(len(v)!=5 for v in groups.values()):raise AssertionError(f'C2 target structure failure {groups}')
 out={'status':'PASS','scope':'French C2 Unit01 calibration target selection','c1_source_blob':c1,'theme':ready['unit01_theme'],'genres':ready['unit01_genres'],'word_band':[ready['c2_word_min'],ready['c2_word_max']],'durable_lexical_planning_band':ready['c2_lexical_planning_band'],'calibration_new_targets_per_standard_passage':5,'calibration_default_is_hard_quota':False,'selected_count':25,'selected':sel,'passage_groups':groups,'source_policy':'validated french_top3000.csv continuation only (rank > 1000)','semantic_fallback_count':0,'note':'Five is a conservative C2 calibration candidate below the maximum planning band; strict post-calibration audit must accept it before production.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','groups':groups},ensure_ascii=False))
if __name__=='__main__':main()
