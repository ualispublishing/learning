#!/usr/bin/env python3
"""Exact-form retry for French B1 Unit 05.

The revised 15-target pool already passed freshness. This wrapper makes the
required P04 and checkpoint lemmas exactly visible before the unchanged
validator runs. No lexical, freshness, word-band, linkage, or checkpoint guard
is weakened.
"""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b1_unit05_retry.py')
src=p.read_text(encoding='utf-8')
old='\nbase.main()\n'
new='''
# Exact-form new-target exposure: existing `mérite` is inflected, so include the
# deliberate lemma naturally without relaxing the exact-exposure rule.
p4=next(s for s in base.SPECS if s["id"]=="fr-b1-u05-p04")
p4["paragraphs"][-1] += " Une amélioration peut mériter du temps même lorsqu’elle n’est pas urgente, si elle rend la participation plus claire et plus fiable."
# Exact-form review exposure: `normalement` is not the deliberate lemma `normal`.
p4["paragraphs"][0] += " Camille vérifie que le fonctionnement normal du système est revenu avant de poursuivre."

# P06 summary reviews are exact-form too: use `clair` and `mériter`, not only
# feminine/conjugated forms.
base.CHECKPOINT["paragraphs"][0]=base.CHECKPOINT["paragraphs"][0].replace("une structure claire", "un message clair")
base.CHECKPOINT["paragraphs"][1]=base.CHECKPOINT["paragraphs"][1].replace("décider ce qui mérite du temps", "décider ce qui peut mériter du temps")
base.CHECKPOINT["paragraphs"][2]=base.CHECKPOINT["paragraphs"][2].replace("une information claire", "un message clair")

base.main()
'''
if src.count(old)!=1:
    raise AssertionError(f'expected exactly one final base.main call, found {src.count(old)}')
src=src.replace(old,new)
code=compile(src,str(p),'exec')
ns={'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code,ns)
