#!/usr/bin/env python3
"""Quality preflight for C1 Unit10 synthesis: deepen cross-domain decision logic."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;p=HERE/'generate_french_c1_unit10.py'
ns={'__name__':'c1_u10_base','__file__':str(p),'__package__':None};exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
ns['EXTRA']=list(ns['EXTRA'])+[
"La synthèse distingue enfin force de preuve et réversibilité de la décision. Une intervention facilement corrigible peut être raisonnable avec une preuve encore incomplète si elle produit de l’information utile; une décision durable ou difficile à réparer exige au contraire une justification plus robuste. Le seuil d’action dépend donc à la fois de ce que l’on sait et du coût d’une erreur.",
"Le transfert entre domaines est soumis à un dernier test : l’analogie doit préserver la relation qui faisait le travail explicatif dans le cas d’origine. Partager un vocabulaire de risque, de justice ou de preuve ne suffit pas si les mécanismes, les acteurs ou les possibilités de révision sont différents. La synthèse annonce explicitement ce qui est transféré et ce qui ne l’est pas."
]
ns['main']()
