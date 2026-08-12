#!/usr/bin/env python3
"""Structural and content-quality inventory for arabic_phrase_bank.csv."""
from __future__ import annotations
import csv, json, re, unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TARGET=ROOT/'arabic_phrase_bank.csv'; AUDIT=ROOT/'audit'; AUDIT.mkdir(exist_ok=True)
AR=re.compile(r'[\u0600-\u06FF]'); LAT=re.compile(r'[A-Za-z]'); PLACE=re.compile(r'(?:placeholder|phrase[_ -]?\d+|arabic[_ -]?phrase[_ -]?\d+)',re.I)

def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s or '').strip())
def main():
 with TARGET.open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f); headers=reader.fieldnames or []; rows=list(reader)
 samples=rows[:20]
 field_stats={}
 for h in headers:
  vals=[norm(r.get(h,'')) for r in rows]; non=[v for v in vals if v]
  field_stats[h]={'nonblank':len(non),'blank':len(vals)-len(non),'distinct':len(set(non)),'arabic_rows':sum(bool(AR.search(v)) for v in non),'latin_rows':sum(bool(LAT.search(v)) for v in non),'placeholder_rows':sum(bool(PLACE.search(v)) for v in non),'max_length':max((len(v) for v in non),default=0),'avg_length':round(sum(map(len,non))/len(non),2) if non else 0}
 exact_rows=Counter(tuple(norm(r.get(h,'')) for h in headers) for r in rows)
 duplicate_exact=sum(n-1 for n in exact_rows.values() if n>1)
 # detect likely Arabic and English columns by script prevalence
 arabic_cols=sorted(headers,key=lambda h:field_stats[h]['arabic_rows'],reverse=True)
 english_cols=sorted(headers,key=lambda h:field_stats[h]['latin_rows'],reverse=True)
 summary={'file':'arabic_phrase_bank.csv','size_bytes':TARGET.stat().st_size,'headers':headers,'rows':len(rows),'exact_duplicate_excess_rows':duplicate_exact,'likely_arabic_columns':arabic_cols[:5],'likely_latin_columns':english_cols[:5],'field_stats':field_stats,'sample_rows':samples,'structural_problems':[]}
 if not headers:summary['structural_problems'].append('no_header')
 if not rows:summary['structural_problems'].append('no_rows')
 (AUDIT/'arabic_phrase_bank_inventory.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
