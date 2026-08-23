import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading'/'urdu'/'a1'/'passages.jsonl'
REPORT=ROOT/'reading'/'audit'/'urdu_a1_wave2a_operational_questions_2026-08-23.json'
EXPECTED='1ffdbba556b5d9b42b07c454ce84d4e728c1e19e'


def blob(path):
    return subprocess.check_output(['git','hash-object',str(path)],text=True).strip()

def key_parts(answer):
    return [x.strip() for x in answer.split('؛')]

def reconstruct(prompt,answer):
    out=prompt
    for p in key_parts(answer):
        if '_____' not in out: raise AssertionError(f'too many key parts: {prompt!r}')
        out=out.replace('_____',p,1)
    if '_____' in out: raise AssertionError(f'too few key parts: {prompt!r}')
    return out

if blob(PATH)!=EXPECTED:
    raise SystemExit(f'Refusing Wave 2A: expected {EXPECTED}, found {blob(PATH)}')
raw=PATH.read_text(encoding='utf-8').splitlines()
rows=[json.loads(x) for x in raw if x]
assert len(rows)==60 and [r['sequence'] for r in rows]==list(range(1,61))
by_id={r['id']:r for r in rows}
changed=set(); ops=[]

def Q(rid,qid): return next(x for x in by_id[rid]['questions'] if x['id']==qid)
def A(rid,aid): return next(x for x in by_id[rid]['answer_key'] if x['id']==aid)

def fix(rid,qid,aid,old_q,new_q,old_a,new_a,new_type,finding_ids):
    q=Q(rid,qid); a=A(rid,aid)
    if q['prompt']!=old_q: raise AssertionError(f'{rid}/{qid} prompt drift: {q["prompt"]!r}')
    if a['answer']!=old_a: raise AssertionError(f'{rid}/{aid} answer drift: {a["answer"]!r}')
    before_q=dict(q); before_a=dict(a)
    q['prompt']=new_q; q['type']=new_type; a['answer']=new_a
    changed.add(rid)
    ops.append({'passage_id':rid,'question_id':qid,'answer_id':aid,'finding_ids':finding_ids,'before_question':before_q,'after_question':dict(q),'before_answer':before_a,'after_answer':dict(a)})

# Unit 1: replace grammar labels with concrete use/reference.
fix('ur-a1-u01-p04','q3','a3','«اگر» جملے کے کس حصے کو شروع کرتا ہے؟ الف) شرط ب) جگہ ج) شخص','«اگر بارش شروع ہو تو ہم گھر میں رہیں گے» میں گھر میں رہنے کی شرط کیا ہے؟','الف) شرط۔','بارش شروع ہونا۔','vocabulary_in_context',['U1P04-02','SC05'])
fix('ur-a1-u01-p04','q6','a6','«اگر» کا کام کیا ہے؟','کون سا جملہ درست ہے: «اگر بارش ہو تو ہم گھر میں رہیں گے» یا «بارش اگر گھر ہم رہیں گے»؟','کسی شرط کو بیان کرنا۔','«اگر بارش ہو تو ہم گھر میں رہیں گے»۔','contrast',['SC05'])
fix('ur-a1-u01-p05','q10','a10','«ہم» کس قسم کا لفظ ہے؟','اگر عائشہ اپنے اور مریم کے بارے میں بات کرے تو کون سا لفظ کہے گی: «میں» یا «ہم»؟','ضمیر۔','ہم۔','contrast',['U1P05-01','SC05'])
fix('ur-a1-u01-p06','q8','a8','«اگر موسم اچھا ہو» میں «اگر» کیا متعارف کراتا ہے؟','اگر موسم اچھا ہو تو عائشہ اتوار کو کہاں جاتی ہے؟','ایک شرط۔','پارک۔','literal_detail',['U1P06-02','SC05'])

# Unit 2: understand phrases/use instead of naming grammar functions/classes.
fix('ur-a1-u02-p01','q8','a8','«کچھ نہ رہ جائے» میں «نہ» کیا کرتا ہے؟','«کچھ نہ رہ جائے» کا مطلب کیا ہے؟','یہ نفی کرتا ہے، یعنی چیز کے رہ جانے کو رد کرتا ہے۔','کوئی ضروری چیز پیچھے نہ چھوٹے۔','vocabulary_in_context',['U2P01-01','SC05'])
fix('ur-a1-u02-p02','q8','a8','«اس کی روز کی زندگی» میں «کی» کیا تعلق دکھاتا ہے؟','«اس کی روز کی زندگی» کس کی زندگی ہے؟','یہ عائشہ اور اس کی زندگی کے درمیان ملکیت/تعلق دکھاتا ہے۔','عائشہ کی۔','reference_resolution',['U2P02-01','SC05'])
fix('ur-a1-u02-p03','q8','a8','«کیا تم میری مدد کر سکتی ہو؟» کس قسم کا سوال ہے؟','«کیا تم میری مدد کر سکتی ہو؟» کا مختصر مثبت جواب کیا ہوگا؟','ایسا سوال جس کا جواب ہاں یا نہیں میں دیا جا سکتا ہے۔','ہاں، کر سکتی ہوں۔','vocabulary_in_context',['U2P03-02','SC05'])

# Unit 3: reason connector and reflexive possession through actual context.
fix('ur-a1-u03-p01','q4','a4','«کیونکہ» جملے میں کیا کام کرتا ہے؟','عائشہ سیب کیوں لیتی ہے؟','یہ وجہ بتاتا ہے۔','کیونکہ اسے سیب پسند ہے۔','cause_effect',['U3P01-01','SC05'])
fix('ur-a1-u03-p01','q7','a7','«کیونکہ» کس قسم کا تعلق بناتا ہے؟','دو باتوں میں وجہ بتانے کے لیے کون سا لفظ آیا ہے؟','سبب یا وجہ جوڑنے والا حرفِ ربط۔','کیونکہ۔','vocabulary_in_context',['U3P01-01','SC05'])
fix('ur-a1-u03-p05','q3','a3','متن میں «اپنا» کس تعلق کو دکھاتا ہے؟','«عائشہ اپنا ناشتہ خود تیار کرے گی» میں ناشتہ کس کا ہے؟','اپنی ملکیت یا اپنے ہی کام کی طرف اشارہ کرتا ہے۔','عائشہ کا۔','reference_resolution',['U3P05-01','SC05'])

# Unit 4: possessives/ordinal form through concrete reference and contrast.
fix('ur-a1-u04-p03','q4','a4','«ہمارے گھر» میں «ہمارے» کس تعلق کو دکھاتا ہے؟','عائشہ کہتی ہے «ہمارے گھر»۔ یہ گھر کن لوگوں کا ہے؟','عائشہ اور اس کے گھر والوں سے متعلق۔','عائشہ اور اس کے گھر والوں کا۔','reference_resolution',['U4P03-02','SC05'])
fix('ur-a1-u04-p04','q3','a3','«میرا نام حارث ہے» میں «میرا» کیا تعلق دکھاتا ہے؟','«میرا نام حارث ہے» میں نام کس کا ہے؟','اپنی ملکیت یا اپنے بارے میں۔','حارث کا۔','reference_resolution',['U4P04-01','SC05'])
fix('ur-a1-u04-p05','q7','a7','«دوسری» کا مطلب کیا ہے؟','«پہلی کتاب سرخ ہے اور دوسری نیلی ہے» میں «دوسری» کون سی کتاب ہے؟','پہلی کے بعد والی یا کوئی اور مؤنث چیز۔','پہلی کے بعد والی کتاب۔','vocabulary_in_context',['U4P05-01','SC05'])

# Unit 7: markers/adverbs in usable phrases rather than formal descriptions.
fix('ur-a1-u07-p01','q7','a7','«ہفتے» کس وقت کی اکائی سے متعلق ہے؟','«اگلے ہفتے» میں «ہفتے» سے کتنا وقت مراد ہے؟','سات دن کے عرصے کی حالت؛ ہفتہ کے بعد استعمال ہونے والی صورت۔','سات دن کا عرصہ۔','vocabulary_in_context',['U7P01-02','SC05'])
fix('ur-a1-u07-p02','q3','a3','متن میں «بجے» کیا بتاتا ہے؟','«کلاس نو بجے شروع ہوتی ہے» میں «نو بجے» کیا بتاتا ہے؟','گھڑی کے مقررہ گھنٹے کو بتانے والا وقت کا لفظ۔','کلاس شروع ہونے کا وقت۔','vocabulary_in_context',['U7P02-02','SC05'])
fix('ur-a1-u07-p02','q6','a6','«بجے» کا بنیادی استعمال کیا ہے؟','گھڑی کا وقت بتاتے ہوئے «نو» کے بعد کون سا لفظ آتا ہے؟','گھڑی کے گھنٹے کے ساتھ استعمال ہونے والا لفظ۔','بجے۔','vocabulary_in_context',['U7P02-02','SC05'])
fix('ur-a1-u07-p05','q4','a4','متن میں «تقریباً» کس طرح کی مقدار بتاتا ہے؟','«تقریباً پانچ منٹ» کا مطلب کیا ہے؟','بالکل نہیں بلکہ اندازاً مقدار یا وقت بتانا۔','پانچ منٹ کے قریب، ضروری نہیں کہ بالکل پانچ منٹ۔','vocabulary_in_context',['U7P05-01','SC05'])

# Unit 9: confirmation through communicative interpretation/use.
fix('ur-a1-u09-p03','q4','a4','متن میں «بالکل» کیا معنی بڑھاتا ہے؟','عائشہ کہتی ہے: «ہاں، بالکل آؤں گی۔» یہاں «بالکل» کیا بتاتا ہے؟ الف) وہ ضرور آئے گی ب) شاید آئے گی ج) نہیں آئے گی','یہ مکمل یقین یا واضح موافقت دکھاتا ہے۔','الف) وہ ضرور آئے گی۔','vocabulary_in_context',['U9P03-01','SC05'])
fix('ur-a1-u09-p03','q6','a6','«ہاں» کا بنیادی استعمال کیا ہے؟','اگر کوئی پوچھے «کیا تم آؤ گی؟» تو مثبت جواب کے لیے کون سا لفظ کہیں گے؟','کسی سوال کا مثبت جواب دینا۔','ہاں۔','vocabulary_in_context',['U9P03-02','SC05'])

for rid in changed:
    row=by_id[rid]
    row['revision']=int(row.get('revision',0))+1
    qual=row.setdefault('quality',{})
    for k in ('answer_key_check','linguistic_review','pedagogical_review','schema_check'):
        qual[k]='pending'
    qual['status']='draft'
    note='Wave 2A A1-operational question repair applied 2026-08-23; gate revalidation pending.'
    qual.setdefault('notes',[])
    if note not in qual['notes']: qual['notes'].append(note)

clozes=[]
for row in rows:
    ans_by_q={a['question_id']:a for a in row['answer_key']}
    for q in row['questions']:
        linked=ans_by_q.get(q['id'])
        assert linked and linked['id']==q['answer_id']
        if q.get('type')=='cloze_transfer': clozes.append(reconstruct(q['prompt'],linked['answer']))
assert len(clozes)==130

out=[]
for original,row in zip(raw,rows):
    out.append(json.dumps(row,ensure_ascii=False,separators=(',',':')) if row['id'] in changed else original)
PATH.write_text('\n'.join(out)+'\n',encoding='utf-8')
REPORT.write_text(json.dumps({
    'schema_version':1,'date':'2026-08-23','language':'urdu','level':'A1','input_git_blob_sha':EXPECTED,
    'changed_passage_ids':sorted(changed),'changed_passage_count':len(changed),'operations':ops,
    'cloze_question_count':len(clozes),'all_cloze_structures_reconstructed':True,
    'passage_text_changed':False,'lexical_exposure_counts_changed':False,'quality_promotion':False
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'changed':sorted(changed),'operations':len(ops),'clozes':len(clozes)},ensure_ascii=False))
