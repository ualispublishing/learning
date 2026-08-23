import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading'/'urdu'/'a1'/'passages.jsonl'
REPORT=ROOT/'reading'/'audit'/'urdu_a1_postaudit_polish_2026-08-23.json'
EXPECTED='293cdb4ec7855f2c34583e29e47775424faad8b4'
def blob(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def exact(text,form): return len(re.findall(rf'(?<!\w){re.escape(form)}(?!\w)',text,flags=re.UNICODE|re.IGNORECASE))
def sc(text): return sum(text.count(x) for x in ('۔','؟','?','!'))
assert blob(PATH)==EXPECTED,(blob(PATH),EXPECTED)
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
byid={r['id']:r for r in rows}; changes=[]
r=byid['ur-a1-u09-p02']
old='عائشہ کہتی ہے کہ ایک کلو کی مقدار کافی ہے۔'; new='عائشہ کہتی ہے کہ چاول کی مناسب مقدار ایک کلو ہے۔'
assert old in r['text']; r['text']=r['text'].replace(old,new,1); changes.append({'passage_id':r['id'],'kind':'text','before':old,'after':new})
q=next(q for q in r['questions'] if q['id']=='q2'); assert q['prompt']=='ماں کو بینک میں رقم کے ساتھ کیا کرنا ہے؟'; q['prompt']='ماں کو بینک میں رقم کا کیا کام کرنا ہے؟'; changes.append({'passage_id':r['id'],'kind':'question','item':'q2','after':q['prompt']})
a=next(a for a in r['answer_key'] if a['question_id']=='q4'); assert a['answer']=='چاول کتنے ہیں۔'; a['answer']='چاول کی۔'; a['explanation']='متن میں «مقدار» چاول کی مقدار کے لیے آئی ہے۔'; changes.append({'passage_id':r['id'],'kind':'answer','item':'q4','after':a['answer']})
a=next(a for a in r['answer_key'] if a['question_id']=='q7'); assert a['answer']=='کسی چیز کی کتنی مقدار ہے۔'; a['answer']='کسی چیز کی مقدار، یعنی وہ کتنی ہے۔'; changes.append({'passage_id':r['id'],'kind':'answer','item':'q7','after':a['answer']})
q=next(q for q in r['questions'] if q['id']=='q8'); assert q['type']=='sequence'; q['type']='literal_detail'; changes.append({'passage_id':r['id'],'kind':'question_type','item':'q8','after':'literal_detail'})
r['word_count']=len(re.findall(r'\S+',r['text'])); r['sentence_count']=sc(r['text']); r['revision']=int(r.get('revision',0))+1
for t in r.get('new_lexical_targets',[]): t['exposures_in_text']=exact(r['text'],str(t.get('form','')))
note='Post-audit Urdu naturalness polish applied 2026-08-23; independent integrity audit must be rerun.'
if note not in r['quality'].setdefault('notes',[]): r['quality']['notes'].append(note)
for g in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check'): r['quality'][g]='pending'
r['quality']['status']='draft'
# Small explanation-only polish noticed during adversarial read.
r2=byid['ur-a1-u08-p02']; a2=next(a for a in r2['answer_key'] if a['question_id']=='q10')
assert a2['explanation']=='سنائی دینے والی بولی کے لیے «آواز» درست ہے۔'; a2['explanation']='بولنے کی سنائی دینے والی صدا کے لیے «آواز» درست ہے۔'; changes.append({'passage_id':r2['id'],'kind':'answer_explanation','item':'q10','after':a2['explanation']}); r2['revision']=int(r2.get('revision',0))+1
if note not in r2['quality'].setdefault('notes',[]): r2['quality']['notes'].append(note)
for g in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check'): r2['quality'][g]='pending'
r2['quality']['status']='draft'
# Revalidate global invariants.
clozes=0; review_zero=[]
for row in rows:
 assert len(row['questions'])==10 and len(row['answer_key'])==10
 amap={a['question_id']:a for a in row['answer_key']}
 assert len(amap)==10
 for q in row['questions']:
  a=amap[q['id']]; assert q['answer_id']==a['id']
  if q['type']=='cloze_transfer':
   clozes+=1; parts=[x.strip() for x in str(a['answer']).split('؛')]; assert q['prompt'].count('_____')==len(parts); assert all(not p.endswith(('۔','؟','?','!','.')) for p in parts)
 for t in row.get('new_lexical_targets',[]): assert t['exposures_in_text']==exact(row['text'],str(t.get('form',''))) and t['exposures_in_text']>=1
 for t in row.get('review_lexical_targets',[]):
  if exact(row['text'],str(t.get('form','')))==0: review_zero.append((row['id'],t.get('id'),t.get('form')))
 assert row['word_count']==len(re.findall(r'\S+',row['text'])); assert row['sentence_count']==sc(row['text'])
assert clozes==130 and not review_zero
PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+'\n',encoding='utf-8')
out=blob(PATH)
REPORT.write_text(json.dumps({'schema_version':1,'date':'2026-08-23','input_git_blob_sha':EXPECTED,'output_git_blob_sha':out,'changes':changes,'cloze_question_count':clozes,'review_target_zero_exact_occurrence_count':0,'quality_promotion':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)
