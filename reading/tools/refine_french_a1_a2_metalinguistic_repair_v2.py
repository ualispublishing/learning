import hashlib, json, pathlib, re
ROOT=pathlib.Path('.')
FILES={'A1':ROOT/'reading/french/a1/passages.jsonl','A2':ROOT/'reading/french/a2/passages.jsonl'}
PRIOR=ROOT/'reading/audit/french_a1_a2_metalinguistic_repair_2026-08-19.json'
OUT=ROOT/'reading/audit/french_a1_a2_metalinguistic_human_refinement_2026-08-19.json'
EXPECTED={'A1':'97948c375f54649935db2d20c44def1dc539939dc1c14d9b063d6647d566da13','A2':'54e38bdbd8c7264a0d77484296c256857465783d57069ac456cc63538d515552'}

CATEGORY_USE={
'faire':('Choisis la phrase correcte : « tu vas faire un cours » ou « tu vas fais un cours » ?','« tu vas faire un cours ».'),
'mon':('Pour parler de son carnet, Camille dit : « mon carnet » ou « ma carnet » ?','« mon carnet ».'),
'ce':('Choisis la forme correcte : « ce projet » ou « cet projet » ?','« ce projet ».'),
'nous':('Choisis la phrase correcte : « nous avons des informations » ou « nous a des informations » ?','« nous avons des informations ».'),
'moi':('Choisis la forme correcte : « cette photo est pour moi » ou « cette photo est pour je » ?','« cette photo est pour moi ».'),
'ils':('Choisis la phrase correcte : « ils montrent leurs images » ou « ils montre leurs images » ?','« ils montrent leurs images ».'),
'matin':('Choisis la forme correcte : « le matin » ou « la matin » ?','« le matin ».'),
'soir':('Choisis la forme correcte : « le soir » ou « la soir » ?','« le soir ».'),
'chose':('Choisis la forme correcte : « une autre chose » ou « un autre chose » ?','« une autre chose ».'),
'place':('Choisis la forme correcte : « une place » ou « un place » ?','« une place ».'),
'enfant':('Choisis la phrase correcte : « chaque enfant reçoit une feuille » ou « chaque enfants reçoit une feuille » ?','« chaque enfant reçoit une feuille ».'),
'question':('Choisis la forme correcte : « une question » ou « un question » ?','« une question ».'),
'rue':('Choisis la forme correcte : « une rue » ou « un rue » ?','« une rue ».'),
'main':('Choisis la forme correcte : « une main » ou « un main » ?','« une main ».'),
'pied':('Choisis la forme correcte : « son pied droit » ou « sa pied droit » ?','« son pied droit ».'),
'manger':('Choisis la phrase correcte : « elle veut manger » ou « elle veut mange » ?','« elle veut manger ».'),
'sentir':('Choisis la phrase correcte : « elle commence à sentir la fatigue » ou « elle commence à sent la fatigue » ?','« elle commence à sentir la fatigue ».'),
'malade':('Choisis la phrase correcte : « Camille est malade » ou « Camille est malades » ?','« Camille est malade ».'),
'famille':('Choisis la forme correcte : « sa famille » ou « son famille » ?','« sa famille ».'),
'mère':('Choisis la forme correcte : « sa mère » ou « son mère » ?','« sa mère ».'),
'école':('Choisis la forme correcte : « à l’école » ou « au école » ?','« à l’école ».'),
'table':('Choisis la forme correcte : « une table » ou « un table » ?','« une table ».'),
'eau':('Choisis la forme correcte : « de l’eau » ou « du eau » ?','« de l’eau ».'),
'livre':('Choisis la forme correcte au pluriel : « des livres » ou « des livre » ?','« des livres ».'),
'soleil':('Choisis la forme correcte : « le soleil » ou « la soleil » ?','« le soleil ».'),
'chaud':('Choisis la phrase correcte : « il fait chaud » ou « il fait chaude » ?','« il fait chaud ».'),
'acheter':('Choisis la phrase correcte : « elle veut acheter un livre » ou « elle veut achète un livre » ?','« elle veut acheter un livre ».'),
'vêtement':('Choisis la forme correcte : « un vêtement » ou « une vêtement » ?','« un vêtement ».'),
'sac':('Choisis la forme correcte : « un sac » ou « une sac » ?','« un sac ».'),
'expliquer':('Choisis la phrase correcte : « elle peut expliquer le problème » ou « elle peut explique le problème » ?','« elle peut expliquer le problème ».'),
'essayer':('Choisis la phrase correcte : « elle décide d’essayer » ou « elle décide d’essaie » ?','« elle décide d’essayer ».'),
'réparer':('Choisis la phrase correcte : « il peut réparer le vélo » ou « il peut répare le vélo » ?','« il peut réparer le vélo ».'),
'découvrir':('Choisis la phrase correcte : « elle vient de découvrir un service » ou « elle vient de découvre un service » ?','« elle vient de découvrir un service ».')}
FUNC_MEAN={'quand':'« quand » signifie ici « au moment où ».','avec':'« avec » signifie ici que Sami et Camille sont ensemble.','si':'« si » présente la condition : si elle ne trouve pas quelque chose, elle doit demander.','plus':'« plus » signifie ici qu’elle veut une quantité plus grande de place.','qui':'« qui » renvoie à la personne et précise qu’elle répond.','très':'« très » renforce l’idée de grandeur : le cahier est vraiment grand.','toujours':'« toujours » signifie ici que l’action se fait de manière habituelle ou à chaque fois.','encore':'Ici, « encore » signifie qu’une durée supplémentaire reste avant l’ouverture.','avant':'« avant » signifie qu’une action se produit plus tôt qu’une autre.','après':'« après » signifie qu’une action se produit plus tard qu’une autre.','peu':'« peu » indique ici une petite quantité.','trop':'« trop » indique ici une quantité excessive.','même':'« même » signifie ici qu’il s’agit d’un livre identique.','jamais':'Dans cette phrase négative, « jamais » signifie « à aucun moment ».','maintenant':'« maintenant » signifie « au moment présent ».','près':'« près » signifie « à une petite distance » ou « proche ».','devant':'« devant » indique une position en face ou à l’avant du gymnase.','entre':'« entre » signifie « au milieu de deux éléments ».','gauche':'« à gauche » indique la direction du côté gauche.','sous':'« sous » signifie « plus bas que » ou « en dessous de ».','mieux':'« mieux » signifie que l’état s’est amélioré.'}
CTX={
('fr-a1-u01-p02','q7'):'Quand le feu devient vert, ils traversent.',('fr-a1-u01-p03','q7'):'Sami s’assoit avec elle.',('fr-a1-u01-p06','q10'):'Quand elle rencontre Sami, ils marchent ensemble.',('fr-a1-u02-p03','q7'):'Si elle ne trouve pas quelque chose, elle doit demander.',('fr-a1-u02-p05','q7'):'Elle veut plus de place pour dessiner.',('fr-a1-u03-p02','q7'):'Ils cherchent une personne qui peut répondre à leurs questions.',('fr-a1-u04-p01','q7'):'Le premier cahier est très grand.',('fr-a1-u04-p02','q7'):'Elle travaille toujours à la table du salon.',('fr-a1-u04-p03','q7'):'Il reste encore cinq minutes.',('fr-a1-u04-p04','q7'):'Avant de dormir, elle prépare son sac.',('fr-a1-u04-p05','q7'):'Après le petit-déjeuner, elle aide sa mère.',('fr-a1-u06-p01','q7'):'Elle met peu de pain sur son plateau.',('fr-a1-u06-p02','q7'):'Il y a trop de travail pour une seule soirée.',('fr-a1-u06-p03','q7'):'C’est bien le même livre.',('fr-a1-u06-p04','q7'):'Elle ne parle jamais fort dans la salle de lecture.',('fr-a1-u06-p05','q7'):'Camille et son petit frère sont maintenant dans le centre de la ville.',('fr-a1-u06-p06','q7'):'Camille y va souvent, mais elle ne parle jamais fort.',('fr-a1-u07-p01','q7'):'La bibliothèque est près de leur école.',('fr-a1-u07-p02','q7'):'La classe attend devant le gymnase.',('fr-a1-u07-p03','q7'):'Un banc se trouve entre deux arbres.',('fr-a1-u07-p04','q7'):'Au premier carrefour, ils tournent à gauche.',('fr-a1-u07-p06','q7'):'Une balle est sous le banc.',('fr-a1-u08-p06','q7'):'Après du repos, elle peut se sentir mieux.'}

def load(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(p,rows): p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def form(rec,tids):
 d={t['id']:t['form'] for t in rec.get('new_lexical_targets',[])+rec.get('review_lexical_targets',[]) if t.get('id') and t.get('form')}; fs=[]
 for i in tids:
  if i in d and d[i] not in fs: fs.append(d[i])
 assert len(fs)==1,(rec['id'],tids,fs); return fs[0]

before={k:sha(v) for k,v in FILES.items()}; assert before==EXPECTED,('hash drift',before)
prior=json.loads(PRIOR.read_text(encoding='utf-8')); assert prior['after_sha256']==EXPECTED and prior['confirmed_defect_count']==63
corpora={k:load(v) for k,v in FILES.items()}; idx={r['id']:r for rows in corpora.values() for r in rows}
refined=[]; changed=set(); seen=set()
for t in prior['transformations']:
 key=(t['passage_id'],t['question_id']); assert key not in seen; seen.add(key); rec=idx[key[0]]
 q=next(x for x in rec['questions'] if x['id']==key[1]); a=next(x for x in rec['answer_key'] if x['id']==t['answer_id'])
 assert q['type']==t['after']['type'] and q['prompt']==t['after']['prompt'] and a['answer']==t['after']['answer'],(key,'intermediate drift')
 tids=list(q.get('target_ids',[])); old={'type':q['type'],'prompt':q['prompt'],'answer':a['answer'],'target_ids':tids}; reasons=set(t['reasons'])
 if key==('fr-a1-u03-p04','q8'):
  q['type']='reference_resolution'; q['prompt']='Dans « Cette photo est pour moi », à qui est destinée la photo ?'; a['answer']='À la personne qui parle.'
 elif 'formal_grammar_category_retrieval' in reasons:
  f=form(rec,tids); assert f in CATEGORY_USE,(key,f); q['type']='grammar_choice'; q['prompt'],a['answer']=CATEGORY_USE[f]
 elif 'low_level_function_label_task' in reasons:
  if key==('fr-a2-u01-p01','q7'):
   q['type']='cause_effect'; q['prompt']='Pourquoi Camille suit-elle ce conseil ?'; a['answer']='Parce qu’elle ne veut pas rester sans information.'
  else:
   f=form(rec,tids); assert f in FUNC_MEAN and key in CTX,(key,f); q['type']='vocabulary_in_context'; q['prompt']=f'Dans « {CTX[key]} », que signifie « {f} » ici ?'; a['answer']=FUNC_MEAN[f]
 elif 'formal_grammar_in_context_retrieval' in reasons:
  if key==('fr-a2-u02-p01','q7'): q['type']='vocabulary_in_context'; q['prompt']='Dans « la raison de ce changement », que signifie « raison » ?'; a['answer']='La cause ou l’explication du changement.'
  elif key==('fr-a2-u02-p02','q7'): q['type']='grammar_choice'; q['prompt']='Choisis la phrase correcte : « avant de prendre une décision » ou « avant de prends une décision » ?'; a['answer']='« avant de prendre une décision ».'
  elif key==('fr-a2-u02-p03','q7'): q['type']='grammar_choice'; q['prompt']='Choisis la phrase correcte : « il est important de pratiquer » ou « il est important de pratique » ?'; a['answer']='« il est important de pratiquer ».'
  else: raise AssertionError((key,'unreviewed structure item'))
 else: raise AssertionError((key,sorted(reasons)))
 assert q.get('target_ids',[])==tids; changed.add(rec['id']); refined.append({'level':rec['cefr'],'passage_id':rec['id'],'sequence':rec['sequence'],'question_id':q['id'],'answer_id':a['id'],'reasons':sorted(reasons),'before':old,'after':{'type':q['type'],'prompt':q['prompt'],'answer':a['answer'],'target_ids':list(q.get('target_ids',[]))}})
assert len(refined)==63

# Repair an exact duplicate independently exposed by the stronger duplicate guard.
extra=[]; rec=idx['fr-a1-u08-p02']; q6=next(q for q in rec['questions'] if q['id']=='q6'); a6=next(a for a in rec['answer_key'] if a['id']=='a6')
assert q6['prompt']=='Que signifie « corps » ?' and a6['answer']=='L’ensemble physique d’une personne.'
q6['type']='vocabulary_in_context'; q6['prompt']='Dans « écouter son corps », que doit faire Camille ?'; a6['answer']='Elle doit faire attention à ce qu’elle ressent physiquement.'
changed.add(rec['id']); extra.append({'passage_id':rec['id'],'question_id':'q6','category':'preexisting_exact_duplicate_prompt','before':'Que signifie « corps » ?','after':q6['prompt']})

for rid in changed: idx[rid]['revision']=int(idx[rid].get('revision',1))+1

duplicates=[]
for level,rows in corpora.items():
 assert len(rows)==60 and [r['sequence'] for r in rows]==list(range(1,61))
 for rec in rows:
  assert len(rec['questions'])==len(rec['answer_key'])==10
  qids=[q['id'] for q in rec['questions']]; aids=[a['id'] for a in rec['answer_key']]
  assert len(qids)==len(set(qids))==10 and len(aids)==len(set(aids))==10
  assert {q['answer_id'] for q in rec['questions']}==set(aids) and {a['question_id'] for a in rec['answer_key']}==set(qids)
  bucket={}
  for q in rec['questions']: bucket.setdefault(re.sub(r'\s+',' ',q['prompt'].strip().lower()),[]).append(q['id'])
  for p,ids in bucket.items():
   if len(ids)>1: duplicates.append({'level':level,'passage_id':rec['id'],'question_ids':ids,'prompt':p})
if duplicates: raise SystemExit('EXACT DUPLICATE PROMPTS REMAIN: '+json.dumps(duplicates,ensure_ascii=False))

formal_prompt=['quel type de mot','quelle est la catégorie de','quel type de pronom','quel rôle joue','quelle fonction','après une préposition','quelle forme suit','quelle forme vient après','que complète']
formal_answers=['un déterminant possessif','un pronom personnel','un infinitif','un adjectif.','un verbe.','un nom.']; residue=[]
for level,rows in corpora.items():
 for rec in rows:
  amap={a['id']:a for a in rec['answer_key']}
  for q in rec['questions']:
   p=q['prompt'].lower().replace('’',"'"); aa=amap[q['answer_id']]['answer'].lower().replace('’',"'"); hits=[x for x in formal_prompt if x in p]
   if q['type'] in {'grammar_category','grammar_function'}: hits.append('formal_question_type')
   hits += [x for x in formal_answers if x in aa and q['type'] in {'grammar_category','grammar_function','grammar_in_context'}]
   if hits: residue.append({'level':level,'passage_id':rec['id'],'question_id':q['id'],'hits':sorted(set(hits)),'prompt':q['prompt'],'answer':amap[q['answer_id']]['answer']})
if residue: raise SystemExit('DEFINED DEFECT CLASS REMAINS: '+json.dumps(residue,ensure_ascii=False))
for item in refined:
 q=next(x for x in idx[item['passage_id']]['questions'] if x['id']==item['question_id']); assert q['prompt'].count('«')==q['prompt'].count('»') and q['type']!='cloze_transfer',(item['passage_id'],item['question_id'])

for k,p in FILES.items(): dump(p,corpora[k])
after={k:sha(v) for k,v in FILES.items()}; assert after!=before
OUT.write_text(json.dumps({'audit':'French A1-A2 human semantic refinement of metalinguistic repair','date':'2026-08-19','status':'HUMAN_REVIEWED_DEFINED_CLASS_PASS','review_scope':'All 63 machine-repaired Q/A transformations, plus exact-duplicate checks over all 120 A1/A2 passages','before_sha256':before,'after_sha256':after,'reviewed_transformations':63,'changed_passages':len(changed),'additional_preexisting_repairs':extra,'human_review_findings':['Machine cloze extraction produced malformed nested quotation marks in dialogue contexts.','fr-a1-u03-p04 q7/q8 became duplicate malformed clozes and q8 lost the intended pour moi context.','fr-a1-u01-p03 q7 selected avec un livre instead of accompaniment.','fr-a1-u04-p03 q7 selected pas encore instead of additional-time encore.','fr-a1-u06-p03 q7 selected adverbial même instead of identical/same.','A definition fallback duplicated an existing meaning task; an exact pre-existing q4/q6 duplicate in fr-a1-u08-p02 was also repaired.','Copied-passage clozes duplicated the role of later transfer items and conflicted with the ten-question standard.'],'resolution':'Former category-label tasks now use operational form/use choices; function-label tasks use reviewed plain-language contextual meaning/reference; formal A2 structure-label tasks use form choice or contextual meaning; copied-passage clozes were removed from this repair class.','transformations':refined,'validation':{'all_63_machine_repairs_reviewed':'PASS','120_passages_duplicate_prompt_scan':'PASS','60_records_each_level':'PASS','sequence_continuity':'PASS','ten_questions_ten_answers':'PASS','question_answer_linkage':'PASS','target_ids_preserved':'PASS','unbalanced_guillemets':0,'defined_metalinguistic_defect_class_residue':0,'copied_passage_clozes_remaining_in_refined_class':0},'release_effect':'French remains REOPEN_REQUIRED; A1/A2 hashes changed and all recertification gates must bind the final hashes.','next_gate':'Rerun deterministic evidence validation and continue full 100% French semantic educator recertification against final repaired hashes.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reviewed':63,'changed_passages':len(changed),'extra_repairs':len(extra),'before':before,'after':after},ensure_ascii=False,indent=2))