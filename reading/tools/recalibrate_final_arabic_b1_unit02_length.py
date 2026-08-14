#!/usr/bin/env python3
"""Final-review remediation: expand B1 Unit 02 into the documented 220-350 word band.

Additions deepen causal diagnosis, side-effect monitoring, shared-reference
repair, perspective updating, contingency redesign, and cumulative transfer.
No deliberate lexical target set is changed.
"""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/arabic/b1/passages.jsonl'
ADD={
'ar-b1-u02-p01': """بعد أن سلّموا التقرير، لم يكتفوا بالقاعدة الجديدة على الورق. جرّبوها في مهمة قصيرة في الأسبوع التالي: أنشأوا ملفًا واحدًا باسم واضح، وحددوا وقتًا لإغلاق التعديلات، ثم طلبوا من شخص آخر التأكد من أن كل جزء موجود قبل الإرسال. ظهر خطأ صغير هذه المرة أيضًا، لكنهم اكتشفوه قبل الموعد لأن المسؤول عرف أين يبحث. عندها فهمت نور أن معرفة السبب الحقيقي لا تعني العثور على شخص آخر للومه؛ بل تعني تحديد النقطة التي يمكن تغييرها في طريقة العمل بحيث يصبح الخطأ أقل احتمالًا أو أسهل اكتشافًا.""",
'ar-b1-u02-p02': """ولكي تعرف المدرسة هل التعديل الجديد أفضل فعلًا، لم تعتمد على انطباع يوم واحد. سجلت لمدة أسبوع عدد الطلاب الذين ينتظرون عند كل باب، وعدد السيارات التي تتوقف في الشارع الجانبي، والوقت الذي يستغرقه خروج آخر مجموعة. لاحظت أن تأخير بعض الصفوف خمس دقائق خفف التجمع، لكنه جعل مجموعة من الإخوة تنتظر مدة أطول حتى يخرجوا معًا. أضافت المدرسة مكان انتظار صغيرًا لهم. أظهر ذلك أن تقييم الحل يحتاج إلى أكثر من رقم واحد، لأن تحسين حركة الطلاب قد يخلق كلفة مختلفة لأسرة أو شارع أو مجموعة أخرى.""",
'ar-b1-u02-p03': """بعد الحادثة جربت هدى ثلاث صيغ للرسالة نفسها. كتبت أولًا: «نلتقي عند الباب القديم»، ثم: «نلتقي عند الباب القديم قرب الصيدلية»، وأخيرًا أرسلت اسم المكان على الخريطة. أعطت الرسائل لصديقة لم تزر المنطقة من قبل وسألتها أي صيغة تسمح لها بالوصول بلا سؤال إضافي. كانت الصيغة الثانية أوضح، لكن الخريطة حسمت المرجع تمامًا. تعلمت هدى أن وضوح الرسالة لا يقاس فقط بسلامة كلماتها، بل بقدرة شخص لا يشارك الكاتب معرفته السابقة على تحديد الشخص أو المكان أو الوقت المقصود.""",
'ar-b1-u02-p04': """بعد أن هدأت مريم، فكرت في طريقة تتجنب بها التفسير السريع في المواقف المشابهة. قررت أن تكتب في ذهنها احتمالين على الأقل عندما لا تعرف سبب قرار ما: قد يكون القرار متعلقًا بأدائها، وقد يكون مرتبطًا بجدول أو شرط لم تره. هذا لا يعني أن تتجاهل شعورها أو تتخلى عن حقها في الاعتراض، بل أن تعرف أولًا ما الذي تعترض عليه. وعندما شرحت لها نور طريقة الاختيار، استطاعت مريم أن تفرق بين معلومة غيّرت معنى القرار ومعلومة لا تغيره. لذلك بقي اهتمامها بالمشاركة، لكن سبب غضبها الأول لم يعد قائمًا.""",
'ar-b1-u02-p05': """قبل الموافقة النهائية على الخطة الداخلية، رسم الطلاب مخططًا بسيطًا للقاعة. اكتشفوا أن تقسيم العروض إلى فترتين لا يكفي إذا بقي المدخل نفسه مزدحمًا، فوضعوا مسارًا للدخول وآخر للخروج وحددوا عدد الزوار في كل فترة. كما اختاروا الأنشطة التي يمكن تصغيرها من دون أن تفقد فكرتها الأساسية، وأبقوا نشاطًا واحدًا خارج البرنامج لأنه يحتاج إلى مساحة لا توجد في القاعة. بهذا لم يصبح البديل نسخة أصغر من الخطة القديمة، بل تصميمًا جديدًا يحقق الهدف نفسه ضمن حدود مختلفة. وعندما هطل المطر، عرفوا مسبقًا ما الذي سيتغير وما الذي سيبقى.""",
'ar-b1-u02-p06': """يمكن استخدام أسئلة قصيرة لتمييز أنواع التعقيد قبل القفز إلى الحل. إذا اختفى عمل من ملف، نسأل أولًا عن مسار العمل والنسخة المعتمدة. وإذا كان الحل يحسن مكانًا ويضر مكانًا آخر، نراقب أكثر من نتيجة. وإذا اختلف شخصان حول رسالة، نبحث عن المرجع الذي لا يشتركان فيه. وإذا تغير موقف بعد معلومة جديدة، نسأل هل تغيرت الوقائع أم تغير تفسيرها. أما عندما تتبدل الظروف نفسها، فقد لا يكفي استبدال خيار بآخر؛ ربما يجب إعادة تصميم الخطة. تساعد هذه الأسئلة على اختيار نوع الفحص المناسب بدل استعمال علاج واحد لكل مشكلة.""",
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()];by={r['id']:r for r in rows};results=[]
for pid,addition in ADD.items():
 r=by[pid];assert addition.strip() not in r['text']
 old_wc=len(r['text'].split());r['text']=r['text'].rstrip()+' '+addition.strip();new_wc=len(r['text'].split())
 assert 220<=new_wc<=350,(pid,old_wc,new_wc)
 if pid.endswith('-p06'):assert not r.get('new_lexical_targets'),(pid,r.get('new_lexical_targets'))
 r['word_count']=new_wc;r['sentence_count']=len([s for s in re.split(r'(?<=[.!؟])\s+',r['text']) if s.strip()]);r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final Pass 07 remediation: expanded B1 Unit 02 with passage-specific causal evidence, side-effect monitoring, reference repair, perspective updating, contingency redesign, and transfer while preserving deliberate target sets.'
 if note not in notes:notes.append(note)
 results.append({'passage_id':pid,'old_word_count':old_wc,'new_word_count':new_wc,'added_words':new_wc-old_wc})
assert len(results)==6
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'level':'B1','unit':2,'repairs':results,'all_in_standard_band':all(220<=x['new_word_count']<=350 for x in results)},ensure_ascii=False))
