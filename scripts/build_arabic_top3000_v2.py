#!/usr/bin/env python3
"""Build a precision-gated Arabic rank-1001..3000 continuation.

Rank candidates come from the broad CAMeL MSA frequency inventory. The live
verified top-1000 is excluded. A continuation item is admitted only when an exact
CALIMA analysis has learner semantics independently corroborated by Kaikki/
Wiktextract. When CALIMA lists several senses, only the sense fragments that agree
with Kaikki are retained. This intentionally skips high-frequency abbreviation and
wrong-sense noise instead of forcing a dubious card.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
from wordfreq import zipf_frequency
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.morphology.database import MorphologyDB
from camel_tools.utils.charmap import CharMapper
import build_french_urdu_core_candidates_v2 as fu
import build_arabic_top1000_precision as ar
ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'; TARGET=2000
WORD=re.compile(r"[A-Za-z][A-Za-z'\-]*")
STOP={'a','an','the','to','of','in','on','at','for','from','by','with','and','or','as','is','are','was','were','be','been','being','one','that','this','which','who','whom','something','someone','used','use','form','forms','person','thing','things','depending','context','noun','verb','adjective','adverb'}
SENSE_SPLIT=re.compile(r"\s*(?:;|/|\|)\s*")
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
def split_senses(t):
 return [clean(x) for x in SENSE_SPLIT.split(t or '') if good(x)]
def corroborated_calima(cal,external):
 parts=[]
 for part in split_senses(cal):
  if agree(part,external) and part not in parts:parts.append(part)
 if not parts and agree(cal,external):
  parts=[clean(cal)]
 return '; '.join(parts[:5])
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
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--broad',required=True);ap.add_argument('--kaikki',required=True);a=ap.parse_args()
 with (ROOT/'arabic_top1000.csv').open(encoding='utf-8-sig',newline='') as f:excluded={ar.undiac((r.get('Front') or '')).strip() for r in csv.DictReader(f)}
 with Path(a.broad).open(encoding='utf-8',newline='') as f:broad=list(csv.DictReader(f))
 targets=[]
 for r in broad:
  w=ar.undiac(r.get('front','')).strip()
  if w and w not in excluded and len(w)>=2:targets.append(w)
 kk=load_kaikki(Path(a.kaikki),set(targets))
 an=Analyzer(MorphologyDB.builtin_db('calima-msa-r13',flags='a'),backoff='NONE',cache_size=40000);bw=CharMapper.builtin_mapper('bw2ar')
 rows=[];rej=[];seen=set()
 for r in broad:
  front=ar.undiac(r.get('front','')).strip();pos=(r.get('pos') or '').strip()
  if not front or front in excluded or front in seen or len(front)<2:continue
  if zipf_frequency(front,'ar')<=0:continue
  kg=kk.get(front,'')
  if not kg:
   rej.append({'front':front,'frequency':r.get('frequency',''),'reason':'no_kaikki_semantic_entry'});continue
  analyses=[x for x in an.analyze(front) if ar.exact_lexical_match(front,x) and str(x.get('pos',''))==pos];analyses.sort(key=ar.score,reverse=True)
  chosen='';cal_raw='';root=''
  for x in analyses:
   g=clean(str(x.get('stemgloss','')))
   if not good(g):continue
   narrowed=corroborated_calima(g,kg)
   if narrowed:
    chosen=narrowed;cal_raw=g;root=ar.root_to_arabic(str(x.get('root','')),pos,bw);break
  if not chosen:
   rej.append({'front':front,'frequency':r.get('frequency',''),'reason':'no_calima_kaikki_semantic_agreement','kaikki_meaning':kg});continue
  if not good(chosen):continue
  seen.add(front);rows.append({'rank':1001+len(rows),'front':front,'meaning':chosen,'pos':pos,'root':root,'frequency':r.get('frequency',''),'calima_raw_meaning':cal_raw,'kaikki_meaning':kg,'semantic_basis':'exact CALIMA sense fragment + Kaikki agreement','source':'CAMeL MSA frequency ranking; exact CALIMA morphology; Kaikki/Wiktextract independent semantics'})
  if len(rows)>=TARGET:break
 if rows:
  fields=list(rows[0])
 else:
  fields=['rank','front','meaning','pos','root','frequency','calima_raw_meaning','kaikki_meaning','semantic_basis','source']
 with (AUDIT/'arabic_top3000_continuation_evidence_v2.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 with (AUDIT/'arabic_top3000_candidate_v2.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
  for x in rows:
   lines=[f"Rank: {x['rank']}",'',f"Meaning: {x['meaning']}",'',f"Part of speech: {x['pos']}"]
   if x['root']:lines+=['',f"Root: {x['root']}"]
   lines+=['',f"Frequency evidence: {x['frequency']}",'',f"Semantic verification: {x['semantic_basis']}",'','Sources:','- CAMeL MSA frequency lists — rank candidate authority','- CALIMA-MSA r13 — exact morphology/stem semantics','- Kaikki/Wiktextract — independent semantic corroboration','- Candidate only; requires final audit before promotion']
   w.writerow({'Front':x['front'],'Back':'\n'.join(lines)})
 rfields=sorted({k for x in rej for k in x}) if rej else ['front','reason']
 with (AUDIT/'arabic_top3000_rejections_v2.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=rfields);w.writeheader();w.writerows(rej)
 s={'rows':len(rows),'expected_rows':2000,'distinct_fronts':len(seen),'rank_range':[1001,3000] if len(rows)==2000 else [1001,1000+len(rows)],'rejected_before_target':len(rej),'semantic_basis_counts':{'exact_calima_plus_kaikki':len(rows)},'structural_gate':'PASS' if len(rows)==2000 and len(seen)==2000 else 'FAIL','status':'candidate_only_not_promoted','policy':'Only CALIMA sense fragments independently corroborated by Kaikki are retained; unsupported higher-frequency rows are skipped.'}
 (AUDIT/'arabic_top3000_candidate_v2_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))
 if s['structural_gate']!='PASS':raise SystemExit('not enough cross-source verified Arabic continuation items')
if __name__=='__main__':main()
