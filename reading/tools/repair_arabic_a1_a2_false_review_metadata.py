#!/usr/bin/env python3
import json,re,subprocess,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
A1=ROOT/'reading/arabic/a1/passages.jsonl';A2=ROOT/'reading/arabic/a2/passages.jsonl'
EVID=ROOT/'reading/audit/arabic_a1_a2_manual_review_evidence_2026-08-23.json'
REPORT=ROOT/'reading/audit/arabic_a1_a2_false_review_metadata_repair_2026-08-23.json'
EXPECTED={'a1':'4723cb4c9974a9a9c84b6c030d9c1a30c0820500','a2':'d6a10dddde14628c8e4a7ddb4db7781604852210'}
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]');WORD=re.compile(r'[\u0621-\u064A]+')
PRO=('و','ف','ب','ك','ل');NSUF=('هما','هم','هن','كما','كم','كن','نا','ها','ه','ك','ي','ات','ون','ين','ان');VPRE=('أ','ا','ن','ي','ت');VSUF=('ون','ين','ان','وا','نا','تم','تن','ن','ت')
def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
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
 return e
def vcores(tok):
 o=set(nominal(tok))
 for x in list(o):
  if len(x)>=4 and x[0] in VPRE:o.add(x[1:])
 for x in list(o):
  for s in VSUF:
   if x.endswith(s) and len(x)-len(s)>=3:o.add(x[:-len(s)])
 return {x for x in o if len(x)>=2}
def forms(meta,teach):
 vals=[teach]
 for p in re.split(r'[/؛;،,]|\bor\b',str(meta.get('lemma') or '')):
  if re.search(r'[\u0621-\u064A]',p):vals.append(p.strip())
 return list(dict.fromkeys(norm(x) for x in vals if norm(x)))
def supported(text,fs,isverb):
 hits=[]
 for t in toks(text):
  kind=None
  if t in fs:kind='exact_or_lemma'
  elif any(nominal(t)&nominal(f) for f in fs):kind='nominal_or_orthographic'
  elif isverb and any(vcores(t)&vcores(f) for f in fs):kind='verbal_inflection_or_lemma_alternation'
  if kind:hits.append({'token':t,'kind':kind})
 return hits
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(p,rows):p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
def main():
 actual={'a1':blob(A1),'a2':blob(A2)}
 if actual!=EXPECTED:raise SystemExit(f'unexpected input blobs {actual}')
 evidence=json.loads(EVID.read_text(encoding='utf-8'))
 rows={'a1':load(A1),'a2':load(A2)};idx={l:{r['id']:r for r in rs} for l,rs in rows.items()}
 removals=[];resolved_variants=[];new_target_blockers=[];count_blockers=[]
 for item in evidence['items']:
  pid=item['passage_id'];level=item['level'];row=idx[level][pid];meta=item.get('target_metadata') or {};isverb='verb' in str(meta.get('part_of_speech') or '').lower();fs=forms(meta,item.get('target_form',''));hits=supported(row.get('text',''),fs,isverb);code=item['warning_code'];tid=item['target_id']
  if code=='running_text_review_target_no_exact_surface':
   if hits:
    resolved_variants.append({'review_id':item['review_id'],'passage_id':pid,'target_id':tid,'forms_checked':fs,'hits':hits})
   else:
    review=row.get('review_lexical_targets',[]);matches=[i for i,t in enumerate(review) if isinstance(t,dict) and t.get('id')==tid]
    if len(matches)!=1:raise SystemExit(f'{pid} {tid}: expected exactly one review target, got {len(matches)}')
    removed=review.pop(matches[0]);removals.append({'review_id':item['review_id'],'passage_id':pid,'target_id':tid,'removed':removed,'reason':'Declared running_text review has no exact, conservative orthographic/nominal, or POS-confirmed verbal realization, including lemma alternatives.'})
    q=row.setdefault('quality',{});q['coverage_check']='pending';q['status']='draft';notes=q.setdefault('notes',[]);note='False running-text review metadata removed 2026-08-23 after lemma-aware Arabic surface audit; review-spacing revalidation pending.'
    if note not in notes:notes.append(note)
  elif code=='new_target_form_not_exactly_found_in_text':
   declared=meta.get('declared_exposures_in_text')
   if not hits or (isinstance(declared,int) and len(hits)!=declared):new_target_blockers.append({'review_id':item['review_id'],'passage_id':pid,'target_id':tid,'form':item.get('target_form'),'lemma':meta.get('lemma'),'declared':declared,'supported_count':len(hits),'hits':hits})
   else:resolved_variants.append({'review_id':item['review_id'],'passage_id':pid,'target_id':tid,'forms_checked':fs,'hits':hits})
  elif code=='declared_exposure_count_differs_from_exact_surface_count':
   declared=meta.get('declared_exposures_in_text')
   if not isinstance(declared,int) or len(hits)!=declared:count_blockers.append({'review_id':item['review_id'],'passage_id':pid,'target_id':tid,'form':item.get('target_form'),'lemma':meta.get('lemma'),'declared':declared,'supported_count':len(hits),'hits':hits})
   else:resolved_variants.append({'review_id':item['review_id'],'passage_id':pid,'target_id':tid,'forms_checked':fs,'hits':hits})
 for level,path in [('a1',A1),('a2',A2)]:dump(path,rows[level])
 out={'schema_version':1,'date':'2026-08-23','input_blobs':actual,'output_blobs':{'a1':blob(A1),'a2':blob(A2)},'removed_false_running_text_reviews_count':len(removals),'resolved_variant_diagnostics_count':len(resolved_variants),'new_target_blocker_count':len(new_target_blockers),'exposure_count_blocker_count':len(count_blockers),'removals':removals,'resolved_variants':resolved_variants,'new_target_blockers':new_target_blockers,'exposure_count_blockers':count_blockers,'quality_promotion':False}
 REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:out[k] for k in ('output_blobs','removed_false_running_text_reviews_count','resolved_variant_diagnostics_count','new_target_blocker_count','exposure_count_blocker_count')},ensure_ascii=False))
if __name__=='__main__':main()
