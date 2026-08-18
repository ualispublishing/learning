#!/usr/bin/env python3
"""Run Unit05 transaction with the scientific-uncertainty quality preflight."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'complete_french_c1_unit05.py'
ns={'__name__':'c1_u05_transaction','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
orig_run=ns['run']
def run(name):
    if name=='generate_french_c1_unit05.py':
        return orig_run('generate_french_c1_unit05_retry.py')
    return orig_run(name)
ns['run']=run
ns['main']()
