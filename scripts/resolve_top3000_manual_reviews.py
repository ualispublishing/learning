#!/usr/bin/env python3
"""Apply narrow, auditable human resolutions to top3000 review queues."""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
# front -> required learner-meaning fragments (any one suffices unless tuple nested later)
RESOLVED={
 'french': {'les': ('the (plural)','them')},
 'arabic': {},
 'urdu': {},
}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--language',choices=RESOLVED,required=True); a=ap.parse_args(); lang=a.language
 p=AUDIT/f'{lang}_top3000_audit.csv'
 with p.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
 applied=[]
 for r in rows:
  req=RESOLVED[lang].get(r.get('front',''))
  if not req: continue
  m=(r.get('meaning') or '').casefold()
  if not any(x.casefold() in m for x in req): raise SystemExit(f"manual resolution meaning mismatch for {r.get('front')}: {m}")
  if r.get('flags'): raise SystemExit(f"cannot manually resolve structural flags for {r.get('front')}: {r.get('flags')}")
  r['status']='manual_verified'; applied.append({'rank':r['rank'],'front':r['front'],'meaning':r['meaning'],'reason':'explicit human review of conservative semantic-overlap false negative'})
 fields=list(rows[0])
 with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 review=[r for r in rows if r['status'] in {'explicit_review_required','verified_morphology_review_semantics'}]
 with (AUDIT/f'{lang}_top3000_review_queue.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(review)
 counts=Counter(r['status'] for r in rows)
 sp=AUDIT/f'{lang}_top3000_audit_summary.json'; s=json.loads(sp.read_text(encoding='utf-8'))
 s['status_counts']=dict(sorted(counts.items())); s['review_rows']=len(review); s['manual_resolutions_applied']=applied
 s['promotion_gate']='PASS' if s.get('blocking_problems',0)==0 and len(rows)==2000 and len(review)==0 else 'REVIEW_REQUIRED'
 sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (AUDIT/f'{lang}_top3000_manual_resolutions.json').write_text(json.dumps({'language':lang,'resolved':applied,'remaining_review_rows':len(review)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'language':lang,'applied':len(applied),'remaining_review_rows':len(review),'promotion_gate':s['promotion_gate']},ensure_ascii=False))
if __name__=='__main__':main()
