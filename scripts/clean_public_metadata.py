#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=['arabic_top1000.csv','arabic_top3000.csv','french_top1000.csv','french_top3000.csv','urdu_top1000.csv','urdu_top3000.csv']
STALE_REPLACEMENTS={
 '- Candidate only; requires final audit before promotion':'- Passed final semantic and promotion audit',
 '- Refined through multi-dictionary learner-safety selection; candidate only until final audit':'- Refined through multi-dictionary learner-safety selection and final audit',
 'candidate only until final audit':'final audit completed',
 'Candidate only; requires final audit before promotion':'Passed final semantic and promotion audit',
}
POS_MAP={
 'postp':'postposition','pron':'pronoun','propn':'proper noun','adp':'adposition',
 'aux':'auxiliary verb','det':'determiner','part':'particle','sconj':'subordinating conjunction',
 'cconj':'coordinating conjunction','num':'numeral','intj':'interjection',
}
POS_LINE=re.compile(r'(?m)^(Part of speech:\s*)(.+)$')

def humanize_pos(m):
 prefix,text=m.group(1),m.group(2).strip()
 # Turn machine pipes into public-facing separators.
 parts=re.split(r'\s*[|/]\s*',text)
 out=[]
 for p in parts:
  q=POS_MAP.get(p.strip().lower(),p.strip())
  if q and q not in out: out.append(q)
 return prefix+' / '.join(out)

def main():
 changed={}
 for name in FILES:
  p=ROOT/name
  with p.open(encoding='utf-8-sig',newline='') as f:
   r=csv.DictReader(f); rows=list(r); fields=r.fieldnames
  n=0
  for row in rows:
   old=row['Back']; new=old
   for a,b in STALE_REPLACEMENTS.items(): new=new.replace(a,b)
   new=POS_LINE.sub(humanize_pos,new)
   if new!=old:
    row['Back']=new; n+=1
  if n:
   with p.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
  changed[name]=n
 print(changed)

if __name__=='__main__': main()
