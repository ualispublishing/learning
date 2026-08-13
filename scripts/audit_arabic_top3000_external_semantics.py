#!/usr/bin/env python3
"""Independent Kaikki + OMW semantic audit for Arabic ranks 1001-3000.

The workflow also applies a narrow set of educator-confirmed modern-sense repairs
to the live continuation. Repairs are rank/front/current-meaning guarded and the
live rank sequence is rechecked before the CSV is staged for the workflow's
normal evidence commit.
"""
from __future__ import annotations
import csv, json, re, subprocess, unicodedata
from pathlib import Path
import wn
from wordfreq import zipf_frequency

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit'
TARGET=AUDIT/'arabic_top3000_candidate.csv'; EVID=AUDIT/'arabic_top3000_continuation_evidence.csv'
LIVE=ROOT/'arabic_top3000.csv'; REPAIR_DATA=AUDIT/'arabic_top3000_confirmed_modern_repairs.json'
DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]'); WORD=re.compile(r"[A-Za-z][A-Za-z'\-]*")
SPLIT=re.compile(r'\s*(?:;|/|\||,)\s*')
STOP={'a','an','the','to','of','in','on','at','for','from','by','with','and','or','as','is','are','was','were','be','been','being','one','that','this','which','who','whom','something','someone','used','use','form','forms','person','thing','things','depending','context','noun','verb','adjective','adverb','preposition','conjunction'}
RANK_RE=re.compile(r'(?m)^Rank:\s*(\d+)\s*$'); MEANING_RE=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$'); POS_RE=re.compile(r'(?m)^Part of speech:\s*(.+?)\s*$')
SOURCE='- Cairo Arabic Language Academy + CALIMA/Kaikki modern-sense educator review (2026-08-13)'
MODERN_REPAIRS={
 1001:('منتدى','assembly room; gathering place','forum; gathering/meeting place','noun'),
 1031:('خارجي','outer; foreign','external; outer; foreign','adj'),
 1090:('جهد','exertion','effort; exertion','noun'),
 1150:('شهادة','martyrdom','testimony; certificate; credential/diploma; martyrdom','noun'),
 1178:('ساحة','field','square; open space; courtyard; field/arena','noun'),
 1214:('مطلوب','demanded','required; wanted; requested; demanded','adjective / passive participle'),
 1259:('ذكرى','remembrance','memory; remembrance; commemoration; anniversary','noun'),
 1281:('شرح','commentary','explanation; commentary','noun'),
 1283:('داخلي','domestic','internal; inner; domestic','adj'),
 1292:('وجهة','side; direction','direction; destination; viewpoint / point of view','noun'),
 1336:('تطور','progress','development; evolution; progress','noun'),
 1340:('متعدد','numerous','multiple; varied; numerous','adj'),
 1408:('إقليم','region','region; province; territory','noun'),
 1436:('تكوين','structure','formation; composition; structure; creation','noun'),
 1453:('ثابت','permanent','fixed; stable; constant; permanent','adj'),
}

def load_review_repairs():
 if not REPAIR_DATA.exists():return
 data=json.loads(REPAIR_DATA.read_text(encoding='utf-8'))
 for r in data.get('repairs',[]):
  MODERN_REPAIRS[int(r['rank'])]=(r['front'],r['expected'],r['meaning'],r['pos'])

def norm(s): return DIAC.sub('',unicodedata.normalize('NFKC',s or '').replace('ـ','')).strip()
def meaning(back):
 m=MEANING_RE.search(back or ''); return m.group(1).strip() if m else ''
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

def apply_confirmed_live_repairs():
 load_review_repairs()
 with LIVE.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 if len(rows)!=2000:raise SystemExit(f'expected 2000 live continuation rows, found {len(rows)}')
 applied=[]
 for rank,(front,expected,new_meaning,new_pos) in MODERN_REPAIRS.items():
  row=rows[rank-1001]
  if row.get('Front')!=front:raise SystemExit(f'rank {rank} front mismatch: {row.get("Front")!r}')
  back=row.get('Back') or ''
  rm=RANK_RE.search(back); mm=MEANING_RE.search(back); pm=POS_RE.search(back)
  if not rm or int(rm.group(1))!=rank or not mm or not pm:raise SystemExit(f'rank {rank} metadata mismatch')
  current=mm.group(1).strip()
  if current not in {expected,new_meaning}:raise SystemExit(f'rank {rank} changed since review: {current!r}')
  if current!=new_meaning or pm.group(1).strip()!=new_pos:
   back=MEANING_RE.sub(f'Meaning: {new_meaning}',back,count=1)
   back=POS_RE.sub(f'Part of speech: {new_pos}',back,count=1)
   if SOURCE not in back:back=back.rstrip()+'\n'+SOURCE
   row['Back']=back;applied.append(rank)
 for rank,row in enumerate(rows,1001):
  m=RANK_RE.search(row.get('Back') or '')
  if not (row.get('Front') or '').strip() or not m or int(m.group(1))!=rank:
   raise SystemExit(f'live continuation structural guard failed at rank {rank}')
 with LIVE.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['Front','Back'],lineterminator='\n');w.writeheader();w.writerows(rows)
 subprocess.run(['git','add','arabic_top3000.csv'],cwd=ROOT,check=True)
 return applied

def main():
 import argparse
 ap=argparse.ArgumentParser(); ap.add_argument('--kaikki-jsonl',required=True); a=ap.parse_args()
 applied=apply_confirmed_live_repairs()
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
 s={'rows':2000,'status_counts':counts,'kaikki_entry_coverage':sum(r['kaikki_entry'] for r in results),'kaikki_semantic_agreement':sum(r['kaikki_semantic_agreement'] for r in results),'omw_entry_coverage':sum(r['omw_entry'] for r in results),'omw_semantic_agreement':sum(r['omw_semantic_agreement'] for r in results),'wordfreq_attested':sum(r['wordfreq_attested'] for r in results),'calima_exact':sum(r['calima_exact'] for r in results),'explicit_review_rows':len(review),'promotion_gate':'PASS' if not review else 'REVIEW_REQUIRED','confirmed_live_modern_sense_repairs_applied':applied}
 (AUDIT/'arabic_top3000_external_semantic_audit_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
