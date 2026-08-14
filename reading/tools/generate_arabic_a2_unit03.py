#!/usr/bin/env python3
"""Generate Arabic A2 Unit 03: past events and memories."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"reading"/"arabic"/"a2"/"passages.jsonl"; LEX=ROOT/"reading"/"lexicons"/"arabic.jsonl"
T={
865:("مؤخرا","recently; lately",["scenario_resolution"]),
868:("مجددا","again; once more",["parallel_structure"]),
872:("تسجيل","recording; registration",["scenario_resolution"]),
867:("نظرة","look; glance; view",["behavior_interpretation"]),
761:("حفل","party; ceremony; event",["scenario_resolution"]),
765:("زمن","time; period; era",["contrast"]),
723:("معظم","most; the majority of",["category_relation"]),
885:("ظن","thought; believed; assumption",["behavior_interpretation"]),
899:("أثر","trace; effect; impact",["cause_consequence"]),
897:("فاز","won",["cause_consequence"]),
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
"id":"ar-a2-u03-p01","sequence":13,"title":"صورة رأيتها مؤخرًا","passage_type":"instructional","genre":"photo-memory narrative","domains":["personal"],"topics":["memories","photos","family"],
"text":"عثرت نور مؤخرًا على صندوق قديم في خزانة بيت جدتها. كان فيه عدد من الصور التي لم ترها منذ سنوات. أخذت صورة يظهر فيها أفراد العائلة أمام بيت قديم وسألت جدتها عن المناسبة. نظرت الجدة إليها قليلًا ثم قالت إن الصورة التُقطت في يوم انتقلت فيه الأسرة إلى ذلك البيت. لم تتذكر نور ذلك اليوم جيدًا لأنها كانت صغيرة، لكنها تذكرت الشجرة الكبيرة عند الباب. أعطتها الصورة نظرة إلى فترة لا تحتفظ عنها بذكريات كثيرة. بعد أن عادت إلى بيتها فتحت الصورة مجددًا على هاتفها، لأنها كانت قد التقطت لها نسخة. لاحظت تفاصيل لم تنتبه إليها أول مرة: حقيبة سفر قرب الباب، وطفلًا يحمل لعبة، وجدها يضحك في الخلف. قالت نور: أحيانًا أحتاج إلى أن أنظر إلى الصورة مجددًا حتى أرى ما لم أره في النظرة الأولى.",
"new":[865,868],
"reviews":[{"id":"ar-r357","form":"صورة","review_stage":"R3","representation":"running_text"},{"id":"ar-r461","form":"لحظة","review_stage":"R3","representation":"other"}],
"grammar":[{"id":"ar-a2-recently","role":"new","description":"مؤخرًا with a completed recent event"},{"id":"ar-a2-again","role":"new","description":"مجددا for repeating an action"}],
"discourse":[{"id":"a2-photo-reconstruction","role":"new","description":"use repeated observation of a photo to reconstruct a past event"}],
"qa":[
("gist","ما الذي تتعلمه نور من الصورة القديمة؟","تتعرف إلى تفاصيل من يوم انتقال الأسرة إلى بيت قديم.",None),
("literal_detail","أين وجدت نور الصور؟","في صندوق قديم في خزانة بيت جدتها.",None),
("vocabulary_in_context","ماذا تعني «مؤخرًا»؟","في وقت قريب من الحاضر.",["ar-r865"]),
("vocabulary_in_context","لماذا تنظر نور إلى الصورة «مجددا»؟","لتراها مرة أخرى وتلاحظ تفاصيل جديدة.",["ar-r868"]),
("inference","لماذا تتذكر نور الشجرة أكثر من بقية اليوم؟","لأنها كانت صغيرة ولا تملك ذكريات كثيرة، لكن الشجرة بقيت تفصيلًا واضحًا في ذاكرتها.",None),
("single_word_definition","ما معنى «مؤخرًا»؟","في الفترة القريبة الماضية.",["ar-r865"]),
("single_word_definition","ما معنى «مجددا»؟","مرة أخرى.",["ar-r868"]),
("reference_resolution","إلى ماذا تشير «ذلك اليوم»؟","إلى يوم انتقال الأسرة إلى البيت القديم.",None),
("cloze_transfer","أكمل: زرت هذا المكان _____، أي قبل أيام قليلة.","مؤخرًا",["ar-r865"]),
("cloze_transfer","أكمل: لم أفهم الجملة، فقرأتها _____.","مجددا",["ar-r868"])
]},
{
"id":"ar-a2-u03-p02","sequence":14,"title":"صوت من الماضي","passage_type":"reinforcement","genre":"audio-memory narrative","domains":["personal"],"topics":["recording","family","memory"],
"text":"كانت والدة نور ترتب ملفات قديمة على الحاسوب عندما وجدت تسجيلًا صوتيًا من مناسبة عائلية قبل سبع سنوات. نادت نور وقالت: تعالي واسمعي هذا. بدأ التسجيل بصوت أطفال يضحكون، ثم سُمعت الجدة وهي تقرأ قصة قصيرة. توقفت نور عند جزء معين وقالت إنها تعرف ذلك الصوت، لكنها لم تتذكر متى سمعته أول مرة. أعادت الأم التسجيل من البداية، وطلبت من نور أن تأخذ نظرة إلى الصور المحفوظة في المجلد نفسه. عندما رأت الصور فهمت أن التسجيل كان من مساء قضوه في بيت خالتها. قالت نور: الصورة جعلت المكان واضحًا، لكن التسجيل أعاد إليّ الأصوات وطريقة كلام الناس. استمعتا إلى المقطع مرة أخرى، وفي كل مرة لاحظت نور شيئًا صغيرًا مختلفًا. في النهاية حفظت نسخة من التسجيل في هاتفها، ليس لأنه حدث مهم جدًا، بل لأنه جعل مساءً عاديًا من الماضي يبدو قريبًا مرة أخرى.",
"new":[872,867],
"reviews":[{"id":"ar-r865","form":"مؤخرا","review_stage":"R1","representation":"other"},{"id":"ar-r868","form":"مجددا","review_stage":"R1","representation":"running_text"},{"id":"ar-r357","form":"صورة","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-when-found","role":"new","description":"كان... عندما... to frame a past discovery"},{"id":"ar-a2-past-sequence","role":"new","description":"بدأ... ثم... عندما... in sustained past narrative"}],
"discourse":[{"id":"a2-multimodal-memory","role":"new","description":"combine audio and images to identify a past event"}],
"qa":[
("gist","كيف تتعرف نور إلى المناسبة الموجودة في التسجيل؟","تسمع التسجيل وتنظر إلى الصور المرتبطة به حتى تعرف المكان والمناسبة.",None),
("literal_detail","من يقرأ القصة في التسجيل؟","الجدة.",None),
("vocabulary_in_context","ماذا يعني «تسجيل صوتي»؟","ملف محفوظ يحتوي على أصوات حدث سابق.",["ar-r872"]),
("vocabulary_in_context","ماذا تعني «نظرة» في طلب الأم؟","إلقاء نظر على الصور لفحصها بسرعة أو بعناية.",["ar-r867"]),
("inference","لماذا كان التسجيل مفيدًا رغم وجود الصور؟","لأنه أعاد الأصوات وطريقة كلام الناس، وهي معلومات لا تظهر في الصورة.",None),
("single_word_definition","ما معنى «تسجيل» هنا؟","صوت أو صورة محفوظة يمكن تشغيلها لاحقًا.",["ar-r872"]),
("single_word_definition","ما معنى «نظرة»؟","مرة من النظر أو رؤية سريعة/مركزة لشيء.",["ar-r867"]),
("cause_effect","لماذا تفهم نور أن الحدث كان في بيت خالتها؟","لأن الصور الموجودة مع التسجيل أظهرت لها المكان.",None),
("cloze_transfer","أكمل: استمعت إلى _____ للمحاضرة بعد العودة إلى البيت.","تسجيل",["ar-r872"]),
("cloze_transfer","أكمل: ألقيت _____ على الخريطة قبل الخروج.","نظرة",["ar-r867"])
]},
{
"id":"ar-a2-u03-p03","sequence":15,"title":"حفل قبل سنوات","passage_type":"interleaved","genre":"family interview narrative","domains":["personal"],"topics":["celebration","family interview","past time"],
"text":"طلب المعلم من الطلاب أن يسألوا شخصًا كبيرًا في العائلة عن مناسبة يتذكرها من زمن مضى. اختارت نور جدها وسألته عن حفل تخرج عمها. قال الجد إن الحفل كان قبل أكثر من عشر سنوات، وإن العائلة استعدت له أيامًا. سألته نور ماذا يتذكر أكثر. قال إنه لا يتذكر كل التفاصيل، لكنه يتذكر انتظارهم خارج القاعة، ثم لحظة خروج ابنهم وهو يحمل الشهادة. وأضاف أن الزمن غيّر أشياء كثيرة؛ بعض الأشخاص الذين كانوا أطفالًا في الصور أصبحوا الآن في الجامعة، والمكان نفسه تغير. سألت نور: هل تتذكر الطعام أو الملابس؟ ضحك الجد وقال: أتذكر بعض الأشياء فقط، وليس كل ما حدث. كتبت نور ملاحظات بدل محاولة حفظ كلامه حرفيًا. بعد المقابلة فهمت أن الحديث عن حفل قديم لا يعني أن الشخص يتذكر كل لحظة؛ الذاكرة تحتفظ بأجزاء، بينما تكمل الصور والأسئلة أجزاء أخرى من القصة.",
"new":[761,765],
"reviews":[{"id":"ar-r872","form":"تسجيل","review_stage":"R1","representation":"other"},{"id":"ar-r867","form":"نظرة","review_stage":"R1","representation":"other"},{"id":"ar-r461","form":"لحظة","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-past-time-ago","role":"new","description":"قبل أكثر من... سنة for past distance"},{"id":"ar-a2-reported-memory","role":"new","description":"قال إنه يتذكر... / لا يتذكر..."}],
"discourse":[{"id":"a2-memory-interview","role":"new","description":"reconstruct a past celebration from an older person's partial memories"}],
"qa":[
("gist","ما المهمة التي تقوم بها نور؟","تجري مقابلة مع جدها عن مناسبة عائلية قديمة.",None),
("literal_detail","ما المناسبة التي يتحدث عنها الجد؟","حفل تخرج عم نور.",["ar-r761"]),
("vocabulary_in_context","ماذا يعني «حفل»؟","مناسبة يجتمع فيها الناس للاحتفال بحدث، وهنا التخرج.",["ar-r761"]),
("vocabulary_in_context","ماذا يعني «زمن مضى»؟","فترة من الوقت في الماضي.",["ar-r765"]),
("inference","لماذا تكتب نور ملاحظات؟","حتى تحفظ الأفكار المهمة من كلام جدها بدل الاعتماد على الذاكرة وحدها.",None),
("single_word_definition","ما معنى «حفل»؟","مناسبة أو اجتماع منظم للاحتفال بشيء.",["ar-r761"]),
("single_word_definition","ما معنى «زمن»؟","وقت أو فترة زمنية.",["ar-r765"]),
("contrast","هل يتذكر الجد كل تفاصيل الحفل؟","لا، يتذكر أجزاء محددة فقط.",None),
("cloze_transfer","أكمل: حضرنا _____ تخرج أخي العام الماضي.","حفل",["ar-r761"]),
("cloze_transfer","أكمل: تغير الحي كثيرًا مع مرور _____.","الزمن",["ar-r765"])
]},
{
"id":"ar-a2-u03-p04","sequence":16,"title":"ما الذي تذكره معظم الطلاب؟","passage_type":"transfer","genre":"class survey narrative","domains":["educational","personal"],"topics":["memory","school event","comparison"],
"text":"بعد رحلة مدرسية بأسبوع طلبت المعلمة من الطلاب أن يكتبوا ثلاثة أشياء يتذكرونها من الرحلة من غير أن ينظروا إلى الصور. عندما جمعوا الإجابات، لاحظوا أن معظم الطلاب كتبوا عن المكان المرتفع الذي شاهدوا منه المدينة. وذكر عدد كبير منهم وجبة الغداء، لكن تفاصيل أخرى ظهرت عند طلاب قليلين فقط. قالت مريم إنها كانت تظن أن الجميع سيتذكرون الحافلة القديمة لأنها أزعجتها طوال الطريق، لكنها اكتشفت أن معظم أصدقائها لم يذكروها أصلًا. بعد ذلك عرضت المعلمة صور الرحلة، فتذكر الطلاب أشياء جديدة لم يكتبوها في البداية. قالت: ما نتذكره من حدث واحد قد يختلف من شخص إلى آخر. أضافت نور: كنت أظن أن الذاكرة تشبه نسخة من الحدث، لكن يبدو أنها تختار بعض التفاصيل وتترك غيرها. احتفظ الصف بالقائمة الأولى ثم أضاف إليها ما تذكروه بعد رؤية الصور، فصار الفرق بين المرحلتين واضحًا.",
"new":[723,885],
"reviews":[{"id":"ar-r761","form":"حفل","review_stage":"R1","representation":"other"},{"id":"ar-r765","form":"زمن","review_stage":"R1","representation":"other"},{"id":"ar-r357","form":"صورة","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-most-people","role":"new","description":"معظم + plural noun"},{"id":"ar-a2-thought-that","role":"new","description":"ظن أن... for a past belief later revised"}],
"discourse":[{"id":"a2-memory-comparison","role":"new","description":"compare independent recollections before and after visual prompts"}],
"qa":[
("gist","ماذا يكتشف الصف عن الذاكرة؟","أن الناس قد يتذكرون تفاصيل مختلفة من الحدث نفسه وأن الصور قد تذكرهم بأشياء إضافية.",None),
("literal_detail","ما الشيء الذي ذكره معظم الطلاب؟","المكان المرتفع الذي شاهدوا منه المدينة.",["ar-r723"]),
("vocabulary_in_context","ماذا تعني «معظم الطلاب»؟","أكثر الطلاب أو الغالبية منهم، وليس الجميع بالضرورة.",["ar-r723"]),
("vocabulary_in_context","ماذا يعني «كنت أظن»؟","كان لدى نور اعتقاد في الماضي ثم تغير بعد التجربة.",["ar-r885"]),
("inference","لماذا تحتفظ المعلمة بالقائمة الأولى؟","حتى يقارن الطلاب ما تذكروه وحدهم بما تذكروه بعد رؤية الصور.",None),
("single_word_definition","ما معنى «معظم»؟","أغلب أو أكثر أفراد المجموعة.",["ar-r723"]),
("single_word_definition","ما معنى «ظن»؟","اعتقد أو حسب شيئًا من غير يقين كامل.",["ar-r885"]),
("contrast","هل «معظم» تعني «جميع» دائمًا؟","لا، تعني الأغلبية لا المجموعة كلها بالضرورة.",["ar-r723"]),
("cloze_transfer","أكمل: حضر _____ الطلاب إلى النشاط، لكن بعضهم غاب.","معظم",["ar-r723"]),
("cloze_transfer","أكمل: _____ أن المتجر مفتوح، لكنه كان مغلقًا.","ظننت",["ar-r885"])
]},
{
"id":"ar-a2-u03-p05","sequence":17,"title":"أثر مباراة قديمة","passage_type":"checkpoint","genre":"memory-and-result narrative","domains":["personal","public"],"topics":["sports memory","impact","past result"],
"text":"أثناء ترتيب غرفته وجد سامر تذكرة قديمة لمباراة حضرها مع أبيه عندما كان أصغر. لم يتذكر النتيجة فورًا، لكنه تذكر ازدحام الملعب وصوت الجمهور. أخذ التذكرة إلى أبيه وسأله عن ذلك اليوم. قال الأب إن فريقهما فاز في الدقائق الأخيرة، وإن سامر ظل يتحدث عن المباراة طوال الطريق إلى البيت. بحثا عن صورة قديمة من اليوم نفسه، فظهر سامر فيها وهو يحمل وشاح الفريق. قال سامر: الآن تذكرت الفوز، لكنني لم أتذكره قبل أن أرى الصورة. أجاب الأب: بعض الأحداث تترك أثرًا واضحًا، لكن تفاصيل الأثر قد تختفي ثم تعود عندما نرى شيئًا مرتبطًا بها. فكر سامر في كلامه. التذكرة نفسها لم تكن مهمة بسبب ثمنها، بل لأنها كانت أثرًا ماديًا يقوده إلى قصة أوسع: من كان معه، وما الذي شاهده، ولماذا كان سعيدًا بعد أن فاز الفريق. قرر الاحتفاظ بها في صندوق الصور بدل رميها.",
"new":[899,897],
"reviews":[{"id":"ar-r723","form":"معظم","review_stage":"R1","representation":"other"},{"id":"ar-r885","form":"ظن","review_stage":"R1","representation":"other"},{"id":"ar-r180","form":"مباراة","review_stage":"R3","representation":"running_text"},{"id":"ar-r290","form":"فوز","review_stage":"R3","representation":"running_text"}],
"grammar":[{"id":"ar-a2-when-younger","role":"new","description":"عندما كان أصغر for past-state framing"},{"id":"ar-a2-past-result","role":"new","description":"فاز + time/result detail"}],
"discourse":[{"id":"a2-object-memory-cue","role":"integration","description":"use a physical object and photo as cues to reconstruct a past event"}],
"qa":[
("gist","كيف يستعيد سامر تفاصيل المباراة القديمة؟","من خلال التذكرة وكلام أبيه وصورة من اليوم نفسه.",None),
("literal_detail","متى فاز الفريق؟","في الدقائق الأخيرة.",["ar-r897"]),
("vocabulary_in_context","ماذا يعني «أثرًا» عندما يصف الأب بعض الأحداث؟","علامة أو تأثيرًا يبقى من الحدث بعد انتهائه.",["ar-r899"]),
("vocabulary_in_context","ماذا يعني «فاز الفريق»؟","حقق الفريق النتيجة الأفضل وانتصر في المباراة.",["ar-r897"]),
("inference","لماذا يحتفظ سامر بالتذكرة رغم أن ثمنها ليس مهمًا؟","لأنها تذكره بالقصة والمشاعر والأشخاص المرتبطين بالمباراة.",None),
("single_word_definition","ما معنى «أثر»؟","علامة أو نتيجة أو تأثير يبقى من شيء حدث.",["ar-r899"]),
("single_word_definition","ما معنى «فاز»؟","حقق الفوز أو انتصر.",["ar-r897"]),
("cause_effect","ما الذي يجعل سامر يتذكر الفوز؟","رؤية الصورة بعد الحديث مع أبيه.",None),
("cloze_transfer","أكمل: تركت الرحلة _____ جميلًا في ذاكرتي.","أثرًا",["ar-r899"]),
("cloze_transfer","أكمل: _____ فريقنا في المباراة الأخيرة.","فاز",["ar-r897"])
]},
{
"id":"ar-a2-u03-p06","sequence":18,"title":"كيف نعيد بناء ذكرى؟","passage_type":"fluency","genre":"connected reflection on memory","domains":["personal","educational"],"topics":["memory","past events","evidence","review"],
"text":"بدأت نور مؤخرًا تهتم بالطريقة التي نتذكر بها الأحداث الماضية. اكتشفت أن صورة واحدة قد تجعلها تنظر إلى يوم قديم مجددًا، وأن تسجيلًا صوتيًا يعيد أصواتًا لا تستطيع الصورة حفظها. وعندما تسأل شخصًا عن حفل من زمن بعيد، لا تتوقع أن يتذكر كل التفاصيل؛ معظم الناس يحتفظون بأجزاء واضحة وأجزاء أخرى أقل وضوحًا. وقد تظن نور أن حدثًا ما وقع بطريقة معينة، ثم تغير رأيها عندما ترى دليلًا أو تسمع رواية شخص آخر. بعض الأشياء الصغيرة، مثل تذكرة أو رسالة، تبقى لأنها تحمل أثرًا من الماضي وتفتح بابًا لقصة أكبر. وإذا كان الحدث مباراة فاز فيها فريق تحبه الأسرة، فقد تتذكر المشاعر قبل أن تتذكر النتيجة نفسها. لذلك أصبحت نور ترى الذكرى كقصة نعيد بناءها من مصادر متعددة: ما نتذكره بأنفسنا، وما يقوله الآخرون، وما بقي من صور وتسجيلات وأشياء. كل مصدر يضيف جزءًا، ولا يحتاج أي واحد منها إلى أن يحمل القصة كاملة وحده.",
"new":[],
"reviews":[{"id":"ar-r865","form":"مؤخرا","review_stage":"R2","representation":"running_text"},{"id":"ar-r868","form":"مجددا","review_stage":"R2","representation":"running_text"},{"id":"ar-r872","form":"تسجيل","review_stage":"R2","representation":"running_text"},{"id":"ar-r867","form":"نظرة","review_stage":"R2","representation":"other"},{"id":"ar-r761","form":"حفل","review_stage":"R2","representation":"running_text"},{"id":"ar-r765","form":"زمن","review_stage":"R2","representation":"running_text"},{"id":"ar-r723","form":"معظم","review_stage":"R2","representation":"running_text"},{"id":"ar-r885","form":"ظن","review_stage":"R2","representation":"running_text"},{"id":"ar-r899","form":"أثر","review_stage":"R1","representation":"running_text"},{"id":"ar-r897","form":"فاز","review_stage":"R1","representation":"running_text"}],
"grammar":[{"id":"ar-a2-u03-cumulative","role":"integration","description":"recycle sustained past narration, reported memories, past beliefs, and evidence-based reconstruction"}],
"discourse":[{"id":"a2-memory-fluency","role":"integration","description":"high-coverage cumulative reading about reconstructing past events from multiple sources"}],
"qa":[
("gist","ما الفكرة الرئيسية في النص؟","الذكريات تُبنى من الذاكرة الشخصية ومن أدلة ومصادر متعددة مثل الصور والتسجيلات وكلام الآخرين.",None),
("literal_detail","ما الذي يضيفه التسجيل الصوتي ولا تضيفه الصورة بالطريقة نفسها؟","الأصوات وطريقة كلام الناس.",["ar-r872"]),
("inference","لماذا قد تغير نور رأيها عن حدث قديم؟","لأن دليلًا جديدًا أو رواية شخص آخر قد تكشف أن تصورها الأول لم يكن كاملًا.",["ar-r885"]),
("summary","لخص طريقة إعادة بناء الذكرى كما يصفها النص.","نجمع ما نتذكره مع الصور والتسجيلات والأشياء وكلام الآخرين حتى نحصل على قصة أكثر اكتمالًا.",None),
("single_word_definition","ما معنى «معظم»؟","أغلب أفراد مجموعة أو أكبر جزء منها.",["ar-r723"]),
("single_word_definition","ما معنى «أثر»؟","علامة أو تأثير باقٍ من حدث سابق.",["ar-r899"]),
("contrast","أيهما يحفظ الصوت مباشرة: صورة أم تسجيل؟","تسجيل.",["ar-r872"]),
("reference_resolution","إلى ماذا تشير «كل مصدر» في الجملة الأخيرة؟","إلى الذاكرة الشخصية وكلام الآخرين والصور والتسجيلات والأشياء المرتبطة بالماضي.",None),
("grammar_function","ماذا تفعل «ثم» ضمنيًا في فكرة تغير رأي نور بعد دليل جديد؟","تربط تصورًا سابقًا بنتيجة أو فهم لاحق تغير بسبب معلومات جديدة.",None),
("inference","لماذا لا يحتاج مصدر واحد إلى حمل القصة كاملة؟","لأن المصادر المختلفة تكمل بعضها وتقدم أنواعًا مختلفة من التفاصيل.",None)
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
    return {"id":x["id"],"language":"ar","cefr":"A2","unit":3,"sequence":x["sequence"],"revision":1,"title":x["title"],"passage_type":x["passage_type"],"genre":x["genre"],"domains":x["domains"],"topics":x["topics"],"text":text,"word_count":len(text.split()),"sentence_count":max(1,len(re.findall(r"[.!؟](?:\s|$)",text))),"estimated_known_token_coverage":0,"new_lexical_targets":[target(n,text,d) for n in x["new"]],"review_lexical_targets":x["reviews"],"grammar_targets":x["grammar"],"discourse_targets":x["discourse"],"questions":qs,"answer_key":ans,"speed_training":{"timed":x["passage_type"]=="fluency","benchmark_eligible":False,"comprehension_gate":0.8,"new_word_policy":"none" if x["passage_type"]=="fluency" else "controlled","notes":"A2 generation-stage passage; formal fluency/coverage decision deferred to final audit."},"quality":{"status":"draft","linguistic_review":"pending","pedagogical_review":"pending","coverage_check":"pending","answer_key_check":"pending","schema_check":"pending","fact_check":"not_required","notes":["High-quality A2 generation-stage draft; formal audits deferred to the final multi-pass review phase."]},"paired_text_group":None,"prerequisites":["Arabic A1 generation corpus","Arabic A2 Units 01-02 generation corpus"],"difficulty_notes_internal":"A2 Unit 03 generation draft: sustained past narration, partial memories, evidence, and multi-source reconstruction.","reader_tags":["unit_role:"+x["passage_type"],"generation_batch","a2"],"complexity_profile":{"mean_sentence_length":None,"median_sentence_length":None,"clause_count":None,"subordination_count":None,"coordination_count":None,"connective_diversity":None,"lexical_diversity":None,"reference_chain_max_distance":None,"multiword_expression_count":None,"morphology_notes":"A2 generation-stage draft; sustained past narration and reported recollection.","inference_depth":"local_to_two_sentence"}}

def main():
    existing=[json.loads(line) for line in OUT.read_text(encoding="utf-8").splitlines() if line.strip()] if OUT.exists() else []
    existing=[r for r in existing if r.get("unit")!=3]
    d=lex();new=[build(x,d) for x in R]
    if len(new)!=6 or any(len(r["questions"])!=10 or len(r["answer_key"])!=10 for r in new):raise SystemExit("A2 Unit03 generation contract failed")
    rows=sorted(existing+new,key=lambda r:(r.get("unit",0),r.get("sequence",0)))
    OUT.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    print("generated Arabic A2 Unit 03: six passages, sixty questions, sixty answers")
if __name__=="__main__":main()
