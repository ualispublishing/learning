#!/usr/bin/env python3
"""Publication-clean Urdu 1001..3000 candidate.

Requirements for every row:
1. Unicode Urdu frequency ordering from wordfreq (no legacy PDF extraction).
2. At least two independent bilingual sources agree.
3. The exposed English gloss is a concise learner meaning, not dictionary metadata,
   inflection prose, source markup, or an unbalanced/truncated definition.
"""
from __future__ import annotations
import argparse,csv,json,re,sys
from pathlib import Path
from word2word import Word2word
from wordfreq import top_n_list,zipf_frequency
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_french_urdu_core_candidates_v2 as fu
AUDIT=ROOT/'audit';TARGET=2000
WORD=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?");URDU=re.compile(r'[\u0600-\u06ff]');DEV=re.compile(r'[\u0900-\u097f]')
STOP={'a','an','the','to','of','and','or','for','as','be','is','are','was','were','with','by','from','that','which','who','this','it','he','she','they','you','i','we','one','ones','someone','something','having','used','use'}
META_RE=re.compile(r'^(?:form|inflection|inflected|plural|singular|oblique|vocative|masculine|feminine|formal plural|only used|phrase only used)\b',re.I)
BAD_PUBLIC=re.compile(r'\b(?:Platts|infinitive of|form of|plural of|singular of|masculine of|feminine of|only used in)\b',re.I)

def clean(t):return ' '.join((t or '').replace('_',' ').split()).strip(' ;,."')
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
def safe_text(t,limit=400):
 x=clean(t)
 if not x or len(x)>limit or DEV.search(x) or any(c in x for c in '[]<>'):return ''
 return x
def safe_read(t):
 x=clean(t)
 if not x:return ''
 m=DEV.search(x)
 # Keep text before Devanagari contamination, but Urdu script is legitimate inside source notes.
 if m:x=x[:m.start()].strip(' ;,|')
 if ' | also:' in x:x=x.split(' | also:',1)[0]
 if ' | Platts:' in x:x=x.split(' | Platts:',1)[0]
 return clean(x)[:300]
def source_fragments(text):
 t=clean(text)
 if not t:return []
 # If a grammatical source note contains an em-dash definition, rescue the actual gloss.
 rescued=[]
 for m in re.finditer(r'[—–-]\s*to\s+([^)]{2,100})',t,re.I):
  rescued.extend(re.split(r'\s*[,;/]\s*',m.group(1)))
 # Remove balanced and then unmatched parentheticals from exposed candidate fragments.
 t=re.sub(r'\([^)]*\)',' ',t)
 t=re.sub(r'\([^)]*$',' ',t)
 t=re.sub(r'\b(?:name|phrase|n|v|adj|adv)\s*:\s*',' ',t,flags=re.I)
 t=re.sub(r'\b(?:n|v|adj|adv)\.\s*',' ',t,flags=re.I)
 raw=rescued+re.split(r'\s*[;|]\s*|\s*,\s*',t)
 out=[]
 for p in raw:
  p=clean(p)
  p=re.sub(r'^(?:said|told|made|built|took|went|came|does|can)\s+\((?:[^)]*)\)$',lambda m:m.group(0).split(' (',1)[0],p,flags=re.I)
  # Convert common inline parenthetical morphology already stripped by keeping the core before it.
  if META_RE.match(p):continue
  if BAD_PUBLIC.search(p):continue
  if not p or len(p)>75 or not toks(p):continue
  if URDU.search(p):continue
  if p.casefold() not in {x.casefold() for x in out}:out.append(p)
 return out

def public_gloss(primary,corroborators):
 frags=source_fragments(primary);hits=[]
 for p in frags:
  if any(agree(p,o) for o in corroborators if o):hits.append(p)
 # If metadata stripping removed the obvious surface core, recover simple leading phrase.
 if not hits:
  lead=clean(re.sub(r'\([^)]*\)|\([^)]*$',' ',primary)).split('|',1)[0]
  for p in re.split(r'\s*[;,]\s*',lead):
   p=clean(p)
   if p and len(p)<=60 and not META_RE.match(p) and not BAD_PUBLIC.search(p) and not URDU.search(p) and any(agree(p,o) for o in corroborators if o):hits.append(p)
 out=[]
 for p in hits:
  if p.casefold() not in {x.casefold() for x in out}:out.append(p)
 meaning='; '.join(out[:4])
 if not meaning or len(meaning)>150 or BAD_PUBLIC.search(meaning) or URDU.search(meaning):return ''
 if meaning.count('(')!=meaning.count(')'):return ''
 return meaning

def top1000():
 with (ROOT/'urdu_top1000.csv').open(encoding='utf-8-sig',newline='') as f:return {fu.norm_ur((r.get('Front') or '').strip()) for r in csv.DictReader(f)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kaikki',required=True);ap.add_argument('--readurdu',required=True);a=ap.parse_args()
 kk=fu.load_kaikki(Path(a.kaikki),fu.norm_ur);read=fu.read_readurdu(Path(a.readurdu));w2=Word2word('ur','en')
 excluded=top1000();seen=set();rows=[];rej=[];examined=0
 def vals(word):
  ko=kk.get(word,{})
  kg=safe_text(fu.compact_meaning(ko.get('all_glosses',[])),380) if ko else ''
  rg=safe_read(read.get(word,{}).get('meaning','')) if word in read else ''
  try:wl=w2(word) or []
  except Exception:wl=[]
  wg=safe_text('; '.join(dict.fromkeys(str(x) for x in wl[:12])),380)
  return kg,rg,wg
 for raw in top_n_list('ur',120000):
  if len(rows)>=TARGET:break
  examined+=1;word=fu.norm_ur(raw)
  if not word or word in excluded or word in seen or re.search(r'\s',word) or not URDU.search(word) or DEV.search(word):continue
  kg,rg,wg=vals(word);kr=bool(kg and rg and agree(kg,rg));kw=bool(kg and wg and agree(kg,wg));rw=bool(rg and wg and agree(rg,wg))
  if not(kr or kw or rw):rej.append({'front':word,'zipf':f'{zipf_frequency(word,"ur"):.2f}','reason':'no_two_source_agreement'});continue
  choices=[]
  if kr or kw:
   os=([rg] if kr else [])+([wg] if kw else []);g=public_gloss(kg,os)
   if g:choices.append((g,['Kaikki']+(['ReadUrdu'] if kr else [])+(['word2word'] if kw else [])))
  if rw:
   g=public_gloss(rg,[wg])
   if g:choices.append((g,['ReadUrdu','word2word']))
  if not choices:rej.append({'front':word,'zipf':f'{zipf_frequency(word,"ur"):.2f}','reason':'agreement_but_no_clean_public_gloss'});continue
  # Prefer the shortest independently supported gloss; this intentionally drops obscure extra senses.
  meaning,support=min(choices,key=lambda x:(len(x[0]),x[0].count(';')))
  seen.add(word);rows.append({'rank':1001+len(rows),'front':word,'meaning':meaning,'wordfreq_zipf':f'{zipf_frequency(word,"ur"):.2f}','semantic_support':'+'.join(support),'kaikki_readurdu_agree':kr,'kaikki_word2word_agree':kw,'readurdu_word2word_agree':rw,'kaikki_meaning':kg,'readurdu_meaning':rg,'word2word_meaning':wg})
 fields=list(rows[0]) if rows else ['rank','front','meaning']
 with (AUDIT/'urdu_top3000_continuation_evidence_v10.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 with (AUDIT/'urdu_top3000_candidate_v10.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back']);w.writeheader()
  for r in rows:
   back='\n'.join([f"Rank: {r['rank']}",'',f"Meaning: {r['meaning']}",'',f"Frequency evidence: wordfreq Zipf {r['wordfreq_zipf']}",'Frequency source: wordfreq Urdu multi-corpus ranking','',f"Semantic verification: independent agreement — {r['semantic_support']}",'','Sources:','- wordfreq Urdu — Unicode multi-corpus frequency ordering','- Kaikki/Wiktextract — bilingual lexicographic evidence','- ReadUrdu — independent Urdu-English bilingual evidence','- word2word — independent corpus-derived bilingual evidence'])
   w.writerow({'Front':r['front'],'Back':back})
 with (AUDIT/'urdu_top3000_rejections_v10.csv').open('w',encoding='utf-8',newline='') as f:fs=['front','zipf','reason'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rej)
 bad=[r for r in rows if len(r['meaning'])>150 or BAD_PUBLIC.search(r['meaning']) or URDU.search(r['meaning']) or r['meaning'].count('(')!=r['meaning'].count(')')]
 summary={'rows':len(rows),'expected_rows':TARGET,'distinct_fronts':len(seen),'rank_range':[1001,1000+len(rows)] if rows else [],'wordfreq_candidates_examined':examined,'public_gloss_violations':len(bad),'all_rows_two_source_supported':all(r['semantic_support'] for r in rows),'structural_gate':'PASS' if len(rows)==TARGET and len(seen)==TARGET and not bad else 'FAIL','status':'candidate_only_not_promoted','policy':'Unicode wordfreq ordering; two independent bilingual sources per row; concise metadata-free public English gloss required.'}
 (AUDIT/'urdu_top3000_candidate_v10_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
 if summary['structural_gate']!='PASS':raise SystemExit('v10 publication gate failed')
if __name__=='__main__':main()
