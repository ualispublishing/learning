#!/usr/bin/env python3
"""Resolve the canonical C1 Unit01 planning node from topic_genre_matrix.json.

The matrix has an explicit levels.C1 branch, so resolution must use that branch
rather than heuristic scoring across every level's Unit 1. Fails closed unless
exactly one C1 node declares unit=1 and contains an explicit theme.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];READY=R/'reading/audit/french_c1_readiness.json';MATRIX=R/'reading/planning/topic_genre_matrix.json';B2=R/'reading/french/b2/passages.jsonl';OUT=R/'reading/audit/french_c1_unit01_plan.json'

def extract(node,keys):
 for k in keys:
  if k in node:return node[k]
 low={str(k).lower():v for k,v in node.items()}
 for k in keys:
  if k.lower() in low:return low[k.lower()]
 return None

def main():
 ready=json.loads(READY.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if ready.get('status')!='PASS' or ready.get('b2_canonical_blob')!=blob:raise AssertionError('C1 readiness/live B2 mismatch')
 matrix=json.loads(MATRIX.read_text(encoding='utf-8'))
 levels=matrix.get('levels')
 if not isinstance(levels,dict) or 'C1' not in levels or not isinstance(levels['C1'],list):raise AssertionError('topic_genre_matrix lacks explicit levels.C1 list')
 matches=[]
 for i,node in enumerate(levels['C1']):
  if not isinstance(node,dict):continue
  unit=node.get('unit',node.get('unit_number',node.get('unit_no')))
  if str(unit).strip().lower() in {'1','01','u01','unit01','unit 01','unit 1'}:matches.append((i,node))
 if len(matches)!=1:raise AssertionError(f'Expected exactly one levels.C1 Unit01 node, found {len(matches)}')
 idx,node=matches[0];path=f'$.levels.C1[{idx}]'
 theme=extract(node,['theme','unit_theme','topic','title']);genres=extract(node,['genres','recommended_genres','genre','text_types']);domains=extract(node,['domains','domain']);notes=extract(node,['notes','guidance','description','requirements'])
 if not isinstance(theme,str) or not theme.strip():raise AssertionError(f'C1 Unit01 node lacks explicit theme at {path}')
 if genres is not None and not isinstance(genres,(list,str)):raise AssertionError(f'C1 Unit01 genres have unexpected shape at {path}')
 out={'status':'PASS','scope':'French C1 Unit01 canonical planning resolution','b2_canonical_blob':blob,'c1_word_min':ready['c1_word_min'],'c1_word_max':ready['c1_word_max'],'matrix_path':path,'theme':theme,'genres':genres,'domains':domains,'notes':notes,'canonical_node':node,'note':'Resolved from exact canonical levels.C1 Unit01 node; no cross-level heuristic matching is allowed.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','path':path,'theme':theme,'genres':genres,'word_band':[ready['c1_word_min'],ready['c1_word_max']]},ensure_ascii=False))
if __name__=='__main__':main()
