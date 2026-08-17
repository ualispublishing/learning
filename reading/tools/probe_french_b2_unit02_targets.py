#!/usr/bin/env python3
"""Read-only source/freshness probe for French B2 Unit 02 candidates."""
from __future__ import annotations
import json
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
REPO=Path(__file__).resolve().parents[2]
PATHS=[REPO/'reading/french/a1/passages.jsonl',REPO/'reading/french/a2/passages.jsonl',REPO/'reading/french/b1/passages.jsonl',REPO/'reading/french/b2/passages.jsonl']
CANDIDATES=['promettre','ramener','secret','guerre','ordre','lieu','surtout','calmer','grave','pousser','maître','lumière','pareil','simplement','partager','réussir','maintenir','valeur','opinion','confiance','condition','avantage','alternative','limite','priorité','réduire','augmenter','choisir','doute','douter','hasard','probable','possible','nécessaire','utile','préférer','événement','évaluer','risque','conséquence','coût','temps','chance','problème','solution','difficile','attendre','agir','décider','option','responsabilité','prévision','avenir','inconnu','incertain','incertitude']

def main():
 rows=[]
 for p in PATHS: rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)]
 ids={t.get('id') for t in prior}; forms={t.get('form') for t in prior}; deck=base.deck();out=[]
 for f in CANDIDATES:
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 print(json.dumps({'prior_deliberate_targets':len(prior),'fresh':[x for x in out if x['status']=='fresh'],'rejected':[x for x in out if x['status']!='fresh']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
