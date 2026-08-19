import hashlib,json,pathlib,re
ROOT=pathlib.Path('.')
A1=ROOT/'reading/french/a1/passages.jsonl'; A2=ROOT/'reading/french/a2/passages.jsonl'
OLD=ROOT/'reading/audit/french_a1_a2_metalinguistic_human_refinement_2026-08-19.json'
OUT=ROOT/'reading/audit/french_a1_a2_metalinguistic_human_refinement_v2_2026-08-19.json'
EXPECTED={'A1':'48db8f58dc105bcd880302d31b0f7fcae439e3018a35b0adb62b690d42b85562','A2':'8fcd71903e6a495a2abaac8d436232b4b7ee00ae5ac0bce4d273aa4a134b3c15'}
USE={
('fr-a1-u01-p02','q7'):('Complète avec le bon choix : « _____ le feu devient vert, ils traversent. » — « quand » ou « avec » ?','« quand ».') ,
('fr-a1-u01-p03','q7'):('Complète avec le bon choix : « Sami s’assoit _____ elle. » — « avec » ou « sans » ?','« avec ».') ,
('fr-a1-u01-p06','q10'):('Complète : « _____ il arrive, Camille sourit. » — « quand » ou « avec » ?','« quand ».') ,
('fr-a1-u02-p03','q7'):('Complète : « Elle demandera de l’aide _____ elle ne trouve pas le livre. » — « si » ou « avec » ?','« si ».') ,
('fr-a1-u02-p05','q7'):('Dans le texte, elle veut _____ de place pour dessiner : « plus » ou « moins » ?','« plus ».') ,
('fr-a1-u03-p02','q7'):('Complète : « Ils cherchent une personne _____ peut répondre. » — « qui » ou « avec » ?','« qui ».') ,
('fr-a1-u04-p01','q7'):('Complète : « Le premier cahier est _____ grand. » — « très » ou « beaucoup » ?','« très ».') ,
('fr-a1-u04-p02','q7'):('Complète : « Elle travaille _____ à la table du salon. » — « toujours » ou « très » ?','« toujours ».') ,
('fr-a1-u04-p03','q7'):('Complète : « Il reste _____ cinq minutes. » — « encore » ou « très » ?','« encore ».') ,
('fr-a1-u04-p04','q7'):('D’après le texte, elle prépare son sac _____ de dormir : « avant » ou « après » ?','« avant ».') ,
('fr-a1-u04-p05','q7'):('D’après le texte, elle aide sa mère _____ le petit-déjeuner : « après » ou « avant » ?','« après ».') ,
('fr-a1-u06-p01','q7'):('Complète : « Elle met _____ de pain sur son plateau. » — « peu » ou « très » ?','« peu ».') ,
('fr-a1-u06-p02','q7'):('Complète : « Il y a _____ de travail pour une seule soirée. » — « trop » ou « très » ?','« trop ».') ,
('fr-a1-u06-p03','q7'):('D’après le texte, Camille et Sami ont choisi le _____ titre : « même » ou « autre » ?','« même ».') ,
('fr-a1-u06-p04','q7'):('Complète : « Elle ne parle _____ fort dans la salle de lecture. » — « jamais » ou « très » ?','« jamais ».') ,
('fr-a1-u06-p05','q7'):('D’après le texte, ils sont _____ dans le centre de la ville : « maintenant » ou « plus tard » ?','« maintenant ».') ,
('fr-a1-u06-p06','q7'):('Complète : « Camille ne crie _____ dans la bibliothèque. » — « jamais » ou « très » ?','« jamais ».') ,
('fr-a1-u07-p01','q7'):('D’après le texte, la bibliothèque est _____ de leur école : « près » ou « loin » ?','« près ».') ,
('fr-a1-u07-p02','q7'):('D’après le texte, la classe attend _____ le gymnase : « devant » ou « derrière » ?','« devant ».') ,
('fr-a1-u07-p03','q7'):('Complète : « Un banc se trouve _____ deux arbres. » — « entre » ou « devant » ?','« entre ».') ,
('fr-a1-u07-p04','q7'):('D’après le texte, au premier carrefour ils tournent à _____ : « gauche » ou « droite » ?','« gauche ».') ,
('fr-a1-u07-p06','q7'):('D’après le texte, une balle est _____ le banc : « sous » ou « devant » ?','« sous ».') ,
('fr-a1-u08-p06','q7'):('Après du repos, Camille se sent-elle « mieux » ou « plus malade » ?','« mieux ».')}
def load(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(p,rows): p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before={'A1':sha(A1),'A2':sha(A2)}; assert before==EXPECTED,('final refinement hash drift',before)
rows1=load(A1); rows2=load(A2); idx={r['id']:r for r in rows1+rows2}
old=json.loads(OLD.read_text(encoding='utf-8')); assert old['status']=='HUMAN_REVIEWED_DEFINED_CLASS_PASS'
source={}
for t in old['transformations']:
 if 'low_level_function_label_task' in t['reasons'] and t['level']=='A1': source[(t['passage_id'],t['question_id'])]=t
assert set(source)==set(USE) and len(source)==23,(len(source),set(source)^set(USE))
changes=[]; changed=set()
for key,(prompt,answer) in USE.items():
 t=source[key]; rec=idx[key[0]]; q=next(x for x in rec['questions'] if x['id']==key[1]); a=next(x for x in rec['answer_key'] if x['id']==t['answer_id'])
 assert q['prompt']==t['after']['prompt'] and a['answer']==t['after']['answer'],(key,'post-pass drift')
 tids=list(q.get('target_ids',[])); oldqa={'type':q['type'],'prompt':q['prompt'],'answer':a['answer'],'target_ids':tids}
 q['type']='grammar_choice'; q['prompt']=prompt; a['answer']=answer; assert q.get('target_ids',[])==tids
 changed.add(rec['id']); changes.append({'passage_id':key[0],'question_id':key[1],'answer_id':a['id'],'reason':'semantic_assessment_duplication_after_first_human_refinement','before':oldqa,'after':{'type':q['type'],'prompt':q['prompt'],'answer':a['answer'],'target_ids':tids}})
for rid in changed: idx[rid]['revision']=int(idx[rid].get('revision',1))+1
# Full A1/A2 structural, exact-duplicate and defined-class validation.
dups=[]; residue=[]
formal_markers=['quel type de mot','quelle est la catégorie de','quel type de pronom','après une préposition','quelle forme suit','quelle forme vient après','que complète']
for level,rows in [('A1',rows1),('A2',rows2)]:
 assert len(rows)==60 and [r['sequence'] for r in rows]==list(range(1,61))
 for rec in rows:
  assert len(rec['questions'])==len(rec['answer_key'])==10
  qids=[q['id'] for q in rec['questions']]; aids=[a['id'] for a in rec['answer_key']]
  assert len(qids)==len(set(qids))==10 and len(aids)==len(set(aids))==10
  assert {q['answer_id'] for q in rec['questions']}==set(aids) and {a['question_id'] for a in rec['answer_key']}==set(qids)
  bucket={}
  for q in rec['questions']: bucket.setdefault(re.sub(r'\s+',' ',q['prompt'].strip().lower()),[]).append(q['id'])
  for p,ids in bucket.items():
   if len(ids)>1: dups.append({'level':level,'passage_id':rec['id'],'question_ids':ids,'prompt':p})
  for q in rec['questions']:
   p=q['prompt'].lower().replace('’',"'"); hits=[m for m in formal_markers if m in p]
   if q['type'] in {'grammar_category','grammar_function'}: hits.append('formal_question_type')
   if hits: residue.append({'level':level,'passage_id':rec['id'],'question_id':q['id'],'hits':hits,'prompt':q['prompt']})
assert not dups,dups
assert not residue,residue
# Each superseded function item now has a different assessment type from vocabulary meaning questions.
for c in changes:
 rec=idx[c['passage_id']]; q=next(x for x in rec['questions'] if x['id']==c['question_id']); assert q['type']=='grammar_choice'
 assert q['prompt'].count('«')==q['prompt'].count('»'),(c['passage_id'],c['question_id'])
dump(A1,rows1); after={'A1':sha(A1),'A2':sha(A2)}; assert after['A1']!=before['A1'] and after['A2']==before['A2']
# Preserve the first refinement as evidence but explicitly mark it superseded.
old['status']='SUPERSEDED_AFTER_DIRECT_SEMANTIC_SPOT_CHECK'
old['superseded_by']='reading/audit/french_a1_a2_metalinguistic_human_refinement_v2_2026-08-19.json'
old['supersession_reason']='Direct canonical spot-check found that several former function-label questions had been reframed as near-duplicate vocabulary-meaning questions. A second refinement converts all 23 A1 function-label items to operational use/choice tasks.'
OLD.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
OUT.write_text(json.dumps({'audit':'French A1-A2 metalinguistic human refinement v2','date':'2026-08-19','status':'HUMAN_REVIEWED_DEFINED_CLASS_PASS_V2','supersedes':'reading/audit/french_a1_a2_metalinguistic_human_refinement_2026-08-19.json','before_sha256':before,'after_sha256':after,'function_items_semantically_rechecked':23,'changed_passages':len(changed),'finding':'The first human refinement removed formal metalanguage but some function-label replacements duplicated existing vocabulary-meaning assessment roles.','resolution':'All 23 A1 function-label items now use operational use/choice or contextual selection tasks; q3/q4 retain meaning, q7/q10 use/grammar roles remain distinct, and existing transfer/cloze questions remain separate.','changes':changes,'validation':{'23_function_items_rechecked':'PASS','120_passages_exact_duplicate_prompt_scan':'PASS','60_records_each_level':'PASS','sequence_continuity':'PASS','ten_questions_ten_answers':'PASS','question_answer_linkage':'PASS','target_ids_preserved':'PASS','defined_metalinguistic_defect_class_residue':0,'function_items_now_operational_use_choice':'PASS'},'release_effect':'French remains REOPEN_REQUIRED; final A1 hash changed again and all recertification gates must bind the v2 final hash.','next_gate':'Update generation policy to prohibit formal metalinguistic burden at A1/A2, then rerun deterministic evidence validation and continue 100% French semantic educator recertification.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'changed_function_items':23,'changed_passages':len(changed),'before':before,'after':after},ensure_ascii=False,indent=2))