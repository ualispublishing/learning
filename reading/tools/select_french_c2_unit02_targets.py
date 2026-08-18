#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';LOCK=R/'reading/audit/french_c2_unit01_frontier_lock.json';PLAN=R/'reading/audit/french_c2_unit02_plan.json';PROBE=R/'reading/audit/french_c2_unit02_target_probe.json';OUT=R/'reading/audit/french_c2_unit02_target_selection.json'
SELECTION=[
 ('p01_article','article'),('p01_contract','contrat'),('p01_act','acte'),('p01_respect','respect'),('p01_scope','concerner'),
 ('p02_accuse','accuser'),('p02_confess','avouer'),('p02_question','interroger'),('p02_source','source'),('p02_signal','signal'),
 ('p03_police','policier'),('p03_detain','enfermer'),('p03_threat','menacer'),('p03_access','accès'),('p03_refer','renvoyer'),
 ('p04_value','valeur'),('p04_oppose','combattre'),('p04_deliver','livrer'),('p04_place','placer'),('p04_cease','cesser'),
 ('p05_break','rompre'),('p05_join','joindre'),('p05_direction','direction'),('p05_change','changement'),('p05_announce','annoncer')]
def main():
 l=json.loads(LOCK.read_text());p=json.loads(PLAN.read_text());q=json.loads(PROBE.read_text());c1=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();c2=subprocess.check_output(['git','hash-object',str(C2)],text=True).strip()
 if l.get('status')!='PASS' or l.get('last_sequence')!=6 or l.get('c1_canonical_blob')!=c1 or l.get('c2_canonical_blob')!=c2:raise AssertionError('C2 Unit01 lock/live mismatch')
 if p.get('status')!='PASS' or p.get('c2_source_blob')!=c2 or q.get('status')!='PASS' or q.get('c2_source_blob')!=c2:raise AssertionError('C2 Unit02 plan/probe stale')
 fresh={x['form']:x for x in q['fresh']};sel=[];seen=set()
 for slot,f in SELECTION:
  if f not in fresh:raise AssertionError(f'C2 Unit02 curated target not fresh/source-backed: {f}')
  x=fresh[f]
  if x.get('rank',0)<=1000 or x.get('source_lexicon')!='french_top3000.csv':raise AssertionError(f'C2 Unit02 target source invalid: {f}')
  if f in seen:raise AssertionError(f'duplicate target {f}')
  seen.add(f);y=dict(x);y.update({'slot':slot,'semantic_fallback':False,'pedagogical_content_word':True});sel.append(y)
 groups={k:[x['form'] for x in sel if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(sel)!=25 or any(len(v)!=5 for v in groups.values()):raise AssertionError(f'C2 Unit02 target structure failure {groups}')
 out={'status':'PASS','scope':'French C2 Unit02 pedagogical target selection','c1_canonical_blob':c1,'c2_source_blob':c2,'theme':p['theme'],'genres':p['genres'],'word_band':[p['c2_word_min'],p['c2_word_max']],'new_targets_per_standard_passage':l['accepted_c2_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'selected_count':25,'selected':sel,'passage_groups':groups,'source_policy':'validated french_top3000.csv continuation rank > 1000','semantic_fallback_count':0,'note':'C2 law/interpretation terms use explicit institutional senses; ordinary forms are not treated as advanced merely by frequency.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','groups':groups},ensure_ascii=False))
if __name__=='__main__':main()
