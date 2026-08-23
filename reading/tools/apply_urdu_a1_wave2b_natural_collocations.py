import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading'/'urdu'/'a1'/'passages.jsonl'
REPORT=ROOT/'reading'/'audit'/'urdu_a1_wave2b_natural_collocations_2026-08-23.json'
EXPECTED='c65d1988cd74690c7a42b5a230e5c34c3b75b9b3'


def blob(path): return subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
def words(text): return len(re.findall(r'\S+',text))
def count(text,form): return text.casefold().count(form.casefold())
def parts(ans): return [x.strip() for x in ans.split('؛')]
def reconstruct(prompt,ans):
    out=prompt
    for p in parts(ans):
        if '_____' not in out: raise AssertionError(f'too many key parts {prompt!r}/{ans!r}')
        out=out.replace('_____',p,1)
    if '_____' in out: raise AssertionError(f'too few key parts {prompt!r}/{ans!r}')
    return out

if blob(PATH)!=EXPECTED: raise SystemExit(f'Refusing Wave 2B: expected {EXPECTED}, found {blob(PATH)}')
raw=PATH.read_text(encoding='utf-8').splitlines(); rows=[json.loads(x) for x in raw if x]
assert len(rows)==60 and [r['sequence'] for r in rows]==list(range(1,61))
by={r['id']:r for r in rows}; changed=set(); ops=[]; exposure=[]; reviews=[]

def Q(rid,qid): return next(x for x in by[rid]['questions'] if x['id']==qid)
def A(rid,aid): return next(x for x in by[rid]['answer_key'] if x['id']==aid)

def set_text(rid,old,new,findings):
    row=by[rid]
    if row['text']!=old: raise AssertionError(f'{rid} text drift')
    before_new={t['id']:count(old,str(t.get('form',''))) for t in row.get('new_lexical_targets',[])}
    before_rev={t['id']:count(old,str(t.get('form',''))) for t in row.get('review_lexical_targets',[])}
    row['text']=new; row['word_count']=words(new)
    for t in row.get('new_lexical_targets',[]):
        oldmeta=t.get('exposures_in_text'); after=count(new,str(t.get('form',''))); t['exposures_in_text']=after
        exposure.append({'passage_id':rid,'target_id':t['id'],'form':t.get('form'),'before_text_count':before_new[t['id']],'before_metadata_count':oldmeta,'after_text_count':after,'after_metadata_count':after})
    for t in row.get('review_lexical_targets',[]):
        after=count(new,str(t.get('form','')))
        if after!=before_rev[t['id']]: reviews.append({'passage_id':rid,'target_id':t['id'],'form':t.get('form'),'before_text_count':before_rev[t['id']],'after_text_count':after})
    changed.add(rid); ops.append({'passage_id':rid,'kind':'text','finding_ids':findings,'before':old,'after':new,'word_count_after':row['word_count']})

def fix_q(rid,qid,old,new,new_type=None,findings=None):
    q=Q(rid,qid)
    if q['prompt']!=old: raise AssertionError(f'{rid}/{qid} prompt drift: {q["prompt"]!r}')
    b=dict(q); q['prompt']=new
    if new_type is not None: q['type']=new_type
    changed.add(rid); ops.append({'passage_id':rid,'kind':'question','item':qid,'finding_ids':findings or [],'before':b,'after':dict(q)})

def fix_a(rid,aid,old,new,new_explanation=None,findings=None):
    a=A(rid,aid)
    if a['answer']!=old: raise AssertionError(f'{rid}/{aid} answer drift: {a["answer"]!r}')
    b=dict(a); a['answer']=new
    if new_explanation is not None: a['explanation']=new_explanation
    changed.add(rid); ops.append({'passage_id':rid,'kind':'answer','item':aid,'finding_ids':findings or [],'before':b,'after':dict(a)})

# Unit 2 checkpoint: preserve both review targets in a natural cloze.
fix_q('ur-a1-u02-p06','q7','خالی جگہیں پُر کریں: اس _____ منظم _____ کے لیے میں روز چارٹ دیکھتا ہوں۔','خالی جگہیں پُر کریں: اس _____ اپنی روز کی _____ منظم کرنے کے لیے میں چارٹ دیکھتا ہوں۔',findings=['W0-U2P06-Q7','SC04'])

# Unit 6 P02: natural bus-trip constituent order while preserving سفر/پہلا exposure.
set_text('ur-a1-u06-p02',
'جمعہ کو عائشہ اپنے ماموں کے ساتھ شہر کے ایک حصے تک مختصر سفر کرتی ہے۔ یہ اس سال اس کا پہلا بس کا سفر ہے۔ وہ پہلے اسٹاپ پر وقت سے پہنچتی ہے اور ماموں کے قریب کھڑی رہتی ہے۔ بس آتی ہے تو عائشہ کا پہلا کام اپنا کارڈ تیار کرنا ہے۔ سفر کے دوران وہ کھڑکی سے دکانیں اور پارک دیکھتی ہے۔ ماموں اسے بتاتے ہیں کہ اگلا اسٹاپ ان کا ہے۔ عائشہ پوچھتی ہے کہ سفر کتنا لمبا ہے۔ ماموں کہتے ہیں کہ صرف بیس منٹ۔ بس رکتی ہے تو عائشہ پہلے ماموں کے ساتھ نیچے اترتی ہے۔ اسے اپنا پہلا بس کا سفر آسان اور دلچسپ لگتا ہے۔ بعد میں گھر واپس جا کر وہ خالہ کو سفر کی باتیں بتاتی ہے۔',
'جمعہ کو عائشہ اپنے ماموں کے ساتھ شہر کے ایک حصے تک مختصر سفر کرتی ہے۔ یہ اس سال بس میں اس کا پہلا سفر ہے۔ وہ پہلے اسٹاپ پر وقت سے پہنچتی ہے اور ماموں کے قریب کھڑی رہتی ہے۔ بس آتی ہے تو عائشہ کا پہلا کام اپنا کارڈ تیار کرنا ہے۔ سفر کے دوران وہ کھڑکی سے دکانیں اور پارک دیکھتی ہے۔ ماموں اسے بتاتے ہیں کہ اگلا اسٹاپ ان کا ہے۔ عائشہ پوچھتی ہے کہ سفر کتنا لمبا ہے۔ ماموں کہتے ہیں کہ صرف بیس منٹ۔ بس رکتی ہے تو عائشہ پہلے ماموں کے ساتھ نیچے اترتی ہے۔ اسے بس میں اپنا پہلا سفر آسان اور دلچسپ لگتا ہے۔ بعد میں گھر واپس جا کر وہ خالہ کو سفر کی باتیں بتاتی ہے۔',
['U6P02-01','SC04'])
by['ur-a1-u06-p02']['title']='بس میں پہلا سفر'
ops.append({'passage_id':'ur-a1-u06-p02','kind':'title','finding_ids':['U6P02-01'],'after':'بس میں پہلا سفر'})
fix_a('ur-a1-u06-p02','a6','ایک جگہ سے دوسری جگہ جانے کا عمل یا دورہ۔','ایک جگہ سے دوسری جگہ جانے کا عمل۔',findings=['U6P02-02'])
fix_q('ur-a1-u06-p02','q10','خالی جگہ پُر کریں: یہ میرا _____ بس کا سفر ہے۔','خالی جگہیں پُر کریں: یہ بس میں میرا _____ _____ ہے۔',findings=['U6P02-01'])
fix_a('ur-a1-u06-p02','a10','پہلا','پہلا؛ سفر','پہلے سفر کے لیے «پہلا» اور سفر کے عمل کے لیے «سفر» درست ہیں۔',['U6P02-01'])

# Unit 9 P02: keep bank context, move مقدار to a natural rice-quantity context.
set_text('ur-a1-u09-p02',
'ہفتے کی صبح عائشہ اپنی ماں کے ساتھ بینک جاتی ہے۔ ماں کو ایک بل ادا کرنا ہے اور کچھ رقم گھر کے خرچ کے لیے رکھنی ہے۔ بینک کے دروازے پر ایک ملازم لوگوں کو قطار دکھاتا ہے۔ عائشہ پوچھتی ہے کہ جمع کرانے والی رقم کی مقدار کہاں لکھی ہے۔ ماں اسے رسید پر مقدار دکھاتی ہیں۔ پھر دونوں بینک کی کھڑکی تک پہنچتی ہیں۔ ملازم رقم گنتا ہے اور مقدار دوبارہ بتاتا ہے۔ عائشہ دیکھتی ہے کہ ہر چیز صاف لکھی ہوئی ہے۔ کام مکمل ہونے کے بعد ماں ایک دوسرا کاغذ سنبھال کر رکھتی ہیں۔ بینک سے نکلتے وقت عائشہ کہتی ہے کہ صحیح مقدار لکھنا ضروری ہے تاکہ بعد میں کوئی غلطی نہ ہو۔',
'ہفتے کی صبح عائشہ اپنی ماں کے ساتھ بینک جاتی ہے۔ ماں کو ایک بل ادا کرنا ہے اور کچھ رقم جمع کرانی ہے۔ بینک میں وہ رسید لیتی ہیں اور کام مکمل کرتی ہیں۔ بینک سے نکلنے کے بعد دونوں قریبی دکان پر چاول خریدنے جاتی ہیں۔ ماں عائشہ سے پوچھتی ہیں کہ گھر کے لیے کتنی مقدار چاہیے۔ عائشہ کہتی ہے کہ ایک کلو کی مقدار کافی ہے۔ دکاندار چاول تولتا ہے اور مقدار تھیلے پر لکھ دیتا ہے۔ عائشہ مقدار دوبارہ دیکھتی ہے تاکہ زیادہ چاول نہ خریدے جائیں۔ ماں بینک کی رسید اور خریداری کا کاغذ سنبھال کر رکھتی ہیں۔ عائشہ سمجھتی ہے کہ بینک میں رقم کا حساب اور دکان میں چیز کی مقدار دونوں درست دیکھنا ضروری ہے۔',
['U9P02-01','SC04'])
by['ur-a1-u09-p02']['title']='بینک اور چاول کی مقدار'; ops.append({'passage_id':'ur-a1-u09-p02','kind':'title','finding_ids':['U9P02-01'],'after':'بینک اور چاول کی مقدار'})
fix_q('ur-a1-u09-p02','q4','متن میں «مقدار» کس چیز کو بتاتی ہے؟','متن میں «مقدار» کس چیز کی مقدار بتاتی ہے؟',findings=['U9P02-01'])
fix_a('ur-a1-u09-p02','a4','رقم کتنی ہے۔','چاول کتنے ہیں۔','متن میں مقدار چاول کی مقدار کے لیے آئی ہے۔',['U9P02-01'])
fix_q('ur-a1-u09-p02','q5','عائشہ مقدار کہاں دیکھتی ہے؟','عائشہ چاول کی مقدار کہاں دیکھتی ہے؟',findings=['U9P02-01'])
fix_a('ur-a1-u09-p02','a5','رسید پر۔','تھیلے پر۔','دکاندار مقدار تھیلے پر لکھ دیتا ہے۔',['U9P02-01'])
fix_q('ur-a1-u09-p02','q8','بینک سے نکلنے سے پہلے ماں کیا رکھتی ہیں؟','آخر میں ماں کون سے کاغذ سنبھال کر رکھتی ہیں؟',findings=['U9P02-02'])
fix_a('ur-a1-u09-p02','a8','ایک دوسرا کاغذ سنبھال کر رکھتی ہیں۔','بینک کی رسید اور خریداری کا کاغذ۔','متن میں ماں دونوں کاغذ سنبھال کر رکھتی ہیں۔',['U9P02-02'])

# Unit 9 checkpoint: align review to the repaired natural quantity context.
set_text('ur-a1-u09-p06',
'اس ہفتے عائشہ نے کئی عملی کام کیے۔ خاندان کے دورے میں اس نے تحفہ دینا اور دوسروں کو وقت دینا سیکھا۔ بینک میں اس نے رقم کی مقدار دیکھی اور سمجھا کہ بینک کے کاغذ صاف رکھنا کیوں ضروری ہے۔ مریم سے گفتگو میں اس نے ہاں اور بالکل کہہ کر منصوبے کی تصدیق کی۔ اسکول کے کام میں محنت کے بعد اس نے دیکھا کہ تھوڑی دیر آرام کرنے سے طاقت واپس آ سکتی ہے۔ گھر میں اس نے پنکھے کی حالت دیکھی اور مرمت کا فائدہ سمجھا۔ عائشہ کو اب معلوم ہے کہ روزمرہ کے کام مختلف ہوتے ہیں، مگر ہر کام میں سوال پوچھنا، صحیح مقدار دیکھنا، مناسب جواب دینا، محنت کرنا اور چیز کی حالت سمجھنا مدد دیتا ہے۔ اگلے ہفتے وہ انہی طریقوں کو دوسرے کاموں میں بھی استعمال کرنا چاہتی ہے۔',
'اس ہفتے عائشہ نے کئی عملی کام کیے۔ خاندان کے دورے میں اس نے تحفہ دینا اور دوسروں کو وقت دینا سیکھا۔ بینک کا کام مکمل کرنے کے بعد اس نے دکان میں چاول کی مقدار دیکھی اور دونوں کاموں کے کاغذ سنبھال کر رکھے۔ مریم سے گفتگو میں اس نے ہاں اور بالکل کہہ کر منصوبے کی تصدیق کی۔ اسکول کے کام میں محنت کے بعد اس نے دیکھا کہ تھوڑی دیر آرام کرنے سے طاقت واپس آ سکتی ہے۔ گھر میں اس نے پنکھے کی حالت دیکھی اور مرمت کا فائدہ سمجھا۔ عائشہ کو اب معلوم ہے کہ روزمرہ کے کام مختلف ہوتے ہیں، مگر ہر کام میں سوال پوچھنا، صحیح مقدار دیکھنا، مناسب جواب دینا، محنت کرنا اور چیز کی حالت سمجھنا مدد دیتا ہے۔ اگلے ہفتے وہ انہی طریقوں کو دوسرے کاموں میں بھی استعمال کرنا چاہتی ہے۔',
['U9P06-02','SC03','SC04'])
fix_q('ur-a1-u09-p06','q3','بینک میں عائشہ نے کس چیز کی مقدار دیکھی؟','بینک کے بعد دکان میں عائشہ نے کس چیز کی مقدار دیکھی؟',findings=['U9P06-02'])
fix_a('ur-a1-u09-p06','a3','رقم کی مقدار۔','چاول کی مقدار۔','متن میں بینک کے بعد چاول خریدنے کا ذکر ہے۔',['U9P06-02'])

# Unit 10 P02: remove اردو کی زبان / لفظ کی مقدار while preserving a natural مقدار review example.
set_text('ur-a1-u10-p02',
'اسکول میں آج عائشہ اردو کی زبان کے ساتھ ایک نیا لفظ سیکھتی ہے۔ استاد تختے پر لفظ لکھتے ہیں اور کہتے ہیں کہ زبان سیکھنے میں نیا لفظ بار بار سننا مفید ہوتا ہے۔ عائشہ لفظ پڑھتی ہے، پھر اسے ایک جملے میں استعمال کرتی ہے۔ وقفے میں وہ مریم کو بتاتی ہے کہ اس نے آج زبان کے بارے میں نیا سوال بھی پوچھا۔ مریم ہنستی ہے اور کہتی ہے کہ اس نے بینک کے باہر بھی یہی لفظ ایک اعلان میں دیکھا تھا۔ عائشہ کہتی ہے کہ لفظ کی مقدار نہیں، درست استعمال اہم ہے۔ گھر جاتے وقت وہ نیا لفظ اپنی کاپی میں لکھتی ہے۔ اسے لگتا ہے کہ ہر دن زبان میں کچھ نیا سیکھا جا سکتا ہے۔',
'اسکول میں آج عائشہ اردو کا ایک نیا لفظ سیکھتی ہے۔ استاد تختے پر لفظ لکھتے ہیں اور کہتے ہیں کہ نئی زبان سیکھتے وقت نیا لفظ بار بار سننا مفید ہوتا ہے۔ عائشہ لفظ پڑھتی ہے، پھر اسے ایک جملے میں استعمال کرتی ہے۔ وقفے میں وہ مریم کو بتاتی ہے کہ اس نے آج زبان کے بارے میں نیا سوال بھی پوچھا۔ مریم کہتی ہے کہ اس نے بینک کے باہر بھی یہی لفظ ایک اعلان میں دیکھا تھا۔ استاد ایک اور مثال دیتے ہیں: بوتل میں پانی کی مقدار کم ہے۔ عائشہ کہتی ہے کہ ہر زبان میں نیا لفظ درست جملے کے ساتھ یاد کرنا بہتر ہے۔ گھر جاتے وقت وہ نیا لفظ اپنی کاپی میں لکھتی ہے اور سوچتی ہے کہ زبان میں ہر دن کچھ نیا سیکھا جا سکتا ہے۔',
['U10P02-01','U10P02-02','SC04'])
fix_a('ur-a1-u10-p02','a1','اردو کی زبان میں ایک نیا لفظ۔','اردو کا ایک نیا لفظ۔','متن کے آغاز میں یہی بات بیان ہوئی ہے۔',['U10P02-01'])
fix_q('ur-a1-u10-p02','q8','عائشہ لفظ کی مقدار کے بارے میں کیا کہتی ہے؟','استاد «مقدار» کی مثال کس چیز سے دیتے ہیں؟',findings=['U10P02-02'])
fix_a('ur-a1-u10-p02','a8','وہ کہتی ہے کہ درست استعمال اہم ہے۔','بوتل کے پانی سے۔','استاد کہتے ہیں: «بوتل میں پانی کی مقدار کم ہے۔»',['U10P02-02'])

# Unit 10 checkpoint: operational frequency wording.
fix_q('ur-a1-u10-p06','q4','عادت کی مقدار بتانے کے لیے کون سے دو الفاظ آتے ہیں؟','کوئی کام کتنی بار ہوتا ہے، یہ بتانے کے لیے کون سے دو الفاظ آتے ہیں؟',findings=['U10P06-01','SC04'])

for rid in changed:
    row=by[rid]; row['revision']=int(row.get('revision',0))+1
    qual=row.setdefault('quality',{})
    for k in ('coverage_check','answer_key_check','linguistic_review','pedagogical_review','schema_check'): qual[k]='pending'
    qual['status']='draft'; note='Wave 2B natural-collocation repair applied 2026-08-23; full gate revalidation pending.'
    qual.setdefault('notes',[])
    if note not in qual['notes']: qual['notes'].append(note)

clozes=[]
for row in rows:
    ans={a['question_id']:a for a in row['answer_key']}
    for q in row['questions']:
        a=ans.get(q['id']); assert a and a['id']==q['answer_id']
        if q.get('type')=='cloze_transfer': clozes.append(reconstruct(q['prompt'],a['answer']))
assert len(clozes)==130

out=[]
for original,row in zip(raw,rows): out.append(json.dumps(row,ensure_ascii=False,separators=(',',':')) if row['id'] in changed else original)
PATH.write_text('\n'.join(out)+'\n',encoding='utf-8')
REPORT.write_text(json.dumps({'schema_version':1,'date':'2026-08-23','language':'urdu','level':'A1','input_git_blob_sha':EXPECTED,'changed_passage_ids':sorted(changed),'changed_passage_count':len(changed),'operations':ops,'new_target_exposure_deltas':exposure,'review_target_text_occurrence_deltas':reviews,'cloze_question_count':len(clozes),'all_cloze_structures_reconstructed':True,'quality_promotion':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'changed':sorted(changed),'clozes':len(clozes),'exposure':exposure,'review_deltas':reviews},ensure_ascii=False))
