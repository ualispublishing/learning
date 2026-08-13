#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
FIELDS=re.compile(r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$')
SOURCE='- Arabic Language Academy in Cairo / Quranic Arabic Corpus - second-pass educator review (2026-08-13)'
REPAIRS={
115:{'front':'\u0639\u0646\u062f','meaning':'at; near; with/in the possession of','pos':'temporal/spatial adverbial noun'},
143:{'front':'\u0623\u064a\u0647\u0627','meaning':'O...! (formal masculine vocative introducer)','pos':'vocative expression'},
276:{'front':'\u0635\u0628\u0627\u062d','meaning':'morning; in the morning','pos':'noun; adverbial time expression in context'},
320:{'front':'\u062d\u0633\u0646','meaning':'good/fine; goodness/beauty; became good/beautiful (depending on vocalization)','pos':'adjective / noun / perfect-past verb'},
354:{'front':'\u0639\u0642\u062f','meaning':'contract/agreement; decade; necklace; held/concluded/tied (depending on vocalization)','pos':'noun / perfect-past verb'},
}
def parse(back):
    m=FIELDS.match(back or '')
    if not m: raise SystemExit('cannot parse card fields')
    rank,meaning,pos,sources=m.groups()
    return int(rank),re.sub(r'\s+',' ',meaning).strip(),re.sub(r'\s+',' ',pos).strip(),sources.strip()
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
    print('refined',len(REPAIRS),'Arabic cards')
if __name__=='__main__': main()
