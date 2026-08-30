#!/usr/bin/env python3
"""Apply nine current-corpus Arabic B1-C1 assessment-grounding repairs.

No passage prose, lexical targets, grammar targets, discourse targets, or non-targeted
Q/A are changed. The repair is bound to current Gate-0 pre-repair hashes.
"""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
AUDIT=READING/'audit'/'arabic_b1_c2_metalinguistic_grounding_repair_2026-08-30.json'
PRE={
 'b1':'8f0fdaac2cf8f6941008b32971f328e45ff670bf790e1091e3dab9d773ab9ddc',
 'b2':'5e387ff7eb730358c48fe2329b826d8effc5698079487e71f0f8f064e13b4907',
 'c1':'2a8d71a25a8176a4383488b8d794151eb041e0e60e96b251f1c13e403d14b23e',
}
REPAIRS={
 ('b1','ar-b1-u02-p01','q8'):{
   'old_prompt':'ما وظيفة «مع أن» في بيان أن التقرير احتوى كل الأجزاء مع أنه اعتمد على نسخة غير صحيحة؟','old_type':'grammar_function',
   'new_prompt':'ما وظيفة «لكن» في القول إن لوم سامر كان سهلًا لكن ذلك لم يكن السبب الكامل؟','new_type':'grammar_function',
   'new_answer':'تستدرك على التفسير الظاهر وتفتح الطريق للسبب الأعمق المتعلق بالنسخ وطريقة العمل.'},
 ('b1','ar-b1-u03-p05','q8'):{
   'old_prompt':'ما وظيفة «لا... بل» في وصف رد مريم على التصحيح الذي يغيّر المعنى؟','old_type':'grammar_function',
   'new_prompt':'ما وظيفة «بل» في «لم تكتف برفضه، بل حاولت فهم النمط الذي أدى إليه»؟','new_type':'grammar_function',
   'new_answer':'تنقل من مجرد رفض الاقتراح إلى خطوة أعمق هي فهم سبب ظهور ذلك الاقتراح.'},
 ('b2','ar-b2-u08-p04','q8'):{
   'old_prompt':'ما وظيفة «إذا» الضمنية في تغير أهمية الطريق مع الموسم والغرض؟','old_type':'grammar_function',
   'new_prompt':'كيف تربط عبارة «أهمية الطريق قد تتغير مع الموسم والغرض» بين مركزية الطريق وظروف الاستخدام؟','new_type':'argument_relation',
   'new_answer':'تربط مركزية الطريق بظروف الاستخدام بدل معاملتها كخاصية جغرافية ثابتة في كل وقت.'},
 ('b2','ar-b2-u09-p03','q8'):{
   'old_prompt':'ما وظيفة «إذا» في التحذير من إذن طارئ لم يصل في الوقت المناسب؟','old_type':'grammar_function',
   'new_prompt':'ما وظيفة السؤال عن إذن طارئ لم يصل في الوقت المناسب في نقد الإغلاق الآلي بالقائمة؟','new_type':'argument_relation',
   'new_answer':'يقدم حالة تكشف كلفة الاعتماد على قائمة منع آلية عندما لا تستطيع الإجراءات الإدارية مواكبة الاستثناء المشروع.'},
 ('b2','ar-b2-u09-p06','q8'):{
   'old_prompt':'ما وظيفة «إذا» في سؤال ما الذي سيجعل نور تقترح تعديل القاعدة بدل تعديل التنفيذ؟','old_type':'grammar_function',
   'new_prompt':'ما وظيفة تسجيل ما الذي سيجعل نور تقترح تعديل القاعدة بدل تعديل التنفيذ مسبقًا؟','new_type':'argument_relation',
   'new_answer':'يربط المراجعة بمؤشر محدد ونوع المشكلة، فيقل خطر تغيير المستوى الخطأ من النظام.'},
 ('c1','ar-c1-u01-p05','q8'):{
   'old_prompt':'ما وظيفة «إذا» الضمنية في فكرة أن قيمة الدراسة التالية تعتمد على قدرتها على تقليل عدم اليقين؟','old_type':'grammar_function',
   'new_prompt':'لماذا يربط النص اختيار الدراسة التالية بالجزء الأكثر قدرة على تقليل عدم اليقين؟','new_type':'argument_relation',
   'new_answer':'يجعل اختيار التصميم تابعًا للجزء غير المحسوم من الحجة بدل تكرار أسهل نتيجة مؤيدة وإضافة عدد جديد فقط.'},
 ('c1','ar-c1-u05-p01','q8'):{
   'old_prompt':'ما وظيفة «إذا» في ربط تغير صياغة التقرير بظهور شروط تحد النتيجة؟','old_type':'grammar_function',
   'new_prompt':'كيف يربط النص ظهور شروط جديدة بتعديل نطاق الادعاء في التقرير؟','new_type':'argument_relation',
   'new_answer':'يجعل الدليل الجديد سببًا لتعديل نطاق الادعاء بدل حماية العبارة الأولى بعد اتساع الاختبار.'},
 ('c1','ar-c1-u05-p02','q8'):{
   'old_prompt':'ما وظيفة «إذا» في سؤال ما إذا كان المسار سيبقى بعد موسم تشغيل مختلف؟','old_type':'grammar_function',
   'new_prompt':'ما وظيفة السؤال عن استمرار المسار بعد فترة أو موسم تشغيل مختلف؟','new_type':'argument_relation',
   'new_answer':'يختبر ثبات العلاقة وحدود تعميمها ويمنع تمديد الاتجاه خارج الفترة المدروسة تلقائيًا.'},
 ('c1','ar-c1-u09-p01','q8'):{
   'old_prompt':'ما وظيفة «إذا» الضمنية في سؤال ما الذي كان يمكن أن يحدث قبل معرفة الإغلاق؟','old_type':'grammar_function',
   'new_prompt':'ما وظيفة السؤال عما كان يمكن أن يحدث قبل معرفة الإغلاق؟','new_type':'argument_relation',
   'new_answer':'يفتح بدائل كانت ممكنة وقتها ويقاوم قراءة النتيجة إلى الخلف بوصفها نهاية حتمية لكل ما سبق.'},
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def protected(r):
    x=copy.deepcopy(r); x.pop('questions',None); x.pop('answer_key',None); x.pop('revision',None)
    if isinstance(x.get('quality'),dict): x['quality'].pop('notes',None)
    return x

def main():
    changes=[]; changed_by_level={}
    for level in ('b1','b2','c1'):
        path=READING/'arabic'/level/'passages.jsonl'
        if sha(path)!=PRE[level]: raise SystemExit(f'{level}: pre-repair hash drift')
        raw=path.read_text(encoding='utf-8').splitlines(keepends=True)
        rows=[json.loads(x) for x in raw]
        if len(rows)!=60 or [r['sequence'] for r in rows]!=list(range(1,61)): raise SystemExit(f'{level}: layout drift')
        before={r['id']:protected(r) for r in rows}; changed=set()
        for (lev,rid,qid),spec in REPAIRS.items():
            if lev!=level: continue
            rec=next((r for r in rows if r['id']==rid),None)
            if rec is None: raise SystemExit(f'missing {rid}')
            q=next((q for q in rec['questions'] if q['id']==qid),None)
            a=next((a for a in rec['answer_key'] if a['question_id']==qid),None)
            if q is None or a is None: raise SystemExit(f'missing linkage {rid}/{qid}')
            if q.get('prompt')!=spec['old_prompt'] or q.get('type')!=spec['old_type']: raise SystemExit(f'question drift {rid}/{qid}')
            q['prompt']=spec['new_prompt']; q['type']=spec['new_type']; a['answer']=spec['new_answer']
            changed.add(rid); changes.append({'level':level.upper(),'passage_id':rid,'question_id':qid,'before':{'prompt':spec['old_prompt'],'type':spec['old_type']},'after':{'prompt':spec['new_prompt'],'type':spec['new_type'],'answer':spec['new_answer']}})
        note='2026-08-30 current-corpus metalinguistic grounding review: repaired a question that attributed an absent/implicit connector to the passage; assessment intent preserved with an explicitly grounded construction or discourse relation.'
        for r in rows:
            if r['id'] in changed:
                if protected(r)!=before[r['id']]: raise SystemExit(f'protected content changed {r["id"]}')
                r.setdefault('quality',{}).setdefault('notes',[])
                if note not in r['quality']['notes']: r['quality']['notes'].append(note)
                r['revision']=int(r.get('revision',0))+1
                if protected(r)!=before[r['id']]: raise SystemExit(f'protected content changed after note {r["id"]}')
            if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10: raise SystemExit(f'QA count drift {r["id"]}')
            amap={a['question_id']:a for a in r['answer_key']}
            if any(q['answer_id'] not in {a['id'] for a in r['answer_key']} or amap.get(q['id']) is None for q in r['questions']): raise SystemExit(f'QA linkage drift {r["id"]}')
        out=list(raw)
        for i,r in enumerate(rows):
            if r['id'] in changed: out[i]=json.dumps(r,ensure_ascii=False)+('\n' if raw[i].endswith('\n') else '')
        path.write_text(''.join(out),encoding='utf-8')
        after=path.read_text(encoding='utf-8').splitlines(keepends=True)
        for i,r in enumerate(rows):
            if r['id'] not in changed and after[i]!=raw[i]: raise SystemExit(f'untargeted record changed {r["id"]}')
        changed_by_level[level]={'passages':len(changed),'result_sha256':sha(path)}
    if len(changes)!=9: raise SystemExit(f'expected 9 repairs, got {len(changes)}')
    report={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','levels':['B1','B2','C1'],'date':'2026-08-30','status':'APPLIED_INTERNAL_REVIEW','scope':'Nine hash-bound B1-C1 question/answer grounding repairs from the fresh 2026-08-30 B1-C2 metalinguistic manual queue.','pre_repair_sha256':PRE,'repairs_applied':9,'changed_by_level':changed_by_level,'passage_prose_changed':False,'lexical_targets_changed':False,'untargeted_records_byte_identical':True,'repairs':changes,'retained_false_positive_items':[{'passage_id':'ar-c1-u10-p06','question_id':'q10','reason':'Passage explicitly says: ليس حفظ مفردات أصعب، بل القدرة...; ellipsis shorthand caused detector miss.'},{'passage_id':'ar-c2-u01-p06','question_id':'q10','reason':'Passage explicitly says: لا يكافأ بكثرة الأسماء ولا بغرابة الأمثلة; ellipsis shorthand caused detector miss.'}],'quality_promotion':False,'release_claim':False}
    AUDIT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='repairs'},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
