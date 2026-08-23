import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading'/'urdu'/'a1'/'passages.jsonl'
REPORT=ROOT/'reading'/'audit'/'urdu_a1_wave1d_explanation_alignment_2026-08-23.json'
EXPECTED='c2b5ab4b3b763d102ff97d13d87774da8bad227c'

def blob(path):
    return subprocess.check_output(['git','hash-object',str(path)],text=True).strip()

def parts(answer):
    return [x.strip() for x in answer.split('؛')]

def reconstruct(prompt, answer):
    out=prompt
    for p in parts(answer):
        if '_____' not in out: raise AssertionError('too many key parts')
        out=out.replace('_____',p,1)
    if '_____' in out: raise AssertionError('too few key parts')
    return out

if blob(PATH)!=EXPECTED:
    raise SystemExit(f'Refusing Wave 1D: expected {EXPECTED}, found {blob(PATH)}')
raw=PATH.read_text(encoding='utf-8').splitlines()
rows=[json.loads(x) for x in raw if x]
assert len(rows)==60 and [r['sequence'] for r in rows]==list(range(1,61))
by_id={r['id']:r for r in rows}
changes=[]; changed=set()

def fix(row_id, aid, old, new):
    row=by_id[row_id]
    item=next(x for x in row['answer_key'] if x['id']==aid)
    if item['explanation']!=old:
        raise AssertionError(f'{row_id}/{aid} explanation drift: {item["explanation"]!r}')
    item['explanation']=new
    changes.append({'passage_id':row_id,'answer_id':aid,'old_explanation':old,'new_explanation':new})
    changed.add(row_id)

fix('ur-a1-u03-p06','a5','کھانا بنانے کے وقت یہی سوال متن میں ہے۔','متن میں سبزی ابھی پک رہی ہوتی ہے، اس لیے عائشہ انتظار کرتی ہے۔')
fix('ur-a1-u05-p06','a4','متن میں عائشہ کے اندر جانے کے وقت یہی جگہ بتائی گئی ہے۔','متن میں دونوں پہلے کلاس کے اندر جاتی ہیں اور پھر دروازے کے قریب آتی ہیں۔')

for row_id in changed:
    row=by_id[row_id]
    row['revision']=int(row.get('revision',0))+1
    q=row.setdefault('quality',{})
    q['answer_key_check']='pending'; q['pedagogical_review']='pending'; q['schema_check']='pending'; q['status']='draft'
    note='Wave 1D answer-explanation alignment applied 2026-08-23; gate revalidation pending.'
    q.setdefault('notes',[])
    if note not in q['notes']: q['notes'].append(note)

clozes=[]
for row in rows:
    ans_by_q={a['question_id']:a for a in row['answer_key']}
    for q in row['questions']:
        a=ans_by_q.get(q['id'])
        assert a and a['id']==q['answer_id']
        if q.get('type')=='cloze_transfer':
            clozes.append(reconstruct(q['prompt'],a['answer']))
assert len(clozes)==130

out=[]
for original,row in zip(raw,rows):
    out.append(json.dumps(row,ensure_ascii=False,separators=(',',':')) if row['id'] in changed else original)
PATH.write_text('\n'.join(out)+'\n',encoding='utf-8')
REPORT.write_text(json.dumps({
    'schema_version':1,'date':'2026-08-23','language':'urdu','level':'A1',
    'input_git_blob_sha':EXPECTED,'changed_passage_ids':sorted(changed),'changes':changes,
    'cloze_question_count':len(clozes),'all_cloze_structures_reconstructed':True,'quality_promotion':False
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'changed':sorted(changed),'clozes':len(clozes)},ensure_ascii=False))
