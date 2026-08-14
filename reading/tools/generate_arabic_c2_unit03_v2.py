#!/usr/bin/env python3
"""Repair C2 Unit 03 collisions: prior حرارة/ملاحظة/دقة become reviews; محور/خام/متوازي become new targets."""
from __future__ import annotations
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE/'generate_arabic_c2_unit03.py'
spec=importlib.util.spec_from_file_location('c2u03_base',BASE);base=importlib.util.module_from_spec(spec)
assert spec.loader is not None;spec.loader.exec_module(base)
base.SENSE.update({'محور':'axis; pivot','خام':'raw; unprocessed','متوازي':'parallel'})

p1=next(x for x in base.R if x['id']=='ar-c2-u03-p01')
p1['target_forms']=['فيزياء','محور'];p1['reviews'].append(('ملاحظة','R4','running_text'))
p1['text']=p1['text'].replace('قاس فريق حركة جسم صغير في مسار مغلق.','قاس فريق حركة جسم صغير حول محور داخل مسار مغلق.')
p1['qa'][-1]=('single_word_definition','ما معنى «محور» هنا؟','خط أو مركز مرجعي تنتظم حوله الحركة أو الوصف.','محور')

p2=next(x for x in base.R if x['id']=='ar-c2-u03-p02')
p2['target_forms']=['خام','كيمياء'];p2['reviews'].append(('حرارة','R4','running_text'))
p2['text']=p2['text'].replace('فتدفع الحساس إلى قراءة أعلى.','فتدفع الحساس إلى قراءة أعلى رغم أن الإشارة الخام مستقرة.')
p2['qa'][-2]=('single_word_definition','ما معنى «خام» في «الإشارة الخام»؟','أولي غير معالج أو غير مصحح بعد.','خام')

p5=next(x for x in base.R if x['id']=='ar-c2-u03-p05')
p5['target_forms']=['تأكد','متوازي'];p5['reviews'].append(('دقة','R4','other'))
p5['text']=p5['text'].replace('ثانيًا يكتب فريق مستقل شفرة جديدة من وصف الطريقة.','ثانيًا يجري فريق مستقل تحليلًا متوازيًا ويكتب شفرة جديدة من وصف الطريقة.')
p5['qa'][-1]=('single_word_definition','ما معنى «متوازي» هنا؟','يجري إلى جانب تحليل آخر بصورة مستقلة للمقارنة أو التحقق.','متوازي')

p6=next(x for x in base.R if x['id']=='ar-c2-u03-p06')
replace={'ملاحظة':'محور','حرارة':'خام','دقة':'متوازي'}
p6['reviews']=[(replace.get(f,f),s,r) for f,s,r in p6['reviews']]
p6['reviews'].extend([('ملاحظة','R4','running_text'),('حرارة','R4','running_text'),('دقة','R4','running_text')])
p6['text']=p6['text'].replace('في الفيزياء قد تتفق عدة نماذج مع ملاحظة واحدة','في الفيزياء قد تتفق عدة نماذج على وصف حركة حول محور واحد رغم اختلاف آلياتها')
p6['text']=p6['text'].replace('وفي قياس الحرارة قد تكون كيمياء الحساس مصدر انحياز','وفي القياس قد تكون كيمياء الحساس والإشارة الخام مصدرين يحتاجان إلى فصل قبل تفسير الانحياز')
p6['text']=p6['text'].replace('وحتى عندما نقول «تأكدنا»','وحتى عندما يجري تحليل متوازي ونقول «تأكدنا»')

if __name__=='__main__':base.main()
