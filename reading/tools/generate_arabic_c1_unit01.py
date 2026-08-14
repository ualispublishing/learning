#!/usr/bin/env python3
"""Generate Arabic C1 Unit 01: research and evidence.

All scenarios/data are fictional and method-focused. This is generation-stage
content; formal linguistic, pedagogical, lexical, factual, and adversarial audit
passes remain deferred under the generation-first policy.
"""
from __future__ import annotations
import json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reading/arabic/c1/passages.jsonl'
LEX=ROOT/'reading/lexicons/arabic.jsonl'
AR_DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')

def norm(s): return AR_DIAC.sub('',unicodedata.normalize('NFC',str(s or '')).replace('ـ','').strip())
def lexicon():
    d={}
    for line in LEX.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r=json.loads(line); d.setdefault(norm(r.get('form','')),r)
    return d

def lexrow(form,d):
    r=d.get(norm(form))
    if not r: raise KeyError(f'cleared lexicon form missing: {form}')
    return r

SENSE={
'مقياس':'measure; measurement standard','بروتوكول':'protocol; predefined research procedure',
'إحصائي':'statistical','حسبما':'according to; as indicated by','خفي':'hidden; not directly observed',
'منطقي':'logical; consistent with the stated reasoning','تكرار':'repetition; recurrence',
'منتظم':'regular; following a stable pattern','إجماع':'consensus; broad agreement',
'ثغرة':'gap; missing element in an argument or design'
}

def target(form,text,d):
    r=lexrow(form,d)
    return {'id':f"ar-r{r['rank']}",'form':form,'lemma':form,'part_of_speech':r.get('part_of_speech_source'),
            'intended_sense':SENSE[form],'register':'academic/contemporary standard','variety':'MSA',
            'context_strategy':['research_method','evidence_qualification','inference_chain'],
            'first_introduced':True,'exposures_in_text':max(1,text.count(form)),
            'source_lexicon':r.get('source_file'),'source_rank':r['rank'],'beyond_base':False}

def review(form,stage,representation,d):
    r=lexrow(form,d); return {'id':f"ar-r{r['rank']}",'form':form,'review_stage':stage,'representation':representation}

def qa(items,target_ids):
    qs=[]; ans=[]
    for i,(typ,prompt,answer,form) in enumerate(items,1):
        q={'id':f'q{i}','type':typ,'prompt':prompt,'answer_id':f'a{i}'}
        if form: q['target_ids']=[target_ids[form]]
        qs.append(q); ans.append({'id':f'a{i}','question_id':f'q{i}','answer':answer,'explanation':''})
    if len(qs)!=10: raise ValueError('exactly ten questions required')
    return qs,ans

R=[
{
'id':'ar-c1-u01-p01','sequence':1,'title':'حين يصبح الرقم بديلًا عن الظاهرة','passage_type':'instructional','genre':'methods explanation','domains':['research','education','methods'],'topics':['measurement','construct validity','operationalization'],
'text':'في دراسة خيالية أراد فريق مقارنة «جودة التعلّم» بين مجموعتين من الطلبة. بدا السؤال بسيطًا حتى طلبت الباحثة سلمى تعريف ما ستقيسه بالفعل. اقترح أحد الزملاء استخدام عدد الدقائق التي يقضيها الطالب داخل منصة رقمية بوصفه مقياسًا مباشرًا للجودة. اعترضت سلمى: الزمن قابل للعد، لكنه قد يمثل القراءة المتأنية أو التشتت أو مجرد ترك الصفحة مفتوحة. لذلك صمم الفريق بروتوكولًا يسبق جمع البيانات: يحدد السؤال، ويشرح لماذا اختير كل مقياس، وما الظاهرة التي يفترض أن يمثلها، وما الحالات التي قد ينفصل فيها الرقم عن المفهوم. أضافوا ثلاثة مؤشرات بدل مؤشر واحد: أداءً في مهمة جديدة، وشرحًا كتابيًا لطريقة الحل، ووقتًا تقريبيًا للعمل. لم يعاملوا المؤشرات الثلاثة كأنها نسخ من الشيء نفسه؛ فقد يتحسن الأداء من دون أن يصبح الشرح أوضح، وقد يطول الوقت لأن المهمة أصعب لا لأن التعلم أعمق. في نهاية المرحلة التجريبية اكتشفوا أن زمن المنصة يرتفع عند بعض الطلبة الذين يواجهون صعوبة، بينما يتحسن أداء آخرين في وقت أقصر. لم يجعل ذلك الزمن عديم الفائدة، لكنه أسقط الادعاء بأنه مقياس كاف للجودة وحده. كتبت سلمى في التقرير أن القياس ليس خطوة محايدة تقع بعد صياغة السؤال، بل قرار نظري يربط مفهومًا مجردًا بملاحظة قابلة للتسجيل. وإذا كان هذا الربط ضعيفًا، فقد تصبح الحسابات دقيقة جدًا حول شيء لا يجيب عن السؤال الأصلي.',
'target_forms':['مقياس','بروتوكول'],'reviews':[],
'grammar':[{'id':'ar-c1-qualification-measurement','role':'new','description':'تمييز ما يمكن قياسه مباشرة عما يفترض المؤشر أنه يمثله'}],
'discourse':[{'id':'c1-construct-vs-measure','role':'new','description':'separate a construct from its operational measure and identify failure cases in the mapping'}],
'qa':[('gist','ما المشكلة المركزية في الدراسة؟','إمكان الخلط بين رقم سهل القياس ومفهوم أوسع لا يمثله ذلك الرقم بصورة كاملة.',None),('literal_detail','ما المؤشرات الثلاثة التي استخدمها الفريق؟','الأداء في مهمة جديدة، والشرح الكتابي لطريقة الحل، والوقت التقريبي للعمل.',None),('inference','لماذا لا يؤدي ارتفاع زمن المنصة بالضرورة إلى استنتاج إيجابي؟','لأنه قد يعكس صعوبة أو تشتتًا أو سلوكًا لا يدل على تعلم أعمق.',None),('argument_relation','ما وظيفة الحالات التي قد ينفصل فيها الرقم عن المفهوم؟','تختبر حدود صلاحية المؤشر بدل افتراض أن العلاقة ثابتة في كل حالة.',None),('main_claim','كيف يصف النص عملية القياس؟','بوصفها قرارًا نظريًا يربط مفهومًا مجردًا بملاحظة قابلة للتسجيل، لا مجرد عد محايد.',None),('contrast','ما الفرق بين دقة الحساب وصلاحية المقياس؟','قد تكون الحسابات دقيقة عدديًا بينما يكون المؤشر نفسه ضعيف الصلة بالسؤال المقصود.',None),('inference','ماذا كان سيحدث لو اعتمد الفريق الزمن وحده؟','كان يمكن أن يصنف بعض الطلبة ذوي الصعوبة على أنهم يحققون تعلمًا أفضل لمجرد بقائهم مدة أطول.',None),('summary','ما التغيير المنهجي الأهم الذي أدخله البروتوكول؟','ألزم الفريق بتبرير كل مؤشر وبيان حدود ما يمكن أن يمثله قبل تفسير النتائج.',None),('single_word_definition','ما معنى «مقياس» هنا؟','وسيلة أو معيار يستخدم لتقدير مقدار أو خاصية بطريقة محددة.','مقياس'),('single_word_definition','ما معنى «بروتوكول» في هذا السياق؟','خطة أو إجراءات محددة مسبقًا لتنظيم طريقة إجراء الدراسة وجمع الأدلة.','بروتوكول')]
},
{
'id':'ar-c1-u01-p02','sequence':2,'title':'عينة واسعة لا تعني تمثيلًا كاملًا','passage_type':'reinforcement','genre':'academic-style synthesis','domains':['research','society','statistics'],'topics':['sampling','generalization','selection bias'],
'text':'نشرت مجموعة بحثية خيالية ملخصًا عن عادات القراءة لدى سكان مدينة كبيرة. كان لديها آلاف الإجابات، ولذلك وصف أحد المحررين النتيجة بأنها «صورة دقيقة لسكان المدينة». غير أن الباحثة مريم سألت سؤالًا مختلفًا: من الذي وصل أصلًا إلى الاستبيان ومن الذي اختار الإجابة؟ نُشر الرابط في مكتبات عامة ونوادٍ للقراءة وصفحات ثقافية، أي في أماكن يرتادها أشخاص مهتمون بالقراءة أكثر من المتوسط. العدد الكبير يقلل بعض أنواع الخطأ العشوائي، لكنه لا يصلح تلقائيًا انحياز الدخول إلى العينة. حسبما أظهر الوصف الإحصائي، كانت الأعمار والأحياء متنوعة، لكن المشاركين الذين قالوا إنهم لا يقرأون إلا نادرًا كانوا أقل بكثير مما توقعه الفريق من سجلات خدمة عامة مستقلة. لم تستخدم مريم هذا الفرق لإلغاء الدراسة. قالت إن البيانات ما زالت مفيدة للإجابة عن سؤال أضيق: ما الأنماط الموجودة بين الأشخاص الذين وصل إليهم الاستبيان واستجابوا له؟ ثم قارنت النتائج بمصدر ثان جُمعت بياناته بطريقة مختلفة. بعض العلاقات ظهرت في المصدرين، بينما اختفت علاقات أخرى. عند كتابة الخلاصة تجنب الفريق عبارتين متطرفتين: لم يقل إن «الآلاف يضمنون التمثيل»، ولم يقل إن «العينة المنحازة لا تعلمنا شيئًا». بدل ذلك فصل بين حجم العينة وطريقة اختيارها، وبين وصف المشاركين وتعميم الوصف على مجتمع أوسع. كانت الصياغة النهائية أطول وأقل جاذبية من العنوان الأول، لكنها أوضحت بدقة من تشملهم النتيجة وما الذي يحتاج إلى دليل إضافي قبل تعميمه.',
'target_forms':['إحصائي','حسبما'],'reviews':[('مقياس','R1','other'),('بروتوكول','R1','other')],
'grammar':[{'id':'ar-c1-scope-qualification','role':'new','description':'تقييد التعميم وفق آلية اختيار العينة لا وفق حجمها فقط'}],
'discourse':[{'id':'c1-sample-generalization','role':'new','description':'separate sample size, sampling mechanism, description, and population-level generalization'}],
'qa':[('gist','لماذا لا يكفي وجود آلاف الإجابات لتمثيل سكان المدينة؟','لأن طريقة الوصول إلى المشاركين قد تختار أشخاصًا مهتمين بالقراءة أكثر من غيرهم.',None),('literal_detail','أين نشر الاستبيان؟','في المكتبات العامة ونوادي القراءة والصفحات الثقافية.',None),('inference','ما نوع الخطأ الذي لا يعالجه العدد الكبير تلقائيًا؟','الانحياز المنهجي الناتج من دخول أنواع معينة من الناس إلى العينة أكثر من غيرهم.',None),('argument_relation','ما وظيفة المصدر الثاني؟','اختبار ما إذا كانت بعض العلاقات تظهر تحت طريقة جمع مختلفة بدل الاعتماد على مصدر واحد.',None),('main_claim','ما الفرق بين وصف العينة وتعميم النتيجة؟','الوصف يخص من شارك فعليًا، أما التعميم فيحتاج مبررًا لاعتبارهم ممثلين لمجتمع أوسع.',None),('contrast','ما العبارتان المتطرفتان اللتان يتجنبهما الفريق؟','أن العدد الكبير يضمن التمثيل، وأن وجود انحياز يجعل البيانات عديمة القيمة تمامًا.',None),('inference','لماذا كانت الصياغة النهائية أقل جاذبية؟','لأنها تضيف قيودًا وحدودًا للنطاق بدل تقديم نتيجة بسيطة شاملة.',None),('summary','كيف تعاملت مريم مع مشكلة العينة؟','ضيقت نطاق الادعاء، قارنت بمصدر مستقل، وميزت بين حجم العينة وآلية اختيارها.',None),('single_word_definition','ما معنى «إحصائي»؟','متعلق بتحليل البيانات العددية والأنماط المستخرجة منها.','إحصائي'),('single_word_definition','ما معنى «حسبما»؟','وفقًا لما أو كما يدل عليه مصدر أو وصف مذكور.','حسبما')]
},
{
'id':'ar-c1-u01-p03','sequence':3,'title':'العلاقة الظاهرة والسبب الخفي','passage_type':'interleaved','genre':'critique','domains':['research','behavior','methods'],'topics':['association','causal explanation','confounding'],
'text':'وجد تحليل خيالي أن الموظفين الذين يرسلون رسائل أكثر داخل نظام العمل ينجزون عددًا أكبر من المشروعات في السنة نفسها. كتب قارئ متحمس أن «زيادة الرسائل ترفع الإنتاج»، لكن الباحث يوسف رأى أن الانتقال من العلاقة إلى السبب أسرع من الأدلة. قد تكون الرسائل وسيلة للتنسيق فعلًا، وقد يكون هناك عامل خفي: الفرق التي تعمل على مشروعات أكثر تحتاج بطبيعتها إلى تواصل أكثر، فيرتفع المتغيران معًا من دون أن يكون أحدهما سبب الزيادة في الآخر. اقترح يوسف رسم سلسلة التفسير خطوة خطوة. أولًا: ما النمط المرصود؟ ثانيًا: ما الآلية المقترحة؟ ثالثًا: ما النتائج الأخرى التي نتوقعها إذا كانت الآلية صحيحة؟ رابعًا: ما التفسيرات البديلة التي تنتج النمط نفسه؟ كان أحد الزملاء يظن أن القصة الأولى أكثر منطقية لأنها «تبدو معقولة»، لكن يوسف فرّق بين كون التفسير منطقيًا وبين كونه مميزًا بالأدلة عن منافسيه. إذا تنبأت تفسيرات متعددة بالنتيجة نفسها، فلا يكفي تطابق النتيجة مع واحد منها. أضاف الفريق مقارنة داخل الفرق نفسها عبر فترات مختلفة، ثم فحص هل تسبق تغييرات التواصل تغييرات الإنجاز أم تأتي بعدها. لم تحسم المقارنة السببية وحدها، لكنها أضعفت بعض البدائل وقوت بدائل أخرى. انتهى التقرير إلى لغة مقيدة: توجد علاقة مستقرة نسبيًا، وهناك تفسير محتمل، لكن البيانات الحالية لا تفصل نهائيًا بين اتجاهات سببية متعددة. كانت هذه العبارة أقل حدة من الادعاء الأول، إلا أنها أوضح بشأن المسافة بين ما لوحظ وما فُسر.',
'target_forms':['خفي','منطقي'],'reviews':[('إحصائي','R1','other'),('مقياس','R2','other')],
'grammar':[{'id':'ar-c1-causal-modality','role':'new','description':'استخدام الاحتمال والشرط لفصل الملاحظة عن تفسيرها السببي'}],
'discourse':[{'id':'c1-association-explanation','role':'new','description':'reconstruct an inference chain from observed association through mechanism, predictions, and rival explanations'}],
'qa':[('gist','ما الاعتراض على قول إن زيادة الرسائل ترفع الإنتاج؟','البيانات تظهر علاقة، لكن عوامل أخرى أو اتجاه السببية قد يفسرانها.',None),('literal_detail','ما العامل الخفي المقترح؟','أن الفرق ذات المشروعات الأكثر تحتاج أصلًا إلى تواصل أكثر.',None),('inference','لماذا لا تكفي معقولية التفسير؟','لأن عدة تفسيرات معقولة قد تتنبأ بالنمط نفسه ويجب التمييز بينها بالأدلة.',None),('argument_relation','ما وظيفة فحص ترتيب التغيرات زمنيًا؟','المساعدة في تقييم اتجاه العلاقة وإضعاف بعض التفسيرات البديلة.',None),('main_claim','ما الفرق بين الملاحظة والتفسير؟','الملاحظة تصف نمطًا في البيانات، والتفسير يضيف آلية أو علاقة سببية تحتاج أدلة مستقلة.',None),('contrast','ما الفرق بين تفسير منطقي وتفسير مميز بالأدلة؟','المنطقي متسق ومعقول، أما المميز بالأدلة فتدعمه نتائج لا تفسرها البدائل بالسهولة نفسها.',None),('inference','لماذا لا تدعي الدراسة حسم السببية بعد المقارنة الإضافية؟','لأن المقارنة تضيق البدائل لكنها لا تستبعد كل تفسير ممكن.',None),('summary','ما سلسلة الأسئلة الأربعة التي يقترحها يوسف؟','النمط المرصود، الآلية المقترحة، تنبؤاتها الإضافية، والتفسيرات البديلة.',None),('single_word_definition','ما معنى «خفي» هنا؟','غير ظاهر مباشرة في القياس مع أنه قد يؤثر في النتائج.','خفي'),('single_word_definition','ما معنى «منطقي»؟','متسق مع قواعد التفكير ولا يتضمن تناقضًا ظاهرًا، من دون أن يعني ذلك أنه مثبت.','منطقي')]
},
{
'id':'ar-c1-u01-p04','sequence':4,'title':'إعادة النتيجة أم إعادة الاختبار؟','passage_type':'transfer','genre':'methods explanation','domains':['research','laboratory','methods'],'topics':['replication','repeatability','procedure variation'],
'text':'أراد مختبر خيالي التحقق من نتيجة سابقة تقول إن طريقة معينة لترتيب المعلومات تساعد المشاركين على تذكر قائمة معقدة. كان أسهل خيار هو تكرار التجربة الأصلية بأدواتها نفسها تقريبًا. قالت الباحثة هناء إن هذا مفيد، لكنه يجيب عن سؤال واحد فقط: هل تظهر النتيجة مرة أخرى عندما نحافظ على معظم التفاصيل؟ اقترحت مرحلتين. في الأولى يجري تكرار قريب من الأصل للتأكد من أن النمط ليس حادثة منفردة أو خطأ في التنفيذ. في الثانية يغير الفريق تفاصيل ليست جزءًا من النظرية: يستخدم مهمة أخرى، ومجموعة مختلفة، وترتيبًا منتظمًا جديدًا للخطوات مع الحفاظ على الفكرة الأساسية. إذا ظهرت النتيجة في النسخة الأولى فقط، فقد يعني ذلك أن بعض التفاصيل التي ظنها الباحثون هامشية كانت في الحقيقة ضرورية. وإذا ظهرت في نسخ متعددة، يصبح الادعاء أوسع، لكن ليس بلا حدود. نفذ المختبر المرحلتين. ظهرت النتيجة في التكرار القريب، ثم ضعفت عندما تغير نوع المهمة. بدل وصف الدراسة الجديدة بأنها «فشل في إعادة النتيجة»، أعاد الفريق صياغة السؤال: ما الخاصية الموجودة في المهمة الأصلية والمفقودة في الثانية؟ قاد ذلك إلى فرضية أدق حول مقدار البنية التي يحتاجها المشاركون قبل أن يفيدهم أسلوب الترتيب. قالت هناء إن قيمة التكرار ليست في جمع انتصارات تؤكد الدراسة الأولى، بل في كشف الشروط التي يستمر تحتها الأثر والشروط التي يختفي عندها. النتيجة القابلة للتكرار تحت شروط ضيقة قد تكون صحيحة، لكنها أضيق مما يوحي به عنوان عام.',
'target_forms':['تكرار','منتظم'],'reviews':[('بروتوكول','R3','other'),('منطقي','R1','other'),('خفي','R1','other')],
'grammar':[{'id':'ar-c1-replication-conditionals','role':'new','description':'صياغة ما تعنيه النتيجة تحت تغير الشروط باستخدام تراكيب إذا/فقد'}],
'discourse':[{'id':'c1-replication-boundary','role':'new','description':'distinguish close repetition from boundary-testing replication and use failure to refine claim scope'}],
'qa':[('gist','لماذا تقترح هناء مرحلتين بدل تكرار واحد؟','للفصل بين إعادة النتيجة تحت الشروط نفسها تقريبًا واختبار مدى استمرارها عند تغيير تفاصيل غير مفترضة نظريًا.',None),('literal_detail','ما الذي تغير في المرحلة الثانية؟','نوع المهمة والمجموعة وبعض ترتيب الخطوات مع إبقاء الفكرة الأساسية.',None),('inference','ماذا قد يعني ظهور النتيجة في النسخة القريبة فقط؟','أن بعض التفاصيل التي اعتبرت هامشية قد تكون شرطًا مهمًا لظهور الأثر.',None),('argument_relation','ما وظيفة النسخة التي ضعفت فيها النتيجة؟','تساعد في تحديد حدود الادعاء وتوليد فرضية أدق عن الشروط اللازمة.',None),('main_claim','ما قيمة التكرار وفق هناء؟','كشف الشروط التي يستمر تحتها الأثر أو يختفي، لا مجرد زيادة عدد النتائج المؤيدة.',None),('contrast','ما الفرق بين التكرار القريب واختبار الحدود؟','الأول يحافظ على معظم التفاصيل، والثاني يغير تفاصيل مدروسة لمعرفة مدى عمومية النتيجة.',None),('inference','لماذا لا يعد ضعف النتيجة بالضرورة هدمًا للدراسة الأولى؟','قد يبين أن النتيجة صحيحة ضمن نطاق أضيق مما صيغ أولًا.',None),('summary','كيف تغيرت الفرضية بعد المرحلة الثانية؟','أصبحت تربط فائدة أسلوب الترتيب بوجود قدر معين من البنية في المهمة.',None),('single_word_definition','ما معنى «تكرار»؟','إعادة حدوث أو إجراء الشيء مرة أخرى، وهنا إعادة اختبار دراسة أو إجراء.','تكرار'),('single_word_definition','ما معنى «منتظم»؟','يجري وفق ترتيب أو نمط ثابت نسبيًا يمكن تتبعه.','منتظم')]
},
{
'id':'ar-c1-u01-p05','sequence':5,'title':'النقد الذي يقوي البحث','passage_type':'integration','genre':'academic-style critique','domains':['research','publication','methods'],'topics':['consensus','critique','research gaps'],
'text':'ناقشت مجموعة خيالية ثلاث دراسات عن طريقة تعليم جديدة. كانت نتائجها تميل إلى الاتجاه نفسه، ولذلك كتب أحد الأعضاء أن هناك «إجماعًا علميًا» على فعاليتها. اعترضت ليلى على العبارة لا لأنها تعتقد أن الطريقة عديمة الفائدة، بل لأن كلمة إجماع تصف حالة أوسع من وجود ثلاث نتائج متشابهة. سألت: هل استخدمت الدراسات عينات مستقلة؟ هل قاست النتيجة نفسها؟ هل كانت هناك دراسات بنتائج مختلفة لم تدخل المراجعة؟ وهل تتشابه القيود إلى درجة تجعل النتائج الثلاث تعتمد على الثغرة نفسها؟ عندما أعاد الفريق القراءة وجد أن دراستين استخدمتا مواد تعليمية مشتقة من المصدر نفسه، وأن الثالثة قاست الأداء بعد يوم واحد فقط. ظهرت إذن ثغرة مشتركة: لا توجد معرفة كافية عن بقاء الأثر بعد مدة أو انتقاله إلى مهمة مختلفة. لم تستنتج ليلى أن النتائج «خاطئة». فرقت بين نقد الاستنتاج ونقد البيانات. البيانات قد تكون صحيحة ضمن شروطها، بينما تكون الخلاصة أوسع مما تسمح به. اقترحت صياغة مركبة: الأدلة الحالية متسقة في اتجاهها ضمن ثلاثة تصاميم محددة، لكنها لا تكفي بعد للقول إن الفائدة عامة أو طويلة الأمد. ثم حددت الدراسة التالية بحيث تستهدف الثغرة مباشرة بدل إعادة تصميم قريب من الدراسات السابقة. قالت إن النقد الجيد لا يبحث عن نقطة ضعف ليعلن سقوط العمل كله، ولا يحمي النتيجة من الأسئلة خوفًا من إضعافها. وظيفته تحديد الجزء الذي تدعمه الأدلة، والجزء الذي يعتمد على افتراض إضافي، والاختبار الذي يمكن أن يقلل عدم اليقين. بهذا المعنى، قد يجعل النقد الادعاء أضيق اليوم لكنه يجعل برنامج البحث أقوى غدًا.',
'target_forms':['إجماع','ثغرة'],'reviews':[('تكرار','R1','running_text'),('إحصائي','R3','other'),('حسبما','R3','other')],
'grammar':[{'id':'ar-c1-claim-scope-contrast','role':'new','description':'التفريق بين صحة البيانات ضمن شروطها وسعة الاستنتاج الذي يبنى عليها'}],
'discourse':[{'id':'c1-critique-as-refinement','role':'new','description':'treat critique as decomposition of supported claims, assumptions, gaps, and next discriminating tests'}],
'qa':[('gist','لماذا تعترض ليلى على كلمة «إجماع»؟','لأن ثلاث نتائج متشابهة لا تكفي وحدها لإثبات اتفاق علمي واسع ومستقل.',None),('literal_detail','ما الثغرة المشتركة التي يكتشفها الفريق؟','عدم معرفة بقاء الأثر بعد مدة أو انتقاله إلى مهمة مختلفة.',None),('inference','لماذا يهم أن دراستين استخدمتا مواد من المصدر نفسه؟','لأن استقلال الأدلة قد يكون أقل مما يوحي به عد الدراسات كأنها اختبارات منفصلة تمامًا.',None),('argument_relation','ما وظيفة التمييز بين نقد البيانات ونقد الاستنتاج؟','يسمح بقبول نتائج محدودة مع رفض تعميم أوسع لا تدعمه تلك النتائج.',None),('main_claim','ما وظيفة النقد الجيد في البحث؟','تحديد ما تدعمه الأدلة وما يعتمد على افتراض وما الاختبار الذي يقلل عدم اليقين.',None),('contrast','ما الفرق بين النقد والهدم في النص؟','النقد يضبط نطاق الادعاء ويقترح اختبارًا أفضل، أما الهدم فيعامل أي ضعف كسبب لإلغاء العمل كله.',None),('inference','لماذا قد يكون الادعاء الأضيق أقوى؟','لأنه يطابق حدود الأدلة ويكون أقل اعتمادًا على افتراضات غير مختبرة.',None),('summary','كيف تغير اقتراح الدراسة التالية؟','أصبح يستهدف بقاء الأثر وانتقاله بدل تكرار تصميم قريب لا يعالج الفجوة.',None),('single_word_definition','ما معنى «إجماع»؟','اتفاق واسع نسبيًا بين جهات أو خبراء، وليس مجرد تطابق عدد قليل من النتائج.','إجماع'),('single_word_definition','ما معنى «ثغرة» هنا؟','جزء ناقص في المعرفة أو التصميم أو الحجة يحتاج إلى اختبار أو دليل إضافي.','ثغرة')]
},
{
'id':'ar-c1-u01-p06','sequence':6,'title':'خريطة الدليل قبل قوة العبارة','passage_type':'fluency','genre':'C1 research synthesis','domains':['research','methods','evidence'],'topics':['measurement','sampling','causality','replication','critique'],
'text':'في نهاية الوحدة رسمت سلمى خريطة لا تبدأ بالنتيجة بل بالسؤال. إذا كان المفهوم واسعًا، سألت أولًا أي مقياس يمثله وما الذي قد يفلت منه، ثم كتبت بروتوكولًا يوضح القرارات قبل رؤية النتيجة. وعند قراءة وصف إحصائي، لم تسأل عن حجم العينة فقط، بل حسبما جُمعت ومن يستطيع الدخول إليها ومن بقي خارجها. وإذا ظهر ارتباط قوي، بحثت عن عامل خفي وعن تفسير منطقي منافس قبل الانتقال إلى لغة السبب. ثم ميزت بين تكرار قريب يعيد الإجراء تحت شروط متشابهة واختبار منتظم يغير بعض الشروط ليكشف حدود الادعاء. وأخيرًا رفضت استخدام كلمة إجماع لمجرد أن عدة أوراق تسير في اتجاه واحد، وسألت هل الأدلة مستقلة وما الثغرة المشتركة التي قد تتكرر بينها. لم تكن هذه الخريطة قائمة حيل تجعل كل بحث ضعيفًا. بالعكس، كانت طريقة لتحديد نوع القوة التي يملكها كل دليل. مقياس جيد يقوي الصلة بين السؤال والملاحظة، وعينة مناسبة تقوي التعميم، وتصميم يميز التفسيرات يقوي الادعاء السببي، وتكرار متنوع يقوي معرفة الحدود، ونقد واضح يقوي القرار بشأن الدراسة التالية. قالت سلمى إن العبارة العلمية الأقوى ليست دائمًا العبارة الأوسع. أحيانًا تكون القوة في أن نعرف بدقة أين ينتهي الدليل. عندما يقول التقرير «نعرف هذا تحت هذه الشروط، ونرجح ذلك بسبب هذه المقارنة، ولا نعرف بعد هذا الجزء»، فهو لا يعرض ضعفًا لغويًا، بل يبني خريطة يستطيع قارئ آخر فحصها أو الاعتراض عليها أو تطويرها.',
'target_forms':[],'reviews':[('مقياس','R2','running_text'),('بروتوكول','R2','running_text'),('إحصائي','R2','running_text'),('حسبما','R2','running_text'),('خفي','R2','running_text'),('منطقي','R2','running_text'),('تكرار','R2','running_text'),('منتظم','R2','running_text'),('إجماع','R2','running_text'),('ثغرة','R2','running_text')],
'grammar':[{'id':'ar-c1-u01-cumulative','role':'integration','description':'تقييد قوة العبارة وفق نوع الدليل وحدوده'}],
'discourse':[{'id':'c1-evidence-map-synthesis','role':'integration','description':'synthesize construct measurement, sampling, causal inference, replication, and critique into an inspectable evidence map'}],
'qa':[('gist','ما الفكرة المنظمة لخريطة سلمى؟','ربط قوة كل نوع من الادعاء بنوع الدليل وحدوده بدل القفز من نتيجة إلى عبارة واسعة.',None),('literal_detail','ما الذي تسأل عنه عند قراءة وصف إحصائي؟','كيف جُمعت العينة ومن يستطيع الدخول إليها ومن بقي خارجها.',None),('inference','لماذا تبحث عن تفسير منافس حتى عندما يكون الارتباط قويًا؟','لأن قوة العلاقة لا تحدد وحدها سببها وقد تنتج من عامل خفي أو اتجاه سببي آخر.',None),('argument_relation','ما وظيفة سلسلة «مقياس، عينة، تصميم، تكرار، نقد»؟','تربط كل عنصر بنوع مختلف من القوة المعرفية التي يضيفها.',None),('main_claim','لماذا ليست العبارة الأوسع دائمًا الأقوى؟','لأن العبارة التي تتجاوز حدود الأدلة تعتمد على افتراضات إضافية، بينما العبارة المقيدة قد تكون أوثق تبريرًا.',None),('contrast','ما الفرق بين إظهار حدود المعرفة وإظهار ضعف البحث؟','ذكر الحدود يوضح ما تدعمه الأدلة فعلًا، ولا يعني أن الدراسة بلا قيمة.',None),('inference','كيف تجعل الخريطة البحث قابلًا للنقد البنّاء؟','تظهر أين دخل القياس والاختيار والتفسير وما الذي يحتاج إلى اختبار جديد.',None),('summary','اذكر خمسة مكونات في خريطة الدليل.','المقياس، طريقة اختيار العينة، التفسيرات السببية المنافسة، التكرار عبر الشروط، والثغرات التي يكشفها النقد.',None),('inference','ما معنى قول التقرير «نرجح ذلك» بدل «أثبتنا ذلك»؟','أن المقارنة تدعم تفسيرًا أكثر من غيره من دون استبعاد كل بديل نهائيًا.',None),('inference','ما المهارة العامة التي تختبرها الوحدة؟','مطابقة قوة الاستنتاج ونطاقه مع نوع الدليل المتاح وحدوده.',None)]
}
]

def build(x,d):
    text=x['text']; targets=[target(f,text,d) for f in x['target_forms']]; ids={t['form']:t['id'] for t in targets}
    qs,answers=qa(x['qa'],ids); reviews=[review(f,s,r,d) for f,s,r in x['reviews']]
    return {'id':x['id'],'language':'ar','cefr':'C1','unit':1,'sequence':x['sequence'],'revision':1,'title':x['title'],
    'passage_type':x['passage_type'],'genre':x['genre'],'domains':x['domains'],'topics':x['topics'],'text':text,
    'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!؟](?:\s|$)',text))),
    'estimated_known_token_coverage':0,'new_lexical_targets':targets,'review_lexical_targets':reviews,'grammar_targets':x['grammar'],'discourse_targets':x['discourse'],
    'questions':qs,'answer_key':answers,'speed_training':{'timed':x['passage_type']=='fluency','benchmark_eligible':False,'comprehension_gate':0.8,'new_word_policy':'none' if x['passage_type']=='fluency' else 'controlled','notes':'C1 generation-stage passage; formal fluency/coverage decision deferred to final audit.'},
    'quality':{'status':'draft','linguistic_review':'pending','pedagogical_review':'pending','coverage_check':'pending','answer_key_check':'pending','schema_check':'pending','fact_check':'not_required','notes':['Fictional/method-focused C1 generation-stage draft; formal 10+ pass audit battery deferred.']},
    'paired_text_group':None,'prerequisites':['Arabic A1-B2 generation corpus'],
    'difficulty_notes_internal':'C1 Unit 01 generation draft: research and evidence through construct validity, sampling, causal inference, replication boundaries, critique, and calibrated claim strength.',
    'reader_tags':['unit_role:'+x['passage_type'],'generation_batch','c1'],
    'complexity_profile':{'mean_sentence_length':None,'median_sentence_length':None,'clause_count':None,'subordination_count':None,'coordination_count':None,'connective_diversity':None,'lexical_diversity':None,'reference_chain_max_distance':None,'multiword_expression_count':None,'morphology_notes':'C1 generation-stage MSA with academic qualification, method comparison, and inference language.','inference_depth':'multi_step_cross_paragraph'}}

def main():
    d=lexicon(); forms=[]
    for x in R: forms.extend(x['target_forms']); forms.extend(f for f,_,_ in x['reviews'])
    missing=sorted({f for f in forms if norm(f) not in d})
    if missing: raise KeyError(f'missing cleared forms: {missing}')
    rows=[]
    if OUT.exists(): rows=[json.loads(line) for line in OUT.read_text(encoding='utf-8').splitlines() if line.strip()]
    rows=[r for r in rows if r.get('unit')!=1]; rows.extend(build(x,d) for x in R); rows.sort(key=lambda r:r.get('sequence',0))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
    print(f'wrote {len(R)} Arabic C1 Unit 01 passages; total C1 rows={len(rows)}')
if __name__=='__main__': main()
