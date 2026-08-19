import json, hashlib, pathlib
p=pathlib.Path('reading/french/c1/passages.jsonl')
a=pathlib.Path('reading/audit/french_c1_u01_p06_followup_repair_2026-08-19.json')
rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
assert len(rows)==60 and [r['sequence'] for r in rows]==list(range(1,61))
r=next(x for x in rows if x['id']=='fr-c1-u01-p06')
before=hashlib.sha256(p.read_bytes()).hexdigest()
q={x['id']:x for x in r['questions']}; ans={x['id']:x for x in r['answer_key']}
assert q['q1']['prompt']=='Quelles sont les cinq exigences que cette synthèse synthétise ?'
q['q1']['prompt']='Quelles sont les cinq exigences que cette synthèse réunit ?'
q['q10']['prompt']='Résume la synthèse.'
assert ans['a10']['answer'].startswith('Le checkpoint organise les vingt formes de l’unité')
ans['a10']['answer']='La synthèse organise les vingt formes de l’unité autour d’un raisonnement qui sépare preuve, interprétation, portée, contreargument et critère de décision tout en restant réellement révisable.'
r['topics']=['synthèse' if t=='checkpoint' else t for t in r.get('topics',[])]
r['revision']=int(r.get('revision',2))+1
assert len(r['questions'])==len(r['answer_key'])==10
assert {x['answer_id'] for x in r['questions']}=={x['id'] for x in r['answer_key']}
for t in r.get('review_lexical_targets',[]):
    if t.get('representation') in {'running_text','summary'}: assert t['form'] in r['text'], t['form']
learner='\n'.join([r.get('text',''),r.get('title','')]+[x['prompt'] for x in r['questions']]+[x['answer'] for x in r['answer_key']])
for bad in ['research and evidence','Le checkpoint organise','cette synthèse synthétise']: assert bad not in learner,bad
p.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
after=hashlib.sha256(p.read_bytes()).hexdigest(); assert after!=before
a.write_text(json.dumps({'audit':'French C1 P06 follow-up educator repair','date':'2026-08-19','status':'PASS','passage_id':r['id'],'before_c1_sha256':before,'after_c1_sha256':after,'repairs':['q1 tautology','q10 wording','a10 checkpoint wording','topic label'],'review_forms_preserved':True,'qa_linkage':'PASS'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(before,after)
