#!/usr/bin/env python3
"""Build a compact title/text-only C1 snapshot for manual Pass 11 review."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/arabic/c1/passages.jsonl'
OUT=ROOT/'reading/audit/final_arabic_pass11_c1_snapshot.jsonl'
rows=[json.loads(x) for x in SRC.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(rows)!=60:
    raise RuntimeError(f'expected 60 C1 passages, got {len(rows)}')
seen=set();out=[]
for r in rows:
    pid=r.get('id')
    if not pid or pid in seen:
        raise RuntimeError(f'duplicate/missing id: {pid}')
    seen.add(pid)
    wc=int(r.get('word_count',0))
    if not 500<=wc<=800:
        raise RuntimeError(f'{pid}: C1 word_count outside 500-800: {wc}')
    out.append({'id':pid,'unit':r.get('unit'),'sequence':r.get('sequence'),'title':r.get('title'),'text':r.get('text')})
OUT.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in out)+'\n',encoding='utf-8')
print(f'wrote {len(out)} compact C1 naturalness-review snapshots')
