import hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'
OUT=ROOT/'reading/audit/arabic_a2_formal_inventory_2026-08-21.json'
FORMAL={'grammar_category','grammar_function','grammar_identification','person_form'}
PATS=[re.compile(r'التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+«|ما\s+نوع\s+كلمة'),re.compile(r'الوظيفة\s+النحوية|ما\s+وظيفة\s+«|ما\s+وظيفة\s+كلمة|ما\s+الدور\s+النحوي')]
def main():
 bound=hashlib.sha256(PATH.read_bytes()).hexdigest()
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [p.get('sequence') for p in rows]!=list(range(1,61)): raise SystemExit('A2 structural precondition failed')
 findings=[]; by_unit=defaultdict(int); by_type=Counter()
 for p in rows:
  amap={a.get('question_id'):a for a in p.get('answer_key',[])}
  for q in p.get('questions',[]):
   prompt=q.get('prompt') or ''; typ=q.get('type')
   if typ in FORMAL or any(pat.search(prompt) for pat in PATS):
    a=amap.get(q.get('id'),{})
    findings.append({'unit':p.get('unit'),'sequence':p.get('sequence'),'passage_id':p.get('id'),'question_id':q.get('id'),'type':typ,'prompt':prompt,'answer':a.get('answer'),'explanation':a.get('explanation'),'target_ids':q.get('target_ids',[])})
    by_unit[str(p.get('unit'))]+=1; by_type[typ]+=1
 out={'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','scope':{'records':60,'questions':sum(len(p.get('questions',[])) for p in rows),'answers':sum(len(p.get('answer_key',[])) for p in rows)},'bound_sha256':bound,'finding_count':len(findings),'by_unit':dict(sorted(by_unit.items(),key=lambda x:int(x[0]))),'by_type':dict(by_type),'findings':findings,'status':'INVENTORY_ONLY_NO_REPAIR','release_effect':'Audit evidence only; Arabic remains educator-blocked.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'bound':bound,'count':len(findings),'by_unit':out['by_unit'],'by_type':out['by_type']},ensure_ascii=False))
if __name__=='__main__': main()
