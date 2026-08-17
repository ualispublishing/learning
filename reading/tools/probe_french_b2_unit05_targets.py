#!/usr/bin/env python3
"""Persist source/freshness probe for B2 Unit05: climate and uncertainty."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit04_frontier_lock.json';OUT=R/'reading/audit/french_b2_unit05_target_probe.json'
PATHS=[R/'reading/french/a1/passages.jsonl',R/'reading/french/a2/passages.jsonl',R/'reading/french/b1/passages.jsonl',B2]
CANDIDATES=[
 'climat','climatique','météo','temps','pluie','neige','vent','soleil','chaleur','froid','chaud','température','saison','été','hiver','printemps','automne',
 'année','mois','jour','nuit','matin','soir','période','futur','avenir','passé','ancien','nouveau','récent','long','court','haut','bas','niveau',
 'changer','changement','continuer','rester','devenir','augmenter','réduire','baisser','monter','descendre','varier','variation','tendance','moyenne','écart',
 'mesure','mesurer','compter','nombre','chiffre','résultat','donnée','information','preuve','cause','effet','raison','exemple','comparaison','modèle','scénario',
 'prévoir','prévision','probable','probabilité','possible','possibilité','certain','incertain','incertitude','doute','risque','chance','attendre','supposer','estimer',
 'croire','penser','sembler','montrer','indiquer','expliquer','comprendre','savoir','connaître','vérifier','observer','remarquer','comparer','conclure','annoncer',
 'grave','danger','dangereux','dommage','protéger','éviter','prévenir','adapter','préparer','plan','décider','choisir','solution','action','réponse','coût','besoin',
 'eau','air','arbre','forêt','mer','océan','rivière','terre','sol','glace','feu','nature','environnement','animal','plante','agriculture','ville','région','pays',
 'public','groupe','personne','famille','travail','économie','prix','énergie','électricité','transport','voiture','maison','bâtiment','route','service','système',
 'fort','faible','important','petit','grand','simple','difficile','différent','pareil','général','local','normal','extrême','rapide','lent','souvent','rare','rarement',
 'retirer','tourner','rester','servir','bureau','beau','autour','utiliser','ouvrir','fermer','construire','proche','côté','coin'
]
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=24 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit04 lock/live B2 mismatch')
 rows=[]
 for p in PATHS:rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();seen=set();out=[]
 for f in CANDIDATES:
  if f in seen:continue
  seen.add(f)
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 fresh=[x for x in out if x['status']=='fresh']
 result={'status':'PASS','scope':'French B2 Unit 05 target probe','theme':'climate and uncertainty','genres':['evidence summary','news analysis','argument'],'b2_source_blob':blob,'prior_deliberate_targets':len(prior),'candidate_count':len(out),'fresh_count':len(fresh),'fresh':fresh,'rejected':[x for x in out if x['status']!='fresh'],'note':'Read-only candidate/source/freshness probe; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
