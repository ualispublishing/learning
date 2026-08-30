#!/usr/bin/env python3
"""Remove one stale Arabic release blocker after current-corpus closure evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'reading'/'RELEASE_STATUS.json'
CLOSURE=ROOT/'reading'/'audit'/'arabic_b1_c2_metalinguistic_cefr_adjudication_2026-08-30.json'
STALE='corpus-wide low-level metalinguistic/CEFR audit and repair'
def main():
    c=json.loads(CLOSURE.read_text(encoding='utf-8'))
    if c.get('status')!='CURRENT_LOWLEVEL_METALINGUISTIC_CANDIDATE_CLASS_CLOSED' or c.get('postrepair_manual_review')!=0 or c.get('release_claim') is not False:
        raise SystemExit('Current-corpus metalinguistic closure evidence is not sufficient')
    d=json.loads(P.read_text(encoding='utf-8')); ar=d['languages']['arabic']
    if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False:
        raise SystemExit('Arabic release state drift; refusing bookkeeping cleanup')
    items=ar.get('open_release_classes',[])
    if items.count(STALE)!=1: raise SystemExit(f'Expected exactly one stale blocker, found {items.count(STALE)}')
    ar['open_release_classes']=[x for x in items if x!=STALE]
    d['updated']='2026-08-30'
    P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Removed stale Arabic metalinguistic blocker; release state remains REOPEN_REQUIRED.')
if __name__=='__main__':main()
