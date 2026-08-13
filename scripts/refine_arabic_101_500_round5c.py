#!/usr/bin/env python3
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
FIELDS=re.compile(r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$')
SOURCE='- Arabic Language Academy in Cairo, Al-Mujam Al-Wasit - common-polysemy educator review (2026-08-13)'
RANK=456; FRONT='\u0630\u0643\u0631'
def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    row=rows[RANK-1]
    if row['Front']!=FRONT: raise SystemExit('front mismatch')
    m=FIELDS.match(row['Back'] or '')
    if not m or int(m.group(1))!=RANK: raise SystemExit('metadata mismatch')
    sources=[x.rstrip() for x in m.group(4).strip().splitlines() if x.strip()]
    if SOURCE not in sources: sources.append(SOURCE)
    meaning='masculine being; mention or remembrance; mentioned or recalled'
    pos='noun / perfect-past verb'
    row['Back']=f'Rank: {RANK}\n\nMeaning: {meaning}\n\nPart of speech: {pos}\n\nSources:\n'+"\n".join(sources)
    with TARGET.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n');w.writeheader();w.writerows(rows)
if __name__=='__main__': main()
