#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TARGETS={
'a1': [('ar-a1-u03-p01','ar-r124'),('ar-a1-u06-p02','ar-r317'),('ar-a1-u09-p03','ar-r205'),('ar-a1-u10-p02','ar-r249')],
'a2': [('ar-a2-u02-p01','ar-r663'),('ar-a2-u02-p02','ar-r648'),('ar-a2-u02-p04','ar-r707'),('ar-a2-u03-p04','ar-r936')],
}
for level,pairs in TARGETS.items():
 rows=[json.loads(x) for x in (ROOT/f'reading/arabic/{level}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
 idx={r['id']:r for r in rows}
 for pid,tid in pairs:
  r=idx[pid]
  t=next((x for x in r.get('new_lexical_targets',[]) if x.get('id')==tid),{})
  print(f'### {pid} | {tid} | {t.get("form")} | lemma={t.get("lemma")} | declared={t.get("exposures_in_text")}')
  print(r['text'])
  print()
