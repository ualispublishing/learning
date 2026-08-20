import hashlib, json, re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; OUT=ROOT/'reading/audit/arabic_a1_u02_metalinguistic_postrepair_2026-08-20.json'
EXPECTED='6623ca967269d4d0bfaa4bb3cf8ad99d8156508079f2a79a91fd2f221b9c7805'
FORMAL={'grammar_category','grammar_function','grammar_identification','person_form'}
PATS=[('explicit_classification',re.compile(r'التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+«|ما\s+نوع\s+كلمة')),('explicit_function',re.compile(r'الوظيفة\s+النحوية|ما\s+وظيفة\s+«|ما\s+وظيفة\s+كلمة|ما\s+الدور\s+النحوي'))]
def main():
 bound=hashlib.sha256(PATH.read_bytes()).hexdigest()
 if bound!=EXPECTED: raise SystemExit(f'hash drift {bound}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]; unit=[p for p in rows if p.get('unit')==2]
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(7,13)): raise SystemExit('Unit 02 scope regression')
 findings=[]; dups=[]; counts=Counter()
 for p in unit:
  qs=p.get('questions',[]); ans=p.get('answer_key',[])
  if len(qs)!=10 or len(ans)!=10: findings.append({'passage_id':p['id'],'kind':'cardinality'})
  if {q.get('id') for q in qs}!={a.get('question_id') for a in ans}: findings.append({'passage_id':p['id'],'kind':'linkage'})
  seen={}
  for q in qs:
   typ=q.get('type'); counts[typ]+=1; prompt=(q.get('prompt') or '').strip()
   if typ in FORMAL: findings.append({'passage_id':p['id'],'question_id':q.get('id'),'kind':'formal_question_type','type':typ,'prompt':prompt})
   for name,pat in PATS:
    if pat.search(prompt): findings.append({'passage_id':p['id'],'question_id':q.get('id'),'kind':name,'type':typ,'prompt':prompt})
   key=re.sub(r'\s+',' ',prompt)
   if key in seen: dups.append({'passage_id':p['id'],'question_ids':[seen[key],q.get('id')],'prompt':prompt})
   else: seen[key]=q.get('id')
 out={'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':2,'bound_sha256':bound,'scope':{'records':6,'questions':60,'answers':60},'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':'PASS_DETERMINISTIC_UNIT02' if not findings and not dups else 'FAIL','limitations':'Deterministic/self-review evidence only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':out['status'],'findings':len(findings),'duplicates':len(dups)},ensure_ascii=False))
 if out['status']!='PASS_DETERMINISTIC_UNIT02': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
