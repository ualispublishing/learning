#!/usr/bin/env python3
"""Guarded Pass 07 length remediation for all remaining short Arabic A1 passages (Units 07-10)."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
TOKEN=re.compile(r'\S+')
SPECS={
 'ar-a1-u07-p01':{'old_wc':77,'unit':7,'sentence_increment':1,'addition':'تضع ليلى زجاجة ماء في حقيبتها، ثم تغلق النافذة وتخرج مع أمها إلى المدرسة.'},
 'ar-a1-u07-p02':{'old_wc':82,'unit':7,'sentence_increment':1,'addition':'تأخذ معها زجاجة ماء، ثم تمشي مع أمها إلى باب المدرسة.'},
 'ar-a1-u07-p03':{'old_wc':84,'unit':7,'sentence_increment':1,'addition':'ويضعن أيضًا زجاجات ماء صغيرة في حقائبهن قبل الخروج.'},
 'ar-a1-u08-p01':{'old_wc':76,'unit':8,'sentence_increment':2,'addition':'تنام ليلى قليلًا، ثم تستيقظ وتشرب ماءً آخر. تبقى في البيت بقية المساء وتقرأ كتابًا قصيرًا.'},
 'ar-a1-u08-p02':{'old_wc':89,'unit':8,'sentence_increment':1,'addition':'بعد الحصة تعيدان الكتب إلى الرف معًا.'},
 'ar-a1-u08-p03':{'old_wc':77,'unit':8,'sentence_increment':1,'addition':'في آخر الدرس يطلب المعلم منهم الوقوف، ثم يشرح أسماء أخرى من الجسم ويكتبها على اللوح.'},
 'ar-a1-u09-p01':{'old_wc':87,'unit':9,'sentence_increment':1,'addition':'ثم يشرب الجميع الماء.'},
 'ar-a1-u09-p03':{'old_wc':85,'unit':9,'sentence_increment':1,'addition':'قبل العودة يجمعون أغراضهم، ثم يمشون معًا إلى باب الحديقة.'},
 'ar-a1-u10-p01':{'old_wc':89,'unit':10,'sentence_increment':1,'addition':'بعد الحصة ترتب كتبها في الخزانة قبل أن تبدأ يومها الدراسي.'},
 'ar-a1-u10-p02':{'old_wc':87,'unit':10,'sentence_increment':1,'addition':'بعد الدرس يكتب سامر الكلمة في دفتره حتى يتذكرها في البيت.'},
 'ar-a1-u10-p04':{'old_wc':88,'unit':10,'sentence_increment':1,'addition':'بعد ذلك تغلق ليلى الهاتف وتضع الألبوم قرب كتبها على الرف.'},
}
def wc(t): return len(TOKEN.findall(t))
def target_counts(r):
 text=str(r.get('text','')).casefold(); out={}
 for t in r.get('new_lexical_targets',[]):
  form=str(t.get('form','')).strip()
  if not form: raise SystemExit(f"{r['id']}: blank target")
  out[str(t.get('id',form))]=text.count(form.casefold())
 return out
def main():
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=60: raise SystemExit(f'expected 60 rows, found {len(rows)}')
 by={r['id']:r for r in rows}
 missing=sorted(set(SPECS)-set(by))
 if missing: raise SystemExit(f'missing targets: {missing}')
 touched=[]
 for pid,s in SPECS.items():
  r=by[pid]; old=str(r.get('text','')).strip(); stored=int(r.get('word_count',0) or 0); actual=wc(old)
  if r.get('unit')!=s['unit']: raise SystemExit(f'{pid}: wrong unit')
  if stored!=s['old_wc'] or actual!=s['old_wc']: raise SystemExit(f'{pid}: source changed; expected {s["old_wc"]}, got {stored}/{actual}')
  if s['addition'] in old: raise SystemExit(f'{pid}: addition already present')
  bt=target_counts(r); bq=json.dumps(r.get('questions'),ensure_ascii=False,sort_keys=True); ba=json.dumps(r.get('answer_key'),ensure_ascii=False,sort_keys=True); bm=json.dumps(r.get('new_lexical_targets'),ensure_ascii=False,sort_keys=True)
  r['text']=old+' '+s['addition']; r['word_count']=wc(r['text']); r['sentence_count']=int(r.get('sentence_count',0) or 0)+s['sentence_increment']; r['revision']=int(r.get('revision',0) or 0)+1
  if not 90<=r['word_count']<=140: raise SystemExit(f'{pid}: count {r["word_count"]} outside A1 band')
  if target_counts(r)!=bt: raise SystemExit(f'{pid}: new target occurrence count changed: {bt} -> {target_counts(r)}')
  if json.dumps(r.get('questions'),ensure_ascii=False,sort_keys=True)!=bq: raise SystemExit(f'{pid}: questions changed')
  if json.dumps(r.get('answer_key'),ensure_ascii=False,sort_keys=True)!=ba: raise SystemExit(f'{pid}: answer key changed')
  if json.dumps(r.get('new_lexical_targets'),ensure_ascii=False,sort_keys=True)!=bm: raise SystemExit(f'{pid}: target metadata changed')
  note='Final review Pass 07: expanded below-band passage into the A1 90-140 production band; questions and new-target exposure counts preserved.'
  notes=r.setdefault('quality',{}).setdefault('notes',[])
  if note not in notes: notes.append(note)
  touched.append((pid,stored,r['word_count']))
 # This is the final A1 length batch: every A1 passage must now be in the standard band.
 for r in rows:
  if not 90<=int(r.get('word_count',0) or 0)<=140:
   raise SystemExit(f'{r["id"]}: A1 passage still outside standard band at {r.get("word_count")}')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
 print(json.dumps({'level':'A1','units':[7,8,9,10],'passages_touched':len(touched),'word_counts':touched},ensure_ascii=False))
if __name__=='__main__': main()
