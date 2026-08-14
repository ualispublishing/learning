#!/usr/bin/env python3
"""Generate repaired Arabic B2 Unit 09: public policy and trade-offs.

Generation-stage source only. Target and review IDs are derived from the
canonical cleared Arabic lexicon; no guessed rank IDs are permitted.
"""
from __future__ import annotations
import json,re,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reading/arabic/b2/passages.jsonl'
LEX=ROOT/'reading/lexicons/arabic.jsonl'
AR_DIAC=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')

def norm(s):
    return AR_DIAC.sub('',unicodedata.normalize('NFC',str(s or '')).replace('ـ','').strip())

def lexicon():
    d={}
    for line in LEX.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r=json.loads(line); d.setdefault(norm(r.get('form','')),r)
    return d

PREFERRED={
    'توصية':'recommendation',
    'بند':'clause; provision',
    'تخصيص':'allocation; assignment of resources',
    'فاعل':'effective; active in producing an effect',
    'رصد':'observation; monitoring',
    'توازن':'balance',
    'تقليل':'reduction; minimizing',
    'تعويض':'compensation',
    'ترقية':'promotion; advancement',
    'مستقبلي':'future-oriented',
}

def lexrow(form,d):
    r=d.get(norm(form))
    if not r:
        raise KeyError(f'Cleared lexicon form not found: {form}')
    return r

def target(form,text,d):
    r=lexrow(form,d)
    return {
        'id':f"ar-r{r['rank']}",'form':form,'lemma':form,
        'part_of_speech':r.get('part_of_speech_source'),
        'intended_sense':PREFERRED[form],
        'register':'contemporary standard','variety':'MSA',
        'context_strategy':['policy_tradeoff','distributional_effect','implementation_gap'],
        'first_introduced':True,'exposures_in_text':max(1,text.count(form)),
        'source_lexicon':r.get('source_file'),'source_rank':r['rank'],'beyond_base':False,
    }

def review(form,stage,representation,d):
    r=lexrow(form,d)
    return {'id':f"ar-r{r['rank']}",'form':form,'review_stage':stage,'representation':representation}

def qa(items,target_ids):
    q=[]; a=[]
    for i,(typ,prompt,answer,target_form) in enumerate(items,1):
        z={'id':f'q{i}','type':typ,'prompt':prompt,'answer_id':f'a{i}'}
        if target_form:
            z['target_ids']=[target_ids[target_form]]
        q.append(z)
        a.append({'id':f'a{i}','question_id':f'q{i}','answer':answer,'explanation':''})
    if len(q)!=10: raise ValueError('ten questions required')
    return q,a

R=[
{
'id':'ar-b2-u09-p01','sequence':49,'title':'من التوصية إلى البند الملزم','passage_type':'instructional','genre':'policy-design case','domains':['public','policy','community'],'topics':['recommendations','rules','implementation'],
'text':'أعدت لجنة خيالية تقريرًا عن تقليل الازدحام قرب مدرسة. انتهى التقرير إلى توصية بأن تخصص منطقة قصيرة للتوقف السريع في ساعات محددة. بعد أشهر كتب مسؤول مسودة لائحة تتضمن بندًا يمنع الوقوف أكثر من خمس دقائق في مساحة أوسع من التي اقترحها التقرير. قال بعض السكان إن «اللجنة قررت المنع»، مع أن التقرير الأصلي لم يكن قرارًا ملزمًا ولم يحدد المساحة الجديدة. أعادت نور تتبع المراحل: الدراسة تصف المشكلة، والتوصية تقترح اتجاهًا، ثم تأتي مرحلة تحويل الاقتراح إلى بند يمكن تطبيقه وعقوبته ومراجعته. في هذه المرحلة قد تضاف تفاصيل لم تختبرها الدراسة نفسها. لذلك طلبت اللجنة أن يوضح المسؤول لماذا وسع المنطقة وكيف سيقاس أثر القاعدة الجديدة، وأن ينشر نسخة تميز بوضوح ما جاء من التوصية وما أضيف أثناء الصياغة. قالت نور إن السياسة لا تنتقل من الدليل إلى التطبيق بضغطة واحدة. كل خطوة ترجمة بين لغة مختلفة: الباحث يسأل ما الذي يحدث، وصانع التوصية يسأل ما الذي قد يساعد، وكاتب البند يحدد من يلزم بماذا ومتى. إذا اختلطت هذه المراحل، قد ننسب إلى الدليل قرارًا لم يتخذه أو نعامل خيارًا إداريًا كأنه نتيجة علمية حتمية.',
'target_forms':['توصية','بند'],'reviews':[],
'grammar':[{'id':'ar-b2-policy-stage-translation','role':'new','description':'الدراسة ثم التوصية ثم البند الملزم مراحل مختلفة في السلطة والتفاصيل'}],
'discourse':[{'id':'b2-policy-evidence-to-rule','role':'new','description':'trace how evidence is translated into recommendations and then binding provisions, with additions made visible'}],
'qa':[('gist','ما الخطأ في قول السكان إن اللجنة «قررت المنع»؟','اللجنة قدمت توصية غير ملزمة، بينما المسؤول أضاف تفاصيل ملزمة أوسع في مرحلة الصياغة.',None),('literal_detail','ما التفصيلان اللذان أضيفا في المسودة؟','حد خمس دقائق ومنطقة أوسع من مساحة التوصية.',None),('inference','لماذا يهم توضيح ما أضيف بعد التقرير؟','لأن هذه التفاصيل لم تختبرها الدراسة ولا يجوز نسبها تلقائيًا إلى دليلها.',None),('cause_effect','ماذا تطلب اللجنة من المسؤول؟','تبرير توسيع المنطقة وبيان طريقة القياس وفصل الإضافات عن التوصية الأصلية.',None),('main_claim','ما العلاقة بين الدليل والسياسة؟','يمر الدليل بمراحل ترجمة تتضمن اختيارات إضافية يجب إعلانها بدل تقديمها كحتمية.',None),('argument_relation','ما وظيفة وصف أسئلة الباحث وصانع التوصية وكاتب البند؟','يبين اختلاف وظيفة كل مرحلة ونوع الحكم الذي تضيفه.',None),('contrast','ما الفرق بين توصية وبند ملزم؟','التوصية تقترح اتجاهًا، والبند يحدد قاعدة قابلة للتطبيق على أشخاص أو حالات.',None),('reference_resolution','إلى ماذا تشير «هذه المرحلة»؟','إلى مرحلة تحويل التوصية إلى لائحة أو بند ملزم.',None),('single_word_definition','ما معنى «توصية»؟','اقتراح رسمي أو مدروس لما ينبغي فعله من دون أن يكون بالضرورة ملزمًا.','توصية'),('single_word_definition','ما معنى «بند»؟','جزء محدد من لائحة أو اتفاق أو وثيقة يقرر قاعدة أو شرطًا.','بند')]
},
{
'id':'ar-b2-u09-p02','sequence':50,'title':'سياسة جيدة على الورق وتنفيذ ضعيف في الواقع','passage_type':'reinforcement','genre':'implementation analysis','domains':['public','policy'],'topics':['implementation','system design','service access'],
'text':'أطلقت جهة خيالية برنامجًا يضمن موعدًا سريعًا لخدمة عامة بعد تسجيل الطلب. كانت القاعدة واضحة، لكن بعد أشهر اختلفت النتائج بين ثلاثة مكاتب. في الأول كان معظم الطلبات يعالج في الوقت المطلوب، وفي الثاني تراكم التأخير، وفي الثالث كان المواطنون يعيدون إرسال الطلبات لأن الإرشادات غير واضحة. قال مسؤول إن المشكلة تثبت أن السياسة نفسها فاشلة. اعترضت نور على سرعة الحكم. قد يكون هناك خلل في التصميم، لكن يجب أولًا فصل تصميم القاعدة عن ظروف التنفيذ. هل تملك المكاتب العدد نفسه من الموظفين؟ هل البرنامج الرقمي يعمل بالطريقة نفسها؟ هل تعريف «الطلب المكتمل» واضح؟ وهل تخصيص الموارد يتناسب مع عدد المستخدمين؟ أظهرت المقارنة أن المكتب الثاني فقد موظفين ولم تعوضهم الجهة، بينما الثالث يستخدم صفحة قديمة تختلف عن الإرشادات المركزية. أصلحت الجهة مشكلتين وبقي تأخير أصغر مشترك بين الجميع. عندها أصبح من المعقول سؤال هل الهدف الزمني نفسه واقعي وفاعل في تحسين الخدمة أم أنه يفرض معيارًا لا تعكسه القدرة المتاحة. قالت نور إن تقييم السياسة يحتاج إلى فحص «النظرية» و«التنفيذ» معًا؛ فالفشل قد يأتي من قاعدة غير مناسبة، أو من تنفيذ لا يطابق القاعدة، أو من الاثنين.',
'target_forms':['تخصيص','فاعل'],'reviews':[('توصية','R1','running_text'),('بند','R1','other')],
'grammar':[{'id':'ar-b2-policy-design-implementation','role':'new','description':'افصل عيب التصميم عن عيب التنفيذ ثم افحص ما يبقى مشتركًا'}],
'discourse':[{'id':'b2-policy-implementation-gap','role':'new','description':'diagnose implementation variation before attributing outcomes to the policy rule itself'}],
'qa':[('gist','لماذا لا تعتبر نور النتائج دليلًا مباشرًا على فشل السياسة؟','لأن المكاتب تنفذها في ظروف وأدوات وموارد مختلفة وقد يكون جزء كبير من الفرق تنفيذيًا.',None),('literal_detail','ما مشكلتا المكتبين الثاني والثالث؟','نقص الموظفين وصفحة قديمة لا تطابق الإرشادات.',None),('inference','لماذا يصبح السؤال عن الهدف الزمني أقوى بعد الإصلاح؟','لأن إزالة اختلافات التنفيذ تكشف تأخيرًا مشتركًا قد يعود إلى تصميم الهدف نفسه.',None),('cause_effect','ماذا يحدث بعد إصلاح المشكلتين؟','تقل الفروق ويبقى تأخير أصغر مشترك يمكن تقييمه على مستوى السياسة.',None),('main_claim','كيف يجب تفسير فشل سياسة؟','بفصل تصميم القاعدة عن قدرة التنفيذ وظروفه ثم معرفة مقدار مساهمة كل مستوى.',None),('argument_relation','ما وظيفة المكاتب الثلاثة؟','توفر مقارنة تكشف أن النتائج المختلفة قد تنشأ من التنفيذ لا من القاعدة المشتركة وحدها.',None),('contrast','ما الفرق بين عيب التصميم وعيب التنفيذ؟','عيب التصميم يتعلق بالقاعدة أو الهدف المشترك، وعيب التنفيذ يتعلق بطريقة التطبيق والموارد في الواقع.',None),('reference_resolution','إلى ماذا تشير «المشكلتين»؟','إلى نقص الموظفين وعدم تطابق الصفحة القديمة مع الإرشادات.',None),('single_word_definition','ما معنى «تخصيص» الموارد؟','تعيين موارد أو وقت أو مال لغرض أو جهة محددة.','تخصيص'),('single_word_definition','ما معنى «فاعل» هنا؟','قادر على إحداث أثر حقيقي أو أداء الوظيفة المقصودة.','فاعل')]
},
{
'id':'ar-b2-u09-p03','sequence':51,'title':'الرصد أم المنع التلقائي؟','passage_type':'interleaved','genre':'regulation tradeoff case','domains':['public','policy','ethics'],'topics':['monitoring','enforcement','compliance'],
'text':'وضعت مؤسسة خيالية قاعدة تمنع استخدام قاعة مشتركة بعد منتصف الليل بسبب شكاوى متكررة من الضوضاء. في البداية اعتمدت على لافتة فقط، لكن القاعدة لم تحترم دائمًا. اقترح فريق رصد الدخول بعد الوقت المحدد وإرسال تنبيه إلى الإدارة، واقترح فريق آخر إغلاق الباب آليًا تمامًا عند منتصف الليل. بدا الخيار الثاني أكثر ضمانًا، لكنه لا يسمح باستثناء حتى في حالة طارئة أو نشاط حصل على إذن خاص. ناقش الفريق درجات التنفيذ: إشعار، ثم مراجعة، ثم عقوبة عند التكرار، مع مفتاح طوارئ موثق. قال مؤيدو الإغلاق الكامل إن المرونة ستسمح بالتحايل، بينما رأى المعارضون أن النظام يجب أن يميز بين الخرق والاستثناء المشروع. اختاروا الرصد مع سجل واضح وقواعد للاستثناء بدل الإغلاق التام، ثم قرروا مراجعة عدد المخالفات بعد شهر. قالت نور إن المسألة تحتاج إلى توازن بين خفض المخالفات والحفاظ على مساحة للحكم في الحالات الاستثنائية. كلما زادت قوة المنع قل مجال التقدير، وقد ينخفض الخرق لكن ترتفع تكلفة الخطأ عندما تمنع القاعدة حالة كان ينبغي السماح بها.',
'target_forms':['رصد','توازن'],'reviews':[('توصية','R2','other'),('تخصيص','R1','other'),('فاعل','R1','other')],
'grammar':[{'id':'ar-b2-enforcement-proportionality','role':'new','description':'قوة التنفيذ تقلل الخرق لكنها قد تزيد تكلفة الخطأ والاستثناء الممنوع'}],
'discourse':[{'id':'b2-policy-monitoring-enforcement','role':'new','description':'compare monitoring and hard technical prevention by compliance and exception costs'}],
'qa':[('gist','لماذا لا يختار الفريق الإغلاق الآلي الكامل؟','لأنه يمنع المخالفات لكنه يمنع أيضًا استثناءات مشروعة وقد يخلق أخطاء عالية التكلفة.',None),('literal_detail','ما تسلسل التنفيذ المختار؟','إشعار ثم مراجعة ثم عقوبة عند التكرار مع مفتاح طوارئ موثق.',None),('inference','لماذا يخشى مؤيدو الإغلاق من المرونة؟','لأنهم يرون أن الاستثناءات قد تستخدم للتحايل وتضعف الامتثال.',None),('cause_effect','كيف تؤثر زيادة المنع التلقائي في الحكم البشري؟','تقلل مساحة التقدير والاستثناء حتى عندما تكون الحالة مختلفة.',None),('main_claim','ما الذي يجب موازنته في التنفيذ؟','خفض المخالفات مقابل تكلفة الأخطاء والحاجة إلى استثناءات مشروعة.',None),('argument_relation','ما وظيفة حالة الطوارئ؟','تقدم مثالًا على حالة يكون فيها المنع الآلي نتيجة غير مرغوبة رغم القاعدة العامة.',None),('contrast','ما الفرق بين الرصد والإغلاق الكامل؟','الرصد يسجل ما يحدث ويسمح بالمراجعة، والإغلاق يمنع الفعل مباشرة.',None),('reference_resolution','إلى ماذا تشير «القاعدة» في النهاية؟','إلى قاعدة منع استخدام القاعة بعد منتصف الليل.',None),('single_word_definition','ما معنى «رصد» هنا؟','متابعة ما يحدث وتسجيله أو ملاحظته بصورة منظمة.','رصد'),('single_word_definition','ما معنى «توازن»؟','حالة تراعي فيها اعتبارات متعارضة من دون أن يطغى أحدها تمامًا.','توازن')]
},
{
'id':'ar-b2-u09-p04','sequence':52,'title':'من يدفع ثمن المنفعة العامة؟','passage_type':'transfer','genre':'distributional policy case','domains':['public','economics','policy'],'topics':['costs','compensation','distribution'],
'text':'قررت مدينة خيالية إغلاق شارع صغير أمام السيارات في ساعات معينة لتحسين سلامة المشاة والوصول إلى المدرسة. استفاد كثير من الأسر من انخفاض حركة السيارات، لكن متجرًا يعتمد على توصيل بضائع ثقيلة في الصباح تحمل عبئًا أكبر من غيره. قال بعض السكان إن السياسة مفيدة للأغلبية ولذلك لا حاجة إلى تغييرها. وقال صاحب المتجر إن المنفعة العامة لا تمحو خسارته الخاصة. ناقشت اللجنة ثلاثة ردود: إلغاء القاعدة، أو إبقاؤها بلا تغيير، أو توفير تعويض عملي مثل نافذة توصيل قصيرة وتصريح خاص للمركبات الثقيلة. اختاروا الحل الثالث بعد اختبار تأثيره في السلامة. لم يكن التعويض مالًا، بل تعديلًا يحقق تقليل العبء على طرف محدد من دون إزالة الهدف الأساسي. قالت نور إن توزيع العبء جزء من تقييم السياسة لا موضوع منفصل يأتي بعد إثبات فائدتها العامة. يمكن لسياسة أن تزيد المنفعة الكلية وفي الوقت نفسه تضع عبئًا شديدًا على فئة صغيرة. السؤال عندها يصبح: هل العبء ضروري لتحقيق الهدف؟ وهل يمكن تقليله من دون فقد معظم الفائدة؟ وإذا لم يمكن، فما المبرر الذي يجعل تحميله لهذا الطرف عادلًا؟',
'target_forms':['تقليل','تعويض'],'reviews':[('رصد','R1','other'),('توازن','R1','running_text')],
'grammar':[{'id':'ar-b2-policy-concentrated-cost','role':'new','description':'الفائدة العامة لا تمحو التكلفة المركزة على فئة صغيرة'}],
'discourse':[{'id':'b2-policy-compensation','role':'new','description':'evaluate concentrated burdens and targeted mitigation while preserving the policy objective'}],
'qa':[('gist','ما المشكلة في الاكتفاء بالمنفعة للأغلبية؟','قد تخفي عبئًا كبيرًا ومركزًا على طرف صغير مثل المتجر.',None),('literal_detail','ما التعويض العملي الذي يختاره الفريق؟','نافذة توصيل قصيرة وتصريح خاص للمركبات الثقيلة.',None),('inference','لماذا لا يكون التعويض بالضرورة مالًا؟','لأن الهدف هو تخفيف العبء ويمكن فعل ذلك بتغيير في التطبيق أو الوصول.',None),('cause_effect','كيف يتجنب الحل الثالث إلغاء الهدف؟','يحافظ على إغلاق الشارع عمومًا ويضيف استثناءً محدودًا ومدروسًا للتوصيل.',None),('main_claim','كيف تدخل أعباء الفئات الصغيرة في تقييم السياسة؟','يجب فحص شدة العبء وضرورته وإمكانية تخفيفه لا الاكتفاء بالمنفعة الإجمالية.',None),('argument_relation','ما وظيفة سؤال «هل العبء ضروري»؟','يختبر ما إذا كانت التكلفة ملازمة للهدف أم نتيجة تصميم يمكن تحسينه.',None),('contrast','ما الفرق بين إلغاء السياسة وتعويض الطرف المتضرر؟','الإلغاء يزيل الهدف كله، والتعويض يحاول خفض العبء مع إبقاء معظم الفائدة.',None),('reference_resolution','إلى ماذا تشير «فقد معظم الفائدة»؟','إلى خسارة منفعة سلامة المشاة والوصول التي تحققها السياسة.',None),('single_word_definition','ما معنى «تقليل»؟','جعل المقدار أو الأثر أقل مما كان عليه.','تقليل'),('single_word_definition','ما معنى «تعويض»؟','شيء يقدم لتخفيف خسارة أو ضرر أو استبدال ما فُقد.','تعويض')]
},
{
'id':'ar-b2-u09-p05','sequence':53,'title':'مساعدة اليوم وفرص الغد','passage_type':'integration','genre':'social-program analysis','domains':['public','policy','community'],'topics':['assistance','advancement','future outcomes'],
'text':'صمم مركز خيالي برنامجًا لمساعدة أشخاص يبحثون عن عمل. كان يستطيع استخدام الميزانية لتقديم دعم مباشر قصير المدى، أو الاستثمار في تدريب وخدمات قد توسع فرص المشاركين مستقبلًا. انقسم الفريق. الدعم المباشر يخفف حاجة حاضرة ويمكن قياسه فورًا، لكن أثره ينتهي عندما ينتهي المال. التدريب قد يفتح خيارات أطول، مثل اكتساب مهارة أو الوصول إلى وظيفة تسمح بترقية لاحقة، لكنه لا يضمن نتيجة لكل شخص ويحتاج إلى وقت قبل أن يظهر أثره. رفضت نور صياغة الاختيار كأنه «مساعدة حقيقية» مقابل «اعتماد على النفس». بعض المشاركين يحتاجون إلى دعم الآن حتى يستطيعوا أصلًا حضور التدريب، بينما قد لا يكفي الدعم وحده لتغيير الفرص المستقبلية. صمم الفريق مسارًا يجمع حدًا من المساعدة المباشرة مع خيارات تدريب مختلفة، ثم قاس نتيجتين: الاستقرار القصير وقدرة المشاركين على الوصول إلى فرص جديدة بعد مدة. كما سمحوا بالخروج من التدريب الذي لا يناسب الشخص بدل جعله شرطًا لكل مساعدة. قالت نور إن السياسة ذات الأثر المستقبلي الجيد لا تضحي بالحاضر دائمًا باسم فائدة بعيدة، ولا تعالج الحاضر بطريقة تجعل كل عام نسخة من السابق. يجب أن تسأل أي حاجات عاجلة تمنع الناس من استخدام الفرص، وأي استثمار يزيد الخيارات بدل تحديد طريق واحد للجميع.',
'target_forms':['ترقية','مستقبلي'],'reviews':[('تقليل','R1','other'),('تعويض','R1','other')],
'grammar':[{'id':'ar-b2-present-future-policy','role':'new','description':'المساعدة الحالية والفرص المستقبلية قد تكون مكملة لا بدائل مطلقة'}],
'discourse':[{'id':'b2-policy-capability','role':'new','description':'compare immediate relief and future advancement while preserving choice and heterogeneous needs'}],
'qa':[('gist','لماذا يرفض النص الاختيار الثنائي بين الدعم والتدريب؟','لأن الحاجة الحالية قد تمنع استخدام التدريب، والتدريب قد يضيف خيارات لا يوفرها الدعم وحده.',None),('literal_detail','ما النتيجتان اللتان يقيسهما الفريق؟','الاستقرار القصير والوصول إلى فرص جديدة بعد مدة.',None),('inference','لماذا يسمح بالخروج من تدريب غير مناسب؟','حتى لا يتحول البرنامج إلى فرض مسار واحد لا يناسب ظروف كل شخص.',None),('cause_effect','كيف يكمل الدعم المباشر التدريب؟','يخفف عوائق عاجلة قد تمنع الشخص من حضور التدريب أو الاستفادة منه.',None),('main_claim','ما شكل السياسة المتوازنة هنا؟','معالجة حاجات عاجلة مع توسيع خيارات مستقبلية من دون فرض وسيلة واحدة على الجميع.',None),('argument_relation','ما وظيفة رفض عبارة «اعتماد على النفس»؟','يمنع تحويل تصميم البرنامج إلى حكم أخلاقي مبسط على من يحتاج دعمًا حاليًا.',None),('contrast','ما الفرق بين أثر الدعم وأثر التدريب؟','الدعم مباشر وقصير نسبيًا، والتدريب أبطأ وغير مضمون لكنه قد يوسع الخيارات مستقبلًا.',None),('reference_resolution','إلى ماذا تشير «طريق واحد»؟','إلى نوع تدريب أو مسار موحد تفرضه السياسة على جميع المشاركين.',None),('single_word_definition','ما معنى «ترقية» في سياق العمل؟','انتقال إلى مرتبة أو مسؤولية أعلى.','ترقية'),('single_word_definition','ما معنى «مستقبلي»؟','متعلق بما سيأتي لاحقًا أو مصمم لأثر في المستقبل.','مستقبلي')]
},
{
'id':'ar-b2-u09-p06','sequence':54,'title':'السياسة ليست نتيجة واحدة بل سلسلة اختيارات','passage_type':'fluency','genre':'B2 policy synthesis','domains':['public','policy','ethics'],'topics':['policy process','tradeoffs','evaluation'],
'text':'بعد أمثلة الوحدة رأت نور أن السياسة العامة سلسلة اختيارات أكثر من كونها قرارًا واحدًا. يبدأ الأمر أحيانًا بدراسة ثم توصية، لكن تحويلها إلى بند ملزم يضيف تفاصيل وسلطة جديدة. وبعد ذلك قد تفشل النتيجة لأن التصميم ضعيف أو لأن تخصيص الموارد لا يطابق الحاجة، ولذلك يجب فصل القاعدة عن ظروف التنفيذ وسؤال هل الأداة فاعلة أصلًا. أما الرصد والمنع فهما درجتان مختلفتان من القوة، ويحتاج الاختيار بينهما إلى توازن يراعي تكلفة الخطأ والاستثناء. وعندما تحقق السياسة منفعة عامة، يبقى سؤال تقليل العبء وتعويض من يتحمل ضررًا أكبر. وحتى البرامج الاجتماعية تحتاج إلى موازنة دعم الحاضر مع فرص ترقية وأثر مستقبلي لا يفرض طريقًا واحدًا على كل شخص. قالت نور إن تقييم السياسة يحتاج إلى خريطة زمنية: ما المشكلة التي عرفت؟ ما الدليل؟ ما التوصية؟ من أضاف القاعدة الملزمة؟ كيف نُفذت؟ من استفاد؟ من تحمل العبء؟ وما المؤشر الذي سيجعلنا نراجع القرار؟ هذه الأسئلة لا تجعل السياسة محايدة أو خالية من القيم، لكنها تمنعنا من إخفاء الاختيارات داخل كلمات مثل «الدليل» أو «التنفيذ». القرار العام الجيد يوضح أين دخلت القيمة، وأين دخلت القيود، وأين يستطيع الواقع أن يعيد فتح النقاش.',
'target_forms':[],'reviews':[('توصية','R2','running_text'),('بند','R2','running_text'),('تخصيص','R2','running_text'),('فاعل','R2','running_text'),('رصد','R2','running_text'),('توازن','R2','running_text'),('تقليل','R2','running_text'),('تعويض','R2','running_text'),('ترقية','R2','running_text'),('مستقبلي','R2','running_text')],
'grammar':[{'id':'ar-b2-u09-cumulative','role':'integration','description':'policy as staged translation from evidence to rule, implementation, burden, and revision'}],
'discourse':[{'id':'b2-policy-synthesis','role':'integration','description':'synthesize policy design, implementation, enforcement, distribution, future opportunity, and review over time'}],
'qa':[('gist','لماذا تصف نور السياسة كسلسلة اختيارات؟','لأن الدليل والتوصية والصياغة والتنفيذ والإنفاذ والتوزيع والتقييم تضيف قرارات مختلفة عبر الزمن.',None),('literal_detail','ما السؤال الذي تطرحه عن مراجعة القرار؟','ما المؤشر الذي سيجعلنا نراجع القرار؟',None),('inference','لماذا لا تجعل الخريطة السياسة محايدة؟','لأن القيم والأولويات ما زالت تدخل، لكن الخريطة توضح موضع دخولها بدل إخفائها.',None),('cause_effect','كيف يساعد فصل التصميم عن التنفيذ؟','يمنع تعديل القاعدة بسبب مشكلة كان يمكن حلها في التطبيق أو العكس.',None),('main_claim','ما الذي يميز القرار العام الجيد؟','إظهار الأدلة والقيم والقيود والأعباء ونقاط المراجعة بدل تقديم النتيجة كحتمية.',None),('argument_relation','لماذا يجمع النص المراحل الخمس السابقة؟','ليبين أن أثر السياسة النهائي ينتج من سلسلة قرارات لا من النص الأول فقط.',None),('contrast','ما الفرق بين الدليل والقاعدة الملزمة؟','الدليل يصف أو يدعم معرفة، والقاعدة تضيف حكمًا على ما يجب أن يفعله الناس أو المؤسسات.',None),('reference_resolution','إلى ماذا تشير «هذه الأسئلة»؟','إلى أسئلة المشكلة والدليل والتوصية والقاعدة والتنفيذ والمستفيدين والأعباء والمراجعة.',None),('summary','اذكر أربعة أبعاد لتقييم السياسة.','تصميم القاعدة، جودة التنفيذ، قوة الإنفاذ، توزيع العبء، الفرص المستقبلية، ونقطة المراجعة.',None),('inference','لماذا يجب أن يستطيع الواقع إعادة فتح النقاش؟','لأن التنفيذ قد يكشف آثارًا وفئات أو أخطاء لم تكن معروفة عند تصميم السياسة.',None)]
}
]

def build(x,d):
    text=x['text']
    targets=[target(f,text,d) for f in x['target_forms']]
    target_ids={t['form']:t['id'] for t in targets}
    questions,answers=qa(x['qa'],target_ids)
    reviews=[review(f,s,r,d) for f,s,r in x['reviews']]
    return {
        'id':x['id'],'language':'ar','cefr':'B2','unit':9,'sequence':x['sequence'],'revision':2,
        'title':x['title'],'passage_type':x['passage_type'],'genre':x['genre'],'domains':x['domains'],'topics':x['topics'],'text':text,
        'word_count':len(text.split()),'sentence_count':max(1,len(re.findall(r'[.!؟](?:\s|$)',text))),
        'estimated_known_token_coverage':0,'new_lexical_targets':targets,'review_lexical_targets':reviews,
        'grammar_targets':x['grammar'],'discourse_targets':x['discourse'],'questions':questions,'answer_key':answers,
        'speed_training':{'timed':x['passage_type']=='fluency','benchmark_eligible':False,'comprehension_gate':0.8,'new_word_policy':'none' if x['passage_type']=='fluency' else 'controlled','notes':'B2 generation-stage passage; formal fluency/coverage decision deferred to final audit.'},
        'quality':{'status':'draft','linguistic_review':'pending','pedagogical_review':'pending','coverage_check':'pending','answer_key_check':'pending','schema_check':'pending','fact_check':'not_required','notes':['High-quality fictional, non-partisan B2 public-policy generation-stage draft; formal audits deferred.','Revision 2 repairs source-backed lexical targets and derives target IDs from the canonical lexicon.']},
        'paired_text_group':None,'prerequisites':['Arabic A1-B1 generation corpus','Arabic B2 Units 01-08 generation corpus'],
        'difficulty_notes_internal':'B2 Unit 09 generation draft: public policy and trade-offs through evidence-to-rule translation, implementation gaps, enforcement, burden distribution, compensation, advancement, and review.',
        'reader_tags':['unit_role:'+x['passage_type'],'generation_batch','b2'],
        'complexity_profile':{'mean_sentence_length':None,'median_sentence_length':None,'clause_count':None,'subordination_count':None,'coordination_count':None,'connective_diversity':None,'lexical_diversity':None,'reference_chain_max_distance':None,'multiword_expression_count':None,'morphology_notes':'B2 generation-stage MSA with policy-process, distribution, and revision language.','inference_depth':'multi_paragraph_local_to_global'}
    }

def main():
    d=lexicon()
    # Preflight every deliberate/review form before touching canonical data.
    all_forms=[]
    for x in R:
        all_forms.extend(x['target_forms']); all_forms.extend(f for f,_,_ in x['reviews'])
    missing=sorted({f for f in all_forms if norm(f) not in d})
    if missing: raise KeyError(f'missing cleared forms: {missing}')
    rows=[]
    if OUT.exists():
        rows=[json.loads(line) for line in OUT.read_text(encoding='utf-8').splitlines() if line.strip()]
    rows=[r for r in rows if r.get('unit')!=9]
    rows.extend(build(x,d) for x in R)
    rows.sort(key=lambda r:r.get('sequence',0))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
    print(f'wrote {len(R)} repaired Arabic B2 Unit 09 passages; total B2 rows={len(rows)}')

if __name__=='__main__': main()
