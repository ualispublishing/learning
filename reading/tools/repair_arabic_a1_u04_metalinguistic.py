import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'; OUT=ROOT/'reading/audit/arabic_a1_u04_metalinguistic_repair_2026-08-20.json'; EXPECTED='d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b'
R={
('ar-a1-u04-p01','q6'):{'op':'ما التصنيف النحوي لكلمة «أب» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا كنت تشير إلى والدك، أي صيغة أنسب: «هذا أبي» أم «هذا أب أنا»؟','t':'grammar_choice','a':'هذا أبي.','e':'في هذا التعبير نستخدم «أبي» للدلالة على والدي.'},
('ar-a1-u04-p02','q6'):{'op':'ما التصنيف النحوي لكلمة «اسم» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'إذا أردت تقديم نفسك، أي صيغة أنسب: «اسمي نور» أم «اسم أنا نور»؟','t':'grammar_choice','a':'اسمي نور.','e':'«اسمي» هي الصيغة الطبيعية هنا عند ذكر اسم المتكلم.'},
('ar-a1-u04-p03','q7'):{'op':'ما التصنيف النحوي لكلمة «يقول» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل مضارع','p':'اختر الصحيح مع «سامي»: «سامي يقول مرحبًا» أم «سامي تقول مرحبًا»؟','t':'grammar_choice','a':'سامي يقول مرحبًا.','e':'مع «سامي» نستعمل «يقول».'},
('ar-a1-u04-p03','q8'):{'op':'في «تقول هدى»، من صاحب الفعل؟','ot':'person_form','oa':'هدى.','p':'حوّل الجملة إلى هدى: «سامي يقول مرحبًا» تصبح «هدى _____ مرحبًا».','t':'cloze_transfer','a':'تقول.','e':'مع «هدى» نستعمل «تقول».'},
('ar-a1-u04-p04','q6'):{'op':'ما التصنيف النحوي لكلمة «أخبر» في هذا الاستعمال؟','ot':'grammar_category','oa':'فعل ماضٍ','p':'أي جملة تتحدث عن خبر حدث أمس: «أخبرت ليلى هدى أمس» أم «ستخبر ليلى هدى غدًا»؟','t':'grammar_choice','a':'أخبرت ليلى هدى أمس.','e':'«أخبرت» هنا تدل على حدث وقع في الماضي.'},
('ar-a1-u04-p05','q6'):{'op':'ما التصنيف النحوي لكلمة «جميع» في هذا الاستعمال؟','ot':'grammar_category','oa':'اسم','p':'في التحية للمجموعة، أي صيغة أنسب: «مرحبًا بكم جميعًا» أم «مرحبًا بكم جميع»؟','t':'grammar_choice','a':'مرحبًا بكم جميعًا.','e':'بعد «بكم» تأتي هنا الصيغة «جميعًا».'},
('ar-a1-u04-p06','q9'):{'op':'ماذا يحدد «أمام» في «يقف الأطفال أمام الكبار»؟','ot':'grammar_function','oa':'الموقع المكاني للأطفال بالنسبة إلى الكبار.','p':'إذا كان الأطفال في مقدمة الصورة والكبار خلفهم، أي جملة أنسب: «الأطفال أمام الكبار» أم «الأطفال خلف الكبار»؟','t':'grammar_choice','a':'الأطفال أمام الكبار.','e':'«أمام» تبين أن الأطفال في الجهة الأمامية بالنسبة إلى الكبار.'}}
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
 if len(applied)!=7: raise SystemExit(f'expected 7 got {len(applied)}')
 unit=[p for p in rows if p.get('unit')==4]
 if len(unit)!=6 or any(len(p.get('questions',[]))!=10 or len(p.get('answer_key',[]))!=10 for p in unit): raise SystemExit('structural failure')
 if any(q.get('type') in {'grammar_category','grammar_function','grammar_identification','person_form'} for p in unit for q in p.get('questions',[])): raise SystemExit('formal type remains')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8'); after=sha(PATH)
 OUT.write_text(json.dumps({'schema_version':1,'date':'2026-08-20','language':'ar','level':'A1','unit':4,'status':'BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW','before_sha256':before,'after_sha256':after,'repairs_applied':7,'passage_text_changed':False,'repairs':applied,'release_effect':'Arabic remains educator-blocked; independent semantic/native/educator review required.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(after)
if __name__=='__main__': main()
