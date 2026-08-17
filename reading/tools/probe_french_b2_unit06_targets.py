#!/usr/bin/env python3
"""Dependency-locked source/freshness probe for B2 Unit06: digital life and privacy.

Intentionally requires the completed Unit05 frontier lock before it can emit an
auditable result; creating this script does not touch canonical B2 data.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit05_frontier_lock.json';OUT=R/'reading/audit/french_b2_unit06_target_probe.json'
PATHS=[R/'reading/french/a1/passages.jsonl',R/'reading/french/a2/passages.jsonl',R/'reading/french/b1/passages.jsonl',B2]
CANDIDATES=[
 'ordinateur','téléphone','écran','machine','appareil','internet','réseau','site','page','compte','message','courrier','adresse','photo','image','vidéo','fichier','document',
 'information','donnée','nombre','nom','identité','personne','profil','public','privé','secret','personnel','partager','envoyer','recevoir','garder','effacer','supprimer','copier',
 'protéger','protection','sécurité','risque','danger','contrôle','contrôler','surveiller','suivre','observer','connaître','savoir','voir','montrer','cacher','chercher','trouver',
 'autoriser','permission','permettre','refuser','accepter','accord','choix','choisir','décider','obliger','interdire','droit','loi','règle','condition','limite','responsable',
 'utiliser','usage','service','système','fonction','programme','application','technologie','numérique','digital','automatique','modèle','algorithme','code','clé','accès','entrer','sortir',
 'ami','famille','groupe','entreprise','travail','école','client','utilisateur','public','gouvernement','police','bureau','maison','ville','pays','monde',
 'vrai','faux','vérité','croire','penser','comprendre','expliquer','preuve','doute','confiance','erreur','problème','cause','effet','résultat','prévoir','sembler',
 'simple','facile','difficile','rapide','lent','important','utile','gratuit','libre','ouvert','fermé','nouveau','ancien','possible','nécessaire','certain','général',
 'mémoire','oublier','retenir','reconnaître','voix','visage','corps','position','lieu','temps','date','heure','jour','nuit','habitude','activité','action',
 'acheter','vendre','payer','prix','argent','offre','publicité','marché','produit','contrat','demander','répondre','signer','inscrire','inscription','contact'
]
def main():
 if not LOCK.exists():raise AssertionError('Unit05 frontier lock missing; Unit06 probe must not run early')
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=30 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit05 lock/live B2 mismatch')
 rows=[]
 for p in PATHS:rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len([r for r in rows if r.get('cefr')=='B2'])!=30:raise AssertionError('expected 30 B2 passages before Unit06 probe')
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();seen=set();out=[]
 for f in CANDIDATES:
  if f in seen:continue
  seen.add(f)
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 fresh=[x for x in out if x['status']=='fresh']
 result={'status':'PASS','scope':'French B2 Unit 06 target probe','theme':'digital life and privacy','genres':['analysis','policy-style summary','paired opinions'],'b2_source_blob':blob,'prior_deliberate_targets':len(prior),'candidate_count':len(out),'fresh_count':len(fresh),'fresh':fresh,'rejected':[x for x in out if x['status']!='fresh'],'note':'Read-only dependency-locked candidate/source/freshness probe; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
