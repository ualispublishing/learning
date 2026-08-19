#!/usr/bin/env python3
"""Pedagogical-pair and depth preflight for French C2 Unit10."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'generate_french_c2_unit10.py'
ns={'__name__':'c2_u10_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
PAIR='fr-c2-u10-shared-case-viewpoints'
_original_specs=ns['specs']
def specs():
    rows=_original_specs()
    by={x['id']:x for x in rows}
    # The source generator grouped P02 and P03 despite their being different
    # scenarios. Make the explicit pair pedagogically genuine: P03 and P04
    # analyze the same fictional library sensing proposal from distinct lenses.
    by['fr-c2-u10-p02'].pop('pair',None)
    p3=by['fr-c2-u10-p03']; p3['pair']=PAIR
    p3['title']='Perspective A : une autorisation limitée peut rendre l’essai gouvernable'
    p4=by['fr-c2-u10-p04']; p4['pair']=PAIR; p4['genre']='complex paired texts'
    p4['title']='Perspective B : la gouvernance ne suffit pas si l’infrastructure devient fragile'
    p4['topics']=['paired argument','infrastructure dependence','reliability and exit']
    p4['paras']=[
      "La perspective B examine le même projet fictif que la perspective A : une bibliothèque souhaite analyser certains déplacements afin de réorganiser ses espaces. B accepte les protections de gouvernance proposées par A, mais soutient qu’elles ne règlent qu’une partie du problème. Avant même de choisir la durée de conservation ou les droits d’accès, il faut demander de quels appareils, connexions et compétences le service dépendra une fois intégré au fonctionnement ordinaire.",
      "B reconstruit la chaîne matérielle : capteurs, alimentation, traitement local, réseau, maintenance et procédure de secours. Une autorisation juridiquement ou administrativement limitée ne garantit pas qu’un service soit facile à retirer si les anciennes procédures disparaissent entre-temps.",
      "Le meilleur contreargument d’A affirme qu’un pilote court évite justement cette dépendance. B répond par une condition plus précise : le pilote doit conserver une voie de fonctionnement sans le nouveau dispositif, documenter le coût de retour et empêcher que les décisions essentielles soient transférées trop tôt vers une infrastructure encore expérimentale. La révision des dossiers précédents sert à distinguer possibilité technique, mécanisme réel et portée d’une conclusion.",
      "B compare ensuite deux pannes imaginaires. Dans la première, un capteur cesse de répondre et le personnel revient immédiatement au plan des espaces existant. Dans la seconde, plusieurs fonctions ont été regroupées autour du système et l’interruption bloque aussi l’accès à des informations nécessaires au service. Le même incident matériel produit alors des dégâts très différents parce que l’organisation a créé des dépendances différentes.",
      "La perspective B ne recommande donc pas de renoncer au projet. Elle conseille une expérimentation en couches : commencer par les fonctions dont l’arrêt est simple, mesurer les bénéfices, puis développer seulement les composantes dont la valeur supplémentaire justifie une dépendance nouvelle. Son désaccord avec A est gradué : A met l’accent sur permission, finalité et recours; B demande que la réversibilité organisationnelle et matérielle soit testée avec la même rigueur.",
    ]
    p4.update({
      'qclaim':'Quelle thèse la perspective B ajoute-t-elle au raisonnement de A ?',
      'aclaim':'Une gouvernance limitée ne suffit pas si le pilote crée des dépendances matérielles ou organisationnelles difficiles à retirer.',
      'qamb':'Quelle différence B établit-elle entre arrêter un appareil et revenir à l’ancien service ?',
      'aamb':'Éteindre un composant est une action technique; restaurer le service exige aussi que les anciennes procédures, données et compétences existent encore.',
      'qassume':'Pourquoi B conserve-t-elle une voie de fonctionnement sans le nouveau système ?',
      'aassume':'Pour tester la valeur du pilote sans rendre l’organisation dépendante avant que les bénéfices et modes de panne soient suffisamment connus.',
      'qrhet':'Quel rôle jouent les deux pannes imaginaires ?',
      'arhet':'Elles montrent qu’un même incident peut produire des conséquences très différentes selon les dépendances créées autour du dispositif.',
      'qstance':'Quel compromis B recommande-t-elle ?',
      'astance':'Une expérimentation en couches qui augmente la dépendance seulement lorsque la valeur supplémentaire est établie et que le retour reste praticable.'
    })
    return rows
ns['specs']=specs
# Depth material is appended only when the strict 700-word floor is not yet met.
ns['EXTRA']=list(ns['EXTRA'])+[
 "Le checkpoint ajoute un audit de contradiction. Pour deux phrases apparemment opposées, le lecteur réécrit la population, la période, la variable et le degré de modalité. Si les propositions reformulées peuvent être vraies ensemble, le désaccord était en partie produit par le cadrage; sinon, il faut identifier l’observation qui peut les départager.",
 "Une seconde tâche porte sur la dépendance des preuves. Le lecteur dessine mentalement un graphe reliant chaque conclusion à ses sources premières. Une répétition issue d’un même rapport n’augmente pas artificiellement le nombre de confirmations, tandis qu’une observation indépendante peut renforcer une conclusion même si son vocabulaire est différent.",
 "La réponse finale distingue aussi recommandation et prédiction. On peut recommander une option parce qu’elle est réversible ou protège mieux contre une erreur grave sans prédire qu’elle donnera nécessairement le meilleur résultat moyen. Cette séparation oblige à annoncer les valeurs qui complètent les faits dans la décision.",
 "Enfin, le lecteur fournit une condition de transfert. Il précise quelle propriété du contexte doit rester stable pour appliquer la conclusion ailleurs, puis décrit un cas plausible où cette propriété change. Une règle capable de nommer sa propre limite est plus informative qu’une généralisation qui survit seulement parce qu’elle n’est jamais testée."
]
ns['main']()
