#!/usr/bin/env python3
"""Repair high-confidence A1 defects found in the post-Pass07 current-text re-read."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
TOKEN=re.compile(r'\S+')
REPAIRS={
'ar-a1-u01-p01':('رأت بابا ونافذة وكرسيا.','رأت الباب والنافذة والكرسي.'),
'ar-a1-u01-p03':('ثم شربت ماء مع أمها قبل العودة.','ثم شربت الماء مع أمها قبل العودة.'),
'ar-a1-u02-p01':('وضعت زجاجة الماء في الحقيبة، وأغلقت النافذة، ثم سألت أمها عن دفتر صغير كان على الطاولة.','تضع زجاجة الماء في الحقيبة، وتغلق النافذة، ثم تسأل أمها عن دفتر صغير على الطاولة.'),
'ar-a1-u02-p03':('وضعت كتبها في مكانها، ثم ساعدت أمها في ترتيب الطاولة قبل النوم.','تضع كتبها في مكانها، ثم تساعد أمها في ترتيب الطاولة قبل النوم.'),
'ar-a1-u03-p04':('بعد الطعام تحمل ليلى كأس الماء إلى الطاولة، وتتأكد أن طلبها صار صحيحًا قبل أن تغادر مع أمها.','بعد الطعام تتأكد ليلى أن طلبها صار صحيحًا قبل أن تغادر مع أمها.'),
'ar-a1-u05-p02':('قبل أن تعود، تنظر إلى لوحة صغيرة قرب الباب وتقرأ موعد اجتماع المعلمين. ثم تسير في الممر بهدوء حتى تصل إلى صفها.','وفي يوم آخر، تنظر ليلى إلى لوحة صغيرة قرب الباب وتقرأ موعد اجتماع المعلمين. ثم تسير في الممر بهدوء حتى تصل إلى صفها.'),
'ar-a1-u08-p01':('تنام ليلى قليلًا، ثم تستيقظ وتشرب ماءً آخر.','تنام ليلى قليلًا، ثم تستيقظ وتشرب مزيدًا من الماء.'),
'ar-a1-u08-p03':('في آخر الدرس يطلب المعلم منهم الوقوف، ثم يشرح أسماء أخرى من الجسم ويكتبها على اللوح.','وفي الحصة التالية يطلب المعلم منهم الوقوف، ثم يشرح أسماء أخرى من الجسم ويكتبها على اللوح.'),
'ar-a1-u10-p01':('بعد الحصة ترتب كتبها في الخزانة قبل أن تبدأ يومها الدراسي.','وقبل بدء الحصة ترتب كتبها في الخزانة وتضع ما تحتاج إليه على الطاولة.'),
}
NOTE='Post-Pass07 naturalness re-review: repaired a high-confidence tense, event-order, logic, or MSA idiom defect introduced by the length expansion.'
def wc(t): return len(TOKEN.findall(t))
def counts(r):
 text=str(r.get('text','')).casefold(); out={}
 for t in r.get('new_lexical_targets',[]):
  f=str(t.get('form','')).strip()
  if not f: raise SystemExit(f"{r['id']}: blank target")
  out[str(t.get('id',f))]=text.count(f.casefold())
 return out
def stable(r,k): return json.dumps(r.get(k),ensure_ascii=False,sort_keys=True)
def main():
 rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or len({r['id'] for r in rows})!=60: raise SystemExit('expected 60 unique A1 passages')
 by={r['id']:r for r in rows}
 for pid,(old,new) in REPAIRS.items():
  r=by[pid]; text=str(r.get('text',''))
  if text.count(old)!=1: raise SystemExit(f'{pid}: expected repair literal exactly once, found {text.count(old)}')
  bt=counts(r); bq=stable(r,'questions'); ba=stable(r,'answer_key'); bn=stable(r,'new_lexical_targets'); br=stable(r,'review_lexical_targets'); bs=stable(r,'speed_training')
  r['text']=text.replace(old,new,1); r['word_count']=wc(r['text']); r['revision']=int(r.get('revision',0) or 0)+1
  if not 90<=r['word_count']<=140: raise SystemExit(f'{pid}: count {r["word_count"]} outside A1 band')
  if counts(r)!=bt: raise SystemExit(f'{pid}: new-target occurrence count changed')
  for k,b in [('questions',bq),('answer_key',ba),('new_lexical_targets',bn),('review_lexical_targets',br),('speed_training',bs)]:
   if stable(r,k)!=b: raise SystemExit(f'{pid}: {k} changed unexpectedly')
  notes=r.setdefault('quality',{}).setdefault('notes',[])
  if NOTE not in notes: notes.append(NOTE)
 PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
 print(json.dumps({'level':'A1','repairs':len(REPAIRS),'passages_touched':len(REPAIRS),'counts':[(p,by[p]['word_count']) for p in REPAIRS]},ensure_ascii=False))
if __name__=='__main__': main()
