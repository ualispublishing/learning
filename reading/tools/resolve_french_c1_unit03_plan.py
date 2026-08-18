#!/usr/bin/env python3
"""Resolve canonical French C1 Unit03 from the exact levels.C1 branch."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit02_frontier_lock.json';READY=R/'reading/audit/french_c1_readiness.json';MATRIX=R/'reading/planning/topic_genre_matrix.json';OUT=R/'reading/audit/french_c1_unit03_plan.json'
def extract(node,keys):
 low={str(k).lower():v for k,v in node.items()}
 for k in keys:
  if k.lower() in low:return low[k.lower()]
 return None
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));ready=json.loads(READY.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=12 or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 Unit02 lock/live mismatch')
 if ready.get('status')!='PASS' or ready.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 readiness stale')
 matrix=json.loads(MATRIX.read_text(encoding='utf-8'));levels=matrix.get('levels')
 if not isinstance(levels,dict) or not isinstance(levels.get('C1'),list):raise AssertionError('topic_genre_matrix lacks explicit levels.C1 list')
 matches=[]
 for i,node in enumerate(levels['C1']):
  if not isinstance(node,dict):continue
  unit=node.get('unit',node.get('unit_number',node.get('unit_no')))
  if str(unit).strip().lower() in {'3','03','u03','unit03','unit 03','unit 3'}:matches.append((i,node))
 if len(matches)!=1:raise AssertionError(f'Expected exactly one levels.C1 Unit03 node, found {len(matches)}')
 idx,node=matches[0];path=f'$.levels.C1[{idx}]';theme=extract(node,['theme','unit_theme','topic','title']);genres=extract(node,['genres','recommended_genres','genre','text_types']);domains=extract(node,['domains','domain']);notes=extract(node,['notes','guidance','description','requirements'])
 if not isinstance(theme,str) or not theme.strip():raise AssertionError(f'C1 Unit03 node lacks explicit theme at {path}')
 out={'status':'PASS','scope':'French C1 Unit03 canonical planning resolution','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'c1_unit02_lock':'reading/audit/french_c1_unit02_frontier_lock.json','c1_word_min':ready['c1_word_min'],'c1_word_max':ready['c1_word_max'],'matrix_path':path,'theme':theme,'genres':genres,'domains':domains,'notes':notes,'canonical_node':node,'accepted_c1_default_new_targets_per_standard_passage':lock['accepted_c1_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':False,'note':'Resolved from exact canonical levels.C1 Unit03 node after Unit02 generation seal.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','path':path,'theme':theme,'genres':genres},ensure_ascii=False))
if __name__=='__main__':main()
