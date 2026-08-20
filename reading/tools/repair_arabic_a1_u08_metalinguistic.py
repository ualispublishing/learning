import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; REPAIR=ROOT/'reading/audit/arabic_a1_u08_metalinguistic_repair_2026-08-20.json'; POST=ROOT/'reading/audit/arabic_a1_u08_metalinguistic_postrepair_2026-08-20.json'; EXPECTED='d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b'
R={
('ar-a1-u08-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «يشعر» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل مضارع','p':'اختر الجملة الصحيحة مع «مريم»: «مريم تشعر بالتعب» أم «مريم يشعر بالتعب»؟','t':'grammar_choice','a':'مريم تشعر بالتعب.','e':'مع «مريم» نستعمل هنا «تشعر».'},
('ar-a1-u08-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «حاجة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا وصفت حاجة بسيطة، أي جملة أنسب: «هذه حاجة بسيطة» أم «هذا حاجة بسيطة»؟','t':'grammar_choice','a':'هذه حاجة بسيطة.','e':'«حاجة» مؤنثة، لذلك نستخدم معها «هذه» هنا.'},
('ar-a1-u08-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «يد» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أشرت إلى يدك، أي جملة أنسب: «هذه يدي» أم «هذا يدي»؟','t':'grammar_choice','a':'هذه يدي.','e':'«يد» مؤنثة، لذلك نستخدم معها «هذه».'},
('ar-a1-u08-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «قلب» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'إذا أشرت إلى جزء الجسم داخل صدرك، أي جملة أنسب: «هذا قلبي» أم «هذه قلبي»؟','t':'grammar_choice','a':'هذا قلبي.','e':'«قلب» في هذا السياق اسم لجزء من الجسم، وهو مذكر.'},
('ar-a1-u08-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «حاول» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'اختر الجملة الصحيحة مع «سامر» عن محاولة حدثت أمس: «حاول سامر أن يقرأ» أم «تحاول سامر أن يقرأ»؟','t':'grammar_choice','a':'حاول سامر أن يقرأ.','e':'مع «سامر» ولحدث ماضٍ نستعمل هنا «حاول».'},
('ar-a1-u08-p06','q9'):{'op':'ماذا يصف «يشعر»؟','ot':'grammar_function','oa':'إحساس الشخص بحالة جسدية أو نفسية.','p':'إذا كان سامر متعبًا، أي جملة أنسب: «سامر يشعر بالتعب» أم «سامر يصل بالتعب»؟','t':'grammar_choice','a':'سامر يشعر بالتعب.','e':'«يشعر» تصف هنا إحساس سامر بحالته.'}}
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
 unit=[p for p in rows if p.get('unit')==8]; findings=[]; dups=[]; counts=Counter()
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(43,49)): raise SystemExit('scope regression')
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
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':8,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'repairs_applied':6,'passage_text_changed':False,'notable_correction':'ar-a1-u08-p04 q6 previously labeled قلب as a past-tense verb despite noun/body-part usage; replacement tests the intended heart sense operationally.','repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_UNIT08' if not findings and not dups else 'FAIL'; POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':8,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':6,'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_UNIT08': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
