#!/usr/bin/env python3
"""Promote a fully gated rank-1001..3000 candidate over a placeholder deck."""
from __future__ import annotations
import argparse,csv,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'; ARCH=ROOT/'archive'/'legacy_language_decks'
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--language',choices=['arabic','french','urdu'],required=True); a=ap.parse_args(); lang=a.language
 sp=AUDIT/f'{lang}_top3000_audit_summary.json'; s=json.loads(sp.read_text(encoding='utf-8'))
 if s.get('promotion_gate')!='PASS' or s.get('review_rows')!=0 or s.get('blocking_problems')!=0: raise SystemExit(f'{lang}: audit gate not PASS: {s}')
 cand=AUDIT/f'{lang}_top3000_candidate.csv'; target=ROOT/f'{lang}_top3000.csv'
 with cand.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 if len(rows)!=2000: raise SystemExit(f'{lang}: candidate rows {len(rows)} != 2000')
 ranks=[]; fronts=[]
 import re
 rr=re.compile(r'(?m)^Rank:\s*(\d+)\s*$')
 for r in rows:
  fronts.append((r.get('Front') or '').strip()); m=rr.search(r.get('Back') or ''); ranks.append(int(m.group(1)) if m else -1)
 if ranks!=list(range(1001,3001)): raise SystemExit(f'{lang}: rank sequence invalid')
 if len(set(fronts))!=2000: raise SystemExit(f'{lang}: duplicate candidate fronts')
 ARCH.mkdir(parents=True,exist_ok=True); archive=ARCH/f'{lang}_top3000_placeholder_2026-08-12.csv'
 if target.exists() and not archive.exists(): shutil.copy2(target,archive)
 with target.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
  for r in rows:
   back=(r.get('Back') or '').replace('Continuation candidate; requires independent verification before promotion','Verified continuation; passed structural, corpus, lexical, and semantic review gates')
   w.writerow({'Front':r.get('Front',''),'Back':back})
 print(json.dumps({'language':lang,'promoted_rows':len(rows),'rank_range':[1001,3000],'archived_previous':str(archive.relative_to(ROOT))},ensure_ascii=False))
if __name__=='__main__':main()
