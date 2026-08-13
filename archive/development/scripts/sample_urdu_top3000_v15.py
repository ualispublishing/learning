#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'audit/urdu_top3000_continuation_evidence_v15.csv';OUT=ROOT/'audit/urdu_top3000_v15_stratified_sample.json'

def main():
    if not P.exists():raise SystemExit('v15 evidence missing')
    with P.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    windows=[]
    for start in (0,480,980,1480,max(0,len(rows)-40)):
        for i in range(start,min(start+40,len(rows))):
            r=rows[i];windows.append({'row_index':i+1,'rank':r.get('rank'),'front':r.get('front'),'meaning':r.get('meaning'),'semantic_support':r.get('semantic_support'),'kaikki':(r.get('kaikki_meaning') or '')[:220],'readurdu':(r.get('readurdu_meaning') or '')[:220],'opensubtitles':(r.get('opensubtitles_word2word') or '')[:180],'opus_independent':(r.get('opus_independent_word2word') or '')[:180]})
    # De-duplicate overlapping windows while preserving order.
    seen=set();sample=[]
    for x in windows:
        if x['row_index'] not in seen:seen.add(x['row_index']);sample.append(x)
    risk_words=['کرتا','پولیس','مطابق','اعلان','کورٹ','پیج','گن','والی','سرخ','کرن','امریکہ','لشکر','تجدید','جاسوسی','فوائد','پیدل']
    lookup={r.get('front'):r for r in rows};reg=[]
    for w in risk_words:
        r=lookup.get(w)
        reg.append({'front':w,'present':bool(r),'rank':r.get('rank') if r else None,'meaning':r.get('meaning') if r else None,'support':r.get('semantic_support') if r else None,'opus_independent':(r.get('opus_independent_word2word') or '')[:180] if r else None})
    out={'rows':len(rows),'stratified_sample':sample,'known_risk_words':reg}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'rows':len(rows),'sample_rows':len(sample),'risk_words':reg},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
