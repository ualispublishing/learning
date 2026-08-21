import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a2_u01_metalinguistic_repair_2026-08-21.json'; POST=ROOT/'reading/audit/arabic_a2_u01_metalinguistic_postrepair_2026-08-21.json'
EXPECTED='f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c'
R={
('ar-a2-u01-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «شارع» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت الطريق الرئيسي في الحي، أي جملة أنسب: «هذا شارع رئيسي» أم «هذه شارع رئيسية»؟','t':'grammar_choice','a':'هذا شارع رئيسي.','e':'«شارع» مذكر، لذلك نستخدم معه «هذا» ويأتي الوصف «رئيسي».'},
('ar-a2-u01-p01','q7'):{'op':'ما التصنيف النحوي لكلمة «خدمة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت مساعدة يقدمها المركز للسكان، أي جملة أنسب: «هذه خدمة مفيدة» أم «هذا خدمة مفيد»؟','t':'grammar_choice','a':'هذه خدمة مفيدة.','e':'«خدمة» مؤنثة، لذلك نستخدم معها «هذه» ويأتي الوصف «مفيدة».'},
('ar-a2-u01-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «هاتف» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا أشرت إلى الجهاز الذي اتصل به الأب، أي جملة أنسب: «هذا هاتف أبي» أم «هذه هاتف أبي»؟','t':'grammar_choice','a':'هذا هاتف أبي.','e':'«هاتف» في هذا السياق اسم للجهاز، وهو مذكر؛ وليس فعلًا ماضيًا هنا.'},
('ar-a2-u01-p02','q7'):{'op':'ما التصنيف النحوي لكلمة «بنك» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت المؤسسة المالية القريبة، أي جملة أنسب: «هذا بنك قريب» أم «هذه بنك قريبة»؟','t':'grammar_choice','a':'هذا بنك قريب.','e':'«بنك» مذكر، لذلك نستخدم معه «هذا».'},
('ar-a2-u01-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «إعلان» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كان النص المعلق عند المدخل مهمًا للسكان، أي جملة أنسب: «هذا إعلان مهم» أم «هذه إعلان مهمة»؟','t':'grammar_choice','a':'هذا إعلان مهم.','e':'«إعلان» مذكر، لذلك نستخدم معه «هذا».'},
('ar-a2-u01-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «زيارة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت المرة الأولى في المركز قصيرة، أي جملة أنسب: «هذه زيارة قصيرة» أم «هذا زيارة قصير»؟','t':'grammar_choice','a':'هذه زيارة قصيرة.','e':'«زيارة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a2-u01-p04','q7'):{'op':'ما التصنيف النحوي لكلمة «قسم» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا أشرت إلى جزء المؤسسة المخصص للاستقبال، أي عبارة أنسب: «هذا قسم الاستقبال» أم «هذه قسم الاستقبال»؟','t':'grammar_choice','a':'هذا قسم الاستقبال.','e':'«قسم» في هذا السياق اسم لجزء من المؤسسة، وهو مذكر؛ وليس فعلًا ماضيًا هنا.'},
('ar-a2-u01-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «قائمة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كانت ورقة الأسعار محدثة، أي جملة أنسب: «هذه قائمة حديثة» أم «هذا قائمة حديث»؟','t':'grammar_choice','a':'هذه قائمة حديثة.','e':'«قائمة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a2-u01-p05','q7'):{'op':'ما التصنيف النحوي لكلمة «سعر» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا أشرت إلى المبلغ المطلوب للمنتج، أي جملة أنسب: «هذا سعر جديد» أم «هذه سعر جديدة»؟','t':'grammar_choice','a':'هذا سعر جديد.','e':'«سعر» في هذا السياق اسم للمبلغ المطلوب، وهو مذكر؛ وليس فعلًا ماضيًا هنا.'},
('ar-a2-u01-p06','q9'):{'op':'لماذا تستخدم «إذا» أكثر من مرة في النص؟','ot':'grammar_function','oa':'لربط حالة ممكنة بالتصرف المناسب لها.','p':'أكمل بما يناسب لربط الحالة بالتصرف: «_____ كان البنك مغلقًا، أعود غدًا»: «إذا» أم «لأن»؟','t':'grammar_choice','a':'إذا.','e':'«إذا» تربط هنا حالة ممكنة بالتصرف الذي يحدث عند تحققها.'}}
FALSE_POSITIVE={('ar-a2-u01-p02','q4'):{'prompt':'ما وظيفة «البنك» في النص؟','type':'vocabulary_in_context','reason':'Comprehension asks the real-world role of the bank in the passage; it is not a grammatical-function question.'}}
FORMAL={'grammar_category','grammar_function','grammar_identification','person_form'}
PATS=[re.compile(r'التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+«|ما\s+نوع\s+كلمة'),re.compile(r'الوظيفة\s+النحوية|ما\s+وظيفة\s+«|ما\s+وظيفة\s+كلمة|ما\s+الدور\s+النحوي')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before=sha(PATH)
 if before!=EXPECTED: raise SystemExit(f'hash drift {before}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [p.get('sequence') for p in rows]!=list(range(1,61)): raise SystemExit('A2 structural precondition failed')
 applied=[]; fp_seen=[]
 for p in rows:
  amap={a['question_id']:a for a in p.get('answer_key',[])}; changed=0
  for q in p.get('questions',[]):
   k=(p['id'],q['id'])
   if k in FALSE_POSITIVE:
    f=FALSE_POSITIVE[k]
    if q.get('prompt')!=f['prompt'] or q.get('type')!=f['type']: raise SystemExit(f'false-positive precondition mismatch {k}')
    fp_seen.append({'passage_id':p['id'],'question_id':q['id'],'prompt':q['prompt'],'type':q['type'],'reason':f['reason']})
   s=R.get(k)
   if not s: continue
   a=amap[q['id']]
   if q.get('prompt')!=s['op'] or q.get('type')!=s['ot'] or a.get('answer')!=s['oa']: raise SystemExit(f'repair precondition mismatch {k}')
   applied.append({'passage_id':p['id'],'question_id':q['id'],'before':{'prompt':q['prompt'],'type':q['type'],'answer':a['answer']},'after':{'prompt':s['p'],'type':s['t'],'answer':s['a'],'explanation':s['e']}})
   q['prompt']=s['p']; q['type']=s['t']; a['answer']=s['a']; a['explanation']=s['e']; changed+=1
  if changed: p['revision']=int(p.get('revision',0))+1
 if len(applied)!=10 or len(fp_seen)!=1: raise SystemExit(f'adjudication cardinality repairs={len(applied)} false_positive={len(fp_seen)}')
 unit=[p for p in rows if p.get('unit')==1]
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(1,7)): raise SystemExit('Unit01 scope regression')
 findings=[]; dups=[]; counts=Counter()
 for p in unit:
  qs=p.get('questions',[]); ans=p.get('answer_key',[])
  if len(qs)!=10 or len(ans)!=10: findings.append({'passage_id':p['id'],'kind':'cardinality'})
  if {q.get('id') for q in qs}!={a.get('question_id') for a in ans}: findings.append({'passage_id':p['id'],'kind':'linkage'})
  seen={}
  for q in qs:
   typ=q.get('type'); counts[typ]+=1; prompt=(q.get('prompt') or '').strip(); k=(p['id'],q['id'])
   if typ in FORMAL: findings.append({'passage_id':p['id'],'question_id':q.get('id'),'kind':'formal_question_type','type':typ,'prompt':prompt})
   if k not in FALSE_POSITIVE and any(pat.search(prompt) for pat in PATS): findings.append({'passage_id':p['id'],'question_id':q.get('id'),'kind':'explicit_formal_metalinguistic_pattern','type':typ,'prompt':prompt})
   key=re.sub(r'\s+',' ',prompt)
   if key in seen: dups.append({'passage_id':p['id'],'question_ids':[seen[key],q.get('id')],'prompt':prompt})
   else: seen[key]=q.get('id')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8'); after=sha(PATH)
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':1,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'inventory_candidates':11,'confirmed_repairs':10,'adjudicated_false_positives':fp_seen,'passage_text_changed':False,'notable_sense_corrections':['هاتف: live context is phone/device noun, not past-tense verb.','قسم: live context is department/section noun, not past-tense verb.','سعر: live context is price noun, not past-tense verb.'],'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_A2_UNIT01' if not findings and not dups else 'FAIL'
 POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-21','language':'ar','level':'A2','unit':1,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'inventory_candidates':11,'confirmed_repairs':10,'adjudicated_false_positive_count':1,'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':len(applied),'false_positive':len(fp_seen),'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_A2_UNIT01': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
