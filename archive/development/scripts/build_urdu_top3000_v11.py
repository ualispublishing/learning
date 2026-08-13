#!/usr/bin/env python3
"""Consensus-ranked publication candidate for Urdu ranks 1001..3000.

The public gloss is chosen from atomic senses shared by independent bilingual
sources, not from raw dictionary order. Wordfreq provides Unicode Urdu ordering and
also a small English-frequency tie-break so everyday shared senses outrank obscure
technical/historical ones. Inflected verb forms are handled separately so the exposed
gloss reflects the surface form rather than a homographic noun.
"""
from __future__ import annotations
import argparse,csv,json,re,sys
from pathlib import Path
from word2word import Word2word
from wordfreq import top_n_list,zipf_frequency
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_french_urdu_core_candidates_v2 as fu
AUDIT=ROOT/'audit';TARGET=2000
URDU=re.compile(r'[\u0600-\u06ff]');DEV=re.compile(r'[\u0900-\u097f]')
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used','use','anything'}
GRAMMAR={'intransitive','transitive','participle','inflection','vocative','oblique','singular','plural'}
RAW_MARK=re.compile(r'\b(?:Platts|s\.m\.|s\.f\.|interj\.|infinitive of|inflection of|form of|plural of|singular of|masculine of|feminine of|only used in)\b',re.I)
INFLECT_MARK=re.compile(r'\b(?:inflection of|masculine of|feminine of|plural perfective|perfective|went \(plural\)|came \(plural\)|took \(|does \(|gives \(|kept \(|saw \(|made, built \()\b',re.I)

def clean(s):return re.sub(r'\s+',' ',(s or '').replace('_',' ')).strip(' ;,."')
def stem(w):
 w=w.lower().strip("'-")
 if len(w)>5 and w.endswith('iness'):return w[:-5]+'y'
 if len(w)>5 and w.endswith('iness'):return w[:-5]+'y'
 for suf in ('ingly','ments','ment','ation','ities','ity','ness','ingly','ing','ied','ed','es','s'):
  if len(w)>len(suf)+3 and w.endswith(suf):
   base=w[:-len(suf)]
   if suf=='ied':base+='y'
   return base
 return w
def toks(s):
 out=[]
 for w in WORD.findall(s or ''):
  q=stem(w)
  if q not in STOP and len(q)>1:out.append(q)
 return out
def related(a,b):
 ta,tb=set(toks(a)),set(toks(b))
 if ta&tb:return True
 for x in ta:
  for y in tb:
   if min(len(x),len(y))>=4 and (x.startswith(y) or y.startswith(x)):return True
 return False
def atoms(text):
 t=clean(text)
 if not t:return []
 if ' | Platts:' in t:t=t.split(' | Platts:',1)[0]
 # Rescue gloss after em-dash definitions before stripping Urdu-script source notes.
 rescued=[]
 for m in re.finditer(r'[—–-]\s*to\s+([^)]{2,100})',t,re.I):rescued.extend(re.split(r'\s*[,;/]\s*',m.group(1)))
 t=re.sub(r'\([^)]*\)',' ',t);t=re.sub(r'\([^)]*$',' ',t)
 t=re.sub(r'\b(?:name|phrase|n|v|adj|adv)\s*:\s*',' ',t,flags=re.I)
 t=re.sub(r'\b(?:s\.m\.|s\.f\.|n\.|v\.|adj\.|adv\.|interj\.)\s*',' ',t,flags=re.I)
 parts=rescued+re.split(r'\s*[;|]\s*|\s*,\s*',t)
 out=[]
 for i,p in enumerate(parts):
  p=clean(p)
  p=re.sub(r'^(?:rt\.[^,;]*,?\s*)','',p,flags=re.I)
  if not p or URDU.search(p) or DEV.search(p) or RAW_MARK.search(p):continue
  if len(p)>65 or not toks(p):continue
  if all(x in GRAMMAR for x in toks(p)):continue
  key=p.casefold()
  if key not in {x.casefold() for x in out}:out.append(p)
 return out[:30]
def source_texts(word,kk,read,w2):
 ko=kk.get(word,{})
 kg=clean(fu.compact_meaning(ko.get('all_glosses',[]))) if ko else ''
 rg=clean(read.get(word,{}).get('meaning','')) if word in read else ''
 try:wl=w2(word) or []
 except Exception:wl=[]
 wg='; '.join(dict.fromkeys(clean(str(x)) for x in wl[:12] if clean(str(x))))
 return kg,rg,wg
def english_commonness(s):
 ts=[w.lower() for w in WORD.findall(s) if w.lower() not in STOP]
 if not ts:return 0.0
 return max(zipf_frequency(w,'en') for w in ts)
def first_word2word_match(wg,dict_texts):
 for w in atoms(wg)[:6]:
  if len(w)>30:continue
  if any(related(w,d) for text in dict_texts for d in atoms(text)):
   return w
 return ''
def consensus_atoms(kg,rg,wg):
 src={'Kaikki':atoms(kg),'ReadUrdu':atoms(rg),'word2word':atoms(wg)}
 candidates=[]
 for sname,vals in src.items():
  for pos,v in enumerate(vals):
   supporters=[];best_positions=[]
   for oname,ovals in src.items():
    if oname==sname:continue
    matches=[(j,o) for j,o in enumerate(ovals) if related(v,o)]
    if matches:
     supporters.append(oname);best_positions.append(min(j for j,_ in matches))
   if not supporters:continue
   # dictionary-origin candidates are preferred over raw corpus translations;
   # everyday English frequency breaks ties among equally corroborated senses.
   dict_bonus=1.2 if sname in ('Kaikki','ReadUrdu') else 0
   support_bonus=3.0*len(supporters)
   position_penalty=.18*(pos+sum(best_positions))
   common_bonus=.42*english_commonness(v)
   length_penalty=.015*len(v)
   score=support_bonus+dict_bonus+common_bonus-position_penalty-length_penalty
   candidates.append((score,sname,v,[sname]+supporters))
 candidates.sort(key=lambda x:x[0],reverse=True)
 return candidates
def make_gloss(word,kg,rg,wg):
 # Surface-form inflections: use a simple corpus translation that is explicitly
 # corroborated anywhere in a dictionary entry, avoiding noun homographs.
 if INFLECT_MARK.search(rg):
  w=first_word2word_match(wg,[rg,kg])
  if w and len(w.split())<=3:return w,['word2word','ReadUrdu']
 cands=consensus_atoms(kg,rg,wg)
 if not cands:return '',[]
 chosen=[];support=set()
 for score,sname,v,sups in cands:
  if RAW_MARK.search(v) or URDU.search(v):continue
  # If a one-word corpus gloss is embedded in a longer dictionary phrase, prefer
  # the simple corpus term (e.g. کالی -> black rather than "a black woman").
  simple=first_word2word_match(wg,[v])
  if simple and len(simple.split())<=2 and related(simple,v):v=simple;sups=list(set(sups+['word2word']))
  # Avoid adding near-duplicates.
  if any(related(v,x) and (set(toks(v))<=set(toks(x)) or set(toks(x))<=set(toks(v))) for x in chosen):continue
  if len(v)>55:continue
  chosen.append(v);support.update(sups)
  if len(chosen)>=3:break
 if not chosen:return '',[]
 gloss='; '.join(chosen)
 gloss=re.sub(r'\b(?:s\.m\.|s\.f\.|n\.|v\.|adj\.|adv\.|interj\.)\s*','',gloss,flags=re.I)
 gloss=clean(gloss)
 if len(gloss)>140 or RAW_MARK.search(gloss) or URDU.search(gloss):return '',[]
 return gloss,sorted(support)
def top1000():
 with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kaikki',required=True);ap.add_argument('--readurdu',required=True);a=ap.parse_args()
 kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur);read=fu.read_readurdu(Path(a.readurdu));w2=Word2word('ur','en')
 excluded=top1000();seen=set();rows=[];rej=[];examined=0
 for raw in top_n_list('ur',150000):
  if len(rows)>=TARGET:break
  examined+=1;word=fu.norm_ur(raw)
  if not word or word in excluded or word in seen or re.search(r'\s',word) or not URDU.search(word) or DEV.search(word):continue
  kg,rg,wg=source_texts(word,kk,read,w2);gloss,support=make_gloss(word,kg,rg,wg)
  if len(set(support))<2 or not gloss:
   rej.append({'front':word,'zipf':f'{zipf_frequency(word,"ur"):.2f}','reason':'no_clean_two_source_consensus'});continue
  seen.add(word);rows.append({'rank':1001+len(rows),'front':word,'meaning':gloss,'wordfreq_zipf':f'{zipf_frequency(word,"ur"):.2f}','semantic_support':'+'.join(support),'kaikki_meaning':kg,'readurdu_meaning':rg,'word2word_meaning':wg})
 fields=list(rows[0]) if rows else ['rank','front','meaning']
 with (AUDIT/'urdu_top3000_continuation_evidence_v11.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 with (AUDIT/'urdu_top3000_candidate_v11.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
  for r in rows:
   back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: wordfreq Zipf {r['wordfreq_zipf']}",'Frequency source: wordfreq Urdu multi-corpus ranking','',f"Semantic verification: independent consensus — {r['semantic_support']}",'','Sources:','- wordfreq Urdu — Unicode multi-corpus frequency ordering','- Kaikki/Wiktextract — bilingual lexicographic evidence','- ReadUrdu — independent Urdu-English bilingual evidence','- word2word — independent corpus-derived bilingual evidence'])
   w.writerow({'Front':r['front'],'Back':back})
 with (AUDIT/'urdu_top3000_rejections_v11.csv').open('w',encoding='utf-8',newline='') as f:fs=['front','zipf','reason'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rej)
 bad=[r for r in rows if len(r['meaning'])>140 or RAW_MARK.search(r['meaning']) or URDU.search(r['meaning'])]
 summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'wordfreq_candidates_examined':examined,'public_gloss_violations':len(bad),'all_rows_two_source_supported':all(len(set(r['semantic_support'].split('+')))>=2 for r in rows),'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET and not bad else 'FAIL','status':'candidate_only_not_promoted','policy':'Unicode wordfreq ordering; atomic cross-source consensus; everyday shared senses outrank obscure senses; surface-form inflections receive surface-form glosses.'}
 (AUDIT/'urdu_top3000_candidate_v11_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
 if summary['structural_gate']!='PASS':raise SystemExit('v11 gate failed')
if __name__=='__main__':main()
