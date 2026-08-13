#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
FIELDS=re.compile(r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$')
SOURCE='- Second-pass educator grammar review: Arabic Language Academy in Cairo / formal MSA grammar (2026-08-13)'
REPAIRS={
106:{'front':'أين','pos':'interrogative/conditional place adverb (ظرف مكان)'},
116:{'front':'أفضل','pos':'elative / comparative-superlative (اسم تفضيل)'},
130:{'front':'خاصة','pos':'adjective; adverbial expression in the sense “especially”'},
142:{'front':'حقا','pos':'noun / verbal-noun form used adverbially (“really; truly”)'},
160:{'front':'الذين','pos':'relative pronoun (اسم موصول)'},
161:{'front':'كلا','pos':'particle (كَلَّا “no/certainly not”) / dual noun-pronominal form (كِلَا “both”)'},
195:{'front':'عربية','pos':'adjective / noun'},
261:{'front':'فني','pos':'noun / adjective'},
263:{'front':'عامة','pos':'adjective; adverbial expression in “in general”'},
271:{'front':'منتخب','pos':'noun / adjective / passive participle'},
291:{'front':'أقل','pos':'elative / comparative-superlative (اسم تفضيل)'},
338:{'front':'إطلاقا','pos':'verbal noun / adverbial expression'},
339:{'front':'تماما','pos':'verbal noun / adverbial expression'},
355:{'front':'دقيقة','pos':'noun / adjective'},
373:{'front':'خصوصا','pos':'verbal noun / adverbial expression'},
422:{'front':'واقع','pos':'noun / adjective / active participle'},
431:{'front':'عربي','pos':'noun / adjective'},
455:{'front':'خارجية','pos':'noun / adjective'},
467:{'front':'دوري','pos':'noun / adjective'},
}
def parse(back):
    m=FIELDS.match(back or '')
    if not m: raise SystemExit('cannot parse card fields')
    rank,meaning,pos,sources=m.groups()
    return int(rank),meaning.strip(),pos.strip(),sources.strip()
def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    changed=[]
    for rank,spec in REPAIRS.items():
        row=rows[rank-1]
        if row['Front']!=spec['front']: raise SystemExit(f'rank {rank} front mismatch: {row["Front"]}')
        card_rank,meaning,oldpos,sources=parse(row['Back'])
        if card_rank!=rank: raise SystemExit(f'rank {rank} metadata mismatch')
        lines=[x.rstrip() for x in sources.splitlines() if x.strip()]
        if SOURCE not in lines: lines.append(SOURCE)
        row['Back']=f'Rank: {rank}\n\nMeaning: {meaning}\n\nPart of speech: {spec["pos"]}\n\nSources:\n'+"\n".join(lines)
        changed.append((rank,row['Front'],oldpos,spec['pos']))
    with TARGET.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n');w.writeheader();w.writerows(rows)
    print('refined',len(changed),'POS labels')
    for item in changed: print(item)
if __name__=='__main__': main()
