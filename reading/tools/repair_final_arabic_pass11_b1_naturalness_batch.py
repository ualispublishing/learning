#!/usr/bin/env python3
"""Apply only passage-scoped, high-confidence B1 Pass-11 MSA repairs.

The 60 canonical B1 texts were manually read after Pass-03/07 recalibration.
Each replacement below is exact and asserted to occur once in the named field;
there is no broad stylistic rewrite. The script preserves the B1 220-350 word
planning band, 10 linked Q/A, and all lexical-target metadata.
"""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/b1/passages.jsonl'

# (passage_id, field, old, new)
REPAIRS=[
('ar-b1-u01-p01','text','ووقت الدرس مناسبًا من حيث المبدأ','وكان وقت الدرس مناسبًا من حيث المبدأ'),
('ar-b1-u01-p04','text','دليلًا قاطعًا أن الطريقة الثانية أفضل','دليلًا قاطعًا على أن الطريقة الثانية أفضل'),
('ar-b1-u02-p02','text','لم تختف كل الزحمة، إلا أن الحركة أصبحت أكثر انتظامًا','لم يختف الازدحام تمامًا، إلا أن الحركة أصبحت أكثر انتظامًا'),
('ar-b1-u02-p03','text','كانت هدى تقف عند باب آخر أقدم من المبنى نفسه','كانت هدى تقف عند باب آخر هو الأقدم في المبنى نفسه'),
('ar-b1-u03-p01','text','الرسالة التي تتطلب فعلًا في اليوم نفسه','الرسالة التي تتطلب إجراءً في اليوم نفسه'),
('ar-b1-u03-p02','text','لأن المتحدث تحرك بسرعة وأظهر نتيجة ناجحة','لأن المتحدث انتقل بسرعة بين الخطوات وأظهر نتيجة ناجحة'),
('ar-b1-u03-p06','text','لذلك لم تحاول نور أن تصبح أقل استخدامًا للتقنية في كل شيء.','لذلك لم تحاول نور أن تقلل استخدام التقنية في كل شيء.'),
('ar-b1-u04-p02','text','إزالة المخلفات الموجودة، وتقليل السرعة التي تعود بها','إزالة المخلفات الموجودة، وإبطاء عودتها'),
('ar-b1-u04-p05','text','أن إحدى قاعات المدرسة تصبح ثقيلة الهواء','أن الهواء في إحدى قاعات المدرسة يصبح ثقيلًا'),
('ar-b1-u04-p05','text','ومعرفة إن كان التعديل يعطي أثرًا متكررًا','ومعرفة إن كان التعديل يؤدي إلى أثر متكرر'),
('ar-b1-u04-p06','text','فائدة عامة يمكن أن توزع تكاليفها بشكل غير متساو','فائدة عامة قد تتوزع تكاليفها بشكل غير متساو'),
('ar-b1-u05-p01','text','الأيام التي وصف فيها جسمه بأنه أكثر تعبًا','الأيام التي وصف فيها نفسه بأنه أكثر تعبًا'),
('ar-b1-u05-p01','text','في بعض الأيام القصيرة النوم','في بعض الأيام التي قل فيها نومه'),
('ar-b1-u05-p04','text','طلبت المعلمة منهما مقارنة ظروف الاختبارين.','طلبت المعلمة من الطلاب مقارنة ظروف الاختبارين.'),
('ar-b1-u05-p05','text','ما المعلومات التي سيحتاجها بحث أوسع','ما المعلومات التي سيحتاج إليها بحث أوسع'),
('ar-b1-u06-p01','text','أعطتها انطباعًا أن الحي موجود أساسًا للزوار','أعطتها انطباعًا بأن الحي موجود أساسًا للزوار'),
('ar-b1-u06-p03','text','إلى صاحبة المنزل الذي تستضيفهم فيه.','إلى صاحبة المنزل التي تستضيفهم فيه.'),
('ar-b1-u06-p04','text','لم يكن سامر قد سمع الإعلان «خطأ» بالكامل؛','لم يكن فهم سامر للإعلان خاطئًا بالكامل؛'),
('ar-b1-u06-p05','text','لم تكن المشكلة اختلاف الرغبات نفسه، بل أن كل واحدة تعاملت','لم تكن المشكلة في اختلاف الرغبات نفسه، بل في أن كل واحدة تعاملت'),
('ar-b1-u06-p06','text','عن السفر مع صديق لم يُذكر بصوت واضح.','عن السفر مع صديق لم يُعبَّر عنه بوضوح.'),
('ar-b1-u06-p06','text','أن المضيف قلق فقط على موعد الاستيقاظ','أن المضيف قلق فقط بشأن موعد الاستيقاظ'),
('ar-b1-u07-p02','title','العناية ليست أن نفعل كل شيء عن الآخر','العناية ليست أن نفعل كل شيء نيابةً عن الآخر'),
('ar-b1-u07-p02','text','أن توفر عليها كل تعب:','أن توفر عليها كل عناء:'),
('ar-b1-u07-p03','text','وأن يقولوا ما الذي يعمل أيضًا','وأن يقولوا ما الذي ينجح أيضًا'),
('ar-b1-u07-p04','text','ووضع عبارة واضحة بأن بقية التفاصيل ستتحدث لاحقًا.','ووضع عبارة واضحة بأنهم سيحدّثون بقية التفاصيل لاحقًا.'),
('ar-b1-u07-p05','text','ما دام لا يكسر الاتفاقات المشتركة.','ما دام لا يخرق الاتفاقات المشتركة.'),
('ar-b1-u07-p06','text','وفي الخلاف قد نسمع حجة الطرف الآخر كعقبة يجب هزيمتها','وفي الخلاف قد نتعامل مع حجة الطرف الآخر بوصفها عقبة يجب هزيمتها'),
('ar-b1-u08-p01','text','لكنه ضغط عدة تفاصيل في جملة قصيرة','لكنه اختصر عدة تفاصيل في جملة قصيرة'),
('ar-b1-u08-p02','text','إذا كان القارئ يعتمد نسخة قديمة منه.','إذا كان القارئ يعتمد على نسخة قديمة منه.'),
('ar-b1-u08-p03','text','على فصل التأطير الطبيعي الناتج عن الاختيار من حذف','على فصل التأطير الطبيعي الناتج عن الاختيار عن حذف'),
('ar-b1-u08-p04','title','مصدر متعدد لا يعني نسخًا متعددة','كثرة المصادر لا تعني تعدد الأدلة'),
('ar-b1-u08-p04','text','صار لديها انتشار متعدد، لا أدلة مستقلة متعددة.','صار أمامها انتشار واسع، لا أدلة مستقلة متعددة.'),
('ar-b1-u08-p04','text','يمكن لخبر واحد أن يبدو واسع التأكيد على الإنترنت','يمكن لخبر واحد أن يبدو مؤكدًا على نطاق واسع على الإنترنت'),
('ar-b1-u08-p05','text','وأصبح استعارة الكتب جزءًا من بعض الواجبات.','وأصبحت استعارة الكتب جزءًا من بعض الواجبات.'),
('ar-b1-u09-p01','text','لكن ظهرت أيضًا حاجات لمقاعد إضافية وأنشطة للأطفال.','لكن ظهرت أيضًا حاجة إلى مقاعد إضافية وأنشطة للأطفال.'),
('ar-b1-u09-p01','text','ومن ما زال احتمال غيابه كبيرًا','ومن لا يزال احتمال غيابه كبيرًا'),
('ar-b1-u09-p04','text','مع أشخاص لا يحملون النموذج نفسه في ذاكرتهم','مع أشخاص لا يعرفون النموذج مسبقًا'),
('ar-b1-u09-p06','text','كانت تريد نقدًا يمكن العمل به:','كانت تريد نقدًا يمكن العمل على أساسه:'),
('ar-b1-u10-p01','text','وجدوا أن الملخص حفظ النتيجة العامة','وجدوا أن الملخص حافظ على النتيجة العامة'),
('ar-b1-u10-p03','text','وأن التفاصيل ستؤكد مساءً.','وأن التفاصيل سيجري تأكيدها مساءً.'),
('ar-b1-u10-p03','text','بدرجة الرجوع عن القرار.','بمدى صعوبة الرجوع عن القرار.'),
('ar-b1-u10-p04','text','قالت مريم إن الصياغة الأضعف ليست دائمًا معرفة أقل؛','قالت مريم إن الصياغة الأكثر حذرًا لا تعني دائمًا معرفة أقل؛'),
('ar-b1-u10-p05','text','ما إذا كان التعديل حل الحاجة التي كشفها الاعتراض فعلًا.','ما إذا كان التعديل لبّى الحاجة التي كشفها الاعتراض فعلًا.'),
('ar-b1-u10-p05','text','تبقى قابلة للمراجعة أمام استخدام جديد أو أثر غير متوقع.','تبقى قابلة للمراجعة عند ظهور استخدام جديد أو أثر غير متوقع.'),
]

def wc(s:str)->int:
    return len(re.findall(r'\S+',s.strip()))

def main():
    rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(rows)!=60: raise RuntimeError(f'expected 60 B1 passages, got {len(rows)}')
    by={r['id']:r for r in rows}
    touched=set(); applied=[]
    for pid,field,old,new in REPAIRS:
        if pid not in by: raise RuntimeError(f'missing passage {pid}')
        if field not in {'title','text'}: raise RuntimeError(field)
        value=by[pid][field]
        count=value.count(old)
        if count!=1:
            raise RuntimeError(f'exact-match guard failed {pid} {field}: expected 1 occurrence, got {count}: {old!r}')
        by[pid][field]=value.replace(old,new,1)
        touched.add(pid); applied.append({'passage_id':pid,'field':field,'old':old,'new':new})
    for pid in touched:
        r=by[pid]
        n=wc(r['text'])
        if not 220<=n<=350: raise RuntimeError(f'B1 length guard failed after naturalness repair {pid}: {n}')
        if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10:
            raise RuntimeError(f'10Q/10A guard failed {pid}')
        if {q['id'] for q in r['questions']}!={a['question_id'] for a in r['answer_key']}:
            raise RuntimeError(f'Q/A link guard failed {pid}')
        r['word_count']=n
        r['sentence_count']=len([s for s in re.split(r'(?<=[.!؟])\s+',r['text']) if s.strip()])
        r['revision']=int(r.get('revision',1))+1
        notes=r.setdefault('quality',{}).setdefault('notes',[])
        note='Final Pass 11 B1 manual naturalness review: high-confidence MSA grammar/idiom/reference repair applied after full 60-passage prose read; no stylistic-only rewrites.'
        if note not in notes: notes.append(note)
    PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
    print(json.dumps({'passages_reviewed':60,'repairs_applied':len(applied),'passages_touched':len(touched),'by_unit':dict(sorted(Counter(int(x['passage_id'].split('-u')[1].split('-')[0]) for x in applied).items()))},ensure_ascii=False))

if __name__=='__main__': main()
