#!/usr/bin/env python3
"""Guarded Pass 07 length remediation for the five short Arabic A2 Unit 03 passages."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'
TOKEN=re.compile(r'\S+')
SPECS={
 'ar-a2-u03-p01':{'old_wc':127,'sentence_increment':1,'addition':'وفي المساء سألت أمها عن الأشخاص الظاهرين في الخلف، فشرحت لها أسماء اثنين منهم وقصة الحقيبة قرب الباب.'},
 'ar-a2-u03-p02':{'old_wc':134,'sentence_increment':1,'addition':'ثم سألت أمها عن صوت آخر لم تعرفه.'},
 'ar-a2-u03-p03':{'old_wc':134,'sentence_increment':1,'addition':'وفي النهاية قرأت نور ملاحظاتها لجدها وصححت اسمًا واحدًا.'},
 'ar-a2-u03-p04':{'old_wc':133,'sentence_increment':1,'addition':'ثم ناقش الصف كيف يمكن للصورة أن تغير ما يتذكره شخص ما.'},
 'ar-a2-u03-p05':{'old_wc':136,'sentence_increment':1,'addition':'وفي المساء حكى سامر القصة لأخته الأصغر.'},
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
 if len(rows)!=60: raise SystemExit(f'expected 60 A2 passages, found {len(rows)}')
 by={r['id']:r for r in rows}; missing=sorted(set(SPECS)-set(by))
 if missing: raise SystemExit(f'missing targets: {missing}')
 touched=[]
 for pid,s in SPECS.items():
  r=by[pid]; old=str(r.get('text','')).strip(); stored=int(r.get('word_count',0) or 0); actual=wc(old)
  if r.get('unit')!=3: raise SystemExit(f'{pid}: wrong unit')
  if stored!=s['old_wc'] or actual!=s['old_wc']: raise SystemExit(f'{pid}: source changed; expected {s["old_wc"]}, got {stored}/{actual}')
  if s['addition'] in old: raise SystemExit(f'{pid}: addition already present')
  bt=target_counts(r); bq=json.dumps(r.get('questions'),ensure_ascii=False,sort_keys=True); ba=json.dumps(r.get('answer_key'),ensure_ascii=False,sort_keys=True); bm=json.dumps(r.get('new_lexical_targets'),ensure_ascii=False,sort_keys=True); br=json.dumps(r.get('review_lexical_targets'),ensure_ascii=False,sort_keys=True); old_notes=list(r.get('quality',{}).get('notes',[]))
  r['text']=old+' '+s['addition']; r['word_count']=wc(r['text']); r['sentence_count']=int(r.get('sentence_count',0) or 0)+s['sentence_increment']; r['revision']=int(r.get('revision',0) or 0)+1
  if not 140<=r['word_count']<=220: raise SystemExit(f'{pid}: count {r["word_count"]} outside A2 band')
  if target_counts(r)!=bt: raise SystemExit(f'{pid}: new target occurrence changed: {bt} -> {target_counts(r)}')
  if json.dumps(r.get('questions'),ensure_ascii=False,sort_keys=True)!=bq: raise SystemExit(f'{pid}: questions changed')
  if json.dumps(r.get('answer_key'),ensure_ascii=False,sort_keys=True)!=ba: raise SystemExit(f'{pid}: answer key changed')
  if json.dumps(r.get('new_lexical_targets'),ensure_ascii=False,sort_keys=True)!=bm: raise SystemExit(f'{pid}: target metadata changed')
  if json.dumps(r.get('review_lexical_targets'),ensure_ascii=False,sort_keys=True)!=br: raise SystemExit(f'{pid}: review target metadata changed')
  # Existing Pass11 notes/repairs must survive verbatim; only append the Pass07 note.
  if any(note not in r.get('quality',{}).get('notes',[]) for note in old_notes): raise SystemExit(f'{pid}: existing quality note lost')
  note='Final review Pass 07: expanded below-band passage into the A2 140-220 production band; assessment structure and new-target exposure counts preserved.'
  notes=r.setdefault('quality',{}).setdefault('notes',[])
  if note not in notes: notes.append(note)
  touched.append((pid,stored,r['word_count']))
 p06=by['ar-a2-u03-p06']
 if int(p06.get('word_count',0) or 0)!=145: raise SystemExit(f'ar-a2-u03-p06 source changed; expected 145, got {p06.get("word_count")}')
 if p06.get('new_lexical_targets')!=[] or p06.get('speed_training',{}).get('new_word_policy')!='none': raise SystemExit('ar-a2-u03-p06 zero-new-word policy changed')
 for r in rows[12:18]:
  if not 140<=int(r.get('word_count',0) or 0)<=220: raise SystemExit(f'{r["id"]}: Unit03 remains outside A2 standard band')
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
 print(json.dumps({'level':'A2','unit':3,'passages_touched':len(touched),'word_counts':touched,'p06_untouched':145},ensure_ascii=False))
if __name__=='__main__': main()
