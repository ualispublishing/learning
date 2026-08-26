#!/usr/bin/env python3
import json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILES={
 'b1':ROOT/'reading/arabic/b1/passages.jsonl',
 'b2':ROOT/'reading/arabic/b2/passages.jsonl',
 'c1':ROOT/'reading/arabic/c1/passages.jsonl',
 'c2':ROOT/'reading/arabic/c2/passages.jsonl',
}
EXPECTED={
 'b1':'16a07aca4bcf7c9148969a466e1b68da3a60ae62',
 'b2':'a9486b2c38dc53661143e734c9797cd26fa1f742',
 'c1':'3f68da825c50c3018f9e054cbeec27ba01b17be0',
 'c2':'b8e78e2a8dce942e87ef627a8436f1c8571f9d43',
}
OUT=ROOT/'reading/audit/arabic_b1_c2_semantic_remainder_repairs_2026-08-23.json'

def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(p,rows):p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
def getqa(r,qid):
 q=next(x for x in r['questions'] if x.get('id')==qid);a=next(x for x in r['answer_key'] if x.get('question_id')==qid);return q,a

def apply(rows,level,pid,qid,old_prompt,new_prompt,new_type=None,old_answer=None,new_answer=None):
 r=next(x for x in rows[level] if x.get('id')==pid);q,a=getqa(r,qid)
 if q.get('prompt')!=old_prompt:raise RuntimeError(f'{pid} {qid} prompt drift: {q.get("prompt")!r}')
 before={'prompt':q.get('prompt'),'type':q.get('type'),'answer':a.get('answer')}
 q['prompt']=new_prompt
 if new_type:q['type']=new_type
 if old_answer is not None:
  if a.get('answer')!=old_answer:raise RuntimeError(f'{pid} {qid} answer drift: {a.get("answer")!r}')
  a['answer']=new_answer
 r['revision']=int(r.get('revision') or 0)+1
 qm=r.setdefault('quality',{});qm['status']='draft'
 for gate in ('answer_key_check','coverage_check','linguistic_review','pedagogical_review','schema_check'):qm[gate]='pending'
 notes=qm.setdefault('notes',[]);note='Advanced Arabic semantic remainder adjudicated 2026-08-23: assessment wording grounded in the exact passage language; final validation pending.'
 if note not in notes:notes.append(note)
 return {'level':level,'passage_id':pid,'question_id':qid,'before':before,'after':{'prompt':q['prompt'],'type':q['type'],'answer':a.get('answer')}}

def main():
 actual={k:blob(v) for k,v in FILES.items()}
 if actual!=EXPECTED:raise SystemExit(f'Unexpected input blobs: {actual}')
 rows={k:load(v) for k,v in FILES.items()};repairs=[]
 repairs.append(apply(rows,'b1','ar-b1-u02-p01','q8',
  'ما وظيفة «مع أن» في بيان أن التقرير احتوى كل الأجزاء مع أنه اعتمد على نسخة غير صحيحة؟',
  'ما وظيفة «لكن» في «كان من السهل لوم سامر... لكن هذا لم يكن السبب الكامل»؟',
  'grammar_function',
  'تقدم مفارقة أو تنازلًا: وجود الأجزاء لا يمنع أن النسخة المختارة كانت خاطئة.',
  'تحد من التفسير الظاهر للمشكلة وتفتح الانتقال إلى السبب الجذري في طريقة إدارة النسخ.'))
 repairs.append(apply(rows,'b1','ar-b1-u03-p05','q8',
  'ما وظيفة «لا... بل» في وصف رد مريم على التصحيح الذي يغيّر المعنى؟',
  'ما وظيفة «لم تكتف... بل...» في وصف رد مريم على التصحيح الذي يغيّر المعنى؟'))
 repairs.append(apply(rows,'b2','ar-b2-u08-p04','q8',
  'ما وظيفة «إذا» الضمنية في تغير أهمية الطريق مع الموسم والغرض؟',
  'كيف يربط النص تغير أهمية الطريق بالموسم والغرض؟','argument_relation'))
 repairs.append(apply(rows,'b2','ar-b2-u09-p03','q8',
  'ما وظيفة «إذا» في التحذير من إذن طارئ لم يصل في الوقت المناسب؟',
  'ما وظيفة سؤال من سيحدّث القائمة وكيف سيعالج إذنًا طارئًا لم يصل في الوقت المناسب؟','argument_relation'))
 repairs.append(apply(rows,'b2','ar-b2-u09-p06','q8',
  'ما وظيفة «إذا» في سؤال ما الذي سيجعل نور تقترح تعديل القاعدة بدل تعديل التنفيذ؟',
  'ما وظيفة تسجيل ما الذي سيجعل نور تقترح تعديل القاعدة بدل تعديل التنفيذ؟','argument_relation'))
 repairs.append(apply(rows,'c1','ar-c1-u01-p05','q8',
  'ما وظيفة «إذا» الضمنية في فكرة أن قيمة الدراسة التالية تعتمد على قدرتها على تقليل عدم اليقين؟',
  'كيف يربط النص قيمة الدراسة التالية بقدرتها على تقليل عدم اليقين؟','argument_relation'))
 repairs.append(apply(rows,'c1','ar-c1-u05-p01','q8',
  'ما وظيفة «إذا» في ربط تغير صياغة التقرير بظهور شروط تحد النتيجة؟',
  'كيف يربط النص تغير صياغة التقرير بظهور شروط تحد النتيجة؟','argument_relation'))
 repairs.append(apply(rows,'c1','ar-c1-u05-p02','q8',
  'ما وظيفة «إذا» في سؤال ما إذا كان المسار سيبقى بعد موسم تشغيل مختلف؟',
  'ما وظيفة مراجعة النتيجة بعد موسم تشغيل مختلف؟','argument_relation'))
 for level,path in FILES.items():dump(path,rows[level])
 outblobs={k:blob(v) for k,v in FILES.items()}
 report={'schema_version':1,'date':'2026-08-23','scope':'Arabic B1-C2 10-case semantic remainder adjudication','input_blobs':actual,'output_blobs':outblobs,'manual_remainder_count':10,'repair_count':len(repairs),'confirmed_valid':[{'passage_id':'ar-c1-u10-p06','question_id':'q10','evidence':'The source explicitly contains ليس ... بل in the readiness sentence.'},{'passage_id':'ar-c2-u01-p06','question_id':'q10','evidence':'The source explicitly contains لا ... ولا ... in the final analytical-value sentence.'}],'repairs':repairs,'quality_promotion':False}
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':len(repairs),'output_blobs':outblobs},ensure_ascii=False))
if __name__=='__main__':main()
