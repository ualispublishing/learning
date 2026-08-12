#!/usr/bin/env python3
"""Third-source semantic audit for Urdu ranks 1001-3000 using word2word.

word2word is a corpus-derived bilingual lexicon, so it is used only as an
independent semantic confirmation/triage signal, never as an automatic rewrite
or sole authority.
"""
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path
from word2word import Word2word
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
WORD=re.compile(r"[a-z]+(?:'[a-z]+)?",re.I); STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one'}
def toks(t):
 x={w.lower() for w in WORD.findall(t or '') if w.lower() not in STOP}; y=set(x)
 for w in list(x):
  if len(w)>4 and w.endswith('ies'):y.add(w[:-3]+'y')
  if len(w)>4 and w.endswith('es'):y.add(w[:-2])
  if len(w)>3 and w.endswith('s'):y.add(w[:-1])
  if len(w)>5 and w.endswith('ing'):y.add(w[:-3])
  if len(w)>4 and w.endswith('ed'):y.add(w[:-2])
 return y
def overlap(a,b):
 h=sorted(toks(a)&toks(b));return bool(h),'|'.join(h[:12])
def main():
 with (AUDIT/'urdu_top3000_audit.csv').open(encoding='utf-8',newline='') as f:base=list(csv.DictReader(f))
 with (AUDIT/'urdu_top3000_continuation_evidence.csv').open(encoding='utf-8',newline='') as f:ev=list(csv.DictReader(f))
 if len(base)!=2000 or len(ev)!=2000:raise SystemExit('expected 2000 rows')
 try:ur2en=Word2word('ur','en')
 except Exception as exc:raise SystemExit(f'word2word Urdu-English lexicon unavailable: {exc}')
 out=[]
 for b,e in zip(base,ev):
  front=b['front']; meaning=b['meaning']
  try:translations=ur2en(front) or []
  except Exception:translations=[]
  w2='; '.join(dict.fromkeys(str(x) for x in translations[:12])); wok,hits=overlap(meaning,w2) if w2 else (False,'')
  rok,_=overlap(meaning,e.get('readurdu_meaning','')) if e.get('readurdu_meaning') else (False,'')
  kok,_=overlap(meaning,e.get('kaikki_meaning','')) if e.get('kaikki_meaning') else (False,'')
  semantic_sources=int(rok)+int(kok)+int(wok)
  lexical=e.get('cle_wordnet')=='True' or e.get('cle_closed_class')=='True'
  corpus=float(b.get('wordfreq_zipf') or 0)>0
  if semantic_sources>=2 and corpus:status='verified_strong'
  elif semantic_sources>=1 and corpus and lexical:status='verified'
  else:status='explicit_review_required'
  x=dict(b);x.update({'readurdu_semantic_agreement':rok,'kaikki_semantic_agreement_recheck':kok,'word2word_entry':bool(translations),'word2word_translations':w2,'word2word_semantic_agreement':wok,'word2word_overlap_terms':hits,'semantic_source_count':semantic_sources,'combined_status':status});out.append(x)
 fields=list(out[0]);review=[r for r in out if r['combined_status']=='explicit_review_required']
 with (AUDIT/'urdu_top3000_multisource_audit.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
 with (AUDIT/'urdu_top3000_multisource_review_queue.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(review)
 c=Counter(r['combined_status'] for r in out);s={'rows':2000,'status_counts':dict(sorted(c.items())),'readurdu_semantic_agreement':sum(r['readurdu_semantic_agreement'] for r in out),'kaikki_semantic_agreement':sum(r['kaikki_semantic_agreement_recheck'] for r in out),'word2word_entry_coverage':sum(r['word2word_entry'] for r in out),'word2word_semantic_agreement':sum(r['word2word_semantic_agreement'] for r in out),'explicit_review_rows':len(review),'promotion_gate':'PASS' if not review else 'REVIEW_REQUIRED','policy':'word2word is an independent corpus-derived semantic signal, never a sole rewrite authority.'}
 (AUDIT/'urdu_top3000_multisource_audit_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
