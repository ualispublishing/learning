#!/usr/bin/env python3
"""Final-review remediation for Arabic B1 Unit 03.

Atomically expands all six passages into the 220-350 planning band and repairs
question composition. Nothing is written unless every passage satisfies the B1
length, zero-new P6, and question-mix guards.
"""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/b1/passages.jsonl'
ADD={
'ar-b1-u03-p01':"""قبل أن تختار سلمى الجدول الجديد، حسبت وقت الانتقال بين الجامعة والعمل والبيت، لا عدد الساعات المكتوبة فقط. اكتشفت أن وردية تبدو قصيرة قد تستهلك جزءًا كبيرًا من المساء إذا أضيف إليها الطريق. لذلك طلبت من المشرف أن يجرب معها جدولًا ثابتًا مدة أسبوعين، ووعدت أن تخبره مبكرًا إذا اقترب موعد تسليم جامعي صعب. كما كتبت لنفسها حدًا أدنى للنوم لا تريد تجاوزه. بهذه الطريقة لم يعد تنظيم الوقت مجرد محاولة لوضع كل واجب في فراغ صغير، بل أصبح قرارًا حول أي التزامات ثابتة وأيها يمكن التفاوض بشأنه قبل أن يتحول الضغط إلى تأخير دائم.""",
'ar-b1-u03-p02':"""ولكي لا يبقى النقاش قائمًا على الانطباع، اقترحت اللجنة جمع معلومات بسيطة قبل الاجتماع التالي. سيعدّ أحد الأعضاء عدد الحافلات في ساعة الذروة، ويسأل آخر بعض أصحاب المتاجر عن أثر التغيير في الزوار، بينما تسجل مجموعة ثالثة آراء السكان في الشارعين. اتفقوا أيضًا على فصل ما يصفه الشخص بنفسه عما سمعه من غيره. عندما عادت البيانات، لم يختف الخلاف، لكنه أصبح أدق: بعض المخاوف كانت مرتبطة فعلًا بالازدحام، وبعضها كان توقعًا لم يحدث بعد. وهكذا صار الرأي بداية لسؤال يمكن فحصه، لا نهاية للنقاش.""",
'ar-b1-u03-p03':"""بعد ذلك كتبت نور قاعدة صغيرة لمجموعتها: الخبر الذي يغير قرارًا يحتاج إلى طريق يمكن تتبعه إلى مصدر. إذا وصلت صورة شاشة، يسألون من نشر الأصل ومتى. وإذا كانت الجملة منسوبة إلى إدارة أو معلم، يبحثون عن إعلان يمكن للجميع فتحه. جرّبوا القاعدة على رسالتين أخريين؛ كانت إحداهما صحيحة لكن قديمة، وكانت الثانية حديثة لكنها رأي لطالب لا إعلانًا رسميًا. ساعدهم ذلك على فهم أن التحقق ليس سؤالًا واحدًا من نوع «هل هذه الجملة تبدو معقولة؟»، بل مقارنة بين المصدر والوقت وما يدعيه النص فعلًا.""",
'ar-b1-u03-p04':"""في القاعة التالية لاحظت نور أن بعض الزوار يقرؤون التاريخ ثم ينتقلون بسرعة، بينما يقف آخرون عند تفسير سبب أهمية القطعة. سألت المرشدة كيف تختار المتحف ما يضعه على البطاقة. قالت إن المساحة محدودة، لذلك يختار الفريق معلومة تساعد الزائر على فهم القطعة من دون تحويل البطاقة إلى فصل طويل. إذا كان التاريخ مهمًا لتسلسل الأحداث يوضع بوضوح، وإذا كان مصدر القطعة أو أثرها أهم فقد يأخذ مساحة أكبر. أدركت نور أن التفاصيل ليست متساوية القيمة في كل سياق؛ المعلومة الجيدة هي التي تخدم سؤال القارئ والغرض من العرض.""",
'ar-b1-u03-p05':"""في اليوم التالي اتصلت مريم بالخدمة مرة أخرى لتتأكد من أن الحل لم يكن مؤقتًا فقط. كان الموظف الجديد يستطيع رؤية الملاحظة التي سجلها زميله، فشرح لها أين وصلت المعاملة وما الخطوة التالية. سألت مريم ماذا تفعل إذا عاد الخطأ، فأعطاها رقم متابعة وحدد المدة التي يجب أن تنتظرها قبل الاتصال. أعجبها أن النظام لم يعتمد على ذاكرة موظف واحد. فهمت أن الخدمة الجيدة لا تعني أن الخطأ لن يحدث أبدًا، بل أن توجد مسؤولية واضحة وطريقة يعرف بها العميل كيف يتابع المشكلة ومتى يطلب تغييرًا إضافيًا.""",
'ar-b1-u03-p06':"""تجمع هذه المواقف مهارة واحدة: تحويل المعلومة إلى قرار قابل للمراجعة. في الوقت والعمل نحدد الواجب والحدود قبل أن تتراكم المهام. وفي الحي نفرق بين رأي صاحبه وبين معلومة يمكن فحصها. وفي الرسائل نسأل عن المصدر والزمن قبل نشر الخبر. وفي المتحف نبحث عن وظيفة كل تفصيل داخل سياقه، لا عن أكبر عدد ممكن من الحقائق. وفي الخدمة نتابع هل عالج الحل سبب المشكلة أم أخفاها مؤقتًا. عندما تتغير الأدلة يمكن أن يتغير الموقف أو الحل، لكن المهم أن يبقى سبب التغيير واضحًا لمن يراجعه لاحقًا.""",
}
UPDATES={
'ar-b1-u03-p01':{
'q5':('vocabulary_in_context','ماذا يعني «واجب» في سياق دراسة سلمى وعملها؟',['ar-r750'],'مهمة أو التزام يجب على الشخص إنجازه في وقت محدد.'),
'q6':('vocabulary_in_context','ماذا تعني «مسؤولية» عندما تتحدث سلمى مع المشرف عن الجدول؟',['ar-r774'],'التزام واضح تجاه عمل أو مهمة يجب أداؤها أو التنبيه مبكرًا إذا تعذر أداؤها.'),
'q8':('grammar_function','ما وظيفة «إذا» في فكرة إخبار المشرف مبكرًا إذا اقترب موعد تسليم صعب؟',[],'تحدد حالة مستقبلية تجعل الإخبار المبكر مطلوبًا.'),},
'ar-b1-u03-p02':{
'q5':('vocabulary_in_context','ماذا يعني «رأي» في نقاش سكان الحي؟',['ar-r359'],'تقدير أو موقف يعبّر عنه شخص وقد يحتاج إلى دليل قبل أن يعامل كحقيقة.'),
'q6':('vocabulary_in_context','ماذا يعني «تأثير» عند بحث أثر تغيير الطريق؟',['ar-r702'],'النتيجة التي يحدثها التغيير في السكان أو المتاجر أو حركة المرور.'),
'q8':('grammar_function','ما وظيفة «بينما» في مقارنة مهام مجموعات جمع المعلومات؟',[],'تربط أفعالًا تحدث في الفترة نفسها وتوضح اختلاف دور كل مجموعة.'),},
'ar-b1-u03-p03':{
'q5':('vocabulary_in_context','ماذا يعني «خبر» في هذا النص؟',['ar-r383'],'معلومة تُنقل عن حدث أو قرار ويجب فحص مصدرها وزمنها قبل الاعتماد عليها.'),
'q6':('vocabulary_in_context','ماذا يعني «مصدر» عند التحقق من الرسالة؟',['ar-r1613'],'الجهة أو النص الأصلي الذي يمكن الرجوع إليه لمعرفة من أين جاءت المعلومة.'),
'q8':('grammar_function','ما وظيفة «إذا» المتكررة في قاعدة التحقق التي كتبتها نور؟',[],'تقسم حالات مختلفة من الرسائل وتربط كل حالة بخطوة تحقق مناسبة.'),},
'ar-b1-u03-p04':{
'q4':('vocabulary_in_context','ماذا يعني «تاريخ» على بطاقة المتحف؟',['ar-r647'],'وقت أو سنة مرتبطة بالقطعة تساعد على وضعها في تسلسل الأحداث.'),
'q5':('vocabulary_in_context','ماذا تعني «معلومة» في سياق البطاقة؟',['ar-r427'],'تفصيل يختاره المتحف لمساعدة القارئ على فهم القطعة أو أهميتها.'),
'q7':('grammar_function','ما وظيفة «إذا» في شرح المرشدة لاختيار محتوى البطاقة؟',[],'توضح أن نوع المعلومة المختارة يتغير بحسب ما يحتاجه السياق أو الغرض.'),},
'ar-b1-u03-p05':{
'q4':('vocabulary_in_context','ماذا تعني «خدمة» في هذا النص؟',['ar-r432'],'العملية التي تساعد العميل على حل مشكلة ومتابعة ما سيحدث بعدها.'),
'q5':('vocabulary_in_context','ماذا تعني «مسؤولية» عندما يناقش النص متابعة الخطأ؟',['ar-r774'],'تحديد من يتولى الخطوة التالية وكيف يعرف العميل أين وصلت المشكلة.'),
'q7':('grammar_function','ما وظيفة «إذا» في سؤال مريم عما تفعله إذا عاد الخطأ؟',[],'تقدم احتمالًا مستقبليًا وتطلب الإجراء المناسب عند تحققه.'),},
'ar-b1-u03-p06':{
'q3':('vocabulary_in_context','ماذا تعني «رسالة» في فقرة التحقق من الأخبار؟',['ar-r544'],'معلومة منقولة تحتاج إلى مصدر وزمن واضحين قبل نشرها.'),
'q4':('vocabulary_in_context','ماذا يعني «سبب» عندما يسأل النص هل عالج الحل سبب المشكلة؟',['ar-r292'],'العامل الذي أدى إلى المشكلة ويجب فهمه حتى لا يكون العلاج مؤقتًا فقط.'),
'q7':('grammar_function','ما وظيفة «عندما» في «عندما تتغير الأدلة يمكن أن يتغير الموقف أو الحل»؟',[],'تربط تغير الأدلة بإمكان مراجعة الحكم أو الحل في الوقت الذي يحدث فيه ذلك التغير.'),},
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];by={r['id']:r for r in rows};lengths=[];changes=[]
for pid,addition in ADD.items():
 r=by[pid];assert addition.strip() not in r['text'];old=len(r['text'].split());r['text']=r['text'].rstrip()+' '+addition.strip();new=len(r['text'].split());assert 220<=new<=350,(pid,old,new)
 if pid.endswith('-p06'):assert not r.get('new_lexical_targets'),(pid,r.get('new_lexical_targets'))
 r['word_count']=new;r['sentence_count']=len([s for s in re.split(r'(?<=[.!؟])\s+',r['text']) if s.strip()]);lengths.append({'passage_id':pid,'old':old,'new':new})
for pid,items in UPDATES.items():
 r=by[pid];qmap={q['id']:q for q in r['questions']};amap={a['question_id']:a for a in r['answer_key']}
 for qid,(typ,prompt,tids,answer) in items.items():
  q=qmap[qid];a=amap[qid];assert q.get('type') not in {'vocabulary_in_context','single_word_definition','grammar_function','grammar_in_context'},(pid,qid,q)
  changes.append({'passage_id':pid,'question_id':qid,'old_type':q.get('type'),'new_type':typ});q['type']=typ;q['prompt']=prompt;q['target_ids']=tids;a['answer']=answer
 r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final Pass 03/07 remediation: expanded B1 Unit 03 discourse and recalibrated passage-specific lexical/grammar assessment while preserving comprehension/inference and synthesis coverage.'
 if note not in notes:notes.append(note)
COMP={'gist','literal_detail','sequence','cause_effect','reference_resolution','main_claim','inference','motive','stance','assumption','ambiguity_resolution','argument_relation'};LEX={'vocabulary_in_context','single_word_definition','cloze_transfer','register_style'};GRAM={'grammar_in_context','grammar_category','grammar_choice','grammar_identification','grammar_function','person_form','contrast','register_style'};SYN={'paraphrase','summary','synthesis','cross_text_synthesis'}
mix={}
for pid in UPDATES:
 types=[q['type'] for q in by[pid]['questions']];c={'comprehension_inference':sum(t in COMP for t in types),'lexical':sum(t in LEX for t in types),'grammar_style':sum(t in GRAM for t in types),'synthesis':sum(t in SYN for t in types)};assert c['comprehension_inference']>=4 and c['lexical']>=2 and c['grammar_style']>=2 and c['synthesis']>=1,(pid,types,c);mix[pid]=c
assert len(changes)==18
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'level':'B1','unit':3,'lengths':lengths,'question_changes':len(changes),'mix':mix},ensure_ascii=False))
