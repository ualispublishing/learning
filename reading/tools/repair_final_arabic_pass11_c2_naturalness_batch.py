#!/usr/bin/env python3
"""Apply only high-confidence manual Pass 11 MSA/naturalness repairs to C2."""
from __future__ import annotations
import copy,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/c2/passages.jsonl'
TITLE_REPAIRS={
'ar-c2-u02-p04':[('الخصم والإجراء ذي الطابع الجنائي','الخصم والإجراء ذو الطابع الجنائي')],
}
REPAIRS={
'ar-c2-u01-p02':[('النظرية كلها باطل','كل ما في النظرية باطل')],
'ar-c2-u01-p05':[('بحيث يجعل الوفاء الحرفي أثرًا غير عادل على طرف','بحيث يترتب على الوفاء الحرفي أثر غير عادل على طرف'),('كما ناقشوا الفعل تحت الوقت الضيق','كما ناقشوا الفعل في ظل ضيق الوقت')],
'ar-c2-u01-p06':[('لأن الصياغة قد تكون باطلًا في عمومها','لأن الحكم العام على الصياغة قد يكون باطلًا'),('إذا لم يستطيع الطالب','إذا لم يستطع الطالب')],
'ar-c2-u02-p01':[('لأن جميعها زمني','لأن جميعها زمنية')],
'ar-c2-u02-p03':[('الحدث الذي يفعله','الحدث الذي ينظمه')],
'ar-c2-u02-p04':[('يترأس القرار النهائي','يتولى اتخاذ القرار النهائي')],
'ar-c2-u02-p05':[('إن الرسالة تزوير','إن في الرسالة تزويرًا'),('النزاع الجيد التحليل','التحليل الجيد للنزاع'),('مقدار الحمل الذي تضعه الحجة على ذلك الدليل','مدى اعتماد الحجة على ذلك الدليل')],
'ar-c2-u02-p06':[('وفي مطالبة تعتمد وثيقة يقال إنها تزوير','وفي مطالبة تعتمد وثيقة يقال إن فيها تزويرًا'),('ثلاثة خرائط متداخلة','ثلاث خرائط متداخلة'),('صار الطلاب قادرين على ذكر ليس فقط القراءة التي يفضلونها، بل الحلقة التي إذا تغيرت ستجعلهم يغيرون ذلك التفضيل','صار الطلاب قادرين على ذكر القراءة التي يفضلونها، وكذلك الحلقة التي إذا تغيرت ستجعلهم يغيرون ذلك التفضيل')],
'ar-c2-u03-p01':[('لا واحد من هذه الأسباب يحول التفضيل العملي تلقائيًا','ولا يحول أي من هذه الأسباب التفضيل العملي تلقائيًا')],
'ar-c2-u03-p02':[('يجب أن نعرف أيضًا النموذج الذي يحول الإشارة إلى كمية ومع الشروط التي يظل فيها التحويل صالحًا','يجب أن نعرف أيضًا النموذج الذي يحول الإشارة إلى كمية، والشروط التي يظل فيها التحويل صالحًا'),('على فشل كل الطريقة','على فشل الطريقة كلها')],
'ar-c2-u03-p03':[('لا ملحق بعدي','لا ملحق لاحق')],
'ar-c2-u03-p04':[('يمثل كل خلية كنقطة','يمثل كل خلية بنقطة'),('تتغير بسرعة أصغر','تتغير بوتيرة أبطأ')],
'ar-c2-u03-p05':[('كلتيهما تستخدم المصدر الأساسي نفسه أو نفس إجراء التنظيف','كلتيهما تستخدم المصدر الأساسي نفسه أو إجراء التنظيف نفسه'),('بل بتنوع الطرق التي يمكن أن تفشل بها الحجة ثم بقائها بعد اختبارات','بل بتنوع الطرق التي يمكن أن تفشل بها الحجة، ثم ببقائها بعد اختبارات')],
'ar-c2-u03-p06':[('وفي القياس قد تكون كيمياء الحساس والإشارة الخام مصدرين يحتاجان إلى فصل قبل تفسير الانحياز يجعل القراءات ثابتة وغير صحيحة في الوقت نفسه','وفي القياس قد تكون كيمياء الحساس والإشارة الخام عاملين يحتاجان إلى الفصل بينهما قبل تفسير انحياز يجعل القراءات ثابتة وغير صحيحة في الوقت نفسه')],
'ar-c2-u04-p02':[('نتيجة اقتصادية على فترة','نتيجة اقتصادية على مدى فترة'),('الأولى تحتاج إلى تمويل العامل الزمني أكثر من الثانية','الأولى تحتاج إلى تمويل الفجوة الزمنية أكثر من الثانية')],
'ar-c2-u04-p03':[('وتفاوض الموردين','وتتفاوض مع الموردين')],
'ar-c2-u04-p04':[('يحجز طاقة مقدمة بعقود مرنة','يحجز قدرة إنتاجية مقدمًا بعقود مرنة')],
'ar-c2-u04-p05':[('أن يشترى الآخرون غدًا','أن يشتري الآخرون غدًا'),('لم يمكن الإجابة من النسبة وحدها','لم يكن من الممكن الإجابة من النسبة وحدها')],
'ar-c2-u04-p06':[('المؤشرات القائدة والمؤشرات المتأخرة','المؤشرات الاستباقية والمؤشرات المتأخرة'),('حساسية لا يخفى خلف رقم متوسط','حساسية لا تخفى خلف رقم متوسط')],
'ar-c2-u05-p01':[('حول ما يحتاج إلى التركيز','حول ما ينبغي التركيز عليه'),('اعتراض اعتراضي بين شرطتين','جملة اعتراضية بين شرطتين')],
'ar-c2-u05-p03':[('وإذا لا يظهر ذلك إلا بعد المشهد','وإذا لم يظهر ذلك إلا بعد المشهد'),('فصل الاقتصاد المنتج من الفراغ غير المنظم','فصل الاقتصاد المنتج عن الفراغ غير المنظم')],
'ar-c2-u05-p04':[('اعترضت المحررة سارة: وقالت إن التقييم الموضوعي','وقالت إن التقييم الموضوعي'),('وناقشت الفريق مسألة الجمهور','وناقش الفريق مسألة الجمهور')],
'ar-c2-u05-p06':[('اختياره المباشرة والترتيب نفسه قرار شكلي','اختيار المباشرة والترتيب نفسه قرار شكلي'),('استقبله كما أريد','استقبله كما كان مقصودًا')],
'ar-c2-u06-p01':[('مؤشرات سباقة مثل عمر المعدات','مؤشرات استباقية مثل عمر المعدات')],
'ar-c2-u06-p02':[('بأن النظامي في القرار لا يتعلق بالعدد فقط','بأن الجانب النظامي في القرار لا يتعلق بالعدد فقط')],
'ar-c2-u06-p03':[('النتائج التي لا يملك المفاوض قبول خلافها','النتائج التي لا يملك المفاوض قبول ما يخالفها')],
'ar-c2-u06-p05':[('يجعل المشاركة عقلانية أقل','يجعل المشاركة أقل عقلانية')],
'ar-c2-u06-p06':[('ومع ذلك يجمع الوقت والمقياس ليجعل غيابهم أقل ظهورًا','ومع ذلك يجتمع الوقت والمقياس ليجعلا غيابهم أقل ظهورًا'),('إذا نعم، تحتاج المؤسسة','إذا كان الجواب نعم، تحتاج المؤسسة')],
'ar-c2-u07-p01':[('هل تصبح المصباح علامة تماسك','هل يصبح المصباح علامة تماسك'),('يتعمد الأصل أن يترك هل الجملة تهديد أم مزاحًا مفتوحًا','يتعمد الأصل أن يترك مسألة ما إذا كانت الجملة تهديدًا أم مزاحًا مفتوحة')],
'ar-c2-u07-p04':[('عن ما يستحق البقاء','عما يستحق البقاء')],
'ar-c2-u08-p01':[('استخدمته مصدرًا عن إعادة تفسير الماضي','استخدمته مصدرًا لدراسة إعادة تفسير الماضي')],
'ar-c2-u08-p03':[('أن أحد الزخارف قد أُعيد استخدامه','أن إحدى الزخارف قد أُعيد استخدامها')],
'ar-c2-u08-p04':[('اعتمد تاريخ قديم على هذه اليوميات','اعتمد مؤرخ قديم على هذه اليوميات')],
'ar-c2-u08-p05':[('لأنه واضح الوثيقة','لأنه موثق بوضوح')],
'ar-c2-u09-p02':[('هي الحفاظ على قدرة المستقبل على الاختيار','هي الحفاظ على قدرة المؤسسة على الاختيار مستقبلًا'),('إذا استخدم الفريق المتوسطات منفصلة، يقلل خطر الاجتماع','إذا استخدم الفريق المتوسطات منفصلة، فإنه يقلل من تقدير خطر اجتماعها')],
'ar-c2-u09-p04':[('لم يكن هناك عطل برمجي في كل جزء منفصل','لم يكن هناك عطل برمجي في أي جزء منفرد')],
'ar-c2-u09-p05':[('وفتح قناة بلاغ تسمح','وفتح قناة للإبلاغ تسمح'),('الحالات التي لا يناسبها النظام الجديد فترة معينة','الحالات التي لا يناسبها النظام الجديد خلال فترة معينة')],
'ar-c2-u09-p06':[('إذا كان الخبر السلبي يقع في أثر اعتبروه','إذا كان الخبر السلبي يتعلق بأثر اعتبروه')],
'ar-c2-u10-p02':[('كتبوا نسبًا للبيانات وراقبوا متى تتغير خصائصها','وثقوا مصادر البيانات ومساراتها وراقبوا متى تتغير خصائصها')],
'ar-c2-u10-p03':[('أضافوا أمثلة حالة','أضافوا أمثلة لحالات')],
'ar-c2-u10-p04':[('بقي بعض الحي منخفضًا في كل الحالات','بقي تقدير الحي منخفضًا في كل الحالات')],
'ar-c2-u10-p06':[('وفي السادس ميزوا الأداء الحالي من سهولة الاعتراض','وفي السادس ميزوا الأداء الحالي عن سهولة الاعتراض'),('ممنوع تجاهله فقط لأنه غير مريح','ولا يجوز تجاهله لمجرد أنه غير مريح')],
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(rows)!=60: raise RuntimeError(f'expected 60 C2 passages, got {len(rows)}')
if [r.get('sequence') for r in rows]!=list(range(1,61)): raise RuntimeError('C2 sequence drift')
if any(r.get('cefr')!='C2' for r in rows): raise RuntimeError('non-C2 row in C2 corpus')
by={r['id']:r for r in rows}
expected_repairs=sum(len(v) for v in REPAIRS.values())+sum(len(v) for v in TITLE_REPAIRS.values())
if expected_repairs!=64: raise RuntimeError(expected_repairs)
applied=0;touched=[]
all_pids=sorted(set(REPAIRS)|set(TITLE_REPAIRS))
for pid in all_pids:
    r=by[pid]
    before=copy.deepcopy(r)
    before_occ={('new',t['id']):r['text'].count(t['form']) for t in r.get('new_lexical_targets',[])}
    before_occ.update({('review',t['id']):r['text'].count(t['form']) for t in r.get('review_lexical_targets',[])})
    title=r['title']
    for old,new in TITLE_REPAIRS.get(pid,[]):
        count=title.count(old)
        if count!=1: raise RuntimeError(f'{pid}: expected one title occurrence of {old!r}, got {count}')
        title=title.replace(old,new,1);applied+=1
    text=r['text']
    for old,new in REPAIRS.get(pid,[]):
        count=text.count(old)
        if count!=1: raise RuntimeError(f'{pid}: expected one text occurrence of {old!r}, got {count}')
        remainder=text.replace(old,'',1)
        if new in remainder: raise RuntimeError(f'{pid}: replacement already present outside target occurrence: {new!r}')
        text=text.replace(old,new,1);applied+=1
    r['title']=title;r['text']=text
    r['word_count']=len(text.split())
    r['sentence_count']=len(re.findall(r'[.!؟]+',text))
    r['revision']=int(r.get('revision',1))+1
    note='Final Pass 11 manual naturalness review: applied only high-confidence C2 MSA grammar/idiom/collocation repairs; assessment, speed-training, and lexical-target contracts unchanged.'
    notes=r.setdefault('quality',{}).setdefault('notes',[])
    if note not in notes:notes.append(note)
    if r['questions']!=before['questions'] or r['answer_key']!=before['answer_key']:raise RuntimeError(f'{pid}: assessment drift')
    if r.get('new_lexical_targets',[])!=before.get('new_lexical_targets',[]):raise RuntimeError(f'{pid}: new-target metadata drift')
    if r.get('review_lexical_targets',[])!=before.get('review_lexical_targets',[]):raise RuntimeError(f'{pid}: review-target metadata drift')
    if r.get('speed_training')!=before.get('speed_training'):raise RuntimeError(f'{pid}: speed-training drift')
    after_occ={('new',t['id']):r['text'].count(t['form']) for t in r.get('new_lexical_targets',[])}
    after_occ.update({('review',t['id']):r['text'].count(t['form']) for t in r.get('review_lexical_targets',[])})
    if after_occ!=before_occ:raise RuntimeError(f'{pid}: lexical literal occurrence drift: {before_occ} -> {after_occ}')
    if not 700<=r['word_count']<=1200:raise RuntimeError(f'{pid}: post-repair word count {r["word_count"]}')
    if re.search(r'[A-Za-z]',r['title']) or re.search(r'[A-Za-z]',r['text']):raise RuntimeError(f'{pid}: Latin reader-text intrusion')
    touched.append(pid)
if applied!=expected_repairs:raise RuntimeError((applied,expected_repairs))
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'level':'C2','passages_reviewed':60,'repairs_applied':applied,'passages_touched':len(touched),'touched_ids':touched},ensure_ascii=False))
