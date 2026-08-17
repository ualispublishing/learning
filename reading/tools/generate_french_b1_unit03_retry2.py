#!/usr/bin/env python3
"""Final pre-canonical retry for B1 Unit 03: lift P06 above the B1 floor."""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b1_unit03_retry.py')
src=p.read_text(encoding='utf-8')
old='\nbase.main()\n'
new='''\n# P06 was 217 words after the source-target repair; keep the 220-word floor intact.\nbase.CHECKPOINT["paragraphs"][-1] += " Cette méthode lui permet surtout de distinguer une observation, une hypothèse et une conclusion avant de choisir la prochaine action."\n\nbase.main()\n'''
if src.count(old)!=1:
    raise AssertionError(f'expected exactly one final base.main call, found {src.count(old)}')
src=src.replace(old,new)
code=compile(src,str(p),'exec')
ns={'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code,ns)
