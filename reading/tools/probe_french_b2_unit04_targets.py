#!/usr/bin/env python3
"""Persist source/freshness probe for B2 Unit04: cities and design."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
REPO=Path(__file__).resolve().parents[2]
B2=REPO/'reading/french/b2/passages.jsonl';LOCK=REPO/'reading/audit/french_b2_unit03_frontier_lock.json';OUT=REPO/'reading/audit/french_b2_unit04_target_probe.json'
PATHS=[REPO/'reading/french/a1/passages.jsonl',REPO/'reading/french/a2/passages.jsonl',REPO/'reading/french/b1/passages.jsonl',B2]
CANDIDATES=[
 'ville','rue','route','place','espace','bâtiment','maison','quartier','centre','coin','côté','bord','entrée','sortie','porte','mur','sol','toit','fenêtre',
 'pont','parc','jardin','arbre','eau','air','lumière','ombre','bruit','silence','circulation','transport','bus','train','voiture','vélo','pied','chemin',
 'large','étroit','haut','bas','long','court','proche','loin','autour','devant','derrière','entre','milieu','direction','ligne','forme','couleur','niveau',
 'construire','créer','ouvrir','fermer','changer','déplacer','traverser','tourner','monter','descendre','entrer','sortir','passer','rester','utiliser','servir',
 'améliorer','réduire','augmenter','ajouter','retirer','installer','placer','dessiner','plan','projet','travail','usage','fonction','besoin','accès','accessible',
 'public','privé','commun','local','habitants','habitant','personne','enfant','famille','travailleur','visiteur','commerce','magasin','école','hôpital','service',
 'sécurité','danger','risque','coût','prix','temps','distance','vitesse','qualité','confort','utile','pratique','possible','nécessaire','important','simple','beau',
 'protéger','aider','permettre','empêcher','préférer','choisir','décider','garder','donner','juste','accord','groupe','chance','difficile','dommage','ordre',
 'zone','terrain','surface','station','arrêt','passage','passerelle','tunnel','parking','place','banc','marché','restaurant','bureau','étage','ascenseur','escalier',
 'modern','moderne','ancien','nouveau','récent','futur','avenir','développement','construction','architecture','design','urbanisme','population','environnement'
]
def main():
 if not LOCK.exists():raise AssertionError('Unit03 frontier lock missing')
 lock=json.loads(LOCK.read_text(encoding='utf-8'));current=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=18 or current!=lock.get('canonical_blob'):raise AssertionError('Unit03 frontier lock/live B2 mismatch')
 rows=[]
 for p in PATHS:rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len([r for r in rows if r.get('cefr')=='B2'])!=18:raise AssertionError('expected 18 B2 passages before Unit04 probe')
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();out=[];seen=set()
 for f in CANDIDATES:
  if f in seen:continue
  seen.add(f)
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 fresh=[x for x in out if x['status']=='fresh']
 result={'status':'PASS','scope':'French B2 Unit 04 target probe','theme':'cities and design','genres':['report','proposal','critique'],'b2_source_blob':current,'prior_deliberate_targets':len(prior),'candidate_count':len(out),'fresh_count':len(fresh),'fresh':fresh,'rejected':[x for x in out if x['status']!='fresh'],'note':'Read-only candidate/source/freshness probe; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
