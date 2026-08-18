#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit08_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit09_plan.json';PROBE=R/'reading/audit/french_c1_unit09_target_probe.json';OUT=R/'reading/audit/french_c1_unit09_target_selection.json'
SELECTION=[('p01_yesterday','hier'),('p01_old','vieux'),('p01_duration','longtemps'),('p01_return','retourner'),('p02_day','journée'),('p02_parent','parent'),('p02_marriage','mariage'),('p02_fire','feu'),('p03_army','armée'),('p03_captain','capitaine'),('p03_camp','camp'),('p03_enemy','ennemi'),('p04_weapon','arme'),('p04_blood','sang'),('p04_fight','battre'),('p04_save','sauver'),('p05_place','endroit'),('p05_there','là-bas'),('p05_bring','amener'),('p05_take','emmener')]
def main():
 l=json.loads(LOCK.read_text());p=json.loads(PLAN.read_text());q=json.loads(PROBE.read_text());c=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if l.get('status')!='PASS' or l.get('last_sequence')!=48 or l.get('c1_canonical_blob')!=c or l.get('b2_canonical_blob')!=b:raise AssertionError('Unit08 lock/live mismatch')
 if p.get('status')!='PASS' or p.get('c1_source_blob')!=c or q.get('status')!='PASS' or q.get('c1_source_blob')!=c:raise AssertionError('Unit09 plan/probe stale')
 fresh={x['form']:x for x in q['fresh']};sel=[];seen=set()
 for slot,f in SELECTION:
  if f not in fresh:raise AssertionError(f'Unit09 curated target not fresh/source-backed: {f}')
  if f in seen:raise AssertionError('Unit09 duplicate target')
  seen.add(f);x=dict(fresh[f]);x.update({'slot':slot,'semantic_fallback':False,'pedagogical_content_word':True});sel.append(x)
 groups={k:[x['form'] for x in sel if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(sel)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit09 target structure failure')
 OUT.write_text(json.dumps({'status':'PASS','scope':'French C1 Unit09 pedagogical target selection','b2_canonical_blob':b,'c1_source_blob':c,'theme':p['theme'],'genres':p['genres'],'word_band':[p['c1_word_min'],p['c1_word_max']],'new_targets_per_standard_passage':4,'default_is_hard_quota':False,'selected_count':20,'selected':sel,'passage_groups':groups,'semantic_fallback_count':0,'pedagogical_filter':'temporal distance, social memory, competing conflict sources, violence/rescue claims, and narrative geography'},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
