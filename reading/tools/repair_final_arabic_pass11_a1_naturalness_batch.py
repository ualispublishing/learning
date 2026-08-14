#!/usr/bin/env python3
"""Apply high-confidence defects found by the full manual A1 Pass-11 prose read.

Only exact reviewed strings are replaced. No question/answer semantics or target
IDs are changed. Deliberate vocabulary forms are preserved where practical.
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/a1/passages.jsonl'
REPAIRS={
 'ar-a1-u02-p03':[
  ('عندما يصبح الوقت متأخرًا تعودان إلى المنزل.','عندما يتأخر الوقت تعودان إلى المنزل.'),
 ],
 'ar-a1-u03-p06':[
  ('وتعرف عدد ما يجب شراؤه.','وتعرف عدد الأشياء التي يجب شراؤها.'),
 ],
 'ar-a1-u04-p01':[
  ('أب ليلى يعمل في مدرسة قريبة ويحب القراءة.','أبو ليلى يعمل في مدرسة قريبة ويحب القراءة.'),
 ],
 'ar-a1-u04-p04':[
  ('أخبرتني أمي أن المكتبة عندها نشاط صغير غدًا.','أخبرتني أمي أن في المكتبة نشاطًا صغيرًا غدًا.'),
 ],
 'ar-a1-u04-p05':[
  ('يأتي أب ليلى وأمها وأخوها،','يأتي أبو ليلى وأمها وأخوها،'),
 ],
 'ar-a1-u04-p06':[
  ('في البيت تعرف أباها وأمها وأخوها،','في البيت تعرف أباها وأمها وأخاها،'),
 ],
 'ar-a1-u05-p01':[
  ('لأن الدرس يبدأ منظمًا.','لأن الدرس يبدأ بشكل منظم.'),
 ],
 'ar-a1-u06-p01':[
  ('من هناك امشي نحو اليمين قليلًا،','من هناك اتجهي قليلًا نحو اليمين،'),
 ],
 'ar-a1-u06-p02':[
  ('أظن أننا نصل الآن.','أظن أننا سنصل الآن.'),
 ],
 'ar-a1-u06-p06':[
  ('إذا أرادت مكانًا جديدًا تنظر إلى موقعه وتسأل أين هو.','إذا أرادت الذهاب إلى مكان جديد تنظر إلى موقعه وتسأل أين هو.'),
 ],
 'ar-a1-u07-p02':[
  ('في الطريق ترى الشمس قليلًا،','في الطريق ترى الشمس تظهر قليلًا،'),
 ],
 'ar-a1-u07-p03':[
  ('ننظر إلى الجو القادم،','ننظر إلى طقس اليوم القادم،'),
 ],
 'ar-a1-u07-p04':[
  ('تلاحظ ليلى أن الصباح لا يكون مثل نفسه في كل أيام الأسبوع.','تلاحظ ليلى أن الصباح يختلف من يوم إلى آخر خلال الأسبوع.'),
 ],
 'ar-a1-u07-p05':[
  ('وتضع علامة بجانب الأيام التي قد تمطر فيها السماء.','وتضع علامة بجانب الأيام التي قد يكون فيها مطر.'),
 ],
 'ar-a1-u07-p06':[
  ('وإذا كانت السماء كثيرة الغيوم تقول:','وإذا كانت السماء مليئة بالغيوم تقول:'),
 ],
 'ar-a1-u08-p01':[
  ('بعد فترة تقول: أشعر أفضل قليلًا.','بعد فترة تقول: أشعر أنني أفضل قليلًا.'),
 ],
 'ar-a1-u08-p02':[
  ('طلب المساعدة جيد عندما تكون المهمة أكبر من شخص واحد.','طلب المساعدة جيد عندما تكون المهمة أكبر من أن يقوم بها شخص واحد.'),
 ],
 'ar-a1-u08-p03':[
  ('ماذا نستخدم اليد لفعل أشياء كثيرة؟','ماذا نفعل باليد؟'),
 ],
 'ar-a1-u08-p04':[
  ('ثم تطلب من ليلى أن تسمع صوت قلبها بعد حركة قصيرة.','ثم تطلب من ليلى أن تستمع إلى صوت قلبها بعد حركة قصيرة.'),
  ('تمشي ليلى بسرعة دقيقة، ثم تجلس.','تمشي ليلى بسرعة لمدة دقيقة، ثم تجلس.'),
  ('الآن أشعر أن قلبي أسرع.','الآن أشعر أن نبض قلبي أسرع.'),
 ],
 'ar-a1-u08-p05':[
  ('وعندما أشعر أفضل أحاول من جديد خطوة صغيرة.','وعندما أشعر أنني أفضل أحاول من جديد خطوة صغيرة.'),
 ],
 'ar-a1-u09-p05':[
  ('كان عندنا هدف في النتيجة، وكان عندنا هدف آخر هو اللعب بطريقة جيدة.','كان هدفنا أن نسجل، وكان لنا هدف آخر هو اللعب بطريقة جيدة.'),
 ],
 'ar-a1-u10-p01':[
  ('تأكل فطورًا صغيرًا،','تأكل فطورًا خفيفًا،')
 ],
 'ar-a1-u10-p03':[
  ('تقول ليلى إنها تعلمت طريقة جديدة لتنظيم سؤال القراءة.','تقول ليلى إنها تعلمت طريقة جديدة للتعامل مع سؤال القراءة.'),
 ],
 'ar-a1-u10-p04':[
  ('لأنها تحفظ شكل لحظة لا تبقى طويلًا.','لأنها تحفظ لحظة لا تدوم طويلًا.'),
 ],
 'ar-a1-u10-p05':[
  ('والسؤال يساعدني على معرفة هل فهمت ما قرأت.','والسؤال يساعدني على أن أعرف هل فهمت ما قرأت.'),
 ],
 'ar-a1-u10-p06':[
  ('في نهاية مستوى المستوى المبتدئ الأول تستطيع ليلى','في نهاية المستوى المبتدئ الأول تستطيع ليلى'),
 ],
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];by={r['id']:r for r in rows};done=[]
for pid,repls in REPAIRS.items():
 r=by[pid]
 for old,new in repls:
  assert r['text'].count(old)==1,(pid,old,r['text'])
  r['text']=r['text'].replace(old,new);done.append({'passage_id':pid,'old':old,'new':new})
 r['word_count']=len(r['text'].split());r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final Arabic Pass 11 manual naturalness review: corrected one or more high-confidence MSA grammar/idiom defects; passage intent and assessment structure preserved.'
 if note not in notes:notes.append(note)
assert len(done)==28,len(done)
PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
print(json.dumps({'reviewed_passages':60,'touched_passages':len(REPAIRS),'repairs':len(done),'changes':done},ensure_ascii=False))
