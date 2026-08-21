import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a2_u02_metalinguistic_repair_2026-08-21.json'; POST=ROOT/'reading/audit/arabic_a2_u02_metalinguistic_postrepair_2026-08-21.json'
EXPECTED='f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c'
R={
('ar-a2-u02-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «موعد» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أردت تحديد وقت ثابت للقاء، أي جملة أنسب: «موعد اللقاء في الرابعة» أم «يلتقي الموعد في الرابعة»؟','t':'grammar_choice','a':'موعد اللقاء في الرابعة.','e':'«موعد» هنا اسم للوقت المحدد للقاء.'},
('ar-a2-u02-p01','q7'):{'op':'ما التصنيف النحوي لكلمة «رد» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا أجبت عن دعوة كتابةً، أي عبارة أنسب: «أرسلت ردًا واضحًا» أم «أرسلت موعدًا واضحًا»؟','t':'grammar_choice','a':'أرسلت ردًا واضحًا.','e':'«رد» في هذا السياق اسم للجواب على الدعوة، وليس فعلًا ماضيًا.'},
('ar-a2-u02-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «متأكد» في هذا الاستعمال؟','ot':'grammar_category','oa':'صفة','p':'إذا كانت نور واثقة من الموعد، أي جملة أنسب: «نور متأكدة من الموعد» أم «نور متأكد من الموعد»؟','t':'grammar_choice','a':'نور متأكدة من الموعد.','e':'مع «نور» المؤنثة تأتي الصفة هنا بصيغة «متأكدة».'},
('ar-a2-u02-p02','q7'):{'op':'ما التصنيف النحوي لكلمة «تالي» في هذا الاستعمال؟','ot':'grammar_category','oa':'صفة','p':'إذا كنت تقصد اليوم الذي يأتي بعد الخميس مباشرة، أي عبارة أنسب: «اليوم التالي» أم «اليوم التالية»؟','t':'grammar_choice','a':'اليوم التالي.','e':'«التالي» يوافق «اليوم» المذكر في هذا التعبير.'},
('ar-a2-u02-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «اتصل» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا أخبرت عن سامر وما فعله أمس، أي جملة أنسب: «اتصل سامر بصديقه أمس» أم «يتصل سامر بصديقه أمس»؟','t':'grammar_choice','a':'اتصل سامر بصديقه أمس.','e':'«اتصل» تناسب هنا فعلًا حدث في الماضي.'},
('ar-a2-u02-p03','q7'):{'op':'ما التصنيف النحوي لكلمة «لاحق» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا كان اللقاء في وقت يأتي بعد الوقت الأول، أي عبارة أنسب: «وقت لاحق» أم «وقت لاحقة»؟','t':'grammar_choice','a':'وقت لاحق.','e':'«لاحق» في «وقت لاحق» صفة توافق «وقت» المذكر، وليست فعلًا ماضيًا هنا.'},
('ar-a2-u02-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «اختيار» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان البديل مناسبًا، أي جملة أنسب: «هذا اختيار مناسب» أم «هذه اختيار مناسبة»؟','t':'grammar_choice','a':'هذا اختيار مناسب.','e':'«اختيار» مذكر، لذلك نستخدم معه «هذا».'},
('ar-a2-u02-p04','q7'):{'op':'ما التصنيف النحوي لكلمة «حالي» في هذا الاستعمال؟','ot':'grammar_category','oa':'صفة','p':'إذا وصفت الخطة الموجودة الآن، أي عبارة أنسب: «الخطة الحالية» أم «الخطة الحالي»؟','t':'grammar_choice','a':'الخطة الحالية.','e':'«الحالية» توافق «الخطة» المؤنثة.'},
('ar-a2-u02-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «دورة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان البرنامج التعليمي قصيرًا، أي جملة أنسب: «هذه دورة قصيرة» أم «هذا دورة قصير»؟','t':'grammar_choice','a':'هذه دورة قصيرة.','e':'«دورة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a2-u02-p05','q7'):{'op':'ما التصنيف النحوي لكلمة «تنظيم» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أردت وصف ترتيب المواعيد جيدًا، أي عبارة أنسب: «تنظيم الوقت مهم» أم «ينظم الوقت مهم»؟','t':'grammar_choice','a':'تنظيم الوقت مهم.','e':'«تنظيم» هنا اسم للعملية أو الترتيب.'},
('ar-a2-u02-p06','q9'):{'op':'ماذا يصف «التالي» في «اليوم التالي»؟','ot':'grammar_function','oa':'اليوم الذي يأتي بعد اليوم المذكور مباشرة.','p':'إذا كان النشاط بعد يوم الاثنين مباشرة، أي عبارة أنسب: «في اليوم التالي» أم «في اليوم السابق»؟','t':'grammar_choice','a':'في اليوم التالي.','e':'«اليوم التالي» هو اليوم الذي يأتي مباشرة بعد اليوم المذكور.'}}
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
 if len(applied)!=11: raise SystemExit(f'expected 11 repairs got {len(applied)}')
 unit=[p for p in rows if p.get('unit')==2]
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(7,13)): raise SystemExit('Unit02 scope regression')
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
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':2,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'inventory_candidates':11,'confirmed_repairs':11,'passage_text_changed':False,'notable_sense_corrections':['رد: live context is the noun reply/response, not a past-tense verb.','لاحق: live context is the adjective later in وقت لاحق, not a past-tense verb.'],'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_A2_UNIT02' if not findings and not dups else 'FAIL'
 POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':2,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'inventory_candidates':11,'confirmed_repairs':11,'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':len(applied),'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_A2_UNIT02': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
