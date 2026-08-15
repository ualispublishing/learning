#!/usr/bin/env python3
"""Apply only high-confidence manual Pass 11 MSA/naturalness repairs to B2."""
from __future__ import annotations
import copy,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/b2/passages.jsonl'
REPAIRS={
'ar-b2-u01-p01': [('مستخدم القرار معرفة ما الذي يحتاج إلى فحص إضافي','متخذ القرار معرفة ما الذي يحتاج إلى فحص إضافي')],
'ar-b2-u01-p03': [('في السيناريو الأول خفضت قيمة التمويل المتاح','في السيناريو الأول انخفض حجم التمويل المتاح')],
'ar-b2-u01-p04': [('لغة الخطر تحتاج إلى حمل الكمية والاحتمال معًا','لغة الخطر تحتاج إلى أن تتضمن مقدار الضرر واحتماله معًا')],
'ar-b2-u01-p06': [('وفي حديث الخطر يجب الفصل بين الاحتمال والأثر','وعند الحديث عن الخطر يجب الفصل بين الاحتمال والأثر')],
'ar-b2-u02-p03': [('إذا ظهر عيب مختلف عليه','إذا ظهر عيب يختلفان عليه'),('لكنها أخذت وقتًا وانتباهًا ومخاطرة','لكنها استغرقت وقتًا وتطلبت انتباهًا وتحملًا للمخاطرة')],
'ar-b2-u02-p05': [('بدل الجدال على أن خطة واحدة «أفضل» مطلقًا','بدل الجدال حول كون خطة واحدة «أفضل» مطلقًا')],
'ar-b2-u02-p06': [('ويعمل السائقون داخل وقت وموارد محدودة','ويعمل السائقون ضمن وقت وموارد محدودة')],
'ar-b2-u03-p03': [('وكيف تحول الحالات المتكررة إلى إصلاح في النظام الأساسي','وكيف نحوّل الحالات المتكررة إلى دافع لإصلاح النظام الأساسي')],
'ar-b2-u03-p04': [('زاد ما يبرر من القيود','زادت القيود التي يمكن تبريرها')],
'ar-b2-u04-p03': [('ثم قارنت بين كلفة إنشاء رخيصة الآن','ثم قارنت بين كلفة إنشاء منخفضة الآن')],
'ar-b2-u04-p04': [('إذا كان المشروع يحتاج إلى أشخاص أن يختفوا مؤقتًا كي ينجح','إذا كان المشروع يقتضي غياب أشخاص مؤقتًا كي ينجح')],
'ar-b2-u04-p06': [('ويختبر هل يقع العبء مرارًا على المستخدم نفسه','ويختبر ما إذا كان العبء يقع مرارًا على المستخدم نفسه')],
'ar-b2-u05-p03': [('بينما احتاج خيار آخر إلى نمو أبطأ لكنه حافظ على حالته','بينما نما خيار آخر ببطء أكبر لكنه حافظ على حالته')],
'ar-b2-u05-p04': [('أن نمنع القارئ من قراءة ثقة لم يقدمها النموذج أصلًا','أن نمنع القارئ من استنتاج درجة ثقة لم يقدمها النموذج أصلًا')],
'ar-b2-u06-p02': [('أن ضغطًا قديمًا على «أوافق» يغطي تلقائيًا الاستخدام الجديد','أن نقرة سابقة على «أوافق» تغطي تلقائيًا الاستخدام الجديد')],
'ar-b2-u06-p06': [('والموافقة قد تسجل ضغطًا على زر من دون وعي كاف','والموافقة قد تسجل نقرة على زر من دون وعي كاف')],
'ar-b2-u07-p01': [('وأن الضوء ليس مظلمًا تمامًا','وأن الإضاءة ليست قاتمة تمامًا')],
'ar-b2-u07-p05': [('لماذا يمنح الراوي بعض أفعال الشخصية لغة إعجاب قوية','لماذا يصف الراوي بعض أفعال الشخصية بعبارات إعجاب قوية')],
'ar-b2-u08-p01': [('وسألوا هل الفراغ يوافق حادثًا في الحفظ أو تغيرًا في طريقة الإدارة','وسألوا هل يتوافق الفراغ مع حادثة أثرت في الحفظ أو تغير في طريقة الإدارة')],
'ar-b2-u09-p02': [('حتى لا تخفي أرقام جيدة غالبية صغيرة تنتظر طويلًا جدًا','حتى لا تخفي أرقام جيدة أقلية صغيرة تنتظر طويلًا جدًا')],
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(rows)!=60: raise RuntimeError(f'expected 60 B2 passages, got {len(rows)}')
by={r['id']:r for r in rows}
expected_repairs=sum(len(v) for v in REPAIRS.values())
if expected_repairs!=21: raise RuntimeError(expected_repairs)
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
    if note not in notes: notes.append(note)
    if r['questions']!=before_q or r['answer_key']!=before_a: raise RuntimeError(f'{pid}: assessment drift')
    if r.get('new_lexical_targets',[])!=before_new: raise RuntimeError(f'{pid}: new-target metadata drift')
    if r.get('review_lexical_targets',[])!=before_review: raise RuntimeError(f'{pid}: review-target metadata drift')
    if not 350<=r['word_count']<=550: raise RuntimeError(f'{pid}: post-repair word count {r["word_count"]}')
    for t in r.get('new_lexical_targets',[]):
        if t['form'] not in r['text']: raise RuntimeError(f'{pid}: lost new target {t["form"]}')
    touched.append(pid)
if applied!=expected_repairs: raise RuntimeError((applied,expected_repairs))
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'level':'B2','passages_reviewed':60,'repairs_applied':applied,'passages_touched':len(touched),'touched_ids':touched},ensure_ascii=False))
