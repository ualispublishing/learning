#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
FIELDS=re.compile(r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$')
SOURCE='- Second-pass educator review: Arabic Language Academy in Cairo / formal Arabic grammar sources (2026-08-13)'
REPAIRS={
335:{'front':'\u0639\u0644\u0645','meaning':'knowledge; science; flag; knew/recognized; taught/instructed (depending on vocalization/form)','pos':'noun / perfect-past verb'},
347:{'front':'\u0645\u0627','meaning':'how...!; what a...! (exclamative ma in the ma afala pattern)','pos':'exclamative noun in the traditional ma afala analysis'},
}
def parse(back):
    m=FIELDS.match(back or '')
    if not m: raise SystemExit('cannot parse card fields')
    rank,meaning,pos,sources=m.groups()
    return int(rank),meaning.strip(),pos.strip(),sources.strip()
def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    for rank,spec in REPAIRS.items():
        row=rows[rank-1]
        if row['Front']!=spec['front']: raise SystemExit(f'rank {rank} front mismatch')
        card_rank,_,_,sources=parse(row['Back'])
        if card_rank!=rank: raise SystemExit(f'rank {rank} metadata mismatch')
        lines=[x.rstrip() for x in sources.splitlines() if x.strip()]
        if SOURCE not in lines: lines.append(SOURCE)
        row['Back']=f'Rank: {rank}\n\nMeaning: {spec["meaning"]}\n\nPart of speech: {spec["pos"]}\n\nSources:\n'+"\n".join(lines)
    with TARGET.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n'); w.writeheader(); w.writerows(rows)
    print('refined',len(REPAIRS),'cards')
if __name__=='__main__': main()
