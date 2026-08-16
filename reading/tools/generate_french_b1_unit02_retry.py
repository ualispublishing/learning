#!/usr/bin/env python3
"""Retry B1 Unit 02 after repairing a single source-level bracket typo in memory.

The canonical generator remains inspectable as originally committed; this wrapper
changes only the malformed comprehension bracket before compiling/executing it.
"""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b1_unit02.py')
src=p.read_text(encoding='utf-8')
bad="ids={t['form']:t['id'] for t in reviews]"
good="ids={t['form']:t['id'] for t in reviews}"
if src.count(bad)!=1:
    raise AssertionError(f'expected exactly one known bracket typo, found {src.count(bad)}')
src=src.replace(bad,good)
code=compile(src,str(p),'exec')
ns={'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code,ns)
