#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
RANK_RE=re.compile(r'(?m)^Rank:\s*(\d+)\s*$')
POS_RE=re.compile(r'(?m)^Part of speech:\s*(.+?)\s*$')
MEAN_RE=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$')
SOURCE='- Arabic Language Academy in Cairo / Quranic Arabic Corpus — second-pass educator review (2026-08-13)'
REPAIRS={
109:{'front':'هيا','meaning':'come on!; let’s go!','pos':'exhortative particle / expression (كلمة حثّ)'},
151:{'front':'جانب','meaning':'side; aspect; flank','pos':'noun'},
189:{'front':'قدم','meaning':'foot; antiquity/oldness; presented/offered (depending on vocalization/form)','pos':'noun / perfect-past verb'},
194:{'front':'لذا','meaning':'therefore; thus; for that reason','pos':'prepositional/adverbial expression (لِ + ذا)'},
221:{'front':'هم','meaning':'they; concern; worry (هُمْ / هَمّ)','pos':'personal pronoun / noun'},
231:{'front':'كم','meaning':'how many?; how much?; many/a great many (interrogative or declarative كَمْ)','pos':'quantitative noun; interrogative or declarative (اسم مبني)'},
234:{'front':'حسب','meaning':'according to; enough/sufficient; calculated/count(ed); considered/thought (depending on vocalization/use)','pos':'noun / adverbial-relational expression / perfect-past verb'},
243:{'front':'يعد','meaning':'counts/enumerates; prepares; is considered (يَعُدّ / يُعِدّ / يُعَدّ)','pos':'imperfect verb; active or passive depending on vocalization'},
248:{'front':'فقد','meaning':'lost; loss/absence; so/then + already/may (فَقَدَ / فَقْد / فَ + قَدْ)','pos':'perfect-past verb / noun / conjunction + particle sequence'},
250:{'front':'ألف','meaning':'thousand; authored/composed/compiled (أَلْف / أَلَّفَ)','pos':'numeral/noun / perfect-past verb'},
320:{'front':'حسن','meaning':'good; fine; goodness; beauty; became good/beautiful (حَسَن / حُسْن / حَسُنَ)','pos':'adjective / noun / perfect-past verb'},
354:{'front':'عقد','meaning':'contract; agreement; decade; necklace; held/concluded/tied (عَقْد / عِقْد / عَقَدَ)','pos':'noun / perfect-past verb'},
494:{'front':'شعر','meaning':'poetry; hair; felt/perceived (شِعْر / شَعْر / شَعَرَ)','pos':'noun / perfect-past verb'},
}
def repl(back,rx,label,value):
    if not rx.search(back): raise SystemExit(f'missing {label}')
    return rx.sub(f'{label}: {value}',back,count=1)
def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    if len(rows)!=1000: raise SystemExit(f'expected 1000 rows, got {len(rows)}')
    changed=[]
    for rank,spec in REPAIRS.items():
        row=rows[rank-1]
        if row['Front']!=spec['front']: raise SystemExit(f'rank {rank} front mismatch')
        back=row['Back']; m=RANK_RE.search(back)
        if not m or int(m.group(1))!=rank: raise SystemExit(f'rank {rank} metadata mismatch')
        oldm=MEAN_RE.search(back).group(1).strip(); oldp=POS_RE.search(back).group(1).strip()
        back=repl(back,MEAN_RE,'Meaning',spec['meaning'])
        back=repl(back,POS_RE,'Part of speech',spec['pos'])
        if SOURCE not in back: back=back.rstrip()+'\n'+SOURCE
        row['Back']=back; changed.append((rank,row['Front'],oldm,spec['meaning'],oldp,spec['pos']))
    with TARGET.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n'); w.writeheader(); w.writerows(rows)
    print('repaired',len(changed),'rows')
    for item in changed: print(item)
if __name__=='__main__': main()
