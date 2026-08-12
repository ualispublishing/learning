#!/usr/bin/env python3
"""Build a conservative cleaned candidate from arabic_phrase_bank.csv.

Quality-first policy: remove unmistakable synthetic escalation artifacts and
mixed-script/overlong fronts, normalize one recurring generations typo, and
collapse normalized duplicate fronts. The live phrase bank is never changed by
this script; output stays under audit/ until the candidate passes a fresh audit.
"""
from __future__ import annotations
import csv,re,unicodedata,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'arabic_phrase_bank.csv'; OUT=ROOT/'audit'/'arabic_phrase_bank_clean_candidate.csv'; REJ=ROOT/'audit'/'arabic_phrase_bank_clean_rejections.csv'
DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]'); LAT=re.compile(r'[A-Za-z]'); ARW=re.compile(r'[\u0621-\u064a]+'); PUN=re.compile(r'[^\u0621-\u064a\s]')
SYNTH=re.compile(r'(?:-emphatic\)|maximum possible human way|absolute ultimate|absolute maximum|100%|thronely|luminously|celestially|immortally|malakutiyyan|arshiyyan|sarmadiyyan|qudusiyyan|hexacosi|heptacosi|enneadeca|icosa|pentacosi|divinely luminous)',re.I)
def undiac(s):return DIAC.sub('',unicodedata.normalize('NFKC',s or '').replace('ـ','')).strip()
def norm(s):return re.sub(r'\s+',' ',PUN.sub(' ',undiac(s))).strip()
def repair(s):
 # recurring malformed spelling of أجيال in both vocalized and unvocalized text
 s=(s or '').replace('الجِيال','الأَجْيَال').replace('الجيال','الأجيال')
 return s
def main():
 with SRC.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 kept=[];rejected=[];seen={}
 for rank,r in enumerate(rows,1):
  front=repair((r.get('Front') or '').strip());back=repair(r.get('Back') or ''); reasons=[]
  if LAT.search(front):reasons.append('latin_in_front')
  if len(front)>180:reasons.append('overlong_front')
  if len(ARW.findall(undiac(front)))>18:reasons.append('too_many_front_tokens')
  if SYNTH.search(front) or SYNTH.search(back):reasons.append('synthetic_escalation_artifact')
  n=norm(front)
  if n in seen:reasons.append(f'normalized_duplicate_of_source_rank_{seen[n]}')
  if reasons:
   rejected.append({'source_rank':rank,'front':front,'reasons':'|'.join(reasons)});continue
  seen[n]=rank;kept.append({'Front':front,'Back':back})
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader();w.writerows(kept)
 with REJ.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=['source_rank','front','reasons']);w.writeheader();w.writerows(rejected)
 s={'source_rows':len(rows),'candidate_rows':len(kept),'rejected_rows':len(rejected),'distinct_normalized_fronts':len(seen),'policy':'prune unmistakable synthetic/mixed-script/overlong/duplicate artifacts; repair recurring أجيال typo; preserve remaining cards for fresh audit'}
 (ROOT/'audit'/'arabic_phrase_bank_clean_candidate_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
