#!/usr/bin/env python3
"""Run the Unit09 recalibration with one substantive P03 enforcement-audit extension."""
from pathlib import Path

SOURCE = Path(__file__).with_name("recalibrate_final_arabic_b2_unit09.py")
text = SOURCE.read_text(encoding="utf-8")
old = "'ar-b2-u09-p03':'ووضعوا قناة طعن قصيرة حتى يستطيع الشخص تصحيح سجل خاطئ قبل تراكم العقوبات. جعل ذلك المراجعة جزءًا من الإنفاذ نفسه لا استثناءً يأتي بعد وقوع الضرر.',"
new = "'ar-b2-u09-p03':'ووضعوا قناة طعن قصيرة حتى يستطيع الشخص تصحيح سجل خاطئ قبل تراكم العقوبات. جعل ذلك المراجعة جزءًا من الإنفاذ نفسه لا استثناءً يأتي بعد وقوع الضرر. كما راقبوا زمن معالجة الطعون حتى لا تصبح المراجعة متاحة نظريًا فقط بينما تستمر العقوبة العملية مدة طويلة قبل التصحيح.',"
assert text.count(old) == 1, "expected exactly one Unit09 P03 retry insertion point"
patched = text.replace(old, new)
exec(compile(patched, str(SOURCE), "exec"), {"__name__": "__main__", "__file__": str(SOURCE)})
