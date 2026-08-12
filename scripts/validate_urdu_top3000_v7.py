#!/usr/bin/env python3
"""Hard promotion gate for the final Urdu rank-1001..3000 candidate."""
from __future__ import annotations
import csv,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
CAND=AUDIT/'urdu_top3000_candidate_v7.csv'; EVID=AUDIT/'urdu_top3000_continuation_evidence_v7.csv'
OUT=AUDIT/'urdu_top3000_v7_promotion_gate_summary.json'
URDU=re.compile(r'[\u0600-\u06ff]'); DEV=re.compile(r'[\u0900-\u097f]'); LATIN=re.compile(r'[A-Za-z]')
RANK=re.compile(r'(?m)^Rank:\s*(\d+)\s*$'); MEANING=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$')
PLACEHOLDER=re.compile(r'urdu_word_\d+|placeholder',re.I)
def norm(s): return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s or '')).strip()
def main():
    with CAND.open(encoding='utf-8-sig',newline='') as f:c=list(csv.DictReader(f))
    with EVID.open(encoding='utf-8-sig',newline='') as f:e=list(csv.DictReader(f))
    with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:top={norm(r.get('Front','')) for r in csv.DictReader(f)}
    problems=[]; fronts=[norm(r.get('Front','')) for r in c]
    if len(c)!=2000: problems.append(f'candidate_rows={len(c)}')
    if len(e)!=2000: problems.append(f'evidence_rows={len(e)}')
    if len(fronts)!=len(set(fronts)): problems.append('duplicate_fronts')
    overlap=sorted(set(fronts)&top)
    if overlap: problems.append(f'top1000_overlap={len(overlap)}')
    if any(not f or not URDU.search(f) or DEV.search(f) or LATIN.search(f) for f in fronts): problems.append('invalid_front_script')
    if any(PLACEHOLDER.search((r.get('Front','') or '')+' '+(r.get('Back','') or '')) for r in c): problems.append('placeholder_marker')
    ranks=[]; blank_meanings=0; devanagari_meanings=0
    for r in c:
        m=RANK.search(r.get('Back','') or ''); ranks.append(int(m.group(1)) if m else -1)
        mm=MEANING.search(r.get('Back','') or '')
        if not mm or not mm.group(1).strip(): blank_meanings+=1
        elif DEV.search(mm.group(1)): devanagari_meanings+=1
    if ranks!=list(range(1001,3001)): problems.append('rank_sequence_not_1001_3000')
    if blank_meanings: problems.append(f'blank_meanings={blank_meanings}')
    if devanagari_meanings: problems.append(f'devanagari_meanings={devanagari_meanings}')
    if len(e)==len(c):
        mismatches=sum(norm(r.get('front',''))!=fronts[i] for i,r in enumerate(e))
        if mismatches: problems.append(f'candidate_evidence_front_mismatch={mismatches}')
    tierA=tierB=supp=bad_tier=bad_supp=0
    for r in e:
        tier=r.get('evidence_tier',''); src=r.get('frequency_source',''); ids=(r.get('iwn_en_english_ids') or '').strip(); basis=r.get('semantic_basis','')
        try:dcount=int(r.get('iwn_en_direct_sense_count') or 0); selector=int(r.get('external_selector_score') or 0)
        except ValueError:dcount=selector=-1
        if tier=='A_direct_iwn_en':
            tierA+=1
            if not ids or dcount<1 or 'IWN-En Direct' not in basis: bad_tier+=1
        elif tier=='B_two_source_fallback':
            tierB+=1
            if ids or str(r.get('indowordnet_lemma','')).lower() not in {'true','1'} or selector<2 or 'agreement' not in basis.lower(): bad_tier+=1
        else: bad_tier+=1
        if src.startswith('wordfreq'):
            supp+=1
            if tier!='A_direct_iwn_en' or not ids or dcount<1: bad_supp+=1
    if bad_tier: problems.append(f'evidence_tier_violations={bad_tier}')
    if bad_supp: problems.append(f'supplemental_non_direct_rows={bad_supp}')
    summary={'rows':len(c),'evidence_rows':len(e),'distinct_fronts':len(set(fronts)),'top1000_overlap_rows':len(overlap),'rank_range':[min(ranks),max(ranks)] if ranks else [],'tier_A_direct_rows':tierA,'tier_B_two_source_fallback_rows':tierB,'supplemental_wordfreq_rows':supp,'evidence_tier_violations':bad_tier,'supplemental_non_direct_rows':bad_supp,'problems':problems,'promotion_gate':'PASS' if not problems else 'FAIL','policy':'2000 unique Urdu-script continuation cards; no top1000 overlap/placeholders; Tier A requires CFILT IWN-En Direct IDs; Tier B requires IndoWordNet lemma plus two-source agreement; every wordfreq supplemental row must be Tier A Direct.'}
    OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(summary,ensure_ascii=False,indent=2))
    if problems: raise SystemExit('Urdu v7 promotion gate failed')
if __name__=='__main__': main()
