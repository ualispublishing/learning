import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
REPAIR=ROOT/'reading/audit/arabic_a1_u06_metalinguistic_repair_2026-08-20.json'
POST=ROOT/'reading/audit/arabic_a1_u06_metalinguistic_postrepair_2026-08-20.json'
EXPECTED='d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b'
R={
('ar-a1-u06-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «طريق» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أردت تسمية المسار الذي تسلكه إلى السوق، أي عبارة أنسب: «طريق السوق» أم «وسط السوق»؟','t':'grammar_choice','a':'طريق السوق.','e':'«طريق» تسمّي المسار الذي نسلكه للوصول إلى مكان.'},
('ar-a1-u06-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «سيارة» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'أي جملة أنسب للإشارة إلى مركبة أبي: «هذه سيارة أبي» أم «هذا سيارة أبي»؟','t':'grammar_choice','a':'هذه سيارة أبي.','e':'«سيارة» مؤنثة، لذلك نستخدم معها «هذه» هنا.'},
('ar-a1-u06-p03','q6'):{'op':'ما التصنيف النحوي لكلمة «تحت» في هذا الاستعمال؟','ot':'grammar_category','oa':'ظرف','p':'إذا كانت الحقيبة أسفل الكرسي، أي جملة أنسب: «الحقيبة تحت الكرسي» أم «الحقيبة فوق الكرسي»؟','t':'grammar_choice','a':'الحقيبة تحت الكرسي.','e':'«تحت» تصف موقعًا أسفل شيء آخر.'},
('ar-a1-u06-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «اذهب» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل أمر','p':'إذا أردت أن تطلب من سامر التوجه إلى الصف الآن، أي صيغة أنسب: «اذهب إلى الصف» أم «يذهب إلى الصف»؟','t':'grammar_choice','a':'اذهب إلى الصف.','e':'«اذهب» تُستعمل هنا لطلب القيام بالفعل.'},
('ar-a1-u06-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «موقع» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أردت السؤال عن مكان المدرسة على الخريطة، أي عبارة أنسب: «موقع المدرسة» أم «مدرسة الموقع»؟','t':'grammar_choice','a':'موقع المدرسة.','e':'«موقع المدرسة» تعني المكان الذي تقع فيه المدرسة.'},
('ar-a1-u06-p06','q9'):{'op':'ماذا يحدد «تحت»؟','ot':'grammar_function','oa':'موقعًا أسفل شيء آخر.','p':'إذا كنت في ممر أسفل الجسر، أي وصف أنسب: «أنا تحت الجسر» أم «أنا أمام الجسر»؟','t':'grammar_choice','a':'أنا تحت الجسر.','e':'«تحت» تبين أن موقع المتكلم أسفل الجسر.'}}
FORMAL={'grammar_category','grammar_function','grammar_identification','person_form'}
PATS=[re.compile(r'التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+«|ما\s+نوع\s+كلمة'),re.compile(r'الوظيفة\s+النحوية|ما\s+وظيفة\s+«|ما\s+وظيفة\s+كلمة|ما\s+الدور\s+النحوي')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before=sha(PATH)
 if before!=EXPECTED: raise SystemExit(f'hash drift {before}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): raise SystemExit('A1 structural precondition failed')
 applied=[]
 for p in rows:
  amap={a['question_id']:a for a in p.get('answer_key',[])}; n=0
  for q in p.get('questions',[]):
   k=(p['id'],q['id']); s=R.get(k)
   if not s: continue
   a=amap[q['id']]
   if q.get('prompt')!=s['op'] or q.get('type')!=s['ot'] or a.get('answer')!=s['oa']: raise SystemExit(f'precondition mismatch {k}')
   applied.append({'passage_id':p['id'],'question_id':q['id'],'before':{'prompt':q['prompt'],'type':q['type'],'answer':a['answer']},'after':{'prompt':s['p'],'type':s['t'],'answer':s['a'],'explanation':s['e']}})
   q['prompt']=s['p']; q['type']=s['t']; a['answer']=s['a']; a['explanation']=s['e']; n+=1
  if n: p['revision']=int(p.get('revision',0))+1
 if len(applied)!=6: raise SystemExit(f'expected 6 repairs got {len(applied)}')
 unit=[p for p in rows if p.get('unit')==6]
 if len(unit)!=6 or [p.get('sequence') for p in unit]!=list(range(31,37)): raise SystemExit('Unit 06 scope regression')
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
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
 after=sha(PATH)
 REPAIR.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':6,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'repairs_applied':len(applied),'passage_text_changed':False,'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 status='PASS_DETERMINISTIC_UNIT06' if not findings and not dups else 'FAIL'
 POST.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':6,'bound_sha256':after,'scope':{'records':6,'questions':60,'answers':60},'formal_metalinguistic_finding_count':len(findings),'findings':findings,'exact_duplicate_prompt_count':len(dups),'duplicate_prompts':dups,'question_type_counts':dict(counts),'status':status,'limitations':'Deterministic/self-review only; independent native/educator review remains required.','release_effect':'Arabic remains educator-blocked.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':len(applied),'status':status,'findings':len(findings),'duplicates':len(dups),'after':after},ensure_ascii=False))
 if status!='PASS_DETERMINISTIC_UNIT06': raise SystemExit('postrepair audit failed')
if __name__=='__main__': main()
