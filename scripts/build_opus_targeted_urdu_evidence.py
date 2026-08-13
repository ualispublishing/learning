#!/usr/bin/env python3
"""Build targeted Urdu sense corroboration from independent OPUS aligned sentences.

For each high-frequency Urdu candidate, collect the English content-word stems present
in its Kaikki/ReadUrdu dictionary senses. Across aligned non-subtitle OPUS sentences,
measure sentence-level co-occurrence and lift for those *pre-existing* dictionary
terms. This can corroborate or reject a dictionary sense but cannot generate one.
"""
from __future__ import annotations
import argparse,json,re,requests,zipfile,io,sys,math
from collections import Counter,defaultdict
from pathlib import Path
from wordfreq import top_n_list
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_french_urdu_core_candidates_v2 as fu
import build_urdu_top3000_v14 as base
AUDIT=ROOT/'audit';AR=re.compile(r'[\u0600-\u06ff]+')
CORPORA={
 'Anuvaad':'https://object.pouta.csc.fi/OPUS-Anuvaad/v1/moses/en-ur.txt.zip',
 'GlobalVoices':'https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/moses/en-ur.txt.zip',
 'QED':'https://object.pouta.csc.fi/OPUS-QED/v2.0a/moses/en-ur.txt.zip',
 'TED2020':'https://object.pouta.csc.fi/OPUS-TED2020/v1/moses/en-ur.txt.zip',
 'Tatoeba':'https://object.pouta.csc.fi/OPUS-Tatoeba/v2026-07-08/moses/en-ur.txt.zip',
 'pmindia':'https://object.pouta.csc.fi/OPUS-pmindia/v1b/moses/en-ur.txt.zip',
 'tico-19':'https://object.pouta.csc.fi/OPUS-tico-19/v2020-10-28/moses/en-ur.txt.zip',
 'translatewiki':'https://object.pouta.csc.fi/OPUS-translatewiki/v2026-07-01/moses/en-ur.txt.zip',
 'GNOME':'https://object.pouta.csc.fi/OPUS-GNOME/v1/moses/en-ur.txt.zip',
 'NeuLab-TedTalks':'https://object.pouta.csc.fi/OPUS-NeuLab-TedTalks/v1/moses/en-ur.txt.zip',
}

def pick(z):
 ns=z.namelist();en=[n for n in ns if n.lower().endswith('.en')];ur=[n for n in ns if n.lower().endswith('.ur')]
 if not en or not ur:raise RuntimeError(ns[:20])
 return en[0],ur[0]
def ur_tokens(s):return {fu.norm_ur(x) for x in AR.findall(s or '') if fu.norm_ur(x)}
def atom_specs(kg,rg):
 out=[]
 for src,text in [('Kaikki',kg),('ReadUrdu',rg)]:
  for atom in base.atoms(text):
   ts=frozenset(base.toks(atom))
   if not ts or len(ts)>3:continue
   if not any(x['tokens']==ts for x in out):out.append({'source':src,'gloss':atom,'tokens':ts})
 return out[:30]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kaikki',required=True);ap.add_argument('--readurdu',required=True);a=ap.parse_args()
 kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur);read=fu.read_readurdu(Path(a.readurdu))
 words=[];seen=set()
 for w in top_n_list('ur',20000):
  w=fu.norm_ur(w)
  if w and ' ' not in w and w not in seen:seen.add(w);words.append(w)
 specs={};interest={};all_stems=set()
 for w in words:
  ko=kk.get(w,{});kg=base.clean(fu.compact_meaning(ko.get('all_glosses',[]))) if ko else '';rg=base.clean(read.get(w,{}).get('meaning','')) if w in read else ''
  sp=atom_specs(kg,rg)
  if sp:
   specs[w]={'kaikki':kg,'readurdu':rg,'atoms':sp}; stems=set().union(*(x['tokens'] for x in sp));interest[w]=stems;all_stems.update(stems)
 ur_df=Counter();en_df=Counter();cooc=defaultdict(Counter);N=0;stats={};errors={}
 for name,url in CORPORA.items():
  try:
   r=requests.get(url,timeout=120);r.raise_for_status()
   with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    en_name,ur_name=pick(z);ens=z.read(en_name).decode('utf-8',errors='replace').splitlines();urs=z.read(ur_name).decode('utf-8',errors='replace').splitlines()
   n=min(len(ens),len(urs));kept=0
   for e,u in zip(ens[:n],urs[:n]):
    us=ur_tokens(u)&interest.keys()
    if not us:continue
    es=set(base.toks(e))&all_stems
    N+=1;kept+=1
    for t in es:en_df[t]+=1
    for w in us:
     ur_df[w]+=1
     for t in interest[w]&es:cooc[w][t]+=1
   stats[name]={'raw_pairs':n,'target_word_pairs':kept,'url':url}
  except Exception as exc:errors[name]=repr(exc)
 evidence={};supported=0
 for w,meta in specs.items():
  ud=ur_df[w]
  if ud<2:continue
  accepted=[]
  for sp in meta['atoms']:
   detail=[];ok=True
   for t in sp['tokens']:
    c=cooc[w][t];basep=en_df[t]/max(N,1);obs=c/ud;lift=obs/max(basep,1/max(N,1))
    detail.append({'stem':t,'cooccurrence_sentences':c,'urdu_sentences':ud,'english_sentences':en_df[t],'observed_rate':round(obs,5),'lift':round(lift,2)})
    # Require repeated evidence. Low-frequency words may pass with two sentence
    # witnesses; high-frequency words need three. Lift filters generic English words.
    need=3 if ud>=20 else 2
    if c<need or lift<2.5 or obs<0.01:ok=False
   if ok:accepted.append({'source':sp['source'],'gloss':sp['gloss'],'details':detail,'score':round(min(d['lift'] for d in detail),2)})
  if accepted:
   accepted.sort(key=lambda x:(-x['score'],len(x['gloss'])));evidence[w]={'urdu_sentence_count':ud,'accepted_dictionary_senses':accepted[:8]};supported+=1
 out={'method':'targeted aligned-sentence dictionary-sense corroboration','selected_corpora':stats,'errors':errors,'aligned_sentences_with_target_words':N,'candidate_words_with_dictionary_atoms':len(specs),'words_with_independent_opus_support':supported,'evidence':evidence,'policy':'Evidence only: each supported English token must come from an existing Kaikki/ReadUrdu sense and independently recur in aligned non-subtitle OPUS translations with minimum count, rate, and lift. No meaning is generated from the corpus.'}
 (AUDIT/'opus_targeted_urdu_evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');summary={k:v for k,v in out.items() if k!='evidence'};(AUDIT/'opus_targeted_urdu_evidence_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
