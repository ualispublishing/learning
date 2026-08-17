#!/usr/bin/env python3
"""Final guarded retry for French B1 Unit 04.

Repairs accumulated before canonical mutation:
- keep the three fresh source-backed replacements from retry1;
- map the theatre passage to schema-approved domains;
- keep P05 and P06 safely above the unchanged 220-word B1 floor.
No lexical, freshness, linkage, review-visibility, or checkpoint guard is weakened.
"""
from pathlib import Path

p=Path(__file__).with_name('generate_french_b1_unit04_retry.py')
src=p.read_text(encoding='utf-8')
old='\nbase.main()\n'
new='''
# Schema-approved domain repair: `cultural` is not an allowed domain enum.
p2=next(s for s in base.SPECS if s["id"]=="fr-b1-u04-p02")
p2["domains"]=["educational","public"]

# Keep the 220-word B1 floor unchanged; enrich the short museum passage and checkpoint.
p5=next(s for s in base.SPECS if s["id"]=="fr-b1-u04-p05")
p5["paragraphs"][-1] += " Elle note enfin deux interprétations dans son carnet et indique pour chacune le contexte qui la rend plausible. Cette comparaison l’aide à expliquer la relation sans transformer une préférence actuelle en vérité historique."
base.CHECKPOINT["paragraphs"][-1] += " Cette méthode lui permet aussi de revenir sur une première lecture lorsque de nouvelles informations rendent une autre interprétation plus solide."

base.main()
'''
if src.count(old)!=1:
    raise AssertionError(f'expected exactly one final base.main call, found {src.count(old)}')
src=src.replace(old,new)
code=compile(src,str(p),'exec')
ns={'__name__':'__main__','__file__':str(p),'__package__':None}
exec(code,ns)
