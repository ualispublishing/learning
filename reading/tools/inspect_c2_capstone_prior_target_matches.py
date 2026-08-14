#!/usr/bin/env python3
from __future__ import annotations
import json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/c2/passages.jsonl';OUT=ROOT/'reading/audit/final_arabic_c2_capstone_prior_target_matches.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
def norm(s):
 s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا');return DIAC.sub('',s)
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
cap=next(r for r in rows if r['id']=='ar-c2-u10-p06');text=' '+norm(cap['text'])+' '
matches=[]
for r in rows:
 if r['sequence']>=60:continue
 for t in r.get('new_lexical_targets',[]):
  if not isinstance(t,dict):continue
  form=norm(t.get('form','')).strip();lemma=norm(t.get('lemma','')).strip()
  hit_form=bool(form and f' {form} ' in text);hit_lemma=bool(lemma and f' {lemma} ' in text)
  if hit_form or hit_lemma:
   matches.append({'introduced_in':r['id'],'target_id':t.get('id'),'form':t.get('form'),'lemma':t.get('lemma'),'intended_sense':t.get('intended_sense'),'hit_form':hit_form,'hit_lemma':hit_lemma})
OUT.write_text(json.dumps({'capstone':'ar-c2-u10-p06','matches':matches,'count':len(matches)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'count':len(matches),'matches':matches},ensure_ascii=False))
