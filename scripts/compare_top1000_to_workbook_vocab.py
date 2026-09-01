#!/usr/bin/env python3
"""Compare original root top-1000 flashcards to audited LANG-WB vocabulary companions."""
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MR=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$')
for lang in ('arabic','french','urdu'):
    with (ROOT/f'{lang}_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
        old=list(csv.DictReader(f))
    with (ROOT/f'completed/languages/workbooks/v1.0/{lang}/{lang}_vocabulary_1000.csv').open(encoding='utf-8-sig',newline='') as f:
        wb=list(csv.DictReader(f))
    assert len(old)==len(wb)==1000
    target_diff=[]; meaning_diff=[]
    for i,(a,b) in enumerate(zip(old,wb),1):
        m=MR.search(a.get('Back') or '')
        om=m.group(1).strip() if m else ''
        if (a.get('Front') or '').strip() != (b.get('target') or '').strip():
            target_diff.append({'rank':i,'root':a.get('Front'),'workbook':b.get('target')})
        if om != (b.get('english') or '').strip():
            meaning_diff.append({'rank':i,'target':a.get('Front'),'root':om,'workbook':b.get('english')})
    print(json.dumps({'language':lang,'rows':1000,'target_differences':len(target_diff),'meaning_differences':len(meaning_diff),'target_examples':target_diff[:10],'meaning_examples':meaning_diff[:10]},ensure_ascii=False))
