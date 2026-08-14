#!/usr/bin/env python3
"""Generate Arabic A2 Unit 08: nature and environment.

Generation-stage only: content is written carefully, while formal audit fields
remain pending for the later multi-pass review phase.
"""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"reading"/"arabic"/"a2"/"passages.jsonl"
LEX=ROOT/"reading"/"lexicons"/"arabic.jsonl"
T={
969:("منطقة","area; region",["scenario_resolution"]),
822:("مواد","materials; substances",["category_relation"]),
850:("استخدام","use; usage",["cause_consequence"]),
993:("طاقة","energy",["cause_consequence"]),
968:("نمو","growth",["cause_consequence"]),
794:("مجتمع","community; society",["category_relation"]),
}
def qa(items):
    qs=[];ans=[]
    for i,(typ,prompt,answer,ids) in enumerate(items,1):
        q={"id":f"q{i}","type":typ,"prompt":prompt,"answer_id":f"a{i}"}
        if ids:q["target_ids"]=ids
        qs.append(q);ans.append({"id":f"a{i}","question_id":f"q{i}","answer":answer,"explanation":""})
    if len(qs)!=10:raise ValueError("ten questions required")
    return qs,ans
R=[
{
"id":"ar-a2-u08-p01","sequence":43,"title":"منطقة تحتاج إلى تنظيف","passage_type":"instructional","genre":"community clean-up narrative","domains":["public","personal"],"topics":["environment","park","waste"],
"text":"يمر عدد كبير من سكان الحي بحديقة صغيرة تقع بين المدرسة والمركز الرياضي. في أحد الأسابيع لاحظت نور أن منطقة قرب المقاعد أصبحت مليئة بأكواب ورقية وعلب فارغة، بينما بقيت بقية الحديقة نظيفة نسبيًا. اقترح نادي المدرسة يومًا قصيرًا للتنظيف، لكنه طلب من المشاركين ألا يجمعوا الأشياء عشوائيًا فقط. أحضر المشرف أكياسًا منفصلة وشرح أن المواد الموجودة في النفايات ليست كلها من النوع نفسه؛ فبعضها ورق، وبعضها بلاستيك أو معدن. قسم الطلاب أنفسهم إلى مجموعات وبدأوا من المنطقة الأكثر ازدحامًا. أثناء العمل لاحظوا أن معظم النفايات كانت قريبة من مكان لا توجد فيه سلة واضحة. بعد التنظيف كتبوا ملاحظة للمركز البلدي يقترحون فيها وضع سلة إضافية قرب المقاعد. قالت نور: تنظيف المنطقة يحل المشكلة اليوم، لكن معرفة أنواع المواد ومكان تجمعها قد تساعد على تقليل المشكلة لاحقًا. وافق المشرف وقال إن النشاط البيئي الجيد لا يكتفي بإزالة ما نراه؛ يحاول أيضًا فهم لماذا ظهر في هذا المكان.",
"new":[969,822],
"reviews":[{"id":"ar-r974","form":"تحقيق","review_stage":"R3","representation":"other"},{"id":"ar-r924","form":"تأثير","review_stage":"R3","representation":"other"},{"id":"ar-r246","form":"مجموعة","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-not-all-same","role":"new","description":"ليست كلها من النوع نفسه / بعضها... وبعضها..."},{"id":"ar-a2-not-only-but-understand","role":"new","description":"لا يكتفي بـ... بل يحاول أيضًا..."}],
"discourse":[{"id":"a2-environment-problem-pattern","role":"new","description":"move from visible litter to material categories and a likely location-based cause"}],
"qa":[
("gist","ما الذي يفعله الطلاب إلى جانب تنظيف الحديقة؟","يصنفون المواد ويحاولون فهم سبب تجمع النفايات قرب المقاعد.",None),
("literal_detail","أين كانت النفايات أكثر؟","في المنطقة القريبة من المقاعد.",["ar-r969"]),
("vocabulary_in_context","ماذا تعني «منطقة» في النص؟","جزء محدد من الحديقة أو الحي.",["ar-r969"]),
("vocabulary_in_context","ماذا تعني «مواد» عندما يتحدث المشرف عن النفايات؟","الأنواع التي صُنعت منها الأشياء مثل الورق والبلاستيك والمعدن.",["ar-r822"]),
("inference","لماذا يقترح الطلاب سلة إضافية قرب المقاعد؟","لأن معظم النفايات تجمعت هناك ولا توجد سلة واضحة قريبة.",None),
("single_word_definition","ما معنى «منطقة»؟","جزء محدد من مكان أو إقليم.",["ar-r969"]),
("single_word_definition","ما معنى «مواد»؟","أشياء أو مواد أولية يتكون منها شيء أو تستخدم لغرض ما.",["ar-r822"]),
("cause_effect","كيف يمكن للتصنيف أن يفيد أكثر من الجمع العشوائي؟","يكشف أنواع النفايات ويساعد على التفكير في طريقة التعامل معها وتقليلها.",None),
("cloze_transfer","أكمل: هذه _____ هادئة من الحديقة.","منطقة",["ar-r969"]),
("cloze_transfer","أكمل: صنع الطلاب النموذج من _____ بسيطة معاد استخدامها.","مواد",["ar-r822"])
]},
{
"id":"ar-a2-u08-p02","sequence":44,"title":"كم نستخدم من الطاقة؟","passage_type":"reinforcement","genre":"school energy-observation narrative","domains":["educational","public"],"topics":["energy","school","resource use"],
"text":"بدأت مدرسة نور أسبوعًا لملاحظة استخدام الكهرباء، لا بهدف إيقاف الأجهزة الضرورية، بل لفهم أين يمكن تقليل الاستخدام من غير أن يتأثر العمل. في اليوم الأول مر الطلاب على الصفوف بعد انتهاء الدوام ولاحظوا أن بعض المصابيح بقيت مضاءة في غرف فارغة. كما وجدوا حاسوبين يعملان مع أن أحدًا لم يكن يستخدمهما. شرحت المعلمة أن الطاقة التي تصل إلى المدرسة تُستخدم في الإضاءة والتدفئة والأجهزة، وأن تقليل الاستخدام غير الضروري يوفر المال والطاقة معًا. لم تطلب من الطلاب إطفاء كل شيء بأنفسهم، بل سجلوا الملاحظات وأرسلوها إلى المسؤول عن المبنى. في الأسبوع التالي وُضعت ملصقات صغيرة قرب الأبواب تذكر المعلمين والطلاب بفحص الضوء قبل الخروج. لاحظت نور أن الفكرة بسيطة، لكن تأثيرها يعتمد على تكرار السلوك كل يوم. قالت: لا نحتاج إلى جعل الغرفة مظلمة أو باردة حتى نوفر الطاقة؛ نحتاج أولًا إلى أن نميز الاستخدام الضروري من الاستخدام الذي لا يفيد أحدًا.",
"new":[850,993],
"reviews":[{"id":"ar-r969","form":"منطقة","review_stage":"R1","representation":"other"},{"id":"ar-r822","form":"مواد","review_stage":"R1","representation":"other"},{"id":"ar-r924","form":"تأثير","review_stage":"R2","representation":"running_text"}],
"grammar":[{"id":"ar-a2-use-noun","role":"new","description":"استخدام + noun / تقليل الاستخدام"},{"id":"ar-a2-without-affecting","role":"new","description":"من غير أن يتأثر..."}],
"discourse":[{"id":"a2-resource-observation","role":"new","description":"identify avoidable resource use without confusing conservation with stopping necessary use"}],
"qa":[
("gist","ما هدف أسبوع الكهرباء؟","فهم أين يمكن تقليل استخدام الكهرباء غير الضروري من دون تعطيل العمل.",None),
("literal_detail","ما الشيئان اللذان وجد الطلاب أنهما يعملان بلا حاجة واضحة؟","بعض المصابيح وحاسوبان في غرف فارغة.",None),
("vocabulary_in_context","ماذا يعني «استخدام الكهرباء»؟","الطريقة والقدر الذي تُستهلك به الكهرباء في الإضاءة والأجهزة وغيرها.",["ar-r850"]),
("vocabulary_in_context","ماذا تعني «طاقة» هنا؟","القدرة التي تشغل الإضاءة والتدفئة والأجهزة الكهربائية.",["ar-r993"]),
("inference","لماذا لا تطلب المعلمة إطفاء كل شيء؟","لأن بعض الاستخدام ضروري، والهدف هو تقليل الهدر لا إيقاف العمل.",None),
("single_word_definition","ما معنى «استخدام»؟","استعمال شيء لغرض معين.",["ar-r850"]),
("single_word_definition","ما معنى «طاقة»؟","قدرة تستخدم لإحداث عمل مثل تشغيل الأجهزة أو التدفئة.",["ar-r993"]),
("cause_effect","كيف تساعد الملصقات الصغيرة؟","تذكر الناس بتكرار سلوك بسيط يقلل الاستخدام غير الضروري يوميًا.",None),
("cloze_transfer","أكمل: نحاول تقليل _____ الورق عندما لا نحتاج إليه.","استخدام",["ar-r850"]),
("cloze_transfer","أكمل: تحتاج الأجهزة الكهربائية إلى _____.","طاقة",["ar-r993"])
]},
{
"id":"ar-a2-u08-p03","sequence":45,"title":"حديقة تنمو ببطء","passage_type":"interleaved","genre":"community-garden observation narrative","domains":["public","educational"],"topics":["garden","growth","observation"],
"text":"خصص مركز الحي قطعة أرض صغيرة لحديقة يشترك في رعايتها السكان. زرعت نور ومجموعة من الطلاب أعشابًا وبعض الخضروات، ثم وضعوا بطاقات تحمل تاريخ الزراعة. في الأسبوع الأول لم يظهر تغير كبير، فظن بعض الطلاب أن البذور لم تنجح. طلبت منهم المشرفة الانتظار وتسجيل ما يرونه كل عدة أيام. بعد أسبوعين بدأت نباتات صغيرة تظهر في أكثر من مكان. قارنت نور الصور التي التقطتها في البداية بالصور الجديدة ولاحظت أن النمو لا يحدث بالسرعة نفسها لكل النباتات. كان الجزء القريب من السور أقل نموًا، لأن الشمس تصل إليه مدة أقصر. بدل أن ينقلوا النباتات فورًا، راقبوا المنطقة أسبوعًا آخر وسجلوا ساعات الضوء تقريبًا. أظهرت الملاحظات فرقًا واضحًا. قالت المشرفة إن نمو النبات يعتمد على أكثر من عامل، مثل الضوء والماء ونوع النبات. تعلمت نور أن عدم رؤية نتيجة سريعة لا يعني أن المشروع فشل؛ بعض التغيرات تحتاج إلى وقت ومتابعة حتى تصبح واضحة.",
"new":[968],
"reviews":[{"id":"ar-r850","form":"استخدام","review_stage":"R1","representation":"other"},{"id":"ar-r993","form":"طاقة","review_stage":"R1","representation":"other"},{"id":"ar-r913","form":"أظهرت","review_stage":"R3","representation":"running_text"},{"id":"ar-r957","form":"متابعة","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-growth-comparison","role":"new","description":"أقل/أكثر نموًا and unequal rates"},{"id":"ar-a2-does-not-mean-failure","role":"new","description":"لا يعني أن..."}],
"discourse":[{"id":"a2-slow-change-evidence","role":"new","description":"track gradual change across repeated observations and compare possible factors"}],
"qa":[
("gist","ما الذي تتعلمه نور من الحديقة؟","أن النمو قد يكون بطيئًا ومختلفًا بين الأماكن، ويحتاج إلى ملاحظة عبر الوقت.",None),
("literal_detail","لماذا كان النمو أقل قرب السور؟","لأن الشمس تصل إلى ذلك الجزء مدة أقصر.",None),
("vocabulary_in_context","ماذا يعني «النمو» في النص؟","زيادة حجم النبات وتطوره مع مرور الوقت.",["ar-r968"]),
("inference","لماذا لا ينقلون النباتات فورًا؟","لأنهم يريدون جمع ملاحظات إضافية قبل أن يقرروا أن المكان هو سبب المشكلة.",None),
("cause_effect","كيف تساعد الصور في فهم التغير؟","تسمح بمقارنة شكل النباتات في أوقات مختلفة ورؤية النمو تدريجيًا.",None),
("single_word_definition","ما معنى «نمو»؟","زيادة أو تطور تدريجي في الحجم أو القدرة أو العدد.",["ar-r968"]),
("contrast","هل كل النباتات تنمو بالسرعة نفسها؟","لا، يختلف النمو حسب عوامل متعددة.",["ar-r968"]),
("reference_resolution","إلى ماذا تشير «ذلك الجزء»؟","إلى الجزء القريب من السور.",None),
("cloze_transfer","أكمل: يحتاج _____ النبات إلى ماء وضوء مناسبين.","نمو",["ar-r968"]),
("inference","ما الخطأ في الحكم على المشروع بعد أسبوع واحد فقط؟","قد يكون الوقت قصيرًا جدًا لرؤية نمو واضح، فيصبح الحكم مبكرًا.",None)
]},
{
"id":"ar-a2-u08-p04","sequence":46,"title":"يوم على الشاطئ بعد العاصفة","passage_type":"transfer","genre":"coastal observation narrative","domains":["public","personal"],"topics":["sea","litter","environmental impact"],
"text":"بعد ليلة كثيرة الرياح ذهبت نور مع أسرتها إلى شاطئ قريب من البحر. كان الرمل رطبًا، وعلى جزء من الشاطئ ظهرت أغصان وقطع خشب حملتها المياه. لكنهم لاحظوا أيضًا أكياسًا بلاستيكية وعلبًا لا تبدو طبيعية في المكان. قالت نور إن العاصفة ربما نقلت بعض هذه الأشياء من منطقة أخرى. قرأت لوحة عند المدخل تطلب من الزوار عدم لمس الأشياء الحادة وإبلاغ العاملين إذا وجدوا شيئًا خطرًا. أثناء المشي جمعت الأسرة بعض النفايات الخفيفة في كيس، لكنها تركت المواد الكبيرة أو غير المعروفة للعاملين. تحدثوا عن تأثير ما يتركه الناس في الشوارع والحدائق؛ فقد تنتقل بعض النفايات مع الماء والرياح حتى تصل إلى البحر. قالت نور: عندما أرى كيسًا على الشاطئ لا أعرف دائمًا أين بدأ طريقه، لكنني أفهم أن البيئة مترابطة. ما نتركه في مكان قد يظهر أثره في مكان آخر بعد وقت.",
"new":[],
"reviews":[{"id":"ar-r835","form":"بحر","review_stage":"R3","representation":"running_text"},{"id":"ar-r822","form":"مواد","review_stage":"R2","representation":"running_text"},{"id":"ar-r969","form":"منطقة","review_stage":"R2","representation":"running_text"},{"id":"ar-r924","form":"تأثير","review_stage":"R3","representation":"running_text"},{"id":"ar-r899","form":"أثر","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-may-have-moved","role":"new","description":"ربما + past cause inference"},{"id":"ar-a2-place-to-place","role":"new","description":"من مكان... إلى مكان آخر..."}],
"discourse":[{"id":"a2-environment-connection","role":"new","description":"infer how material can move between locations and create effects elsewhere"}],
"qa":[
("gist","ما الفكرة التي تفهمها نور من الشاطئ؟","أن النفايات قد تنتقل بين الأماكن وأن أثرها البيئي لا يبقى في موقع واحد.",None),
("literal_detail","ما الذي حملته المياه طبيعيًا إلى الشاطئ؟","أغصانًا وقطع خشب.",None),
("inference","لماذا لا تجمع الأسرة كل شيء بنفسها؟","لأن بعض المواد قد تكون كبيرة أو حادة أو مجهولة ويجب أن يتعامل معها العاملون.",None),
("cause_effect","كيف قد تصل النفايات من الشوارع إلى البحر؟","قد تحملها المياه أو الرياح من منطقة إلى أخرى.",None),
("summary","لخص ما تلاحظه الأسرة بعد العاصفة.","ترى مواد طبيعية ونفايات بشرية على الشاطئ وتفكر في كيفية انتقالها وتأثيرها.",None),
("single_word_definition","ما معنى «تأثير» في هذا السياق؟","النتيجة التي يسببها تصرف أو مادة في البيئة.",["ar-r924"]),
("contrast","أيهما من البيئة الطبيعية في النص: غصن أم كيس بلاستيكي؟","الغصن.",None),
("reference_resolution","إلى ماذا تشير «هذه الأشياء» بعد ذكر العاصفة؟","إلى بعض النفايات والأشياء التي ظهرت على الشاطئ.",None),
("inference","لماذا تقول نور إن البيئة مترابطة؟","لأن المواد والآثار يمكن أن تنتقل من مكان إلى آخر عبر الماء والرياح.",None),
("grammar_function","ماذا تعبر «ربما» في تفسير نور؟","عن احتمال غير مؤكد لسبب انتقال الأشياء.",None)
]},
{
"id":"ar-a2-u08-p05","sequence":47,"title":"مشروع صغير للمجتمع","passage_type":"checkpoint","genre":"community environmental project","domains":["public","educational"],"topics":["community","environment","project"],
"text":"بعد أن نفذ طلاب المدرسة عدة أنشطة بيئية، اقترحوا مشروعًا يمكن أن يستفيد منه المجتمع كله بدل أن يبقى داخل المدرسة. اختاروا إعداد خريطة بسيطة تظهر أماكن تعبئة زجاجات الماء، وصناديق جمع بعض المواد القابلة لإعادة الاستخدام، والمساحات الخضراء العامة. لم يريدوا أن تكون الخريطة مجرد قائمة؛ أرادوا أن توضح كيف يستطيع الشخص استخدام هذه الأماكن في حياته اليومية. قسموا العمل بين مجموعات: فريق يجمع العناوين، وفريق يتأكد من أوقات فتح الأماكن، وفريق يصمم النسخة الرقمية. تحدثوا أيضًا مع سكان مختلفين قبل نشرها، لأن احتياجات المجتمع ليست واحدة. قال شخص كبير في السن إن الخط الصغير يصعب قراءته، واقترح أحد الآباء إضافة أماكن قريبة من المدارس. عدل الطلاب التصميم بناءً على هذه الملاحظات. عند إطلاق الخريطة قال المدير إن نجاح المشروع لا يعتمد فقط على عدد الأشخاص الذين يفتحونها أول مرة، بل على أن تبقى معلوماتها صحيحة ومفيدة. اقترحت نور متابعة التغييرات كل شهرين حتى يظل المشروع صالحًا للاستخدام.",
"new":[794],
"reviews":[{"id":"ar-r968","form":"نمو","review_stage":"R1","representation":"other"},{"id":"ar-r850","form":"استخدام","review_stage":"R2","representation":"running_text"},{"id":"ar-r822","form":"مواد","review_stage":"R2","representation":"running_text"},{"id":"ar-r935","form":"مشاريع","review_stage":"R3","representation":"running_text"},{"id":"ar-r957","form":"متابعة","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-community-whole","role":"new","description":"المجتمع كله / احتياجات المجتمع"},{"id":"ar-a2-not-just-list","role":"review","description":"لا... مجرد... بل..."}],
"discourse":[{"id":"a2-community-design","role":"integration","description":"design a practical resource using information from different community users and plan maintenance"}],
"qa":[
("gist","ما هدف مشروع الطلاب؟","إنشاء خريطة بيئية عملية يستفيد منها سكان المجتمع في حياتهم اليومية.",None),
("literal_detail","ما أنواع الأماكن التي تظهرها الخريطة؟","أماكن تعبئة الماء وصناديق جمع بعض المواد والمساحات الخضراء.",None),
("vocabulary_in_context","ماذا يعني «المجتمع» في النص؟","مجموعة السكان والأشخاص الذين يعيشون ويستخدمون الخدمات في المنطقة.",["ar-r794"]),
("inference","لماذا يسأل الطلاب سكانًا مختلفين قبل النشر؟","لأن احتياجات المستخدمين تختلف وقد تكشف الملاحظات مشكلات في التصميم.",None),
("cause_effect","كيف تغير ملاحظات السكان الخريطة؟","تكبر بعض العناصر وتضاف أماكن مفيدة قرب المدارس وتتحسن سهولة الاستخدام.",None),
("single_word_definition","ما معنى «مجتمع»؟","مجموعة أشخاص يعيشون أو يتفاعلون ضمن مكان أو نظام اجتماعي مشترك.",["ar-r794"]),
("reference_resolution","إلى ماذا تشير «معلوماتها» في الجملة الأخيرة تقريبًا؟","إلى معلومات الخريطة عن الأماكن والمواعيد.",None),
("inference","لماذا تحتاج الخريطة إلى متابعة بعد نشرها؟","لأن المواقع والمواعيد قد تتغير، والمعلومات القديمة تجعلها أقل فائدة.",None),
("cloze_transfer","أكمل: شارك أفراد _____ في اقتراح حلول للحي.","المجتمع",["ar-r794"]),
("contrast","هل نجاح المشروع يعتمد على الإطلاق فقط؟","لا، يعتمد أيضًا على بقاء المعلومات صحيحة ومفيدة مع الوقت.",None)
]},
{
"id":"ar-a2-u08-p06","sequence":48,"title":"ملاحظة البيئة قبل الحكم عليها","passage_type":"fluency","genre":"connected environment reflection","domains":["public","educational","personal"],"topics":["environment","resources","community","review"],
"text":"أصبحت نور تنظر إلى المشكلات البيئية الصغيرة بطريقة أكثر تنظيمًا. إذا رأت نفايات في منطقة من الحديقة، لا تكتفي بجمعها؛ تنظر إلى أنواع المواد وإلى المكان الذي تتجمع فيه. وفي المدرسة تفكر في استخدام الطاقة: ما الذي نحتاج إليه فعلًا، وما الذي يعمل من غير فائدة؟ وعندما تتابع نمو النباتات، تعرف أن النتيجة قد تحتاج إلى أسابيع قبل أن تظهر، وأن الضوء والماء والمكان عوامل يمكن مقارنتها. حتى الشاطئ يذكرها بأن ما يحدث في مكان قد يصل أثره إلى مكان آخر، لأن الماء والرياح ينقلان الأشياء. وتعلمت أيضًا أن المشروع البيئي لا يصبح مفيدًا للمجتمع لمجرد أن فكرته جيدة؛ يجب أن يناسب الأشخاص الذين سيستخدمونه وأن تبقى معلوماته حديثة. لذلك تبدأ نور بالملاحظة، ثم تجمع معلومات بسيطة، وتقارن ما يحدث، وبعد ذلك تقترح تغييرًا محددًا يمكن متابعته. هي لا تتوقع أن تحل نشاطات صغيرة كل المشكلات، لكنها ترى أنها طريقة عملية لفهم جزء من البيئة والتصرف فيه بصورة أفضل.",
"new":[],
"reviews":[{"id":"ar-r969","form":"منطقة","review_stage":"R2","representation":"running_text"},{"id":"ar-r822","form":"مواد","review_stage":"R2","representation":"running_text"},{"id":"ar-r850","form":"استخدام","review_stage":"R2","representation":"running_text"},{"id":"ar-r993","form":"طاقة","review_stage":"R2","representation":"running_text"},{"id":"ar-r968","form":"نمو","review_stage":"R2","representation":"running_text"},{"id":"ar-r794","form":"مجتمع","review_stage":"R1","representation":"running_text"}],
"grammar":[{"id":"ar-a2-u08-cumulative","role":"integration","description":"recycle environmental observation, resource use, gradual change, interconnected effects, and community design"}],
"discourse":[{"id":"a2-environment-fluency","role":"integration","description":"high-coverage cumulative environment reading from observation to practical response"}],
"qa":[
("gist","ما الفكرة الرئيسية في النص؟","نور تتعامل مع القضايا البيئية الصغيرة بالملاحظة وجمع المعلومات والمقارنة ثم اقتراح تغيير قابل للمتابعة.",None),
("literal_detail","ما الذي تفكر فيه عند استخدام الطاقة؟","تمييز الاستخدام الضروري من الاستخدام الذي يعمل بلا فائدة.",["ar-r850","ar-r993"]),
("inference","لماذا قد تنتظر نور أسابيع قبل الحكم على نمو النباتات؟","لأن النمو تدريجي وقد لا تظهر الفروق سريعًا.",["ar-r968"]),
("summary","لخص خطوات نور في التعامل مع مشكلة بيئية صغيرة.","تلاحظ المشكلة، تجمع معلومات، تقارن الأسباب والآثار، ثم تقترح تغييرًا محددًا وتتابعه.",None),
("single_word_definition","ما معنى «مواد»؟","أشياء أو مكونات يتكون منها شيء أو تستخدم لغرض معين.",["ar-r822"]),
("single_word_definition","ما معنى «مجتمع»؟","مجموعة الأشخاص الذين يعيشون أو يتفاعلون في مكان مشترك.",["ar-r794"]),
("contrast","أيهما عملية تدريجية عبر الوقت: نمو أم منطقة؟","نمو.",["ar-r968","ar-r969"]),
("reference_resolution","إلى ماذا تشير «معلوماته» عند وصف المشروع؟","إلى المعلومات التي يقدمها المشروع للمستخدمين.",None),
("inference","لماذا لا تتوقع نور أن تحل الأنشطة الصغيرة كل المشكلات؟","لأن المشكلات البيئية أوسع، لكن النشاط الصغير يمكن أن يساعد في فهم جزء محدد وتحسينه.",None),
("grammar_function","ماذا تفعل «بعد ذلك» في ترتيب منهج نور؟","تربط مرحلة المقارنة بالمرحلة التالية، وهي اقتراح تغيير محدد.",None)
]}
]
def lex():
    d={}
    for line in LEX.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r=json.loads(line);d[r["rank"]]=r
    return d
def target(n,text,d):
    f,s,c=T[n];r=d[n]
    return {"id":f"ar-r{n}","form":f,"lemma":f,"part_of_speech":r.get("part_of_speech_source"),"intended_sense":s,"register":"contemporary standard","variety":"MSA","context_strategy":c,"first_introduced":True,"exposures_in_text":max(1,text.count(f)),"source_lexicon":r.get("source_file"),"source_rank":n,"beyond_base":False}
def build(x,d):
    qs,ans=qa(x["qa"]);text=x["text"]
    return {"id":x["id"],"language":"ar","cefr":"A2","unit":8,"sequence":x["sequence"],"revision":1,"title":x["title"],"passage_type":x["passage_type"],"genre":x["genre"],"domains":x["domains"],"topics":x["topics"],"text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r"[.!؟](?:\s|$)",text))),"estimated_known_token_coverage":0,"new_lexical_targets":[target(n,text,d) for n in x["new"]],"review_lexical_targets":x["reviews"],"grammar_targets":x["grammar"],"discourse_targets":x["discourse"],"questions":qs,"answer_key":ans,"speed_training":{"timed":x["passage_type"]=="fluency","benchmark_eligible":False,"comprehension_gate":0.8,"new_word_policy":"none" if x["passage_type"]=="fluency" else "controlled","notes":"A2 generation-stage passage; formal fluency/coverage decision deferred to final audit."},"quality":{"status":"draft","linguistic_review":"pending","pedagogical_review":"pending","coverage_check":"pending","answer_key_check":"pending","schema_check":"pending","fact_check":"not_required","notes":["High-quality A2 generation-stage draft; formal audits deferred to the final multi-pass review phase."]},"paired_text_group":None,"prerequisites":["Arabic A1 generation corpus","Arabic A2 Units 01-07 generation corpus"],"difficulty_notes_internal":"A2 Unit 08 generation draft: environmental observation, gradual change, resource use, interconnected effects, and community-scale practical responses.","reader_tags":["unit_role:"+x["passage_type"],"generation_batch","a2"],"complexity_profile":{"mean_sentence_length":None,"median_sentence_length":None,"clause_count":None,"subordination_count":None,"coordination_count":None,"connective_diversity":None,"lexical_diversity":None,"reference_chain_max_distance":None,"multiword_expression_count":None,"morphology_notes":"A2 generation-stage draft; practical environmental explanation and causal links.","inference_depth":"local_to_two_sentence"}}
def main():
    old=[json.loads(x) for x in OUT.read_text(encoding="utf-8").splitlines() if x.strip()] if OUT.exists() else []
    old=[r for r in old if r.get("unit")!=8];d=lex();new=[build(x,d) for x in R]
    if len(new)!=6 or any(len(r["questions"])!=10 or len(r["answer_key"])!=10 for r in new):raise SystemExit("A2 Unit08 generation contract failed")
    rows=sorted(old+new,key=lambda r:(r.get("unit",0),r.get("sequence",0)))
    OUT.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    print("generated Arabic A2 Unit 08: six passages, sixty questions, sixty answers")
if __name__=="__main__":main()
