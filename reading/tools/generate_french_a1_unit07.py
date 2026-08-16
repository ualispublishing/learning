#!/usr/bin/env python3
"""Append French A1 Unit 07 (sequences 37-42) as one guarded spatial-orientation batch."""
from __future__ import annotations
import csv,json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/french/a1/passages.jsonl'; SCHEMA=ROOT/'reading/schema/passage.schema.json'; LEXICON=ROOT/'french_top1000.csv'
EXPECTED_BLOB='3389674dd9ec9a64ab105552141d2ac1b892e266'
NEW_FORMS=('près','loin','devant','derrière','entre','sous','gauche','droite','chemin','rue')

def lexicon():
 out={}
 with LEXICON.open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   form=(row.get('Front') or '').strip(); back=row.get('Back') or ''
   a=re.search(r'Rank:\s*(\d+)',back); b=re.search(r'Meaning:\s*(.+)',back); c=re.search(r'Part of speech:\s*(.+)',back)
   if form and a and b and c: out[form]={'rank':int(a.group(1)),'sense':b.group(1).strip(),'pos':c.group(1).strip()}
 return out
def tid(r): return f'fr-rank-{r:04d}'
def count(text,form): return len(re.findall(rf'(?<!\w){re.escape(form)}(?!\w)',text,flags=re.I|re.UNICODE))
def prior_index(rows):
 d={}
 for r in rows:
  for t in r.get('new_lexical_targets',[]):
   if isinstance(t,dict) and t.get('form'): d.setdefault(t['form'],[]).append(t)
 return d
def nt(form,text,L):
 s=L[form]; n=count(text,form)
 if n<1: raise AssertionError(f'{form}: invisible new target')
 return {'id':tid(s['rank']),'form':form,'lemma':form,'intended_sense':s['sense'],'part_of_speech':s['pos'],'register':'contemporary standard','variety':None,'context_strategy':['scenario_resolution'],'first_introduced':True,'exposures_in_text':n,'source_lexicon':'french_top1000.csv','source_rank':s['rank'],'beyond_base':False}
def rev(form,stage,rep,P):
 h=P.get(form,[])
 if len(h)!=1: raise AssertionError(f'{form}: expected one earlier deliberate target, got {len(h)}')
 return {'id':h[0]['id'],'form':form,'review_stage':stage,'representation':rep,'expected_exposure_number':None}
def cur(form,stage,rep,L):
 return {'id':tid(L[form]['rank']),'form':form,'review_stage':stage,'representation':rep,'expected_exposure_number':None}
def qa(items):
 q=[]; a=[]
 for i,(typ,prompt,answer,tids) in enumerate(items,1):
  qi=f'q{i}'; ai=f'a{i}'; x={'id':qi,'type':typ,'prompt':prompt,'answer_id':ai}
  if tids:x['target_ids']=tids
  q.append(x); a.append({'id':ai,'question_id':qi,'answer':answer,'explanation':''})
 return q,a
def mk(pid,seq,ptype,title,genre,domains,topics,text,new,reviews,grammar,discourse,items,speed=False):
 q,a=qa(items)
 return {'id':pid,'language':'fr','cefr':'A1','unit':7,'sequence':seq,'revision':1,'title':title,'passage_type':ptype,'genre':genre,'domains':domains,'topics':topics,'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':grammar,'discourse_targets':discourse,'questions':q,'answer_key':a,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'Generation-stage French A1 Unit 07; full multi-pass audit deferred.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French A1 Unit 07 spatial-orientation batch.','Schema, source identity, word band, local target declaration, linkage, visible review, continuity, and checkpoint invariants are enforced.']},'paired_text_group':None,'prerequisites':['French A1 Units 01-06 canonical corpus'],'difficulty_notes_internal':'A1 spatial orientation: distance, front/back, containment, left/right, route and street navigation.','reader_tags':['unit_role:'+ptype,'generation_batch','french_a1_u07']}

def build(rows,L):
 P=prior_index(rows)
 for f in NEW_FORMS:
  if f not in L: raise AssertionError(f'{f}: missing from french_top1000.csv')
  if P.get(f): raise AssertionError(f'{f}: already deliberately introduced')
 out=[]
 text='''Après l’école, Camille regarde un petit plan du quartier avec Sami. La bibliothèque est près de leur école : ils peuvent y aller en cinq minutes. Le grand parc est plus loin et demande beaucoup de marche. Camille préfère commencer par un lieu près d’eux parce qu’ils ont peu de temps avant le dîner. Sami montre aussi un café sur le plan, mais il est assez loin. Ils décident donc d’aller à la bibliothèque. En marchant, Camille compare les distances et comprend qu’un lieu peut sembler proche sur une carte, mais être plus loin quand les rues ne vont pas directement vers lui.'''
 a,b=nt('près',text,L),nt('loin',text,L)
 out.append(mk('fr-a1-u07-p01',37,'instructional','Près ou loin ?','map-reading narrative',['public','educational'],['map','distance','neighborhood'],text,[a,b],[rev('beaucoup','R2','running_text',P),rev('peu','R2','running_text',P)],[{'id':'fr-a1-pres-distance','role':'new','description':'près for short distance'},{'id':'fr-a1-loin-distance','role':'new','description':'loin for greater distance'}],[{'id':'fr-a1-distance-choice','role':'new','description':'compare two destinations by distance'}],[('gist','Quel lieu Camille et Sami choisissent-ils ?','La bibliothèque.',[]),('literal_detail','Combien de minutes faut-il pour aller à la bibliothèque ?','Cinq minutes.',[]),('vocabulary_in_context','Que signifie « près » dans « près de leur école » ?','À une courte distance.',[a['id']]),('vocabulary_in_context','Que signifie « loin » pour le parc ?','À une distance plus grande.',[b['id']]),('cause_effect','Pourquoi choisissent-ils la bibliothèque ?','Parce qu’elle est près et qu’ils ont peu de temps.',[]),('single_word_definition','Que signifie « loin » ?','À grande distance.',[b['id']]),('grammar_function','Dans « près de l’école », quel rôle joue « près de » ?','Il indique une proximité de lieu.',[a['id']]),('contrast','Pour une courte distance, lequel convient : « près » ou « loin » ?','près',[a['id'],b['id']]),('cloze_transfer','Complète : La boulangerie est _____ de chez moi.','près',[a['id']]),('cloze_transfer','Complète : Cette ville est très _____.','loin',[b['id']])]))

 text='''Le lendemain, la classe attend devant le gymnase. La porte est déjà ouverte, mais le professeur demande aux élèves de rester devant le bâtiment quelques minutes. Camille voit trop de sacs près de l’entrée et propose de les déplacer. Elle met son sac derrière un banc, où il ne bloque pas le passage. Sami place le sien derrière celui de Camille. Quand le professeur appelle le groupe, les élèves entrent. Camille regarde encore devant elle pour vérifier que personne ne reste dehors. Après l’activité, elle retrouve facilement son sac derrière le banc. Elle remarque que « devant » et « derrière » permettent de décrire clairement la position de deux choses.'''
 a,b=nt('devant',text,L),nt('derrière',text,L)
 out.append(mk('fr-a1-u07-p02',38,'reinforcement','Devant le gymnase','school-position narrative',['educational'],['school','position','objects'],text,[a,b],[rev('trop','R2','running_text',P),rev('déjà','R2','running_text',P)],[{'id':'fr-a1-devant-position','role':'new','description':'devant for a position in front'},{'id':'fr-a1-derriere-position','role':'new','description':'derrière for a position at the back'}],[{'id':'fr-a1-relative-position','role':'new','description':'locate objects relative to a building or object'}],[('gist','Où la classe attend-elle ?','Devant le gymnase.',[]),('literal_detail','Où Camille met-elle son sac ?','Derrière un banc.',[]),('vocabulary_in_context','Que signifie « devant » dans « devant le bâtiment » ?','Du côté de la façade ou de l’avant du bâtiment.',[a['id']]),('vocabulary_in_context','Que signifie « derrière » dans « derrière un banc » ?','Du côté opposé à l’avant, à l’arrière du banc.',[b['id']]),('cause_effect','Pourquoi Camille déplace-t-elle son sac ?','Parce qu’il y a trop de sacs près de l’entrée et qu’ils bloquent le passage.',[]),('single_word_definition','Que signifie « derrière » ?','À l’arrière de quelque chose.',[b['id']]),('grammar_function','Dans « devant le gymnase », que précise « devant » ?','La position du groupe.',[a['id']]),('contrast','Si le sac est à l’arrière du banc, lequel convient : « derrière » ou « devant » ?','derrière',[a['id'],b['id']]),('cloze_transfer','Complète : J’attends _____ la porte.','devant',[a['id']]),('cloze_transfer','Complète : Le jardin est _____ la maison.','derrière',[b['id']])]))

 text='''Au parc, Camille et Sami cherchent un endroit calme. Ils voient deux grands arbres avec un banc entre eux. Camille s’assoit sur le banc et Sami aussi. Sous le banc, ils remarquent une petite balle rouge. Camille regarde autour d’elle : un enfant joue avec le même type de balle plus loin. Elle lui demande si la balle sous le banc est à lui. L’enfant répond oui et vient la prendre. Camille trouve aussi une feuille entre deux pierres et la met dans une poubelle. Elle explique à Sami que « entre » montre une position au milieu de deux choses, tandis que « sous » indique une position plus basse.'''
 a,b=nt('entre',text,L),nt('sous',text,L)
 out.append(mk('fr-a1-u07-p03',39,'interleaved','Entre les arbres','park-location narrative',['public','personal'],['park','objects','spatial relations'],text,[a,b],[rev('aussi','R2','running_text',P),rev('même','R2','running_text',P)],[{'id':'fr-a1-entre-middle','role':'new','description':'entre for a middle position'},{'id':'fr-a1-sous-lower','role':'new','description':'sous for a lower position'}],[{'id':'fr-a1-locate-small-object','role':'new','description':'locate small objects relative to other objects'}],[('gist','Qu’est-ce que Camille et Sami trouvent sous le banc ?','Une petite balle rouge.',[]),('literal_detail','Où se trouve le banc ?','Entre deux grands arbres.',[]),('vocabulary_in_context','Que signifie « entre » dans « entre deux arbres » ?','Au milieu des deux arbres.',[a['id']]),('vocabulary_in_context','Que signifie « sous » dans « sous le banc » ?','Dans une position plus basse que le banc.',[b['id']]),('reference_resolution','À qui appartient la balle ?','À un enfant qui joue plus loin.',[]),('single_word_definition','Que signifie « sous » ?','Plus bas que quelque chose.',[b['id']]),('grammar_function','Quelle relation exprime « entre » ?','Une position au milieu de deux éléments.',[a['id']]),('contrast','Pour une balle plus basse que le banc, lequel convient : « sous » ou « entre » ?','sous',[a['id'],b['id']]),('cloze_transfer','Complète : La chaise est _____ la table et la fenêtre.','entre',[a['id']]),('cloze_transfer','Complète : Le chat dort _____ la table.','sous',[b['id']])]))

 text='''Camille va souvent à pied de l’école à la bibliothèque, mais elle ne prend jamais une petite rue qu’elle ne connaît pas. Aujourd’hui, Sami lui montre un itinéraire simple. Au premier carrefour, ils tournent à gauche. Après la boulangerie, ils tournent à droite. Camille répète : « gauche, puis droite ». Elle regarde les magasins pour garder des repères. À un autre carrefour, Sami lui demande quel côté choisir. Camille répond « à gauche » sans hésiter. Ils arrivent bientôt devant la bibliothèque. Camille est contente : elle sait maintenant distinguer la gauche et la droite dans un trajet réel, pas seulement sur un dessin.'''
 a,b=nt('gauche',text,L),nt('droite',text,L)
 out.append(mk('fr-a1-u07-p04',40,'transfer','À gauche, puis à droite','walking-directions narrative',['public'],['directions','walking','left/right'],text,[a,b],[rev('souvent','R2','running_text',P),rev('jamais','R2','running_text',P)],[{'id':'fr-a1-gauche-direction','role':'new','description':'gauche for the left direction'},{'id':'fr-a1-droite-direction','role':'new','description':'droite for the right direction'}],[{'id':'fr-a1-follow-turns','role':'new','description':'follow a two-turn route'}],[('gist','Quel trajet Camille apprend-elle ?','Le trajet à pied de l’école à la bibliothèque.',[]),('literal_detail','De quel côté tournent-ils au premier carrefour ?','À gauche.',[]),('vocabulary_in_context','Que signifie « gauche » dans « tourner à gauche » ?','Le côté gauche.',[a['id']]),('vocabulary_in_context','Que signifie « droite » dans « tourner à droite » ?','Le côté droit.',[b['id']]),('sequence','Quel est l’ordre des deux premiers changements de direction ?','Gauche, puis droite.',[]),('single_word_definition','Que signifie « droite » ici ?','Le côté droit.',[b['id']]),('grammar_function','Dans « à gauche », que précise l’expression ?','La direction du déplacement.',[a['id']]),('contrast','Si on ne tourne pas à gauche mais de l’autre côté, lequel convient ?','droite',[a['id'],b['id']]),('cloze_transfer','Complète : Tourne à _____ après le café.','gauche',[a['id']]),('cloze_transfer','Complète : La pharmacie est à _____.','droite',[b['id']])]))

 text='''Camille est maintenant près du centre de la ville. Elle doit rejoindre sa mère bientôt dans une grande rue commerçante. Sur le plan, deux chemins sont possibles. Le premier chemin suit une rue très animée. Le second passe par un petit parc et rejoint la même rue plus loin. Camille choisit le chemin du parc parce qu’il est plus calme. Elle marche jusqu’à une fontaine, puis suit les panneaux vers la rue principale. Bientôt, elle voit sa mère devant un magasin. Sa mère lui demande quel chemin elle a pris. Camille décrit simplement le parc, la fontaine et la rue. Elle comprend qu’un chemin est l’itinéraire suivi pour aller d’un lieu à un autre.'''
 a,b=nt('chemin',text,L),nt('rue',text,L)
 out.append(mk('fr-a1-u07-p05',41,'integration','Le chemin vers la grande rue','route-choice narrative',['public','personal'],['route','street','city'],text,[a,b],[rev('maintenant','R2','running_text',P),rev('bientôt','R2','running_text',P)],[{'id':'fr-a1-chemin-route','role':'new','description':'chemin as a path or route'},{'id':'fr-a1-rue-public-way','role':'new','description':'rue as a street'}],[{'id':'fr-a1-route-choice','role':'new','description':'choose and describe a simple route'}],[('gist','Pourquoi Camille choisit-elle le chemin du parc ?','Parce qu’il est plus calme.',[]),('literal_detail','Où voit-elle sa mère ?','Devant un magasin dans la rue principale.',[]),('vocabulary_in_context','Que signifie « chemin » dans le texte ?','L’itinéraire ou le passage suivi pour aller quelque part.',[a['id']]),('vocabulary_in_context','Que signifie « rue » ?','Une voie dans la ville bordée de bâtiments ou de lieux publics.',[b['id']]),('sequence','Quels repères Camille suit-elle avant d’arriver ?','Le parc, une fontaine, puis la rue principale.',[]),('single_word_definition','Que signifie « chemin » ici ?','Une route ou un itinéraire suivi.',[a['id']]),('grammar_category','Quel type de mot est « rue » ?','Un nom.',[b['id']]),('contrast','Pour parler de l’itinéraire choisi, lequel convient : « chemin » ou « rue » ?','chemin',[a['id'],b['id']]),('cloze_transfer','Complète : Ce _____ mène au parc.','chemin',[a['id']]),('cloze_transfer','Complète : Le magasin est dans cette _____.','rue',[b['id']])]))

 text='''Camille sait maintenant décrire un trajet avec plus de précision. Un lieu peut être près ou loin. Elle peut attendre devant une porte et laisser son vélo derrière un mur. Au parc, un banc peut être entre deux arbres et une balle sous le banc. Quand elle marche, elle sait tourner à gauche ou à droite. Elle peut choisir un chemin calme ou suivre une grande rue. Ces mots lui permettent de comprendre des indications simples, de demander son chemin et d’expliquer où se trouve un objet. Elle regarde encore les repères autour d’elle, mais elle dépend moins du plan qu’avant.'''
 reviews=[cur(f,'R1','summary',L) for f in NEW_FORMS]
 out.append(mk('fr-a1-u07-p06',42,'checkpoint','Décrire un trajet','cumulative spatial summary',['public','personal'],['directions','location','route'],text,[],reviews,[{'id':'fr-a1-u07-spatial-review','role':'integration','description':'integrate basic spatial prepositions and direction words'}],[{'id':'fr-a1-u07-route-summary','role':'integration','description':'summarize a simple route and object positions'}],[('gist','Quelle compétence Camille a-t-elle développée ?','Elle sait mieux décrire les positions et les trajets.',[]),('literal_detail','Que peut-elle faire à un carrefour ?','Tourner à gauche ou à droite.',[]),('vocabulary_in_context','Que signifie « derrière » dans le résumé ?','À l’arrière de quelque chose.',[tid(L['derrière']['rank'])]),('vocabulary_in_context','Que signifie « entre » ?','Au milieu de deux éléments.',[tid(L['entre']['rank'])]),('reference_resolution','À quoi servent les repères autour de Camille ?','À l’aider à suivre et expliquer son trajet.',[]),('single_word_definition','Que signifie « rue » ?','Une voie publique dans une ville.',[tid(L['rue']['rank'])]),('grammar_function','Dans « sous le banc », que précise « sous » ?','La position de la balle par rapport au banc.',[tid(L['sous']['rank'])]),('contrast','Pour le côté opposé à gauche, lequel convient ?','droite',[tid(L['gauche']['rank']),tid(L['droite']['rank'])]),('cloze_transfer','Complète : Le parc est _____ de l’école ; il faut deux minutes.','près',[tid(L['près']['rank'])]),('summary','Résume en une phrase comment Camille décrit maintenant un trajet.','Elle utilise des mots de distance, de position et de direction pour expliquer où aller et où se trouvent les choses.',[])],speed=True))
 return out

def main():
 blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
 if blob!=EXPECTED_BLOB: raise AssertionError(f'canonical blob drift: {blob} != {EXPECTED_BLOB}')
 rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=36 or [r['sequence'] for r in rows]!=list(range(1,37)) or rows[-1]['id']!='fr-a1-u06-p06': raise AssertionError('expected exact 36-passage frontier through Unit 06')
 L=lexicon(); unit=build(rows,L); V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
 if [r['sequence'] for r in unit]!=list(range(37,43)) or len({r['id'] for r in rows+unit})!=42: raise AssertionError('Unit 07 continuity failure')
 old={t['id'] for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
 for r in unit:
  e=sorted(V.iter_errors(r),key=lambda x:list(x.path))
  if e: raise AssertionError(f"{r['id']}: schema {[x.message for x in e[:5]]}")
  if not 90<=r['word_count']<=140: raise AssertionError(f"{r['id']}: word band {r['word_count']}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
  amap={a['question_id']:a['id'] for a in r['answer_key']}; declared={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict)}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id']: raise AssertionError(f"{r['id']} {q['id']}: linkage")
   if any(x not in declared for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} {q['id']}: undeclared target")
  for t in r['new_lexical_targets']:
   s=L.get(t['form'])
   if t['id'] in old or not s or t['source_rank']!=s['rank'] or t['id']!=tid(s['rank']): raise AssertionError(f"{r['id']}: source/reintroduction drift {t}")
   if count(r['text'],t['form'])!=t['exposures_in_text']: raise AssertionError(f"{r['id']}: exposure drift {t['form']}")
  for t in r['review_lexical_targets']:
   if t['representation'] in {'running_text','summary'} and count(r['text'],t['form'])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
 if sum(len(r['new_lexical_targets']) for r in unit[:5])!=10 or unit[-1]['new_lexical_targets']!=[]: raise AssertionError('Unit 07 lexical-cycle invariant')
 CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows+unit),encoding='utf-8')
 print(json.dumps({'status':'PASS','unit':7,'appended_passages':6,'sequences':list(range(37,43)),'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':[{'form':f,'rank':L[f]['rank'],'id':tid(L[f]['rank'])} for f in NEW_FORMS],'checkpoint_new_targets':0,'questions':60,'answers':60},ensure_ascii=False))
if __name__=='__main__': main()
