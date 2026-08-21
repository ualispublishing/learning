import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a2_u04_metalinguistic_repair_2026-08-21.json'; POST=ROOT/'reading/audit/arabic_a2_u04_metalinguistic_postrepair_2026-08-21.json'
EXPECTED='f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c'
R={
('ar-a2-u04-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «حجم» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت العبوة متوسطة وليست كبيرة، أي جملة أنسب: «هذا حجم مناسب» أم «هذه حجم مناسبة»؟','t':'grammar_choice','a':'هذا حجم مناسب.','e':'«حجم» اسم مذكر يصف مقدار كبر الشيء أو صغره.'},
('ar-a2-u04-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «ثمن» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أشرت إلى المبلغ المطلوب للحقيبة، أي جملة أنسب: «هذا ثمن الحقيبة» أم «هذه ثمن الحقيبة»؟','t':'grammar_choice','a':'هذا ثمن الحقيبة.','e':'«ثمن» اسم مذكر للمبلغ المطلوب مقابل الشيء.'},
('ar-a2-u04-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «يستحق» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل مضارع','p':'إذا كان الكتاب مفيدًا بما يكفي لتبرير سعره، أي جملة أنسب: «الكتاب يستحق ثمنه» أم «الكتاب تستحق ثمنه»؟','t':'grammar_choice','a':'الكتاب يستحق ثمنه.','e':'مع «الكتاب» المذكر نستخدم هنا «يستحق».'},
('ar-a2-u04-p03','q7'):{'op':'ما التصنيف النحوي لكلمة «تطبيق» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أشرت إلى برنامج رقمي مفيد، أي جملة أنسب: «هذا تطبيق مفيد» أم «هذه تطبيق مفيدة»؟','t':'grammar_choice','a':'هذا تطبيق مفيد.','e':'«تطبيق» اسم مذكر لبرنامج رقمي.'},
('ar-a2-u04-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «صالح» في هذا الاستعمال؟','ot':'grammar_category','oa':'صفة','p':'إذا كانت البطارية ما زالت قابلة للاستخدام، أي جملة أنسب: «البطارية صالحة للاستخدام» أم «البطارية صالح للاستخدام»؟','t':'grammar_choice','a':'البطارية صالحة للاستخدام.','e':'الصفة توافق «البطارية» المؤنثة هنا فتأتي «صالحة».'},
('ar-a2-u04-p04','q7'):{'op':'ما التصنيف النحوي لكلمة «بدل» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا أخذت مصباحًا جديدًا مكان المصباح المعطل، أي عبارة أنسب: «أخذت مصباحًا جديدًا بدل المعطل» أم «أخذت مصباحًا جديدًا فاز المعطل»؟','t':'grammar_choice','a':'أخذت مصباحًا جديدًا بدل المعطل.','e':'«بدل» هنا تدل على الاستبدال أو أخذ شيء مكان آخر، وليست فعلًا ماضيًا.'},
('ar-a2-u04-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «إصلاح» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان الكرسي يحتاج إلى عمل يعيده إلى حالة جيدة، أي عبارة أنسب: «يحتاج الكرسي إلى إصلاح» أم «يحتاج الكرسي إلى صفقة»؟','t':'grammar_choice','a':'يحتاج الكرسي إلى إصلاح.','e':'«إصلاح» اسم للعملية التي تعيد الشيء إلى حالة جيدة.'},
('ar-a2-u04-p05','q7'):{'op':'ما التصنيف النحوي لكلمة «أسوأ» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا تدهورت الحالة مقارنة بما قبل، أي جملة أنسب: «أصبحت الحالة أسوأ من قبل» أم «أصبحت الحالة أسوأ قبل»؟','t':'grammar_choice','a':'أصبحت الحالة أسوأ من قبل.','e':'«أسوأ» هنا وصف مقارن يدل على حالة أكثر سوءًا من حالة أخرى.'},
('ar-a2-u04-p06','q9'):{'op':'ماذا تعبر «أسوأ»؟','ot':'grammar_function','oa':'مقارنة تدل على حالة أكثر سوءًا من غيرها.','p':'إذا كان الوضع بعد المشكلة أكثر سوءًا من السابق، أي جملة أنسب: «الوضع أسوأ من قبل» أم «الوضع صالح من قبل»؟','t':'grammar_choice','a':'الوضع أسوأ من قبل.','e':'«أسوأ من» تستعمل هنا للمقارنة بين حالتين.'}}
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
 if len(applied)!=9: raise SystemExit(f'expected 9 repairs got {len(applied)}')
 unit=[p for p in rows if p.get('unit')==4]
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(19,25)): raise SystemExit('Unit04 scope regression')
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
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':4,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'inventory_candidates':9,'confirmed_repairs':9,'passage_text_changed':False,'notable_sense_corrections':['بدل: live context expresses replacement/instead-of, not a past-tense verb.','أسوأ: live context is a comparative description (worse), not a plain noun label.'],'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_A2_UNIT04' if not findings and not dups else 'FAIL'
 POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':4,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'inventory_candidates':9,'confirmed_repairs':9,'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':len(applied),'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_A2_UNIT04': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
