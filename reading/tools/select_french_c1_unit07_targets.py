#!/usr/bin/env python3
"""Curated fresh target selection for C1 Unit07: literature and cultural criticism."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit06_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit07_plan.json';PROBE=R/'reading/audit/french_c1_unit07_target_probe.json';OUT=R/'reading/audit/french_c1_unit07_target_selection.json'
SELECTION=[('p01_memory','souvenir'),('p01_dream','rêve'),('p01_mind','esprit'),('p01_inner','âme'),('p02_laughter','rire'),('p02_tears','pleurer'),('p02_tone','triste'),('p02_pride','fier'),('p03_king','roi'),('p03_lord','seigneur'),('p03_lady','dame'),('p03_horse','cheval'),('p04_sing','chanter'),('p04_dance','danser'),('p04_festival','fête'),('p04_evening','soirée'),('p05_piece','pièce'),('p05_face','face'),('p05_inside','dedans'),('p05_across','travers')]
def main():
 lock=json.loads(LOCK.read_text());plan=json.loads(PLAN.read_text());probe=json.loads(PROBE.read_text());c1=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=36 or lock.get('c1_canonical_blob')!=c1 or lock.get('b2_canonical_blob')!=b2:raise AssertionError('Unit06 lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1 or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1:raise AssertionError('Unit07 plan/probe stale')
 fresh={x['form']:x for x in probe['fresh']};selected=[];used=set()
 for slot,form in SELECTION:
  if form not in fresh:raise AssertionError(f'Unit07 curated target not fresh/source-backed: {form}')
  if form in used:raise AssertionError('duplicate Unit07 target');used.add(form);x=dict(fresh[form]);x.update({'slot':slot,'semantic_fallback':False,'pedagogical_content_word':True});selected.append(x)
 groups={k:[x['form'] for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit07 target structure failure')
 OUT.write_text(json.dumps({'status':'PASS','scope':'French C1 Unit07 pedagogical target selection','b2_canonical_blob':b2,'c1_source_blob':c1,'theme':plan['theme'],'genres':plan['genres'],'word_band':[plan['c1_word_min'],plan['c1_word_max']],'new_targets_per_standard_passage':4,'default_is_hard_quota':False,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':0,'pedagogical_filter':'literary memory/interiority, tone, historical-symbolic figures, performance culture, and close-reading spatial/form vocabulary'},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','groups':groups},ensure_ascii=False))
if __name__=='__main__':main()
