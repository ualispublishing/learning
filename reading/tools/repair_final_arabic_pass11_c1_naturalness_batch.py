#!/usr/bin/env python3
"""Apply only high-confidence manual Pass 11 MSA/naturalness repairs to C1."""
from __future__ import annotations
import copy,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/c1/passages.jsonl'
REPAIRS={
'ar-c1-u01-p04': [('لم يجروا وراء كل فرق بتفسير جديد','لم يسارعوا إلى وضع تفسير جديد لكل فرق')],
'ar-c1-u01-p05': [('لم تدّع وجود انحياز منشور','لم تدّع وجود انحياز في النشر')],
'ar-c1-u01-p06': [('بل حسبما جُمعت','بل كيف جُمعت'),('استخدمت سلمى خريطتها على دراسة خيالية جديدة','طبقت سلمى خريطتها على دراسة خيالية جديدة')],
'ar-c1-u02-p06': [('وأي أجزاء تحتاج إلى رأي من العقود والتدريب والعمليات','وأي أجزاء تحتاج إلى رأي مختصي العقود والتدريب والعمليات')],
'ar-c1-u03-p01': [('المطلوب تصميم رقابة تفترض التكيف وتستخدمه معلومة','المطلوب تصميم رقابة تفترض التكيف وتتعامل معه بوصفه معلومة')],
'ar-c1-u03-p04': [('قد تتحول المشاورة إلى طقس شرعي','قد تتحول المشاورة إلى طقس لإضفاء الشرعية')],
'ar-c1-u04-p01': [('لا قرارًا مغلقًا يورث تفسيره تلقائيًا إلى كل تحليل لاحق','لا قرارًا مغلقًا ينقل تفسيره تلقائيًا إلى كل تحليل لاحق')],
'ar-c1-u04-p03': [('ليست مجرد ضوضاء يجب متوسطها','ليست مجرد ضوضاء يجب أخذ متوسطها'),('قبول التسجيل نفسه قد يختار متحدثين أكثر راحة','قد يؤدي قبول التسجيل نفسه إلى اختيار متحدثين أكثر راحة')],
'ar-c1-u04-p06': [('وما العلاقات والأماكن التي تكررها العينة أكثر من غيرها؟','وما العلاقات والأماكن التي تتكرر في العينة أكثر من غيرها؟')],
'ar-c1-u05-p02': [('extrapolating المسار الأول إلى سنة كاملة','استقراء المسار الأول إلى سنة كاملة'),('قد يكون الأثر صغيرًا لكنه ثابتًا','قد يكون الأثر صغيرًا لكنه ثابت')],
'ar-c1-u05-p03': [('لم يكن البساطة معيارًا مطلقًا','لم تكن البساطة معيارًا مطلقًا')],
'ar-c1-u05-p05': [('منع هذا السلم من تغير اللغة بحسب الإثارة الإعلامية','حال هذا السلم دون تغير اللغة بحسب الإثارة الإعلامية'),('أو ظهر تفسير قياسي جديد','أو ظهر تفسير جديد متعلق بالقياس')],
'ar-c1-u05-p06': [('كما ناقشوا متى يحتاج القرار إلى الحركة قبل اختفاء كل الشك','كما ناقشوا متى يتطلب القرار التحرك قبل اختفاء كل الشك')],
'ar-c1-u06-p01': [('لم تستنتج اللجنة أن أي منصة بعيدة تكفي','لم تستنتج اللجنة أن أي منصة للمشاركة عن بعد تكفي')],
'ar-c1-u06-p02': [('علم ذلك اللجنة أن توفير طريق بديل على الورق لا يكفي','أوضح ذلك للجنة أن توفير طريق بديل على الورق لا يكفي'),('لذلك صارت أي وسيلة بديلة تقيم من حيث وجودها ووضوحها وزمن استخدامها معًا','لذلك صار تقييم أي وسيلة بديلة يعتمد على وجودها ووضوحها وزمن استخدامها معًا')],
'ar-c1-u06-p03': [('ثم ناقشت اللجنة خطر الجهة المقابلة','ثم ناقشت اللجنة الخطر المقابل'),('تعني استخدام حكم مبرر داخل هدف وحدود','تعني استخدام حكم مبرر ضمن هدف وحدود')],
'ar-c1-u07-p02': [('في البداية يطلب الشخصية الضوء ويمنع الصوت الخارجي','في البداية تطلب الشخصية الضوء وتمنع الصوت الخارجي')],
'ar-c1-u07-p03': [('إذا كانت عدم المطابقة نتيجة تقنية','إذا كان عدم التطابق نتيجة تقنية')],
'ar-c1-u07-p05': [('لكن القراءة الحالية يجب أن تحاسب على الأدلة المتاحة الآن','لكن يجب تقييم القراءة الحالية على أساس الأدلة المتاحة الآن')],
'ar-c1-u08-p01': [('توظيف مجموعة كبيرة أو توقيع عقد طويل لا يحمل مرونة شراء خدمة قصيرة يمكن إيقافها لاحقًا','توظيف مجموعة كبيرة أو توقيع عقد طويل لا يوفر مرونة شراء خدمة قصيرة يمكن إيقافها لاحقًا')],
'ar-c1-u08-p04': [('أصبح الافتراض أقل دقة لكنه أكثر صدقًا عن مقدار ما تسمح به البيانات','أصبح الافتراض أقل دقة لكنه أكثر صدقًا في تمثيل مقدار ما تسمح به البيانات')],
'ar-c1-u08-p05': [('سمت الأول أكثر صمودًا تحت الجهل الحالي','سمت الأول أكثر صمودًا في ظل الجهل الحالي')],
'ar-c1-u09-p03': [('فالغ absence يحتاج إلى تفسير أقوى','فالغياب يحتاج إلى تفسير أقوى')],
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(rows)!=60: raise RuntimeError(f'expected 60 C1 passages, got {len(rows)}')
by={r['id']:r for r in rows}
expected_repairs=sum(len(v) for v in REPAIRS.values())
if expected_repairs!=29: raise RuntimeError(expected_repairs)
applied=0;touched=[]
for pid,pairs in REPAIRS.items():
    r=by[pid]
    before_q=copy.deepcopy(r['questions']); before_a=copy.deepcopy(r['answer_key'])
    before_new=copy.deepcopy(r.get('new_lexical_targets',[])); before_review=copy.deepcopy(r.get('review_lexical_targets',[]))
    text=r['text']
    for old,new in pairs:
        count=text.count(old)
        if count!=1: raise RuntimeError(f'{pid}: expected one occurrence of {old!r}, got {count}')
        if new in text: raise RuntimeError(f'{pid}: replacement already present: {new!r}')
        text=text.replace(old,new,1); applied+=1
    r['text']=text
    r['word_count']=len(text.split())
    r['sentence_count']=len(re.findall(r'[.!؟]+',text))
    r['revision']=int(r.get('revision',1))+1
    note='Final Pass 11 manual naturalness review: applied only high-confidence MSA grammar/idiom/collocation repairs; assessment and lexical-target contracts unchanged.'
    notes=r.setdefault('quality',{}).setdefault('notes',[])
    if note not in notes:notes.append(note)
    if r['questions']!=before_q or r['answer_key']!=before_a:raise RuntimeError(f'{pid}: assessment drift')
    if r.get('new_lexical_targets',[])!=before_new:raise RuntimeError(f'{pid}: new-target metadata drift')
    if r.get('review_lexical_targets',[])!=before_review:raise RuntimeError(f'{pid}: review-target metadata drift')
    if not 500<=r['word_count']<=800:raise RuntimeError(f'{pid}: post-repair word count {r["word_count"]}')
    for t in r.get('new_lexical_targets',[]):
        if t['form'] not in r['text']:raise RuntimeError(f'{pid}: lost new target {t["form"]}')
    touched.append(pid)
if applied!=expected_repairs:raise RuntimeError((applied,expected_repairs))
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'level':'C1','passages_reviewed':60,'repairs_applied':applied,'passages_touched':len(touched),'touched_ids':touched},ensure_ascii=False))
