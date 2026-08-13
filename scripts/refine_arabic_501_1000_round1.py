#!/usr/bin/env python3
import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
FIELDS=re.compile(r'(?s)^\s*Rank:\s*(\d+)\s+Meaning:\s*(.*?)\s+Part of speech:\s*(.*?)\s+Sources:\s*(.*)\s*$')
SOURCE='- Arabic Language Academy in Cairo, Al-Mujam Al-Wasit - educator second-pass review (2026-08-13)'
REPAIRS={
505:('متى','when?; when/whenever (in conditional use)','temporal adverb (interrogative / conditional)'),
527:('خلف','behind; at the back of; rear/back; succeeded or followed; came after','adverbial noun / noun / perfect-past verb'),
562:('ولد','boy; son; gave birth; was born (depending on vocalization/voice)','noun / perfect-past verb'),
568:('أمين','trustworthy; honest; faithful; trustee/custodian; secretary or officer entrusted with a responsibility','adjective / noun'),
619:('مؤكدا','confirmed; certain; confirming/emphasizing (depending on vocalization)','active or passive participle used adjectivally/adverbially'),
634:('سوى','except; other than; apart from; other/alternative (depending on construction)','exceptive noun / adverbial nominal expression'),
644:('أشهر','months; more famous; most famous (depending on vocalization)','plural noun / elative adjective'),
645:('ملك','angel (مَلَك); king (مَلِك); ownership/possession or dominion/rule (مِلْك / مُلْك)','noun'),
646:('قضاء','judgment/ruling; judiciary; fulfillment/carrying out; spending or passing (time)','noun / verbal noun'),
650:('صعب','difficult; hard; was/became difficult','adjective / perfect-past verb'),
732:('يصدق','is truthful; proves true; believes; gives credence to; confirms/approves (depending on vocalization/form)','imperfect / present verb'),
767:('حي','neighborhood; district; living/alive (depending on vocalization)','noun / adjective'),
797:('صدر','chest; breast/front; was issued; was published; came from','noun / perfect-past verb'),
814:('شاب','young man; youth; young; mixed/adulterated (rare verb reading)','noun / adjective / perfect-past verb'),
845:('قلق','anxiety; concern; anxious/worried; became anxious/agitated','noun / adjective / perfect-past verb'),
873:('أوسط','middle; central; intermediate; moderate','adjective / elative'),
882:('قرب','nearness; proximity; approached; came near','noun / perfect-past verb'),
886:('مر','bitter (مُرّ); passed/went by (مَرَّ)','adjective / perfect-past verb'),
895:('سر','secret (سِرّ); go!/proceed! (سِرْ, imperative of سار)','noun / imperative verb'),
911:('حمل','pregnancy/gestation (حَمْل); load/burden (حِمْل); carrying; carried/bore (حَمَلَ)','noun / perfect-past verb'),
936:('شاهد','witness; evidence; watched; saw; witnessed','noun / perfect-past verb'),
943:('يقبل','accepts; agrees to; kisses; approaches/comes forward (depending on vocalization/form)','imperfect / present verb'),
967:('فصل','chapter; season; class/classroom; school term; separated; divided; dismissed','noun / perfect-past verb'),
972:('أسوأ','worse; worst','comparative / superlative adjective (elative)'),
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
