#!/usr/bin/env python3
"""Generate Arabic A2 Unit 02: plans, invitations, and changes."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"reading"/"arabic"/"a2"/"passages.jsonl"
LEX=ROOT/"reading"/"lexicons"/"arabic.jsonl"
T={
621:("حالي","current; present",["contrast","scenario_resolution"]),
691:("موعد","appointment; date; scheduled time",["scenario_resolution"]),
663:("رد","reply; response",["behavior_interpretation"]),
648:("متأكد","sure; certain",["behavior_interpretation"]),
674:("اتصل","contacted; called",["scenario_resolution"]),
673:("لاحق","later; subsequent",["contrast"]),
682:("اختيار","choice; selection",["contrast","scenario_resolution"]),
623:("تالي","next; following",["parallel_structure"]),
659:("تنظيم","organization; arranging",["cause_consequence"]),
661:("دورة","course; session; cycle",["category_relation"]),
626:("معا","together",["behavior_interpretation"]),
}

def qa(items):
    qs=[]; ans=[]
    for i,(typ,prompt,answer,ids) in enumerate(items,1):
        q={"id":f"q{i}","type":typ,"prompt":prompt,"answer_id":f"a{i}"}
        if ids:q["target_ids"]=ids
        qs.append(q); ans.append({"id":f"a{i}","question_id":f"q{i}","answer":answer,"explanation":""})
    if len(qs)!=10: raise ValueError("ten questions required")
    return qs,ans

R=[
{
"id":"ar-a2-u02-p01","sequence":7,"title":"دعوة إلى المكتبة","passage_type":"instructional","genre":"message exchange","domains":["personal","public"],"topics":["invitation","library","scheduling"],
"text":"في مساء الثلاثاء أرسلت هدى إلى نور رسالة تقول فيها إن المكتبة ستقيم لقاءً للقراءة يوم الجمعة. كتبت: «الموعد في الرابعة، وسأذهب قبل البداية بقليل. هل تريدين أن تأتي معي؟» قرأت نور الرسالة وهي تنظر إلى خطتها للأسبوع. كان عندها عمل منزلي في ذلك اليوم، لكنها توقعت أن تنتهي منه قبل الثالثة. لم ترد مباشرة، لأنها أرادت أن تتأكد من وقتها أولًا. بعد نصف ساعة راجعت ما عليها، ثم أرسلت ردًا: «نعم، الموعد مناسب لي. سأقابلك أمام المكتبة في الثالثة وخمسين دقيقة.» أجابت هدى بسرعة: «ممتاز، سأكون هناك.» في اليوم التالي أخبرت نور أمها بالاتفاق. قالت أمها: من الجيد أنك لم ترسلي ردًا قبل أن تعرفي هل الموعد يناسبك. قالت نور: الدعوة سهلة، لكن الرد الجيد يحتاج أحيانًا إلى أن أنظر إلى خطتي قبل أن أقول نعم أو لا.",
"new":[691,663],
"reviews":[{"id":"ar-r544","form":"رسالة","review_stage":"R3","representation":"running_text"},{"id":"ar-r505","form":"متى","review_stage":"R3","representation":"other"}],
"grammar":[{"id":"ar-a2-invitation-response","role":"new","description":"هل تريد أن...؟ followed by a reasoned acceptance or decline"},{"id":"ar-a2-before-answering","role":"new","description":"قبل أن + present/subjunctive in planning contexts"}],
"discourse":[{"id":"a2-invitation-decision","role":"new","description":"evaluate an invitation against an existing schedule before replying"}],
"qa":[
("gist","لماذا تنتظر نور قبل الرد على هدى؟","لأنها تريد أن تتأكد أن موعد اللقاء يناسب عملها وخطتها.",None),
("literal_detail","ما موعد لقاء القراءة؟","يوم الجمعة في الرابعة.",["ar-r691"]),
("vocabulary_in_context","ماذا يعني «الموعد» في رسالة هدى؟","الوقت المحدد مسبقًا لبدء لقاء القراءة.",["ar-r691"]),
("vocabulary_in_context","ماذا يعني «ردًا» في «أرسلت ردًا»؟","الجواب الذي ترسله نور على دعوة هدى.",["ar-r663"]),
("cause_effect","لماذا يصبح الموعد مناسبًا لنور؟","لأنها تتوقع أن تنتهي من عملها قبل الثالثة.",None),
("single_word_definition","ما معنى «موعد»؟","وقت أو تاريخ محدد مسبقًا للقاء أو عمل.",["ar-r691"]),
("single_word_definition","ما معنى «رد»؟","جواب أو استجابة لكلام أو رسالة أو طلب.",["ar-r663"]),
("inference","ماذا يدل تصرف نور على طريقة جيدة لقبول الدعوات؟","أن تتحقق من التزاماتها قبل أن تعد بالحضور.",None),
("cloze_transfer","أكمل: عندي _____ مع طبيب الأسنان في العاشرة.","موعد",["ar-r691"]),
("cloze_transfer","أكمل: أرسلت رسالة إلى صديقي وانتظرت _____.","رده",["ar-r663"])
]},
{
"id":"ar-a2-u02-p02","sequence":8,"title":"هل أنت متأكد من الوقت؟","passage_type":"reinforcement","genre":"schedule-change narrative","domains":["personal","educational"],"topics":["schedule","change","confirmation"],
"text":"في صباح الخميس أخبر المعلم الطلاب أن نشاط الصف الذي كان مقررًا بعد الظهر سيتغير. قال إن القاعة المطلوبة غير متاحة، ولذلك سينتقل النشاط إلى اليوم التالي. كتبت نور الموعد الجديد في دفترها، لكن مريم لم تسمع الجملة الأخيرة لأنها كانت تجمع كتبها. بعد الدرس سألت نور: «هل أنت متأكدة أن النشاط غدًا، وليس اليوم؟» فتحت نور دفترها وقالت: «نعم، أنا متأكدة. المعلم قال إن اليوم التالي هو الموعد الجديد.» لم تعتمد مريم على الذاكرة وحدها؛ ذهبتا معًا إلى اللوحة عند باب الصف، فوجدتا ورقة كتب عليها الوقت نفسه. قالت مريم: الآن أنا متأكدة أيضًا. وأضافت: عندما يتغير موعد، أفضل أن أتحقق من مصدرين إذا لم أسمع الكلام كاملًا. في اليوم التالي حضرتا النشاط في الوقت الصحيح، ولم تضطر أي منهما إلى العودة إلى المدرسة في وقت غير مناسب.",
"new":[648,623],
"reviews":[{"id":"ar-r691","form":"موعد","review_stage":"R1","representation":"running_text"},{"id":"ar-r663","form":"رد","review_stage":"R1","representation":"other"},{"id":"ar-r563","form":"إعلان","review_stage":"R3","representation":"other"}],
"grammar":[{"id":"ar-a2-certainty","role":"new","description":"متأكد أن... for checking certainty"},{"id":"ar-a2-next-following","role":"new","description":"التالي with day/event reference"}],
"discourse":[{"id":"a2-confirm-change","role":"new","description":"verify a changed schedule using more than one information source"}],
"qa":[
("gist","ما التغيير الذي يحدث في خطة الصف؟","ينتقل النشاط من اليوم الحالي إلى اليوم التالي.",None),
("literal_detail","لماذا لم تسمع مريم كل كلام المعلم؟","لأنها كانت تجمع كتبها.",None),
("vocabulary_in_context","ماذا تعني «متأكدة» عندما تسأل مريم نور؟","واثقة من أن المعلومة صحيحة.",["ar-r648"]),
("vocabulary_in_context","ماذا يعني «اليوم التالي»؟","اليوم الذي يأتي مباشرة بعد اليوم الحالي.",["ar-r623"]),
("cause_effect","لماذا تذهبان إلى لوحة الصف؟","لتتحققا من الموعد الجديد من مصدر آخر.",None),
("single_word_definition","ما معنى «متأكد»؟","واثق أو على يقين من صحة شيء.",["ar-r648"]),
("single_word_definition","ما معنى «تالي»؟","الذي يأتي بعد شيء آخر مباشرة أو في الترتيب.",["ar-r623"]),
("inference","لماذا كان التحقق مفيدًا رغم أن نور كتبت الموعد؟","لأنه أعطى مريم دليلًا مستقلًا وأزال الشك.",None),
("cloze_transfer","أكمل: لست _____ من رقم القاعة؛ سأتحقق منه.","متأكدًا",["ar-r648"]),
("cloze_transfer","أكمل: انتهى هذا الدرس، والدرس _____ يبدأ بعد عشر دقائق.","التالي",["ar-r623"])
]},
{
"id":"ar-a2-u02-p03","sequence":9,"title":"اتصال بعد تغيير الخطة","passage_type":"interleaved","genre":"phone-call narrative","domains":["personal","public"],"topics":["calling","changed plans","later time"],
"text":"كان من المفترض أن تلتقي نور بابنة خالتها سلمى في مقهى قريب مساء السبت، لكن أم نور احتاجت إلى السيارة في الوقت نفسه. حاولت نور أن تجد طريقًا آخر، ثم رأت أن الوصول بالحافلة سيجعلها تتأخر كثيرًا. بدل أن تنتظر حتى آخر لحظة، اتصلت بسلمى بعد الظهر وشرحت لها المشكلة. قالت: «لا أريد أن أصلك متأخرة من غير أن أخبرك. هل يمكن أن نلتقي في وقت لاحق؟» نظرت سلمى إلى خطتها وقالت إن السابعة والنصف تناسبها. اتفقتا على الموعد الجديد، ثم أرسلت نور رسالة قصيرة تؤكد المكان والوقت حتى لا يحدث سوء فهم. في المساء وصلت نور قبل الموعد بخمس دقائق. قالت سلمى: كان تغيير الخطة بسيطًا لأنك اتصلت مبكرًا. أجابت نور: تعلمت أن الاتصال في الوقت المناسب أفضل من ترك شخص آخر ينتظر من غير معلومات.",
"new":[674,673],
"reviews":[{"id":"ar-r648","form":"متأكد","review_stage":"R1","representation":"other"},{"id":"ar-r623","form":"تالي","review_stage":"R1","representation":"other"},{"id":"ar-r576","form":"هاتف","review_stage":"R3","representation":"other"},{"id":"ar-r447","form":"ينتظر","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-planned-vs-changed","role":"new","description":"كان من المفترض أن... لكن..."},{"id":"ar-a2-later-time","role":"new","description":"وقت لاحق for rescheduling"}],
"discourse":[{"id":"a2-reschedule-call","role":"new","description":"explain a constraint, propose a later time, and confirm a changed plan"}],
"qa":[
("literal_detail","لماذا لا تستطيع نور الالتزام بالوقت الأول؟","لأن أمها تحتاج إلى السيارة والوصول بالحافلة سيؤخرها كثيرًا.",None),
("literal_detail","ما الوقت الجديد للقاء؟","السابعة والنصف.",None),
("vocabulary_in_context","ماذا يعني «اتصلت بسلمى»؟","تواصلت معها هاتفيًا لتخبرها بتغيير الخطة.",["ar-r674"]),
("vocabulary_in_context","ماذا يعني «وقت لاحق»؟","وقت يأتي بعد الموعد الأول المقترح.",["ar-r673"]),
("cause_effect","لماذا ترسل نور رسالة بعد الاتصال؟","لتؤكد المكان والوقت الجديدين وتمنع سوء الفهم.",None),
("single_word_definition","ما معنى «اتصل» في هذا السياق؟","تواصل مع شخص، غالبًا عبر الهاتف.",["ar-r674"]),
("single_word_definition","ما معنى «لاحق»؟","آتٍ بعد وقت أو حدث سابق.",["ar-r673"]),
("inference","لماذا تمدح سلمى اتصال نور المبكر؟","لأنه أعطاها وقتًا لتعديل خطتها بدل الانتظار بلا خبر.",None),
("cloze_transfer","أكمل: عندما تغير الموعد _____ بصديقي لأخبره.","اتصلت",["ar-r674"]),
("cloze_transfer","أكمل: لا أستطيع الآن؛ سأتحدث معك في وقت _____.","لاحق",["ar-r673"])
]},
{
"id":"ar-a2-u02-p04","sequence":10,"title":"اختيار جديد للخطة الحالية","passage_type":"transfer","genre":"planning problem-solution narrative","domains":["personal","public"],"topics":["alternatives","current plan","weather"],
"text":"خططت نور وصديقاتها لقضاء عصر الأحد في الحديقة، وكانت الخطة الحالية أن يحضرن طعامًا خفيفًا ويجلسن قرب البحيرة. في الظهر تغير الطقس، وبدأ المطر قبل موعدهن بساعة. كتبت هدى في المجموعة: «هل نلغي اللقاء؟» لم ترغب نور في اتخاذ القرار بسرعة، واقترحت أن يبحثن عن اختيار آخر. كانت هناك ثلاثة اقتراحات: تأجيل اللقاء إلى يوم لاحق، أو الذهاب إلى مقهى قريب، أو الاجتماع في بيت مريم. قالت مريم إن بيتها متاح، وإن الجميع يستطيع الوصول إليه بسهولة. بعد عدة رسائل اتفقن على هذا الاختيار. لم تعد الخطة الحالية هي الحديقة، بل أصبح اللقاء في بيت مريم في الوقت نفسه. أحضرت كل واحدة شيئًا بسيطًا، وقضين ساعتين معًا. في النهاية قالت هدى: تغير المكان، لكن هدف اللقاء لم يتغير. قالت نور: عندما تتغير الظروف، وجود أكثر من اختيار يجعل تعديل الخطة أسهل من إلغائها مباشرة.",
"new":[682,621],
"reviews":[{"id":"ar-r674","form":"اتصل","review_stage":"R1","representation":"other"},{"id":"ar-r673","form":"لاحق","review_stage":"R1","representation":"running_text"},{"id":"ar-r105","form":"ربما","review_stage":"R3","representation":"other"}],
"grammar":[{"id":"ar-a2-current-plan","role":"new","description":"حالي/حالية describing the present plan or situation"},{"id":"ar-a2-alternatives","role":"new","description":"either/or alternatives and selecting among options"}],
"discourse":[{"id":"a2-plan-alternatives","role":"new","description":"compare alternatives after external conditions invalidate the original plan"}],
"qa":[
("gist","كيف تتعامل الصديقات مع تغير الطقس؟","يبحثن عن بدائل ويغيرن مكان اللقاء بدل إلغائه.",None),
("literal_detail","ما الاختيار الذي يتفقن عليه؟","الاجتماع في بيت مريم.",["ar-r682"]),
("vocabulary_in_context","ماذا يعني «اختيار آخر»؟","بديل مختلف يمكن أن يحل محل الخطة الأصلية.",["ar-r682"]),
("vocabulary_in_context","ماذا تعني «الخطة الحالية»؟","الخطة الموجودة والمعتمدة في الوقت الراهن.",["ar-r621"]),
("cause_effect","لماذا يصبح بيت مريم مناسبًا؟","لأنه متاح والجميع يستطيع الوصول إليه بسهولة.",None),
("single_word_definition","ما معنى «اختيار»؟","أحد البدائل الممكنة أو عملية تحديد بديل منها.",["ar-r682"]),
("single_word_definition","ما معنى «حالي»؟","موجود أو واقع في الوقت الحاضر.",["ar-r621"]),
("inference","ماذا تقصد هدى بقولها إن هدف اللقاء لم يتغير؟","أنهن ما زلن يردن قضاء الوقت معًا رغم تغير المكان.",None),
("cloze_transfer","أكمل: عندي أكثر من _____ للوصول إلى الجامعة.","اختيار",["ar-r682"]),
("cloze_transfer","أكمل: عنواني _____ مختلف عن عنواني القديم.","الحالي",["ar-r621"])
]},
{
"id":"ar-a2-u02-p05","sequence":11,"title":"تنظيم دورة قصيرة","passage_type":"checkpoint","genre":"community-course planning narrative","domains":["educational","public"],"topics":["course","organization","shared planning"],
"text":"أعلن مركز الحي عن دورة قصيرة في التصوير مدتها أربعة أسابيع. أرادت نور وهدى التسجيل معًا، لكنهما لاحظتا أن بعض الجلسات تتعارض مع أنشطة المدرسة. قبل التسجيل قرأتا البرنامج كاملًا بدل النظر إلى اليوم الأول فقط. كانت الدورة تقام كل ثلاثاء، وفي الأسبوع الثالث توجد جلسة إضافية يوم الخميس. قالت نور: تنظيم وقتنا مهم إذا أردنا حضور الدورة معًا من غير أن نهمل المدرسة. فتحتا تقويميهما وحددتا الأيام التي تحتاج إلى تغيير. وجدت هدى أنها تستطيع نقل تدريب رياضي واحد، بينما احتاجت نور إلى إنهاء واجب أسبوعي في وقت أبكر. بعد ذلك سجلتا في الدورة وأرسلتا إلى أسرتيهما جدولًا واضحًا بالمواعيد. في الأسبوع الأول وصلتا في الوقت ووجدتا أن التحضير المسبق جعلهما أكثر هدوءًا. قالت هدى: الدورة نفسها ليست المشكلة؛ تنظيم الأنشطة حولها هو الجزء الذي يحتاج إلى التفكير. قالت نور: والقيام بذلك معًا جعل ملاحظة التعارضات أسهل.",
"new":[661,659],
"reviews":[{"id":"ar-r682","form":"اختيار","review_stage":"R1","representation":"other"},{"id":"ar-r621","form":"حالي","review_stage":"R1","representation":"other"},{"id":"ar-r626","form":"معا","review_stage":"R3","representation":"running_text"},{"id":"ar-r691","form":"موعد","review_stage":"R2","representation":"running_text"}],
"grammar":[{"id":"ar-a2-if-want","role":"new","description":"إذا أردنا... for condition linked to a shared goal"},{"id":"ar-a2-while-contrast-plan","role":"review","description":"بينما for contrasting each person's schedule adjustment"}],
"discourse":[{"id":"a2-schedule-coordination","role":"integration","description":"coordinate a recurring course with existing obligations"}],
"qa":[
("gist","ما المشكلة التي تحاول نور وهدى حلها؟","تنظيم مواعيد دورة التصوير مع أنشطة المدرسة الأخرى.",None),
("literal_detail","كم تستمر الدورة؟","أربعة أسابيع.",["ar-r661"]),
("vocabulary_in_context","ماذا تعني «دورة» هنا؟","برنامج تعليمي قصير يتكون من عدة جلسات.",["ar-r661"]),
("vocabulary_in_context","ماذا يعني «تنظيم وقتنا»؟","ترتيب المواعيد والواجبات بحيث لا تتعارض بلا خطة.",["ar-r659"]),
("cause_effect","لماذا تقرآن البرنامج كاملًا قبل التسجيل؟","حتى تعرفا كل الجلسات وتكتشفا التعارضات قبل الالتزام.",None),
("single_word_definition","ما معنى «دورة» في التعليم؟","سلسلة دروس أو جلسات حول موضوع محدد.",["ar-r661"]),
("single_word_definition","ما معنى «تنظيم»؟","ترتيب عناصر أو أعمال بطريقة واضحة ومنسقة.",["ar-r659"]),
("inference","كيف ساعد العمل معًا في التخطيط؟","جعل مقارنة المواعيد واكتشاف التعارضات أسهل.",None),
("cloze_transfer","أكمل: سجلت في _____ قصيرة لتعلم التصوير.","دورة",["ar-r661"]),
("cloze_transfer","أكمل: يحتاج السفر إلى _____ جيد للوقت والحجوزات.","تنظيم",["ar-r659"])
]},
{
"id":"ar-a2-u02-p06","sequence":12,"title":"خطة يمكن أن تتغير","passage_type":"fluency","genre":"connected planning reflection","domains":["personal","public","educational"],"topics":["plans","invitations","changes","review"],
"text":"أصبحت نور أكثر راحة عندما تتعامل مع الخطط التي تتغير. إذا وصلتها دعوة، تنظر أولًا إلى الموعد ثم ترسل ردًا واضحًا بدل أن توافق بسرعة. وإذا سمعت أن نشاطًا انتقل إلى اليوم التالي، تتحقق من المعلومة حتى تكون متأكدة. وعندما لا تستطيع الوصول في الوقت المتفق عليه، تتصل بالشخص مبكرًا وتقترح وقتًا لاحقًا. أحيانًا لا يحتاج التغيير إلى موعد جديد، بل إلى اختيار مختلف للمكان أو طريقة اللقاء. وفي الخطط الأطول، مثل دورة تمتد عدة أسابيع، تعرف نور أن تنظيم الوقت قبل البداية يمنع مشكلات كثيرة لاحقًا. هي لا تتوقع أن تسير كل خطة كما كُتبت أول مرة. الأهم عندها أن يعرف الأشخاص المعنيون ما تغير، وأن يكون الرد واضحًا، وأن يتفقوا معًا على البديل. بهذه الطريقة يصبح تغيير الخطة جزءًا طبيعيًا من التنظيم، لا سببًا للفوضى أو سوء الفهم.",
"new":[],
"reviews":[{"id":"ar-r691","form":"موعد","review_stage":"R2","representation":"running_text"},{"id":"ar-r663","form":"رد","review_stage":"R2","representation":"running_text"},{"id":"ar-r648","form":"متأكد","review_stage":"R2","representation":"running_text"},{"id":"ar-r674","form":"اتصل","review_stage":"R2","representation":"running_text"},{"id":"ar-r673","form":"لاحق","review_stage":"R2","representation":"running_text"},{"id":"ar-r682","form":"اختيار","review_stage":"R2","representation":"running_text"},{"id":"ar-r623","form":"تالي","review_stage":"R2","representation":"running_text"},{"id":"ar-r659","form":"تنظيم","review_stage":"R1","representation":"running_text"},{"id":"ar-r661","form":"دورة","review_stage":"R1","representation":"running_text"},{"id":"ar-r626","form":"معا","review_stage":"R2","representation":"running_text"}],
"grammar":[{"id":"ar-a2-u02-cumulative","role":"integration","description":"recycle invitations, confirmation, rescheduling, alternatives, and longer-plan coordination"}],
"discourse":[{"id":"a2-plan-change-fluency","role":"integration","description":"high-coverage cumulative reading about adapting plans and communicating changes"}],
"qa":[
("gist","ما الفكرة الرئيسية في النص؟","نور تعلمت أن تتعامل مع تغير الخطط بالتأكد والتواصل واختيار بدائل واضحة.",None),
("literal_detail","ماذا تفعل نور قبل الرد على دعوة؟","تنظر إلى الموعد أولًا.",["ar-r691","ar-r663"]),
("literal_detail","ماذا تفعل إذا لن تصل في الوقت المتفق عليه؟","تتصل مبكرًا وتقترح وقتًا لاحقًا.",["ar-r674","ar-r673"]),
("inference","لماذا لا تعتبر نور تغيير الخطة فشلًا؟","لأن التغيير يمكن تنظيمه إذا عرف الجميع ما حدث واتفقوا على بديل.",None),
("summary","لخص طريقة نور في إدارة الخطط المتغيرة.","تتحقق من المعلومات، ترد بوضوح، تتصل مبكرًا عند المشكلة، وتختار بديلًا وتنظم المواعيد مع الآخرين.",None),
("single_word_definition","ما معنى «متأكد»؟","واثق من صحة المعلومة.",["ar-r648"]),
("contrast","أيهما يدل على بديل من عدة بدائل: «اختيار» أم «موعد»؟","اختيار.",["ar-r682","ar-r691"]),
("reference_resolution","إلى ماذا تشير «البديل» في الجملة الأخيرة؟","إلى الخطة أو الوقت أو المكان الجديد المتفق عليه بدل الأصل.",None),
("grammar_function","ماذا يصف «التالي» في «اليوم التالي»؟","اليوم الذي يأتي بعد اليوم المذكور مباشرة.",["ar-r623"]),
("contrast","أيهما سلسلة تعليمية: «دورة» أم «رد»؟","دورة.",["ar-r661","ar-r663"])
]}
]

def lex():
    d={}
    for line in LEX.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row=json.loads(line); d[row["rank"]]=row
    return d

def target(rank,text,d):
    form,sense,strat=T[rank]; src=d[rank]
    return {"id":f"ar-r{rank}","form":form,"lemma":form,"part_of_speech":src.get("part_of_speech_source"),"intended_sense":sense,"register":"contemporary standard","variety":"MSA","context_strategy":strat,"first_introduced":True,"exposures_in_text":max(1,text.count(form)),"source_lexicon":src.get("source_file"),"source_rank":rank,"beyond_base":False}

def build(x,d):
    qs,ans=qa(x["qa"]); text=x["text"]
    return {"id":x["id"],"language":"ar","cefr":"A2","unit":2,"sequence":x["sequence"],"revision":1,"title":x["title"],"passage_type":x["passage_type"],"genre":x["genre"],"domains":x["domains"],"topics":x["topics"],"text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r"[.!؟](?:\s|$)",text))),"estimated_known_token_coverage":0,"new_lexical_targets":[target(n,text,d) for n in x["new"]],"review_lexical_targets":x["reviews"],"grammar_targets":x["grammar"],"discourse_targets":x["discourse"],"questions":qs,"answer_key":ans,"speed_training":{"timed":x["passage_type"]=="fluency","benchmark_eligible":False,"comprehension_gate":0.8,"new_word_policy":"none" if x["passage_type"]=="fluency" else "controlled","notes":"A2 generation-stage passage; formal fluency/coverage decision deferred to final audit."},"quality":{"status":"draft","linguistic_review":"pending","pedagogical_review":"pending","coverage_check":"pending","answer_key_check":"pending","schema_check":"pending","fact_check":"not_required","notes":["High-quality A2 generation-stage draft; formal audits deferred to the final multi-pass review phase."]},"paired_text_group":None,"prerequisites":["Arabic A1 generation corpus","Arabic A2 Unit 01 generation corpus"],"difficulty_notes_internal":"A2 Unit 02 generation draft: invitations, changed plans, confirmation, alternatives, and longer scheduling chains.","reader_tags":["unit_role:"+x["passage_type"],"generation_batch","a2"],"complexity_profile":{"mean_sentence_length":None,"median_sentence_length":None,"clause_count":None,"subordination_count":None,"coordination_count":None,"connective_diversity":None,"lexical_diversity":None,"reference_chain_max_distance":None,"multiword_expression_count":None,"morphology_notes":"A2 generation-stage draft; connected MSA clauses with schedule changes and reasons.","inference_depth":"local_to_two_sentence"}}

def main():
    existing=[json.loads(line) for line in OUT.read_text(encoding="utf-8").splitlines() if line.strip()] if OUT.exists() else []
    existing=[r for r in existing if r.get("unit")!=2]
    d=lex(); new=[build(x,d) for x in R]
    if len(new)!=6 or any(len(r["questions"])!=10 or len(r["answer_key"])!=10 for r in new): raise SystemExit("A2 Unit02 generation contract failed")
    rows=sorted(existing+new,key=lambda r:(r.get("unit",0),r.get("sequence",0)))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    print("generated Arabic A2 Unit 02: six passages, sixty questions, sixty answers")
if __name__=="__main__":main()
