import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a2_u03_metalinguistic_repair_2026-08-21.json'; POST=ROOT/'reading/audit/arabic_a2_u03_metalinguistic_postrepair_2026-08-21.json'
EXPECTED='f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c'
R={
('ar-a2-u03-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «مؤخرا» في هذا الاستعمال؟','ot':'grammar_category','oa':'ظرف','p':'إذا حدثت الزيارة قبل أيام قليلة، أي جملة أنسب: «زرت المكان مؤخرًا» أم «سأزور المكان مؤخرًا غدًا»؟','t':'grammar_choice','a':'زرت المكان مؤخرًا.','e':'«مؤخرًا» تشير هنا إلى وقت قريب مضى.'},
('ar-a2-u03-p01','q7'):{'op':'ما التصنيف النحوي لكلمة «مجددا» في هذا الاستعمال؟','ot':'grammar_category','oa':'ظرف','p':'إذا لم أفهم الصورة أول مرة وأعدت النظر إليها، أي جملة أنسب: «نظرت إليها مجددًا» أم «نظرت إليها مؤخرًا فقط»؟','t':'grammar_choice','a':'نظرت إليها مجددًا.','e':'«مجددًا» تعني أن الفعل حدث مرة أخرى.'},
('ar-a2-u03-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «تسجيل» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا حفظ الهاتف ملفًا فيه أصوات، أي عبارة أنسب: «تسجيل صوتي» أم «نظرة صوتية»؟','t':'grammar_choice','a':'تسجيل صوتي.','e':'«تسجيل» هنا اسم لملف أو مادة محفوظة فيها أصوات.'},
('ar-a2-u03-p02','q7'):{'op':'ما التصنيف النحوي لكلمة «نظرة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أردت فحص الصور سريعًا، أي عبارة أنسب: «ألقيت نظرة على الصور» أم «ألقيت تسجيلًا على الصور»؟','t':'grammar_choice','a':'ألقيت نظرة على الصور.','e':'«نظرة» هنا اسم لفعل النظر أو الفحص.'},
('ar-a2-u03-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «حفل» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أشرت إلى مناسبة التخرج، أي جملة أنسب: «هذا حفل تخرج» أم «هذه حفل تخرج»؟','t':'grammar_choice','a':'هذا حفل تخرج.','e':'«حفل» مذكر، لذلك نستخدم معه «هذا».'},
('ar-a2-u03-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «معظم» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا حضر أغلب الطلاب وغاب بعضهم، أي جملة أدق: «حضر معظم الطلاب» أم «حضر جميع الطلاب»؟','t':'grammar_choice','a':'حضر معظم الطلاب.','e':'«معظم» تدل على الأغلبية ولا تعني الجميع.'},
('ar-a2-u03-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «أثر» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا بقيت علامة جميلة من الرحلة في الذاكرة، أي جملة أنسب: «تركت الرحلة أثرًا جميلًا» أم «تركت الرحلة فاز جميلًا»؟','t':'grammar_choice','a':'تركت الرحلة أثرًا جميلًا.','e':'«أثر» في هذا السياق اسم لعلامة أو تأثير باقٍ، وليس فعلًا ماضيًا.'},
('ar-a2-u03-p05','q7'):{'op':'ما التصنيف النحوي لكلمة «فاز» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا كان الفوز حدث أمس، أي جملة أنسب: «فاز الفريق أمس» أم «يفوز الفريق أمس»؟','t':'grammar_choice','a':'فاز الفريق أمس.','e':'«فاز» تناسب حدثًا وقع في الماضي.'},
('ar-a2-u03-p06','q9'):{'op':'ماذا تفعل «ثم» ضمنيًا في فكرة تغير رأي نور بعد دليل جديد؟','ot':'grammar_function','oa':'تربط تصورًا سابقًا بنتيجة أو فهم لاحق تغير بسبب معلومات جديدة.','p':'إذا كان رأي نور تغير بعد ظهور دليل جديد، أي ربط أنسب: «ظنت شيئًا، ثم تغير رأيها» أم «ظنت شيئًا، لأن تغير رأيها»؟','t':'grammar_choice','a':'ظنت شيئًا، ثم تغير رأيها.','e':'«ثم» تربط حدثًا أو فهمًا أول بما جاء بعده في التسلسل.'}}
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
 unit=[p for p in rows if p.get('unit')==3]
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(13,19)): raise SystemExit('Unit03 scope regression')
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
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':3,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'inventory_candidates':9,'confirmed_repairs':9,'passage_text_changed':False,'notable_sense_corrections':['أثر: live context is the noun trace/effect, not a past-tense verb.'],'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_A2_UNIT03' if not findings and not dups else 'FAIL'
 POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':3,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'inventory_candidates':9,'confirmed_repairs':9,'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':len(applied),'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_A2_UNIT03': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
