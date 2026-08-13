#!/usr/bin/env python3
"""Targeted final example-sentence corrections found during manual public-readiness review."""
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'arabic_phrase_bank.csv';AUDIT=ROOT/'audit'
REPLACEMENTS={
    'الكُلُّ جَاءُوا بِمَا فِي ذَلِكَ أَحْمَدُ.':'جَاءَ الجَمِيعُ، بِمَا فِي ذَلِكَ أَحْمَدُ.',
}
def main():
    with P.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);rows=list(r);fields=r.fieldnames
    changes=[]
    for i,row in enumerate(rows,1):
        old=row['Back'];new=old
        for a,b in REPLACEMENTS.items():new=new.replace(a,b)
        if new!=old:
            row['Back']=new;changes.append({'row':i,'front':row.get('Front',''),'change':'subject-verb agreement / idiomatic MSA example'})
    with P.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    out={'rows':len(rows),'changes':changes,'changed_rows':len(changes),'policy':'Targeted manual corrections only; no broad automatic grammar rewriting.'}
    (AUDIT/'arabic_phrase_example_polish_summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
