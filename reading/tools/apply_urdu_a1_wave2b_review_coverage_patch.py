import json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading'/'urdu'/'a1'/'passages.jsonl'
REPORT=ROOT/'reading'/'audit'/'urdu_a1_wave2b_review_coverage_patch_2026-08-23.json'
EXPECTED='664c30cf27fe10c95957e1ea29c69605d9fbb95f'

def blob(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def cnt(t,f): return t.casefold().count(f.casefold())
def wc(t): return len(re.findall(r'\S+',t))
def parts(a): return [x.strip() for x in a.split('؛')]
def rec(p,a):
    o=p
    for x in parts(a): o=o.replace('_____',x,1)
    if '_____' in o: raise AssertionError('unfilled cloze')
    return o
if blob(PATH)!=EXPECTED: raise SystemExit(f'expected {EXPECTED}, found {blob(PATH)}')
raw=PATH.read_text(encoding='utf-8').splitlines(); rows=[json.loads(x) for x in raw if x]
assert len(rows)==60
row=next(r for r in rows if r['id']=='ur-a1-u09-p02')
old='ہفتے کی صبح عائشہ اپنی ماں کے ساتھ بینک جاتی ہے۔ ماں کو ایک بل ادا کرنا ہے اور کچھ رقم جمع کرانی ہے۔ بینک میں وہ رسید لیتی ہیں اور کام مکمل کرتی ہیں۔ بینک سے نکلنے کے بعد دونوں قریبی دکان پر چاول خریدنے جاتی ہیں۔ ماں عائشہ سے پوچھتی ہیں کہ گھر کے لیے کتنی مقدار چاہیے۔ عائشہ کہتی ہے کہ ایک کلو کی مقدار کافی ہے۔ دکاندار چاول تولتا ہے اور مقدار تھیلے پر لکھ دیتا ہے۔ عائشہ مقدار دوبارہ دیکھتی ہے تاکہ زیادہ چاول نہ خریدے جائیں۔ ماں بینک کی رسید اور خریداری کا کاغذ سنبھال کر رکھتی ہیں۔ عائشہ سمجھتی ہے کہ بینک میں رقم کا حساب اور دکان میں چیز کی مقدار دونوں درست دیکھنا ضروری ہے۔'
new='ہفتے کی صبح عائشہ اپنی ماں کے ساتھ بینک جاتی ہے۔ ماں کو ایک بل ادا کرنا ہے اور کچھ رقم جمع کرانی ہے۔ بینک میں وہ رسید لیتی ہیں اور کام مکمل کرتی ہیں۔ بینک سے نکلنے کے بعد دونوں قریبی دکان پر چاول خریدنے جاتی ہیں۔ ماں عائشہ سے پوچھتی ہیں کہ گھر کے لیے کتنی مقدار چاہیے۔ عائشہ کہتی ہے کہ ایک کلو کی مقدار کافی ہے۔ دکاندار چاول تولتا ہے اور مقدار تھیلے پر لکھ دیتا ہے۔ عائشہ مقدار دوبارہ دیکھتی ہے تاکہ زیادہ چاول نہ خریدے جائیں۔ ماں بینک کی رسید سنبھال کر رکھتی ہیں اور خریداری کا دوسرا کاغذ بھی ساتھ رکھتی ہیں۔ عائشہ سمجھتی ہے کہ بینک میں رقم کا حساب اور دکان میں چیز کی مقدار دونوں درست دیکھنا ضروری ہے۔'
if row['text']!=old: raise AssertionError('u09-p02 text drift')
before={t['id']:cnt(old,t['form']) for t in row.get('review_lexical_targets',[])}
row['text']=new; row['word_count']=wc(new); row['revision']=int(row.get('revision',0))+1
for t in row.get('new_lexical_targets',[]): t['exposures_in_text']=cnt(new,t['form'])
after={t['id']:cnt(new,t['form']) for t in row.get('review_lexical_targets',[])}
assert before['ur-rank-0443']==0 and after['ur-rank-0443']==1
q=row['quality'];
for k in ('coverage_check','answer_key_check','linguistic_review','pedagogical_review','schema_check'): q[k]='pending'
q['status']='draft'; note='Wave 2B review-coverage patch applied 2026-08-23; gate revalidation pending.'
if note not in q.setdefault('notes',[]): q['notes'].append(note)
cl=0
for r in rows:
    ans={a['question_id']:a for a in r['answer_key']}
    for qu in r['questions']:
        assert ans[qu['id']]['id']==qu['answer_id']
        if qu.get('type')=='cloze_transfer': rec(qu['prompt'],ans[qu['id']]['answer']); cl+=1
assert cl==130
out=[]
for orig,r in zip(raw,rows): out.append(json.dumps(r,ensure_ascii=False,separators=(',',':')) if r['id']=='ur-a1-u09-p02' else orig)
PATH.write_text('\n'.join(out)+'\n',encoding='utf-8')
REPORT.write_text(json.dumps({'schema_version':1,'date':'2026-08-23','passage_id':'ur-a1-u09-p02','input_git_blob_sha':EXPECTED,'review_before':before,'review_after':after,'new_target_counts':{t['id']:t['exposures_in_text'] for t in row['new_lexical_targets']},'cloze_question_count':cl,'all_clozes_reconstructed':True,'quality_promotion':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review_before':before,'review_after':after,'word_count':row['word_count'],'clozes':cl},ensure_ascii=False))
