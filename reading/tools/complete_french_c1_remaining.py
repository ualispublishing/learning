#!/usr/bin/env python3
"""Finish French C1 Units06-10 serially from whatever sealed frontier currently exists."""
from __future__ import annotations
import json,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];T=R/'reading/tools';A=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';OUT=A/'french_c1_remaining_pipeline.json';sys.path.insert(0,str(T))
def rows():return [json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()] if C1.exists() else []
def h():return subprocess.check_output(['git','hash-object',str(C1)],text=True).strip()
def run(name):print(f'=== SERIAL C1 RUN {name} ===');runpy.run_path(str(T/name),run_name='__main__')
def main():
 A.mkdir(parents=True,exist_ok=True);start=len(rows());stages=[];error=None
 try:
  n=len(rows())
  if n<36:run('complete_french_c1_unit06_retry.py');stages.append('unit06_transaction');n=len(rows())
  if n<42:run('complete_french_c1_unit07_retry.py');stages.append('unit07_transaction');n=len(rows())
  if n<48:run('complete_french_c1_unit08_retry.py');stages.append('unit08_transaction');n=len(rows())
  if n<54:run('complete_french_c1_unit09_retry.py');stages.append('unit09_transaction');n=len(rows())
  if n<60:run('complete_french_c1_unit10_retry.py');stages.append('unit10_integrity_c2_readiness_transaction');n=len(rows())
  elif n==60:
   run('complete_french_c1_unit10.py');stages.append('verify_unit10_integrity_c2_readiness')
  else:raise AssertionError(f'unsupported C1 row count {n}')
  c2=json.loads((A/'french_c2_readiness.json').read_text())
  if len(rows())!=60 or c2.get('status')!='PASS':raise AssertionError('C1 serial finisher ended without C2 readiness')
 except Exception:
  error=traceback.format_exc();print(error);(A/'french_c1_remaining_pipeline_failure.txt').write_text(error,encoding='utf-8')
 final=len(rows());result={'status':'PASS_TO_C2_UNIT01_CALIBRATION' if final==60 and error is None else 'STOPPED_AT_FIRST_FAILING_GUARD','starting_c1_passages':start,'ending_c1_passages':final,'c1_blob':h(),'completed_stages':stages,'error':error}
 if error is None:
  (A/'french_c1_remaining_pipeline_failure.txt').unlink(missing_ok=True);r=json.loads((A/'french_c2_readiness.json').read_text());result.update({'c2_word_band':[r['c2_word_min'],r['c2_word_max']],'c2_lexical_planning_band':r['c2_lexical_planning_band'],'c2_unit01_theme':r['unit01_theme'],'fresh_top3000_continuation':r['fresh_top3000_continuation']})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
 if error is not None:raise SystemExit(1)
if __name__=='__main__':main()
