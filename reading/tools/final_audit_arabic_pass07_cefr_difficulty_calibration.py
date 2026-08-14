#!/usr/bin/env python3
"""Final Arabic review pass 07: CEFR/difficulty calibration diagnostics.

Uses explicit planning bands from docs/READING_PASSAGE_STANDARD.md. Bands are
calibration targets, not single-factor CEFR proofs; deviations are review flags.
"""
from __future__ import annotations
import json,statistics,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass07_cefr_difficulty_calibration.json'
BANDS={
'a1':{'standard':(90,140),'extended':(160,220),'new_max':3},
'a2':{'standard':(140,220),'extended':(250,350),'new_max':4},
'b1':{'standard':(220,350),'extended':(400,550),'new_max':6},
'b2':{'standard':(350,550),'extended':(600,900),'new_max':8},
'c1':{'standard':(500,800),'extended':(900,1400),'new_max':10},
'c2':{'standard':(700,1200),'extended':(1300,2200),'new_max':14},
}
TOKEN=re.compile(r'\S+')
def add(flags,code,**kw):flags.append({'code':code,**kw})
def zone(n,b):
    lo,hi=b['standard'];elo,ehi=b['extended']
    if lo<=n<=hi:return 'standard'
    if elo<=n<=ehi:return 'extended'
    if n<lo:return 'below_standard_min'
    if hi<n<elo:return 'between_standard_and_extended'
    return 'above_extended_max'
def main():
    flags=[];summary={};means=[]
    for level in LEVELS:
        rows=[json.loads(x) for x in (ROOT/f'reading/arabic/{level}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
        wc=[];actual_wc=[];new_counts=[];zones=Counter();coverage=Counter();flagged=set();count_mismatch=0;over_new=0
        for r in rows:
            pid=r['id'];stored=int(r.get('word_count',0) or 0);actual=len(TOKEN.findall(str(r.get('text',''))));wc.append(stored);actual_wc.append(actual)
            z=zone(stored,BANDS[level]);zones[z]+=1
            if z in {'below_standard_min','above_extended_max'}:
                add(flags,'length_outside_calibration_bands',level=level,passage_id=pid,word_count=stored,zone=z,standard=BANDS[level]['standard'],extended=BANDS[level]['extended']);flagged.add(pid)
            if abs(stored-actual)>2:
                count_mismatch+=1;add(flags,'stored_word_count_differs_from_whitespace_count',level=level,passage_id=pid,stored=stored,whitespace_count=actual);flagged.add(pid)
            nc=len(r.get('new_lexical_targets',[]) if isinstance(r.get('new_lexical_targets'),list) else []);new_counts.append(nc)
            if nc>BANDS[level]['new_max']:
                over_new+=1;add(flags,'new_target_load_above_planning_max',level=level,passage_id=pid,new_targets=nc,planning_max=BANDS[level]['new_max']);flagged.add(pid)
            cov=r.get('estimated_known_token_coverage')
            if isinstance(cov,(int,float)) and cov>0: coverage['measured']+=1
            else:
                coverage['missing_or_placeholder']+=1;add(flags,'known_token_coverage_unmeasured',level=level,passage_id=pid,value=cov);flagged.add(pid)
        m=statistics.mean(wc);means.append((level,m))
        summary[level]={
            'passages':len(rows),'word_count_mean':round(m,2),'word_count_median':statistics.median(wc),'word_count_min':min(wc),'word_count_max':max(wc),
            'length_zones':dict(zones),'stored_word_count_mismatches_gt2':count_mismatch,
            'new_target_mean':round(statistics.mean(new_counts),2),'new_target_max':max(new_counts),'passages_above_new_target_max':over_new,
            'coverage_state':dict(coverage),'flagged_passages':len(flagged),
        }
    monotonic=all(means[i][1] <= means[i+1][1] for i in range(len(means)-1))
    payload={'pass':7,'name':'cefr_difficulty_calibration_against_production_standard','scope':'Arabic A1-C2 canonical reading corpus','reference':'docs/READING_PASSAGE_STANDARD.md sections 6,7,19','interpretation':'length and lexical-load bands are planning diagnostics, not sufficient CEFR classifiers','levels':summary,'cross_level':{'mean_word_count_non_decreasing':monotonic,'mean_word_counts':dict((l,round(m,2)) for l,m in means)},'totals':{'review_flags':len(flags)},'flags':flags,'status':'PASS' if not flags else 'REVIEW_REQUIRED'}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'means':payload['cross_level']['mean_word_counts'],'review_flags':len(flags)},ensure_ascii=False));print('status='+payload['status'])
if __name__=='__main__':main()
