#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit';ARCH=AUDIT/'archive';ARCH.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'arabic_phrase_bank.csv';QUEUE=AUDIT/'arabic_phrase_naturalness_v2_queue.json'
def main():
    flagged=json.loads(QUEUE.read_text(encoding='utf-8'))
    remove={int(x['row']) for x in flagged}
    if len(remove)!=224: raise SystemExit(f'expected 224 residual generated/synthetic rows, got {len(remove)}')
    with SRC.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f);rows=list(r);fields=r.fieldnames
    kept=[];quar=[]
    for i,row in enumerate(rows,1):(quar if i in remove else kept).append(row)
    if len(kept)!=665 or len(quar)!=224:raise SystemExit((len(kept),len(quar)))
    out=ARCH/'arabic_phrase_bank_residual_generated_quarantine_2026-08-12.csv'
    with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(quar)
    with SRC.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(kept)
    summary={'pre_rows':len(rows),'quarantined_rows':len(quar),'live_rows':len(kept),'archive':str(out.relative_to(ROOT)),'policy':'Second independent front-naturalness pass: all 224 residual rows matching productive generated templates, stacked adjectival chains, or extreme front-length generation patterns were quarantined. Quality is prioritized over coverage.'}
    (AUDIT/'arabic_phrase_bank_residual_quarantine_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
