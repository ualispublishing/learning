#!/usr/bin/env python3
"""Quality preflight for French C1 Unit02 professional-judgment production."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c1_unit02.py'
ns={'__name__':'c1_u02_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
USE={
'sûr':'Être sûr décrit ici un degré de confiance professionnel : l’auteur doit montrer quelles preuves justifient cette assurance et ce qui pourrait la réduire.',
'falloir':'Le verbe « falloir » sert à distinguer une nécessité démontrée d’une simple préférence; une recommandation doit expliciter pourquoi une contrainte rend une action nécessaire.',
'vraiment':'Le mot « vraiment » signale une affirmation renforcée dont le niveau d’assurance doit être proportionné aux éléments disponibles, et non à l’intensité rhétorique.',
'seul':'Le terme « seul » permet de tester la suffisance : une seule source, une seule mesure ou un seul cas ne doit pas recevoir la portée d’un ensemble de preuves indépendantes.',
'regarder':'Regarder signifie ici examiner directement un indicateur, un dossier ou un comportement avant de l’intégrer au jugement professionnel.',
'entendre':'Entendre un témoignage fournit une information située; le décideur doit distinguer ce que la personne rapporte directement de ce qu’elle interprète.',
'parler':'Parler d’un problème transforme une expérience en énoncé; l’analyse doit conserver qui parle, à quel titre et avec quel accès aux faits.',
'passer':'Ce qui se passe avant, pendant et après une décision permet de reconstruire la séquence causale et d’éviter d’attribuer au choix un effet qui l’a précédé.',
'homme':'La catégorie « homme » peut révéler un effet de groupe, mais elle ne doit être utilisée que si le sexe ou le genre est réellement pertinent pour le mécanisme examiné.',
'femme':'La catégorie « femme » rappelle qu’une moyenne globale peut masquer des effets distribués différemment; le jugement doit vérifier si la recommandation reste défendable pour ce groupe.',
'gens':'Le mot « gens » est trop général pour porter seul une conclusion; l’auteur doit préciser quelles personnes sont incluses, absentes ou particulièrement exposées.',
'peut-être':'« Peut-être » marque une hypothèse encore ouverte; le texte doit préciser quelle observation la rendrait plus ou moins probable au lieu de laisser l’incertitude indéterminée.',
'arriver':'Ce qui peut arriver après une décision appartient à l’analyse des conséquences; il faut distinguer possibilité, probabilité et gravité.',
'partir':'Partir d’un poste, d’un service ou d’une situation peut modifier les ressources et responsabilités disponibles; le scénario doit donc intégrer cette transition plutôt que supposer une structure fixe.',
'laisser':'Laisser une marge de discrétion est un choix de gouvernance : le briefing doit préciser qui peut l’exercer, sous quelles conditions et avec quelle traçabilité.',
'arrêter':'Arrêter une procédure, un traitement ou un projet exige un seuil préalable; une bonne règle d’arrêt évite de déplacer le critère après avoir vu le résultat.',
'petit':'Un petit effet peut être statistiquement stable mais pratiquement négligeable; le jugement doit donc séparer magnitude et certitude.',
'grand':'Un grand effet apparent peut provenir d’un petit échantillon ou d’un cas atypique; sa taille ne remplace pas l’évaluation de la méthode.',
'mourir':'Le risque de mourir représente un dommage irréversible : même peu probable, il peut légitimement modifier le seuil de preuve ou de précaution.',
'appeler':'Appeler une situation « urgente », « sûre » ou « exceptionnelle » est déjà un acte de classification; le professionnel doit justifier la catégorie avant d’en déduire une action.'
}
orig=ns['lexical']
def lexical(form):return USE.get(form,orig(form))
ns['lexical']=lexical
ns['main']()
