#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[2]
C1=R/'reading/french/c1/passages.jsonl'; C2=R/'reading/french/c2/passages.jsonl'
LOCK=R/'reading/audit/french_c2_unit05_frontier_lock.json'
PLAN=R/'reading/audit/french_c2_unit06_plan.json'
PROBE=R/'reading/audit/french_c2_unit06_target_probe.json'
OUT=R/'reading/audit/french_c2_unit06_target_selection.json'

# Nonpartisan institutional vocabulary: review and legality; participation and
# representation; administration and implementation; public scrutiny; and
# risk/tradeoff analysis. All forms are validated against the live fresh probe.
SELECTION=[
 ('p01_ruling','arrêt'),('p01_court','tribunal'),('p01_review','examen'),('p01_cancel','annuler'),('p01_jurisdiction','cour'),
 ('p02_participate','participer'),('p02_will','volonté'),('p02_meeting','rencontre'),('p02_many','nombreux'),('p02_social','social'),
 ('p03_senior','supérieur'),('p03_professional','professionnel'),('p03_train','former'),('p03_employment','emploi'),('p03_add','ajouter'),
 ('p04_journalist','journaliste'),('p04_coverage','couverture'),('p04_note','note'),('p04_receipt','reçu'),('p04_emphasize','insister'),
 ('p05_threat','menace'),('p05_target','cible'),('p05_unit','unité'),('p05_future','avenir'),('p05_concern','souci')]

def h(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()

def main():
 l=json.loads(LOCK.read_text()); p=json.loads(PLAN.read_text()); q=json.loads(PROBE.read_text()); c1=h(C1); c2=h(C2)
 if l.get('status')!='PASS' or l.get('last_sequence')!=30 or l.get('c1_canonical_blob')!=c1 or l.get('c2_canonical_blob')!=c2:
  raise AssertionError('C2 Unit05 lock/live mismatch')
 if p.get('status')!='PASS' or p.get('c2_source_blob')!=c2 or q.get('status')!='PASS' or q.get('c2_source_blob')!=c2:
  raise AssertionError('C2 Unit06 plan/probe stale')
 fresh={x['form']:x for x in q['fresh']}; sel=[]; seen=set()
 for slot,f in SELECTION:
  if f not in fresh: raise AssertionError(f'C2 Unit06 target not fresh/source-backed: {f}')
  x=fresh[f]
  if x.get('rank',0)<=1000 or x.get('source_lexicon')!='french_top3000.csv': raise AssertionError(f'advanced source invalid: {f}')
  if f in seen: raise AssertionError(f'duplicate {f}')
  seen.add(f); y=dict(x); y.update({'slot':slot,'semantic_fallback':False,'pedagogical_content_word':True}); sel.append(y)
 groups={k:[x['form'] for x in sel if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(sel)!=25 or any(len(v)!=5 for v in groups.values()): raise AssertionError(f'Unit06 target structure failure {groups}')
 OUT.write_text(json.dumps({'status':'PASS','scope':'French C2 Unit06 pedagogical target selection','c1_canonical_blob':c1,'c2_source_blob':c2,'theme':p['theme'],'genres':p['genres'],'word_band':[p['c2_word_min'],p['c2_word_max']],'new_targets_per_standard_passage':l['accepted_c2_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'selected_count':25,'selected':sel,'passage_groups':groups,'source_policy':'validated french_top3000.csv continuation rank > 1000','semantic_fallback_count':0,'pedagogical_filter':'institutional review and legality; participation and representation; administration and implementation; public scrutiny and documentation; risk, targets and future tradeoffs; no partisan advocacy'},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':'PASS','selected_count':25,'groups':groups},ensure_ascii=False))

if __name__=='__main__': main()
