#!/usr/bin/env python3
"""Append French A1 Unit 08 (sequences 43-48): simple body/health routines."""
from __future__ import annotations
import csv,json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/french/a1/passages.jsonl'; SCHEMA=ROOT/'reading/schema/passage.schema.json'; LEXICON=ROOT/'french_top1000.csv'
EXPECTED_BLOB='fcca7145dbaf11dd71e25d8186fd2811e2c37a86'
NEW_FORMS=('tête','main','pied','corps','manger','boire','dormir','sentir','malade','mieux')

def lexicon():
 out={}
 with LEXICON.open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   x=(row.get('Front') or '').strip(); b=row.get('Back') or ''
   a=re.search(r'Rank:\s*(\d+)',b); m=re.search(r'Meaning:\s*(.+)',b); p=re.search(r'Part of speech:\s*(.+)',b)
   if x and a and m and p: out[x]={'rank':int(a.group(1)),'sense':m.group(1).strip(),'pos':p.group(1).strip()}
 return out
def tid(r):return f'fr-rank-{r:04d}'
def count(text,f):return len(re.findall(rf'(?<!\w){re.escape(f)}(?!\w)',text,flags=re.I|re.UNICODE))
def prior(rows):
 d={}
 for r in rows:
  for t in r.get('new_lexical_targets',[]):
   if isinstance(t,dict) and t.get('form'):d.setdefault(t['form'],[]).append(t)
 return d
def nt(f,text,L):
 s=L[f]; n=count(text,f)
 if n<1:raise AssertionError(f'{f}: invisible new target')
 return {'id':tid(s['rank']),'form':f,'lemma':f,'intended_sense':s['sense'],'part_of_speech':s['pos'],'register':'contemporary standard','variety':None,'context_strategy':['scenario_resolution'],'first_introduced':True,'exposures_in_text':n,'source_lexicon':'french_top1000.csv','source_rank':s['rank'],'beyond_base':False}
def rev(f,stage,rep,P):
 h=P.get(f,[])
 if len(h)!=1:raise AssertionError(f'{f}: prior target count={len(h)}')
 return {'id':h[0]['id'],'form':f,'review_stage':stage,'representation':rep,'expected_exposure_number':None}
def cur(f,L):return {'id':tid(L[f]['rank']),'form':f,'review_stage':'R1','representation':'summary','expected_exposure_number':None}
def qa(items):
 q=[];a=[]
 for i,(ty,p,ans,ids) in enumerate(items,1):
  qi=f'q{i}';ai=f'a{i}';x={'id':qi,'type':ty,'prompt':p,'answer_id':ai}
  if ids:x['target_ids']=ids
  q.append(x);a.append({'id':ai,'question_id':qi,'answer':ans,'explanation':''})
 return q,a
def mk(pid,seq,ptype,title,text,new,reviews,items,speed=False):
 q,a=qa(items)
 return {'id':pid,'language':'fr','cefr':'A1','unit':8,'sequence':seq,'revision':1,'title':title,'passage_type':ptype,'genre':'everyday health narrative','domains':['personal'],'topics':['health','daily routine'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':[{'id':'fr-a1-u08-basic-health-language','role':'integration' if speed else 'new','description':'use simple body, routine, and condition language'}],'discourse_targets':[{'id':'fr-a1-u08-cause-action','role':'integration' if speed else 'new','description':'connect a simple physical state to an everyday action'}],'questions':q,'answer_key':a,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'Generation-stage French A1 Unit 08; full multi-pass audit deferred.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French A1 Unit 08 generation batch.','Schema/source/band/linkage/review/checkpoint invariants enforced during generation.']},'paired_text_group':None,'prerequisites':['French A1 Units 01-07 canonical corpus'],'difficulty_notes_internal':'A1 body parts, eating/drinking, sleep/feeling, simple illness and recovery.','reader_tags':['unit_role:'+ptype,'generation_batch','french_a1_u08']}
def build(rows,L):
 P=prior(rows)
 for f in NEW_FORMS:
  if f not in L:raise AssertionError(f'{f}: missing from french_top1000.csv')
  if P.get(f):raise AssertionError(f'{f}: already deliberately introduced')
 out=[]
 text='''Après une longue matinée, Camille a un peu mal à la tête. Elle est près de l’école et sa maison n’est pas loin, alors elle décide de rentrer tranquillement. Dans la cuisine, elle pose une main sur son front et boit un verre d’eau. Sa mère lui demande si sa tête fait encore mal. Camille répond que oui, mais moins qu’avant. Elle lave ensuite chaque main avant de préparer une petite collation. Après vingt minutes au calme, elle se sent déjà mieux. Elle comprend qu’elle doit parfois arrêter une activité, boire de l’eau et laisser sa tête se reposer quelques minutes.'''
 a,b=nt('tête',text,L),nt('main',text,L)
 out.append(mk('fr-a1-u08-p01',43,'instructional','Un peu mal à la tête',text,[a,b],[rev('près','R2','running_text',P),rev('loin','R2','running_text',P)],[('gist','Pourquoi Camille rentre-t-elle chez elle ?','Parce qu’elle a un peu mal à la tête.',[]),('literal_detail','Que boit-elle ?','Un verre d’eau.',[]),('vocabulary_in_context','Que désigne « tête » dans le texte ?','La partie du corps au-dessus du cou.',[a['id']]),('vocabulary_in_context','Que désigne « main » ?','La partie au bout du bras avec les doigts.',[b['id']]),('cause_effect','Pourquoi Camille reste-t-elle au calme ?','Pour laisser sa tête se reposer.',[]),('single_word_definition','Que signifie « tête » ?','La partie supérieure du corps avec le visage et le cerveau.',[a['id']]),('grammar_category','Quel type de mot est « main » ?','Un nom.',[b['id']]),('contrast','Laquelle est au bout du bras : la « main » ou la « tête » ?','La main.',[a['id'],b['id']]),('cloze_transfer','Complète : Je tiens le crayon dans ma _____.','main',[b['id']]),('cloze_transfer','Complète : Je mets un chapeau sur ma _____.','tête',[a['id']])]))
 text='''Pendant le cours de sport, Camille court devant Sami puis ralentit derrière un autre groupe. Après plusieurs tours, son pied droit commence à être fatigué. Elle s’arrête et regarde son pied : rien ne semble grave. Le professeur explique que tout le corps a besoin de pauses quand on fait beaucoup d’exercice. Camille marche lentement pendant quelques minutes. Elle bouge son pied sans douleur et respire calmement. Son corps se repose, puis elle peut reprendre une activité plus douce. Elle ne court pas encore. Elle comprend qu’écouter son corps ne signifie pas arrêter toujours, mais choisir un effort adapté à ce qu’on ressent.'''
 a,b=nt('pied',text,L),nt('corps',text,L)
 out.append(mk('fr-a1-u08-p02',44,'reinforcement','Écouter son corps',text,[a,b],[rev('devant','R2','running_text',P),rev('derrière','R2','running_text',P)],[('gist','Pourquoi Camille s’arrête-t-elle ?','Parce que son pied droit commence à être fatigué.',[]),('literal_detail','Que fait-elle pendant quelques minutes ?','Elle marche lentement.',[]),('vocabulary_in_context','Que signifie « pied » ici ?','La partie du corps au bout de la jambe.',[a['id']]),('vocabulary_in_context','Que signifie « corps » ?','L’ensemble physique d’une personne.',[b['id']]),('inference','Pourquoi ne recommence-t-elle pas tout de suite à courir ?','Elle veut laisser son corps et son pied récupérer.',[]),('single_word_definition','Que signifie « corps » ?','L’ensemble physique d’une personne.',[b['id']]),('grammar_category','Quel type de mot est « pied » ?','Un nom.',[a['id']]),('contrast','Lequel désigne l’ensemble physique : « corps » ou « pied » ?','corps',[a['id'],b['id']]),('cloze_transfer','Complète : Ma chaussure est sur mon _____.','pied',[a['id']]),('cloze_transfer','Complète : Après le sport, mon _____ a besoin de repos.','corps',[b['id']])]))
 text='''À midi, Camille s’assoit entre Sami et une autre élève. Sous la table, leurs sacs sont bien rangés. Camille veut manger son sandwich avant de boire son jus. Sami préfère boire d’abord, puis manger. Camille mange lentement parce qu’elle a encore un peu mal à la tête. Elle boit aussi beaucoup d’eau. Après le repas, elle remarque qu’elle a plus d’énergie. Sami lui demande ce qu’elle préfère manger le matin. Camille répond qu’elle aime manger du pain et un fruit, puis boire de l’eau ou du lait. Ils parlent ainsi de leurs habitudes sans dire qu’une seule façon est correcte pour tout le monde.'''
 a,b=nt('manger',text,L),nt('boire',text,L)
 out.append(mk('fr-a1-u08-p03',45,'interleaved','Manger et boire',text,[a,b],[rev('entre','R2','running_text',P),rev('sous','R2','running_text',P)],[('gist','De quoi parlent Camille et Sami ?','De leurs habitudes pour manger et boire.',[]),('literal_detail','Que boit beaucoup Camille ?','De l’eau.',[]),('vocabulary_in_context','Que signifie « manger » ?','Prendre de la nourriture.',[a['id']]),('vocabulary_in_context','Que signifie « boire » ?','Prendre un liquide.',[b['id']]),('sequence','Que fait Camille avec son sandwich et son jus ?','Elle mange son sandwich avant de boire son jus.',[]),('single_word_definition','Que signifie « boire » ?','Prendre un liquide par la bouche.',[b['id']]),('grammar_category','Quel type de mot est « manger » ?','Un verbe.',[a['id']]),('contrast','Pour l’eau, quel verbe convient : « boire » ou « manger » ?','boire',[a['id'],b['id']]),('cloze_transfer','Complète : Je vais _____ une pomme.','manger',[a['id']]),('cloze_transfer','Complète : Il faut _____ de l’eau.','boire',[b['id']])]))
 text='''Le soir, Camille prépare sa chambre avant de dormir. Son lit est à gauche de la fenêtre et sa lampe est à droite. Elle veut dormir assez longtemps parce qu’elle a école le lendemain. Avant de se coucher, elle ferme son livre et éteint son téléphone. Elle commence à sentir la fatigue : ses yeux sont lourds et elle bâille. Camille sait qu’elle peut sentir la fatigue avant d’être complètement épuisée. Elle se couche donc à une heure raisonnable. Le matin suivant, elle se réveille sans difficulté. Elle dit à sa mère qu’elle a bien dormi et qu’elle se sent prête pour la journée.'''
 a,b=nt('dormir',text,L),nt('sentir',text,L)
 out.append(mk('fr-a1-u08-p04',46,'transfer','Prête à dormir',text,[a,b],[rev('gauche','R2','running_text',P),rev('droite','R2','running_text',P)],[('gist','Pourquoi Camille se couche-t-elle à une heure raisonnable ?','Parce qu’elle veut dormir assez avant l’école.',[]),('literal_detail','Où est sa lampe ?','À droite.',[]),('vocabulary_in_context','Que signifie « dormir » ?','Être dans l’état de sommeil.',[a['id']]),('vocabulary_in_context','Que signifie « sentir » dans « sentir la fatigue » ?','Percevoir ou ressentir la fatigue.',[b['id']]),('cause_effect','Quel signe montre que Camille sent la fatigue ?','Ses yeux sont lourds et elle bâille.',[]),('single_word_definition','Que signifie « dormir » ?','Être endormi, se reposer pendant le sommeil.',[a['id']]),('grammar_category','Quel type de mot est « sentir » ?','Un verbe.',[b['id']]),('contrast','Pour percevoir la fatigue, lequel convient : « sentir » ou « dormir » ?','sentir',[a['id'],b['id']]),('cloze_transfer','Complète : Je vais _____ huit heures cette nuit.','dormir',[a['id']]),('cloze_transfer','Complète : Je peux _____ l’air froid sur mon visage.','sentir',[b['id']])]))
 text='''Un samedi matin, Camille se sent malade et reste à la maison. Elle devait suivre un chemin vers le marché, mais elle préfère ne pas sortir dans la rue. Elle a le nez bouché et un peu de fièvre. Sa mère lui prépare de l’eau et une soupe légère. Camille dort une partie de la matinée. Après le déjeuner, elle se sent déjà mieux. Elle n’est pas encore complètement en forme, mais elle peut lire quelques pages et parler avec son frère. Le lendemain, Camille va mieux : elle n’a plus de fièvre. Elle décide quand même de reprendre ses activités doucement et de ne pas courir tout de suite.'''
 a,b=nt('malade',text,L),nt('mieux',text,L)
 out.append(mk('fr-a1-u08-p05',47,'integration','Malade, puis mieux',text,[a,b],[rev('chemin','R2','running_text',P),rev('rue','R2','running_text',P)],[('gist','Pourquoi Camille reste-t-elle à la maison ?','Parce qu’elle se sent malade.',[]),('literal_detail','Quel symptôme disparaît le lendemain ?','La fièvre.',[]),('vocabulary_in_context','Que signifie « malade » ici ?','En mauvaise santé, avec des symptômes.',[a['id']]),('vocabulary_in_context','Que signifie « mieux » dans « elle se sent mieux » ?','Dans un meilleur état qu’avant.',[b['id']]),('sequence','Que fait Camille après avoir dormi ?','Elle se sent mieux, lit un peu et parle avec son frère.',[]),('single_word_definition','Que signifie « mieux » ?','Dans de meilleures conditions ou un meilleur état.',[b['id']]),('grammar_category','Quel type de mot est « malade » dans « Camille est malade » ?','Un adjectif.',[a['id']]),('contrast','Quand la santé s’améliore, lequel convient : « mieux » ou « malade » ?','mieux',[a['id'],b['id']]),('cloze_transfer','Complète : Il reste à la maison parce qu’il est _____.','malade',[a['id']]),('cloze_transfer','Complète : Après une bonne nuit, je me sens _____.','mieux',[b['id']])]))
 text='''Camille connaît maintenant plusieurs mots simples pour parler de son corps et de ses habitudes. Sa tête, sa main et son pied sont des parties de son corps. Pour avoir de l’énergie, elle doit manger, boire et dormir assez. Elle peut sentir la fatigue ou remarquer qu’elle est malade. Après du repos, elle peut se sentir mieux. Ces mots ne remplacent pas un conseil médical, mais ils l’aident à décrire une situation quotidienne : où elle a mal, ce qu’elle fait pour se reposer et si son état change. Camille apprend surtout à expliquer clairement ce qu’elle ressent avec des phrases simples.'''
 reviews=[cur(f,L) for f in NEW_FORMS]
 out.append(mk('fr-a1-u08-p06',48,'checkpoint','Parler simplement de sa santé',text,[],reviews,[('gist','Quelle est l’idée principale du texte ?','Camille sait mieux parler simplement de son corps, de ses habitudes et de son état.',[]),('literal_detail','Quelles trois parties du corps sont nommées ?','La tête, la main et le pied.',[]),('vocabulary_in_context','Que signifie « corps » dans le résumé ?','L’ensemble physique d’une personne.',[tid(L['corps']['rank'])]),('vocabulary_in_context','Que signifie « mieux » ?','Dans un meilleur état qu’avant.',[tid(L['mieux']['rank'])]),('cause_effect','Pourquoi Camille mange-t-elle, boit-elle et dort-elle assez ?','Pour avoir de l’énergie et se reposer.',[]),('single_word_definition','Que signifie « malade » ?','En mauvaise santé.',[tid(L['malade']['rank'])]),('grammar_function','Dans « se sentir mieux », que décrit « mieux » ?','Une amélioration de l’état.',[tid(L['mieux']['rank'])]),('contrast','Pour un liquide, lequel convient : « boire » ou « manger » ?','boire',[tid(L['boire']['rank']),tid(L['manger']['rank'])]),('cloze_transfer','Complète : Après le sport, je veux _____ un peu.','dormir',[tid(L['dormir']['rank'])]),('summary','Résume en une phrase ce que Camille peut maintenant expliquer.','Elle peut nommer quelques parties du corps et décrire des habitudes ou un état de santé simple.',[])],speed=True))
 return out

def main():
 blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
 if blob!=EXPECTED_BLOB:raise AssertionError(f'canonical blob drift: {blob} != {EXPECTED_BLOB}')
 rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=42 or [r['sequence'] for r in rows]!=list(range(1,43)) or rows[-1]['id']!='fr-a1-u07-p06':raise AssertionError('expected 42-passage frontier through Unit 07')
 L=lexicon();unit=build(rows,L);V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')));old={t['id'] for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
 if [r['sequence'] for r in unit]!=list(range(43,49)) or len({r['id'] for r in rows+unit})!=48:raise AssertionError('continuity failure')
 for r in unit:
  e=sorted(V.iter_errors(r),key=lambda x:list(x.path))
  if e:raise AssertionError(f"{r['id']}: schema {[x.message for x in e[:5]]}")
  if not 90<=r['word_count']<=140:raise AssertionError(f"{r['id']}: word band {r['word_count']}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: assessment count")
  amap={a['question_id']:a['id'] for a in r['answer_key']};decl={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict)}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in decl for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage/target declaration")
  for t in r['new_lexical_targets']:
   s=L.get(t['form'])
   if t['id'] in old or not s or t['source_rank']!=s['rank'] or t['id']!=tid(s['rank']) or count(r['text'],t['form'])!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: target/source/exposure drift {t}")
  for t in r['review_lexical_targets']:
   if t['representation'] in {'running_text','summary'} and count(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
 if sum(len(r['new_lexical_targets']) for r in unit[:5])!=10 or unit[-1]['new_lexical_targets']!=[]:raise AssertionError('lexical cycle invariant')
 CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows+unit),encoding='utf-8')
 print(json.dumps({'status':'PASS','unit':8,'appended_passages':6,'sequences':list(range(43,49)),'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':L[f]['rank'],'id':tid(L[f]['rank'])} for f in NEW_FORMS],'checkpoint_new_targets':0,'questions':60,'answers':60},ensure_ascii=False))
if __name__=='__main__':main()
