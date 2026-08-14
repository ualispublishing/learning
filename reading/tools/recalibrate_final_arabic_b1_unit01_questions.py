#!/usr/bin/env python3
"""Final-review remediation for B1 Unit 01 question composition.

Preserves the strongest comprehension/inference and synthesis questions while
using passage-specific lexical and grammar-in-context slots. Every passage keeps
at least four comprehension/inference questions, gains at least two lexical
questions, at least two grammar/style questions, and at least one synthesis item.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/b1/passages.jsonl'
# passage -> question id -> (type,prompt,target_ids,answer)
UPDATES={
'ar-b1-u01-p01':{
 'q5':('vocabulary_in_context','ماذا يعني «قرار» في هذا النص؟',['ar-r223'],'اختيار يُحسم بعد مقارنة بدائل ومعلومات وآثار محتملة.'),
 'q6':('single_word_definition','ما معنى «أولوية» في سياق جدول نور؟',['ar-r2543'],'شيء يُعطى أهمية أو تقدّمًا على أشياء أخرى في الوقت الحالي.'),
 'q7':('grammar_in_context','ما دلالة «حتى إن» في «حتى إن كانت الإجابة لا الآن»؟',[],'تفيد أن وضوح القرار يظل مهمًا حتى في الحالة التي تكون فيها النتيجة عدم التسجيل الآن.'),
 'q8':('grammar_function','ما وظيفة «إذا» في «إذا كانت الأولوية واضحة، يصبح قول ليس الآن أسهل»؟',[],'تقدم شرطًا ثم تربط به نتيجة مترتبة عليه.'),
},
'ar-b1-u01-p02':{
 'q5':('vocabulary_in_context','ماذا تعني «مسؤولية» عندما يتحدث النص عن دور كل عضو؟',['ar-r774'],'الواجب أو الدور الذي يُتوقع من الشخص أن يؤديه أو يوضح سبب تعذر أدائه.'),
 'q6':('vocabulary_in_context','ماذا تعني «متابعة» في سياق مراقبة الاتفاق الجديد؟',['ar-r957'],'الاستمرار في فحص التقدم والنتائج لمعرفة هل ينجح التعديل.'),
 'q8':('grammar_function','ما وظيفة «قبل» في «قبل تغيير التقسيم، تحدثت المجموعة مع سامر»؟',[],'ترتب الحدثين زمنيًا وتبين أن فهم السبب سبق تعديل المسؤوليات.'),
},
'ar-b1-u01-p03':{
 'q5':('vocabulary_in_context','ماذا تعني «مهارة» في هذا النص؟',['ar-r1481'],'قدرة يمكن إظهارها من خلال فعل أو أداء في موقف حقيقي.'),
 'q6':('vocabulary_in_context','كيف يُفهم معنى «خبرة» في سؤال نور للمعلمة؟',['ar-r1190'],'تجربة أو ممارسة سابقة يتعلم منها الشخص ويستطيع الاستدلال بها على ما فعله.'),
 'q7':('grammar_in_context','ما وظيفة «حتى» في «لا تحتاج دائمًا إلى كتابة أمثلة طويلة حتى تكون واضحة»؟',[],'تربط طول الأمثلة بالغاية المطلوبة، وهي الوضوح، ثم ينفي النص أن الطول شرط دائم لتحقيقها.'),
 'q8':('grammar_function','ما وظيفة «بدل» في «بدل أن يكتب كلمة عامة...» وفي الأمثلة التي بعدها؟',[],'تقدم بديلًا أو صياغة أقوى تحل محل الادعاء العام.'),
},
'ar-b1-u01-p04':{
 'q5':('vocabulary_in_context','ماذا تعني «تجربة» عندما تغير نور طريقة دراستها أسبوعين؟',['ar-r782'],'اختبار محدود لطريقة ما لملاحظة نتيجتها قبل تعميم الحكم.'),
 'q6':('vocabulary_in_context','ماذا تعني «نتيجة» في قول نور إنها تقيس النتيجة؟',['ar-r487'],'ما يظهر بعد تطبيق الطريقة، مثل مقدار ما تتذكره لاحقًا.'),
 'q8':('grammar_function','ما وظيفة «ليست بالضرورة» في قول نور إن الطريقة الأسهل ليست بالضرورة الأفضل للتذكر؟',[],'تمنع تعميم علاقة حتمية بين سهولة الدراسة وجودة التذكر لاحقًا.'),
},
'ar-b1-u01-p05':{
 'q5':('vocabulary_in_context','ماذا يعني «خيار» عند مقارنة هدى الوظيفتين؟',['ar-r1218'],'بديل متاح يمكن اختياره بعد مقارنة فوائده وكلفه.'),
 'q6':('vocabulary_in_context','ماذا يعني «هدف» عندما تتحدث هدى عن الدراسة؟',['ar-r242'],'نتيجة مهمة تريد الوصول إليها وتحاول حماية الوقت اللازم لها.'),
 'q8':('grammar_function','ما وظيفة «إذا» في شرط هدى أن تعيد تقييم القرار بعد شهر؟',[],'تحدد حالة مستقبلية تجعل مراجعة القرار مطلوبة.'),
},
'ar-b1-u01-p06':{
 'q5':('vocabulary_in_context','ماذا تعني «خبرة» في عبارة «إذا ظهرت خبرة جديدة»؟',['ar-r1190'],'معلومة أو تجربة جديدة تكشف أثر القرار وتسمح بإعادة تقييمه.'),
 'q7':('vocabulary_in_context','ماذا يعني «هدف» في مقارنة قرار العمل بالدراسة؟',['ar-r242'],'النتيجة التي يريد الشخص حمايتها أو الوصول إليها عند المفاضلة بين الخيارات.'),
 'q9':('grammar_function','ما وظيفة «إذا» في فكرة مراجعة القرار «إذا ظهرت خبرة جديدة»؟',[],'تجعل ظهور معلومات أو تجربة جديدة شرطًا لإعادة النظر في القرار.'),
},
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];by={r['id']:r for r in rows};changes=[]
for pid,items in UPDATES.items():
 r=by[pid];qmap={q['id']:q for q in r['questions']};amap={a['question_id']:a for a in r['answer_key']}
 for qid,(typ,prompt,tids,answer) in items.items():
  q=qmap[qid];a=amap[qid]
  # Guard that these slots have not already been repurposed by another review.
  assert q.get('type') not in {'vocabulary_in_context','single_word_definition','grammar_function','grammar_in_context'},(pid,qid,q)
  old={'type':q.get('type'),'prompt':q.get('prompt'),'target_ids':q.get('target_ids',[]),'answer':a.get('answer')}
  q['type']=typ;q['prompt']=prompt;q['target_ids']=tids;a['answer']=answer
  changes.append({'passage_id':pid,'question_id':qid,'old':old,'new':{'type':typ,'prompt':prompt,'target_ids':tids,'answer':answer}})
 r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final Pass 03 remediation: recalibrated B1 Unit 01 question composition with passage-specific lexical and grammar-in-context items while preserving comprehension/inference and synthesis coverage.'
 if note not in notes:notes.append(note)
# Independent local mix check mirroring the documented B1 categories.
COMP={'gist','literal_detail','sequence','cause_effect','reference_resolution','main_claim','inference','motive','stance','assumption','ambiguity_resolution','argument_relation'}
LEX={'vocabulary_in_context','single_word_definition','cloze_transfer','register_style'}
GRAM={'grammar_in_context','grammar_category','grammar_choice','grammar_identification','grammar_function','person_form','contrast','register_style'}
SYN={'paraphrase','summary','synthesis','cross_text_synthesis'}
mix={}
for pid in UPDATES:
 types=[q['type'] for q in by[pid]['questions']]
 c={'comprehension_inference':sum(t in COMP for t in types),'lexical':sum(t in LEX for t in types),'grammar_style':sum(t in GRAM for t in types),'synthesis':sum(t in SYN for t in types)}
 assert c['comprehension_inference']>=4 and c['lexical']>=2 and c['grammar_style']>=2 and c['synthesis']>=1,(pid,types,c)
 mix[pid]=c
assert len(changes)==20,len(changes)
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'level':'B1','unit':1,'question_changes':len(changes),'mix':mix},ensure_ascii=False))
