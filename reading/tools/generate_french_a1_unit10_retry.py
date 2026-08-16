#!/usr/bin/env python3
"""Retry Unit 10 replacing out-of-deck pluie/manteau targets with validated ciel/sac."""
from __future__ import annotations
import re
import generate_french_a1_unit10 as base

_orig_lexicon=base.lexicon
_orig_build=base.build

def recount(row):
    row['word_count']=len(row['text'].split())
    row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',row['text'])))

def lexicon():
    L=_orig_lexicon()
    if 'ciel' not in L or 'sac' not in L:
        raise AssertionError('validated ciel/sac replacement targets missing from french_top1000.csv')
    if 'pluie' in L or 'manteau' in L:
        raise AssertionError('unexpected direct pluie/manteau top1000 entry; retry assumptions are stale')
    # Temporary construction aliases only; build() below removes the wrong surface semantics.
    L['pluie']=dict(L['ciel'])
    L['manteau']=dict(L['sac'])
    return L

def replace_target(target, form, L):
    s=L[form]
    target.update({'id':base.tid(s['rank']),'form':form,'lemma':form,'intended_sense':s['sense'],
                   'part_of_speech':s['pos'],'source_rank':s['rank'],'source_lexicon':'french_top1000.csv'})

def set_q(row,qid,prompt,answer,target_ids=None):
    q=next(q for q in row['questions'] if q['id']==qid)
    a=next(a for a in row['answer_key'] if a['question_id']==qid)
    q['prompt']=prompt
    if target_ids is None:q.pop('target_ids',None)
    else:q['target_ids']=target_ids
    a['answer']=answer

def build(rows,L):
    unit=_orig_build(rows,L)
    # P01: target ciel + soleil; rain may appear incidentally but is not a deliberate target.
    p1=next(r for r in unit if r['id']=='fr-a1-u10-p01')
    p1['title']='Le ciel et le soleil'
    p1['text']='''Dimanche, Camille sort avec sa famille. Son père regarde le ciel avant de fermer la porte. Le ciel est gris au début, mais un peu de soleil reste visible entre les nuages. La famille prend un petit parapluie parce que quelques gouttes tombent encore. Après vingt minutes, le ciel devient plus clair et le soleil revient. Le père de Camille dit qu’ils peuvent continuer leur promenade. Camille observe le changement et comprend que le ciel peut changer pendant la même journée. Elle garde quand même le parapluie dans son sac, car des nuages sont encore visibles au loin.'''
    replace_target(p1['new_lexical_targets'][0],'ciel',L)
    replace_target(p1['new_lexical_targets'][1],'soleil',L)
    p1['new_lexical_targets'][0]['exposures_in_text']=base.count(p1['text'],'ciel')
    p1['new_lexical_targets'][1]['exposures_in_text']=base.count(p1['text'],'soleil')
    set_q(p1,'q1','Quel changement observe Camille dans le ciel ?','Le ciel devient plus clair et le soleil revient.')
    set_q(p1,'q3','Que signifie « ciel » dans le texte ?','L’espace visible au-dessus de nous.',[p1['new_lexical_targets'][0]['id']])
    set_q(p1,'q4','Que signifie « soleil » ici ?','L’astre lumineux visible dans le ciel et sa lumière.',[p1['new_lexical_targets'][1]['id']])
    set_q(p1,'q5','Pourquoi la famille garde-t-elle un parapluie ?','Parce que quelques gouttes tombent encore et des nuages restent visibles.')
    set_q(p1,'q6','Que signifie « ciel » ?','L’espace que l’on voit au-dessus de la terre.',[p1['new_lexical_targets'][0]['id']])
    set_q(p1,'q7','Quel type de mot est « soleil » ?','Un nom.',[p1['new_lexical_targets'][1]['id']])
    set_q(p1,'q8','Lequel désigne l’espace au-dessus de nous : « ciel » ou « soleil » ?','ciel',[p1['new_lexical_targets'][0]['id'],p1['new_lexical_targets'][1]['id']])
    set_q(p1,'q9','Complète : Je regarde le _____ au-dessus de la ville.','ciel',[p1['new_lexical_targets'][0]['id']])
    set_q(p1,'q10','Complète : Le _____ brille entre les nuages.','soleil',[p1['new_lexical_targets'][1]['id']])
    p1['grammar_targets'][0]={'id':'fr-a1-ciel-place','role':'new','description':'ciel as the visible sky'}
    p1['grammar_targets'][1]={'id':'fr-a1-soleil-weather','role':'new','description':'soleil as the sun'}
    recount(p1)

    # P05: target sac + chaussure, preserving Unit09 eau/travail review.
    p5=next(r for r in unit if r['id']=='fr-a1-u10-p05')
    p5['title']='Un sac et des chaussures'
    p5['text']='''Après son travail, Camille boit de l’eau puis rejoint sa famille devant un magasin. Elle a besoin d’un sac plus solide pour porter ses livres. Dans le magasin, elle regarde aussi une chaussure de sport, puis une autre paire. Son sac actuel est petit, alors elle choisit un grand sac avec deux poches. Elle n’a pas besoin de nouvelle chaussure aujourd’hui, donc elle n’en achète pas. La famille vérifie le prix avant de payer. En sortant, Camille met une bouteille d’eau dans son nouveau sac et voit que ses livres ont encore beaucoup de place.'''
    replace_target(p5['new_lexical_targets'][0],'sac',L)
    replace_target(p5['new_lexical_targets'][1],'chaussure',L)
    p5['new_lexical_targets'][0]['exposures_in_text']=base.count(p5['text'],'sac')
    p5['new_lexical_targets'][1]['exposures_in_text']=base.count(p5['text'],'chaussure')
    set_q(p5,'q1','Pourquoi Camille veut-elle un nouveau sac ?','Parce qu’elle a besoin d’un sac plus solide pour porter ses livres.')
    set_q(p5,'q2','Achète-t-elle une nouvelle chaussure ?','Non.')
    set_q(p5,'q3','Que signifie « sac » dans le texte ?','Un contenant souple utilisé pour transporter des objets.',[p5['new_lexical_targets'][0]['id']])
    set_q(p5,'q4','Que signifie « chaussure » ?','Un objet porté au pied.',[p5['new_lexical_targets'][1]['id']])
    set_q(p5,'q5','Pourquoi Camille n’achète-t-elle pas de chaussures ?','Parce qu’elle n’en a pas besoin aujourd’hui.')
    set_q(p5,'q6','Que signifie « chaussure » ?','Un objet que l’on porte au pied pour le protéger.',[p5['new_lexical_targets'][1]['id']])
    set_q(p5,'q7','Quel type de mot est « sac » ?','Un nom.',[p5['new_lexical_targets'][0]['id']])
    set_q(p5,'q8','Pour transporter plusieurs livres, lequel convient : « sac » ou « chaussure » ?','sac',[p5['new_lexical_targets'][0]['id'],p5['new_lexical_targets'][1]['id']])
    set_q(p5,'q9','Complète : Je mets mes livres dans mon _____.','sac',[p5['new_lexical_targets'][0]['id']])
    set_q(p5,'q10','Complète : Je mets une _____ à chaque pied.','chaussure',[p5['new_lexical_targets'][1]['id']])
    p5['grammar_targets'][0]={'id':'fr-a1-sac-container','role':'new','description':'sac as a bag for carrying objects'}
    p5['grammar_targets'][1]={'id':'fr-a1-chaussure-footwear','role':'new','description':'chaussure as footwear'}
    recount(p5)

    # P06 capstone: make the new validated target set explicit.
    p6=next(r for r in unit if r['id']=='fr-a1-u10-p06')
    p6['text']='''À la fin du niveau A1, Camille peut gérer de nombreuses situations familières avec un français simple. Elle regarde le ciel et le soleil et sait dire s’il fait froid ou chaud. Dans un magasin, elle peut demander un prix, décider d’acheter quelque chose et préparer l’argent nécessaire. Elle sait nommer un vêtement, un sac ou une chaussure. Avec les mots des unités précédentes, elle peut parler de sa famille, de son école, de son travail, de son quartier, de sa santé et de ses déplacements. Elle ne sait pas encore tout dire, mais elle peut déjà comprendre des informations simples, poser des questions et expliquer ses besoins essentiels.'''
    for t in p6['review_lexical_targets']:
        if t['form']=='pluie': t.update({'form':'ciel','id':base.tid(L['ciel']['rank'])})
        elif t['form']=='manteau': t.update({'form':'sac','id':base.tid(L['sac']['rank'])})
    set_q(p6,'q2','Quels deux éléments du ciel sont nommés ?','Le ciel et le soleil.')
    set_q(p6,'q4','Que signifie « sac » ?','Un contenant utilisé pour transporter des objets.',[base.tid(L['sac']['rank'])])
    set_q(p6,'q8','Pour le pied, lequel convient : « chaussure » ou « sac » ?','chaussure',[base.tid(L['chaussure']['rank']),base.tid(L['sac']['rank'])])
    recount(p6)
    return unit

base.lexicon=lexicon
base.build=build
base.NEW_FORMS=('ciel','soleil','froid','chaud','acheter','prix','argent','vêtement','sac','chaussure')
base.main()
