#!/usr/bin/env python3
"""Build a compact title/text-only B1 snapshot for manual Pass 11 review.

This does not judge or modify passage quality. It removes question/answer and
metadata noise so the independent naturalness pass can read every canonical B1
text after final length/question remediation.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/arabic/b1/passages.jsonl'
OUT=ROOT/'reading/audit/final_arabic_pass11_b1_snapshot.jsonl'
# The snapshot is intentionally derived from current canonical B1 on every run.
rows=[json.loads(x) for x in SRC.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(rows)!=60:
    raise RuntimeError(f'expected 60 B1 passages, got {len(rows)}')
seen=set(); out=[]
for r in rows:
    pid=r.get('id')
    if not pid or pid in seen: raise RuntimeError(f'duplicate/missing id: {pid}')
    seen.add(pid)
    out.append({'id':pid,'unit':r.get('unit'),'sequence':r.get('sequence'),'title':r.get('title'),'text':r.get('text')})
OUT.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in out)+'\n',encoding='utf-8')
print(f'wrote {len(out)} compact B1 naturalness-review snapshots')
