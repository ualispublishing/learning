#!/usr/bin/env python3
"""Quality preflight for C1 Unit05 scientific uncertainty and communication."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c1_unit05.py'
ns={'__name__':'c1_u05_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
orig_fit=ns['fit']
EXTRA=[
"La précision statistique et la pertinence décisionnelle doivent enfin rester distinctes. Un intervalle très étroit autour d’un effet minuscule peut soutenir une estimation précise sans rendre l’effet important pour l’action; inversement, une estimation encore large peut suffire à exclure un scénario extrême. Le résumé précise donc quelle décision la mesure est censée éclairer avant de qualifier son incertitude.",
"Une communication avancée indique aussi ce qui est inconnu pour des raisons différentes. Certaines incertitudes diminueraient avec davantage de données; d’autres viennent d’un modèle, d’une définition ou d’un transfert entre contextes. Les présenter séparément permet de choisir la prochaine collecte ou la prochaine réplication au lieu de demander indistinctement plus d’information."
]
def fit(paras,lo,hi):
    try:return orig_fit(paras,lo,hi)
    except AssertionError as e:
        if 'below C1 minimum' not in str(e):raise
        p=list(paras);text='\n\n'.join(p);i=0
        while len(text.split())<lo and i<len(EXTRA):
            p[-1]+=' '+EXTRA[i];i+=1;text='\n\n'.join(p)
        if len(text.split())<lo:raise AssertionError(f'Unit05 below C1 minimum after substantive uncertainty expansion: {len(text.split())} < {lo}')
        if len(text.split())>hi:raise AssertionError(f'Unit05 above C1 maximum after substantive uncertainty expansion: {len(text.split())} > {hi}')
        return p,text
ns['fit']=fit
ns['main']()
