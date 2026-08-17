#!/usr/bin/env python3
"""Persist source/freshness probe for B2 Unit07: arts and interpretation.

Authoritative Unit07 probe trigger. Read-only against canonical passage data.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit06_frontier_lock.json';OUT=R/'reading/audit/french_b2_unit07_target_probe.json'
PATHS=[R/'reading/french/a1/passages.jsonl',R/'reading/french/a2/passages.jsonl',R/'reading/french/b1/passages.jsonl',B2]
CANDIDATES=[
 'art','artiste','œuvre','tableau','peinture','peindre','dessin','dessiner','image','photo','couleur','forme','ligne','scène','spectacle','théâtre','film','cinéma','acteur','rôle',
 'musique','chanson','son','voix','silence','rythme','danse','danser','jouer','instrument','livre','roman','poème','poésie','texte','auteur','écrivain','histoire','personnage',
 'lecture','lire','écrire','écriture','mot','phrase','langue','style','ton','sens','signification','signifier','idée','thème','sujet','message','symbole','représenter','montrer','cacher',
 'interpréter','interprétation','comprendre','penser','croire','imaginer','sentir','sentiment','impression','émotion','avis','opinion','juger','critique','critiquer','préférer','aimer','apprécier','intéresser',
 'beau','joli','fort','faible','simple','difficile','clair','sombre','original','nouveau','ancien','moderne','classique','réel','vrai','faux','étrange','drôle','sérieux','important',
 'public','spectateur','lecteur','auditeur','groupe','personne','artiste','créateur','création','créer','travail','projet','carrière','vie','époque','temps','passé','présent','futur',
 'contexte','culture','culturel','société','politique','religion','tradition','mémoire','guerre','pays','monde','ville','famille','classe','école','musée','galerie','collection','archive',
 'comparer','comparaison','différent','pareil','ressembler','opposer','contraste','relation','lien','cause','effet','raison','preuve','exemple','détail','partie','ensemble','début','fin',
 'choisir','choix','décider','garder','changer','transformer','utiliser','servir','donner','recevoir','produire','présenter','publier','expliquer','décrire','raconter','reconnaître','remarquer',
 'succès','réussir','prix','valeur','marché','vendre','acheter','publicité','argent','libre','droit','copie','original','version','édition','traduction','traduire','performance','présence',
 'cadre','portrait','mouvement','lumière','ombre','espace','corps','geste','main','visage','regard','œil','position','distance','proche','loin','haut','bas','centre','bord'
]
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=36 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit06 lock/live B2 mismatch')
 rows=[]
 for p in PATHS:rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len([r for r in rows if r.get('cefr')=='B2'])!=36:raise AssertionError('expected 36 B2 passages before Unit07 probe')
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();out=[];seen=set()
 for f in CANDIDATES:
  if f in seen:continue
  seen.add(f)
  if f not in deck:status='missing_lexicon';rank=None;tid=None;meaning=None
  else:
   rank=deck[f]['rank'];tid=base.tid(rank);meaning=deck[f].get('meaning');status='fresh' if f not in forms and tid not in ids else 'already_deliberate'
  out.append({'form':f,'status':status,'rank':rank,'id':tid,'meaning':meaning})
 fresh=[x for x in out if x['status']=='fresh']
 result={'status':'PASS','scope':'French B2 Unit 07 target probe','theme':'arts and interpretation','genres':['review','profile','critical comparison'],'b2_source_blob':blob,'prior_deliberate_targets':len(prior),'candidate_count':len(out),'fresh_count':len(fresh),'fresh':fresh,'rejected':[x for x in out if x['status']!='fresh'],'note':'Read-only candidate/source/freshness probe; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
