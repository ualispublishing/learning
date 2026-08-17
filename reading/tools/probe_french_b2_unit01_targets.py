#!/usr/bin/env python3
"""Read-only source/freshness probe for French B2 Unit 01 calibration candidates."""
from __future__ import annotations
import json
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
REPO=Path(__file__).resolve().parents[2]
PATHS=[REPO/'reading/french/a1/passages.jsonl',REPO/'reading/french/a2/passages.jsonl',REPO/'reading/french/b1/passages.jsonl']
CANDIDATES=['supposer','sécurité','promettre','ramener','valoir','préparer','jeter','presque','secret','raconter','accepter','ressembler','guerre','moyen','apporter','ordre','lieu','protéger','suffire','ainsi','général','apprécier','tromper','certain','surtout','libre','exister','calmer','intéresser','grave','pousser','maître','lumière','pareil','simplement','présent','science','nature','population','mesure','effet','cause','preuve','public','énergie','donnée','données','étude','observer','changer','choisir','possible','différent','résultat','décision','information']

def main():
 rows=[]
 for p in PATHS: rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)]
 ids={t.get('id') for t in prior}; forms={t.get('form') for t in prior}; deck=base.deck()
 out=[]
 for f in CANDIDATES:
  if f not in deck: status='missing_lexicon'; rank=None; tid=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':deck.get(f,{}).get('meaning')})
 print(json.dumps({'prior_deliberate_targets':len(prior),'fresh':[x for x in out if x['status']=='fresh'],'rejected':[x for x in out if x['status']!='fresh']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
