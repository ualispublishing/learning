#!/usr/bin/env python3
"""Read-only source/freshness probe for B2 Unit 03: institutions and rules.

Requires the validated Unit 02 frontier lock before probing candidates.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
REPO=Path(__file__).resolve().parents[2]
B2=REPO/'reading/french/b2/passages.jsonl'; LOCK=REPO/'reading/audit/french_b2_unit02_frontier_lock.json'
PATHS=[REPO/'reading/french/a1/passages.jsonl',REPO/'reading/french/a2/passages.jsonl',REPO/'reading/french/b1/passages.jsonl',B2]
CANDIDATES=['loi','droit','autorité','justice','police','gouvernement','président','ministre','devoir','permettre','interdire','obliger','citoyen','vote','accord','pouvoir','officiel','document','contrat','majorité','minorité','signature','respect','responsable','institution','administration','administratif','commun','collectif','égalité','obligation','permission','sanction','fonction','procédure','légal','légale','élection','élire','règlement','réglementation','norme','principe','comité','membre','bureau','directeur','direction','local','national','municipal','social','parti','groupe','représenter','représentant','autoriser','refuser','exiger','demander','répondre','décider','appliquer','application','exception','contrainte','recours','plainte','appel']

def main():
 if not LOCK.exists(): raise AssertionError('Unit02 frontier lock artifact missing')
 lock=json.loads(LOCK.read_text(encoding='utf-8'))
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=12: raise AssertionError('Unit02 frontier lock not PASS')
 current=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if current!=lock.get('canonical_blob'): raise AssertionError(f"B2 blob drift from Unit02 lock: {current} != {lock.get('canonical_blob')}")
 rows=[]
 for p in PATHS: rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len([r for r in rows if r.get('cefr')=='B2'])!=12: raise AssertionError('expected exactly 12 B2 passages before Unit03 probe')
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)]
 ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();out=[]
 for f in CANDIDATES:
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 print(json.dumps({'b2_source_blob':current,'prior_deliberate_targets':len(prior),'fresh':[x for x in out if x['status']=='fresh'],'rejected':[x for x in out if x['status']!='fresh']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
