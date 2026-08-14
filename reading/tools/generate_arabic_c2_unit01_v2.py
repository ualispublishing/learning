#!/usr/bin/env python3
"""Repair C2 Unit 01 by replacing prior-introduced نظرية with new target بساطة.

The original Unit 01 source remains the authored base. This wrapper mutates only
the collision identified by the corpus preflight, preserving the no-duplicate
new-target invariant.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE/'generate_arabic_c2_unit01.py'
spec=importlib.util.spec_from_file_location('c2u01_base',BASE)
base=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

base.SENSE['بساطة']='simplicity; absence of unnecessary complexity'

p2=next(x for x in base.R if x['id']=='ar-c2-u01-p02')
p2['target_forms']=['بساطة','باطل']
p2['reviews'].append(('نظرية','R3','running_text'))
p2['text']=p2['text'].replace(
    'اقترحت باحثة في تجربة فكرية نظرية بسيطة:',
    'اقترحت باحثة في تجربة فكرية نظرية جذبتها بساطتها:'
)
p2['qa'][-2]=(
    'single_word_definition',
    'ما معنى «بساطة» النظرية هنا؟',
    'قلة التعقيد في صياغتها واعتمادها على عدد محدود من المبادئ أو الشروط.',
    'بساطة'
)

p6=next(x for x in base.R if x['id']=='ar-c2-u01-p06')
p6['reviews']=[
    ('بساطة',s,r) if f=='نظرية' else (f,s,r)
    for f,s,r in p6['reviews']
]
p6['reviews'].append(('نظرية','R4','running_text'))
p6['text']=p6['text'].replace(
    'ونختبر نظرية بمثال مضاد',
    'ونختبر بساطة نظرية بمثال مضاد'
)

if __name__=='__main__':
    base.main()
