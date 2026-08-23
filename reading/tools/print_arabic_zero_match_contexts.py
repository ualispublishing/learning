#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PASSAGES={
'a1': [
'ar-a1-u03-p01','ar-a1-u06-p02','ar-a1-u08-p05','ar-a1-u09-p03','ar-a1-u10-p02',
'ar-a1-u05-p05','ar-a1-u07-p04','ar-a1-u09-p01','ar-a1-u10-p01'
],
'a2': [
'ar-a2-u02-p01','ar-a2-u02-p02','ar-a2-u02-p04','ar-a2-u03-p01','ar-a2-u03-p04','ar-a2-u06-p04'
],
}
FORMS={'يحب','يصل','حاول','سعيد','مختلف','رد','متأكد','حالي','ظن','يتوقف','يعود','أيام','لاعب','دائما','قليل','مجددا'}
for level,pids in PASSAGES.items():
 rows=[json.loads(x) for x in (ROOT/f'reading/arabic/{level}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
 idx={r['id']:r for r in rows}
 for pid in pids:
  r=idx[pid]
  ts=[t for t in r.get('new_lexical_targets',[]) if t.get('form') in FORMS]
  print(f'### {pid}')
  print('targets:', json.dumps([{k:t.get(k) for k in ('id','form','lemma','part_of_speech','intended_sense','exposures_in_text')} for t in ts],ensure_ascii=False))
  print(r['text'])
  print()
