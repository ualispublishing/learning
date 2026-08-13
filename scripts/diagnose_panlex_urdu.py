#!/usr/bin/env python3
from __future__ import annotations
import json,requests,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'audit/panlex_urdu_diagnostic.json'
API='https://api.panlex.org/v2'
WORDS=['پیج','گن','پولیس','کرتا','مطابق','اعلان','کورٹ','لازمی','لشکر','تجدید','جاسوسی','فوائد','پیدل','سرخ','کرن','امریکہ','اردو','معذرت','عادت','صفحہ']
def post(ep,p):
 r=requests.post(API+ep,json=p,timeout=30);r.raise_for_status();return r.json()
def translations(word):
 q=post('/expr',{'uid':'urd-000','txt':word,'limit':20})
 agg={}
 for rec in q.get('result',[]):
  exid=rec.get('id')
  if not exid:continue
  z=post('/expr',{'trans_expr':exid,'uid':'eng-000','include':'trans_quality','trans_distance':1,'sort':'trans_quality desc','limit':20})
  for t in z.get('result',[]):
   txt=t.get('txt') or t.get('text') or ''
   qual=t.get('trq',t.get('trans_quality',0)) or 0
   if txt:agg[txt]=max(float(qual),agg.get(txt,0))
 return [{'translation':k,'quality':v} for k,v in sorted(agg.items(),key=lambda x:(-x[1],x[0]))[:12]]
def main():
 out={'api':API,'from_uid':'urd-000','to_uid':'eng-000','words':{},'errors':{}}
 for w in WORDS:
  try:out['words'][w]=translations(w)
  except Exception as e:out['errors'][w]=repr(e)
  time.sleep(.15)
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
