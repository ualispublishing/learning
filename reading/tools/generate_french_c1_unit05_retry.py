#!/usr/bin/env python3
"""Quality preflight for C1 Unit05 scientific uncertainty and communication.

Rebuilds short passages from the original authored paragraphs using all of the
base generator's scientific-uncertainty expansions first, then adds two further
C1 paragraphs on decision relevance and kinds of uncertainty only if required.
"""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c1_unit05.py'
ns={'__name__':'c1_u05_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
BASE_EXTRA=list(ns.get('EXTRA',[]))
QUALITY_EXTRA=[
"La précision statistique et la pertinence décisionnelle doivent enfin rester distinctes. Un intervalle très étroit autour d’un effet minuscule peut soutenir une estimation précise sans rendre l’effet important pour l’action; inversement, une estimation encore large peut suffire à exclure un scénario extrême. Le résumé précise donc quelle décision la mesure est censée éclairer avant de qualifier son incertitude.",
"Une communication avancée indique aussi ce qui est inconnu pour des raisons différentes. Certaines incertitudes diminueraient avec davantage de données; d’autres viennent d’un modèle, d’une définition ou d’un transfert entre contextes. Les présenter séparément permet de choisir la prochaine collecte ou la prochaine réplication au lieu de demander indistinctement plus d’information."
]
def fit(paras,lo,hi):
    p=list(paras);text='\n\n'.join(p);i=0;extras=BASE_EXTRA+QUALITY_EXTRA
    while len(text.split())<lo and i<len(extras):
        p[-1]+=' '+extras[i];i+=1;text='\n\n'.join(p)
    if len(text.split())<lo:
        raise AssertionError(f'Unit05 below C1 minimum after full substantive uncertainty expansion: {len(text.split())} < {lo}')
    if len(text.split())>hi:
        raise AssertionError(f'Unit05 above C1 maximum after full substantive uncertainty expansion: {len(text.split())} > {hi}')
    return p,text
ns['fit']=fit
ns['main']()
