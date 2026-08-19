#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
C1=R/'reading/french/c1/passages.jsonl'; C2=R/'reading/french/c2/passages.jsonl'
LOCK=R/'reading/audit/french_c2_unit07_frontier_lock.json'; PLAN=R/'reading/audit/french_c2_unit08_plan.json'; PROBE=R/'reading/audit/french_c2_unit08_target_probe.json'; OUT=R/'reading/audit/french_c2_unit08_target_selection.json'

# Five source-critique clusters. The generator will use fictional archives/cases
# so the exercise can focus on evidence and historiography without unsourced
# claims about real disputed events.
SELECTION=[
 ('p01_period','période'),('p01_document','document'),('p01_discussion','discussion'),('p01_boundary','frontière'),('p01_witness','témoigner'),
 ('p02_rumor','rumeur'),('p02_version','version'),('p02_event','événement'),('p02_possibility','possibilité'),('p02_failure','échec'),
 ('p03_painting','peinture'),('p03_imprint','empreinte'),('p03_copy','copie'),('p03_clue','indice'),('p03_property','propriété'),
 ('p04_shock','choc'),('p04_wager','pari'),('p04_mood','humeur'),('p04_reputation','réputation'),('p04_really','réellement'),
 ('p05_approach','approche'),('p05_common','commun'),('p05_previous','précédemment'),('p05_flag','signaler'),('p05_following','suivant')]

def h(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def main():
 l=json.loads(LOCK.read_text(encoding='utf-8')); p=json.loads(PLAN.read_text(encoding='utf-8')); q=json.loads(PROBE.read_text(encoding='utf-8')); c1=h(C1); c2=h(C2)
 if l.get('status')!='PASS' or l.get('last_sequence')!=42 or l.get('c1_canonical_blob')!=c1 or l.get('c2_canonical_blob')!=c2: raise AssertionError('C2 Unit07 lock/live mismatch')
 if p.get('status')!='PASS' or p.get('c2_source_blob')!=c2 or q.get('status')!='PASS' or q.get('c2_source_blob')!=c2: raise AssertionError('C2 Unit08 plan/probe stale')
 fresh={x['form']:x for x in q['fresh']}; sel=[]; seen=set()
 for slot,f in SELECTION:
  if f not in fresh: raise AssertionError(f'C2 Unit08 target not fresh/source-backed: {f}')
  x=fresh[f]
  if x.get('rank',0)<=1000 or x.get('source_lexicon')!='french_top3000.csv': raise AssertionError(f'advanced source invalid: {f}')
  if f in seen: raise AssertionError(f'duplicate target: {f}')
  seen.add(f); y=dict(x); y.update({'slot':slot,'semantic_fallback':False,'pedagogical_content_word':True}); sel.append(y)
 groups={k:[x['form'] for x in sel if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(sel)!=25 or any(len(v)!=5 for v in groups.values()): raise AssertionError(f'Unit08 target structure failure: {groups}')
 OUT.write_text(json.dumps({'status':'PASS','scope':'French C2 Unit08 pedagogical target selection','c1_canonical_blob':c1,'c2_source_blob':c2,'theme':p['theme'],'genres':p['genres'],'word_band':[p['c2_word_min'],p['c2_word_max']],'new_targets_per_standard_passage':l['accepted_c2_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'selected_count':25,'selected':sel,'passage_groups':groups,'source_policy':'validated french_top3000.csv continuation rank > 1000','semantic_fallback_count':0,'pedagogical_filter':'chronology and source provenance; competing versions and causal alternatives; material-source interpretation; shocks versus structural explanation; synthesis with explicit scope and uncertainty','historical_fact_policy':'fictional archival cases for contested reasoning; no unsupported factual claim about a real disputed historical event'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':'PASS','selected_count':25,'groups':groups},ensure_ascii=False))
if __name__=='__main__': main()
