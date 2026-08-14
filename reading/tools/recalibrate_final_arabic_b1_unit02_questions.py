#!/usr/bin/env python3
"""Final-review remediation for B1 Unit 02 question composition.

Each passage retains at least four comprehension/inference items plus its
existing contrast and summary/synthesis structure, while adding two lexical
items and one grammar-in-context/function item tied to the actual passage.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/b1/passages.jsonl'
UPDATES={
'ar-b1-u02-p01':{
 'q5':('vocabulary_in_context','ماذا يعني «سبب» عندما يسأل الفريق لماذا ظهرت المشكلة؟',['ar-r292'],'العامل أو التفسير الذي أدى إلى حدوث المشكلة، لا الشخص الذي لاحظها فقط.'),
 'q6':('vocabulary_in_context','ماذا تعني «نسخة» في سياق ملفات التقرير؟',['ar-r2626'],'إصدار محدد من الملف يمكن تمييزه عن الإصدارات الأخرى.'),
 'q8':('grammar_function','ما وظيفة «مع أن» في بيان أن التقرير احتوى كل الأجزاء مع أنه اعتمد على نسخة غير صحيحة؟',[],'تقدم مفارقة أو تنازلًا: وجود الأجزاء لا يمنع أن النسخة المختارة كانت خاطئة.'),
},
'ar-b1-u02-p02':{
 'q5':('vocabulary_in_context','ماذا يعني «حل» في هذا النص؟',['ar-r867'],'إجراء يُتخذ لتقليل مشكلة، ثم يُختبر لأن آثاره قد تحتاج إلى تعديل.'),
 'q6':('vocabulary_in_context','ماذا يعني «تأثير» عند مقارنة نتائج فتح الباب الثاني؟',['ar-r702'],'الأثر أو النتيجة التي أحدثها التغيير في الطلاب أو السيارات أو أماكن الانتظار.'),
 'q8':('grammar_function','ما وظيفة «إذا» في فكرة أن جمع المعلومات يسمح باختيار تعديل أدق؟',[],'تربط تحقق شرط، وهو جمع معلومات كافية، بالقدرة على اتخاذ تعديل أدق.'),
},
'ar-b1-u02-p03':{
 'q4':('vocabulary_in_context','ماذا يعني «خطأ» في عنوان النص؟',['ar-r515'],'مشكلة أو نتيجة غير صحيحة قد تأتي من صياغة الرسالة أو من تفسير مرجعها.'),
 'q5':('vocabulary_in_context','ماذا تعني «رسالة» في تجربة هدى للصيغ الثلاث؟',['ar-r544'],'معلومة مكتوبة تُرسل إلى شخص آخر ويجب أن يكون مرجعها واضحًا له.'),
 'q7':('grammar_function','ما وظيفة «لكن» في قول النص إن العبارتين صحيحتان لغويًا لكن مرجعهما مختلف؟',[],'توضح تعارضًا بين صحة الصياغة اللغوية وعدم كفاية المرجع المشترك لفهمها.'),
},
'ar-b1-u02-p04':{
 'q5':('vocabulary_in_context','ماذا يعني «موقف» عندما يتغير موقف مريم بعد معرفة طريقة الاختيار؟',['ar-r474'],'رأي أو اتجاه يتخذه الشخص تجاه قرار أو حدث ويمكن أن يتغير مع معلومات جديدة.'),
 'q6':('vocabulary_in_context','ماذا تعني «مشاركة» عندما تبحث مريم عن دور آخر؟',['ar-r304'],'الإسهام في النشاط أو المشروع بطريقة عملية حتى إن تغير الدور الأول.'),
 'q8':('grammar_function','ما وظيفة «لو» في الفكرة التي تتخيل اعتراض مريم قبل أن تسأل عن السبب؟',[],'تبني حالة افتراضية مخالفة لما حدث لتوضيح نتيجة ممكنة لو تصرفت مريم مبكرًا.'),
},
'ar-b1-u02-p05':{
 'q4':('vocabulary_in_context','ماذا يعني «تغيير» عندما ينتقل النشاط من الخارج إلى الداخل؟',['ar-r567'],'تعديل في الخطة أو التصميم استجابةً لظرف جديد.'),
 'q5':('vocabulary_in_context','ماذا يعني «مناسب» عند اختيار بديل للفعالية؟',['ar-r836'],'ملائم للظروف والقيود الجديدة، مثل المساحة وعدد الزوار.'),
 'q7':('grammar_function','ما وظيفة «بدل» في انتقال النص من النقل المباشر إلى إعادة تصميم البرنامج؟',[],'تقدم خيارًا بديلًا يحل محل الخطة التي لا تناسب المكان الجديد.'),
},
'ar-b1-u02-p06':{
 'q3':('vocabulary_in_context','ماذا تعني «رسالة» في مشكلة الفهم المشترك؟',['ar-r544'],'معلومة منقولة إلى شخص آخر وقد تحتاج إلى مرجع يمكن للطرفين التحقق منه.'),
 'q4':('vocabulary_in_context','ماذا يعني «مناسب» عندما يبحث النص عن بديل يلائم ظرفًا جديدًا؟',['ar-r836'],'ملائم للقيود والهدف بعد تغير الظروف.'),
 'q7':('grammar_function','ما وظيفة «إذا» المتكررة في الفقرة الأخيرة التي تميز أنواع المشكلات؟',[],'تقدم شروطًا مختلفة، ويقترن كل شرط بنوع فحص أو استجابة يناسبه.'),
},
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];by={r['id']:r for r in rows};changes=[]
for pid,items in UPDATES.items():
 r=by[pid];qmap={q['id']:q for q in r['questions']};amap={a['question_id']:a for a in r['answer_key']}
 for qid,(typ,prompt,tids,answer) in items.items():
  q=qmap[qid];a=amap[qid]
  assert q.get('type') not in {'vocabulary_in_context','single_word_definition','grammar_function','grammar_in_context'},(pid,qid,q)
  old={'type':q.get('type'),'prompt':q.get('prompt'),'target_ids':q.get('target_ids',[]),'answer':a.get('answer')}
  q['type']=typ;q['prompt']=prompt;q['target_ids']=tids;a['answer']=answer
  changes.append({'passage_id':pid,'question_id':qid,'old':old,'new':{'type':typ,'prompt':prompt,'target_ids':tids,'answer':answer}})
 r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final Pass 03 remediation: recalibrated B1 Unit 02 question composition with passage-specific lexical and grammar-in-context items while preserving comprehension/inference and synthesis coverage.'
 if note not in notes:notes.append(note)
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
assert len(changes)==18,len(changes)
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'level':'B1','unit':2,'question_changes':len(changes),'mix':mix},ensure_ascii=False))
