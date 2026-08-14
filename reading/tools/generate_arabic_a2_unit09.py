#!/usr/bin/env python3
"""Generate Arabic A2 Unit 09: culture, celebrations, and customs."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"reading"/"arabic"/"a2"/"passages.jsonl";LEX=ROOT/"reading"/"lexicons"/"arabic.jsonl"
T={
812:("قصة","story; tale",["scenario_resolution"]),
810:("نسخة","copy; version",["contrast"]),
927:("مطعم","restaurant",["category_relation"]),
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
"id":"ar-a2-u09-p01","sequence":49,"title":"وصفة ومعها قصة","passage_type":"instructional","genre":"family food-memory narrative","domains":["personal"],"topics":["family tradition","food","story"],
"text":"في نهاية الأسبوع ساعدت نور جدتها في إعداد طبق تصنعه العائلة في بعض المناسبات. كانت نور تعرف المكونات الأساسية، لكنها لم تعرف لماذا تصر الجدة على ترتيب الخطوات بالطريقة نفسها كل مرة. أثناء العمل بدأت الجدة تحكي قصة عن أمها، التي كانت تعد الطبق نفسه عندما تجتمع العائلة في بيت قديم خارج المدينة. قالت إن الوصفة تغيرت قليلًا مع السنوات؛ فبعض المكونات أصبحت أسهل في الشراء، وأفراد العائلة لا يفضلون الكمية نفسها من التوابل. مع ذلك بقيت خطوات معينة لأن الناس تعودوا عليها ولأنها تذكر الجدة ببيت أمها. سألت نور هل يجب أن تطبخ الطبق بالطريقة نفسها تمامًا إذا صنعته يومًا ما. ضحكت الجدة وقالت: لا، العادة ليست قانونًا. المهم أن تعرفي القصة التي وراءها، ثم يمكنك أن تغيري ما يناسبك. فهمت نور أن الطبق ليس مهمًا بسبب الطعام وحده؛ القصة المرتبطة به تجعل أفراد العائلة يشعرون أنهم يتذكرون أشخاصًا وأماكن حتى عندما تتغير الوصفة نفسها.",
"new":[812],
"reviews":[{"id":"ar-r977","form":"عادة","review_stage":"R3","representation":"running_text"},{"id":"ar-r761","form":"حفل","review_stage":"R3","representation":"other"},{"id":"ar-r899","form":"أثر","review_stage":"R3","representation":"other"}],
"grammar":[{"id":"ar-a2-used-to-family","role":"new","description":"كان/كانت + habitual past family practice"},{"id":"ar-a2-tradition-not-law","role":"new","description":"ليس... وحده / ليست... قانونًا"}],
"discourse":[{"id":"a2-custom-story","role":"new","description":"connect a repeated family practice to the story and memory that give it meaning"}],
"qa":[
("gist","لماذا يبقى الطبق مهمًا للعائلة؟","لأنه مرتبط بقصة وذكريات عائلية، لا بالطعام وحده.",None),
("literal_detail","هل بقيت الوصفة بلا أي تغيير؟","لا، تغيرت بعض المكونات والكميات مع السنوات.",None),
("vocabulary_in_context","ماذا تعني «قصة» في كلام الجدة؟","حكاية عن الماضي تشرح كيف كان الطبق مرتبطًا ببيت أمها واجتماع العائلة.",["ar-r812"]),
("inference","لماذا تقول الجدة إن العادة ليست قانونًا؟","لأن نور يمكنها فهم معنى العادة ثم تعديل التفاصيل بما يناسبها.",None),
("cause_effect","كيف تجعل القصة بعض الخطوات أكثر أهمية للجدة؟","لأنها تربطها بذكريات أمها والبيت القديم.",None),
("single_word_definition","ما معنى «قصة»؟","حكاية تروي أحداثًا أو تجارب مترابطة.",["ar-r812"]),
("contrast","هل ترى الجدة أن الحفاظ على العادة يعني منع كل تغيير؟","لا، تقبل التغيير ما دام معنى العادة وقصتها مفهومين.",None),
("reference_resolution","إلى ماذا تشير «التي وراءها»؟","إلى القصة أو المعنى الموجود خلف العادة.",None),
("cloze_transfer","أكمل: حكت الجدة _____ عن طفولتها.","قصة",["ar-r812"]),
("inference","ما الفرق بين الوصفة والقصة في النص؟","الوصفة تصف ما يفعلونه، والقصة تشرح لماذا يحمل الفعل معنى للعائلة.",None)
]},
{
"id":"ar-a2-u09-p02","sequence":50,"title":"نسختان من الحكاية","passage_type":"reinforcement","genre":"oral-story comparison","domains":["personal","educational"],"topics":["storytelling","versions","family memory"],
"text":"طلبت المعلمة من الطلاب أن يأتوا بحكاية سمعوها من شخص في العائلة. اختارت نور قصة قصيرة كان جدها يحكيها عن رحلة قديمة إلى قرية جبلية. قبل أن تكتبها، سألت خالتها عن الرحلة نفسها. فوجئت بأن نسخة الخالة لم تكن مطابقة لنسخة الجد. قال الجد إن المطر بدأ بعد وصولهم إلى القرية، بينما قالت الخالة إنها تتذكر أن المطر بدأ في الطريق. وفي نسخة الجد كان الجميع قد نسي المظلات، أما الخالة فتذكرت مظلة واحدة انكسرت بسبب الريح. لم تعرف نور أي التفاصيل أدق، ولذلك لم تحاول جمع النسختين في حكاية واحدة وكأن الاختلاف غير موجود. كتبت في واجبها أن أفراد العائلة يتذكرون الحدث نفسه بطرق مختلفة، ثم عرضت مثالين من الروايتين. قالت المعلمة إن هذا الاختلاف مفيد؛ فهو يذكرنا بأن الحكاية الشفوية قد تتغير قليلًا مع الذاكرة ومع الشخص الذي يرويها. احتفظت نور بالنسختين لأنها رأت أن المقارنة بينهما جزء من القصة نفسها.",
"new":[810],
"reviews":[{"id":"ar-r812","form":"قصة","review_stage":"R1","representation":"running_text"},{"id":"ar-r885","form":"ظن","review_stage":"R3","representation":"other"},{"id":"ar-r765","form":"زمن","review_stage":"R3","representation":"other"}],
"grammar":[{"id":"ar-a2-version-of","role":"new","description":"نسخة من + story/text"},{"id":"ar-a2-while-said","role":"review","description":"بينما قال/قالت... for contrasting recollections"}],
"discourse":[{"id":"a2-story-version-comparison","role":"new","description":"compare two oral versions without falsely resolving every disagreement"}],
"qa":[
("gist","ما الذي تكتشفه نور عندما تسأل خالتها؟","أن خالتها وجدها يتذكران بعض تفاصيل الرحلة بصورة مختلفة.",None),
("literal_detail","في ماذا يختلفان بشأن المطر؟","الجد يقول إنه بدأ بعد الوصول، والخالة تقول إنه بدأ في الطريق.",None),
("vocabulary_in_context","ماذا تعني «نسخة» من القصة؟","صيغة أو رواية معينة للقصة نفسها.",["ar-r810"]),
("inference","لماذا لا تجمع نور الروايتين وكأنهما متطابقتان؟","لأنها لا تعرف أي التفاصيل أدق وتريد أن تحافظ على الاختلاف بدل إخفائه.",None),
("cause_effect","ماذا يعلم الاختلاف نور عن الحكاية الشفوية؟","أنها قد تتغير مع الذاكرة ومع الشخص الذي يرويها.",None),
("single_word_definition","ما معنى «نسخة»؟","صورة أو صيغة أخرى من شيء أصلي أو مشترك.",["ar-r810"]),
("contrast","هل النسختان متطابقتان؟","لا، تتفقان في الحدث العام وتختلفان في بعض التفاصيل.",["ar-r810"]),
("reference_resolution","إلى ماذا تشير «بينهما» في نهاية النص؟","إلى نسختي الجد والخالة من القصة.",None),
("cloze_transfer","أكمل: عندي _____ إلكترونية من الكتاب.","نسخة",["ar-r810"]),
("inference","لماذا تصبح المقارنة نفسها جزءًا من القصة؟","لأن اختلاف الذاكرة يكشف كيف تنتقل الحكاية داخل العائلة.",None)
]},
{
"id":"ar-a2-u09-p03","sequence":51,"title":"عشاء في مطعم جديد","passage_type":"interleaved","genre":"social dining narrative","domains":["public","personal"],"topics":["restaurant","food customs","social expectations"],
"text":"دعت زميلة نور مجموعة صغيرة إلى مطعم يقدم أطعمة من منطقة لم يزرها معظمهم من قبل. قبل الذهاب قرأت نور قائمة الطعام على موقع المطعم حتى تعرف الخيارات، لكنها قررت ألا تختار كل شيء مسبقًا. عندما وصلوا شرح لهم الموظف أن بعض الأطباق توضع في وسط الطاولة ليشاركها الجميع، بينما يطلب كل شخص مشروبه بصورة منفصلة. سألت نور إذا كان هناك ترتيب محدد لتناول الأطباق، فقال الموظف إن المطعم يقترح البدء بأطباق صغيرة ثم الانتقال إلى الطبق الرئيسي، لكن الزبائن أحرار في الاختيار. لاحظت نور أن بعض أصدقائها كانوا قلقين من فعل شيء «خطأ»، فقالت إن السؤال البسيط أفضل من التخمين. خلال العشاء جربوا أطعمة مختلفة وتحدثوا عن الأطباق التي تشبه أطعمة يعرفونها وتلك التي كانت جديدة عليهم. في النهاية قالت نور إن زيارة مطعم جديد ليست اختبارًا لمعرفة كل العادات؛ يمكن للشخص أن يلاحظ ويسأل ويحترم طريقة المكان من غير أن يفترض أن كل مطعم أو كل أسرة تتصرف بالطريقة نفسها.",
"new":[927],
"reviews":[{"id":"ar-r595","form":"قائمة","review_stage":"R3","representation":"running_text"},{"id":"ar-r682","form":"اختيار","review_stage":"R3","representation":"running_text"},{"id":"ar-r723","form":"معظم","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-while-each","role":"new","description":"بينما + contrasting shared and individual ordering"},{"id":"ar-a2-free-to","role":"new","description":"أحرار في + action"}],
"discourse":[{"id":"a2-custom-without-overgeneralizing","role":"new","description":"learn a local dining practice without treating it as a universal cultural rule"}],
"qa":[
("gist","كيف تتعامل نور مع تجربة المطعم الجديد؟","تقرأ بعض المعلومات ثم تلاحظ وتسأل بدل أن تفترض أنها تعرف كل العادات.",None),
("literal_detail","كيف تقدم بعض الأطباق؟","توضع في وسط الطاولة ليشاركها الجميع.",None),
("vocabulary_in_context","ماذا يعني «مطعم»؟","مكان يقدم الطعام للزبائن مقابل الدفع.",["ar-r927"]),
("inference","لماذا تقول نور إن السؤال أفضل من التخمين؟","لأن المجموعة لا تعرف طريقة المكان، والسؤال يمنع افتراضات خاطئة.",None),
("contrast","هل يفرض المطعم ترتيبًا واحدًا لا يمكن تغييره؟","لا، يقترح ترتيبًا لكن الزبائن أحرار في الاختيار.",None),
("single_word_definition","ما معنى «مطعم»؟","مكان يعد الطعام ويقدمه للزبائن.",["ar-r927"]),
("cause_effect","كيف يقل قلق الأصدقاء أثناء العشاء؟","عندما يفهمون أن بإمكانهم السؤال وأنهم ليسوا أمام اختبار للعادات.",None),
("reference_resolution","إلى ماذا تشير «تلك» في «تلك التي كانت جديدة»؟","إلى الأطباق أو الأطعمة الجديدة عليهم.",None),
("cloze_transfer","أكمل: حجزنا طاولة في _____ قريب.","مطعم",["ar-r927"]),
("inference","ما الخطر في قول إن كل أسرة تتصرف بالطريقة نفسها؟","إنه تعميم غير دقيق؛ العادات قد تختلف بين الأسر والأماكن حتى داخل المجتمع نفسه.",None)
]},
{
"id":"ar-a2-u09-p04","sequence":52,"title":"حفل صغير بطريقتين","passage_type":"transfer","genre":"celebration comparison narrative","domains":["personal"],"topics":["celebration","family customs","comparison"],
"text":"احتفلت أسرة نور بتخرج ابنة عمها في نهاية العام. كان الحفل صغيرًا في البيت، مع طعام وصور وكلمات قصيرة من أفراد العائلة. بعد أسبوع حضرت نور حفل تخرج لصديقة في قاعة كبيرة، وكان البرنامج أكثر تنظيمًا: بدأ بكلمة ترحيب، ثم عُرضت صور، وبعد ذلك قُدمت الشهادات. لاحظت نور أن الحدثين يحتفلان بالإنجاز نفسه، لكن طريقة الاحتفال مختلفة. في حفل العائلة كان الناس يتحركون ويتحدثون بحرية، أما في القاعة فكان معظم الجمهور يجلس ويتبع ترتيب البرنامج. سألت نور أمها أي الطريقتين أفضل. قالت الأم إن السؤال لا يحتاج إلى جواب واحد؛ كل حفل يناسب الأشخاص والمكان والغرض. وأضافت أن بعض العائلات تحب طقوسًا متكررة، مثل صورة جماعية أو طبق معين، لكن هذه العادة يمكن أن تتغير من مناسبة إلى أخرى. قالت نور: إذن التشابه في الهدف لا يعني أن شكل الاحتفال يجب أن يكون واحدًا. يمكننا أن نفهم العادة من خلال ما يكرره الناس، لكننا لا نحولها إلى قاعدة لكل شخص.",
"new":[],
"reviews":[{"id":"ar-r761","form":"حفل","review_stage":"R3","representation":"running_text"},{"id":"ar-r977","form":"عادة","review_stage":"R3","representation":"running_text"},{"id":"ar-r965","form":"جمهور","review_stage":"R3","representation":"running_text"},{"id":"ar-r249","form":"مختلف","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-same-goal-different-form","role":"new","description":"نفس... لكن... مختلف"},{"id":"ar-a2-no-single-answer","role":"new","description":"لا يحتاج إلى جواب واحد"}],
"discourse":[{"id":"a2-celebration-comparison","role":"new","description":"compare two celebrations without ranking one as universally better"}],
"qa":[
("gist","ما الذي تقارنه نور؟","تقارن حفلًا عائليًا صغيرًا بحفل تخرج منظم في قاعة.",None),
("literal_detail","كيف كان الجمهور في القاعة؟","كان معظم الجمهور جالسًا ويتبع ترتيب البرنامج.",["ar-r965"]),
("contrast","ما الفرق الرئيسي بين الحفلين؟","الهدف متشابه لكن الشكل والتنظيم وطريقة مشاركة الناس مختلفة.",None),
("inference","لماذا لا تختار الأم حفلًا واحدًا باعتباره الأفضل دائمًا؟","لأن ملاءمة الحفل تعتمد على الأشخاص والمكان والغرض.",None),
("cause_effect","كيف تعرف نور أن شيئًا ما أصبح عادة؟","من ملاحظة أن الناس يكررونه في مناسبات متعددة.",["ar-r977"]),
("single_word_definition","ما معنى «حفل»؟","اجتماع أو مناسبة منظمة للاحتفال بشيء.",["ar-r761"]),
("reference_resolution","إلى ماذا تشير «هذه العادة»؟","إلى الطقس أو الفعل المتكرر في احتفالات العائلة، مثل الصورة أو الطبق.",None),
("inference","لماذا تحذر نور من تحويل العادة إلى قاعدة؟","لأن التكرار في مجموعة لا يعني أن جميع الناس يجب أن يفعلوا الشيء نفسه.",None),
("contrast","هل اختلاف الشكل يعني اختلاف هدف التخرج؟","لا، الحدثان يحتفلان بالإنجاز نفسه.",None),
("summary","لخص ما تعلمته نور عن الاحتفالات.","يمكن أن يكون الهدف واحدًا بينما تختلف طرق الاحتفال والعادات حسب الناس والمكان.",None)
]},
{
"id":"ar-a2-u09-p05","sequence":53,"title":"من يشرح العادة؟","passage_type":"checkpoint","genre":"community interview project","domains":["educational","public","personal"],"topics":["customs","interviews","community diversity"],
"text":"عمل صف نور على مشروع قصير بعنوان «أشياء نفعلها في المناسبات». في البداية أراد بعض الطلاب كتابة قائمة من العادات وكأن كل الناس في الحي يفعلونها بالطريقة نفسها. اقترحت المعلمة بدل ذلك أن يسأل كل طالب شخصين من أسر مختلفة عن مناسبة يعرفانها. سألت نور جدتها وجارة لأسرتها. تحدثت الجدة عن اجتماع العائلة حول الطعام، بينما ركزت الجارة على زيارة الأقارب في الصباح. اتفقتا في بعض الأشياء واختلفتا في أشياء أخرى. لم تقل نور إن إحداهما «أصح» من الأخرى، بل كتبت أن العادة قد تكون مشتركة عند بعض الناس ومختلفة عند غيرهم. عندما جمع الصف المقابلات ظهرت أنماط متكررة، لكن ظهرت استثناءات كثيرة أيضًا. قالت المعلمة: إذا أردنا الحديث عن المجتمع باحترام، من الأفضل أن نقول «بعض الأسر» أو «كثير من الناس» عندما يكون ذلك أدق من «الجميع». في العرض النهائي لم يقدم الطلاب قائمة جامدة، بل قدموا قصصًا قصيرة ومقارنات تبين أن الثقافة اليومية تُرى في الممارسات، لكنها ليست نسخة واحدة عند كل شخص.",
"new":[],
"reviews":[{"id":"ar-r794","form":"مجتمع","review_stage":"R3","representation":"running_text"},{"id":"ar-r812","form":"قصة","review_stage":"R2","representation":"running_text"},{"id":"ar-r810","form":"نسخة","review_stage":"R2","representation":"running_text"},{"id":"ar-r723","form":"معظم","review_stage":"R3","representation":"other"}],
"grammar":[{"id":"ar-a2-some-many-not-all","role":"new","description":"بعض الأسر / كثير من الناس versus الجميع"},{"id":"ar-a2-rather-than-list","role":"review","description":"بدل أن + overgeneralized description"}],
"discourse":[{"id":"a2-custom-evidence","role":"integration","description":"use multiple interviews to describe patterns while preserving variation and exceptions"}],
"qa":[
("gist","كيف يغير الصف طريقة مشروعه؟","ينتقل من قائمة تعميمية إلى مقابلات ومقارنات بين أسر مختلفة.",None),
("literal_detail","من الشخصان اللذان تسألهما نور؟","جدتها وجارة الأسرة.",None),
("inference","لماذا لا تقول نور إن إحدى الروايتين أصح؟","لأن العادات قد تختلف بين الأسر، وكل واحدة تصف ممارسة حقيقية في أسرتها.",None),
("cause_effect","كيف تساعد المقابلات المتعددة؟","تكشف أنماطًا مشتركة واختلافات واستثناءات لا تظهر في رواية واحدة.",None),
("contrast","لماذا قد تكون عبارة «بعض الأسر» أدق من «الجميع»؟","لأن السلوك لا يشمل بالضرورة كل أفراد المجتمع.",["ar-r794"]),
("reference_resolution","إلى ماذا تشير «إحداهما»؟","إلى الجدة والجارة، أو إلى روايتيهما عن المناسبة.",None),
("single_word_definition","ما معنى «مجتمع» في النص؟","مجموعة الناس والأسر الذين يعيشون ضمن المكان ويتفاعلون فيه.",["ar-r794"]),
("inference","ما المشكلة في تقديم الثقافة كنسخة واحدة؟","أنه يخفي اختلاف الناس والأسر ويحوّل الأنماط إلى قواعد غير دقيقة.",["ar-r810"]),
("summary","لخص الطريقة الأفضل التي يقترحها المشروع لوصف العادات.","نسأل عدة أشخاص، نذكر الأنماط المشتركة، ونحافظ على الاختلاف والاستثناء من غير تعميم زائد.",None),
("contrast","هل النمط المتكرر يساوي قاعدة بلا استثناء؟","لا، يمكن أن يكون شائعًا مع وجود اختلافات كثيرة.",None)
]},
{
"id":"ar-a2-u09-p06","sequence":54,"title":"الثقافة في التفاصيل اليومية","passage_type":"fluency","genre":"connected culture reflection","domains":["personal","public","educational"],"topics":["culture","customs","celebrations","review"],
"text":"أصبحت نور أكثر حذرًا عندما تتحدث عن العادات والثقافة. تعلمت من جدتها أن طبقًا عائليًا قد يحمل قصة تمتد إلى أشخاص وأماكن قديمة، لكن الوصفة نفسها يمكن أن تتغير. وعندما قارنت نسختين من حكاية واحدة، فهمت أن الذاكرة لا تحفظ التفاصيل بالطريقة نفسها عند كل شخص. وفي مطعم جديد رأت أن السؤال والملاحظة أفضل من افتراض أنها تعرف طريقة المكان مسبقًا. كما قارنت حفلين لهما الهدف نفسه لكنهما يختلفان في التنظيم وطريقة مشاركة الجمهور. وفي مشروع المدرسة اكتشفت أن الحديث عن المجتمع يحتاج إلى كلمات دقيقة: أحيانًا نقول «بعض الناس» أو «كثير من الأسر» بدل أن نقول «الجميع». لذلك لا ترى نور الثقافة كقائمة قوانين ثابتة. تراها في القصص والطعام والاحتفالات وطريقة استقبال الناس لبعضهم، لكنها تتوقع وجود نسخ مختلفة من الممارسة نفسها. وكلما أرادت أن تفهم عادة، تحاول أن تسأل: من يفعلها؟ متى؟ لماذا؟ وهل يفعلها الآخرون بالطريقة نفسها أم توجد طرق أخرى؟", 
"new":[],
"reviews":[{"id":"ar-r812","form":"قصة","review_stage":"R2","representation":"running_text"},{"id":"ar-r810","form":"نسخة","review_stage":"R2","representation":"running_text"},{"id":"ar-r927","form":"مطعم","review_stage":"R2","representation":"running_text"},{"id":"ar-r761","form":"حفل","review_stage":"R3","representation":"running_text"},{"id":"ar-r977","form":"عادة","review_stage":"R3","representation":"running_text"},{"id":"ar-r794","form":"مجتمع","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-u09-cumulative","role":"integration","description":"recycle stories, versions, custom comparison, cautious generalization, and cultural variation"}],
"discourse":[{"id":"a2-culture-fluency","role":"integration","description":"high-coverage cumulative reading about practices, stories, celebrations, and variation"}],
"qa":[
("gist","ما الفكرة الرئيسية في النص؟","نور تتعلم فهم العادات والثقافة من خلال القصص والممارسات مع تجنب التعميم على الجميع.",None),
("literal_detail","ماذا تعلمت من مقارنة نسختين من حكاية؟","أن الناس قد يتذكرون تفاصيل الحدث نفسه بصورة مختلفة.",["ar-r810"]),
("inference","لماذا تفضل نور السؤال في المطعم الجديد؟","لأن طريقة المكان قد تكون جديدة عليها ولا تريد الاعتماد على افتراضات.",["ar-r927"]),
("summary","لخص طريقة نور في فهم عادة جديدة.","تسأل من يمارسها ومتى ولماذا، وتقارن بين الناس بدل تحويل الممارسة إلى قاعدة ثابتة.",None),
("single_word_definition","ما معنى «قصة»؟","حكاية مترابطة عن أحداث أو تجارب.",["ar-r812"]),
("single_word_definition","ما معنى «نسخة» في الحكايات؟","صيغة أو رواية من القصة يمكن أن تختلف عن صيغة أخرى.",["ar-r810"]),
("contrast","هل الحفلان اللذان قارنت نور بينهما كانا متطابقين؟","لا، تشابه الهدف واختلف الشكل والتنظيم.",None),
("reference_resolution","إلى ماذا تشير «الممارسة نفسها»؟","إلى عادة أو سلوك ثقافي معين قد يظهر بصيغ مختلفة.",None),
("inference","لماذا لا ترى نور الثقافة كقائمة قوانين؟","لأن الممارسات تتغير بين الأسر والأماكن والأشخاص مع وجود أنماط مشتركة.",None),
("grammar_function","لماذا يستخدم النص أسئلة «من؟ متى؟ لماذا؟» في النهاية؟","لتقديم طريقة عملية لفحص العادة وسياقها قبل التعميم.",None)
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
    return {"id":x["id"],"language":"ar","cefr":"A2","unit":9,"sequence":x["sequence"],"revision":1,"title":x["title"],"passage_type":x["passage_type"],"genre":x["genre"],"domains":x["domains"],"topics":x["topics"],"text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r"[.!؟](?:\s|$)",text))),"estimated_known_token_coverage":0,"new_lexical_targets":[target(n,text,d) for n in x["new"]],"review_lexical_targets":x["reviews"],"grammar_targets":x["grammar"],"discourse_targets":x["discourse"],"questions":qs,"answer_key":ans,"speed_training":{"timed":x["passage_type"]=="fluency","benchmark_eligible":False,"comprehension_gate":0.8,"new_word_policy":"none" if x["passage_type"]=="fluency" else "controlled","notes":"A2 generation-stage passage; formal fluency/coverage decision deferred to final audit."},"quality":{"status":"draft","linguistic_review":"pending","pedagogical_review":"pending","coverage_check":"pending","answer_key_check":"pending","schema_check":"pending","fact_check":"not_required","notes":["High-quality A2 generation-stage draft; formal audits deferred to the final multi-pass review phase."]},"paired_text_group":None,"prerequisites":["Arabic A1 generation corpus","Arabic A2 Units 01-08 generation corpus"],"difficulty_notes_internal":"A2 Unit 09 generation draft: family stories, celebrations, social practices, comparison of versions, and cautious description of cultural patterns.","reader_tags":["unit_role:"+x["passage_type"],"generation_batch","a2"],"complexity_profile":{"mean_sentence_length":None,"median_sentence_length":None,"clause_count":None,"subordination_count":None,"coordination_count":None,"connective_diversity":None,"lexical_diversity":None,"reference_chain_max_distance":None,"multiword_expression_count":None,"morphology_notes":"A2 generation-stage draft; comparison, reported memory, and cautious generalization.","inference_depth":"local_to_two_sentence"}}
def main():
    old=[json.loads(x) for x in OUT.read_text(encoding="utf-8").splitlines() if x.strip()] if OUT.exists() else []
    old=[r for r in old if r.get("unit")!=9];d=lex();new=[build(x,d) for x in R]
    if len(new)!=6 or any(len(r["questions"])!=10 or len(r["answer_key"])!=10 for r in new):raise SystemExit("A2 Unit09 generation contract failed")
    rows=sorted(old+new,key=lambda r:(r.get("unit",0),r.get("sequence",0)))
    OUT.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    print("generated Arabic A2 Unit 09: six passages, sixty questions, sixty answers")
if __name__=="__main__":main()
