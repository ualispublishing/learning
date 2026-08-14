#!/usr/bin/env python3
"""Normalize C2 U01 P03 مبرر to one source-tight noun sense.

The draft mixed noun 'justification/reason' and adjectival 'justified' uses under
a target declared as noun. Rewrite only the two adjectival constructions so all
deliberate exposures support the noun sense 'justification; reason that justifies'.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/c2/passages.jsonl';PID='ar-c2-u01-p03';TID='ar-r2401'
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];r=next(x for x in rows if x['id']==PID)
h=[t for t in r.get('new_lexical_targets',[]) if t.get('id')==TID];assert len(h)==1,h;t=h[0]
assert t.get('part_of_speech')=='noun',t
assert t.get('intended_sense')=='justified; having a justification',t
old1='الاعتقاد صحيح، ولدى الشخص سبب يبدو له مبررًا: ساعة اعتاد الاعتماد عليها.'
new1='الاعتقاد صحيح، ولدى الشخص مبرر يبدو معقولًا: ساعة اعتاد الاعتماد عليها.'
old2='«إذا كان الاعتقاد صحيحًا ومبررًا، فما الذي ينقص؟»'
new2='«إذا كان الاعتقاد صحيحًا وله مبرر، فما الذي ينقص؟»'
assert r['text'].count(old1)==1 and r['text'].count(old2)==1
r['text']=r['text'].replace(old1,new1).replace(old2,new2)
t['intended_sense']='justification; reason that justifies a belief or action'
# Reader-facing definition already describes the noun sense; tighten wording slightly.
a={x['question_id']:x for x in r['answer_key']};q={x['id']:x for x in r['questions']}
assert q['q9']['target_ids']==[TID]
q['q9']['prompt']='ما معنى «مبرر» في هذا النص؟'
a['q9']['answer']='سبب أو أساس معقول يُقدَّم لتسويغ اعتقاد أو فعل.'
r['word_count']=len(r['text'].split());r['revision']=int(r.get('revision',1))+1
notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final lexical-sense review: normalized مبرر/ar-r2401 to the noun sense «justification/reason» and removed adjectival uses from the passage; argument unchanged.'
if note not in notes:notes.append(note)
# Guard: no obvious adjectival forms from the old wording remain.
assert 'صحيحًا ومبررًا' not in r['text'] and 'سبب يبدو له مبررًا' not in r['text']
PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
print(json.dumps({'passage_id':PID,'target_id':TID,'new_intended_sense':t['intended_sense'],'word_count':r['word_count']},ensure_ascii=False))
