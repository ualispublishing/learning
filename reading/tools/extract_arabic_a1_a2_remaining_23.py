#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
A1=ROOT/'reading/arabic/a1/passages.jsonl';A2=ROOT/'reading/arabic/a2/passages.jsonl'
SOURCE=ROOT/'reading/audit/arabic_a1_a2_false_review_metadata_repair_2026-08-23.json'
OUT=ROOT/'reading/audit/arabic_a1_a2_remaining_23_2026-08-23.json'
EXPECTED={'a1':'a84ef0bd859e82f3cd85e136c1b9750108d4b1ed','a2':'510baee0040d4bb78272d966666fb62b926b3b8c'}
def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 actual={'a1':blob(A1),'a2':blob(A2)}
 if actual!=EXPECTED:raise SystemExit(f'unexpected blobs {actual}')
 src=json.loads(SOURCE.read_text(encoding='utf-8'))
 blockers=src.get('new_target_blockers',[])+src.get('exposure_count_blockers',[])
 if len(blockers)!=23:raise SystemExit(f'expected 23 blockers, got {len(blockers)}')
 rows={'a1':load(A1),'a2':load(A2)};idx={l:{r['id']:r for r in rs} for l,rs in rows.items()}
 items=[]
 for n,b in enumerate(blockers,1):
  pid=b['passage_id'];level='a1' if '-a1-' in pid else 'a2';r=idx[level][pid];tid=b['target_id']
  new=next((t for t in r.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==tid),None)
  review=next((t for t in r.get('review_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==tid),None)
  qs=[]
  for q in r.get('questions',[]):
   if tid in (q.get('target_ids') or []):
    a=next((a for a in r.get('answer_key',[]) if a.get('question_id')==q.get('id')),None)
    qs.append({'question':q,'answer':a})
  items.append({
   'blocker_id':f'AR23-{n:02d}','kind':'new_target_realization' if b in src.get('new_target_blockers',[]) else 'exposure_count_contract',
   'level':level,'passage_id':pid,'unit':r.get('unit'),'sequence':r.get('sequence'),'title':r.get('title'),'target_id':tid,
   'target_record':new or review,'source_blocker':b,'text':r.get('text'),'questions_assessing_target':qs,
   'decision':{'status':'pending','action':None,'rationale':None,'learner_text_change':None,'metadata_change':None}
  })
 out={'schema_version':1,'date':'2026-08-23','input_blobs':actual,'count':len(items),'new_target_realization_count':len(src.get('new_target_blockers',[])),'exposure_count_contract_count':len(src.get('exposure_count_blockers',[])),'items':items}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'count':out['count'],'new_target':out['new_target_realization_count'],'exposure_count':out['exposure_count_contract_count']},ensure_ascii=False))
if __name__=='__main__':main()
