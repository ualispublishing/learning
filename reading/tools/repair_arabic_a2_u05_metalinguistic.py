import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a2_u05_metalinguistic_repair_2026-08-21.json'; POST=ROOT/'reading/audit/arabic_a2_u05_metalinguistic_postrepair_2026-08-21.json'
EXPECTED='f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c'
R={
('ar-a2-u05-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «تصوير» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كنت تتحدث عن هواية التقاط الصور، أي جملة أنسب: «أحب التصوير في المدينة» أم «أحب يصور في المدينة»؟','t':'grammar_choice','a':'أحب التصوير في المدينة.','e':'«تصوير» هنا اسم للهواية أو النشاط.'},
('ar-a2-u05-p01','q7'):{'op':'ما التصنيف النحوي لكلمة «مسابقة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت المنافسة صغيرة، أي جملة أنسب: «هذه مسابقة صغيرة» أم «هذا مسابقة صغير»؟','t':'grammar_choice','a':'هذه مسابقة صغيرة.','e':'«مسابقة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a2-u05-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «تفكير» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان القرار يحتاج إلى تأمل قبل الاختيار، أي عبارة أنسب: «يحتاج القرار إلى تفكير» أم «يحتاج القرار إلى يفكر»؟','t':'grammar_choice','a':'يحتاج القرار إلى تفكير.','e':'«تفكير» هنا اسم لعملية التأمل والتحليل.'},
('ar-a2-u05-p02','q7'):{'op':'ما التصنيف النحوي لكلمة «متابعة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أردت الرجوع إلى النتيجة الأسبوع القادم، أي عبارة أنسب: «نحتاج إلى متابعة النتيجة» أم «نحتاج إلى يتابع النتيجة»؟','t':'grammar_choice','a':'نحتاج إلى متابعة النتيجة.','e':'«متابعة» هنا اسم لعملية الاستمرار في المراقبة والرجوع إلى النتيجة.'},
('ar-a2-u05-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «خطوة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت هذه أول مرحلة في المشروع، أي جملة أنسب: «هذه خطوة أولى» أم «هذا خطوة أول»؟','t':'grammar_choice','a':'هذه خطوة أولى.','e':'«خطوة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a2-u05-p03','q7'):{'op':'ما التصنيف النحوي لكلمة «مشاريع» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان الطلاب يعملون على أكثر من مشروع، أي جملة أنسب: «هذه مشاريع صغيرة» أم «هذا مشاريع صغير»؟','t':'grammar_choice','a':'هذه مشاريع صغيرة.','e':'«مشاريع» جمع غير عاقل، ويعامل هنا معاملة المفرد المؤنث في الوصف والإشارة.'},
('ar-a2-u05-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «عادة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان المشي بعد العشاء سلوكًا يتكرر يوميًا، أي جملة أنسب: «هذه عادة يومية» أم «هذا عادة يومي»؟','t':'grammar_choice','a':'هذه عادة يومية.','e':'«عادة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a2-u05-p04','q7'):{'op':'ما التصنيف النحوي لكلمة «يتعرف» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل مضارع','p':'إذا كان الطفل الآن يبدأ معرفة زملائه، أي جملة أنسب: «الطفل يتعرف إلى زملائه» أم «الطفل تعرف إلى زملائه الآن»؟','t':'grammar_choice','a':'الطفل يتعرف إلى زملائه.','e':'«يتعرف» تناسب فعلًا جاريًا أو متكررًا في الحاضر.'},
('ar-a2-u05-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «تدريب» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت المهارة تحتاج إلى ممارسة منظمة، أي عبارة أنسب: «تحتاج المهارة إلى تدريب منتظم» أم «تحتاج المهارة إلى يتدرب منتظم»؟','t':'grammar_choice','a':'تحتاج المهارة إلى تدريب منتظم.','e':'«تدريب» هنا اسم للممارسة المنظمة.'},
('ar-a2-u05-p06','q9'):{'op':'ماذا يفعل «بدل أن» في النص؟','ot':'grammar_function','oa':'يقدم طريقة أفضل مقابل طريقة أخرى يريد النص تجنبها.','p':'إذا أرادت نور اختيار طريقة بديلة عن إنهاء المشروع كله دفعة واحدة، أي جملة أنسب: «تقسمه إلى خطوات بدل أن تنهيه كله دفعة واحدة» أم «تقسمه إلى خطوات لأن تنهيه كله دفعة واحدة»؟','t':'grammar_choice','a':'تقسمه إلى خطوات بدل أن تنهيه كله دفعة واحدة.','e':'«بدل أن» تقدم فعلًا بديلًا عن فعل آخر يريد المتكلم تجنبه.'}}
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
 if len(applied)!=10: raise SystemExit(f'expected 10 repairs got {len(applied)}')
 unit=[p for p in rows if p.get('unit')==5]
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(25,31)): raise SystemExit('Unit05 scope regression')
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
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':5,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'inventory_candidates':10,'confirmed_repairs':10,'passage_text_changed':False,'notable_sense_corrections':[],'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_A2_UNIT05' if not findings and not dups else 'FAIL'
 POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':5,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'inventory_candidates':10,'confirmed_repairs':10,'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':len(applied),'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_A2_UNIT05': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
