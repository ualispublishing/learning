#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'; ARCH=AUDIT/'archive'; ARCH.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'arabic_phrase_bank.csv'
REVIEW=AUDIT/'public_review_arabic_phrase_bank.json'

def main():
    flagged=json.loads(REVIEW.read_text(encoding='utf-8'))
    remove={int(x['row']) for x in flagged if 'generated_phrase_wording_fingerprint' in x.get('flags',[])}
    if len(remove)!=189: raise SystemExit(f'expected 189 generated-family rows, got {len(remove)}')
    with SRC.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f); rows=list(r); fields=r.fieldnames
    kept=[]; quarantined=[]
    for i,row in enumerate(rows,1):
        (quarantined if i in remove else kept).append(row)
    if len(kept)!=889 or len(quarantined)!=189: raise SystemExit((len(kept),len(quarantined)))
    with (ARCH/'arabic_phrase_bank_generated_family_quarantine_2026-08-12.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(quarantined)
    with SRC.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(kept)
    summary={
      'pre_rows':len(rows),'quarantined_generated_family_rows':len(quarantined),'live_rows':len(kept),
      'policy':'Quality-first publication pass: all rows identified as belonging to generated phrase families are quarantined, including individually plausible members, so no synthetic family tail remains in the public deck.',
      'archive':'audit/archive/arabic_phrase_bank_generated_family_quarantine_2026-08-12.csv'}
    (AUDIT/'arabic_phrase_bank_public_quarantine_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
