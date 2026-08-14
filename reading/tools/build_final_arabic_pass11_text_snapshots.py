#!/usr/bin/env python3
"""Build compact text-only snapshots for manual Arabic naturalness review."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUTDIR=ROOT/'reading/audit/pass11_texts'
OUTDIR.mkdir(parents=True,exist_ok=True)
summary={}
for level in LEVELS:
    src=ROOT/f'reading/arabic/{level}/passages.jsonl'
    rows=[]
    for raw in src.read_text(encoding='utf-8').splitlines():
        if not raw.strip():continue
        r=json.loads(raw)
        rows.append({'id':r['id'],'sequence':r.get('sequence'),'unit':r.get('unit'),'title':r.get('title',''),'text':r.get('text','')})
    assert len(rows)==60,(level,len(rows))
    out=OUTDIR/f'arabic_{level}_texts.jsonl'
    out.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf-8')
    summary[level]={'rows':len(rows),'path':str(out.relative_to(ROOT))}
(ROOT/'reading/audit/final_arabic_pass11_text_snapshot_summary.json').write_text(json.dumps({'scope':'manual naturalness review text-only snapshots','levels':summary},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
