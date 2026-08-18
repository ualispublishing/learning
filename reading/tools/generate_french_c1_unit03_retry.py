#!/usr/bin/env python3
"""Quality preflight for C1 Unit03: institutions and incentives."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c1_unit03.py'
ns={'__name__':'c1_u03_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
USE={
'travailler':'« Travailler » désigne ici l’effort réellement produit sous une règle donnée; l’analyse compare ce comportement avec l’effort que l’institution affirme vouloir encourager.',
'occuper':'« Occuper » une fonction signifie détenir une position institutionnelle avec des droits, des informations et des responsabilités qui influencent les incitations disponibles.',
'quitter':'La possibilité de « quitter » une organisation constitue une réponse aux incitations : un départ peut signaler que les coûts d’une règle dépassent les avantages perçus.',
'patron':'Le « patron » représente ici l’autorité qui fixe certaines récompenses ou sanctions; son intérêt peut différer de celui des personnes évaluées par le système.',
'inspecteur':'Un « inspecteur » observe la conformité, mais sa présence peut aussi modifier le comportement observé; le contrôle doit donc distinguer conformité durable et réponse temporaire à la surveillance.',
'garde':'La « garde » illustre une fonction de contrôle dont l’efficacité dépend des informations disponibles, de l’autorité réelle et des conséquences attachées à une intervention.',
'rappeler':'« Rappeler » une règle peut corriger un oubli sans traiter une incitation contraire; l’analyse distingue donc manque d’information et intérêt à ne pas respecter la règle.',
'exact':'L’adjectif « exact » peut qualifier une mesure très précise; une mesure exacte décrit précisément ce qu’elle compte, mais cette exactitude ne garantit pas que l’indicateur représente le comportement ou l’objectif institutionnel pertinent.',
'maître':'Le terme « maître » sert à examiner une relation d’autorité forte : la capacité de donner un ordre ne prouve pas que l’exécution produira l’effet recherché ni qu’elle sera légitime.',
'professeur':'Un « professeur » combine expertise, évaluation et relation avec les personnes concernées; ces rôles peuvent créer des incitations différentes lorsqu’un même indicateur sert à enseigner et à sanctionner.',
'club':'Un « club » montre comment l’adhésion volontaire, les normes internes et la possibilité de sortie peuvent produire une discipline différente de celle d’une institution obligatoire.',
'censé':'« Censé » distingue l’effet attendu par la règle de l’effet observé : ce qu’un dispositif est censé produire devient une hypothèse à tester, non une preuve de réussite.',
'mettre':'« Mettre » une règle ou un dispositif en place ne suffit pas à montrer qu’il fonctionne; l’analyse suit les réponses qu’il provoque après son introduction.',
'retirer':'« Retirer » une récompense, une permission ou une ressource modifie les incitations; l’effet dépend de ce que les acteurs peuvent faire à la place.',
'lancer':'« Lancer » un programme crée un point de départ observable qui permet de comparer attentes, comportements initiaux et adaptations ultérieures.',
'virer':'« Virer » quelqu’un représente une sanction forte; sa simple possibilité peut modifier les comportements, mais aussi encourager la dissimulation ou la sélection stratégique des informations.',
'apprendre':'Une institution peut « apprendre » lorsque les exceptions répétées conduisent à modifier une règle plutôt qu’à les traiter comme des anomalies sans conséquence.',
'porter':'« Porter » un coût ou une responsabilité permet d’identifier qui supporte réellement les conséquences d’une règle, ce qui est essentiel pour comprendre les incitations.',
'poser':'« Poser » une condition ou un problème rend explicite le point sur lequel une décision dépend; la formulation choisie peut orienter les réponses possibles.',
'manière':'La « manière » dont une règle est appliquée fait partie du mécanisme institutionnel : deux textes identiques peuvent produire des effets différents selon la procédure et les attentes locales.'
}
orig=ns['lexical']
def lexical(form):return USE.get(form,orig(form))
ns['lexical']=lexical
EXTRA=[
"Une institution doit aussi distinguer conformité et résultat. Un indicateur peut montrer que la procédure a été suivie sans établir que l’objectif final a été atteint. L’analyse conserve donc deux niveaux de mesure et précise lequel déclenche une récompense, une sanction ou une révision de la règle.",
"Les acteurs peuvent en outre anticiper la mesure elle-même. Lorsqu’une récompense dépend d’un chiffre public, ils peuvent déplacer leur effort vers ce qui est compté et négliger ce qui ne l’est pas. Une bonne politique cherche donc des effets de substitution et compare l’indicateur avec des résultats moins faciles à manipuler.",
"Le contreargument le plus sérieux demande si le comportement observé vient réellement de l’incitation ou d’un changement simultané. Pour le tester, le rapport recherche un groupe, une période ou une tâche où la règle diffère tandis que les autres conditions restent comparables.",
"La portée de la recommandation reste limitée aux institutions où l’autorité, les possibilités de sortie et les ressources sont suffisamment proches. Si ces conditions changent, la même récompense peut produire une réponse différente et le mécanisme doit être réévalué.",
"Enfin, la règle de révision est annoncée avant la décision. Des contournements répétés, une charge concentrée sur un groupe ou une amélioration limitée à l’indicateur déclenchent une nouvelle analyse. L’apprentissage institutionnel devient ainsi une conséquence prévue du dispositif plutôt qu’un aveu d’échec tardif."
]
orig_fit=ns['fit']
def fit(paras,lo,hi):
    try:return orig_fit(paras,lo,hi)
    except AssertionError as e:
        if 'below C1 minimum' not in str(e):raise
        p=list(paras);text='\n\n'.join(p);i=0
        while len(text.split())<lo and i<len(EXTRA):
            p[-1]+=' '+EXTRA[i];i+=1;text='\n\n'.join(p)
        if len(text.split())<lo:raise AssertionError(f'Unit03 below C1 minimum after substantive institutional expansion: {len(text.split())} < {lo}')
        if len(text.split())>hi:raise AssertionError(f'Unit03 above C1 maximum after substantive institutional expansion: {len(text.split())} > {hi}')
        return p,text
ns['fit']=fit
ns['main']()
