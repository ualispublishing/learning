import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; OUT=ROOT/'reading/audit/arabic_a1_u03_metalinguistic_repair_2026-08-20.json'
EXPECTED='d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b'
R={
('ar-a1-u03-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «يحب» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل مضارع','p':'اختر الجملة الصحيحة مع «سامي»: «سامي يحب التفاح» أم «سامي أحب التفاح»؟','t':'grammar_choice','a':'سامي يحب التفاح.','e':'مع «سامي» نستعمل هنا «يحب» للتعبير عن تفضيل في الحاضر.'},
('ar-a1-u03-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «يحتاج» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل مضارع','p':'اختر الجملة الصحيحة مع «عمر»: «عمر يحتاج إلى كتاب» أم «عمر أحتاج إلى كتاب»؟','t':'grammar_choice','a':'عمر يحتاج إلى كتاب.','e':'مع «عمر» نستعمل هنا «يحتاج».'},
('ar-a1-u03-p03','q7'):{'op':'ما وظيفة «عند» في «عند الثلاجة»؟','ot':'grammar_function','oa':'تحدد مكان الشيء بالنسبة إلى الثلاجة.','p':'إذا كان الحليب بجانب الثلاجة، أي جملة أنسب: «الحليب عند الثلاجة» أم «الحليب أين الثلاجة»؟','t':'grammar_choice','a':'الحليب عند الثلاجة.','e':'«عند» تبين هنا مكان الحليب بالنسبة إلى الثلاجة.'},
('ar-a1-u03-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «لماذا» في هذا الاستعمال؟','ot':'grammar_category','oa':'أداة استفهام','p':'إذا أردت معرفة سبب اختيار الماء، أي سؤال أنسب: «لماذا اخترت الماء؟» أم «أين اخترت الماء؟»؟','t':'grammar_choice','a':'لماذا اخترت الماء؟','e':'«لماذا» تستعمل للسؤال عن السبب.'},
('ar-a1-u03-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «ثم» في هذا الاستعمال؟','ot':'grammar_category','oa':'حرف عطف','p':'إذا غسلت يديك ثم أكلت، أي جملة تحفظ الترتيب: «غسلت يدي ثم أكلت» أم «أكلت ثم غسلت يدي»؟','t':'grammar_choice','a':'غسلت يدي ثم أكلت.','e':'«ثم» تربط هنا حدثين بحيث يأتي الأكل بعد غسل اليدين.'},
('ar-a1-u03-p06','q9'):{'op':'ماذا تفعل «ثم» في سلسلة الأفعال؟','ot':'grammar_function','oa':'تربط الأفعال بترتيب، بحيث يأتي فعل بعد آخر.','p':'اختر الجملة التي تعني أن الشراء حدث بعد السؤال: «سألت ثم اشتريت» أم «اشتريت ثم سألت»؟','t':'grammar_choice','a':'سألت ثم اشتريت.','e':'ترتيب الجملة يبين أن السؤال حدث أولًا ثم جاء الشراء بعده.'}}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before=sha(PATH)
 if before!=EXPECTED: raise SystemExit(f'hash drift {before}')
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]; applied=[]
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
 unit=[p for p in rows if p.get('unit')==3]
 if len(unit)!=6 or any(len(p.get('questions',[]))!=10 or len(p.get('answer_key',[]))!=10 for p in unit): raise SystemExit('structural failure')
 if any(q.get('type') in {'grammar_category','grammar_function','grammar_identification','person_form'} for p in unit for q in p.get('questions',[])): raise SystemExit('formal type remains')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8'); after=sha(PATH)
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':3,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'repairs_applied':6,'passage_text_changed':False,'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(after)
if __name__=='__main__': main()
