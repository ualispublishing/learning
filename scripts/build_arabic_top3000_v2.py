#!/usr/bin/env python3
"""Build a precision-gated Arabic rank-1001..3000 continuation.

Rank candidates come from the broad CAMeL MSA frequency inventory. The live
verified top-1000 is excluded. A continuation item is admitted only when its
meaning has cross-source semantic support: exact CALIMA stem semantics must agree
with Kaikki or OMW, or Kaikki and OMW must agree with each other. This intentionally
skips high-frequency abbreviation/sense noise rather than forcing a dubious card.
"""
from __future__ import annotations
import argparse,csv,json,re,unicodedata
from pathlib import Path
import wn
from wordfreq import zipf_frequency
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.morphology.database import MorphologyDB
from camel_tools.utils.charmap import CharMapper
import build_french_urdu_core_candidates_v2 as fu
import build_arabic_top1000_precision as ar
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'; TARGET=2000
WORD=re.compile(r"[A-Za-z][A-Za-z'\-]*"); STOP={'a','an','the','to','of','in','on','at','for','from','by','with','and','or','as','is','are','was','were','be','been','being','one','that','this','which','who','whom','something','someone','used','use','form','forms','person','thing','things','depending','context','noun','verb','adjective','adverb'}
def clean(t):return re.sub(r'\s+',' ',(t or '').replace('_',' ')).strip(' ;,.')
def toks(t):
 out=set()
 for x in WORD.findall(t or ''):
  x=x.lower().strip("'-")
  if x in STOP or len(x)<2:continue
  for suf in ('ingly','ation','ments','ment','ing','ied','ed','es','s'):
   if len(x)>len(suf)+3 and x.endswith(suf):x=x[:-len(suf)];break
  if x not in STOP:out.add(x)
 return out
def agree(a,b):return bool(toks(a)&toks(b))
def good(t):
 x=clean(t);return bool(x) and len(x)<=240 and not any(c in x for c in '[]<>_') and '+' not in x
def load_kaikki(path,targets):
 vals={t:[] for t in targets}
 with path.open(encoding='utf-8',errors='replace') as f:
  for line in f:
   try:o=json.loads(line)
   except:continue
   w=ar.undiac(str(o.get('word',''))).strip()
   if w not in vals:continue
   for s in o.get('senses') or []:
    for g in s.get('glosses') or []:
     g=clean(str(g))
     if g and g not in vals[w]:vals[w].append(g)
 return {w:fu.compact_meaning(v) for w,v in vals.items() if v}
def omw_evidence(front,net):
 vals=[]
 try:syns=net.synsets(front)
 except:syns=[]
 for ss in syns:
  try:eng=ss.translate(lexicon='omw-en:2.0')
  except:eng=[]
  for e in eng:
   try:
    vals.extend(e.lemmas());d=e.definition()
    if d:vals.append(d)
   except:pass
 return clean('; '.join(dict.fromkeys(vals)))[:1500]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--broad',required=True);ap.add_argument('--kaikki',required=True);a=ap.parse_args()
 with (ROOT/'arabic_top1000.csv').open(encoding='utf-8-sig',newline='') as f:excluded={ar.undiac((r.get('Front') or '')).strip() for r in csv.DictReader(f)}
 with Path(a.broad).open(encoding='utf-8',newline='') as f:broad=list(csv.DictReader(f))
 targets=[]
 for r in broad:
  w=ar.undiac(r.get('front','')).strip()
  if w and w not in excluded and len(w)>=2:targets.append(w)
 kk=load_kaikki(Path(a.kaikki),set(targets));net=wn.Wordnet('omw-arb:2.0');an=Analyzer(MorphologyDB.builtin_db('calima-msa-r13',flags='a'),backoff='NONE',cache_size=40000);bw=CharMapper.builtin_mapper('bw2ar')
 rows=[];rej=[];seen=set()
 for r in broad:
  front=ar.undiac(r.get('front','')).strip();pos=(r.get('pos') or '').strip()
  if not front or front in excluded or front in seen or len(front)<2:continue
  if zipf_frequency(front,'ar')<=0:continue
  analyses=[x for x in an.analyze(front) if ar.exact_lexical_match(front,x) and str(x.get('pos',''))==pos];analyses.sort(key=ar.score,reverse=True)
  cal='';root=''
  for x in analyses:
   g=clean(str(x.get('stemgloss','')))
   if good(g):cal=g;root=ar.root_to_arabic(str(x.get('root','')),pos,bw);break
  if not cal:rej.append({'front':front,'frequency':r.get('frequency',''),'reason':'no_safe_exact_calima_semantics'});continue
  kg=kk.get(front,'');og=omw_evidence(front,net)
  ck=bool(kg and agree(cal,kg));co=bool(og and agree(cal,og));ko=bool(kg and og and agree(kg,og))
  if ck or co:
   meaning=cal;basis='calima+kaikki' if ck and not co else 'calima+omw' if co and not ck else 'calima+kaikki+omw'
  elif ko:
   meaning=clean(kg);basis='kaikki+omw'
  else:
   rej.append({'front':front,'frequency':r.get('frequency',''),'reason':'no_cross_source_semantic_agreement','calima_meaning':cal,'kaikki_meaning':kg,'omw_evidence':og[:400]});continue
  if not good(meaning):continue
  seen.add(front);rows.append({'rank':1001+len(rows),'front':front,'meaning':meaning,'pos':pos,'root':root,'frequency':r.get('frequency',''),'calima_meaning':cal,'kaikki_meaning':kg,'omw_evidence':og[:1200],'calima_kaikki_agreement':ck,'calima_omw_agreement':co,'kaikki_omw_agreement':ko,'semantic_basis':basis,'source':'CAMeL MSA frequency ranking; exact CALIMA morphology; Kaikki/OMW cross-source semantics'})
  if len(rows)>=TARGET:break
 fields=list(rows[0]);
 with (AUDIT/'arabic_top3000_continuation_evidence_v2.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 with (AUDIT/'arabic_top3000_candidate_v2.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
  for x in rows:
   lines=[f"Rank: {x['rank']}",'',f"Meaning: {x['meaning']}",'',f"Part of speech: {x['pos']}"]
   if x['root']:lines+=['',f"Root: {x['root']}"]
   lines+=['',f"Frequency evidence: {x['frequency']}",'',f"Semantic verification: {x['semantic_basis']}",'','Sources:','- CAMeL MSA frequency lists — rank candidate authority','- CALIMA-MSA r13 — exact morphology/stem semantics','- Kaikki/Wiktextract and Open Multilingual Wordnet — independent semantic corroboration','- Candidate only; requires final audit before promotion']
   w.writerow({'Front':x['front'],'Back':'\n'.join(lines)})
 rfields=sorted({k for x in rej for k in x}) if rej else ['front','reason']
 with (AUDIT/'arabic_top3000_rejections_v2.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=rfields);w.writeheader();w.writerows(rej)
 s={'rows':len(rows),'expected_rows':2000,'distinct_fronts':len(seen),'rank_range':[1001,3000],'rejected_before_target':len(rej),'semantic_basis_counts':{b:sum(x['semantic_basis']==b for x in rows) for b in sorted({x['semantic_basis'] for x in rows})},'structural_gate':'PASS' if len(rows)==2000 and len(seen)==2000 else 'FAIL','status':'candidate_only_not_promoted'}
 (AUDIT/'arabic_top3000_candidate_v2_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))
 if s['structural_gate']!='PASS':raise SystemExit('not enough cross-source verified Arabic continuation items')
if __name__=='__main__':main()
