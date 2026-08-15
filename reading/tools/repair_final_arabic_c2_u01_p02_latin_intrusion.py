#!/usr/bin/env python3
"""Remove the residual Latin-script intrusion from Arabic C2 U01 P02."""
from __future__ import annotations
import copy,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/c2/passages.jsonl'
PID='ar-c2-u01-p02'
OLD='لكنه لا يعيد deliberation في اللحظة نفسها'
NEW='لكنه لا يعيد التفكير المتأني في اللحظة نفسها'
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
found=0
for r in rows:
    if r.get('id')!=PID: continue
    found+=1
    before=copy.deepcopy(r)
    assert r['text'].count(OLD)==1,(PID,'old-count',r['text'].count(OLD))
    r['text']=r['text'].replace(OLD,NEW)
    assert OLD not in r['text']
    assert not re.search(r'[A-Za-z]',r['text']),(PID,'latin-remains')
    for t in r.get('new_lexical_targets',[]):
        assert r['text'].count(t['form'])==t['exposures_in_text'],(PID,t['form'],r['text'].count(t['form']),t['exposures_in_text'])
    assert r['questions']==before['questions'],PID
    assert r['answer_key']==before['answer_key'],PID
    assert r['new_lexical_targets']==before['new_lexical_targets'],PID
    assert r['review_lexical_targets']==before['review_lexical_targets'],PID
    r['revision']=int(r.get('revision',0))+1
    r.setdefault('quality',{}).setdefault('notes',[]).append('Final Pass 11 pre-snapshot repair: replaced a residual Latin-script intrusion in reader-facing Arabic with natural MSA; assessment and lexical exposure contracts preserved.')
assert found==1,found
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'passage':PID,'repair':'deliberation -> التفكير المتأني'},ensure_ascii=False))
