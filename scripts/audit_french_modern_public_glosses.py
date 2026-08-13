#!/usr/bin/env python3
"""Second-pass public-gloss audit for both French vocabulary decks.

The earlier audit caught raw historical/lexicographic artifacts, but some remaining
meanings are still dictionary prose rather than learner glosses. This pass combines
style diagnostics with an independent modern corpus-derived French->English signal.
The corpus signal never authors a gloss; it only indicates which already-published
sense fragments are likely to be current/common.
"""
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path
from word2word import Word2word
ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit'
FILES=['french_top1000.csv','french_top3000.csv']
MEAN=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$');POS=re.compile(r'(?m)^Part of speech:\s*(.+?)\s*$');RANK=re.compile(r'(?m)^Rank:\s*(\d+)\s*$')
WORD=re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:'[A-Za-zÀ-ÖØ-öø-ÿ]+)?")
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used','use'}
PROSE=re.compile(r'\b(?:a time or a place|connects? a person|delegated officially|by extension|figuratively|literally|especially|in particular|used (?:to|for|when)|refers? to|the act of|the state of|a person who|a thing that|someone who|something that|historically|obsolete|archaic)\b',re.I)

def extract(rx,s):
 m=rx.search(s or '');return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
def stem(w):
 w=w.lower().strip("'-")
 if len(w)>5 and w.endswith('ies'):return w[:-3]+'y'
 for suf in ('ingly','ations','ation','ments','ment','ness','ities','ity','ing','ied','ed','es','s'):
  if len(w)>len(suf)+3 and w.endswith(suf):
   b=w[:-len(suf)];return b+'y' if suf=='ied' else b
 return w
def toks(s):return {stem(w) for w in WORD.findall(s or '') if stem(w) not in STOP and len(stem(w))>1}
def agree(a,b):
 A,B=toks(a),toks(b)
 if A&B:return True
 for x in A:
  for y in B:
   if min(len(x),len(y))>=4 and (x.startswith(y) or y.startswith(x)):return True
 return False
def corpus(model,w):
 try:vals=model(w) or []
 except Exception:vals=[]
 return '; '.join(dict.fromkeys(str(x).replace('_',' ') for x in vals[:15]))
def fragments(m):
 # Preserve verb phrases while splitting dictionary bundles into reviewable units.
 out=[]
 for x in re.split(r'\s*;\s*|\s*,\s*(?=(?:to\s+)?[A-Za-z])',m or ''):
  x=re.sub(r'\s+',' ',x).strip(' ;,.')
  if x and x.casefold() not in {y.casefold() for y in out}:out.append(x)
 return out
def main():
 model=Word2word('fr','en');allq=[];summary={}
 for name in FILES:
  with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
  q=[];counts=Counter()
  for i,r in enumerate(rows,1):
   back=r.get('Back','');m=extract(MEAN,back);pos=extract(POS,back);rank=extract(RANK,back) or str(i);c=corpus(model,r.get('Front',''));fs=fragments(m)
   flags=[]
   if PROSE.search(m):flags.append('dictionary_prose_in_meaning')
   if len(WORD.findall(m))>16:flags.append('meaning_over_16_words')
   if len(fs)>5:flags.append('overbundled_6plus_fragments')
   supported=[x for x in fs if agree(x,c)] if c else []
   if c and not agree(m,c):flags.append('no_modern_corpus_overlap')
   if flags:
    for fl in set(flags):counts[fl]+=1
    q.append({'rank':rank,'front':r.get('Front',''),'meaning':m,'pos':pos,'flags':sorted(set(flags)),'corpus_signal':c,'current_fragments':fs,'corpus_supported_fragments':supported})
  summary[name]={'rows':len(rows),'flagged_rows':len(q),'flag_counts':dict(counts)};allq.extend({'file':name,**x} for x in q)
  (AUDIT/f'{name[:-4]}_modern_public_review.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 summary['overall_flagged']=len(allq);summary['policy']='Corpus evidence only selects among already-published sense fragments; it never authors a French meaning. Dictionary prose, very long bundles, and meanings lacking modern-corpus overlap are manual-review signals.'
 (AUDIT/'french_modern_public_gloss_audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
