#!/usr/bin/env python3
"""Run C2 Unit03 recalibration after removing a reader-facing Latin-script draft intrusion."""
from pathlib import Path
SOURCE=Path(__file__).with_name('recalibrate_final_arabic_c2_unit03.py')
text=SOURCE.read_text(encoding='utf-8')
old='بعد perturbation'
new='بعد إزالة الاضطراب'
assert text.count(old)==1
text=text.replace(old,new,1)
exec(compile(text,str(SOURCE),'exec'),{'__name__':'__main__','__file__':str(SOURCE)})
