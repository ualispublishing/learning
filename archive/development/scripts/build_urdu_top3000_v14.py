#!/usr/bin/env python3
"""Modern-corroborated single-sense Urdu continuation for public release.

Ordinary public senses must originate in a clean dictionary entry AND be corroborated
by word2word's modern corpus-derived bilingual signal. Two-dictionary-only consensus
is retained only for unmistakable proper names / named entities, preventing valid but
archaic homographs from displacing modern high-frequency senses.
"""
from __future__ import annotations
import argparse,csv,json,re,sys
from pathlib import Path
from word2word import Word2word
from wordfreq import top_n_list,zipf_frequency
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_french_urdu_core_candidates_v2 as fu
AUDIT=ROOT/'audit';TARGET=2000
URDU=re.compile(r'[\u0600-\u06ff]');DEV=re.compile(r'[\u0900-\u097f]');WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used','use','anything'}
RAW=re.compile(r'\b(?:Platts|s\.m\.|s\.f\.|interj\.|infinitive of|inflection of|form of|plural of|singular of|masculine of|feminine of|only used in|q\.v\.)\b',re.I)
INFLECT=re.compile(r'\b(?:infinitive|inflection|perfective|masculine of|feminine of|plural masculine|plural perfective|singular perfective)\b',re.I)
LEGACY_START=re.compile(r'^\s*(?:\(|s\.[mf]\.|adj\.|adv\.|v\.|n\.|interj\.)',re.I)
BAD_CONCEPT={'intransitive','transitive','participle','inflection','vocative','oblique','singular','plural'}
PUBLIC_OVERRIDES={'اردو':'Urdu language','محمد':'Muhammad','عمران':'Imran','عادت':'habit','معذرت':'apology'}
SAFE_NAMED={'اردو','قرآن'}
def clean(s):return re.sub(r'\s+',' ',(s or '').replace('_',' ')).strip(' ;,."')
def stem(w):
 w=w.lower().strip("'-")
 if len(w)>5 and w.endswith('ies'):return w[:-3]+'y'
 for suf in ('ingly','ations','ation','ments','ment','ness','ities','ity','ingly','ing','ied','ed','es','s','al'):
  if len(w)>len(suf)+3 and w.endswith(suf):
   b=w[:-len(suf)];return b+'y' if suf=='ied' else b
 return w
def toks(s):return [stem(w) for w in WORD.findall(s or '') if stem(w) not in STOP and len(stem(w))>1]
def related(a,b):
 ta,tb=set(toks(a)),set(toks(b))
 if not ta or not tb:return False
 if ta==tb:return True
 if len(ta)==1 and len(tb)==1:
  x,y=next(iter(ta)),next(iter(tb));return min(len(x),len(y))>=4 and (x.startswith(y) or y.startswith(x))
 return False
def atoms(text):
 t=clean(text)
 if not t:return []
 if ' | Platts:' in t:t=t.split(' | Platts:',1)[0]
 rescued=[]
 for m in re.finditer(r'[—–-]\s*to\s+([^)]{2,100})',t,re.I):rescued.extend(re.split(r'\s*[,;/]\s*',m.group(1)))
 t=re.sub(r'\([^)]*\)',' ',t);t=re.sub(r'\([^)]*$',' ',t)
 t=re.sub(r'\b(?:name|phrase|n|v|adj|adv)\s*:\s*',' ',t,flags=re.I)
 t=re.sub(r'\b(?:s\.m\.|s\.f\.|n\.|v\.|adj\.|adv\.|interj\.)\s*',' ',t,flags=re.I)
 parts=rescued+re.split(r'\s*[;|]\s*|\s*,\s*',t)
 out=[]
 for p in parts:
  p=clean(p);p=re.sub(r'^rt\.[^,;]*,?\s*','',p,flags=re.I)
  if not p or URDU.search(p) or DEV.search(p) or RAW.search(p) or len(p)>48:continue
  tt=toks(p)
  if not tt or all(x in BAD_CONCEPT for x in tt) or len(WORD.findall(p))>3:continue
  if p.casefold() not in {x.casefold() for x in out}:out.append(p)
 return out[:25]
def source_texts(word,kk,read,w2):
 ko=kk.get(word,{})
 kg=clean(fu.compact_meaning(ko.get('all_glosses',[]))) if ko else ''
 rg=clean(read.get(word,{}).get('meaning','')) if word in read else ''
 try:wl=w2(word) or []
 except Exception:wl=[]
 wg='; '.join(dict.fromkeys(clean(str(x)) for x in wl[:10] if clean(str(x))))
 return kg,rg,wg
def engfreq(s):
 ws=[w.lower() for w in WORD.findall(s) if w.lower() not in STOP]
 return max([zipf_frequency(w,'en') for w in ws] or [0])
def candidates(kg,rg,wg):
 src={'Kaikki':atoms(kg),'ReadUrdu':atoms(rg),'word2word':atoms(wg)};out=[]
 for sname in ('Kaikki','ReadUrdu'):
  for i,v in enumerate(src[sname]):
   supporters=[];poss=[]
   for oname in ('Kaikki','ReadUrdu','word2word'):
    if oname==sname:continue
    mm=[j for j,o in enumerate(src[oname]) if related(v,o)]
    if mm:supporters.append(oname);poss.append(min(mm))
   if not supporters:continue
   score=5*len(supporters)+engfreq(v)-.22*(i+sum(poss))-.01*len(v)
   out.append((score,v,sorted(set([sname]+supporters))))
 out.sort(reverse=True,key=lambda x:x[0]);ded=[]
 for z in out:
  if any(related(z[1],x[1]) for x in ded):continue
  ded.append(z)
 return ded
def inflected(rg,wg):
 if not INFLECT.search(rg):return ''
 ra,wa=atoms(rg),atoms(wg)
 for w in wa[:6]:
  if len(WORD.findall(w))<=2 and any(related(w,r) for r in ra):return w
 return ''
def proper_like(gloss):
 # Proper-name glosses are title-cased / capitalized and short; ordinary English
 # sentence starts such as "The half" are excluded.
 if not gloss or gloss.startswith('The '):return False
 ws=WORD.findall(gloss)
 return 1<=len(ws)<=3 and ws[0][0].isupper() and not gloss.isupper()
def make_gloss(word,kg,rg,wg):
 iv=inflected(rg,wg)
 if iv:return iv.lower() if iv.isupper() else iv,['ReadUrdu','word2word']
 c=candidates(kg,rg,wg)
 if not c:return '',[]
 # Choose the best dictionary-origin candidate that has a modern corpus witness.
 modern=[z for z in c if 'word2word' in z[2]]
 pool=modern or c
 _,v,support=pool[0]
 if len(v)>45 or RAW.search(v) or URDU.search(v):return '',[]
 if set(support)=={'ReadUrdu','word2word'} and not kg and LEGACY_START.search(rg):return '',[]
 if 'word2word' not in support and word not in SAFE_NAMED and not proper_like(v):return '',[]
 if word in PUBLIC_OVERRIDES:
  ov=PUBLIC_OVERRIDES[word]
  if any(related(ov,x) for x in atoms(kg)+atoms(rg)+atoms(wg)):v=ov
 if v.isupper():v=v.lower()
 return clean(v),support
def top1000():
 with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kaikki',required=True);ap.add_argument('--readurdu',required=True);a=ap.parse_args()
 kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur);read=fu.read_readurdu(Path(a.readurdu));w2=Word2word('ur','en')
 excluded=top1000();seen=set();rows=[];rej=[];examined=0
 for raw in top_n_list('ur',300000):
  if len(rows)>=TARGET:break
  examined+=1;word=fu.norm_ur(raw)
  if not word or word in excluded or word in seen or re.search(r'\s',word) or not URDU.search(word) or DEV.search(word):continue
  kg,rg,wg=source_texts(word,kk,read,w2);gloss,support=make_gloss(word,kg,rg,wg)
  if not gloss or len(set(support))<2:
   rej.append({'front':word,'zipf':f'{zipf_frequency(word,"ur"):.2f}','reason':'no_modern_corroborated_core_sense'});continue
  seen.add(word);rows.append({'rank':1001+len(rows),'front':word,'meaning':gloss,'wordfreq_zipf':f'{zipf_frequency(word,"ur"):.2f}','semantic_support':'+'.join(support),'kaikki_meaning':kg,'readurdu_meaning':rg,'word2word_meaning':wg})
 fields=list(rows[0]) if rows else ['rank','front','meaning']
 with (AUDIT/'urdu_top3000_continuation_evidence_v14.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 with (AUDIT/'urdu_top3000_candidate_v14.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
  for r in rows:
   back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: wordfreq Zipf {r['wordfreq_zipf']}",'Frequency source: wordfreq Urdu multi-corpus ranking','',f"Semantic verification: modern-corroborated core sense — {r['semantic_support']}",'','Sources:','- wordfreq Urdu — Unicode multi-corpus frequency ordering','- Kaikki/Wiktextract — bilingual lexicographic evidence','- ReadUrdu — independent Urdu-English bilingual evidence','- word2word — modern corpus-derived bilingual corroboration'])
   w.writerow({'Front':r['front'],'Back':back})
 with (AUDIT/'urdu_top3000_rejections_v14.csv').open('w',encoding='utf-8',newline='') as f:fs=['front','zipf','reason'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rej)
 bad=[r for r in rows if len(r['meaning'])>45 or RAW.search(r['meaning']) or URDU.search(r['meaning']) or len(WORD.findall(r['meaning']))>3]
 summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'wordfreq_candidates_examined':examined,'public_gloss_violations':len(bad),'all_rows_two_source_supported':all(len(set(r['semantic_support'].split('+')))>=2 for r in rows),'rows_with_word2word_support':sum('word2word' in r['semantic_support'] for r in rows),'two_dictionary_named_exceptions':sum('word2word' not in r['semantic_support'] for r in rows),'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET and not bad else 'FAIL','status':'candidate_only_not_promoted','policy':'One concise dictionary-origin core sense; ordinary meanings require word2word modern-corpus corroboration; two-dictionary-only exceptions limited to proper/named terms; Unicode wordfreq ordering.'}
 (AUDIT/'urdu_top3000_candidate_v14_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
 if summary['structural_gate']!='PASS':raise SystemExit('v14 gate failed')
if __name__=='__main__':main()
