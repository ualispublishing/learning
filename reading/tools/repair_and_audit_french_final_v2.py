#!/usr/bin/env python3
"""Run the atomic French final repair/audit transaction with two quality corrections.

Keeps the base transaction's exact-prefix Unit10 regeneration, fail-closed
rollback, receipt repair, role fixes, and post-repair hash binding. It changes
only:
1) Unit05 P01 is rewritten as sustained original literary prose instead of
   relabeling analytical commentary; and
2) the corrected v2 15-pass audit is used for approval readiness.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
base = HERE / 'repair_and_audit_french_final.py'
src = base.read_text(encoding='utf-8')
old = """    byid['fr-c2-u05-p01']['genre'] = 'critical analysis'
    note = 'Final French review: genre reclassified from literary prose to critical analysis to match the learner-facing analytical commentary.'
    qnotes = byid['fr-c2-u05-p01'].setdefault('quality', {}).setdefault('notes', [])
    if note not in qnotes:
        qnotes.append(note)
"""
new = """    repair_lib = runpy.run_path(str(T / 'apply_french_final_deferred_repairs.py'), run_name='french_deferred_repair_lib')
    repair_lib['repair_u05_p01'](byid['fr-c2-u05-p01'])
    note = 'Final French review: replaced analytical commentary with sustained original literary prose while preserving the planned Unit05 genre slot and lexical curriculum.'
    qnotes = byid['fr-c2-u05-p01'].setdefault('quality', {}).setdefault('notes', [])
    if note not in qnotes:
        qnotes.append(note)
"""
if old not in src:
    raise AssertionError('Base final-repair Unit05 block changed; review before applying v2 wrapper')
src = src.replace(old, new, 1)
src = src.replace("T / 'audit_french_final_whole.py'", "T / 'audit_french_final_whole_v2.py'", 1)
src = src.replace("'Unit05 P01 analytical genre label',", "'Unit05 P01 sustained original literary-prose rewrite',", 1)
ns = {'__name__': '__main__', '__file__': str(base), '__package__': None}
exec(compile(src, str(base), 'exec'), ns)
