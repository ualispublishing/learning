#!/usr/bin/env python3
"""Hard promotion gate for Arabic rank-1001..3000 v2 candidate."""
from __future__ import annotations
import csv,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
CAND=AUDIT/'arabic_top3000_candidate_v2.csv'; EVID=AUDIT/'arabic_top3000_continuation_evidence_v2.csv'
OUT=AUDIT/'arabic_top3000_v2_promotion_gate_summary.json'
DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]'); AR=re.compile(r'[\u0600-\u06ff]')
def norm(s):return DIAC.sub('',unicodedata.normalize('NFKC',s or '').replace('ـ','')).strip()
def meaning(back):
 m=re.search(r'(?m)^Meaning:\s*(.+?)\s*$',back or '');return m.group(1).strip() if m else ''
def main():
 with CAND.open(encoding='utf-8-sig',newline='') as f:c=list(csv.DictReader(f))
 with EVID.open(encoding='utf-8-sig',newline='') as f:e=list(csv.DictReader(f))
 with (ROOT/'arabic_top1000.csv').open(encoding='utf-8-sig',newline='') as f:top={norm(r.get('Front','')) for r in csv.DictReader(f)}
 problems=[]
 fronts=[norm(r.get('Front','')) for r in c]
 if len(c)!=2000:problems.append(f'candidate_rows={len(c)}')
 if len(e)!=2000:problems.append(f'evidence_rows={len(e)}')
 if len(set(fronts))!=2000:problems.append('duplicate_fronts')
 overlap=sorted(set(fronts)&top)
 if overlap:problems.append(f'top1000_overlap={len(overlap)}')
 if any(len(x)<2 for x in fronts):problems.append('single_character_front')
 if any(not AR.search(x) or re.search(r'[A-Za-z]',x) for x in fronts):problems.append('non_arabic_front')
 if any('arabic_word_' in (r.get('Front','')+r.get('Back','')) for r in c):problems.append('placeholder')
 ranks=[]
 for r in c:
  m=re.search(r'(?m)^Rank:\s*(\d+)\s*$',r.get('Back','') or '')
  ranks.append(int(m.group(1)) if m else -1)
 if ranks!=list(range(1001,3001)):problems.append('rank_sequence')
 if any(not meaning(r.get('Back','')) for r in c):problems.append('blank_meaning')
 if any((r.get('semantic_basis') or '')!='exact CALIMA sense fragment + Kaikki agreement' for r in e):problems.append('semantic_basis_not_cross_source')
 if any(norm(r.get('front',''))!=fronts[i] for i,r in enumerate(e)):problems.append('candidate_evidence_front_mismatch')
 # Regression pairs discovered in the rejected v1 candidate. The words may be
 # admitted only if the known wrong learner gloss no longer survives.
 forbidden={
  'أليس':{'valiant'},'خيار':{'good','better','best'},'تعزيز':{'praise','pride'},
  'بطاقة':{'energy','power','potential'},'تفعيل':{'scansion'},'مالك':{'money','capital','funds'},
  'كافي':{'kaf','arabic letter'},'سرطان':{'crayfish'},'بحرية':{'freedom'},'وقود':{'leaders','commanders'},
  'أكلة':{'halos','coronas'},'لبن':{'son'},'فلك':{'dent','notch','nick'},'روحي':{'alcoholic'}
 }
 regressions=[]
 for r in c:
  f=norm(r.get('Front',''));m=meaning(r.get('Back','')).lower()
  if f in forbidden and any(bad in m for bad in forbidden[f]):regressions.append({'front':f,'meaning':m})
 if regressions:problems.append(f'known_bad_sense_regressions={len(regressions)}')
 summary={'rows':len(c),'evidence_rows':len(e),'distinct_fronts':len(set(fronts)),'top1000_overlap_rows':len(overlap),'rank_range':[min(ranks),max(ranks)] if ranks else [],'known_bad_sense_regressions':regressions,'problems':problems,'promotion_gate':'PASS' if not problems else 'FAIL','policy':'2000 unique Arabic-script continuation cards, no top1000 overlap/placeholders, exact CALIMA+Kaikki semantic basis for every row, and hard regression checks for previously observed bad senses.'}
 OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
 if problems:raise SystemExit('Arabic v2 promotion gate failed')
if __name__=='__main__':main()
