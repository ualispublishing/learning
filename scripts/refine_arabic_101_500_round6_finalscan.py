#!/usr/bin/env python3
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
FIELDS=re.compile(r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$')
SOURCE='- Arabic Language Academy in Cairo / formal MSA grammar - final 101-500 manual review (2026-08-13)'
REPAIRS={
159:('\u062b\u0627\u0646\u064a\u0629','second; a second (unit of time); feminine ordinal second','noun / ordinal adjective'),
187:('\u0633\u064a\u0627\u0633\u064a','politician; political figure; political','noun / adjective'),
257:('\u0645\u0627\u0632\u0627\u0644','still is or was; continues or continued to be','negative particle + defective verb (ma + zala), fixed continuative construction'),
393:('\u0623\u0648\u0636\u062d','clearer; clearest; clarified; explained; made clear','elative adjective / perfect-past verb'),
446:('\u0642\u0644\u0628','heart; core or center; turned; overturned; reversed','noun / perfect-past verb'),
475:('\u0645\u0634\u064a\u0631\u0627','indicating; pointing out; noting (mushiran)','active participle used adverbially/circumstantially'),
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
