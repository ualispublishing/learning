#!/usr/bin/env python3
"""Apply Unit09 retry patches while preserving triple-quoted passage boundaries."""
from pathlib import Path
SOURCE=Path(__file__).with_name('recalibrate_final_arabic_c1_unit09.py')
RETRY=Path(__file__).with_name('recalibrate_final_arabic_c1_unit09_retry.py')
ns={'__file__':str(RETRY)}
prefix=RETRY.read_text(encoding='utf-8').split('for old,new in patches.items():',1)[0]
exec(prefix,ns)
text=SOURCE.read_text(encoding='utf-8')
for old,new in ns['patches'].items():
    assert text.count(old)==1, f'expected one retry insertion point: {old[:50]!r}'
    if old.endswith("''',"):
        new += "''',"
    text=text.replace(old,new)
exec(compile(text,str(SOURCE),'exec'),{'__name__':'__main__','__file__':str(SOURCE)})
