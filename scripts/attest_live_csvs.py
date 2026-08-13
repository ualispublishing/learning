#!/usr/bin/env python3
"""Repository-wide integrity attestation for live learner CSVs.

Checks learner-facing root CSVs for schema, row counts, placeholders, rank ranges,
cross-deck overlap, and duplicate cards. Identical surface forms are not treated
as duplicate-card errors when every occurrence explicitly has a different learner
Meaning AND a different Part of speech; those are recorded as intentional
homographs instead. This matters for forms such as Arabic ما, which legitimately
serves multiple grammatical functions.
"""
from __future__ import annotations
import csv, hashlib, json, re, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
FILES={'arabic_top1000.csv':1000,'arabic_top3000.csv':2000,'french_top1000.csv':1000,'french_top3000.csv':2000,'urdu_top1000.csv':1000,'urdu_top3000.csv':2000,'arabic_phrase_bank.csv':665}
DIAC_AR=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')
RANK=re.compile(r'(?m)^Rank:\s*(\d+)\s*$'); ARABIC=re.compile(r'[\u0600-\u06ff]')
PLACEHOLDER=re.compile(r'(?:arabic|french|urdu)_word_\d+|placeholder',re.I)
MEANING=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$'); POS=re.compile(r'(?m)^Part of speech:\s*(.+?)\s*$')

def norm(s:str)->str:
 s=unicodedata.normalize('NFKC',s or '').replace('ـ',''); s=DIAC_AR.sub('',s)
 return re.sub(r'\s+',' ',s).strip().casefold()
def load(name):
 p=ROOT/name; raw=p.read_bytes()
 with p.open(encoding='utf-8-sig',newline='') as f: reader=csv.DictReader(f); rows=list(reader); headers=reader.fieldnames or []
 return raw,headers,rows
def field(rx,back):
 m=rx.search(back or ''); return re.sub(r'\s+',' ',m.group(1)).strip().casefold() if m else ''
def duplicate_groups(rows):
 groups=defaultdict(list)
 for i,r in enumerate(rows,1):
  groups[norm(r.get('Front',''))].append({'row':i,'front':r.get('Front',''),'meaning':field(MEANING,r.get('Back','')),'part_of_speech':field(POS,r.get('Back','')),'back_preview':(r.get('Back','') or '')[:240].replace('\n',' | ')})
 return [{'normalized_front':k,'rows':v} for k,v in groups.items() if k and len(v)>1]
def intentional_homograph(group):
 rows=group['rows']; meanings=[r['meaning'] for r in rows]; poses=[r['part_of_speech'] for r in rows]
 return all(meanings) and all(poses) and len(set(meanings))==len(rows) and len(set(poses))==len(rows)

def main():
 report={'files':{},'cross_file_checks':{},'problems':[]}; loaded={}
 for name,expected in FILES.items():
  raw,headers,rows=load(name); loaded[name]=rows; fronts=[norm(r.get('Front','')) for r in rows]
  all_dups=duplicate_groups(rows); homographs=[g for g in all_dups if intentional_homograph(g)]; blocking=[g for g in all_dups if not intentional_homograph(g)]; problems=[]
  if headers!=['Front','Back']: problems.append(f'headers={headers!r}')
  if len(rows)!=expected: problems.append(f'rows={len(rows)} expected={expected}')
  if any(not f for f in fronts): problems.append('blank_front')
  if blocking: problems.append(f'blocking_duplicate_groups={len(blocking)}')
  if any(not (r.get('Back') or '').strip() for r in rows): problems.append('blank_back')
  if any(PLACEHOLDER.search((r.get('Front') or '')+' '+(r.get('Back') or '')) for r in rows): problems.append('placeholder_marker')
  if name.startswith(('arabic_','urdu_')) and any(not ARABIC.search(r.get('Front','') or '') for r in rows): problems.append('non_arabic_script_front')
  rank_range=None
  if name.endswith('_top3000.csv'):
   ranks=[]
   for r in rows:
    m=RANK.search(r.get('Back') or ''); ranks.append(int(m.group(1)) if m else -1)
   if ranks!=list(range(1001,3001)): problems.append('rank_sequence_not_1001_3000')
   if ranks: rank_range=[min(ranks),max(ranks)]
  report['files'][name]={'rows':len(rows),'expected_rows':expected,'headers':headers,'distinct_normalized_fronts':len(set(fronts)),'intentional_homograph_groups':homographs,'blocking_duplicate_groups':blocking,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'rank_range':rank_range,'problems':problems,'gate':'PASS' if not problems else 'FAIL'}
  report['problems'].extend(f'{name}: {p}' for p in problems); loaded[name]=rows
 for lang in ('arabic','french','urdu'):
  top={norm(r.get('Front','')) for r in loaded[f'{lang}_top1000.csv']}; cont={norm(r.get('Front','')) for r in loaded[f'{lang}_top3000.csv']}; overlap=sorted(top&cont)
  report['cross_file_checks'][f'{lang}_top1000_vs_1001_3000']={'overlap_rows':len(overlap),'sample':overlap[:20],'gate':'PASS' if not overlap else 'FAIL'}
  if overlap: report['problems'].append(f'{lang}: top1000/continuation overlap={len(overlap)}')
 report['overall_gate']='PASS' if not report['problems'] else 'FAIL'
 report['scope']='Learner-facing root CSVs only; legitimate same-surface/different-meaning-and-POS homographs are recorded but are not duplicate-card failures.'
 (AUDIT/'live_csv_attestation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if report['overall_gate']!='PASS': raise SystemExit('live CSV attestation failed')
if __name__=='__main__': main()

# 2026-08-13: refresh attestation after Arabic 501-1000 educator refinements.
