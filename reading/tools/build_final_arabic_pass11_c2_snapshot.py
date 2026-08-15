#!/usr/bin/env python3
"""Build the post-recalibration Arabic C2 Pass 11 title/text snapshot."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'reading/arabic/c2/passages.jsonl'
OUT=ROOT/'reading/audit/final_arabic_pass11_c2_snapshot.jsonl'
rows=[json.loads(x) for x in SOURCE.read_text(encoding='utf-8').splitlines() if x.strip()]
assert len(rows)==60,len(rows)
rows=sorted(rows,key=lambda r:r['sequence'])
assert [r['sequence'] for r in rows]==list(range(1,61))
for r in rows:
    assert r['cefr']=='C2',r['id']
    assert 700<=r['word_count']<=1200,(r['id'],r['word_count'])
    assert not re.search(r'[A-Za-z]',r['title']),('latin-title',r['id'])
    assert not re.search(r'[A-Za-z]',r['text']),('latin-text',r['id'])
compact=[{'id':r['id'],'unit':r['unit'],'sequence':r['sequence'],'title':r['title'],'text':r['text']} for r in rows]
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in compact)+'\n',encoding='utf-8')
print(json.dumps({'level':'C2','passages':len(compact),'min_words':min(r['word_count'] for r in rows),'max_words':max(r['word_count'] for r in rows),'snapshot':str(OUT.relative_to(ROOT))},ensure_ascii=False))
