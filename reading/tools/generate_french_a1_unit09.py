#!/usr/bin/env python3
# Append French A1 Unit 09 (sequences 49-54) as one guarded batch.
from __future__ import annotations
import base64,csv,json,re,subprocess,zlib
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/french/a1/passages.jsonl'; SCHEMA=ROOT/'reading/schema/passage.schema.json'; LEXICON=ROOT/'french_top1000.csv'
EXPECTED_BLOB='3da2da2bfe133ed0bfa59c792e15fa251a343b77'
NEW_FORMS=('famille','père','mère','ami','livre','école','porte','table','eau','travail')
DATA=json.loads(zlib.decompress(base64.b64decode('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')).decode())
SPECS=DATA['specs'];P06=DATA['p06']
def lexicon():
 d={}
 with LEXICON.open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   form=(row.get('Front') or '').strip();back=row.get('Back') or ''
   a=re.search(r'Rank:\s*(\d+)',back);b=re.search(r'Meaning:\s*(.+)',back);c=re.search(r'Part of speech:\s*(.+)',back)
   if form and a and b and c:d[form]={'rank':int(a.group(1)),'sense':b.group(1).strip(),'pos':c.group(1).strip()}
 return d
def tid(r):return f'fr-rank-{r:04d}'
def count(text,form):return len(re.findall(rf'(?<!\w){re.escape(form)}(?!\w)',text,flags=re.I|re.UNICODE))
def prior(rows):
 d={}
 for r in rows:
  for t in r.get('new_lexical_targets',[]):
   if isinstance(t,dict) and t.get('form'):d.setdefault(t['form'],[]).append(t)
 return d
def nt(f,text,L):
 s=L[f];n=count(text,f)
 if n<1:raise AssertionError(f'{f}: invisible new target')
 return {'id':tid(s['rank']),'form':f,'lemma':f,'intended_sense':s['sense'],'part_of_speech':s['pos'],'register':'contemporary standard','variety':None,'context_strategy':['scenario_resolution'],'first_introduced':True,'exposures_in_text':n,'source_lexicon':'french_top1000.csv','source_rank':s['rank'],'beyond_base':False}
def rev(f,P):
 h=P.get(f,[])
 if len(h)!=1:raise AssertionError(f'{f}: expected one earlier deliberate target, got {len(h)}')
 return {'id':h[0]['id'],'form':f,'review_stage':'R2','representation':'running_text','expected_exposure_number':None}
def cur(f,L):return {'id':tid(L[f]['rank']),'form':f,'review_stage':'R1','representation':'summary','expected_exposure_number':None}
def qa(items,ids):
 qs=[];ans=[]
 for i,(typ,prompt,answer,forms) in enumerate(items,1):
  qid=f'q{i}';aid=f'a{i}';q={'id':qid,'type':typ,'prompt':prompt,'answer_id':aid}
  if forms:q['target_ids']=[ids[f] for f in forms]
  qs.append(q);ans.append({'id':aid,'question_id':qid,'answer':answer,'explanation':''})
 return qs,ans
def mk(s,new,reviews,ids,speed=False):
 qs,ans=qa(s['items'],ids);text=s['text']
 return {'id':s['pid'],'language':'fr','cefr':'A1','unit':9,'sequence':s['seq'],'revision':1,'title':s['title'],'passage_type':s['ptype'],'genre':s['genre'],'domains':s['domains'],'topics':s['topics'],'text':text,'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!?](?:[»”"])?',text))),'estimated_known_token_coverage':0,'new_lexical_targets':new,'review_lexical_targets':reviews,'grammar_targets':s['grammar'],'discourse_targets':s['discourse'],'questions':qs,'answer_key':ans,'speed_training':{'timed':speed,'benchmark_eligible':speed,'comprehension_gate':0.8,'new_word_policy':'none' if speed else 'controlled','notes':'Generation-stage French A1 Unit 09; full multi-pass audit deferred.'},'quality':{'status':'draft','schema_check':'pending','linguistic_review':'pending','pedagogical_review':'pending','answer_key_check':'pending','coverage_check':'pending','fact_check':'not_required','notes':['Guarded French A1 Unit 09 generation batch.','Schema, source identity, word band, local target declaration, linkage, visible review, continuity, and checkpoint invariants are enforced.']},'paired_text_group':None,'prerequisites':['French A1 Units 01-08 canonical corpus'],'difficulty_notes_internal':'A1 consolidation: family/friend nouns, school/work vocabulary, everyday objects, with spaced review of Unit 08 body and health terms.','reader_tags':['unit_role:'+s['ptype'],'generation_batch','french_a1_u09']}
def build(rows,L):
 P=prior(rows)
 for f in NEW_FORMS:
  if f not in L:raise AssertionError(f'{f}: missing from french_top1000.csv')
  if P.get(f):raise AssertionError(f'{f}: already deliberately introduced before Unit 09')
 out=[]
 for s in SPECS:
  new=[nt(f,s['text'],L) for f in s['forms']];reviews=[rev(f,P) for f in s['reviews']];ids={t['form']:t['id'] for t in new+reviews};out.append(mk(s,new,reviews,ids))
 reviews=[cur(f,L) for f in NEW_FORMS];ids={t['form']:t['id'] for t in reviews}
 s={'pid':'fr-a1-u09-p06','seq':54,'ptype':'checkpoint','title':'Personnes et objets du quotidien','genre':'cumulative everyday-vocabulary summary','domains':['personal','educational','public'],'topics':['people','objects','daily activity'],'text':P06['text'],'grammar':[{'id':'fr-a1-u09-people-review','role':'integration','description':'integrate core family and friend nouns'},{'id':'fr-a1-u09-object-review','role':'integration','description':'integrate school/work, door, table, book, and water nouns'}],'discourse':[{'id':'fr-a1-u09-categories','role':'integration','description':'distinguish familiar people, objects, places, and tasks'}],'items':P06['items']}
 out.append(mk(s,[],reviews,ids,True));return out
def main():
 blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
 if blob!=EXPECTED_BLOB:raise AssertionError(f'canonical blob drift: {blob} != {EXPECTED_BLOB}')
 rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=48 or [r['sequence'] for r in rows]!=list(range(1,49)) or rows[-1]['id']!='fr-a1-u08-p06':raise AssertionError('expected exact 48-passage frontier through Unit 08')
 L=lexicon();unit=build(rows,L);V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
 if [r['sequence'] for r in unit]!=list(range(49,55)) or len({r['id'] for r in rows+unit})!=54:raise AssertionError('Unit 09 continuity failure')
 old={t['id'] for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')};newids=[]
 for r in unit:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:5]]}")
  if not 90<=r['word_count']<=140:raise AssertionError(f"{r['id']}: word band {r['word_count']}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: assessment count")
  amap={a['question_id']:a['id'] for a in r['answer_key']};local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict)}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id']:raise AssertionError(f"{r['id']} {q['id']}: linkage")
   if any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: undeclared target")
  for t in r['new_lexical_targets']:
   if t['id'] in old:raise AssertionError(f"{r['id']}: reintroduced {t['id']}")
   x=L.get(t['form'])
   if not x or t['source_rank']!=x['rank'] or t['id']!=tid(x['rank']):raise AssertionError(f"{r['id']}: source identity {t['form']}")
   if count(r['text'],t['form'])!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: exposure mismatch {t['form']}")
   newids.append(t['id'])
  for t in r['review_lexical_targets']:
   if t['representation'] in {'running_text','summary'} and count(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
 if len(newids)!=10 or len(set(newids))!=10:raise AssertionError(f'expected 10 unique new targets, got {len(newids)}/{len(set(newids))}')
 if unit[-1]['new_lexical_targets']:raise AssertionError('Unit 09 P06 must have zero new targets')
 original=CANON.read_text(encoding='utf-8');original += '' if original.endswith('\n') else '\n';CANON.write_text(original+''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in unit),encoding='utf-8')
 final=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(final)!=54 or [r['sequence'] for r in final]!=list(range(1,55)):raise AssertionError('post-write continuity failure')
 print(json.dumps({'status':'PASS','unit':9,'appended_passages':6,'french_a1_total':54,'word_counts':{r['id']:r['word_count'] for r in unit},'new_targets':10,'questions':60,'answers':60,'checkpoint_new_targets':0},ensure_ascii=False))
if __name__=='__main__':main()
