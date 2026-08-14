#!/usr/bin/env python3
"""Generate Arabic B1 Unit 03: technology in daily life.

Generation-first policy applies. Formal linguistic, pedagogical, coverage,
answer-key, and schema audits remain deferred to the final multi-pass phase.
"""
from __future__ import annotations
import json,re,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"reading"/"arabic"/"b1"/"passages.jsonl"
LEX=ROOT/"reading"/"lexicons"/"arabic.jsonl"
AR_DIAC=re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")

def norm(s):
    return AR_DIAC.sub("",unicodedata.normalize("NFC",s).replace("ـ","").strip())

def lexicon():
    out={}
    for line in LEX.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row=json.loads(line)
            out.setdefault(norm(row.get("form","")),row)
    return out

PREFERRED={
    "إلكتروني":"electronic; digital",
    "معلومة":"item of information; fact",
    "فيديو":"video",
    "محتوى":"content",
    "قناة":"channel",
    "منتدى":"forum; discussion space",
    "كمبيوتر":"computer",
    "خارجي":"external; outside",
    "مجاني":"free of charge",
    "تصحيح":"correction"
}

def target(form,text,by_form):
    src=by_form.get(norm(form))
    if not src:
        raise KeyError(f"missing target form: {form}")
    return {
        "id":f"ar-r{src['rank']}","form":form,"lemma":form,
        "part_of_speech":src.get("part_of_speech_source"),
        "intended_sense":PREFERRED[form],"register":"contemporary standard","variety":"MSA",
        "context_strategy":["scenario_resolution","contrast","cause_consequence"],
        "first_introduced":True,"exposures_in_text":max(1,text.count(form)),
        "source_lexicon":src.get("source_file"),"source_rank":src["rank"],"beyond_base":False
    }

def qa(items):
    qs=[];ans=[]
    for i,(typ,prompt,answer,ids) in enumerate(items,1):
        q={"id":f"q{i}","type":typ,"prompt":prompt,"answer_id":f"a{i}"}
        if ids:q["target_ids"]=ids
        qs.append(q)
        ans.append({"id":f"a{i}","question_id":f"q{i}","answer":answer,"explanation":""})
    if len(qs)!=10:raise ValueError("ten questions required")
    return qs,ans

R=[
{
"id":"ar-b1-u03-p01","sequence":13,"title":"ليس كل إشعار يحتاج إلى رد","passage_type":"instructional","genre":"explanatory story","domains":["personal","educational"],"topics":["notifications","attention","digital information"],
"text":"بدأت نور تستخدم نظامًا إلكترونيًا جديدًا في المدرسة يجمع الواجبات والرسائل ومواعيد الأنشطة في مكان واحد. في الأسبوع الأول أعجبها أن كل معلومة تصل بسرعة، لكنها لاحظت مشكلة لم تتوقعها: كان هاتفها يصدر إشعارًا عند كل تغيير صغير، حتى عندما يصحح المعلم كلمة في وصف الواجب أو يضيف سطرًا لا يغير المطلوب. صارت نور تفتح الهاتف عشرات المرات في المساء، ثم تعود إلى الدراسة وقد نسيت أين توقفت. في البداية ظنت أن المشكلة في كثرة العمل، لكن مراجعة يومها أظهرت شيئًا آخر. معظم المقاطعات لم تكن مرتبطة بمهمة عاجلة. لذلك غيرت إعدادات النظام الإلكتروني: أبقت إشعارات المواعيد الجديدة والرسائل المباشرة، وأوقفت التنبيه الفوري للتعديلات الصغيرة. كما خصصت وقتين في اليوم لقراءة بقية التحديثات. بعد أسبوع لم تقل كمية المعلومات التي تصل إليها، لكن طريقة وصول كل معلومة تغيرت. أصبحت تعرف الأخبار المهمة من غير أن تسمح لكل إشعار بأن يقرر متى تنظر إلى الهاتف. قالت إن الفائدة الحقيقية من التقنية ليست أن تعطينا معلومات أكثر فقط، بل أن تساعدنا على اختيار متى نحتاج إلى هذه المعلومات وكيف نستخدمها.",
"target_forms":["إلكتروني","معلومة"],
"reviews":[{"id":"ar-r919","form":"تطبيق","review_stage":"R4","representation":"other"},{"id":"ar-r576","form":"هاتف","review_stage":"R4","representation":"running_text"},{"id":"ar-r957","form":"متابعة","review_stage":"R4","representation":"other"}],
"grammar":[{"id":"ar-b1-not-all","role":"new","description":"ليس كل... / معظم... to qualify generalizations"}],
"discourse":[{"id":"b1-tech-attention-cause","role":"new","description":"distinguish information volume from interruption design as competing explanations"}],
"qa":[
("gist","ما المشكلة التي تكتشفها نور بعد استخدام النظام الجديد؟","الإشعارات الكثيرة تقطع تركيزها رغم أن كثيرًا منها غير عاجل.",None),
("literal_detail","أي إشعارات تبقيها نور فورية؟","المواعيد الجديدة والرسائل المباشرة.",None),
("inference","لماذا كان ظن نور الأول بأن العمل نفسه ازداد غير دقيق؟","لأن مراجعة يومها بينت أن كثيرًا من المقاطعات جاءت من تحديثات صغيرة لا من مهام جديدة.",None),
("cause_effect","كيف تغير الإعدادات سلوك نور من غير أن تقل المعلومات؟","تجمع التحديثات الأقل أهمية في أوقات محددة بدل مقاطعتها فورًا.",None),
("main_claim","ما الفكرة الأساسية في الفقرة الأخيرة؟","قيمة التقنية تعتمد أيضًا على التحكم في وقت وطريقة وصول المعلومات، لا على زيادتها فقط.",None),
("argument_relation","ما وظيفة ملاحظة أن «معظم المقاطعات لم تكن مرتبطة بمهمة عاجلة»؟","تقدم دليلًا يدعم تغيير تفسير المشكلة من كثرة العمل إلى تصميم الإشعارات.",None),
("contrast","ما الفرق بين كمية المعلومات وطريقة وصولها في تجربة نور؟","الكمية بقيت تقريبًا نفسها، بينما أصبحت طريقة الوصول أقل مقاطعة وأكثر تنظيمًا.",None),
("reference_resolution","إلى ماذا تشير «هذه المعلومات» في آخر جملة؟","إلى المعلومات والتحديثات التي يصل بها النظام الإلكتروني إلى نور.",None),
("single_word_definition","ما معنى «إلكتروني» في «نظام إلكتروني»؟","يعمل أو يقدم خدمته بوسائل رقمية أو أجهزة إلكترونية.",["ar-r1021"]),
("single_word_definition","ما معنى «معلومة»؟","حقيقة أو جزء محدد من المعرفة يمكن نقله أو استخدامه.",["ar-r1024"])
]},
{
"id":"ar-b1-u03-p02","sequence":14,"title":"فيديو قصير لا يعني شرحًا بسيطًا","passage_type":"reinforcement","genre":"learning-strategy article","domains":["educational","personal"],"topics":["video learning","content quality","verification"],
"text":"أراد سامر أن يتعلم طريقة جديدة لتنظيم البيانات في مشروع مدرسي، فبحث عن فيديو قصير يشرحها. وجد مقطعًا مدته أربع دقائق، وكان عنوانه يعد بشرح الموضوع «من البداية إلى النهاية». شاهد سامر الفيديو مرة واحدة وشعر أن المحتوى واضح، لأن المتحدث تحرك بسرعة وأظهر نتيجة ناجحة في النهاية. لكن عندما حاول تنفيذ الخطوات وحده، توقف في منتصف العمل. عاد إلى الفيديو فاكتشف أن صاحبه حذف مرحلتين اعتبرهما بديهيتين، ولم يوضح متى لا تعمل الطريقة. بحث سامر عن محتوى آخر، فوجد شرحًا أطول قليلًا يعرض مثالًا ناجحًا ومثالًا يفشل فيه الأسلوب نفسه، ثم يبين سبب الفرق. احتاج الشرح الثاني إلى وقت أكبر، لكنه ساعد سامر على إكمال المشروع من دون تقليد الخطوات حرفيًا. بعد التجربة كتب لزملائه أن طول الفيديو ليس مقياسًا كافيًا لجودة الشرح. قد يكون المحتوى القصير مفيدًا للمراجعة عندما يعرف المتعلم الأساس مسبقًا، لكنه قد يخفي افتراضات يحتاج إليها المبتدئ. أما الشرح الجيد، فيجب أن يسمح للمشاهد بأن يفهم لماذا تعمل الخطوات، لا أن يراها تعمل مرة واحدة فقط.",
"target_forms":["فيديو","محتوى"],
"reviews":[{"id":"ar-r935","form":"مشاريع","review_stage":"R4","representation":"running_text"},{"id":"ar-r902","form":"قدرة","review_stage":"R4","representation":"other"}],
"grammar":[{"id":"ar-b1-not-sufficient-measure","role":"new","description":"ليس مقياسًا كافيًا / قد... لكنه... for qualified evaluation"}],
"discourse":[{"id":"b1-tech-evaluate-explanation","role":"new","description":"evaluate instructional media by transfer and explanatory completeness rather than surface fluency"}],
"qa":[
("gist","لماذا لا يكفي الفيديو الأول سامرًا؟","لأنه يعرض نتيجة ناجحة بسرعة لكنه يحذف خطوات وشروطًا يحتاج إليها سامر عند التطبيق.",None),
("literal_detail","ما الذي يضيفه الشرح الثاني؟","يعرض مثالًا ناجحًا وآخر يفشل ويشرح سبب الفرق.",None),
("inference","لماذا بدا المحتوى الأول واضحًا أثناء المشاهدة رغم أنه لم يكن كافيًا للتطبيق؟","لأن سرعة العرض والنتيجة الناجحة أعطتا إحساسًا بالفهم من غير اختبار قدرة سامر على تنفيذ الخطوات وحده.",None),
("cause_effect","كيف يغير المثال الفاشل قيمة الشرح الثاني؟","يكشف حدود الطريقة والشروط التي تجعلها تنجح أو تفشل.",None),
("main_claim","ما معيار سامر الأفضل لتقييم الشرح؟","أن يساعده على فهم السبب والتطبيق المستقل، لا أن يكون قصيرًا أو سلسًا فقط.",None),
("argument_relation","ما دور محاولة سامر تنفيذ الخطوات وحده في الحجة؟","هي اختبار عملي يكشف الفرق بين الشعور بالفهم والقدرة على التطبيق.",None),
("contrast","متى قد يكون المحتوى القصير مفيدًا، ومتى يكون ناقصًا؟","يفيد في المراجعة لمن يعرف الأساس، وقد يكون ناقصًا للمبتدئ إذا حذف الافتراضات والخطوات.",None),
("reference_resolution","إلى ماذا يعود الضمير في «اعتبرهما بديهيتين»؟","إلى المرحلتين اللتين حذفتا من الشرح الأول.",None),
("single_word_definition","ما معنى «فيديو» في النص؟","مقطع مرئي مسجل يعرض صورًا متحركة وصوتًا أو شرحًا.",["ar-r1026"]),
("single_word_definition","ما معنى «محتوى» هنا؟","المادة أو المعلومات والأفكار التي يقدمها الشرح.",["ar-r1028"])
]},
{
"id":"ar-b1-u03-p03","sequence":15,"title":"سؤال واحد وثلاثة أنواع من الإجابة","passage_type":"interleaved","genre":"online discussion story","domains":["educational","social"],"topics":["forum","channels","source evaluation"],
"text":"واجهت هدى مشكلة في برنامج تستخدمه لإعداد عرض مدرسي، فكتبت سؤالًا في منتدى للطلاب. خلال ساعة وصلتها ثلاث إجابات مختلفة. الأولى كانت قصيرة جدًا: «غيّري هذا الإعداد وسيعمل كل شيء». الثانية أرسلت رابطًا إلى قناة تعليمية فيها شرح للمشكلة، أما الثالثة فسألت هدى عن نوع الجهاز وإصدار البرنامج قبل أن تقترح أي حل. جربت هدى النصيحة الأولى، فاختفت المشكلة مؤقتًا ثم عادت. شاهدت الشرح في القناة، لكنه كان يستخدم إصدارًا أقدم من البرنامج، لذلك لم تطابق القوائم ما تراه على الشاشة. عندها عادت إلى المنتدى وأجابت عن الأسئلة التي طرحها صاحب الرد الثالث. اتضح أن المشكلة مرتبطة بإعداد يتغير حسب إصدار البرنامج. أعطاها خطوات تناسب نسختها وشرح كيف تتأكد من النتيجة. نجح الحل، لكن هدى قالت إن أهم ما تعلمته لم يكن اسم الإعداد. تعلمت أن جودة الإجابة لا تقاس فقط بسرعة وصولها أو بثقة صاحبها. في المنتدى المفتوح قد تصل إجابات كثيرة، وفي القناة قد يوجد شرح مرتب، لكن على المستخدم أن يسأل أيضًا: هل هذا المصدر يتحدث عن الحالة نفسها؟ وما المعلومات التي طلبها قبل أن يعطي نصيحته؟",
"target_forms":["منتدى","قناة"],
"reviews":[{"id":"ar-r1024","form":"معلومة","review_stage":"R1","representation":"running_text"},{"id":"ar-r1026","form":"فيديو","review_stage":"R1","representation":"other"},{"id":"ar-r810","form":"نسخة","review_stage":"R4","representation":"running_text"}],
"grammar":[{"id":"ar-b1-source-fit-question","role":"new","description":"هل هذا المصدر يتحدث عن الحالة نفسها؟ as explicit source-fit evaluation"}],
"discourse":[{"id":"b1-tech-source-fit","role":"new","description":"compare answer speed, source organization, contextual fit, and diagnostic questioning"}],
"qa":[
("gist","لماذا تكون الإجابة الثالثة أنفع لهدى؟","لأن صاحبها يجمع معلومات عن حالتها أولًا ثم يقدم حلًا مناسبًا لإصدار البرنامج.",None),
("literal_detail","لماذا لا يطابق شرح القناة شاشة هدى؟","لأنه يستخدم إصدارًا أقدم من البرنامج.",None),
("inference","ماذا يكشف فشل النصيحة الأولى بعد نجاح مؤقت؟","أنها عالجت عرض المشكلة من غير أن تحدد السبب المناسب لحالة هدى.",None),
("cause_effect","كيف تؤثر أسئلة صاحب الرد الثالث في الحل؟","تحدد نوع الجهاز والإصدار فتسمح باختيار خطوات تناسب الحالة الفعلية.",None),
("main_claim","ما المعيار الذي يدافع عنه النص عند تقييم إجابة تقنية؟","مدى ملاءمة المصدر للحالة والأدلة التي يجمعها قبل اقتراح الحل، لا السرعة أو الثقة وحدهما.",None),
("argument_relation","لماذا يقارن النص بين المنتدى والقناة؟","ليبين أن لكل وسيلة ميزة، لكن شكل الوسيلة وحده لا يضمن صحة الإجابة أو ملاءمتها.",None),
("contrast","ما الفرق بين وظيفة المنتدى ووظيفة القناة في القصة؟","المنتدى يسمح بتبادل أسئلة وإجابات متعددة، بينما تقدم القناة شرحًا منظمًا في اتجاه واحد.",None),
("reference_resolution","إلى ماذا تشير «نسختها» في «خطوات تناسب نسختها»؟","إلى إصدار البرنامج الذي تستخدمه هدى.",None),
("single_word_definition","ما معنى «منتدى» هنا؟","مساحة نقاش يتبادل فيها المستخدمون الأسئلة والردود.",["ar-r1001"]),
("single_word_definition","ما معنى «قناة» في السياق؟","مساحة أو حساب ينشر مواد أو مقاطع إلى جمهور من المتابعين.",["ar-r1018"])
]},
{
"id":"ar-b1-u03-p04","sequence":16,"title":"الملف موجود، لكن ليس حيث توقعناه","passage_type":"transfer","genre":"problem-solution workplace story","domains":["work","personal"],"topics":["computer files","external storage","backup"],
"text":"في مركز تطوعي صغير كانت سلمى تعد نشرة أسبوعية على كمبيوتر مشترك. قبل موعد الإرسال بساعة فتحت المجلد المعتاد فلم تجد الصور النهائية. ظنت أولًا أن زميلها حذفها، لأن النسخة التي أمامها كانت تحتوي على ملفات قديمة فقط. اتصلت به، فأخبرها أنه حفظ الصور في قرص خارجي مساء اليوم السابق لأن مساحة الجهاز كانت شبه ممتلئة. كان القرص موجودًا في درج قريب، لكن سلمى لم تعرف أن الملفات انتقلت إليه. بعد أن وجدتها، أرسلت النشرة في الوقت المناسب، إلا أن الفريق ناقش ما حدث بدل اعتبار المشكلة منتهية. وجود نسخة على جهاز خارجي حماهم من فقدان الصور، لكنه خلق اعتمادًا على معلومة لم تكن مشتركة: أين توجد النسخة الأحدث؟ اتفقوا على أن يبقى القرص الخارجي للنسخ الاحتياطي، بينما تحفظ النسخة التي يعمل عليها الجميع في مجلد مشترك يحمل تاريخ آخر تعديل. كما أضافوا ملفًا صغيرًا يوضح مكان النسخ الأخرى. قالت سلمى إن المشكلة لم تكن في الكمبيوتر وحده ولا في القرص الخارجي؛ كانت في أن النظام التقني اعتمد على معرفة شخص واحد. عندما يصبح الوصول إلى ملف مهم مرتبطًا بذاكرة فرد، يمكن أن يكون الملف محفوظًا بأمان ومع ذلك يبدو مفقودًا لمن يحتاج إليه.",
"target_forms":["كمبيوتر","خارجي"],
"reviews":[{"id":"ar-r810","form":"نسخة","review_stage":"R4","representation":"running_text"},{"id":"ar-r612","form":"مؤسسة","review_stage":"R4","representation":"other"},{"id":"ar-r691","form":"موعد","review_stage":"R4","representation":"running_text"}],
"grammar":[{"id":"ar-b1-even-though-state","role":"new","description":"مع ذلك / بينما to contrast safe storage with poor discoverability"}],
"discourse":[{"id":"b1-tech-system-knowledge","role":"new","description":"separate data safety from shared knowledge about data location"}],
"qa":[
("gist","ما السبب الأعمق وراء صعوبة العثور على الصور؟","مكان النسخة الأحدث لم يكن معلومًا للفريق كله، بل اعتمد على معرفة زميل واحد.",None),
("literal_detail","لماذا نقل الزميل الصور إلى قرص خارجي؟","لأن مساحة الكمبيوتر كانت شبه ممتلئة.",None),
("inference","لماذا لا يعد وجود نسخة احتياطية وحده نظامًا كافيًا؟","لأن النسخة لا تفيد بسرعة إذا لم يعرف من يحتاجها أين توجد وأي نسخة هي الأحدث.",None),
("cause_effect","كيف يغير الفريق طريقة العمل بعد الحادثة؟","يبقي نسخة احتياطية خارجية ويحدد مجلدًا مشتركًا للنسخة الحالية مع توضيح أماكن النسخ.",None),
("main_claim","ما الفكرة العامة التي تستخلصها سلمى؟","النظام التقني الجيد يجب أن يشارك معرفة الوصول إلى الملفات، لا أن يحفظ الملفات فقط.",None),
("argument_relation","ما وظيفة عبارة «الملف محفوظ بأمان ومع ذلك يبدو مفقودًا»؟","تلخص المفارقة التي تفرق بين سلامة الملف وإمكانية العثور عليه.",None),
("contrast","ما الدور المختلف للمجلد المشترك والقرص الخارجي في النظام الجديد؟","المجلد المشترك للعمل الحالي والوصول الواضح، والقرص الخارجي للنسخ الاحتياطي.",None),
("reference_resolution","إلى ماذا يعود الضمير في «انتقلت إليه»؟","إلى القرص الخارجي.",None),
("single_word_definition","ما معنى «كمبيوتر»؟","جهاز إلكتروني يعالج البيانات ويشغل البرامج ويحفظ الملفات.",["ar-r1035"]),
("single_word_definition","ما معنى «خارجي» في «قرص خارجي»؟","منفصل عن الجهاز الأساسي أو موصول به من الخارج.",["ar-r1031"])
]},
{
"id":"ar-b1-u03-p05","sequence":17,"title":"مجاني لا يعني بلا مقابل","passage_type":"integration","genre":"opinion and case analysis","domains":["personal","educational"],"topics":["free services","automatic correction","tradeoffs"],
"text":"استخدمت مريم خدمة مجانية لمراجعة الكتابة. كانت تضع فقرتها في الموقع، وبعد ثوان تظهر اقتراحات تصحيح تحت الكلمات والجمل. في البداية قبلت معظم الاقتراحات من غير تفكير، لأن الخدمة كانت سريعة ولم تطلب منها دفع مال. بعد مدة لاحظت أن بعض التصحيحات تغير معنى الجملة أو تجعل الأسلوب أقل طبيعية. بدأت تقرأ كل تصحيح وتسأل: هل الخطأ حقيقي، أم أن البرنامج يفضل صياغة أخرى فقط؟ ثم قرأت صفحة الخدمة باهتمام أكبر. النسخة المجانية تعرض إعلانات، وبعض المزايا لا تعمل إلا بعد إنشاء حساب، كما أن الموقع يشرح كيف يعالج النصوص التي يرسلها المستخدمون. لم تعتبر مريم هذا سببًا لترك الخدمة فورًا، لكنها غيرت طريقة استخدامها. صارت ترسل جملًا قصيرة عندما تحتاج إلى فحص سريع، وتتجنب وضع معلومات شخصية، ولا تقبل أي تصحيح حتى تستطيع شرح سببه. قالت إن كلمة «مجاني» تصف السعر فقط، ولا تخبرنا بكل ما نعطيه مقابل الخدمة من وقت أو انتباه أو بيانات. وكذلك كلمة «تصحيح» لا تعني أن الاقتراح صحيح دائمًا؛ قد تكون الأداة مفيدة جدًا إذا بقي القرار الأخير عند الكاتب.",
"target_forms":["مجاني","تصحيح"],
"reviews":[{"id":"ar-r919","form":"تطبيق","review_stage":"R4","representation":"other"},{"id":"ar-r1024","form":"معلومة","review_stage":"R2","representation":"running_text"},{"id":"ar-r1028","form":"محتوى","review_stage":"R2","representation":"other"}],
"grammar":[{"id":"ar-b1-label-scope","role":"new","description":"X تصف جانبًا واحدًا ولا تخبرنا بكل... to limit category claims"}],
"discourse":[{"id":"b1-tech-hidden-tradeoff","role":"new","description":"analyze monetary price separately from attention, data, accuracy, and decision costs"}],
"qa":[
("gist","كيف تتغير طريقة مريم في استخدام خدمة التصحيح؟","تنتقل من قبول الاقتراحات تلقائيًا إلى فحصها وفهم سببها وتقليل ما ترسله من معلومات.",None),
("literal_detail","ما الذي تعرضه النسخة المجانية إضافة إلى خدمة المراجعة؟","تعرض إعلانات، وبعض المزايا تتطلب حسابًا.",None),
("inference","لماذا لا تترك مريم الخدمة رغم اكتشاف حدودها؟","لأنها ما زالت مفيدة عند الاستخدام الواعي، والمشكلة في الاعتماد عليها بلا تقييم لا في وجودها وحده.",None),
("cause_effect","ما الذي يجعل مريم تتوقف عن قبول كل اقتراح؟","ملاحظتها أن بعض الاقتراحات تغير المعنى أو الأسلوب بدل إصلاح خطأ حقيقي.",None),
("main_claim","ما المقصود بقولها إن «مجاني» تصف السعر فقط؟","عدم دفع المال لا يعني غياب تكاليف أو تبادلات أخرى مثل الانتباه والبيانات والوقت.",None),
("argument_relation","كيف تدعم تجربة التصحيحات الخاطئة حجة النص؟","تثبت أن اسم الوظيفة «تصحيح» لا يضمن أن كل اقتراح صحيح ويجب قبوله.",None),
("contrast","ما الفرق بين استخدام الأداة كمساعد واستخدامها كصاحب قرار؟","المساعد يقدم اقتراحات يفحصها الكاتب، أما صاحب القرار فيفرض تغييرات من غير فهم أو مراجعة.",None),
("reference_resolution","إلى ماذا تشير «هذا» في «لم تعتبر مريم هذا سببًا»؟","إلى ما عرفته عن الإعلانات والحساب ومعالجة النصوص وحدود الخدمة.",None),
("single_word_definition","ما معنى «مجاني»؟","متاح من غير دفع سعر مالي مباشر.",["ar-r1008"]),
("single_word_definition","ما معنى «تصحيح» هنا؟","اقتراح لإزالة خطأ أو تحسين صياغة يعتقد النظام أنها غير صحيحة.",["ar-r1032"])
]},
{
"id":"ar-b1-u03-p06","sequence":18,"title":"أسبوع رقمي أكثر هدوءًا","passage_type":"fluency","genre":"reflective synthesis","domains":["personal","educational","work"],"topics":["digital habits","source evaluation","files","tool choice"],
"text":"في نهاية الشهر لاحظت نور أن الأدوات الرقمية التي تستخدمها لم تكن مشكلة واحدة تحتاج إلى حل واحد. في المدرسة قللت المقاطعات عندما غيرت طريقة وصول الإشعارات، لا عندما أغلقت النظام كله. وعندما احتاج سامر إلى تعلم مهارة، اكتشف أن الشرح القصير ليس أفضل دائمًا، وأن التجربة المستقلة تكشف ما إذا كان قد فهم فعلًا. أما هدى فتعلمت من سؤال تقني أن الإجابة السريعة قد تكون أقل فائدة من إجابة تبدأ بجمع معلومات عن الحالة. وفي العمل التطوعي ظهر درس مختلف: حفظ الملف بأمان لا يكفي إذا كان مكان النسخة الأحدث معروفًا لشخص واحد فقط. حتى أدوات مراجعة الكتابة احتاجت إلى حكم المستخدم؛ الاقتراح المفيد يصبح مشكلة إذا قُبل لمجرد أن البرنامج قدمه بثقة. جمعت نور هذه الأمثلة في ملاحظة واحدة: التقنية توسع ما نستطيع فعله، لكنها تنقل إلينا أيضًا قرارات جديدة. علينا أن نقرر ما الذي يستحق إشعارًا فوريًا، وأي شرح يناسب هدفنا، وأي مصدر يطابق حالتنا، وكيف نجعل المعلومات مشتركة، ومتى نثق باقتراح آلي. لذلك لم تحاول نور أن تصبح أقل استخدامًا للتقنية في كل شيء. كان هدفها أن يصبح استخدامها أكثر قصدًا: أداة مناسبة، في وقت مناسب، مع سؤال واضح عن الفائدة والحدود.",
"target_forms":[],
"reviews":[{"id":"ar-r1021","form":"إلكتروني","review_stage":"R2","representation":"running_text"},{"id":"ar-r1024","form":"معلومة","review_stage":"R2","representation":"running_text"},{"id":"ar-r1026","form":"فيديو","review_stage":"R2","representation":"other"},{"id":"ar-r1028","form":"محتوى","review_stage":"R2","representation":"other"},{"id":"ar-r1001","form":"منتدى","review_stage":"R2","representation":"other"},{"id":"ar-r1018","form":"قناة","review_stage":"R2","representation":"other"},{"id":"ar-r1035","form":"كمبيوتر","review_stage":"R2","representation":"other"},{"id":"ar-r1031","form":"خارجي","review_stage":"R2","representation":"other"},{"id":"ar-r1008","form":"مجاني","review_stage":"R2","representation":"other"},{"id":"ar-r1032","form":"تصحيح","review_stage":"R2","representation":"other"}],
"grammar":[{"id":"ar-b1-u03-cumulative","role":"integration","description":"recycle qualified claims, cause contrasts, and tool-purpose evaluation"}],
"discourse":[{"id":"b1-tech-synthesis","role":"integration","description":"synthesize several technology cases into a general principle without erasing differences among them"}],
"qa":[
("gist","ما الفكرة التي تجمع تجارب الوحدة؟","الأدوات الرقمية تفيد أكثر عندما يفهم المستخدم غرضها وحدودها ويتخذ قرارات واعية حول استخدامها.",None),
("literal_detail","ما الذي خفض مقاطعات نور في المدرسة؟","تغيير طريقة وصول الإشعارات بدل إغلاق النظام كله.",None),
("inference","لماذا يرفض النص فكرة وجود «حل واحد» لكل مشكلات التقنية؟","لأن الأمثلة تكشف مشكلات مختلفة: انتباه، شرح، ملاءمة مصدر، مشاركة ملفات، وحكم على اقتراحات.",None),
("cause_effect","كيف تكشف التجربة المستقلة جودة شرح تعليمي؟","تبين هل يستطيع المتعلم تطبيق الفكرة من دون الاعتماد على مشاهدة المثال فقط.",None),
("main_claim","ما المقصود بالاستخدام «الأكثر قصدًا» في النهاية؟","اختيار الأداة والوقت والطريقة وفق هدف واضح مع الانتباه إلى الفائدة والحدود.",None),
("argument_relation","كيف تخدم الأمثلة الخمسة الجملة العامة عن «قرارات جديدة»؟","كل مثال يوضح قرارًا مختلفًا تخلقه التقنية بدل أن تكون أداة تعمل وحدها بلا حكم بشري.",None),
("contrast","ما الفرق بين تقليل استخدام التقنية وتحسين طريقة استخدامها؟","الأول يخفض الاستخدام عمومًا، أما الثاني فيختار متى وكيف ولماذا تستخدم كل أداة.",None),
("reference_resolution","إلى ماذا تشير «هذه الأمثلة» في «جمعت نور هذه الأمثلة»؟","إلى حالات الإشعارات والتعلم بالفيديو والإجابات التقنية والملفات وأدوات مراجعة الكتابة.",None),
("summary","لخص ثلاثة مبادئ عملية يطرحها النص.","التحكم في المقاطعات، اختبار ملاءمة الشرح والمصدر، وإبقاء الحكم البشري وتنظيم الوصول إلى المعلومات جزءًا من استخدام الأداة.",None),
("inference","لماذا تنتهي الوحدة بسؤال عن «الفائدة والحدود» معًا؟","لأن الحكم الجيد يحتاج إلى معرفة ما تساعد عليه الأداة وما لا تضمنه في الوقت نفسه.",None)
]}
]

def build(x,by_form):
    qs,ans=qa(x["qa"])
    text=x["text"].strip()
    return {
        "id":x["id"],"language":"ar","cefr":"B1","unit":3,"sequence":x["sequence"],"revision":1,
        "title":x["title"],"passage_type":x["passage_type"],"genre":x["genre"],"domains":x["domains"],"topics":x["topics"],
        "text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r"[.!؟](?:\s|$)",text))),
        "estimated_known_token_coverage":0,
        "new_lexical_targets":[target(f,text,by_form) for f in x["target_forms"]],
        "review_lexical_targets":x["reviews"],"grammar_targets":x["grammar"],"discourse_targets":x["discourse"],
        "questions":qs,"answer_key":ans,
        "speed_training":{"timed":x["passage_type"]=="fluency","benchmark_eligible":False,"comprehension_gate":0.8,
            "new_word_policy":"none" if x["passage_type"]=="fluency" else "controlled",
            "notes":"B1 generation-stage passage; formal fluency/coverage decision deferred to final audit."},
        "quality":{"status":"draft","linguistic_review":"pending","pedagogical_review":"pending","coverage_check":"pending",
            "answer_key_check":"pending","schema_check":"pending","fact_check":"not_required",
            "notes":["High-quality B1 generation-stage draft; formal audits deferred to the final multi-pass review phase."]},
        "paired_text_group":None,"prerequisites":["Arabic A1-A2 generation corpus","Arabic B1 Units 01-02 generation corpus"],
        "difficulty_notes_internal":"B1 Unit 03 generation draft: technology in daily life with motives, tradeoffs, evidence, source fit, and multi-sentence inference.",
        "reader_tags":["unit_role:"+x["passage_type"],"generation_batch","b1"],
        "complexity_profile":{"mean_sentence_length":None,"median_sentence_length":None,"clause_count":None,"subordination_count":None,
            "coordination_count":None,"connective_diversity":None,"lexical_diversity":None,"reference_chain_max_distance":None,
            "multiword_expression_count":None,"morphology_notes":"B1 generation-stage MSA with qualified claims and longer reference chains.",
            "inference_depth":"multi_sentence_local_to_global"}
    }

def main():
    by_form=lexicon()
    rows=[]
    if OUT.exists():
        rows=[json.loads(line) for line in OUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows=[r for r in rows if r.get("unit")!=3]
    rows.extend(build(x,by_form) for x in R)
    rows.sort(key=lambda r:r.get("sequence",0))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text("\n".join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+"\n",encoding="utf-8")
    print(f"wrote {len(R)} Arabic B1 Unit 03 passages; total B1 rows={len(rows)}")

if __name__=="__main__":main()
