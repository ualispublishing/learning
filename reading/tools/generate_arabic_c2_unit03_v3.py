#!/usr/bin/env python3
"""Repair C2 Unit 03 v2 by replacing unsupported متوازي with cleared تكرر.

Prior حرارة/ملاحظة/دقة remain review targets. Corpus-wide duplicate-new-target
preflight remains enforced by the underlying base generator.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
V2=HERE/'generate_arabic_c2_unit03_v2.py'
spec=importlib.util.spec_from_file_location('c2u03_v2',V2)
v2=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(v2)
base=v2.base

base.SENSE['تكرر']='repeat; recur'

p5=next(x for x in base.R if x['id']=='ar-c2-u03-p05')
p5['target_forms']=['تأكد','تكرر']
p5['text']=p5['text'].replace(
    'ثانيًا يجري فريق مستقل تحليلًا متوازيًا ويكتب شفرة جديدة من وصف الطريقة.',
    'ثانيًا يكتب فريق مستقل شفرة جديدة من وصف الطريقة ليرى هل تتكرر النتيجة من تنفيذ منفصل.'
)
p5['qa'][-1]=(
    'single_word_definition',
    'ما معنى «تكرر» هنا؟',
    'حدث أو ظهر مرة أخرى عند إعادة التحليل أو الاختبار.',
    'تكرر'
)

p6=next(x for x in base.R if x['id']=='ar-c2-u03-p06')
p6['reviews']=[('تكرر',s,r) if f=='متوازي' else (f,s,r) for f,s,r in p6['reviews']]
p6['text']=p6['text'].replace(
    'وحتى عندما يجري تحليل متوازي ونقول «تأكدنا»',
    'وحتى عندما تتكرر النتيجة في تنفيذ آخر ونقول «تأكدنا»'
)

if __name__=='__main__':
    base.main()
