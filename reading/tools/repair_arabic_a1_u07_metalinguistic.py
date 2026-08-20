import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a1_u07_metalinguistic_repair_2026-08-20.json'; POST=ROOT/'reading/audit/arabic_a1_u07_metalinguistic_postrepair_2026-08-20.json'; EXPECTED='d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b'
R={
('ar-a1-u07-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «سماء» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت السماء اليوم، أي جملة أنسب: «السماء رمادية» أم «السماء رمادي»؟','t':'grammar_choice','a':'السماء رمادية.','e':'«سماء» مؤنثة، لذلك يأتي الوصف هنا بصيغة «رمادية».'},
('ar-a1-u07-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «درجة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان تطبيق الطقس يعرض الرقم عشرة للحرارة، أي عبارة أنسب: «عشر درجات» أم «عشر درجة»؟','t':'grammar_choice','a':'عشر درجات.','e':'مع العدد عشرة نستخدم هنا جمع «درجة»: «عشر درجات».'},
('ar-a1-u07-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «قادم» في هذا الاستعمال؟','ot':'grammar_category','oa':'صفة','p':'أي عبارة أنسب عن الأسبوع الذي سيأتي: «الأسبوع القادم» أم «الأسبوع القادمة»؟','t':'grammar_choice','a':'الأسبوع القادم.','e':'«قادم» يوافق «الأسبوع» هنا في التذكير.'},
('ar-a1-u07-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «صباح» في هذا الاستعمال؟','ot':'grammar_category','oa':'ظرف','p':'إذا كان الوقت بعد الاستيقاظ وقبل الظهر، أي عبارة أنسب: «هذا الصباح» أم «هذا المساء»؟','t':'grammar_choice','a':'هذا الصباح.','e':'«الصباح» هو الجزء الأول من اليوم قبل الظهر.'},
('ar-a1-u07-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «ساعة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا بقيت ستين دقيقة، أي عبارة أنسب: «ساعة واحدة» أم «واحد ساعة»؟','t':'grammar_choice','a':'ساعة واحدة.','e':'«ساعة» مؤنثة، لذلك نقول هنا «ساعة واحدة».'},
('ar-a1-u07-p06','q9'):{'op':'ماذا تدل «درجة» في سياق الطقس؟','ot':'grammar_function','oa':'مقدار الحرارة أو البرودة.','p':'إذا كانت الحرارة خمس عشرة وحدة، أي عبارة أنسب: «خمس عشرة درجة» أم «خمس عشرة ساعة»؟','t':'grammar_choice','a':'خمس عشرة درجة.','e':'في سياق الطقس تُستعمل «درجة» لقياس الحرارة.'}}
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
 if len(applied)!=6: raise SystemExit(f'expected 6 got {len(applied)}')
 unit=[p for p in rows if p.get('unit')==7]; findings=[]; dups=[]; counts=Counter()
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(37,43)): raise SystemExit('scope regression')
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
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':7,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'repairs_applied':6,'passage_text_changed':False,'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_UNIT07' if not findings and not dups else 'FAIL'; POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':7,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':6,'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_UNIT07': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
