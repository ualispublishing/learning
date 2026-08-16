#!/usr/bin/env python3
"""Guarded Pass 07 length remediation for remaining short A1 passages in Units 05-06."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
TOKEN=re.compile(r'\S+')
SPECS={
 'ar-a1-u05-p02':{'old_wc':83,'unit':5,'sentence_increment':2,'addition':'قبل أن تعود، تنظر إلى لوحة صغيرة قرب الباب وتقرأ موعد اجتماع المعلمين. ثم تسير في الممر بهدوء حتى تصل إلى صفها.'},
 'ar-a1-u06-p01':{'old_wc':77,'unit':6,'sentence_increment':2,'addition':'بعد أن تدخل المبنى تسأل الموظفة عن قسم الكتب، فتشير إلى الطابق الثاني. تصعد الدرج، وتجد القاعة مفتوحة وهادئة.'},
 'ar-a1-u06-p02':{'old_wc':81,'unit':6,'sentence_increment':2,'addition':'في الداخل يضع الأب الحقائب قرب الباب، وتساعده ليلى في حمل صندوق خفيف إلى القاعة. بعدها يجلسان قليلًا قبل بدء النشاط.'},
 'ar-a1-u06-p03':{'old_wc':83,'unit':6,'sentence_increment':2,'addition':'في الملعب تجلسان قليلًا قرب الأشجار، ثم تمشيان حول الساحة وتشاهدان الأطفال يلعبون. بعد ذلك تعودان إلى البيت معًا.'},
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
  if target_counts(r)!=bt: raise SystemExit(f'{pid}: new target occurrence count changed')
  if json.dumps(r.get('questions'),ensure_ascii=False,sort_keys=True)!=bq: raise SystemExit(f'{pid}: questions changed')
  if json.dumps(r.get('answer_key'),ensure_ascii=False,sort_keys=True)!=ba: raise SystemExit(f'{pid}: answer key changed')
  if json.dumps(r.get('new_lexical_targets'),ensure_ascii=False,sort_keys=True)!=bm: raise SystemExit(f'{pid}: target metadata changed')
  note='Final review Pass 07: expanded below-band passage into the A1 90-140 production band; questions and new-target exposure counts preserved.'
  notes=r.setdefault('quality',{}).setdefault('notes',[])
  if note not in notes: notes.append(note)
  touched.append((pid,stored,r['word_count']))
 # Current Pass07 identifies no other short rows in these two units.
 for r in rows[24:36]:
  if r['id'] not in SPECS and int(r.get('word_count',0) or 0)<90:
   raise SystemExit(f'{r["id"]}: unexpected additional below-band passage in Units05-06')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
 print(json.dumps({'level':'A1','units':[5,6],'passages_touched':len(touched),'word_counts':touched},ensure_ascii=False))
if __name__=='__main__': main()
