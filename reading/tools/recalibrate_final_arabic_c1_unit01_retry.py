#!/usr/bin/env python3
"""Run C1 Unit01 recalibration with one substantive P02 sampling-diagnostics extension."""
from pathlib import Path
SOURCE=Path(__file__).with_name('recalibrate_final_arabic_c1_unit01.py')
text=SOURCE.read_text(encoding='utf-8')
old="في النهاية نشر الفريق أرقامًا متعددة بحسب طريقة الجمع بدل رقم واحد يخفي هذا الاعتماد، وشرح لماذا لا تكون زيادة العدد بديلًا عن فهم الطريق الذي دخلت منه البيانات.''',"
new="في النهاية نشر الفريق أرقامًا متعددة بحسب طريقة الجمع بدل رقم واحد يخفي هذا الاعتماد، وشرح لماذا لا تكون زيادة العدد بديلًا عن فهم الطريق الذي دخلت منه البيانات. وأضافوا مقارنة بين خصائص من استجابوا مبكرًا ومن استجابوا بعد تذكير ثان، لأن الفروق بين المجموعتين قد تقدم إشارة جزئية إلى نمط عدم الاستجابة. لم تعامل هذه المقارنة من لم يجيبوا كأنهم معروفون، لكنها وفرت اختبارًا إضافيًا لحساسية الوصف وبيّنت أي النتائج تستحق لغة أكثر تحفظًا.''',"
assert text.count(old)==1,'expected exactly one C1 Unit01 P02 insertion point'
patched=text.replace(old,new)
exec(compile(patched,str(SOURCE),'exec'),{'__name__':'__main__','__file__':str(SOURCE)})
