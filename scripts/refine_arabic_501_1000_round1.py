#!/usr/bin/env python3
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
FIELDS=re.compile(r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$')
SOURCE='- Al-Said (2023) Table 4 vocalization/POS recheck + educator second-pass review (2026-08-13)'
REPAIRS={
505:('متى','when?','interrogative particle'),
527:('خلف','succeeded/followed; came after','perfect / past verb'),
553:('فهم','understood','perfect / past verb'),
558:('سجن','prison; imprisonment','noun'),
562:('ولد','boy; son; gave birth','noun / perfect / past verb'),
568:('أمين','trustworthy; honest; faithful','adjective'),
619:('مؤكدا','confirmed; certain; confirming/emphasizing (context-dependent)','adjective / noun'),
634:('سوى','except; other than; apart from','exceptive / restrictive particle'),
644:('أشهر','months','noun'),
645:('ملك','angel (مَلَك)','noun'),
646:('قضاء','judgment / ruling; judiciary; fulfillment / carrying out','noun / verbal noun'),
650:('صعب','was difficult; became hard','perfect / past verb'),
732:('يصدق','is truthful; tells the truth; proves true','verb'),
767:('حي','neighborhood; district','noun'),
797:('صدر','was issued; was published; came from','perfect / past verb'),
814:('شاب','young man; youth; mixed/adulterated (rare verb reading)','noun / perfect / past verb'),
845:('قلق','anxiety; concern; became anxious/worried','noun / perfect / past verb'),
873:('أوسط','middle; central; intermediate (أوسط)','noun'),
882:('قرب','approached; came near','perfect / past verb'),
886:('مر','bitter (مُرّ); passed/went by (مَرَّ)','noun / perfect / past verb'),
895:('سر','secret','noun'),
911:('حمل','load; burden (حِمْل)','noun'),
936:('شاهد','watched; saw; witnessed','perfect / past verb'),
943:('يقبل','kisses; is kissing (يُقَبِّل)','verb'),
967:('فصل','separated; divided; dismissed','verb'),
972:('أسوأ','worse; worst','noun'),
}
def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    if len(rows)!=1000: raise SystemExit(f'expected 1000 rows, found {len(rows)}')
    for rank,(front,meaning,pos) in REPAIRS.items():
        row=rows[rank-1]
        if row['Front']!=front: raise SystemExit(f'rank {rank} front mismatch')
        m=FIELDS.match(row['Back'] or '')
        if not m or int(m.group(1))!=rank: raise SystemExit(f'rank {rank} metadata mismatch')
        sources=[x.rstrip() for x in m.group(4).strip().splitlines() if x.strip()]
        if SOURCE not in sources: sources.append(SOURCE)
        row['Back']=f'Rank: {rank}\n\nMeaning: {meaning}\n\nPart of speech: {pos}\n\nSources:\n'+"\n".join(sources)
    for i,row in enumerate(rows,1):
        m=FIELDS.match(row.get('Back') or '')
        if not (row.get('Front') or '').strip() or not m or int(m.group(1))!=i:
            raise SystemExit(f'global structural guard failed at row {i}')
    with TARGET.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n');w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
