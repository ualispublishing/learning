#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/french/a1/passages.jsonl'; LEX=ROOT/'french_top1000.csv'
OUT=ROOT/'reading/audit/french_a1_generation_integrity.json'
OV={('fr-a1-u04-p01','autre'),('fr-a1-u04-p05','maison'),('fr-a1-u06-p01','beaucoup'),('fr-a1-u06-p04','jamais'),('fr-a1-u07-p04','droite'),('fr-a1-u09-p05','eau')}
def deck():
 d={}
 with LEX.open(encoding='utf-8',newline='') as f:
  for r in csv.DictReader(f):
   b=r.get('Back') or '';x=(r.get('Front') or '').strip()
   a=re.search(r'Rank:\s*(\d+)',b);m=re.search(r'Meaning:\s*(.+)',b)
   if x and a and m:d[x]=(int(a.group(1)),m.group(1).strip())
 return d
def count(text,f):return len(re.findall(rf'(?<!\w){re.escape(f)}(?!\w)',text,flags=re.I|re.UNICODE))
def norm(s):
 s=unicodedata.normalize('NFKC',str(s)).lower().replace('–','-').replace('—','-')
 s=re.sub(r'\([^)]*\)','',s);s=re.sub(r'\bas a noun\b','',s);s=re.sub(r'\s+',' ',s).strip(' .');return s
def atoms(s):
 return [re.sub(r'^(to\s+)','',p).strip(' .-') for p in re.split(r'\s*[;,/]\s*|\s+or\s+',norm(s)) if p.strip(' .-')]
def sense_supported(intended,source):
 i=atoms(intended);s=atoms(source)
 return bool(i) and all(any(x==y or x.startswith(y+' ') or y.startswith(x+' ') for y in s) for x in i)
def main():
 rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()];D=deck();bad=[];seen={};ovs=set();narrow=[];legacy=[]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)):bad.append('passage/sequence continuity')
 if len({r.get('id') for r in rows})!=60:bad.append('duplicate passage id')
 for r in rows:
  pid=r['id'];wc=len(r['text'].split())
  if r.get('word_count')!=wc or not 90<=wc<=140:bad.append(f'{pid}: word count/band')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10:bad.append(f'{pid}: assessment count')
  amap={a.get('question_id'):a.get('id') for a in r.get('answer_key',[])}
  local={t.get('id') for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict)}
  qtargets={str(x) for q in r.get('questions',[]) for x in (q.get('target_ids',[]) if isinstance(q.get('target_ids'),list) else [])}
  for q in r.get('questions',[]):
   if amap.get(q.get('id'))!=q.get('answer_id'):bad.append(f'{pid}:{q.get("id")}: answer link')
   if any(x not in local for x in q.get('target_ids',[])):bad.append(f'{pid}:{q.get("id")}: undeclared target')
  if pid.endswith('-p06') and r.get('new_lexical_targets'):bad.append(f'{pid}: P06 new target')
  for t in r.get('new_lexical_targets',[]):
   key=t.get('id');form=str(t.get('form'));lemma=str(t.get('lemma') or '');explicit=str(t.get('source_lookup_form') or '')
   if key in seen:bad.append(f'{pid}: duplicate new target {key}')
   seen[key]=(r['sequence'],form)
   lookup=form if form in D else (explicit if explicit in D else lemma)
   if lookup not in D:bad.append(f'{pid}:{form}: source form/lemma missing');continue
   rank,sense=D[lookup];eid=f'fr-rank-{rank:04d}'
   if t.get('source_lexicon')!='french_top1000.csv' or t.get('source_rank')!=rank or key!=eid:bad.append(f'{pid}:{form}: source identity')
   adj=t.get('sense_adjudication');k=(pid,form)
   if adj:
    ovs.add(k)
    if k not in OV or adj.get('status')!='VERIFIED_OVERRIDE' or not adj.get('authority_url'):bad.append(f'{pid}:{form}: bad override')
   else:
    intended=t.get('intended_sense')
    if norm(intended)!=norm(sense):
     if sense_supported(intended,sense):narrow.append({'passage_id':pid,'form':form,'lookup':lookup,'intended_sense':intended,'root_gloss':sense})
     else:bad.append(f'{pid}:{form}: unsupported reader sense | intended={intended!r} root={sense!r}')
   declared_forms=t.get('exposure_surface_forms')
   if declared_forms is None:declared_forms=[form]
   if not isinstance(declared_forms,list) or not declared_forms or any(not isinstance(x,str) or not x for x in declared_forms) or len(declared_forms)!=len(set(declared_forms)):
    bad.append(f'{pid}:{form}: invalid exposure_surface_forms');continue
   method=t.get('exposure_count_method')
   if method is not None and method!='exact_declared_surface_forms':bad.append(f'{pid}:{form}: unsupported exposure_count_method {method!r}')
   actual=sum(count(r['text'],surface) for surface in declared_forms);stored=t.get('exposures_in_text')
   if not isinstance(stored,int) or stored<1 or actual!=stored:
    bad.append(f'{pid}:{form}: exposure count | surfaces={declared_forms!r} stored={stored!r} actual={actual}')
 for r in rows:
  for t in r.get('review_lexical_targets',[]):
   x=seen.get(t.get('id'))
   if not x or x[0]>=r['sequence']:bad.append(f'{r["id"]}:{t.get("form")}: invalid review reference')
 if len(seen)!=100:bad.append(f'new target total {len(seen)} != 100')
 if ovs!=OV:bad.append(f'override set {sorted(ovs)}')
 units={str(u):{'passages':sum(r['unit']==u for r in rows),'new_targets':sum(len(r.get('new_lexical_targets',[])) for r in rows if r['unit']==u)} for u in range(1,11)}
 payload={'status':'PASS' if not bad else 'FAIL','scope':'French A1 generation milestone','passages':len(rows),'questions':sum(len(r['questions']) for r in rows),'answers':sum(len(r['answer_key']) for r in rows),'new_targets':len(seen),'verified_sense_overrides':[{'passage_id':p,'form':f} for p,f in sorted(ovs)],'validated_root_gloss_narrowings':narrow,'legacy_unit01_exposure_variances':legacy,'units':units,'failures':bad,'coverage_note':'estimated_known_token_coverage remains unmeasured placeholder data; no percentage is inferred','full_final_audit_deferred':True,'method_notes':['Source identity resolves direct validated surface form first, then explicit source lookup, then validated lemma for inflected reader forms.','A curriculum intended_sense may narrow a validated polysemous root gloss when each normalized sense atom is supported by that root gloss; unsupported extensions require explicit verified adjudication.','Exposure counts are exact Unicode-bounded counts of exposure_surface_forms when explicitly declared, otherwise of the canonical target form; Unit 01 is held to the same exact convention as later units.']}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':payload['status'],'failures':len(bad),'root_gloss_narrowings':len(narrow),'legacy_exposure_variances':len(legacy),'verified_overrides':len(ovs)},ensure_ascii=False))
 if bad:
  print('FRENCH_A1_INTEGRITY_FAILURES_BEGIN')
  for i,item in enumerate(bad,1):print(f'{i:02d}. {item}')
  print('FRENCH_A1_INTEGRITY_FAILURES_END');raise SystemExit(1)
if __name__=='__main__':main()
