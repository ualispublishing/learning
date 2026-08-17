#!/usr/bin/env python3
"""Dependency-locked source/freshness probe for B2 Unit09: public policy and trade-offs."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit08_frontier_lock.json';OUT=R/'reading/audit/french_b2_unit09_target_probe.json'
PATHS=[R/'reading/french/a1/passages.jsonl',R/'reading/french/a2/passages.jsonl',R/'reading/french/b1/passages.jsonl',B2]
CANDIDATES=[
 'public','politique','service','budget','argent','prix','coût','payer','gratuit','dépense','dépenser','économie','économique','finance','financer','ressource','moyen','besoin','priorité','choix',
 'impôt','taxe','revenu','riche','pauvre','égalité','inégalité','juste','justice','aide','aider','soutien','protection','sécurité','accès','droit','liberté','responsabilité','obligation','règle',
 'avantage','bénéfice','gain','perte','dommage','risque','effet','résultat','conséquence','impact','cause','problème','solution','objectif','but','intérêt','valeur','qualité','quantité','niveau','limite',
 'groupe','population','famille','enfant','jeune','vieux','travailleur','client','citoyen','habitant','entreprise','employeur','employé','école','hôpital','médecin','patient','transport','logement','quartier',
 'ville','région','pays','local','national','gouvernement','ministre','administration','institution','bureau','conseil','comité','responsable','chef','membre','autorité','pouvoir','décision','décider','vote',
 'proposer','proposition','plan','mesure','programme','projet','réforme','changer','augmenter','réduire','limiter','développer','améliorer','maintenir','fermer','ouvrir','construire','organiser','appliquer','réviser',
 'accepter','refuser','permettre','interdire','obliger','demander','répondre','expliquer','justifier','comparer','évaluer','mesurer','observer','prévoir','estimer','calculer','compter','vérifier','montrer','prouver',
 'court','long','rapide','lent','immédiat','futur','présent','temporaire','permanent','possible','probable','certain','difficile','simple','complexe','efficace','utile','nécessaire','important','général',
 'partager','répartir','distribution','distribuer','recevoir','donner','prendre','garder','perdre','gagner','offrir','acheter','vendre','utiliser','servir','attendre','choisir','préférer','sacrifier','remplacer',
 'accord','désaccord','conflit','opposition','critique','avis','opinion','argument','raison','preuve','contre','pour','selon','malgré','cependant','pourtant','ainsi','donc','sinon','surtout'
]
def main():
 if not LOCK.exists():raise AssertionError('Unit08 frontier lock missing; Unit09 probe must not run early')
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=48 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit08 lock/live B2 mismatch')
 rows=[]
 for p in PATHS:rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len([r for r in rows if r.get('cefr')=='B2'])!=48:raise AssertionError('expected 48 B2 passages before Unit09 probe')
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();out=[];seen=set()
 for f in CANDIDATES:
  if f in seen:continue
  seen.add(f)
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 fresh=[x for x in out if x['status']=='fresh']
 result={'status':'PASS','scope':'French B2 Unit 09 target probe','theme':'public policy and trade-offs','genres':['briefing','argument','counterargument'],'b2_source_blob':blob,'prior_deliberate_targets':len(prior),'candidate_count':len(out),'fresh_count':len(fresh),'fresh':fresh,'rejected':[x for x in out if x['status']!='fresh'],'note':'Read-only dependency-locked candidate/source/freshness probe; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
