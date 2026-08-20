import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a1_u10_metalinguistic_repair_2026-08-20.json'; POST=ROOT/'reading/audit/arabic_a1_u10_metalinguistic_postrepair_2026-08-20.json'; EXPECTED='d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b'
R={
('ar-a1-u10-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «دائما» في هذا الاستعمال؟','ot':'grammar_category','oa':'ظرف','p':'إذا كان تجهيز الحقيبة عادة يومية، أي جملة أنسب: «أنا دائمًا أجهز حقيبتي» أم «أنا دائم أجهز حقيبتي»؟','t':'grammar_choice','a':'أنا دائمًا أجهز حقيبتي.','e':'«دائمًا» تستعمل هنا للتعبير عن عادة تتكرر باستمرار.'},
('ar-a1-u10-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «طريقة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت أسلوبًا غير الأسلوب الأول، أي جملة أنسب: «هذه طريقة مختلفة» أم «هذا طريقة مختلف»؟','t':'grammar_choice','a':'هذه طريقة مختلفة.','e':'«طريقة» مؤنثة، ولذلك نقول «هذه طريقة مختلفة».'},
('ar-a1-u10-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «مجموعة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت عددًا من الطلاب يعملون معًا، أي جملة أنسب: «هذه مجموعة صغيرة» أم «هذا مجموعة صغيرة»؟','t':'grammar_choice','a':'هذه مجموعة صغيرة.','e':'«مجموعة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a1-u10-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «لحظة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت وقتًا قصيرًا جميلًا، أي جملة أنسب: «هذه لحظة جميلة» أم «هذا لحظة جميلة»؟','t':'grammar_choice','a':'هذه لحظة جميلة.','e':'«لحظة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a1-u10-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «صفحة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا فتحت جزءًا جديدًا من الكتاب، أي جملة أنسب: «هذه صفحة جديدة» أم «هذا صفحة جديدة»؟','t':'grammar_choice','a':'هذه صفحة جديدة.','e':'«صفحة» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a1-u10-p06','q9'):{'op':'ماذا يفعل «سؤال» في القراءة؟','ot':'grammar_function','oa':'يطلب جوابًا ويساعد القارئ على فحص فهمه.','p':'إذا أردت أن تطلب معلومة من القارئ، أي عبارة أنسب: «عندي سؤال» أم «عندي صفحة»؟','t':'grammar_choice','a':'عندي سؤال.','e':'«سؤال» يطلب جوابًا أو معلومة، ويمكن أن يساعد القارئ على فحص فهمه.'}}
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
 unit=[p for p in rows if p.get('unit')==10]; findings=[]; dups=[]; counts=Counter()
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(55,61)): raise SystemExit('scope regression')
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
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':10,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'repairs_applied':6,'passage_text_changed':False,'repairs':applied,'a1_original_candidate_progress':{'original_formal_candidate_count':63,'this_unit_repaired':6,'unit_level_repair_coverage_after_this_batch':63},'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_UNIT10' if not findings and not dups else 'FAIL'; POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':10,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required. Unit repairs remain on separate unmerged branches, so this does not certify one integrated combined A1 file.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':6,'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_UNIT10': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
