#!/usr/bin/env python3
"""Build a quality-first Urdu rank-1001..3000 continuation candidate.

The CLE 5,000-word corpus list supplies ordering only. The verified live top-1000
is excluded. A candidate must be present in the CLE Urdu WordNet wordlist or CLE
closed-class list, and its English learner meaning must be corroborated by at
least two independent semantic signals among Kaikki/Wiktextract, ReadUrdu, and
the corpus-derived word2word Urdu-English lexicon. No source is allowed to fill a
row by itself, and visibly archaic/mixed-Devanagari ReadUrdu prose is excluded
from learner-meaning selection.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
from word2word import Word2word
import build_french_urdu_core_candidates_v2 as fu

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'; TARGET=2000
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
DEV=re.compile(r"[\u0900-\u097f]")
SPLIT=re.compile(r"\s*(?:;|/|\||,(?!\s*(?:which|who|that|when|where)))\s*")
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one'}
BAD_READ=('q.v.','see gram',' gram.','s.m.','s.f.','adj.','adv.','pers.','aor.','contrac.','dialec.','prob. akin')
def clean(t):return ' '.join((t or '').replace('_',' ').split()).strip(' ;,.')
def toks(t):
 out=set()
 for w in WORD.findall(t or ''):
  w=w.lower().strip("'-")
  if w in STOP or len(w)<2:continue
  if len(w)>4 and w.endswith('ies'):w=w[:-3]+'y'
  else:
   for suf in ('ingly','ation','ments','ment','ing','ied','ed','es','s'):
    if len(w)>len(suf)+3 and w.endswith(suf):w=w[:-len(suf)];break
  if w not in STOP:out.add(w)
 return out
def agree(a,b):return bool(toks(a)&toks(b))
def fragments(t):return [clean(x) for x in SPLIT.split(t or '') if clean(x)]
def safe_read(t):
 x=clean(t)
 if not x or len(x)>180 or DEV.search(x):return ''
 low=x.lower()
 if any(p in low for p in BAD_READ):return ''
 if ' | also:' in x:x=x.split(' | also:',1)[0].strip()
 return x if len(x)<=180 else ''
def safe_text(t):
 x=clean(t);return x if x and len(x)<=220 and not DEV.search(x) and not any(c in x for c in '[]<>') else ''
def narrow(primary,other):
 hits=[p for p in fragments(primary) if agree(p,other)]
 if hits:return '; '.join(dict.fromkeys(hits[:5]))
 return clean(primary) if agree(primary,other) else ''
def live_fronts():
 with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kaikki',required=True);ap.add_argument('--urdu-freq-text',required=True);ap.add_argument('--urdu-wordnet-text',required=True);ap.add_argument('--urdu-closed-text',required=True);ap.add_argument('--readurdu',required=True);a=ap.parse_args()
 excluded=live_fronts();freq_text=Path(a.urdu_freq_text).read_text(encoding='utf-8',errors='replace');wn_text=fu.norm_ur(Path(a.urdu_wordnet_text).read_text(encoding='utf-8',errors='replace'));closed_text=fu.norm_ur(Path(a.urdu_closed_text).read_text(encoding='utf-8',errors='replace'))
 ranked=fu.extract_urdu_freq(freq_text);read=fu.read_readurdu(Path(a.readurdu));kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur);w2=Word2word('ur','en')
 rows=[];rej=[];seen=set()
 for word,freq in ranked:
  word=fu.norm_ur(word)
  if not word or word in excluded or word in seen:continue
  in_wn=fu.inventory_contains(wn_text,word);in_closed=fu.inventory_contains(closed_text,word)
  if not (in_wn or in_closed):rej.append({'front':word,'frequency':freq,'reason':'not_cle_lexical_or_closed_class'});continue
  kg=safe_text(fu.compact_meaning(kk.get(word,{}).get('all_glosses',[]))) if word in kk else ''
  rg=safe_read(read.get(word,{}).get('meaning','')) if word in read else ''
  try:wlist=w2(word) or []
  except Exception:wlist=[]
  wg=safe_text('; '.join(dict.fromkeys(str(x) for x in wlist[:12])))
  kr=bool(kg and rg and agree(kg,rg));kw=bool(kg and wg and agree(kg,wg));rw=bool(rg and wg and agree(rg,wg))
  if not (kr or kw or rw):
   rej.append({'front':word,'frequency':freq,'reason':'no_two_source_semantic_agreement','kaikki':kg,'readurdu':rg,'word2word':wg});continue
  if kr or kw:
   other='; '.join(x for x in (rg if kr else '',wg if kw else '') if x);meaning=narrow(kg,other) or kg;basis='kaikki+readurdu' if kr and not kw else 'kaikki+word2word' if kw and not kr else 'kaikki+readurdu+word2word'
  else:
   meaning=narrow(rg,wg) or rg;basis='readurdu+word2word'
  meaning=safe_text(meaning)
  if not meaning:rej.append({'front':word,'frequency':freq,'reason':'no_safe_corroborated_learner_meaning'});continue
  seen.add(word);rows.append({'rank':1001+len(rows),'front':word,'meaning':meaning,'frequency':freq,'cle_wordnet':in_wn,'cle_closed_class':in_closed,'kaikki_meaning':kg,'readurdu_meaning':rg,'word2word_meaning':wg,'kaikki_readurdu_agreement':kr,'kaikki_word2word_agreement':kw,'readurdu_word2word_agreement':rw,'semantic_basis':basis})
  if len(rows)>=TARGET:break
 fields=list(rows[0]) if rows else ['rank','front','meaning']
 with (AUDIT/'urdu_top3000_continuation_evidence_v3.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 with (AUDIT/'urdu_top3000_candidate_v3.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
  for r in rows:
   back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: {r['frequency']}",'',f"Semantic verification: {r['semantic_basis']}",'','Sources:','- CLE Urdu 5,000 corpus frequency list — ordering authority','- CLE Urdu WordNet/closed-class lists — lexical-form gate','- Kaikki/Wiktextract, ReadUrdu, word2word — independent semantic signals','- Candidate only; requires final audit before promotion'])
   w.writerow({'Front':r['front'],'Back':back})
 rfields=sorted({k for r in rej for k in r}) if rej else ['front','frequency','reason']
 with (AUDIT/'urdu_top3000_rejections_v3.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=rfields);w.writeheader();w.writerows(rej)
 summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)],'rejected_before_target':len(rej),'semantic_basis_counts':{b:sum(r['semantic_basis']==b for r in rows) for b in sorted({r['semantic_basis'] for r in rows})},'cle_wordnet_rows':sum(r['cle_wordnet'] for r in rows),'cle_closed_class_rows':sum(r['cle_closed_class'] for r in rows),'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET else 'FAIL','status':'candidate_only_not_promoted','policy':'Require CLE lexical membership plus two-source semantic agreement; never promote one-source or archaic/mixed-script glosses.'}
 (AUDIT/'urdu_top3000_candidate_v3_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
 if summary['structural_gate']!='PASS':raise SystemExit('fewer than 2,000 quality-gated Urdu continuation rows available from CLE top-5000')
if __name__=='__main__':main()
