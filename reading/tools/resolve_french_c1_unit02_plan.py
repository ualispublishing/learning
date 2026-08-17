#!/usr/bin/env python3
"""Resolve the canonical French C1 Unit02 planning node after Unit01 is locked."""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit01_frontier_lock.json';READY=R/'reading/audit/french_c1_readiness.json';MATRIX=R/'reading/planning/topic_genre_matrix.json';OUT=R/'reading/audit/french_c1_unit02_plan.json'
def walk(obj,path='$'):
 yield path,obj
 if isinstance(obj,dict):
  for k,v in obj.items():yield from walk(v,f'{path}.{k}')
 elif isinstance(obj,list):
  for i,v in enumerate(obj):yield from walk(v,f'{path}[{i}]')
def score(path,node):
 if not isinstance(node,dict):return -1
 s=0;pl=path.lower()
 if re.search(r'(^|[.\[_-])c1($|[.\]_-])',pl):s+=8
 if re.search(r'unit[_ -]?0?2|u0?2',pl):s+=8
 for k,v in node.items():
  kl=str(k).lower();sv=str(v).strip().lower()
  if kl in {'cefr','level','cefr_level'} and sv=='c1':s+=14
  if kl in {'unit','unit_number','unit_no','unit_id'} and sv in {'2','02','u02','unit02','unit 02','unit 2'}:s+=14
  if kl in {'theme','topic','title','unit_theme'}:s+=3
  if kl in {'genre','genres','recommended_genres','text_types'}:s+=3
 return s
def extract(node,keys):
 lk={x.lower() for x in keys}
 for k,v in node.items():
  if str(k).lower() in lk:return v
 return None
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));ready=json.loads(READY.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=6 or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 Unit01 lock/live blob mismatch')
 if ready.get('status')!='PASS' or ready.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 readiness stale')
 matrix=json.loads(MATRIX.read_text(encoding='utf-8'));cands=[]
 for path,node in walk(matrix):
  sc=score(path,node)
  if sc>=14:cands.append({'score':sc,'path':path,'node':node})
 if not cands:raise AssertionError('No plausible C1 Unit02 planning node found')
 best=max(x['score'] for x in cands);top=[x for x in cands if x['score']==best];top.sort(key=lambda x:len(json.dumps(x['node'],ensure_ascii=False)));chosen=top[0]
 if len(top)>1:
  sig=json.dumps(chosen['node'],ensure_ascii=False,sort_keys=True);conf=[x for x in top[1:] if json.dumps(x['node'],ensure_ascii=False,sort_keys=True)!=sig and abs(len(json.dumps(x['node']))-len(json.dumps(chosen['node'])))<120]
  if conf:raise AssertionError(f'Ambiguous C1 Unit02 planning nodes: {[x["path"] for x in top[:8]]}')
 node=chosen['node'];theme=extract(node,['theme','unit_theme','topic','title']);genres=extract(node,['genres','recommended_genres','genre','text_types']);domains=extract(node,['domains','domain']);notes=extract(node,['notes','guidance','description','requirements'])
 if theme is None:raise AssertionError(f'C1 Unit02 node lacks explicit theme/topic/title: {chosen["path"]}')
 out={'status':'PASS','scope':'French C1 Unit02 canonical planning resolution','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'c1_unit01_lock':'reading/audit/french_c1_unit01_frontier_lock.json','c1_word_min':ready['c1_word_min'],'c1_word_max':ready['c1_word_max'],'matrix_path':chosen['path'],'matrix_score':chosen['score'],'theme':theme,'genres':genres,'domains':domains,'notes':notes,'canonical_node':node,'accepted_c1_default_new_targets_per_standard_passage':lock['accepted_c1_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':False,'note':'Resolved from canonical topic_genre_matrix.json after calibrated Unit01 lock.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','path':chosen['path'],'theme':theme,'genres':genres,'word_band':[ready['c1_word_min'],ready['c1_word_max']]},ensure_ascii=False))
if __name__=='__main__':main()
