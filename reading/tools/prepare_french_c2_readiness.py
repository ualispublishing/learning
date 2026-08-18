#!/usr/bin/env python3
"""Prepare exact French C2 readiness from sealed C1 integrity and validated top-3000 continuation."""
from __future__ import annotations
import csv,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';INTEG=R/'reading/audit/french_c1_generation_integrity.json';STD=R/'docs/READING_PASSAGE_STANDARD.md';MATRIX=R/'reading/planning/topic_genre_matrix.json';LEX1=R/'french_top1000.csv';LEX3=R/'french_top3000.csv';OUT=R/'reading/audit/french_c2_readiness.json';PROBE=R/'reading/audit/french_c2_unit01_target_probe.json'
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def loadrows(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def deck(p):
 out={}
 with p.open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   form=(row.get('Front') or '').strip();b=row.get('Back') or '';mr=re.search(r'Rank:\s*(\d+)',b);mm=re.search(r'Meaning:\s*(.+)',b);mp=re.search(r'Part of speech:\s*(.+)',b)
   if form and mr:out[form]={'rank':int(mr.group(1)),'id':f"fr-rank-{int(mr.group(1)):04d}",'meaning':mm.group(1).strip() if mm else None,'part_of_speech':mp.group(1).strip() if mp else None,'source_lexicon':p.name}
 return out
def main():
 integ=json.loads(INTEG.read_text());c1=h(C1)
 if integ.get('status')!='PASS' or integ.get('canonical_blob')!=c1 or integ.get('passages')!=60:raise AssertionError('sealed C1 integrity required for C2 readiness')
 text=STD.read_text(encoding='utf-8');m=re.search(r'\|\s*C2\s*\|\s*([\d,]+)\s*[–-]\s*([\d,]+)\s*\|',text)
 if not m:raise AssertionError('cannot resolve C2 standard word band')
 lo,hi=(int(x.replace(',','')) for x in m.groups());lex=re.search(r'C2:\s*(\d+)\s*[–-]\s*(\d+)',text)
 if not lex:raise AssertionError('cannot resolve C2 lexical planning band')
 lexlo,lexhi=map(int,lex.groups());matrix=json.loads(MATRIX.read_text());nodes=matrix.get('levels',{}).get('C2')
 if not isinstance(nodes,list):raise AssertionError('matrix lacks levels.C2')
 matches=[(i,x) for i,x in enumerate(nodes) if isinstance(x,dict) and int(x.get('unit',-1))==1]
 if len(matches)!=1:raise AssertionError(f'expected one C2 Unit01 node, found {len(matches)}')
 idx,node=matches[0];theme=node.get('theme');genres=node.get('genres')
 if not theme or not genres:raise AssertionError('C2 Unit01 node incomplete')
 prior=loadrows(A1)+loadrows(A2)+loadrows(B1)+loadrows(B2)+loadrows(C1);pids={t['id'] for r in prior for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};pforms={t['form'] for r in prior for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
 d={**deck(LEX1),**deck(LEX3)};fresh=[]
 for form,x in sorted(d.items(),key=lambda kv:kv[1]['rank']):
  if x['id'] not in pids and form not in pforms:fresh.append({'form':form,**x,'status':'fresh'})
 # C2 should prefer ranks >1000 now that the earlier curriculum has heavily sampled top1000.
 continuation=[x for x in fresh if x['rank']>1000]
 if len(continuation)<200:raise AssertionError(f'insufficient validated top-3000 continuation: {len(continuation)}')
 ready={'status':'PASS','scope':'French C2 readiness after sealed C1','c1_canonical_blob':c1,'c1_integrity_artifact':'reading/audit/french_c1_generation_integrity.json','c2_word_min':lo,'c2_word_max':hi,'c2_lexical_planning_band':[lexlo,lexhi],'lexical_band_is_maximum_not_quota':True,'unit01_matrix_path':f'$.levels.C2[{idx}]','unit01_theme':theme,'unit01_genres':genres,'source_policy':'validated french_top3000.csv continuation (ranks 1001+) preferred; french_top1000 leftovers not forced','fresh_source_terms_total':len(fresh),'fresh_top3000_continuation':len(continuation),'note':'C2 calibration must choose a conservative load within the maximum planning band and validate it after generation.'}
 OUT.write_text(json.dumps(ready,ensure_ascii=False,indent=2)+'\n');PROBE.write_text(json.dumps({'status':'PASS','scope':'French C2 Unit01 exhaustive advanced target probe','c1_source_blob':c1,'theme':theme,'genres':genres,'word_band':[lo,hi],'lexical_planning_band':[lexlo,lexhi],'fresh_count':len(continuation),'fresh':continuation},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','word_band':[lo,hi],'lexical_band':[lexlo,lexhi],'theme':theme,'fresh_continuation':len(continuation)},ensure_ascii=False))
if __name__=='__main__':main()
