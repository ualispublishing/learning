#!/usr/bin/env python3
"""Append French A1 Unit 03 (sequences 13-18) as one guarded batch."""
from __future__ import annotations

import csv, json, re, subprocess
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/french/a1/passages.jsonl'
SCHEMA=ROOT/'reading/schema/passage.schema.json'
LEXICON=ROOT/'french_top1000.csv'
EXPECTED_BLOB='ac802d0d710a9b6d9095023593889e05b7fbf60c'

TARGETS={
 'fr-rank-0019':dict(lemma='ce',form='ce',rank=19,sense='this; that; it',pos='adjective / pronoun'),
 'fr-rank-0020':dict(lemma='pour',form='pour',rank=20,sense='for; to; in order to',pos='preposition'),
 'fr-rank-0024':dict(lemma='qui',form='qui',rank=24,sense='who; which; that',pos='pronoun'),
 'fr-rank-0025':dict(lemma='mais',form='mais',rank=25,sense='but; however',pos='conjunction'),
 'fr-rank-0027':dict(lemma='nous',form='nous',rank=27,sense='we; us',pos='noun / pronoun'),
 'fr-rank-0028':dict(lemma='dans',form='dans',rank=28,sense='in; into',pos='preposition'),
 'fr-rank-0030':dict(lemma='bien',form='bien',rank=30,sense='well; good',pos='adjective / adverb / noun'),
 'fr-rank-0041':dict(lemma='moi',form='moi',rank=41,sense='me; myself',pos='noun / pronoun'),
 'fr-rank-0042':dict(lemma='oui',form='oui',rank=42,sense='yes',pos='adverb'),
 'fr-rank-0045':dict(lemma='ils',form='ils',rank=45,sense='they',pos='pronoun'),
}

def qa(items):
 qs=[]; ans=[]
 for i,(typ,prompt,answer,tids) in enumerate(items,1):
  qid=f'q{i}'; aid=f'a{i}'; q={'id':qid,'type':typ,'prompt':prompt,'answer_id':aid}
  if tids:q['target_ids']=tids
  qs.append(q); ans.append({'id':aid,'question_id':qid,'answer':answer,'explanation':''})
 return qs,ans

def rev(tid,form,stage,rep):
 return {'id':tid,'form':form,'review_stage':stage,'representation':rep,'expected_exposure_number':None}

def targ(tid,exposures,strategies):
 s=TARGETS[tid]
 return {'id':tid,'form':s['form'],'lemma':s['lemma'],'intended_sense':s['sense'],'part_of_speech':s['pos'],'register':'contemporary standard','variety':None,'context_strategy':strategies,'first_introduced':True,'exposures_in_text':exposures,'source_lexicon':'french_top1000.csv','source_rank':s['rank'],'beyond_base':False}

def row(pid,seq,ptype,title,genre,domains,topics,text,new,reviews,grammar,discourse,items,speed=False):
 qs,ans=qa(items)
 return {'id':pid,'language':'fr','cefr':'A1','unit':3,'sequence':seq,'revision':1,'title':title,'passage_type':ptype,'genre':genre,'domains':domains,'topics':topics,'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”\"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':grammar,'discourse_targets':discourse,'questions':qs,'answer_key':ans,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'Generation-stage French A1 Unit 03; full multi-pass audit deferred until French corpus completion.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['French A1 Unit 03 generated as a guarded unit batch under the ten-question standard.','Source identity, schema, word band, target declaration, question-answer linkage, and checkpoint zero-new-target invariants are enforced during generation.']},'paired_text_group':None,'prerequisites':['French A1 Units 01-02 canonical corpus'],'difficulty_notes_internal':'A1 continuation: simple project work, relative reference, contrast, group pronouns, location, evaluation, and presentation language.','reader_tags':['unit_role:'+ptype,'generation_batch','french_a1_u03']}

def build():
 out=[]
 text='''Mardi, la classe de Camille commence un petit projet sur le quartier. Le professeur montre une grande feuille et dit : « Ce projet est pour toute la classe. » Chaque groupe doit choisir un lieu à présenter. Camille propose la bibliothèque. Sami préfère le parc, mais il accepte l’idée de Camille. Ils décident de préparer une page pour la bibliothèque et une autre pour le parc. Camille prend ce travail au sérieux. Elle écrit deux phrases pour expliquer pourquoi ces lieux sont utiles. Ensuite, elle cherche une photo simple pour chaque page. Avant la fin du cours, le professeur regarde ce qu’ils ont fait et leur donne une idée pour rendre le projet plus clair.'''
 out.append(row('fr-a1-u03-p01',13,'instructional','Un projet sur le quartier','class project narrative',['educational'],['project','neighborhood','planning'],text,[targ('fr-rank-0019',3,['form_function']),targ('fr-rank-0020',6,['scenario_resolution'])],[rev('fr-rank-0013','aller','R2','production'),rev('fr-rank-0014','faire','R2','running_text')],[{'id':'fr-a1-ce-demonstrative','role':'new','description':'ce before a masculine singular noun'},{'id':'fr-a1-pour-purpose','role':'new','description':'pour for recipient or simple purpose'}],[{'id':'fr-a1-project-purpose','role':'new','description':'identify the purpose and audience of a simple class project'}],[
 ('gist','Quel projet commence la classe ?','Un projet sur le quartier.',[]),('literal_detail','Quels deux lieux Camille et Sami choisissent-ils ?','La bibliothèque et le parc.',[]),('vocabulary_in_context','Que montre « ce » dans « ce projet » ?','Il désigne le projet dont on parle.',['fr-rank-0019']),('vocabulary_in_context','Que signifie « pour » dans « pour toute la classe » ?','Le projet est destiné à toute la classe.',['fr-rank-0020']),('cause_effect','Pourquoi Camille écrit-elle deux phrases ?','Pour expliquer pourquoi les lieux choisis sont utiles.',[]),('single_word_definition','Quel sens de « pour » est travaillé ici ?','Pour un destinataire ou dans un but précis.',['fr-rank-0020']),('grammar_category','Quel type de mot est « ce » dans « ce projet » ?','Un déterminant démonstratif.',['fr-rank-0019']),('contrast','Pour désigner le projet présent, lequel convient : « ce projet » ou « mon projet » ?','ce projet',['fr-rank-0019']),('cloze_transfer','Complète : _____ livre est pour la classe.','Ce',['fr-rank-0019']),('cloze_transfer','Complète : Je prépare une carte _____ mon ami.','pour',['fr-rank-0020'])]))

 text='''Le lendemain, Camille et Sami cherchent une personne qui peut répondre à leurs questions sur la bibliothèque. Ils voient une employée qui range des livres près de l’entrée. Camille veut lui parler, mais elle hésite un peu. Sami commence : « Bonjour, nous préparons un projet pour l’école. » L’employée sourit et demande ce qu’ils veulent savoir. Camille pose une question sur les horaires, puis une autre sur les activités pour les enfants. L’employée répond clairement, mais elle explique qu’une activité change chaque mois. Camille note cette information. En sortant, elle dit à Sami qu’elle est contente d’avoir parlé à quelqu’un qui connaît bien le lieu.'''
 out.append(row('fr-a1-u03-p02',14,'reinforcement','Une personne qui connaît la bibliothèque','interview micro-story',['educational','public'],['library','questions','information'],text,[targ('fr-rank-0024',3,['form_function']),targ('fr-rank-0025',2,['contrast'])],[rev('fr-rank-0022','dire','R2','running_text'),rev('fr-rank-0026','savoir','R2','running_text')],[{'id':'fr-a1-qui-relative','role':'new','description':'qui as a simple relative subject pronoun'},{'id':'fr-a1-mais-contrast','role':'new','description':'mais linking two contrasting simple ideas'}],[{'id':'fr-a1-question-answer','role':'new','description':'follow a simple information-seeking exchange'}],[
 ('gist','Pourquoi Camille et Sami parlent-ils à l’employée ?','Pour obtenir des informations sur la bibliothèque.',[]),('literal_detail','Quelle information peut changer chaque mois ?','Une activité pour les enfants.',[]),('vocabulary_in_context','À qui renvoie « qui » dans « une employée qui range des livres » ?','À l’employée.',['fr-rank-0024']),('vocabulary_in_context','Que montre « mais » dans « Camille veut lui parler, mais elle hésite » ?','Un contraste entre son intention et son hésitation.',['fr-rank-0025']),('reference_resolution','Dans « ce qu’ils veulent savoir », qui sont « ils » ?','Camille et Sami.',[]),('single_word_definition','Dans cette unité, que signifie « mais » ?','Il introduit une idée qui contraste avec la précédente.',['fr-rank-0025']),('grammar_function','Quel rôle joue « qui » après un nom comme « une personne qui répond » ?','Il relie le nom à une information sur cette personne.',['fr-rank-0024']),('contrast','Quel mot marque le contraste : « mais » ou « pour » ?','mais',['fr-rank-0025']),('cloze_transfer','Complète : Je cherche un élève _____ connaît la réponse.','qui',['fr-rank-0024']),('cloze_transfer','Complète : Je veux sortir, _____ il pleut.','mais',['fr-rank-0025'])]))

 text='''Jeudi, le groupe se retrouve dans une salle calme après les cours. Camille pose les notes au centre de la table et dit : « Nous avons beaucoup d’informations. Maintenant, nous devons choisir les plus importantes. » Sami lit les phrases sur la bibliothèque. Camille regarde les notes sur le parc. Dans le groupe, chacun propose une idée. Ils décident de garder trois informations pour chaque lieu. Ensuite, nous pouvons imaginer la page finale, dit Camille en riant. Le professeur passe dans la salle et regarde leur travail. Il leur conseille de mettre les titres en haut et les images au milieu. Avant de partir, Camille range tout dans une pochette pour ne rien perdre.'''
 out.append(row('fr-a1-u03-p03',15,'interleaved','Dans la salle de travail','group-work narrative',['educational'],['group work','classroom','organization'],text,[targ('fr-rank-0027',3,['form_function']),targ('fr-rank-0028',4,['scenario_resolution'])],[rev('fr-rank-0032','si','R2','other'),rev('fr-rank-0036','devoir','R2','running_text')],[{'id':'fr-a1-nous-subject','role':'new','description':'nous as first-person plural subject'},{'id':'fr-a1-dans-location','role':'new','description':'dans for location inside a place or container'}],[{'id':'fr-a1-group-selection','role':'new','description':'follow a group selecting information for a shared output'}],[
 ('gist','Que fait surtout le groupe dans la salle ?','Il choisit et organise les informations du projet.',[]),('literal_detail','Combien d’informations garde le groupe pour chaque lieu ?','Trois informations.',[]),('vocabulary_in_context','Qui est inclus dans « nous » quand Camille parle au groupe ?','Camille et les autres membres du groupe.',['fr-rank-0027']),('vocabulary_in_context','Que signifie « dans » dans « dans une salle calme » ?','À l’intérieur de la salle.',['fr-rank-0028']),('sequence','Que fait Camille avant de partir ?','Elle range tout dans une pochette.',[]),('single_word_definition','Quel sens de « dans » est travaillé ici ?','À l’intérieur de quelque chose.',['fr-rank-0028']),('grammar_category','Quel type de mot est « nous » dans « nous avons » ?','Un pronom personnel sujet.',['fr-rank-0027']),('contrast','Pour parler de Camille et de son groupe ensemble, lequel convient : « nous » ou « moi » ?','nous',['fr-rank-0027']),('cloze_transfer','Complète : _____ travaillons ensemble après les cours.','Nous',['fr-rank-0027']),('cloze_transfer','Complète : Les crayons sont _____ la boîte.','dans',['fr-rank-0028'])]))

 text='''Vendredi matin, Camille relit la page du projet. Elle trouve que le titre est bien placé, mais une phrase est trop longue. Sami lui demande : « Tu veux que je la change ? » Camille répond : « Oui, mais laisse-moi essayer d’abord. » Elle écrit une phrase plus courte et la lit à voix haute. Sami dit que c’est bien. Puis il montre une image et demande : « Cette photo est pour moi ou pour la page ? » Camille rit : « Pour la page ! » Ils corrigent encore deux petits détails. À la fin, Camille se sent bien : le travail est simple, clair et facile à lire. Elle garde la dernière vérification pour elle et coche chaque élément de la liste.'''
 out.append(row('fr-a1-u03-p04',16,'transfer','Laisse-moi essayer','revision dialogue',['educational','personal'],['revision','feedback','self'],text,[targ('fr-rank-0030',3,['behavior_interpretation']),targ('fr-rank-0041',2,['form_function'])],[rev('fr-rank-0038','mon','R2','contrast'),rev('fr-rank-0044','sur','R2','other')],[{'id':'fr-a1-bien-evaluation','role':'new','description':'bien as a simple positive evaluation or adverb'},{'id':'fr-a1-moi-stressed-pronoun','role':'new','description':'moi as a stressed first-person pronoun'}],[{'id':'fr-a1-revise-after-feedback','role':'new','description':'follow a simple self-correction after feedback'}],[
 ('gist','Que veut améliorer Camille ?','Une phrase trop longue dans la page du projet.',[]),('literal_detail','Que fait Camille après avoir raccourci la phrase ?','Elle la lit à voix haute.',[]),('vocabulary_in_context','Que signifie « bien » dans « le titre est bien placé » ?','D’une bonne manière ; correctement.',['fr-rank-0030']),('vocabulary_in_context','À qui renvoie « moi » dans « laisse-moi essayer » ?','À Camille.',['fr-rank-0041']),('cause_effect','Pourquoi Camille coche-t-elle les éléments de la liste ?','Pour vérifier que tout le travail est terminé.',[]),('single_word_definition','Quel sens simple de « bien » est utilisé ici ?','Correctement ou d’une bonne manière.',['fr-rank-0030']),('grammar_category','Quel type de pronom est « moi » ici ?','Un pronom personnel tonique.',['fr-rank-0041']),('contrast','Si Camille parle d’elle-même après une préposition, lequel convient : « moi » ou « nous » ?','moi',['fr-rank-0041']),('cloze_transfer','Complète : Le travail est _____ organisé.','bien',['fr-rank-0030']),('cloze_transfer','Complète : Cette lettre est pour _____.','moi',['fr-rank-0041'])]))

 text='''Lundi suivant, deux groupes présentent leur travail devant la classe. Camille et Sami passent en premier. Le professeur demande s’ils sont prêts. « Oui », répond Camille. Sami montre la page sur la bibliothèque pendant que Camille explique le parc. Ils parlent lentement et regardent les autres élèves. Quand ils terminent, plusieurs élèves posent des questions. Camille répond oui quand elle connaît la réponse et demande à Sami de compléter une information. Ensuite, deux garçons présentent leur projet. Ils ont choisi le marché et le centre sportif. Ils montrent leurs images et expliquent pourquoi ces lieux sont importants. À la fin, le professeur remercie tous les groupes et dit qu’ils ont bien travaillé ensemble.'''
 out.append(row('fr-a1-u03-p05',17,'integration','Oui, nous sommes prêts','class presentation narrative',['educational'],['presentation','class','answers'],text,[targ('fr-rank-0042',2,['scenario_resolution']),targ('fr-rank-0045',6,['form_function'])],[rev('fr-rank-0043','tout','R2','running_text'),rev('fr-rank-0037','plus','R2','other')],[{'id':'fr-a1-oui-affirmation','role':'new','description':'oui as a simple affirmative response'},{'id':'fr-a1-ils-subject','role':'new','description':'ils as masculine or mixed-group third-person plural subject'}],[{'id':'fr-a1-presentation-turns','role':'integration','description':'follow presentation turns, questions, and responses'}],[
 ('gist','Que font Camille et Sami devant la classe ?','Ils présentent leur projet.',[]),('literal_detail','Quels lieux le deuxième groupe a-t-il choisis ?','Le marché et le centre sportif.',[]),('vocabulary_in_context','Que signifie « oui » quand Camille répond au professeur ?','Une réponse affirmative.',['fr-rank-0042']),('vocabulary_in_context','À qui renvoie « ils » dans « Ils parlent lentement » ?','À Camille et Sami.',['fr-rank-0045']),('sequence','Que se passe-t-il après la présentation de Camille et Sami ?','Les autres élèves posent des questions, puis un autre groupe présente son projet.',[]),('single_word_definition','Que signifie « oui » ?','Une réponse affirmative.',['fr-rank-0042']),('grammar_category','Quel type de mot est « ils » dans « ils montrent leurs images » ?','Un pronom personnel sujet.',['fr-rank-0045']),('contrast','Pour une réponse affirmative, lequel convient : « oui » ou « non » ?','oui',['fr-rank-0042']),('cloze_transfer','Complète : Paul et Karim arrivent ; _____ sont prêts.','Ils',['fr-rank-0045']),('cloze_transfer','Complète : — Tu viens avec nous ? — _____.','Oui',['fr-rank-0042'])]))

 text='''Après les présentations, Camille pense au projet depuis le début. Ce travail était pour la classe, mais il lui a aussi appris à mieux travailler avec Sami. Ils ont trouvé une personne qui connaissait la bibliothèque, puis ils ont choisi les informations utiles. Dans la salle, ils ont organisé les notes et préparé une page claire. Camille a compris que nous pouvons améliorer un texte en le relisant calmement. Elle sait aussi qu’un travail peut être bien fait sans être compliqué. Pendant la présentation, elle a répondu oui quand elle connaissait la réponse, et les autres groupes ont fait la même chose. Maintenant, Camille range le projet dans son dossier et pense déjà au prochain travail.'''
 out.append(row('fr-a1-u03-p06',18,'checkpoint','Le projet terminé','fluency checkpoint summary',['educational'],['project','review','teamwork'],text,[],[
  rev('fr-rank-0019','ce','R2','summary'),rev('fr-rank-0020','pour','R2','summary'),rev('fr-rank-0024','qui','R2','running_text'),rev('fr-rank-0025','mais','R2','running_text'),rev('fr-rank-0027','nous','R1','running_text'),rev('fr-rank-0028','dans','R1','running_text'),rev('fr-rank-0030','bien','R1','running_text'),rev('fr-rank-0041','moi','R1','cloze'),rev('fr-rank-0042','oui','R1','running_text'),rev('fr-rank-0045','ils','R1','running_text')],[{'id':'fr-a1-u03-grammar-integration','role':'integration','description':'review demonstratives, purpose, relative reference, contrast, pronouns, location, and affirmation'}],[{'id':'fr-a1-u03-project-summary','role':'integration','description':'integrate the main stages of a short collaborative project'}],[
 ('gist','Quelle est l’idée principale du texte ?','Camille résume ce qu’elle a appris en réalisant le projet avec son groupe.',[]),('literal_detail','Où Camille range-t-elle le projet à la fin ?','Dans son dossier.',['fr-rank-0028']),('vocabulary_in_context','À quoi renvoie « ce » dans « Ce travail était pour la classe » ?','Au projet que Camille vient de terminer.',['fr-rank-0019']),('reference_resolution','À qui renvoie « ils » dans « ils ont choisi les informations utiles » ?','À Camille et Sami.',['fr-rank-0045']),('cause_effect','Comment Camille a-t-elle appris à améliorer un texte ?','En le relisant calmement et en corrigeant ce qui pouvait être plus clair.',[]),('single_word_definition','Que signifie « mais » ?','Il introduit un contraste.',['fr-rank-0025']),('grammar_choice','Choisis : « nous pouvons améliorer » ou « nous peut améliorer ».','nous pouvons améliorer',['fr-rank-0027']),('contrast','Pour répondre de façon affirmative, lequel convient : « oui » ou « mais » ?','oui',['fr-rank-0042']),('cloze_transfer','Complète : Je cherche une personne _____ peut m’aider.','qui',['fr-rank-0024']),('cloze_transfer','Complète : Ce cadeau est pour _____.','moi',['fr-rank-0041'])],True))
 return out

def rows(path):return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def declared(r):return {str(t['id']) for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict) and t.get('id')}
def check_source():
 by={}
 with LEXICON.open(encoding='utf-8',newline='') as f:
  for r in csv.DictReader(f):by[r['Front']]=r['Back']
 for tid,s in TARGETS.items():
  b=by.get(s['lemma']); m=re.search(r'Rank:\s*(\d+)',b or '')
  if not m or int(m.group(1))!=s['rank']:raise AssertionError(f'source-rank drift {tid}/{s["lemma"]}')
def validate(r,v):
 es=sorted(v.iter_errors(r),key=lambda e:list(e.path))
 if es:raise AssertionError(f'schema {r["id"]}: {es[0].message} @ {list(es[0].path)}')
 if not 90<=r['word_count']<=140:raise AssertionError(f'word band {r["id"]}: {r["word_count"]}')
 if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f'10Q failure {r["id"]}')
 amap={a['question_id']:a['id'] for a in r['answer_key']}
 if len(amap)!=10:raise AssertionError(f'answer linkage count {r["id"]}')
 loc=declared(r)
 for q in r['questions']:
  if amap.get(q['id'])!=q['answer_id']:raise AssertionError(f'link {r["id"]} {q["id"]}')
  for tid in q.get('target_ids',[]):
   if tid not in loc:raise AssertionError(f'undeclared {r["id"]} {q["id"]} {tid}')
 if r['id'].endswith('-p06') and r['new_lexical_targets']:raise AssertionError(f'checkpoint new target {r["id"]}')
def main():
 blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
 if blob!=EXPECTED_BLOB:raise AssertionError(f'French A1 source drift: {blob} != {EXPECTED_BLOB}')
 old=rows(CANON)
 if len(old)!=12 or [r['sequence'] for r in old]!=list(range(1,13)):raise AssertionError('expected 12 canonical French A1 rows before Unit 03')
 if [r['id'] for r in old[-6:]]!=[f'fr-a1-u02-p{i:02d}' for i in range(1,7)]:raise AssertionError('Unit 02 source IDs drift')
 existing={t.get('id') for r in old for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
 if set(TARGETS)&existing:raise AssertionError(f'reintroduced IDs {sorted(set(TARGETS)&existing)}')
 check_source(); new=build()
 if [r['sequence'] for r in new]!=list(range(13,19)):raise AssertionError('Unit03 sequence failure')
 v=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
 for r in old+new:validate(r,v)
 for r in new:
  for t in r['new_lexical_targets']:
   n=len(re.findall(rf'(?<!\w){re.escape(t["form"])}(?!\w)',r['text'],flags=re.IGNORECASE))
   if n!=t['exposures_in_text']:raise AssertionError(f'exposure drift {r["id"]} {t["id"]}: {n} != {t["exposures_in_text"]}')
 original=CANON.read_text(encoding='utf-8'); original += '' if original.endswith('\n') else '\n'
 CANON.write_text(original+''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in new),encoding='utf-8')
 final=rows(CANON)
 if len(final)!=18 or [r['sequence'] for r in final]!=list(range(1,19)):raise AssertionError('post-write continuity failure')
 for r in final:validate(r,v)
 print(json.dumps({'status':'PASS','unit':3,'appended_passages':6,'french_a1_total':18,'word_counts':{r['id']:r['word_count'] for r in new},'new_targets':10,'questions':60,'answers':60,'checkpoint_new_targets':0},ensure_ascii=False))
if __name__=='__main__':main()
