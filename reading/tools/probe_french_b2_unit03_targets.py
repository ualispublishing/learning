#!/usr/bin/env python3
"""Source/freshness probe for B2 Unit 03: ethics and competing values.

Requires the validated Unit 02 frontier lock and persists an auditable probe
artifact. It never mutates canonical passage data.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
REPO=Path(__file__).resolve().parents[2]
B2=REPO/'reading/french/b2/passages.jsonl'; LOCK=REPO/'reading/audit/french_b2_unit02_frontier_lock.json'; OUT=REPO/'reading/audit/french_b2_unit03_target_probe.json'
PATHS=[REPO/'reading/french/a1/passages.jsonl',REPO/'reading/french/a2/passages.jsonl',REPO/'reading/french/b1/passages.jsonl',B2]
CANDIDATES=[
 'droit','devoir','justice','juste','injuste','liberté','égalité','respect','respecter','valeur','moral','morale','honnête','honnêteté',
 'responsable','responsabilité','obligation','obliger','permettre','interdire','autoriser','refuser','accepter','exiger','choix','choisir',
 'intérêt','avantage','dommage','danger','risque','protéger','aider','nuire','souffrir','sacrifice','partager','garder','donner','recevoir',
 'promesse','promettre','secret','confiance','vérité','vrai','faux','mentir','mensonge','preuve','raison','cause','effet','conséquence',
 'accord','règle','principe','loi','autorité','pouvoir','décision','décider','exception','limite','condition','permission','sanction',
 'commun','collectif','personnel','public','privé','majorité','minorité','groupe','individu','citoyen','famille','ami','étranger','victime',
 'équilibre','équitable','égal','différent','pareil','nécessaire','possible','difficile','grave','important','priorité','préférer','renoncer',
 'guerre','paix','maître','libre','chance','réussir','maintenir','simplement','doute','ordre','lieu','surtout','calmer','ramener'
]

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
 ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();out=[];seen=set()
 for f in CANDIDATES:
  if f in seen: continue
  seen.add(f)
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 fresh=[x for x in out if x['status']=='fresh']
 result={'status':'PASS','scope':'French B2 Unit 03 target probe','theme':'ethics and competing values','genres':['argument','case','response'],'b2_source_blob':current,'prior_deliberate_targets':len(prior),'candidate_count':len(out),'fresh_count':len(fresh),'fresh':fresh,'rejected':[x for x in out if x['status']!='fresh'],'note':'Read-only candidate/source/freshness probe; not a generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
