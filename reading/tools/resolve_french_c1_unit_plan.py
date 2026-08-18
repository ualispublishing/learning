#!/usr/bin/env python3
"""Generic exact-branch C1 unit-plan resolver for target Units 02-10.

Set C1_UNIT to the target unit. Requires the exact previous-unit frontier lock and
resolves only within topic_genre_matrix['levels']['C1']; cross-level heuristic
matching is forbidden.
"""
from __future__ import annotations
import json,os,subprocess
from pathlib import Path
U=int(os.environ.get('C1_UNIT','0'))
if not 2<=U<=10:raise SystemExit('C1_UNIT must be target unit 2..10')
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/f'reading/audit/french_c1_unit{U-1:02d}_frontier_lock.json';READY=R/'reading/audit/french_c1_readiness.json';MATRIX=R/'reading/planning/topic_genre_matrix.json';OUT=R/f'reading/audit/french_c1_unit{U:02d}_plan.json'
def extract(node,keys):
 low={str(k).lower():v for k,v in node.items()}
 for k in keys:
  if k.lower() in low:return low[k.lower()]
 return None
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));ready=json.loads(READY.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip();prev=(U-1)*6
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=prev or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'C1 Unit{U-1:02d} lock/live mismatch')
 if ready.get('status')!='PASS' or ready.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 readiness stale')
 matrix=json.loads(MATRIX.read_text(encoding='utf-8'));levels=matrix.get('levels')
 if not isinstance(levels,dict) or not isinstance(levels.get('C1'),list):raise AssertionError('topic_genre_matrix lacks explicit levels.C1 list')
 matches=[]
 for i,node in enumerate(levels['C1']):
  if not isinstance(node,dict):continue
  unit=node.get('unit',node.get('unit_number',node.get('unit_no')))
  if str(unit).strip().lower() in {str(U),f'{U:02d}',f'u{U:02d}',f'unit{U:02d}',f'unit {U:02d}',f'unit {U}'}:matches.append((i,node))
 if len(matches)!=1:raise AssertionError(f'Expected exactly one levels.C1 Unit{U:02d} node, found {len(matches)}')
 idx,node=matches[0];path=f'$.levels.C1[{idx}]';theme=extract(node,['theme','unit_theme','topic','title']);genres=extract(node,['genres','recommended_genres','genre','text_types']);domains=extract(node,['domains','domain']);notes=extract(node,['notes','guidance','description','requirements'])
 if not isinstance(theme,str) or not theme.strip():raise AssertionError(f'C1 Unit{U:02d} node lacks explicit theme at {path}')
 out={'status':'PASS','scope':f'French C1 Unit{U:02d} canonical planning resolution','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'previous_frontier_lock':f'reading/audit/french_c1_unit{U-1:02d}_frontier_lock.json','c1_word_min':ready['c1_word_min'],'c1_word_max':ready['c1_word_max'],'matrix_path':path,'theme':theme,'genres':genres,'domains':domains,'notes':notes,'canonical_node':node,'accepted_c1_default_new_targets_per_standard_passage':lock['accepted_c1_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':False,'note':f'Resolved from exact canonical levels.C1 Unit{U:02d} node after Unit{U-1:02d} lock.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','unit':U,'path':path,'theme':theme,'genres':genres},ensure_ascii=False))
if __name__=='__main__':main()
