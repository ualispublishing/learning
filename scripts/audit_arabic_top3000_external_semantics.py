#!/usr/bin/env python3
"""Independent Kaikki + OMW semantic audit for Arabic ranks 1001-3000."""
from __future__ import annotations
import csv, json, re, unicodedata
from pathlib import Path
import wn
from wordfreq import zipf_frequency

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
TARGET=AUDIT/'arabic_top3000_candidate.csv'; EVID=AUDIT/'arabic_top3000_continuation_evidence.csv'
DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]'); WORD=re.compile(r"[A-Za-z][A-Za-z'\-]*")
SPLIT=re.compile(r'\s*(?:;|/|\||,)\s*')
STOP={'a','an','the','to','of','in','on','at','for','from','by','with','and','or','as','is','are','was','were','be','been','being','one','that','this','which','who','whom','something','someone','used','use','form','forms','person','thing','things','depending','context','noun','verb','adjective','adverb','preposition','conjunction'}

def norm(s): return DIAC.sub('',unicodedata.normalize('NFKC',s or '').replace('ـ','')).strip()
def meaning(back):
 m=re.search(r'(?m)^Meaning:\s*(.+?)\s*$',back or ''); return m.group(1).strip() if m else ''
def raw(t): return [x.strip("'-").lower() for x in WORD.findall(t or '') if x.strip("'-")]
def content(t):
 out=set()
 for x in raw(t):
  if x in STOP: continue
  if len(x)>5 and x.endswith('ies'): x=x[:-3]+'y'
  else:
   for suf in ('ingly','ation','ments','ment','ing','ied','ed','es','s'):
    if len(x)>len(suf)+3 and x.endswith(suf): x=x[:-len(suf)]; break
  if len(x)>=2 and x not in STOP: out.add(x)
 return out
def canonical(t):
 out=set()
 for p in SPLIT.split(t or ''):
  z=raw(p)
  if len(z)>1 and z[0] in {'a','an','the'}: z=z[1:]
  if z and z[0]=='to' and len(z)==2: z=z[1:]
  if z and len(z)<=5: out.add(' '.join(z))
 return out
def agrees(a,b):
 h=sorted(content(a)&content(b))
 if h:return True,'|'.join(h[:12])
 h=sorted(canonical(a)&canonical(b)); return (bool(h),'|'.join(h[:12]))
def load_kaikki(path,targets):
 vals={t:[] for t in targets}
 with path.open(encoding='utf-8',errors='replace') as f:
  for line in f:
   try:o=json.loads(line)
   except:continue
   w=norm(str(o.get('word','')))
   if w not in vals:continue
   for s in o.get('senses') or []:
    for g in s.get('glosses') or []:
     g=re.sub(r'\s+',' ',str(g)).strip()
     if g and g not in vals[w]:vals[w].append(g)
 return {w:'; '.join(v)[:7000] for w,v in vals.items() if v}
def omw(front,net):
 vals=[]
 try:syn=net.synsets(front)
 except:syn=[]
 for ss in syn:
  try:eng=ss.translate(lexicon='omw-en:2.0')
  except:eng=[]
  for e in eng:
   try:
    vals.extend(e.lemmas()); d=e.definition()
    if d:vals.append(d)
   except:pass
 return '; '.join(dict.fromkeys(vals))[:7000]

def main():
 import argparse
 ap=argparse.ArgumentParser(); ap.add_argument('--kaikki-jsonl',required=True); a=ap.parse_args()
 with TARGET.open(encoding='utf-8-sig',newline='') as f:cards=list(csv.DictReader(f))
 with EVID.open(encoding='utf-8',newline='') as f:ev=list(csv.DictReader(f))
 if len(cards)!=2000 or len(ev)!=2000:raise SystemExit('expected 2000 candidate/evidence rows')
 fronts=[norm(r['Front']) for r in cards]; kk=load_kaikki(Path(a.kaikki_jsonl),set(fronts)); net=wn.Wordnet('omw-arb:2.0')
 results=[]
 for i,(card,e) in enumerate(zip(cards,ev),1001):
  f=norm(card['Front']); m=meaning(card['Back']); kg=kk.get(f,''); ow=omw(f,net)
  ko,kt=agrees(m,kg) if kg else (False,''); oo,ot=agrees(m,ow) if ow else (False,'')
  corpus=zipf_frequency(f,'ar')>0; morph=int(e.get('calima_exact_analyses') or 0)>0; sem=int(ko)+int(oo)
  status='verified_strong' if sem>=2 else 'verified' if sem==1 and corpus and morph else 'explicit_review_required'
  results.append({'rank':i,'front':f,'meaning':m,'kaikki_entry':bool(kg),'kaikki_semantic_agreement':ko,'kaikki_overlap_terms':kt,'omw_entry':bool(ow),'omw_semantic_agreement':oo,'omw_overlap_terms':ot,'wordfreq_attested':corpus,'calima_exact':morph,'status':status})
 fields=list(results[0]); review=[r for r in results if r['status']=='explicit_review_required']
 for name,data in [('arabic_top3000_external_semantic_audit.csv',results),('arabic_top3000_external_semantic_review_queue.csv',review)]:
  with (AUDIT/name).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
 counts={}
 for r in results:counts[r['status']]=counts.get(r['status'],0)+1
 s={'rows':2000,'status_counts':counts,'kaikki_entry_coverage':sum(r['kaikki_entry'] for r in results),'kaikki_semantic_agreement':sum(r['kaikki_semantic_agreement'] for r in results),'omw_entry_coverage':sum(r['omw_entry'] for r in results),'omw_semantic_agreement':sum(r['omw_semantic_agreement'] for r in results),'wordfreq_attested':sum(r['wordfreq_attested'] for r in results),'calima_exact':sum(r['calima_exact'] for r in results),'explicit_review_rows':len(review),'promotion_gate':'PASS' if not review else 'REVIEW_REQUIRED'}
 (AUDIT/'arabic_top3000_external_semantic_audit_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
