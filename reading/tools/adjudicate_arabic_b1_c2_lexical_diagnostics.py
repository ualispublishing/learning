#!/usr/bin/env python3
import json,re,subprocess,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('b1','b2','c1','c2')
PATHS={l:ROOT/f'reading/arabic/{l}/passages.jsonl' for l in LEVELS}
INV=ROOT/'reading/audit/arabic_b1_c2_current_inventory_2026-08-23.json'
OUT=ROOT/'reading/audit/arabic_b1_c2_lexical_diagnostic_adjudication_2026-08-23.json'
EXPECTED={'b1':'cbe9e70e07543c3ce9080fb375af6468cfbd2d3c','b2':'a9486b2c38dc53661143e734c9797cd26fa1f742','c1':'3f68da825c50c3018f9e054cbeec27ba01b17be0','c2':'b8e78e2a8dce942e87ef627a8436f1c8571f9d43'}
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]');WORD=re.compile(r'[\u0621-\u064A]+')
PRO=('و','ف','ب','ك','ل');NSUF=('هما','هم','هن','كما','كم','كن','نا','ها','ه','ك','ي','ات','ون','ين','ان','ة','تين','تان');VPRE=('أ','ا','ن','ي','ت');VSUF=('ون','ين','ان','وا','نا','تم','تن','ن','ت','ا')
def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def norm(s):return DIAC.sub('',unicodedata.normalize('NFKC',str(s or '')).replace('ـ','')).replace('ٱ','ا')
def toks(s):return WORD.findall(norm(s))
def nominal(tok):
 o={tok};f={tok}
 for _ in range(2):
  n=set()
  for x in f:
   for p in PRO:
    if x.startswith(p) and len(x)>2:n.add(x[1:])
   if x.startswith('ال') and len(x)>4:n.add(x[2:])
  o|=n;f=n
 e=set(o)
 for x in list(o):
  for s in NSUF:
   if x.endswith(s) and len(x)-len(s)>=2:e.add(x[:-len(s)])
  if x.endswith('ا') and len(x)>3:e.add(x[:-1])
  if x.endswith('ة') and len(x)>3:e.add(x[:-1])
 return e
def vcores(tok):
 o=set(nominal(tok))
 for x in list(o):
  if len(x)>=4 and x[0] in VPRE:o.add(x[1:])
 for x in list(o):
  for s in VSUF:
   if x.endswith(s) and len(x)-len(s)>=3:o.add(x[:-len(s)])
 return {x for x in o if len(x)>=2}
def forms(meta,teaching):
 vals=[teaching]
 for p in re.split(r'[/؛;،,]|\bor\b',str(meta.get('lemma') or '')):
  if re.search(r'[\u0621-\u064A]',p):vals.append(p.strip())
 return list(dict.fromkeys(norm(x) for x in vals if norm(x)))
def hits(text,fs,isverb):
 out=[]
 for t in toks(text):
  kind=None
  if t in fs:kind='exact_or_lemma'
  elif any(nominal(t)&nominal(f) for f in fs):kind='nominal_clitic_gender_or_orthographic'
  elif isverb and any(vcores(t)&vcores(f) for f in fs):kind='verbal_inflection_or_lemma_alternation'
  if kind:out.append({'token':t,'kind':kind})
 return out
def main():
 actual={l:blob(p) for l,p in PATHS.items()}
 if actual!=EXPECTED:raise SystemExit(f'unexpected blobs {actual}')
 inv=json.loads(INV.read_text(encoding='utf-8'))
 if inv.get('hard_error_count')!=0 or inv.get('diagnostic_count')!=60:raise SystemExit(f'expected zero structural errors and 60 diagnostics, got {inv.get("hard_error_count")}/{inv.get("diagnostic_count")}')
 rows={l:load(PATHS[l]) for l in LEVELS};idx={l:{r['id']:r for r in rs} for l,rs in rows.items()};intro={}
 for l,rs in rows.items():
  intro[l]={}
  for r in rs:
   for t in r.get('new_lexical_targets',[]):
    if isinstance(t,dict) and t.get('id'):intro[l].setdefault(t['id'],t)
 decisions=[];counts=Counter();unresolved=[]
 for d in inv.get('diagnostics',[]):
  pid=d['passage_id'];level=pid.split('-')[1];row=idx[level][pid];tid=d.get('target_id');meta=intro[level].get(tid,{})
  fs=forms(meta,d.get('form') or meta.get('form') or '');isverb='verb' in str(meta.get('part_of_speech') or '').lower();hs=hits(row.get('text',''),fs,isverb)
  x={'diagnostic':d,'level':level,'forms_checked':fs,'target_metadata':{k:meta.get(k) for k in ('id','form','lemma','part_of_speech','intended_sense','exposures_in_text')},'supported_hits':hs}
  if d.get('code')=='new_target_no_exact_surface':
   declared=d.get('declared')
   if hs and (not isinstance(declared,int) or len(hs)==declared):dec='RESOLVED_VALID_MORPHOLOGY_EXACT_COUNT'
   elif hs:dec='UNRESOLVED_NEW_TARGET_COUNT_MISMATCH';unresolved.append(x)
   else:dec='UNRESOLVED_NEW_TARGET_NO_REALIZATION';unresolved.append(x)
  elif d.get('code')=='running_text_review_no_exact_surface':
   if hs:dec='RESOLVED_VALID_REVIEW_MORPHOLOGY'
   else:dec='UNRESOLVED_FALSE_RUNNING_TEXT_REVIEW';unresolved.append(x)
  else:dec='UNRESOLVED_UNKNOWN';unresolved.append(x)
  x['decision']=dec;counts[dec]+=1;decisions.append(x)
 out={'schema_version':1,'date':'2026-08-23','scope':'Arabic B1-C2 lexical surface diagnostic adjudication','input_blobs':actual,'source_diagnostics':60,'decision_counts':dict(counts),'resolved_count':60-len(unresolved),'unresolved_count':len(unresolved),'unresolved':unresolved,'decisions':decisions,'quality_promotion':False}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'decision_counts':out['decision_counts'],'resolved':out['resolved_count'],'unresolved':out['unresolved_count']},ensure_ascii=False))
if __name__=='__main__':main()
