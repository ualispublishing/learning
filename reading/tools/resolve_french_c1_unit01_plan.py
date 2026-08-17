#!/usr/bin/env python3
"""Resolve the canonical C1 Unit01 planning node from topic_genre_matrix.json.

Fails closed on ambiguity. The result is a small auditable artifact that future
C1 writers can depend on without reparsing the entire planning matrix.
"""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];READY=R/'reading/audit/french_c1_readiness.json';MATRIX=R/'reading/planning/topic_genre_matrix.json';B2=R/'reading/french/b2/passages.jsonl';OUT=R/'reading/audit/french_c1_unit01_plan.json'
def walk(obj,path='$'):
 yield path,obj
 if isinstance(obj,dict):
  for k,v in obj.items():yield from walk(v,f'{path}.{k}')
 elif isinstance(obj,list):
  for i,v in enumerate(obj):yield from walk(v,f'{path}[{i}]')
def scalar(v):return isinstance(v,(str,int,float,bool))
def score(path,node):
 if not isinstance(node,dict):return -1
 s=0;pl=path.lower()
 if re.search(r'(^|[.\[_-])c1($|[.\]_-])',pl):s+=8
 if re.search(r'unit[_ -]?0?1|u0?1',pl):s+=8
 for k,v in node.items():
  kl=str(k).lower()
  if kl in {'cefr','level','cefr_level'} and str(v).upper()=='C1':s+=14
  if kl in {'unit','unit_number','unit_no','unit_id'} and str(v).strip().lower() in {'1','01','u01','unit01','unit 01','unit 1'}:s+=14
  if kl in {'theme','topic','title','unit_theme'} and scalar(v):s+=3
  if kl in {'genre','genres','recommended_genres','text_types'}:s+=3
 return s
def extract(node,keys):
 for k in keys:
  if k in node:return node[k]
 for k,v in node.items():
  if str(k).lower() in {x.lower() for x in keys}:return v
 return None
def main():
 ready=json.loads(READY.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if ready.get('status')!='PASS' or ready.get('b2_canonical_blob')!=blob:raise AssertionError('C1 readiness/live B2 mismatch')
 matrix=json.loads(MATRIX.read_text(encoding='utf-8'));cands=[]
 for path,node in walk(matrix):
  sc=score(path,node)
  if sc>=14:cands.append({'score':sc,'path':path,'node':node})
 if not cands:raise AssertionError('No plausible C1 Unit01 planning node found')
 best=max(x['score'] for x in cands);top=[x for x in cands if x['score']==best]
 # Prefer the smallest top-level object that actually contains theme/genre data.
 top.sort(key=lambda x:len(json.dumps(x['node'],ensure_ascii=False)))
 chosen=top[0]
 # Fail if equally scored distinct compact candidates are both plausible C1/U01 nodes.
 if len(top)>1:
  sig0=json.dumps(chosen['node'],ensure_ascii=False,sort_keys=True)
  conflicts=[x for x in top[1:] if json.dumps(x['node'],ensure_ascii=False,sort_keys=True)!=sig0 and abs(len(json.dumps(x['node']))-len(json.dumps(chosen['node'])))<120]
  if conflicts:raise AssertionError(f'Ambiguous C1 Unit01 planning nodes at score {best}: {[x["path"] for x in top[:8]]}')
 node=chosen['node'];theme=extract(node,['theme','unit_theme','topic','title']);genres=extract(node,['genres','recommended_genres','genre','text_types']);domains=extract(node,['domains','domain']);notes=extract(node,['notes','guidance','description','requirements'])
 if theme is None:raise AssertionError(f'C1 Unit01 node lacks explicit theme/topic/title: {chosen["path"]}')
 out={'status':'PASS','scope':'French C1 Unit01 canonical planning resolution','b2_canonical_blob':blob,'c1_word_min':ready['c1_word_min'],'c1_word_max':ready['c1_word_max'],'matrix_path':chosen['path'],'matrix_score':chosen['score'],'theme':theme,'genres':genres,'domains':domains,'notes':notes,'canonical_node':node,'note':'Resolved from canonical topic_genre_matrix.json; future C1 Unit01 calibration must use this artifact and fail closed on B2/plan drift.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','path':chosen['path'],'theme':theme,'genres':genres,'word_band':[ready['c1_word_min'],ready['c1_word_max']]},ensure_ascii=False))
if __name__=='__main__':main()
