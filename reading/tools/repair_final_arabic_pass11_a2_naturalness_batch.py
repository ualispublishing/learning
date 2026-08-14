#!/usr/bin/env python3
"""Apply high-confidence defects found by the full manual A2 Pass-11 prose read."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/a2/passages.jsonl'
REPAIRS={
 'ar-a2-u03-p01':[
  ('أعطتها الصورة نظرة إلى فترة لا تحتفظ عنها بذكريات كثيرة.','منحتها الصورة نظرة على فترة لا تحتفظ عنها بذكريات كثيرة.'),
 ],
 'ar-a2-u03-p02':[
  ('وطلبت من نور أن تأخذ نظرة إلى الصور المحفوظة في المجلد نفسه.','وطلبت من نور أن تلقي نظرة على الصور المحفوظة في المجلد نفسه.'),
 ],
 'ar-a2-u06-p05':[
  ('ولا توجد حركة سيارات كبيرة.','ولا توجد حركة سيارات كثيفة.'),
 ],
 'ar-a2-u07-p02':[
  ('كان الخبر منشورًا في موقع صحافة محلية،','كان الخبر منشورًا في موقع صحفي محلي،'),
 ],
 'ar-a2-u10-p03':[
  ('اختارتا التذكرة الثانية لأنها أكثر مناسبة للاتصال بين وسيلتي النقل.','اختارتا التذكرة الثانية لأنها أنسب للانتقال بين وسيلتي النقل.'),
 ],
 'ar-a2-u10-p04':[
  ('أن ثلاث مبانٍ ستجرب أجهزة تقيس استهلاك الكهرباء مدة شهرين.','أن ثلاثة مبانٍ ستجرب أجهزة تقيس استهلاك الكهرباء مدة شهرين.'),
 ],
 'ar-a2-u10-p06':[
  ('بعد إنهاء مستوى المستوى المبتدئ الثاني،','بعد إنهاء المستوى المبتدئ الثاني،'),
 ],
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];by={r['id']:r for r in rows};changes=[]
for pid,repls in REPAIRS.items():
 r=by[pid]
 for old,new in repls:
  assert r['text'].count(old)==1,(pid,old,r['text'])
  r['text']=r['text'].replace(old,new);changes.append({'passage_id':pid,'old':old,'new':new})
 r['word_count']=len(r['text'].split());r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final Arabic Pass 11 manual naturalness review: corrected a high-confidence A2 MSA grammar/idiom defect; passage intent and assessment structure preserved.'
 if note not in notes:notes.append(note)
assert len(changes)==7,len(changes)
PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
print(json.dumps({'reviewed_passages':60,'touched_passages':len(REPAIRS),'repairs':len(changes),'changes':changes},ensure_ascii=False))
