#!/usr/bin/env python3
"""Persist source/freshness probe for B2 Unit08: history and explanation."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit07_frontier_lock.json';OUT=R/'reading/audit/french_b2_unit08_target_probe.json'
PATHS=[R/'reading/french/a1/passages.jsonl',R/'reading/french/a2/passages.jsonl',R/'reading/french/b1/passages.jsonl',B2]
CANDIDATES=[
 'histoire','historique','passé','présent','ancien','récent','époque','siècle','année','date','jour','mois','période','début','fin','avant','après','pendant','longtemps',
 'roi','reine','prince','empire','état','gouvernement','ministre','président','armée','soldat','guerre','paix','bataille','victoire','défaite','ennemi','peuple','nation','pays','ville',
 'loi','droit','pouvoir','autorité','ordre','règle','institution','administration','bureau','école','église','religion','marché','commerce','travail','argent','terre','route','port','frontière',
 'document','lettre','journal','livre','texte','photo','image','carte','archive','source','preuve','témoin','témoignage','mémoire','nom','liste','registre','rapport','discours','message',
 'écrire','lire','dire','raconter','expliquer','décrire','montrer','cacher','connaître','savoir','croire','penser','comprendre','interpréter','comparer','vérifier','chercher','trouver','observer','noter',
 'cause','effet','raison','résultat','conséquence','problème','solution','changement','changer','devenir','continuer','commencer','finir','créer','détruire','construire','développer','augmenter','réduire','produire',
 'décider','choisir','accepter','refuser','obliger','permettre','protéger','attaquer','défendre','quitter','arriver','partir','revenir','rejoindre','traverser','occuper','gagner','perdre','mourir','naître',
 'groupe','classe','famille','homme','femme','enfant','travailleur','paysan','citoyen','chef','responsable','membre','public','majorité','minorité','communauté','société','population','génération','personne',
 'fort','faible','grand','petit','important','simple','complexe','difficile','possible','probable','certain','général','local','national','international','politique','social','économique','militaire','religieux',
 'accord','conflit','crise','révolution','réforme','mouvement','protestation','élection','vote','traité','alliance','contrat','impôt','prix','faim','maladie','danger','sécurité','liberté','égalité',
 'version','point','vue','avis','opinion','position','intérêt','objectif','but','choix','erreur','doute','confiance','secret','vérité','vrai','faux','différence','relation','lien','ensemble'
]
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=42 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit07 lock/live B2 mismatch')
 rows=[]
 for p in PATHS:rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len([r for r in rows if r.get('cefr')=='B2'])!=42:raise AssertionError('expected 42 B2 passages before Unit08 probe')
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();out=[];seen=set()
 for f in CANDIDATES:
  if f in seen:continue
  seen.add(f)
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 fresh=[x for x in out if x['status']=='fresh']
 result={'status':'PASS','scope':'French B2 Unit 08 target probe','theme':'history and explanation','genres':['historical account','causal analysis','source comparison'],'b2_source_blob':blob,'prior_deliberate_targets':len(prior),'candidate_count':len(out),'fresh_count':len(fresh),'fresh':fresh,'rejected':[x for x in out if x['status']!='fresh'],'note':'Read-only candidate/source/freshness probe; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
