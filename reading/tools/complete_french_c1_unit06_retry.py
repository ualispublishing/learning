#!/usr/bin/env python3
"""Run Unit06 transaction while routing its writer through the quality preflight."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'complete_french_c1_unit06.py'
ns={'__name__':'c1_u06_complete','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
orig=ns['run']
def run(name):
    if name=='generate_french_c1_unit06.py':name='generate_french_c1_unit06_retry.py'
    return orig(name)
ns['run']=run
ns['main']()
