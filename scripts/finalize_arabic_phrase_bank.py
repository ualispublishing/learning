#!/usr/bin/env python3
"""Finalize the Arabic phrase bank by removing every unresolved clean-audit row.

This is intentionally conservative: any card still flagged by the fresh MSA
morphology audit is excluded rather than manually waived through. The output is
therefore the intersection of the quality-first cleaned candidate and the rows
that cleared the audit without review flags.
"""
from __future__ import annotations
import csv, json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
SRC=AUDIT/'arabic_phrase_bank_clean_candidate.csv'
QUEUE=AUDIT/'arabic_phrase_bank_clean_review_queue.csv'
OUT=AUDIT/'arabic_phrase_bank_final_candidate.csv'
SUMMARY=AUDIT/'arabic_phrase_bank_final_candidate_summary.json'
DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')
def norm(s:str)->str:
 s=unicodedata.normalize('NFKC',s or '').replace('ـ','')
 s=DIAC.sub('',s)
 return re.sub(r'\s+',' ',s).strip()
def main():
 with SRC.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 with QUEUE.open(encoding='utf-8-sig',newline='') as f:q=list(csv.DictReader(f))
 blocked={norm(r.get('front','')) for r in q if norm(r.get('front',''))}
 kept=[r for r in rows if norm(r.get('Front','')) not in blocked]
 fronts=[norm(r.get('Front','')) for r in kept]
 problems=[]
 if len(fronts)!=len(set(fronts)):problems.append('normalized_duplicate_fronts')
 if any(not x for x in fronts):problems.append('blank_front')
 if any(re.search(r'[A-Za-z]',r.get('Front','')) for r in kept):problems.append('latin_in_front')
 if any('الجيال' in norm(r.get('Front','')) for r in kept):problems.append('known_ajyal_typo')
 synthetic=('thronely','absolute ultimate maximum','maximum possible human way','heptacosi','hexacosi','enneadeca-emphatic')
 if any(any(x in (r.get('Back','') or '').lower() for x in synthetic) for r in kept):problems.append('known_synthetic_marker')
 with OUT.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader();w.writerows(kept)
 summary={'source_clean_rows':len(rows),'unresolved_rows_removed':len(rows)-len(kept),'final_candidate_rows':len(kept),'distinct_normalized_fronts':len(set(fronts)),'problems':problems,'gate':'PASS' if not problems and len(kept)>0 else 'FAIL','policy':'Every row still requiring explicit review in the clean MSA audit is excluded; no unresolved card is promoted.'}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
 if summary['gate']!='PASS':raise SystemExit('final phrase candidate gate failed')
if __name__=='__main__':main()
