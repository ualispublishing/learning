import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a2_u06_metalinguistic_repair_2026-08-21.json'; POST=ROOT/'reading/audit/arabic_a2_u06_metalinguistic_postrepair_2026-08-21.json'
EXPECTED='f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c'
R={
('ar-a2-u06-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «طائرة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت وسيلة السفر الجوية كبيرة، أي جملة أنسب: «هذه طائرة كبيرة» أم «هذا طائرة كبير»؟','t':'grammar_choice','a':'هذه طائرة كبيرة.','e':'«طائرة» مؤنثة، لذلك نستخدم معها «هذه» وتوافقها الصفة «كبيرة».'},
('ar-a2-u06-p01','q7'):{'op':'ما التصنيف النحوي لكلمة «مطار» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان مكان السفر الجوي كبيرًا، أي جملة أنسب: «هذا مطار كبير» أم «هذه مطار كبيرة»؟','t':'grammar_choice','a':'هذا مطار كبير.','e':'«مطار» مذكر، لذلك نستخدم معه «هذا» وتوافقه الصفة «كبير».'},
('ar-a2-u06-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «قطار» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت وسيلة النقل على السكة سريعة، أي جملة أنسب: «هذا قطار سريع» أم «هذه قطار سريعة»؟','t':'grammar_choice','a':'هذا قطار سريع.','e':'«قطار» مذكر، لذلك نستخدم معه «هذا» وتوافقه الصفة «سريع».'},
('ar-a2-u06-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «نقل» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كنت تتحدث عن نظام الحافلات والقطارات في المدينة، أي عبارة أنسب: «النقل العام» أم «ينقل العام»؟','t':'grammar_choice','a':'النقل العام.','e':'«نقل» هنا اسم في عبارة «النقل العام».'},
('ar-a2-u06-p03','q7'):{'op':'ما التصنيف النحوي لكلمة «وسائل» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت هناك طرق نقل متعددة، أي جملة أنسب: «هذه وسائل نقل مختلفة» أم «هؤلاء وسائل نقل مختلفون»؟','t':'grammar_choice','a':'هذه وسائل نقل مختلفة.','e':'«وسائل» جمع غير عاقل، ويعامل هنا معاملة المفرد المؤنث في الإشارة والوصف.'},
('ar-a2-u06-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «يتوقف» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل مضارع','p':'إذا كان القطار يقف في هذه المحطة كل يوم، أي جملة أنسب: «القطار يتوقف هنا كل يوم» أم «القطار تتوقف هنا كل يوم»؟','t':'grammar_choice','a':'القطار يتوقف هنا كل يوم.','e':'الفعل المضارع «يتوقف» يوافق الفاعل المذكر «القطار».'},
('ar-a2-u06-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «قرية» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان المكان السكني صغيرًا، أي جملة أنسب: «هذه قرية صغيرة» أم «هذا قرية صغير»؟','t':'grammar_choice','a':'هذه قرية صغيرة.','e':'«قرية» مؤنثة، لذلك نستخدم معها «هذه» وتوافقها الصفة «صغيرة».'},
('ar-a2-u06-p06','q9'):{'op':'ماذا يصف «مناسب» في سياق المحطة؟','ot':'grammar_function','oa':'مدى ملاءمة المحطة للوصول العملي إلى الوجهة.','p':'إذا كانت المحطة ملائمة للوصول إلى المكتبة، أي جملة أنسب: «هذه المحطة مناسبة للوصول إلى المكتبة» أم «هذه المحطة مناسب للوصول إلى المكتبة»؟','t':'grammar_choice','a':'هذه المحطة مناسبة للوصول إلى المكتبة.','e':'الصفة «مناسبة» توافق الاسم المؤنث «المحطة».'}}
FORMAL={'grammar_category','grammar_function','grammar_identification','person_form'}
PATS=[re.compile(r'التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+«|ما\s+نوع\s+كلمة'),re.compile(r'الوظيفة\s+النحوية|ما\s+وظيفة\s+«|ما\s+وظيفة\s+كلمة|ما\s+الدور\s+النحوي')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before=sha(PATH)
 if before!=EXPECTED: raise SystemExit(f'hash drift {before}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [p.get('sequence') for p in rows]!=list(range(1,61)): raise SystemExit('A2 structural precondition failed')
 applied=[]
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
 if len(applied)!=8: raise SystemExit(f'expected 8 repairs got {len(applied)}')
 unit=[p for p in rows if p.get('unit')==6]
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(31,37)): raise SystemExit('Unit06 scope regression')
 findings=[]; dups=[]; counts=Counter()
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
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':6,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'inventory_candidates':8,'confirmed_repairs':8,'passage_text_changed':False,'notable_sense_corrections':[],'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_A2_UNIT06' if not findings and not dups else 'FAIL'
 POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':6,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'inventory_candidates':8,'confirmed_repairs':8,'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':len(applied),'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_A2_UNIT06': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
