#!/usr/bin/env python3
"""Generate Arabic A2 Unit 10: cumulative checkpoint.

No deliberately new lexical targets are introduced in this unit. It consolidates
previous A2 vocabulary and discourse work before the later final audit phase.
"""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"reading"/"arabic"/"a2"/"passages.jsonl"

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
"id":"ar-a2-u10-p01","sequence":55,"title":"يوم تغيّرت فيه ثلاث خطط","passage_type":"instructional","genre":"multi-problem daily narrative","domains":["personal","public"],"topics":["services","schedule changes","problem solving"],
"text":"بدأ يوم نور بخطة واضحة: ستذهب إلى البنك مع والدها في الصباح، ثم تقابل هدى في المكتبة، وفي المساء تحضر فعالية قصيرة في مركز الحي. قبل الخروج اتصل والدها بالبنك واكتشف أن الفرع سيفتح في وقت لاحق بسبب عمل فني. لم يلغيا الأمر، بل نقلا الزيارة إلى اليوم التالي. بعد ذلك وصلت نور إلى المكتبة في موعدها، لكنها وجدت إعلانًا عند الباب يقول إن قسمًا من المبنى مغلق وإن اللقاء انتقل إلى غرفة في المركز المجاور. أرسلت إلى هدى رسالة بالعنوان الجديد وانتظرتها هناك. في المساء بدأت السماء تمطر بقوة، فأعلن المركز أن الفعالية ستنتهي أبكر من المتوقع. عادت نور إلى البيت قبل الموعد الأصلي بساعة. عندما راجعت يومها لاحظت أن ثلاث خطط تغيرت، لكن كل تغيير كان له حل مختلف: تأجيل البنك، وتغيير موقع اللقاء، والعودة المبكرة من الفعالية. قالت لأمها: لم يكن اليوم منظمًا لأن كل شيء سار كما أردت، بل لأنني عرفت المعلومة الجديدة وعدلت الخطوة التالية بدل أن أتمسك بالخطة الأولى.",
"reviews":[{"id":"ar-r581","form":"بنك","review_stage":"R3","representation":"running_text"},{"id":"ar-r674","form":"اتصل","review_stage":"R3","representation":"running_text"},{"id":"ar-r691","form":"موعد","review_stage":"R3","representation":"running_text"},{"id":"ar-r563","form":"إعلان","review_stage":"R3","representation":"running_text"},{"id":"ar-r594","form":"قسم","review_stage":"R3","representation":"running_text"},{"id":"ar-r982","form":"فعالية","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-change-chain","role":"integration","description":"multiple plan changes linked by time and cause"}],
"discourse":[{"id":"a2-adaptive-day","role":"integration","description":"compare three different responses to three different plan disruptions"}],
"qa":[
("gist","ما الفكرة الرئيسية في النص؟","نور تتعامل مع ثلاثة تغييرات مختلفة في خطط يومها من خلال تعديل كل خطة بالطريقة المناسبة.",None),
("literal_detail","لماذا تتأجل زيارة البنك؟","لأن الفرع سيفتح في وقت لاحق بسبب عمل فني.",["ar-r581","ar-r674"]),
("literal_detail","أين تقابل نور هدى في النهاية؟","في غرفة في المركز المجاور للمكتبة.",None),
("cause_effect","لماذا تعود نور مبكرًا مساءً؟","لأن المطر قوي والمركز أعلن نهاية مبكرة للفعالية.",["ar-r982"]),
("inference","ما الذي يجعل اليوم منظمًا في نظر نور رغم التغييرات؟","أنها تحصل على معلومات جديدة وتعدل الخطوة التالية بدل التمسك بخطة لم تعد مناسبة.",None),
("summary","لخص الحلول الثلاثة التي تستخدمها نور.","تؤجل زيارة البنك، تغير موقع لقاء المكتبة، وتعود مبكرًا من الفعالية.",None),
("reference_resolution","إلى ماذا تشير «الخطة الأولى» في الجملة الأخيرة؟","إلى الخطة الأصلية لكل نشاط قبل وصول المعلومات الجديدة.",None),
("contrast","أي تغيير احتاج إلى تأجيل يوم كامل؟","زيارة البنك.",None),
("inference","لماذا لا تستخدم نور الحل نفسه لكل مشكلة؟","لأن سبب كل تغيير وطبيعته مختلفان، ولذلك يحتاج كل موقف إلى استجابة مناسبة.",None),
("grammar_function","ماذا تفعل «بل» في «لم يكن... بل...»؟","تصحح الفكرة الأولى وتقدم التفسير الذي تعتبره نور أدق.",None)
]},
{
"id":"ar-a2-u10-p02","sequence":56,"title":"مشروع يبدأ بذكرى","passage_type":"reinforcement","genre":"memory-to-project narrative","domains":["personal","educational"],"topics":["memory","photography","project learning"],
"text":"أثناء زيارة بيت جدتها وجدت نور صورة قديمة لسوق الحي كما كان قبل سنوات. سألت جدتها عن المكان، فحكت لها قصة قصيرة عن المحلات التي كانت موجودة وعن الطريق الذي كانت تسلكه إلى المدرسة. فكرت نور في تحويل هذه الذكرى إلى مشروع تصوير صغير. لم تكن تريد فقط إعادة تصوير المكان نفسه؛ أرادت مقارنة ما بقي وما تغير. بدأت بخطوة بسيطة: أخذت نسخة رقمية من الصورة القديمة وحددت الموقع التقريبي. ثم ذهبت إلى السوق والتقطت صورة حديثة من زاوية مشابهة. عندما قارنت الصورتين لاحظت أن بعض المباني ما زالت موجودة بينما تغيرت واجهات ومحلات كثيرة. في المتابعة مع مدرب التصوير اقترح أن تسأل شخصين آخرين عن ذكرياتهما حتى لا يعتمد المشروع على رواية واحدة. فعلت ذلك واكتشفت اختلافًا في التفاصيل، لكنها وجدت أيضًا نقاطًا مشتركة. في نهاية المشروع كتبت نور فقرة تقول إن الخبرة لا تأتي من التقاط صورة جميلة فقط؛ جاءت من الجمع بين قصة ونسخة قديمة وتصوير جديد ومقابلات، ثم التفكير في العلاقة بينها.",
"reviews":[{"id":"ar-r812","form":"قصة","review_stage":"R3","representation":"running_text"},{"id":"ar-r810","form":"نسخة","review_stage":"R3","representation":"running_text"},{"id":"ar-r912","form":"تصوير","review_stage":"R3","representation":"running_text"},{"id":"ar-r934","form":"خطوة","review_stage":"R3","representation":"running_text"},{"id":"ar-r957","form":"متابعة","review_stage":"R3","representation":"running_text"},{"id":"ar-r780","form":"خبرة","review_stage":"R2","representation":"running_text"}],
"grammar":[{"id":"ar-a2-past-present-comparison","role":"integration","description":"compare a remembered past place with its present form"}],
"discourse":[{"id":"a2-memory-project-synthesis","role":"integration","description":"combine photo evidence, oral memory, new observation, and reflection in one project"}],
"qa":[
("gist","كيف تحول نور صورة قديمة إلى مشروع؟","تقارن الصورة بالمكان الحالي وتضيف قصصًا ومقابلات وتصويرًا جديدًا.",None),
("literal_detail","ما أول خطوة في المشروع؟","أخذ نسخة رقمية من الصورة وتحديد الموقع التقريبي.",["ar-r810","ar-r934"]),
("inference","لماذا يقترح المدرب سؤال شخصين آخرين؟","حتى لا يعتمد المشروع على ذاكرة شخص واحد فقط ويمكن مقارنة الروايات.",None),
("contrast","ما الذي بقي وما الذي تغير في السوق؟","بقيت بعض المباني، بينما تغيرت واجهات ومحلات كثيرة.",None),
("summary","لخص مصادر المعلومات في مشروع نور.","صورة قديمة، قصة الجدة، صورة حديثة، ومقابلات مع أشخاص آخرين.",None),
("reference_resolution","إلى ماذا تشير «بينها» في النهاية؟","إلى القصة والصورة القديمة والتصوير الجديد والمقابلات.",None),
("inference","لماذا لا تعتبر نور الصورة الجميلة وحدها خبرة؟","لأن المشروع احتاج إلى ملاحظة ومقارنة وسؤال أشخاص والتفكير في الأدلة.",["ar-r780"]),
("single_word_definition","ما معنى «متابعة» في مشروع مستمر؟","الرجوع إلى العمل بعد بدايته لمراقبة التقدم ومناقشة الخطوة التالية.",["ar-r957"]),
("cause_effect","كيف تؤثر المقابلات في فهم نور؟","تكشف اختلاف التفاصيل مع وجود نقاط مشتركة بين الذكريات.",None),
("grammar_function","ماذا تفعل «بينما» في مقارنة السوق؟","تربط شيئين متقابلين: ما بقي وما تغير.",None)
]},
{
"id":"ar-a2-u10-p03","sequence":57,"title":"رحلة واختيار لا يعتمد على الثمن وحده","passage_type":"interleaved","genre":"travel-and-purchase decision narrative","domains":["public","personal"],"topics":["travel","shopping","comparison"],
"text":"خططت نور وهدى لرحلة قصيرة بالقطار إلى قرية قرب البحر. وجدتا تذكرتين بسعرين مختلفين: الأولى أرخص لكنها على قطار يصل متأخرًا، والثانية أغلى قليلًا لكنها تترك وقتًا أطول قبل الحافلة الأخيرة إلى القرية. في البداية بدا الثمن الأقل صفقة أفضل، لكنهما قارنتا الخطة كاملة. إذا أخذتا القطار الأرخص وتأخر عشر دقائق فقط، فقد يصبح الانتقال إلى الحافلة صعبًا. اختارتا التذكرة الثانية لأنها أكثر مناسبة للاتصال بين وسيلتي النقل. في المحطة اشترت هدى شاحنًا صغيرًا لهاتفها، لكن الموظف أعطاها نموذجًا بحجم مختلف عن الذي طلبته. احتفظت بالفاتورة وعادت إلى المتجر قبل صعود القطار. كان المنتج صالحًا، لكنه غير مناسب لجهازها، فأخذت بديلًا صحيحًا من غير مشكلة. أثناء الرحلة قالت نور إن اليوم جمع نوعين من المقارنة: في التذكرة قارنتا الثمن بالوقت والمخاطرة، وفي المتجر قارنت هدى المنتج بحاجتها الفعلية. قالت هدى: الاختيار الأرخص أو الموجود أمامنا ليس دائمًا الاختيار الذي يحل المشكلة أفضل.",
"reviews":[{"id":"ar-r953","form":"قطار","review_stage":"R3","representation":"running_text"},{"id":"ar-r800","form":"انتقال","review_stage":"R3","representation":"running_text"},{"id":"ar-r835","form":"بحر","review_stage":"R3","representation":"running_text"},{"id":"ar-r939","form":"ثمن","review_stage":"R3","representation":"running_text"},{"id":"ar-r941","form":"صفقة","review_stage":"R3","representation":"running_text"},{"id":"ar-r836","form":"مناسب","review_stage":"R3","representation":"running_text"},{"id":"ar-r716","form":"صالح","review_stage":"R3","representation":"running_text"},{"id":"ar-r719","form":"بدل","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-multi-factor-comparison","role":"integration","description":"compare cost, time, risk, compatibility, and actual need"}],
"discourse":[{"id":"a2-travel-shopping-decision","role":"integration","description":"apply the same decision principle across transport and product choice"}],
"qa":[
("gist","ما الفكرة المشتركة بين قرار التذكرة وقرار الشاحن؟","أن الاختيار الجيد يعتمد على ملاءمة الحاجة والظروف، لا على السعر أو التوفر وحدهما.",None),
("literal_detail","لماذا تختاران التذكرة الأغلى؟","لأنها تترك وقتًا أفضل للانتقال إلى الحافلة.",["ar-r800"]),
("literal_detail","ما المشكلة في الشاحن الأول؟","حجمه أو نموذجه غير مناسب لجهاز هدى رغم أنه صالح.",["ar-r716","ar-r836"]),
("inference","لماذا يمكن أن تصبح التذكرة الأرخص أسوأ عمليًا؟","لأن تأخيرًا صغيرًا قد يجعلهما تفوتان الحافلة الأخيرة.",None),
("summary","لخص المقارنتين اللتين تجريان في النص.","تقارنان تذكرتين بحسب الثمن ووقت الاتصال، وتقارن هدى الشاحن بحاجتها وتستبدله عندما لا يناسب.",None),
("contrast","ما الفرق بين «صالح» و«مناسب» في حالة الشاحن؟","صالح يعني أنه يعمل، ومناسب يعني أنه يلائم جهاز هدى وحاجتها.",None),
("reference_resolution","إلى ماذا تشير «المنتج» في الفقرة؟","إلى الشاحن الصغير الذي اشترته هدى.",None),
("cause_effect","كيف تساعد الفاتورة هدى؟","تسمح لها بالعودة إلى المتجر وإثبات الشراء وأخذ بديل مناسب.",None),
("inference","ما المبدأ الذي تعبر عنه جملة هدى الأخيرة؟","أن القرار الأفضل هو الذي يحل الحاجة الفعلية، لا الذي يبدو أرخص أو أسهل في اللحظة الأولى.",None),
("grammar_function","ماذا تعبر «إذا... فقد...» في النص؟","عن احتمال نتيجة سلبية إذا حدث تأخير في القطار.",None)
]},
{
"id":"ar-a2-u10-p04","sequence":58,"title":"خبر عن مشروع بيئي","passage_type":"transfer","genre":"simple news-and-evidence synthesis","domains":["public","educational"],"topics":["news","environment","community project"],
"text":"نشرت الصحافة المحلية خبرًا عن مشروع جديد في الحي لتقليل استخدام الطاقة في مبانٍ عامة. بدأ الخبر ببيان من البلدية يعلن أن ثلاث مبانٍ ستجرب أجهزة تقيس استهلاك الكهرباء مدة شهرين. ثم نقل الخبر توقعات المسؤولين بأن المشروع قد يخفض الاستخدام غير الضروري، لكنه أشار بوضوح إلى أن النتائج لم تظهر بعد. طلبت المعلمة من نور أن تقرأ الخبر وتحدد ما هو مؤكد وما هو متوقع. كتبت نور أن تركيب الأجهزة ومدة التجربة حقيقتان معلنتان، أما مقدار التوفير فهو توقع. بعد شهرين قرأت نور خبرًا ثانيًا. أظهرت البيانات انخفاضًا في بعض المباني، بينما لم يتغير مبنى آخر كثيرًا. ذكر التقرير أن اختلاف الاستخدام قد يرتبط بطريقة تشغيل المباني وعدد الزوار. قالت نور إن النتيجة أكثر فائدة من جملة «المشروع نجح» وحدها، لأنها تبين أين ظهر التأثير وأين لم يظهر. وأضافت أن المجتمع يستطيع الآن مناقشة الخطوة التالية بناءً على بيانات فعلية، لا على التوقع الأول فقط.",
"reviews":[{"id":"ar-r960","form":"صحافة","review_stage":"R3","representation":"running_text"},{"id":"ar-r751","form":"بيان","review_stage":"R3","representation":"running_text"},{"id":"ar-r986","form":"توقعات","review_stage":"R3","representation":"running_text"},{"id":"ar-r913","form":"أظهرت","review_stage":"R3","representation":"running_text"},{"id":"ar-r850","form":"استخدام","review_stage":"R3","representation":"running_text"},{"id":"ar-r993","form":"طاقة","review_stage":"R3","representation":"running_text"},{"id":"ar-r924","form":"تأثير","review_stage":"R3","representation":"running_text"},{"id":"ar-r794","form":"مجتمع","review_stage":"R2","representation":"running_text"}],
"grammar":[{"id":"ar-a2-confirmed-vs-expected","role":"integration","description":"distinguish announced facts, forecasts, and later observed results"}],
"discourse":[{"id":"a2-news-environment-evidence","role":"integration","description":"connect source reading with environmental data and community decision making"}],
"qa":[
("gist","ما الذي تتعلمه نور من الخبرين؟","تمييز الخطة والتوقع الأول من النتائج التي ظهرت لاحقًا في بيانات الاستخدام.",None),
("literal_detail","كم مبنى يشارك في التجربة؟","ثلاثة مبانٍ.",None),
("contrast","ما المعلومة المؤكدة وما المعلومة المتوقعة في الخبر الأول؟","تركيب الأجهزة ومدة التجربة مؤكدان، أما مقدار خفض الاستخدام فمتوقع.",["ar-r986"]),
("inference","لماذا لا تكفي جملة «المشروع نجح»؟","لأن النتائج اختلفت بين المباني ويجب معرفة أين وكيف ظهر التأثير.",["ar-r924"]),
("summary","لخص تطور المعلومات من الخبر الأول إلى الثاني.","أُعلن مشروع وتوقع توفير للطاقة، ثم أظهرت البيانات لاحقًا نتائج مختلفة بين المباني.",None),
("reference_resolution","إلى ماذا تشير «النتائج»؟","إلى بيانات استخدام الطاقة بعد شهرين من التجربة.",None),
("cause_effect","ما العوامل المحتملة لاختلاف المباني؟","طريقة التشغيل وعدد الزوار.",None),
("inference","لماذا تصبح مناقشة الخطوة التالية أقوى بعد ظهور البيانات؟","لأن القرار يستطيع الاعتماد على نتائج فعلية بدل توقع غير مختبر.",None),
("contrast","أيهما مصدر رسمي مباشر: البيان أم الصحافة؟","البيان صادر عن الجهة الرسمية، بينما الصحافة تنقل وتشرح الخبر.",["ar-r751","ar-r960"]),
("grammar_function","ماذا تفعل «بينما» في وصف النتائج؟","تظهر الاختلاف بين مبانٍ انخفض فيها الاستخدام ومبنى لم يتغير كثيرًا.",None)
]},
{
"id":"ar-a2-u10-p05","sequence":59,"title":"احتفال تغيّر موعده وبقي معناه","passage_type":"checkpoint","genre":"culture-and-planning synthesis narrative","domains":["personal","public"],"topics":["celebration","customs","changed plans"],
"text":"كانت أسرة نور تستعد لاجتماع عائلي تقيمه كل سنة في بيت الجدة. كان الموعد يوم السبت، لكن قبل يومين أعلنت نشرة الطقس توقعات برياح قوية في المنطقة، وكان جزء كبير من اللقاء سيقام في الحديقة. اتصلت الجدة بأفراد الأسرة واقترحت نقل الاجتماع إلى الأحد بدل إلغائه. لم يناسب الموعد الجديد الجميع، لذلك اتفقوا على أن يأتي من يستطيع، وأن ترسل الأسرة صورًا ورسائل إلى من لا يستطيع الحضور. في يوم الأحد أحضر بعض الأقارب أطباقًا اعتادوا إعدادها، بينما جرب آخرون وصفات مختلفة. حكت الجدة قصة قديمة يعرفها معظم الكبار، ثم طلبت من الأطفال أن يرووا نسخة كما يتذكرونها. ظهرت اختلافات مضحكة بين النسخ، ولم يحاول أحد تحديد «النسخة الصحيحة» الوحيدة. في نهاية اليوم قالت نور إن العادة بقيت موجودة رغم تغير الموعد والطعام وعدد الحاضرين. ما بقي ثابتًا هو رغبة الأسرة في الاجتماع والتواصل وتذكر القصص المشتركة، أما التفاصيل فاستطاعت أن تتغير حسب الظروف.",
"reviews":[{"id":"ar-r691","form":"موعد","review_stage":"R3","representation":"running_text"},{"id":"ar-r986","form":"توقعات","review_stage":"R3","representation":"running_text"},{"id":"ar-r674","form":"اتصل","review_stage":"R3","representation":"running_text"},{"id":"ar-r719","form":"بدل","review_stage":"R3","representation":"running_text"},{"id":"ar-r977","form":"عادة","review_stage":"R3","representation":"running_text"},{"id":"ar-r812","form":"قصة","review_stage":"R3","representation":"running_text"},{"id":"ar-r810","form":"نسخة","review_stage":"R3","representation":"running_text"},{"id":"ar-r723","form":"معظم","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-stable-meaning-changing-details","role":"integration","description":"contrast a stable social purpose with flexible details"}],
"discourse":[{"id":"a2-culture-plan-synthesis","role":"integration","description":"adapt a recurring custom to changed conditions while preserving its social purpose"}],
"qa":[
("gist","ما الذي يبقى ثابتًا رغم تغير خطة الاجتماع؟","رغبة الأسرة في الاجتماع والتواصل وتذكر القصص المشتركة.",None),
("literal_detail","لماذا ينتقل الاجتماع من السبت إلى الأحد؟","بسبب توقع رياح قوية وكان جزء كبير من اللقاء في الحديقة.",["ar-r986"]),
("literal_detail","كيف يشارك من لا يستطيع الحضور؟","من خلال الصور والرسائل.",None),
("inference","لماذا لا يحاولون اختيار نسخة واحدة صحيحة من القصة؟","لأن اختلاف الذاكرة جزء مقبول وممتع من رواية القصة داخل الأسرة.",["ar-r810"]),
("summary","لخص ما تغير وما بقي في الاجتماع.","تغير اليوم وبعض الطعام وعدد الحاضرين، لكن هدف الاجتماع والعادة العائلية بقيا.",None),
("contrast","ما الفرق بين العادة والتفاصيل في النص؟","العادة هي الاجتماع والتواصل المتكرر، أما التفاصيل مثل الموعد والطعام فيمكن تعديلها.",["ar-r977"]),
("reference_resolution","إلى ماذا تشير «التفاصيل» في الجملة الأخيرة؟","إلى الموعد والطعام وعدد الحاضرين وطريقة المشاركة وغيرها من عناصر اللقاء.",None),
("cause_effect","كيف يساعد الاتصال المبكر بالعائلة؟","يعطي الناس وقتًا لمعرفة الموعد الجديد وتحديد هل يستطيعون الحضور.",["ar-r674"]),
("inference","ما الذي يبينه وجود وصفات جديدة إلى جانب الأطباق المعتادة؟","أن العادة يمكن أن تستمر مع وجود تغيير وتجربة داخلها.",None),
("grammar_function","ماذا تفعل «بينما» عند الحديث عن الطعام؟","تقارن بين أقارب أعدوا أطباقًا معتادة وآخرين جربوا وصفات مختلفة.",None)
]},
{
"id":"ar-a2-u10-p06","sequence":60,"title":"ما الذي أستطيع فعله الآن؟","passage_type":"fluency","genre":"A2 cumulative multi-domain reflection","domains":["personal","public","educational"],"topics":["A2 cumulative","practical reading","review"],
"text":"بعد إنهاء مستوى A2، تستطيع نور متابعة نصوص يومية أطول من التي قرأتها في البداية، لأنها لم تعد تبحث عن كلمة منفصلة فقط؛ أصبحت تربط المعلومات عبر عدة جمل. تستطيع قراءة إعلان عن خدمة في الحي ثم استخدام هاتفها للتأكد من الموعد أو القسم المناسب. وإذا تغيرت خطة، تفهم الردود والاختيارات وتستطيع متابعة سبب التغيير وما الخطة التالية. في نص عن الماضي تقارن صورة أو تسجيلًا بقصة شخص آخر، وتعرف أن الذاكرة قد تقدم نسخًا مختلفة من الحدث نفسه. وعند الشراء تقارن الحجم والثمن والحاجة، وتفهم مشكلة منتج غير صالح أو قرار إصلاحه. في التعلم تتبع خطوات مشروع، وتفكر في التدريب والمتابعة والخبرة. وفي السفر تفهم الانتقال والانتظار وتختار الوسيلة والمحطة المناسبة. كما تستطيع قراءة خبر بسيط وتفصل البيان عن توقعات لم تتحقق بعد، أو تتابع أثر مشروع بيئي في المجتمع. وعندما تقرأ عن عادات واحتفالات، تبحث عن الأنماط من غير أن تفترض أن الجميع يتصرف بالطريقة نفسها. هذه المهارات لا تجعل كل نص سهلًا، لكنها تعطي نور طريقة أوضح: تحدد الفكرة الرئيسية، تربط السبب بالنتيجة، تتابع المرجع عبر الجمل، وتقارن ما قيل أولًا بما ظهر لاحقًا.",
"reviews":[{"id":"ar-r583","form":"خدمة","review_stage":"R4","representation":"running_text"},{"id":"ar-r691","form":"موعد","review_stage":"R4","representation":"running_text"},{"id":"ar-r810","form":"نسخة","review_stage":"R3","representation":"running_text"},{"id":"ar-r939","form":"ثمن","review_stage":"R4","representation":"running_text"},{"id":"ar-r963","form":"إصلاح","review_stage":"R3","representation":"running_text"},{"id":"ar-r828","form":"تدريب","review_stage":"R4","representation":"running_text"},{"id":"ar-r800","form":"انتقال","review_stage":"R4","representation":"running_text"},{"id":"ar-r986","form":"توقعات","review_stage":"R3","representation":"running_text"},{"id":"ar-r794","form":"مجتمع","review_stage":"R3","representation":"running_text"},{"id":"ar-r977","form":"عادة","review_stage":"R4","representation":"running_text"}],
"grammar":[{"id":"ar-a2-level-cumulative","role":"integration","description":"cumulative A2 sequencing, cause-result, contrast, reference chains, reported information, and comparison"}],
"discourse":[{"id":"a2-level-fluency","role":"integration","description":"A2-level cumulative reading across services, planning, memory, shopping, learning, travel, news, environment, and culture"}],
"qa":[
("gist","ما الفكرة الرئيسية في النص؟","نور أصبحت قادرة على فهم نصوص A2 اليومية بربط المعلومات عبر الجمل والمقارنة بين الأسباب والنتائج والمصادر.",None),
("literal_detail","ما الذي تفعله نور عند قراءة خبر بسيط؟","تفصل البيان عن التوقعات وتتابع ما ثبت أو ظهر لاحقًا.",["ar-r986"]),
("literal_detail","ما الذي تقارنه عند الشراء؟","الحجم والثمن والحاجة وحالة المنتج.",["ar-r939"]),
("inference","ما الفرق بين قراءة نور الآن وقراءتها في البداية؟","لم تعد تركز على كلمات منفصلة فقط، بل تربط أفكارًا ومراجع وأسبابًا عبر عدة جمل.",None),
("summary","لخص أهم مهارات A2 المذكورة.","فهم الخدمات والخطط والذكريات والمقارنات والتعلم والسفر والأخبار والبيئة والعادات مع ربط السبب والنتيجة والمصادر عبر النص.",None),
("contrast","كيف تتعامل نور مع العادات بدل التعميم؟","تبحث عن أنماط واختلافات ولا تفترض أن الجميع يتصرفون بالطريقة نفسها.",["ar-r977"]),
("reference_resolution","إلى ماذا تشير «هذه المهارات» في الجملة الأخيرة؟","إلى مجموعة مهارات القراءة العملية المذكورة في الخدمات والخطط والذاكرة والشراء والتعلم والسفر والأخبار والبيئة والثقافة.",None),
("inference","لماذا لا تجعل هذه المهارات كل نص سهلًا؟","لأن نصوصًا جديدة قد تبقى صعبة، لكنها توفر طريقة منظمة لفهمها بدل ضمان معرفة كل كلمة.",None),
("grammar_function","ما وظيفة المقارنة بين «ما قيل أولًا» و«ما ظهر لاحقًا»؟","تساعد القارئ على فهم التغير والنتائج وتصحيح التوقع أو الفكرة الأولى.",None),
("synthesis","كيف يجمع النص بين مجالات مختلفة في مهارة واحدة؟","يبين أن نور تستخدم المبادئ نفسها—الفكرة الرئيسية، السبب والنتيجة، المرجع والمقارنة—في خدمات وخطط وذكريات وشراء وسفر وأخبار وغيرها.",None)
]}
]
def build(x):
    qs,ans=qa(x["qa"]);text=x["text"]
    return {"id":x["id"],"language":"ar","cefr":"A2","unit":10,"sequence":x["sequence"],"revision":1,"title":x["title"],"passage_type":x["passage_type"],"genre":x["genre"],"domains":x["domains"],"topics":x["topics"],"text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r"[.!؟](?:\s|$)",text))),"estimated_known_token_coverage":0,"new_lexical_targets":[],"review_lexical_targets":x["reviews"],"grammar_targets":x["grammar"],"discourse_targets":x["discourse"],"questions":qs,"answer_key":ans,"speed_training":{"timed":x["passage_type"]=="fluency","benchmark_eligible":False,"comprehension_gate":0.8,"new_word_policy":"none","notes":"A2 cumulative generation-stage passage; no deliberate new vocabulary. Formal fluency/coverage decision deferred to final audit."},"quality":{"status":"draft","linguistic_review":"pending","pedagogical_review":"pending","coverage_check":"pending","answer_key_check":"pending","schema_check":"pending","fact_check":"not_required","notes":["High-quality A2 cumulative generation-stage draft; formal audits deferred to the final multi-pass review phase."]},"paired_text_group":None,"prerequisites":["Arabic A1 generation corpus","Arabic A2 Units 01-09 generation corpus"],"difficulty_notes_internal":"A2 Unit 10 cumulative checkpoint: no deliberate new lexical targets; integrates prior A2 domains and discourse skills.","reader_tags":["unit_role:"+x["passage_type"],"generation_batch","a2","cumulative"],"complexity_profile":{"mean_sentence_length":None,"median_sentence_length":None,"clause_count":None,"subordination_count":None,"coordination_count":None,"connective_diversity":None,"lexical_diversity":None,"reference_chain_max_distance":None,"multiword_expression_count":None,"morphology_notes":"A2 cumulative generation-stage draft; integration over novelty.","inference_depth":"local_to_two_sentence"}}
def main():
    old=[json.loads(x) for x in OUT.read_text(encoding="utf-8").splitlines() if x.strip()] if OUT.exists() else []
    old=[r for r in old if r.get("unit")!=10];new=[build(x) for x in R]
    if len(new)!=6 or any(r["new_lexical_targets"] for r in new) or any(len(r["questions"])!=10 or len(r["answer_key"])!=10 for r in new):raise SystemExit("A2 Unit10 cumulative generation contract failed")
    rows=sorted(old+new,key=lambda r:(r.get("unit",0),r.get("sequence",0)))
    OUT.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    print("generated Arabic A2 Unit 10: six cumulative passages, sixty questions, sixty answers, zero deliberate new targets")
if __name__=="__main__":main()
