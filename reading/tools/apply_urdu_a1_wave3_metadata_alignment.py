import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading'/'urdu'/'a1'/'passages.jsonl'
REPORT=ROOT/'reading'/'audit'/'urdu_a1_wave3_metadata_alignment_2026-08-23.json'
EXPECTED='a9dc21f1236830765fa401d8e6bd14ebba004b78'


def blob(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def parts(a): return [x.strip() for x in a.split('؛')]
def recon(p,a):
    out=p
    for x in parts(a):
        if '_____' not in out: raise AssertionError('too many answer parts')
        out=out.replace('_____',x,1)
    if '_____' in out: raise AssertionError('unfilled cloze')
    return out

if blob(PATH)!=EXPECTED: raise SystemExit(f'Refusing Wave 3: expected {EXPECTED}, found {blob(PATH)}')
raw=PATH.read_text(encoding='utf-8').splitlines(); rows=[json.loads(x) for x in raw if x]
assert len(rows)==60 and [r['sequence'] for r in rows]==list(range(1,61))
by={r['id']:r for r in rows}; changed=set(); ops=[]

def target(rid,tid): return next(t for t in by[rid]['new_lexical_targets'] if t['id']==tid)
def Q(rid,qid): return next(q for q in by[rid]['questions'] if q['id']==qid)

def sense(rid,tid,old,new,finding):
    t=target(rid,tid)
    if t.get('intended_sense')!=old: raise AssertionError(f'{rid}/{tid} sense drift: {t.get("intended_sense")!r}')
    t['intended_sense']=new; changed.add(rid)
    ops.append({'passage_id':rid,'kind':'intended_sense','target_id':tid,'finding_id':finding,'before':old,'after':new})

def qtype(rid,qid,old,new,finding):
    q=Q(rid,qid)
    if q.get('type')!=old: raise AssertionError(f'{rid}/{qid} type drift: {q.get("type")!r}')
    q['type']=new; changed.add(rid)
    ops.append({'passage_id':rid,'kind':'question_type','question_id':qid,'finding_id':finding,'before':old,'after':new})

def qprompt(rid,qid,old,new,finding,new_type=None):
    q=Q(rid,qid)
    if q['prompt']!=old: raise AssertionError(f'{rid}/{qid} prompt drift: {q["prompt"]!r}')
    b={'prompt':q['prompt'],'type':q.get('type')}; q['prompt']=new
    if new_type is not None: q['type']=new_type
    changed.add(rid); ops.append({'passage_id':rid,'kind':'question_alignment','question_id':qid,'finding_id':finding,'before':b,'after':{'prompt':q['prompt'],'type':q.get('type')}})

sense('ur-a1-u01-p03','ur-rank-0048','many, much; enough, sufficient','many; much; a lot (sense taught in this passage)','U1P03-01')
sense('ur-a1-u01-p04','ur-rank-0058','if; agarwood','if (conditional conjunction)','U1P04-04')
sense('ur-a1-u02-p04','ur-rank-0128','during; duration; course/period','during; in the course of (sense taught here)','U2P04-01')
sense('ur-a1-u03-p04','ur-rank-0247','now; at present','now; right now; still (senses used in this passage)','U3P04-01')

qtype('ur-a1-u02-p05','q8','cause_effect','conditional_comprehension','U2P05-01')
qtype('ur-a1-u02-p06','q5','cause_effect','sequence','U2P06-02')
qtype('ur-a1-u04-p04','q5','cause_effect','literal_detail','U4P04-02')
qprompt('ur-a1-u02-p06','q3','مریم کو گھڑی یا الارم کے بارے میں مسئلہ ہو تو عائشہ کیا کرتی ہے؟','مریم کو گھڑی یا الارم استعمال کرنے میں مدد چاہیے ہو تو عائشہ کیا کرتی ہے؟','U2P06-01','conditional_comprehension')

# Reconcile contradictory legacy Unit 1 quality metadata by demotion only.
legacy_changes=[]
for row in rows:
    if row.get('unit')!=1: continue
    qual=row.setdefault('quality',{})
    before={k:qual.get(k) for k in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check','status')}
    for k in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check'): qual[k]='pending'
    qual['status']='draft'
    note='Legacy Unit 1 pass/calibrated metadata superseded by the 2026-08-23 full A1 audit; all gates remain pending until current revalidation.'
    if note not in qual.setdefault('notes',[]): qual['notes'].append(note)
    after={k:qual.get(k) for k in before}
    if before!=after:
        changed.add(row['id']); legacy_changes.append({'passage_id':row['id'],'before':before,'after':after})

for rid in changed:
    row=by[rid]; row['revision']=int(row.get('revision',0))+1
    # metadata edits never promote content gates
    qual=row.setdefault('quality',{}); qual['status']='draft'
    if rid not in [x['passage_id'] for x in legacy_changes]:
        qual['schema_check']='pending'; qual['pedagogical_review']='pending'
        note='Wave 3 metadata alignment applied 2026-08-23; gate revalidation pending.'
        if note not in qual.setdefault('notes',[]): qual['notes'].append(note)

cl=0; type_counts=Counter()
for row in rows:
    ans={a['question_id']:a for a in row['answer_key']}
    for q in row['questions']:
        a=ans.get(q['id']); assert a and a['id']==q['answer_id']
        type_counts[q.get('type','')]+=1
        if q.get('type')=='cloze_transfer': recon(q['prompt'],a['answer']); cl+=1
assert cl==130
remaining_grammar={k:v for k,v in type_counts.items() if k in {'grammar_function','grammar_category'}}
if remaining_grammar: raise AssertionError(f'Remaining explicit grammar-label question types: {remaining_grammar}')

out=[]
for orig,row in zip(raw,rows): out.append(json.dumps(row,ensure_ascii=False,separators=(',',':')) if row['id'] in changed else orig)
PATH.write_text('\n'.join(out)+'\n',encoding='utf-8')
REPORT.write_text(json.dumps({'schema_version':1,'date':'2026-08-23','language':'urdu','level':'A1','input_git_blob_sha':EXPECTED,'changed_passage_ids':sorted(changed),'operations':ops,'legacy_unit1_quality_demotions':legacy_changes,'question_type_counts':dict(type_counts),'remaining_explicit_grammar_label_types':remaining_grammar,'cloze_question_count':cl,'all_clozes_reconstructed':True,'quality_promotion':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'changed':sorted(changed),'legacy_demotions':len(legacy_changes),'question_types':dict(type_counts),'clozes':cl},ensure_ascii=False))
