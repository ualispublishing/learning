#!/usr/bin/env python3
"""Replace mechanically fresh but pedagogically weak Unit09 targets.

Requires the current canonical B2 file to contain exactly Units01-09. Verifies
that its first 48 rows byte-hash to the sealed Unit08 blob, temporarily restores
that prefix in the working tree, regenerates Unit09 with the exhaustive probe and
content-word-only selector, then runs the Unit09 frontier lock. On any exception
the original 54-row working file is restored before the error is re-raised.
"""
from __future__ import annotations
import json,runpy,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';AUD=R/'reading/audit';B2=R/'reading/french/b2/passages.jsonl';LOCK8=AUD/'french_b2_unit08_frontier_lock.json';SEL=AUD/'french_b2_unit09_target_selection.json'
sys.path.insert(0,str(TOOLS))
EXPECTED={'situation','cas','part','meilleur','riche','pauvre','aide','jeune','assurer','obtenir','offrir','président','contre','humain','appel','propos','recherche','réfléchir','revoir','force'}
BANNED={'être','avoir','de','je','pas','le','que','vous','tu','et','il','un','en','ça','on','une','elle','me','du','te','se','toi','lui','votre','cette','son','par','ou','des'}

def hash_bytes(data:bytes)->str:
 return subprocess.check_output(['git','hash-object','--stdin'],input=data).decode().strip()
def run(name):
 print(f'=== RUN {name} ===');runpy.run_path(str(TOOLS/name),run_name='__main__')

def main():
 original=B2.read_bytes();lines=original.splitlines(keepends=True)
 if len(lines)!=54:raise AssertionError(f'Unit09 pedagogical repair requires exactly 54 B2 rows, found {len(lines)}')
 rows=[json.loads(x) for x in original.decode('utf-8').splitlines() if x.strip()]
 if rows[-1].get('id')!='fr-b2-u09-p06':raise AssertionError('Current B2 frontier is not Unit09')
 lock8=json.loads(LOCK8.read_text(encoding='utf-8'));prefix=b''.join(lines[:48])
 if lock8.get('status')!='PASS' or lock8.get('last_sequence')!=48 or hash_bytes(prefix)!=lock8.get('canonical_blob'):
  raise AssertionError('First 48 canonical rows do not match sealed Unit08 blob')
 try:
  B2.write_bytes(prefix)
  run('generate_french_b2_unit09_retry.py')
  newrows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
  if len(newrows)!=54 or newrows[-1].get('id')!='fr-b2-u09-p06':raise AssertionError('Regenerated Unit09 frontier invalid')
  selected={t['form'] for r in newrows[48:53] for t in r.get('new_lexical_targets',[])}
  if selected!=EXPECTED:raise AssertionError(f'Unit09 pedagogical target set drift: {sorted(selected)}')
  if selected&BANNED:raise AssertionError(f'Unit09 contains banned function-word targets: {sorted(selected&BANNED)}')
  if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) for r in newrows[48:]):raise AssertionError('Unit09 word-band/count failure after repair')
  if any(len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in newrows[48:]):raise AssertionError('Unit09 Q/A count failure after repair')
  if any(len(r.get('new_lexical_targets',[]))!=4 for r in newrows[48:53]) or newrows[53].get('new_lexical_targets'):raise AssertionError('Unit09 target/checkpoint structure failure after repair')
  sel=json.loads(SEL.read_text(encoding='utf-8'))
  if {x['form'] for x in sel.get('selected',[])}!=EXPECTED or sel.get('selected_count')!=20:raise AssertionError('Unit09 pedagogical selection artifact mismatch')
  run('lock_french_b2_unit09_frontier.py')
  lock9=json.loads((AUD/'french_b2_unit09_frontier_lock.json').read_text(encoding='utf-8'))
  live=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
  if lock9.get('status')!='PASS' or lock9.get('last_sequence')!=54 or lock9.get('canonical_blob')!=live:raise AssertionError('Unit09 repaired lock/live blob mismatch')
  print(json.dumps({'status':'PASS','b2_blob':live,'b2_passages':54,'unit09_targets':sorted(EXPECTED),'banned_function_targets':0,'unit09_word_counts':[r['word_count'] for r in newrows[48:54]]},ensure_ascii=False))
 except Exception:
  B2.write_bytes(original)
  raise
if __name__=='__main__':main()
