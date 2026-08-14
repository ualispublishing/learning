#!/usr/bin/env python3
"""Repair one confirmed A1 U07 P03 naturalness defect while preserving meaning."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl';PID='ar-a1-u07-p03';TID='ar-r363'
OLD='تقول مريم: غدًا قادم بجو أدفأ، لكن ربما يكون هناك مطر في المساء.'
NEW='تقول مريم: غدًا سيكون الجو أدفأ، لكن ربما يكون هناك مطر في المساء.'
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
r=next(x for x in rows if x['id']==PID)
assert r['text'].count(OLD)==1,r['text']
r['text']=r['text'].replace(OLD,NEW)
h=[t for t in r.get('new_lexical_targets',[]) if t.get('id')==TID];assert len(h)==1,h
# Natural text now has two deliberate قادم exposures: first and final sentences.
h[0]['exposures_in_text']=2
assert r['text'].count('قادم')==2,r['text']
r['word_count']=len(r['text'].split());r['revision']=int(r.get('revision',1))+1
notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final Arabic naturalness review: replaced the non-idiomatic forecast «غدًا قادم بجو أدفأ» with «غدًا سيكون الجو أدفأ»; قادم remains naturally exposed twice.'
if note not in notes:notes.append(note)
PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
print(json.dumps({'passage_id':PID,'old':OLD,'new':NEW,'qadam_exposures':2,'word_count':r['word_count']},ensure_ascii=False))
