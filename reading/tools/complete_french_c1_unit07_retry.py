#!/usr/bin/env python3
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'complete_french_c1_unit07.py'
ns={'__name__':'c1_u07_complete','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns);orig=ns['run']
def run(name):return orig('generate_french_c1_unit07_retry.py' if name=='generate_french_c1_unit07.py' else name)
ns['run']=run;ns['main']()
