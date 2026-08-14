#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/b2/passages.jsonl'
PID='ar-b2-u04-p06'
OLD='والميدان الذي يقيس نجاحه بعدد الزوار يضع وزنًا أكبر على من يأتي أحيانًا من من يعيش مع أثر المكان كل يوم.'
NEW='والميدان الذي يقيس نجاحه بعدد الزوار يعطي وزنًا أكبر لمن يأتي أحيانًا منه لمن يعيش مع أثر المكان كل يوم.'
rows=[json.loads(line) for line in PATH.read_text(encoding='utf-8').splitlines() if line.strip()]
row=next(r for r in rows if r['id']==PID)
assert row['text'].count(OLD)==1,row['text']
row['text']=row['text'].replace(OLD,NEW)
assert ' من من ' not in row['text']
row['word_count']=len(row['text'].split())
row['revision']=int(row.get('revision',1))+1
notes=row.setdefault('quality',{}).setdefault('notes',[])
note='Final Arabic naturalness review: repaired the awkward comparative sequence «من من» in the public-space design synthesis; meaning unchanged.'
if note not in notes:notes.append(note)
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'passage_id':PID,'old':OLD,'new':NEW,'word_count':row['word_count']},ensure_ascii=False))
