import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a1_u09_metalinguistic_repair_2026-08-20.json'; POST=ROOT/'reading/audit/arabic_a1_u09_metalinguistic_postrepair_2026-08-20.json'; EXPECTED='d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b'
R={
('ar-a1-u09-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «كرة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت كرة صغيرة، أي جملة أنسب: «هذه كرة صغيرة» أم «هذا كرة صغيرة»؟','t':'grammar_choice','a':'هذه كرة صغيرة.','e':'«كرة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a1-u09-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «مباراة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت مباراة قصيرة، أي جملة أنسب: «هذه مباراة قصيرة» أم «هذا مباراة قصيرة»؟','t':'grammar_choice','a':'هذه مباراة قصيرة.','e':'«مباراة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a1-u09-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «أصدقاء» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان أمامك أكثر من صديق، أي عبارة أنسب: «هؤلاء أصدقاء» أم «هذا أصدقاء»؟','t':'grammar_choice','a':'هؤلاء أصدقاء.','e':'«أصدقاء» جمع لأشخاص، لذلك نستخدم «هؤلاء» هنا.'},
('ar-a1-u09-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «هدف» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت هدفًا واضحًا، أي جملة أنسب: «هذا هدف واضح» أم «هذه هدف واضح»؟','t':'grammar_choice','a':'هذا هدف واضح.','e':'«هدف» مذكر، لذلك نستخدم معه «هذا».'},
('ar-a1-u09-p06','q9'):{'op':'ماذا يعني «هدف» خارج نتيجة المباراة أيضًا؟','ot':'grammar_function','oa':'غاية أو شيء يريد الشخص الوصول إليه.','p':'إذا كنت تتحدث عن شيء تريد الوصول إليه، أي عبارة أنسب: «هذا هدفي» أم «هذا فوزي»؟','t':'grammar_choice','a':'هذا هدفي.','e':'«هدف» يمكن أن يعني غاية يريد الشخص الوصول إليها، لا نقطة في مباراة فقط.'}}
FORMAL={'grammar_category','grammar_function','grammar_identification','person_form'}; PATS=[re.compile(r'التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+«|ما\s+نوع\s+كلمة'),re.compile(r'الوظيفة\s+النحوية|ما\s+وظيفة\s+«|ما\s+وظيفة\s+كلمة|ما\s+الدور\s+النحوي')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before=sha(PATH)
 if before!=EXPECTED: raise SystemExit(f'hash drift {before}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]; applied=[]
 for p in rows:
  amap={a['question_id']:a for a in p.get('answer_key',[])}; changed=0
  for q in p.get('questions',[]):
   k=(p['id'],q['id']); s=R.get(k)
   if not s: continue
   a=amap[q['id']]
   if q.get('prompt')!=s['op'] or q.get('type')!=s['ot'] or a.get('answer')!=s['oa']: raise SystemExit(f'precondition mismatch {k}')
   applied.append({'passage_id':p['id'],'question_id':q['id'],'before':{'prompt':q['prompt'],'type':q['type'],'answer':a['answer']},'after':{'prompt':s['p'],'type':s['t'],'answer':s['a'],'explanation':s['e']}})
   q['prompt']=s['p']; q['type']=s['t']; a['answer']=s['a']; a['explanation']=s['e']; changed+=1
  if changed: p['revision']=int(p.get('revision',0))+1
 if len(applied)!=5: raise SystemExit(f'expected 5 got {len(applied)}')
 unit=[p for p in rows if p.get('unit')==9]; findings=[]; dups=[]; counts=Counter()
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(49,55)): raise SystemExit('scope regression')
 for p in unit:
  qs=p.get('questions',[]); ans=p.get('answer_key',[])
  if len(qs)!=10 or len(ans)!=10: findings.append({'passage_id':p['id'],'kind':'cardinality'})
  if {q.get('id') for q in qs}!={a.get('question_id') for a in ans}: findings.append({'passage_id':p['id'],'kind':'linkage'})
  seen={}
  for q in qs:
   typ=q.get('type'); counts[typ]+=1; prompt=(q.get('prompt') or '').strip()
   if typ in FORMAL: findings.append({'passage_id':p['id'],'question_id':q.get('id'),'kind':'formal_question_type','type':typ,'prompt':prompt})
   if any(pat.search(prompt) for pat in PATS): findings.append({'passage_id':p['id'],'question_id':q.get('id'),'kind':'explicit_formal_metalinguistic_pattern','type':typ,'prompt':prompt})
   key=re.sub(r'\s+',' ',prompt)
   if key in seen: dups.append({'passage_id':p['id'],'question_ids':[seen[key],q.get('id')],'prompt':prompt})
   else: seen[key]=q.get('id')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8'); after=sha(PATH)
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':9,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'repairs_applied':5,'passage_text_changed':False,'untouched_passage':'ar-a1-u09-p04 had no finding in the formal-item inventory and was not changed.','repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_UNIT09' if not findings and not dups else 'FAIL'; POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':9,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':5,'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_UNIT09': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
