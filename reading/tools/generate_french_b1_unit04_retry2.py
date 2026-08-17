#!/usr/bin/env python3
"""Final length-safe retry for B1 Unit 04 after freshness replacements passed."""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b1_unit04_retry.py')
src=p.read_text(encoding='utf-8')
old='\nbase.main()\n'
new='''\n# Keep the 220-word B1 floor unchanged; enrich the short museum passage and checkpoint.\np5=next(s for s in base.SPECS if s["id"]=="fr-b1-u04-p05")\np5["paragraphs"][-1] += " Elle note enfin deux interprétations dans son carnet et indique pour chacune le contexte qui la rend plausible. Cette comparaison l’aide à expliquer la relation sans transformer une préférence actuelle en vérité historique."\nbase.CHECKPOINT["paragraphs"][-1] += " Cette méthode lui permet aussi de revenir sur une première lecture lorsque de nouvelles informations rendent une autre interprétation plus solide."\n\nbase.main()\n'''
if src.count(old)!=1:
    raise AssertionError(f'expected exactly one final base.main call, found {src.count(old)}')
src=src.replace(old,new)
code=compile(src,str(p),'exec')
ns={'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code,ns)
