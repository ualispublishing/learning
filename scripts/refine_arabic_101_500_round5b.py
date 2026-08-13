#!/usr/bin/env python3
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
FIELDS=re.compile(r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$')
SOURCE='- Arabic Language Academy in Cairo, Al-Mujam Al-Wasit - common-polysemy educator review (2026-08-13)'
REPAIRS={
442:('\u0645\u0647\u0645\u0629','task; mission; assignment; important in the feminine adjective reading','noun / adjective'),
457:('\u062d\u062f\u064a\u062b','modern; recent; new; speech or talk or report; Hadith','adjective / noun'),
458:('\u0638\u0647\u0631','back; noon or midday; appeared or became visible','noun / perfect-past verb'),
}
def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    for rank,(front,meaning,pos) in REPAIRS.items():
        row=rows[rank-1]
        if row['Front']!=front: raise SystemExit(f'rank {rank} front mismatch')
        m=FIELDS.match(row['Back'] or '')
        if not m or int(m.group(1))!=rank: raise SystemExit(f'rank {rank} metadata mismatch')
        sources=[x.rstrip() for x in m.group(4).strip().splitlines() if x.strip()]
        if SOURCE not in sources: sources.append(SOURCE)
        row['Back']=f'Rank: {rank}\n\nMeaning: {meaning}\n\nPart of speech: {pos}\n\nSources:\n'+"\n".join(sources)
    with TARGET.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n');w.writeheader();w.writerows(rows)
if __name__=='__main__': main()
