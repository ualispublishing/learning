#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
RANK_RE=re.compile(r'(?m)^Rank:\s*(\d+)\s*$')
POS_RE=re.compile(r'(?m)^Part of speech:\s*(.+?)\s*$')
MEAN_RE=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$')
SOURCE_LINE='- Arabic Language Academy in Cairo, Al-Mu’jam Al-Wasit / grammar recheck — second-pass educator review (2026-08-13)'

REPAIRS={
  15:{'front':'مع','pos':'noun functioning adverbially (اسم؛ ويكون ظرفًا عند الإضافة)'},
  21:{'front':'التي','pos':'relative pronoun (اسم موصول)'},
  27:{'front':'الذي','pos':'relative pronoun (اسم موصول)'},
  34:{'front':'هنا','pos':'demonstrative of place / adverbial deictic (اسم إشارة للمكان القريب)'},
  40:{'front':'هناك','pos':'demonstrative of place / adverbial deictic (اسم إشارة للمكان البعيد)'},
  56:{'front':'حتى','meaning':'until; up to; even; so that','pos':'particle / preposition / conjunction'},
  63:{'front':'قبل','meaning':'before; prior to; earlier','pos':'temporal/spatial adverbial noun (ظرف زمان أو مكان)'},
  72:{'front':'كيف','pos':'interrogative noun/adverbial (اسم استفهام مبني)'},
  78:{'front':'غير','pos':'noun / adjective / perfect / past verb (غَيْر / غَيَّر)'},
  94:{'front':'فعل','meaning':'act; action; verb (grammar); did; performed','pos':'noun / perfect / past verb (فِعْل / فَعَلَ)'},
}

def replace_field(back,rx,label,value):
    if not rx.search(back): raise SystemExit(f'missing {label}')
    return rx.sub(f'{label}: {value}',back,count=1)

def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    if len(rows)!=1000: raise SystemExit(f'expected 1000 rows, got {len(rows)}')
    changed=[]
    for rank,spec in REPAIRS.items():
        row=rows[rank-1]
        if row['Front']!=spec['front']: raise SystemExit(f'rank {rank}: expected {spec["front"]}, got {row["Front"]}')
        back=row['Back']; m=RANK_RE.search(back)
        if not m or int(m.group(1))!=rank: raise SystemExit(f'rank metadata mismatch at {rank}')
        old_pos=POS_RE.search(back).group(1).strip(); old_mean=MEAN_RE.search(back).group(1).strip()
        if 'meaning' in spec: back=replace_field(back,MEAN_RE,'Meaning',spec['meaning'])
        back=replace_field(back,POS_RE,'Part of speech',spec['pos'])
        if SOURCE_LINE not in back:
            back=back.rstrip()+"\n"+SOURCE_LINE
        row['Back']=back
        changed.append((rank,row['Front'],old_mean,spec.get('meaning',old_mean),old_pos,spec['pos']))
    with TARGET.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n'); w.writeheader(); w.writerows(rows)
    print('repaired',len(changed),'rows')
    for x in changed: print(x)

if __name__=='__main__': main()
