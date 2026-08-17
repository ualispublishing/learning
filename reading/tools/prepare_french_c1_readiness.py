#!/usr/bin/env python3
"""Extract canonical C1 constraints after the B2 generation-integrity seal.

This gate does not generate C1 content. It proves the B2 seal matches live data,
extracts the C1 word band from the repository passage standard, captures nearby
C1 planning guidance, and records all C1/Unit01 entries found in the topic/genre
matrix for an auditable calibration handoff.
"""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B2=R/'reading/french/b2/passages.jsonl';AUDIT=R/'reading/audit/french_b2_generation_integrity.json';STANDARD=R/'docs/READING_PASSAGE_STANDARD.md';MATRIX=R/'reading/planning/topic_genre_matrix.json';OUT=R/'reading/audit/french_c1_readiness.json'

def collect_c1(obj,path='$',out=None):
 if out is None:out=[]
 if isinstance(obj,dict):
  # Retain any object whose key/value text explicitly points to C1 or unit 01,
  # then continue recursively for nested structures.
  text=' '.join(str(k) for k in obj.keys())+' '+' '.join(str(v) for v in obj.items() if isinstance(v,(str,int,float,bool)))
  if re.search(r'(?i)\bc1\b|unit[_ -]?0?1',text):out.append({'path':path,'value':obj})
  for k,v in obj.items():collect_c1(v,f'{path}.{k}',out)
 elif isinstance(obj,list):
  for i,v in enumerate(obj):collect_c1(v,f'{path}[{i}]',out)
 elif isinstance(obj,str) and re.search(r'(?i)\bc1\b|unit[_ -]?0?1',obj):out.append({'path':path,'value':obj})
 return out

def main():
 audit=json.loads(AUDIT.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if audit.get('status')!='PASS' or audit.get('canonical_blob')!=blob or audit.get('passages')!=60:raise AssertionError('C1 readiness requires matching complete B2 integrity seal')
 text=STANDARD.read_text(encoding='utf-8');lines=text.splitlines();contexts=[]
 for i,line in enumerate(lines):
  if re.search(r'(?i)\bc1\b',line):
   lo=max(0,i-3);hi=min(len(lines),i+5);contexts.append({'line':i+1,'context':'\n'.join(lines[lo:hi])})
 if not contexts:raise AssertionError('No C1 guidance found in passage standard')
 joined='\n'.join(x['context'] for x in contexts)
 # Prefer a band appearing on/near a C1 marker. Accept en dash/em dash/hyphen and
 # optional word labels. Reject implausible bands rather than guessing.
 bands=[]
 for m in re.finditer(r'(?is)\bc1\b.{0,220}?(\d{3,4})\s*(?:–|—|-)\s*(\d{3,4})',joined):
  a,b=map(int,m.groups())
  if 300<=a<b<=2000:bands.append((a,b))
 if not bands:
  for c in contexts:
   for m in re.finditer(r'(\d{3,4})\s*(?:–|—|-)\s*(\d{3,4})',c['context']):
    a,b=map(int,m.groups())
    if 300<=a<b<=2000:bands.append((a,b))
 uniq=[]
 for x in bands:
  if x not in uniq:uniq.append(x)
 if len(uniq)!=1:raise AssertionError(f'Could not derive one unambiguous C1 word band from standard: {uniq}')
 word_min,word_max=uniq[0]
 matrix=json.loads(MATRIX.read_text(encoding='utf-8'));matches=collect_c1(matrix)
 if not matches:raise AssertionError('No C1/Unit01 planning entries found in topic/genre matrix')
 # Deduplicate serialized matches while preserving traversal order.
 seen=set();dedup=[]
 for m in matches:
  sig=json.dumps(m,ensure_ascii=False,sort_keys=True)
  if sig not in seen:seen.add(sig);dedup.append(m)
 out={'status':'PASS','scope':'French C1 readiness','b2_canonical_blob':blob,'b2_generation_integrity_artifact':'reading/audit/french_b2_generation_integrity.json','c1_word_min':word_min,'c1_word_max':word_max,'c1_standard_contexts':contexts,'topic_genre_matrix_c1_matches':dedup[:80],'topic_genre_matrix_match_count':len(dedup),'calibration_policy':'Do not assume the B2 lexical-load default carries forward. Probe remaining source vocabulary exhaustively, choose a conservative Unit01 load, generate six passages with P06 zero-new, then run strict post-calibration language/pedagogy/integrity review before setting the C1 production default.','note':'Readiness artifact only; no C1 generation approval yet.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','b2_blob':blob,'c1_word_band':[word_min,word_max],'matrix_matches':len(dedup)},ensure_ascii=False))
if __name__=='__main__':main()
