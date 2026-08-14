#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl';PID='ar-a1-u07-p03';OLD='وتخبرانهـا';NEW='وتخبرانها'
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
r=next(x for x in rows if x['id']==PID)
assert r['text'].count(OLD)==1,r['text']
r['text']=r['text'].replace(OLD,NEW);assert 'ـ' not in r['text']
r['word_count']=len(r['text'].split());r['revision']=int(r.get('revision',1))+1
notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final audit Pass 05 orthography repair: corrected «وتخبرانهـا» to «وتخبرانها»; no semantic change.'
if note not in notes:notes.append(note)
PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
print(json.dumps({'passage_id':PID,'old':OLD,'new':NEW},ensure_ascii=False))
