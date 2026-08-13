#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
SECOND_PASS='second-pass educator review (2026-08-13)'
PARSE=re.compile(
    r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$'
)

def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    changed=0
    for idx,row in enumerate(rows,1):
        back=row.get('Back','')
        if SECOND_PASS not in back:
            continue
        m=PARSE.match(back)
        if not m:
            raise SystemExit(f'cannot parse second-pass card layout at row {idx}: {row.get("Front","")}')
        rank,meaning,pos,sources=m.groups()
        if int(rank)!=idx:
            raise SystemExit(f'rank mismatch at row {idx}: {rank}')
        meaning=re.sub(r'\s+',' ',meaning).strip()
        pos=re.sub(r'\s+',' ',pos).strip()
        sources=sources.strip()
        normalized=f'Rank: {rank}\n\nMeaning: {meaning}\n\nPart of speech: {pos}\n\nSources:\n{sources}'
        if normalized!=back.strip():
            row['Back']=normalized
            changed+=1
    with TARGET.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n')
        w.writeheader(); w.writerows(rows)
    print(f'normalized {changed} second-pass Arabic card layouts')

if __name__=='__main__':
    main()
