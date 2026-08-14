#!/usr/bin/env python3
"""Generate Arabic B1 Unit 01: work, study, and decisions.

Generation-first policy applies. The texts deliberately raise discourse complexity
from A2: competing constraints, motives, evidence, consequences, and decisions
that must be inferred across multiple sentences. Formal audits remain deferred.
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

def qa(items):
    qs=[];ans=[]
    for i,(typ,prompt,answer,ids) in enumerate(items,1):
        q={"id":f"q{i}","type":typ,"prompt":prompt,"answer_id":f"a{i}"}
        if ids:q["target_ids"]=ids
        qs.append(q);ans.append({"id":f"a{i}","question_id":f"q{i}","answer":answer,"explanation":""})
    if len(qs)!=10:raise ValueError("ten questions required")
    return qs,ans

PREFERRED={
"قرار":"decision","أولوية":"priority","التزام":"commitment; obligation","مهارة":"skill",
"تجربة":"experience; trial","نتيجة":"result; outcome","سبب":"reason; cause","خيار":"option; choice",
"مسؤولية":"responsibility","هدف":"goal; objective","توازن":"balance","مقارنة":"comparison"
}

def lexicon():
    by_form={}
    for line in LEX.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r=json.loads(line);by_form.setdefault(norm(r.get("form", "")),r)
    return by_form

def targets(forms,text,by_form):
    out=[]
    for form in forms:
        src=by_form.get(norm(form))
        if not src: continue
        out.append({
            "id":f"ar-r{src['rank']}","form":form,"lemma":form,
            "part_of_speech":src.get("part_of_speech_source"),"intended_sense":PREFERRED[form],
            "register":"contemporary standard","variety":"MSA",
            "context_strategy":["scenario_resolution","cause_consequence"],
            "first_introduced":True,"exposures_in_text":max(1,text.count(form)),
            "source_lexicon":src.get("source_file"),"source_rank":src["rank"],"beyond_base":False
        })
    return out

R=[
{
"id":"ar-b1-u01-p01","sequence":1,"title":"دورة مفيدة أم أسبوع مزدحم؟","passage_type":"instructional","genre":"decision narrative","domains":["educational","personal"],"topics":["study","course selection","tradeoffs"],
"text":"رأت نور إعلانًا عن دورة قصيرة في الكتابة الرقمية تستمر ستة أسابيع. كان موضوعها قريبًا من الأشياء التي تريد تعلمها، ووقت الدرس مناسبًا من حيث المبدأ، لكن الأسابيع الستة نفسها كانت مزدحمة بمشروع مدرسي والتزامات عائلية. في البداية فكرت أن التسجيل فرصة لا ينبغي أن تضيع، لأن الدورة لا تُقدَّم إلا مرتين في السنة. ثم نظرت إلى جدولها بطريقة أكثر واقعية. لم يكن السؤال: هل الدورة مفيدة؟ بل: هل هي الأولوية الصحيحة الآن؟ كتبت نور ما ستكسبه من الدورة، ثم كتبت ما قد يتأثر إذا أضافت ثلاث ساعات أسبوعيًا للدروس والواجبات. لاحظت أنها ستضطر إلى تقليل الوقت المخصص لمشروع كانت مسؤولة عن جزء أساسي منه. تحدثت مع المعلمة المسؤولة عن المشروع، ولم تطلب منها أن تتخذ القرار مكانها، بل سألتها متى ستكون أسابيع العمل الأكثر ضغطًا. اتضح أن الضغط سيبلغ أعلى مستوى في منتصف الدورة. لذلك قررت نور ألا تسجل هذه المرة، ووضعت موعد الدورة التالية في تقويمها. شعرت ببعض الخيبة، لكنها لم تعتبر القرار رفضًا للتعلم. قالت: أحيانًا يكون الشيء جيدًا، ومع ذلك لا يكون الخيار المناسب في الوقت الحالي. إذا كانت الأولوية واضحة، يصبح قول «ليس الآن» أسهل من محاولة فعل كل شيء ثم أداء كل شيء بصورة أضعف.",
"target_forms":["قرار","أولوية"],
"reviews":[{"id":"ar-r661","form":"دورة","review_stage":"R3","representation":"running_text"},{"id":"ar-r659","form":"تنظيم","review_stage":"R3","representation":"other"},{"id":"ar-r682","form":"اختيار","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-b1-good-but-not-now","role":"new","description":"concession: a good opportunity may still be wrong now"},{"id":"ar-b1-if-added-consequence","role":"new","description":"conditional consequences across competing commitments"}],
"discourse":[{"id":"b1-tradeoff-decision","role":"new","description":"weigh benefits against opportunity cost before making a decision"}],
"qa":[
("gist","ما المشكلة الأساسية التي تواجه نور؟","تريد دورة مفيدة، لكن وقتها يتعارض مع مشروع والتزامات أخرى.",None),
("literal_detail","لماذا تبدو الدورة فرصة نادرة نسبيًا؟","لأنها تقدم مرتين فقط في السنة.",None),
("motive","لماذا تسأل نور معلمة المشروع عن أسابيع الضغط بدل أن تطلب منها اختيار القرار؟","لأن نور تريد معلومات تساعدها على القرار مع بقاء المسؤولية عنها شخصيًا.",None),
("inference","ماذا تقصد نور بقولها إن السؤال ليس «هل الدورة مفيدة؟»؟","تقصد أن فائدة الشيء وحدها لا تكفي؛ يجب مقارنتها بالأولويات والوقت والآثار على التزامات أخرى.",None),
("cause_effect","ما المعلومة التي تدفع نور في النهاية إلى عدم التسجيل؟","أن أعلى ضغط في المشروع سيقع في منتصف فترة الدورة.",None),
("main_claim","ما الفكرة التي يدافع عنها النص من خلال تجربة نور؟","قد يكون التخلي المؤقت عن فرصة جيدة قرارًا عقلانيًا عندما تتعارض مع أولوية أهم.",None),
("reference_resolution","إلى ماذا يشير «هذه المرة»؟","إلى الدورة الحالية ذات الأسابيع الستة، لا إلى رفض النوع من التعلم نهائيًا.",None),
("contrast","ما الفرق بين «ليس الآن» و«لا أريد هذا أبدًا» في النص؟","الأول يؤجل فرصة مناسبة إلى وقت أفضل، والثاني يرفضها نهائيًا.",None),
("summary","لخص عملية اتخاذ القرار التي تتبعها نور.","تحدد الفائدة، تقارنها بتأثير الوقت على التزامات أخرى، تجمع معلومة عن الضغط، ثم تؤجل الدورة إلى موعد أنسب.",None),
("inference","لماذا قد تكون محاولة فعل كل شيء نتيجة أسوأ؟","لأن الموارد الزمنية محدودة وقد تنخفض جودة العمل في الدورة والمشروع معًا.",None)
]},
{
"id":"ar-b1-u01-p02","sequence":2,"title":"مسؤولية في مشروع جماعي","passage_type":"reinforcement","genre":"group-project narrative","domains":["educational"],"topics":["group work","responsibility","communication"],
"text":"عملت نور مع ثلاثة طلاب على مشروع يحتاج إلى عرض شفهي وتقرير مكتوب. اتفقوا في البداية على تقسيم المهام بالتساوي، لكن بعد أسبوع بدأ أحد الأعضاء، سامر، يتأخر في إرسال الجزء المسؤول عنه. في المرة الأولى أكمل الآخرون العمل من دونه حتى لا يتوقف المشروع. تكرر الأمر مرة ثانية، فشعرت هدى أن الحل السريع بدأ يتحول إلى عادة غير عادلة. اقترحت أن يأخذوا جزء سامر نهائيًا ويكملوا المشروع بأنفسهم. لم توافق نور مباشرة. قالت إن مسؤولية المجموعة هي تسليم المشروع، لكن مسؤولية كل عضو أيضًا أن يؤدي دوره أو يشرح مبكرًا لماذا لا يستطيع. قبل تغيير التقسيم، تحدثت المجموعة مع سامر. عرفوا أن لديه التزامًا عائليًا مؤقتًا في المساء وأنه لم يكن يريد استخدام ذلك كعذر. اتفقوا على تعديل واحد: سيأخذ جزءًا يمكن إنجازه في المدرسة، بينما تتولى هدى مهمة تحتاج إلى العمل في البيت. لم يختف الضغط تمامًا، لكن سامر بدأ يسلم أجزاءه في الموعد. في نهاية المشروع ناقشوا ما حدث. قالت هدى إنها كانت محقة في أن المشكلة لا يمكن أن تستمر، لكنها اعترفت بأن حذف سامر من المسؤولية من غير سؤال لم يكن الحل الوحيد. أما نور فقالت إن العمل الجماعي لا يعني أن الجميع يحمل العبء نفسه في كل لحظة؛ يعني أن المسؤوليات واضحة، وأن أي تغيير فيها يُناقش قبل أن يصبح الصمت مشكلة أكبر.",
"target_forms":["مسؤولية","التزام"],
"reviews":[{"id":"ar-r935","form":"مشاريع","review_stage":"R3","representation":"running_text"},{"id":"ar-r246","form":"مجموعة","review_stage":"R4","representation":"running_text"},{"id":"ar-r957","form":"متابعة","review_stage":"R3","representation":"other"}],
"grammar":[{"id":"ar-b1-responsibility-concession","role":"new","description":"two simultaneous responsibilities held in tension"},{"id":"ar-b1-before-reassigning","role":"new","description":"before changing roles, seek explanation and renegotiate"}],
"discourse":[{"id":"b1-group-conflict-resolution","role":"new","description":"move from repeated failure to discussion, contextual explanation, and negotiated role change"}],
"qa":[
("gist","كيف تحل المجموعة مشكلة تأخر سامر؟","تتحدث معه وتعيد توزيع المهام بحيث يستطيع إنجاز دوره في وقت مناسب.",None),
("literal_detail","ما السبب الذي يجعل سامر يتأخر؟","لديه التزام عائلي مؤقت في المساء.",None),
("motive","لماذا لا توافق نور فورًا على أخذ مهمة سامر منه؟","لأنها تريد فهم سبب المشكلة ومناقشة المسؤولية قبل إلغاء دوره.",None),
("inference","لماذا كان إكمال العمل عنه في المرة الأولى حلًا قصير المدى فقط؟","لأنه منع التأخير مرة واحدة لكنه لم يعالج سبب تكرار المشكلة أو يوضح المسؤوليات.",None),
("cause_effect","ما أثر نقل سامر إلى مهمة يمكن إنجازها في المدرسة؟","يبدأ في تسليم أجزائه في الموعد بصورة أفضل.",None),
("main_claim","ما تصور نور للعمل الجماعي؟","أن تكون المسؤوليات واضحة وقابلة للنقاش والتعديل، لا أن يحمل الجميع العبء نفسه حرفيًا في كل وقت.",None),
("contrast","في ماذا كانت هدى محقة وفي ماذا تغير رأيها؟","كانت محقة أن المشكلة لا يمكن تجاهلها، لكنها رأت أن استبعاد سامر من المهمة لم يكن الحل الوحيد.",None),
("reference_resolution","إلى ماذا تشير «ذلك» في فكرة أن سامر لم يرد استخدامه عذرًا؟","إلى التزامه العائلي الذي يؤثر في وقته.",None),
("summary","لخص مراحل حل الخلاف.","لاحظوا التكرار، ناقشوا المشكلة، عرفوا السبب، أعادوا توزيع المهام، ثم راقبوا النتيجة وراجعوا التجربة.",None),
("inference","لماذا يمكن أن يصبح الصمت مشكلة أكبر؟","لأن التأخير والغموض يستمران من غير أن يعرف الآخرون السبب أو يتفقوا على تعديل واضح.",None)
]},
{
"id":"ar-b1-u01-p03","sequence":3,"title":"مهارة لا تظهر في الشهادة","passage_type":"interleaved","genre":"student profile and reflection","domains":["educational","professional"],"topics":["skills","experience","evidence"],
"text":"عندما طُلب من طلاب الصف إعداد ملف بسيط عن مهاراتهم، بدأت نور بكتابة المواد الدراسية التي حصلت فيها على درجات جيدة. ثم لاحظت أن القائمة لا تشرح أشياء كثيرة تعرف أنها تستطيع فعلها. مثلًا، خلال فعالية في مركز الحي ساعدت في توجيه الزوار، وفي مشروع التصوير نظمت العمل على عدة أسابيع، وفي فريق المدرسة اضطرت إلى شرح فكرة لزملاء لم يفهموها في البداية. سألت المعلمة: هل هذه خبرة فعلية، أم أنها مجرد نشاطات صغيرة؟ أجابت المعلمة أن المهارة لا تحتاج دائمًا إلى وظيفة رسمية حتى تظهر، لكن من الأفضل أن يشرح الطالب الموقف وما فعله والنتيجة بدل أن يكتب كلمة عامة مثل «التواصل» أو «التنظيم». أعادت نور كتابة الملف. بدل «أجيد العمل مع الناس»، كتبت مثالًا عن الفعالية: كان عند المدخل زوار يسألون عن أماكن مختلفة، فتعلمت أن تستمع إلى السؤال وتقدم اتجاهًا واضحًا أو تطلب مساعدة من المنظم إذا لم تكن متأكدة. وبدل «أجيد إدارة الوقت»، شرحت كيف قسمت مشروعًا طويلًا إلى خطوات وعدلت الخطة عندما تأخر جزء منه. عندما قرأت الملف الجديد شعرت أنه أقل مبالغة وأكثر إقناعًا. قالت: المهارة ليست صفة أضعها بجانب اسمي؛ هي شيء يجب أن أستطيع إظهار أثره في موقف حقيقي.",
"target_forms":["مهارة"],
"reviews":[{"id":"ar-r780","form":"خبرة","review_stage":"R3","representation":"running_text"},{"id":"ar-r934","form":"خطوة","review_stage":"R3","representation":"running_text"},{"id":"ar-r659","form":"تنظيم","review_stage":"R4","representation":"running_text"}],
"grammar":[{"id":"ar-b1-instead-of-general-claim","role":"new","description":"بدل general claim, give situation-action-result evidence"},{"id":"ar-b1-not-necessarily-formal","role":"new","description":"لا تحتاج دائمًا إلى... حتى..."}],
"discourse":[{"id":"b1-skill-evidence","role":"new","description":"support a self-description with concrete situation, action, and outcome evidence"}],
"qa":[
("gist","كيف تغير نور ملف مهاراتها؟","تستبدل الكلمات العامة بأمثلة توضح الموقف وما فعلته والنتيجة.",None),
("literal_detail","ما المثال الذي تستخدمه لإظهار قدرتها على التواصل؟","مساعدة الزوار في فعالية مركز الحي وتوجيههم أو طلب مساعدة عندما لا تعرف.",None),
("motive","لماذا تسأل نور هل نشاطاتها الصغيرة تُعد خبرة؟","لأنها كانت تربط الخبرة في ذهنها بالعمل الرسمي أو الإنجاز الكبير.",None),
("inference","لماذا يعتبر الملف الثاني أقل مبالغة؟","لأنه لا يدعي صفات عامة بلا دليل، بل يبين حدود المواقف وما فعلته نور فعلًا.",None),
("main_claim","ما الفكرة الرئيسية عن المهارة؟","المهارة تصبح مقنعة عندما يمكن إظهارها من خلال أفعال ونتائج في مواقف حقيقية.",None),
("cause_effect","كيف يساعد مثال مشروع التصوير على إثبات إدارة الوقت؟","يبين أنها قسمت العمل إلى خطوات وعدلت الخطة عند التأخير.",None),
("contrast","ما الفرق بين كتابة «أجيد التواصل» وشرح موقف الفعالية؟","الأولى ادعاء عام، والثانية دليل عملي يوضح كيف استخدمت التواصل.",None),
("reference_resolution","إلى ماذا تشير «هذه» في سؤال نور عن الخبرة؟","إلى نشاطات مثل الفعالية ومشروع التصوير وشرح الأفكار للزملاء.",None),
("summary","لخص نصيحة المعلمة لنور.","لا تكتفي باسم المهارة؛ اشرح موقفًا محددًا، ما فعلته فيه، وما النتيجة.",None),
("inference","ماذا يعني قول نور إن للمهارة «أثرًا» في موقف حقيقي؟","أن استخدام المهارة يجب أن يغير أو يحسن شيئًا يمكن وصفه، لا أن تبقى مجرد كلمة.",None)
]},
{
"id":"ar-b1-u01-p04","sequence":4,"title":"تجربة طريقة دراسة جديدة","passage_type":"transfer","genre":"self-experiment study narrative","domains":["educational","personal"],"topics":["study methods","evidence","results"],
"text":"كانت نور تراجع دروسها عادة بقراءة الملاحظات أكثر من مرة. شعرت أن الطريقة مريحة لأنها تجعل المعلومات مألوفة، لكنها لم تكن متأكدة هل تساعدها على التذكر من غير الكتاب. قررت أن تجري تجربة صغيرة لمدة أسبوعين بدل تغيير كل عاداتها دفعة واحدة. اختارت فصلًا واحدًا فقط. في الأسبوع الأول درست بالطريقة المعتادة، ثم أغلقت الكتاب وحاولت كتابة ما تتذكره. في الأسبوع الثاني قرأت المادة مرة واحدة، وبعد ذلك استخدمت أسئلة قصيرة واختبرت نفسها من غير النظر إلى الإجابات إلا بعد المحاولة. لم تكن النتيجة مثالية؛ أخطأت كثيرًا في البداية وشعرت أن الطريقة الثانية أصعب. لكنها عندما أعادت الاختبار بعد يومين تذكرت تفاصيل أكثر مما توقعت. لم تعتبر نور هذا دليلًا قاطعًا أن الطريقة الثانية أفضل في كل مادة، لأن التجربة كانت قصيرة وعلى فصل واحد. مع ذلك رأت نتيجة تستحق المتابعة. قررت استخدام الأسئلة في فصلين آخرين ومقارنة الأداء مرة ثانية. قالت لصديقتها: أكثر شيء فاجأني أن الطريقة التي تبدو أسهل أثناء الدراسة ليست بالضرورة الطريقة التي تجعلني أتذكر أكثر لاحقًا. لذلك أحاول أن أقيس النتيجة، لا شعوري أثناء المراجعة فقط.",
"target_forms":["تجربة","نتيجة"],
"reviews":[{"id":"ar-r828","form":"تدريب","review_stage":"R3","representation":"other"},{"id":"ar-r948","form":"تفكير","review_stage":"R3","representation":"other"},{"id":"ar-r957","form":"متابعة","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-b1-not-conclusive","role":"new","description":"not enough evidence to generalize beyond a small experiment"},{"id":"ar-b1-easier-not-necessarily-better","role":"new","description":"ليس بالضرورة linking subjective ease and later result"}],
"discourse":[{"id":"b1-study-method-experiment","role":"new","description":"compare two study methods with delayed outcome while limiting the claim to available evidence"}],
"qa":[
("gist","ما الذي تختبره نور؟","تختبر هل الاسترجاع بالأسئلة يساعدها على التذكر أكثر من إعادة قراءة الملاحظات.",None),
("literal_detail","كم تستمر التجربة الأولى؟","أسبوعين.",None),
("motive","لماذا تختار نور فصلًا واحدًا فقط؟","حتى تجرب تغييرًا محدودًا يمكن مقارنته من غير أن تغير كل عاداتها دفعة واحدة.",None),
("inference","لماذا تبدو الطريقة الثانية أسوأ في البداية رغم أنها قد تكون مفيدة؟","لأن الاختبار يكشف ما لا تعرفه ويشعرها بالصعوبة، بينما إعادة القراءة تعطي إحساسًا أكبر بالألفة.",None),
("cause_effect","ما النتيجة التي تشجع نور على المتابعة؟","تذكرها تفاصيل أكثر بعد يومين عند استخدام الأسئلة والاسترجاع.",None),
("main_claim","ما الفكرة التي تستخلصها نور بحذر؟","سهولة الدراسة أثناء الجلسة لا تضمن تذكرًا أفضل لاحقًا، لذلك يجب النظر إلى النتيجة.",None),
("contrast","لماذا لا تقول نور إن الطريقة الثانية أفضل في كل مادة؟","لأن تجربتها قصيرة ومحدودة بفصل واحد، فلا تكفي للتعميم.",None),
("reference_resolution","إلى ماذا تشير «هذا» في «لم تعتبر نور هذا دليلًا قاطعًا»؟","إلى النتيجة الأفضل التي ظهرت بعد يومين في التجربة المحدودة.",None),
("summary","لخص تصميم تجربة نور وقرارها التالي.","تقارن إعادة القراءة بالاختبار الذاتي في فصل واحد، ترى نتيجة مشجعة، ثم توسع التجربة إلى فصلين آخرين.",None),
("inference","ما الذي يجعل موقف نور أقرب إلى التفكير التجريبي؟","أنها تغير عاملًا محدودًا، تقارن نتيجة لاحقة، وتتجنب تعميمًا أكبر من البيانات المتاحة.",None)
]},
{
"id":"ar-b1-u01-p05","sequence":5,"title":"خيار عمل يناسب الدراسة","passage_type":"checkpoint","genre":"part-time work decision narrative","domains":["professional","educational","personal"],"topics":["part-time work","schedule","priorities"],
"text":"وجدت هدى إعلانين عن عمل جزئي في عطلة نهاية الأسبوع. الأول في متجر قريب من بيتها، وعدد الساعات فيه أكبر، لذلك كان الدخل المتوقع أعلى. أما الثاني ففي مكتبة أبعد قليلًا، لكنه يوفر ساعات أقل ومرونة أكبر في تغيير وردية واحدة خلال فترة الاختبارات. كانت هدى تحتاج إلى بعض الدخل، لكنها كانت في الوقت نفسه تستعد لامتحان مهم بعد شهرين. في البداية مالت إلى المتجر لأن الفرق المالي واضح. ثم حاولت حساب ما يعنيه كل خيار على مدى ثمانية أسابيع. إذا عملت الساعات الأطول، فسيبقى لها وقت أقل للمراجعة يومي السبت والأحد، وهما اليومان اللذان تعتمد عليهما عادة لتعويض ما لم تنجزه خلال الأسبوع. تحدثت مع شخص يعمل في المكتبة وسألته عن المسؤوليات الحقيقية، لا عن المرونة فقط. أخبرها أن العمل يتطلب ترتيب الكتب وخدمة الزوار وبعض الأعمال الهادئة، وأن ضغط الزبائن أقل في الصباح. بعد المقارنة اختارت المكتبة، رغم أن الدخل أقل. لم تقل إن المال غير مهم؛ قالت إن هدفها الحالي يجمع بين دخل معقول وحماية وقت الدراسة. وضعت لنفسها شرطًا: إذا وجدت بعد شهر أن الساعات القليلة نفسها تؤثر بقوة في الدراسة، فستعيد تقييم القرار بدل أن تتمسك به لمجرد أنها بدأت.",
"target_forms":["خيار"],
"reviews":[{"id":"ar-r682","form":"اختيار","review_stage":"R3","representation":"running_text"},{"id":"ar-r836","form":"مناسب","review_stage":"R3","representation":"other"},{"id":"ar-r691","form":"موعد","review_stage":"R4","representation":"other"},{"id":"ar-r242","form":"هدف","review_stage":"R4","representation":"running_text"}],
"grammar":[{"id":"ar-b1-tradeoff-not-denial","role":"new","description":"choosing one value without claiming the competing value is unimportant"},{"id":"ar-b1-reevaluate-if","role":"new","description":"conditional re-evaluation after new experience"}],
"discourse":[{"id":"b1-work-study-choice","role":"integration","description":"compare pay, flexibility, responsibilities, and study cost before choosing work"}],
"qa":[
("gist","لماذا تختار هدى عمل المكتبة؟","لأنه يوازن بين دخل مقبول ومرونة أكبر وحماية وقت الدراسة.",None),
("literal_detail","ما ميزة المتجر الأساسية؟","ساعات أكثر ودخل متوقع أعلى.",None),
("motive","لماذا تسأل هدى موظف المكتبة عن المسؤوليات الفعلية؟","حتى تعرف طبيعة العمل نفسها، لا أن تبني القرار على المرونة في الجدول وحدها.",None),
("inference","لماذا تؤثر ساعات نهاية الأسبوع في الدراسة أكثر من عددها الظاهر فقط؟","لأن هدى تعتمد على تلك الأيام لتعويض الدراسة التي لم تنجزها خلال الأسبوع.",None),
("cause_effect","ما الذي يجعل خيار المكتبة أكثر توافقًا مع هدفها الحالي؟","الساعات الأقل والمرونة خلال الاختبارات مع دخل ما زال معقولًا.",None),
("main_claim","ما المبدأ الذي يظهر في قرار هدى؟","القرار الجيد يقارن قيمة مالية بآثارها على هدف آخر مهم بدل تعظيم عامل واحد فقط.",None),
("contrast","هل اختيار المكتبة يعني أن هدى ترى المال غير مهم؟","لا، هي تريد دخلًا معقولًا لكنها لا تريد أن يضر هدف الدراسة.",None),
("reference_resolution","إلى ماذا تشير «الساعات القليلة نفسها»؟","إلى ساعات العمل الأقل في المكتبة.",None),
("summary","لخص عوامل المقارنة بين الوظيفتين.","تقارن الدخل، عدد الساعات، المرونة، طبيعة المسؤوليات، ووقت الدراسة الذي قد يتأثر.",None),
("inference","لماذا تضع هدى شرط إعادة التقييم بعد شهر؟","لأنها تعرف أن القرار مبني على توقعات، والتجربة الفعلية قد تكشف أثرًا مختلفًا.",None)
]},
{
"id":"ar-b1-u01-p06","sequence":6,"title":"كيف أتخذ قرارًا أفضل؟","passage_type":"fluency","genre":"connected decision reflection","domains":["personal","educational","professional"],"topics":["decisions","evidence","tradeoffs","review"],
"text":"خلال الأشهر الماضية واجهت نور وهدى قرارات لم يكن فيها خيار مثالي. أحيانًا كانت الفرصة مفيدة، مثل دورة جيدة، لكنها تتعارض مع أولوية أهم في الوقت نفسه. وفي العمل الجماعي ظهر أن المسؤولية لا تُحل دائمًا بتقسيم متساوٍ جامد؛ قد يحتاج الفريق إلى فهم التزام مؤقت وتعديل الأدوار مع بقاء التوقعات واضحة. عندما فكرت نور في مهاراتها، اكتشفت أن الكلمة العامة لا تكفي، وأن الخبرة تصبح أكثر إقناعًا عندما تستطيع وصف موقف وفعل ونتيجة. وحتى في الدراسة لم تعتمد على شعورها بأن طريقة معينة سهلة، بل أجرت تجربة صغيرة ونظرت إلى ما تذكرته لاحقًا. أما هدى فقارنت خيارين للعمل ولم تجعل الدخل العامل الوحيد؛ نظرت إلى الوقت والمرونة وهدف الدراسة أيضًا. هذه المواقف مختلفة، لكن بينها طريقة مشتركة. يبدأ القرار بسؤال واضح، ثم يحتاج إلى معلومات مرتبطة بالسؤال، لا إلى كل معلومة ممكنة. بعد ذلك تُقارن النتائج المحتملة والأولويات، ويُتخذ خيار يمكن مراجعته إذا ظهرت خبرة جديدة. لا يعني ذلك أن القرار سيكون بلا خسارة أو شك. أحيانًا يظل الشخص غير متأكد من أفضل نتيجة. لكن التفكير بهذه الطريقة يمنع سببًا شائعًا للقرار الضعيف: التركيز على أول فائدة نراها وتجاهل ما سيتأثر بها في بقية الحياة.",
"target_forms":[],
"reviews":[{"id":"ar-r661","form":"دورة","review_stage":"R4","representation":"running_text"},{"id":"ar-r682","form":"اختيار","review_stage":"R4","representation":"running_text"},{"id":"ar-r780","form":"خبرة","review_stage":"R4","representation":"running_text"},{"id":"ar-r828","form":"تدريب","review_stage":"R4","representation":"other"},{"id":"ar-r648","form":"متأكد","review_stage":"R4","representation":"running_text"},{"id":"ar-r242","form":"هدف","review_stage":"R4","representation":"running_text"}],
"grammar":[{"id":"ar-b1-u01-cumulative","role":"integration","description":"concession, conditionals, evidence limits, tradeoffs, and revisable decisions"}],
"discourse":[{"id":"b1-decision-fluency","role":"integration","description":"synthesize decision principles across study, teamwork, skill evidence, experiments, and work"}],
"qa":[
("gist","ما الفكرة الرئيسية في النص؟","القرارات الجيدة تقارن الأولويات والآثار والأدلة، ولا تعتمد على أول فائدة أو شعور فقط.",None),
("main_claim","ما الطريقة المشتركة بين المواقف المختلفة؟","تحديد السؤال، جمع معلومات مرتبطة به، مقارنة النتائج والأولويات، ثم اتخاذ قرار قابل للمراجعة.",None),
("inference","لماذا لا يحتاج الشخص إلى «كل معلومة ممكنة»؟","لأن المعلومات المفيدة هي التي تؤثر في السؤال والخيارات؛ كثرة المعلومات غير المرتبطة قد لا تحسن القرار.",None),
("argument_relation","كيف يدعم مثال الدراسة الفكرة العامة؟","يبين أن الإحساس بسهولة الطريقة ليس كافيًا، وأن نتيجة لاحقة تقدم دليلًا أفضل لاتخاذ قرار الدراسة.",None),
("argument_relation","كيف يختلف مثال الفريق عن مثال الدورة لكنه يخدم الفكرة نفسها؟","الفريق يتعلق بتعديل مسؤوليات، والدورة بتعارض أولويات، لكن كليهما يحتاج إلى فهم القيود قبل اختيار الحل.",None),
("contrast","ما الفرق بين قرار قابل للمراجعة وقرار متردد بلا نهاية؟","الأول يُتخذ بناء على المعلومات الحالية مع شرط واضح للمراجعة، أما الثاني فلا يصل إلى فعل محدد.",None),
("reference_resolution","إلى ماذا تشير «بها» في «ما سيتأثر بها» في النهاية؟","إلى الفائدة أو الخيار الأول الذي يركز عليه الشخص.",None),
("summary","لخص نموذج القرار الذي يقترحه النص.","عرّف السؤال، اجمع الأدلة المهمة، قارن الفوائد والتكاليف والأولويات، اختر، ثم راجع إذا ظهرت معلومات جديدة.",None),
("inference","لماذا يقبل النص وجود بعض الخسارة أو الشك؟","لأن القرارات الواقعية قد تتضمن مفاضلات ومعلومات ناقصة، ولا يشترط القرار الجيد نتيجة مثالية مؤكدة.",None),
("synthesis","ما الخطأ المشترك الذي تحاول الأمثلة الخمسة تجنبه؟","الحكم من عامل واحد فقط—مثل فائدة الدورة أو التساوي أو اسم المهارة أو سهولة الدراسة أو الدخل—من دون النظر إلى السياق والنتائج الأخرى.",None)
]}
]
def main():
    by_form=lexicon(); rows=[]
    for x in R:
        qs,ans=qa(x["qa"]);text=x["text"]
        rows.append({"id":x["id"],"language":"ar","cefr":"B1","unit":1,"sequence":x["sequence"],"revision":1,"title":x["title"],"passage_type":x["passage_type"],"genre":x["genre"],"domains":x["domains"],"topics":x["topics"],"text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r"[.!؟](?:\s|$)",text))),"estimated_known_token_coverage":0,"new_lexical_targets":targets(x["target_forms"],text,by_form),"review_lexical_targets":x["reviews"],"grammar_targets":x["grammar"],"discourse_targets":x["discourse"],"questions":qs,"answer_key":ans,"speed_training":{"timed":x["passage_type"]=="fluency","benchmark_eligible":False,"comprehension_gate":0.8,"new_word_policy":"none" if x["passage_type"]=="fluency" else "controlled","notes":"B1 generation-stage passage; formal fluency/coverage decision deferred to final audit."},"quality":{"status":"draft","linguistic_review":"pending","pedagogical_review":"pending","coverage_check":"pending","answer_key_check":"pending","schema_check":"pending","fact_check":"not_required","notes":["High-quality B1 generation-stage draft; formal audits deferred to the final multi-pass review phase."]},"paired_text_group":None,"prerequisites":["Arabic A1-A2 generation corpus"],"difficulty_notes_internal":"B1 Unit 01 generation draft: multi-sentence inference, motives, tradeoffs, evidence, and revisable decisions.","reader_tags":["unit_role:"+x["passage_type"],"generation_batch","b1"],"complexity_profile":{"mean_sentence_length":None,"median_sentence_length":None,"clause_count":None,"subordination_count":None,"coordination_count":None,"connective_diversity":None,"lexical_diversity":None,"reference_chain_max_distance":None,"multiword_expression_count":None,"morphology_notes":"B1 generation-stage draft; wider clause linking, concession, reported reasoning, and comparison.","inference_depth":"multi_sentence"}})
    if len(rows)!=6 or any(len(r["questions"])!=10 or len(r["answer_key"])!=10 for r in rows):raise SystemExit("B1 Unit01 generation contract failed")
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    print("generated Arabic B1 Unit 01: six passages, sixty questions, sixty answers")
if __name__=="__main__":main()
