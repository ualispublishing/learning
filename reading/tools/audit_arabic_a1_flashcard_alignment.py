#!/usr/bin/env python3
import csv,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/'reading/arabic/a1/passages.jsonl'; D=R/'arabic_top1000.csv'; O=R/'reading/audit/arabic_a1_flashcard_alignment.json'
RXR=re.compile(r'(?m)^Rank:\s*(\d+)\s*$'); RXM=re.compile(r'(?ms)^Meaning:\s*(.+?)(?=\n\nPart of speech:|\Z)'); RXP=re.compile(r'(?ms)^Part of speech:\s*(.+?)(?=\n\nSources:|\Z)')
def x(rx,s):
 m=rx.search(s or ''); return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def rid(s):
 m=re.fullmatch(r'ar-r(\d+)',s or ''); return int(m.group(1)) if m else None
def words(s): return {w.lower() for w in re.findall(r'[A-Za-z]+',s or '') if len(w)>1}
def main():
 ps=[json.loads(z) for z in P.read_text(encoding='utf-8').splitlines() if z.strip()]
 with D.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 cards={}
 for i,r in enumerate(rows,1):
  b=r['Back']; n=int(x(RXR,b) or i); cards[n]={'front':r['Front'],'meaning':x(RXM,b),'pos':x(RXP,b),'verified':n<=100 or 'second-pass educator review (2026-08-13)' in b}
 problems=[]; out=[]
 for p in ps:
  a=[]
  for g in ('new_lexical_targets','review_lexical_targets'):
   for t in p.get(g,[]):
    n=t.get('source_rank') or rid(t.get('id')); c=cards.get(n)
    ok=bool(c) and (not t.get('intended_sense') or bool(words(t['intended_sense']) & words(c['meaning'])))
    verified=bool(c and c['verified'])
    if not c: problems.append(f"{p['id']}:{t.get('id')}:missing_card")
    elif not ok: problems.append(f"{p['id']}:{t.get('id')}:sense_mismatch")
    elif not verified: problems.append(f"{p['id']}:{t.get('id')}:not_second_pass_verified")
    a.append({'group':g,'id':t.get('id'),'rank':n,'form':t.get('form'),'intended_sense':t.get('intended_sense'),'context_pos':t.get('part_of_speech'),'live_meaning':c['meaning'] if c else None,'live_pos':c['pos'] if c else None,'sense_compatible':ok,'second_pass_verified':verified})
  out.append({'id':p['id'],'targets':a})
 data={'passage_count':len(ps),'problems':problems,'gate':'PASS' if not problems else 'REVIEW_REQUIRED','passages':out}
 O.parent.mkdir(parents=True,exist_ok=True); O.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'passages':len(ps),'problems':len(problems),'gate':data['gate']}))
 if problems: raise SystemExit('alignment review required')
if __name__=='__main__': main()
