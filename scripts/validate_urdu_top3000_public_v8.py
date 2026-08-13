#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
AR=re.compile(r'[\u0600-\u06ff]'); DEV=re.compile(r'[\u0900-\u097f]'); RANK=re.compile(r'(?m)^Rank:\s*(\d+)\s*$')
DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')
def norm(s):
 s=unicodedata.normalize('NFKC',s or '').replace('ـ',''); s=DIAC.sub('',s); return re.sub(r'\s+',' ',s).strip().casefold()
def load(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 cand=load(AUDIT/'urdu_top3000_public_candidate_v8.csv'); ev=load(AUDIT/'urdu_top3000_public_evidence_v8.csv'); top=load(ROOT/'urdu_top1000.csv')
 problems=[]
 if len(cand)!=2000: problems.append(f'candidate_rows={len(cand)}')
 if len(ev)!=2000: problems.append(f'evidence_rows={len(ev)}')
 fronts=[norm(r.get('Front','')) for r in cand]
 if len(set(fronts))!=2000: problems.append('duplicate_fronts')
 if {norm(r['Front']) for r in top}&set(fronts): problems.append('top1000_overlap')
 ranks=[]
 for r in cand:
  m=RANK.search(r.get('Back','')); ranks.append(int(m.group(1)) if m else -1)
 if ranks!=list(range(1001,3001)): problems.append('rank_sequence')
 if any(not AR.search(r.get('Front','')) or DEV.search(r.get('Front','')) or re.search(r'[A-Za-z]',r.get('Front','')) for r in cand): problems.append('script_violation')
 if any(re.search(r'placeholder|urdu_word_\d+',r.get('Front','')+' '+r.get('Back',''),re.I) for r in cand): problems.append('placeholder')
 evidence_by_front={norm(r['front']):r for r in ev}
 tier_viol=[]; wide=[]
 for r in cand:
  e=evidence_by_front.get(norm(r['Front']))
  if not e: tier_viol.append((r['Front'],'missing_evidence')); continue
  tier=e.get('evidence_tier',''); src=e.get('frequency_source',''); ids=e.get('iwn_en_english_ids','')
  try: score=int(e.get('external_selector_score') or 0)
  except: score=0
  if tier=='A_direct_corroborated':
   if not ids or score<1: tier_viol.append((r['Front'],'bad_tier_A'))
  elif tier=='B_two_source_fallback':
   basis=e.get('semantic_basis','').lower()
   if 'indowordnet' not in basis or 'agreement' not in basis or score<2: tier_viol.append((r['Front'],'bad_tier_B'))
  else: tier_viol.append((r['Front'],'unknown_tier'))
  if src.startswith('wordfreq') and tier!='A_direct_corroborated': tier_viol.append((r['Front'],'supplemental_not_tier_A'))
  parts=[x.strip() for x in (e.get('meaning') or '').split(';') if x.strip()]
  if len(parts)>3: wide.append((r['Front'],parts))
 if tier_viol: problems.append(f'evidence_tier_violations={len(tier_viol)}')
 if wide: problems.append(f'overbundled_meanings={len(wide)}')
 # Known regressions from v7 publication audit. Omission is acceptable; inclusion must be clean.
 regressions=[]
 checks={
  'تحت':({'under','beneath','below'},{'claim','combined'}),
  'نمائندہ':({'representative','delegate','agent'},{'decay'}),
  'سردار':({'chief','leader','head'},{'usurer','god'}),
 }
 for word,(good,bad) in checks.items():
  e=evidence_by_front.get(norm(word))
  if not e: continue
  m=(e.get('meaning') or '').casefold()
  if not any(g in m for g in good) or any(x in m for x in bad): regressions.append({'front':word,'meaning':e.get('meaning')})
 if regressions: problems.append(f'known_bad_gloss_regressions={len(regressions)}')
 report={'rows':len(cand),'evidence_rows':len(ev),'distinct_fronts':len(set(fronts)),'top1000_overlap_rows':len({norm(r['Front']) for r in top}&set(fronts)),'rank_range':[min(ranks),max(ranks)] if ranks else [],'tier_A_direct_corroborated_rows':sum(r.get('evidence_tier')=='A_direct_corroborated' for r in ev),'tier_B_two_source_fallback_rows':sum(r.get('evidence_tier')=='B_two_source_fallback' for r in ev),'wordfreq_supplemental_rows':sum((r.get('frequency_source') or '').startswith('wordfreq') for r in ev),'evidence_tier_violations':tier_viol[:20],'overbundled_meanings':wide[:20],'known_bad_gloss_regressions':regressions,'problems':problems,'promotion_gate':'PASS' if not problems else 'FAIL','policy':'Publication gate: every Direct sense independently corroborated; ambiguous Direct senses uniquely selected; learner gloss max three senses; Tier B requires IndoWordNet plus two-source agreement; all supplemental rows must be corroborated Tier A Direct.'}
 (AUDIT/'urdu_top3000_public_v8_promotion_gate_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if problems: raise SystemExit('Urdu public v8 promotion gate failed')
if __name__=='__main__':main()
