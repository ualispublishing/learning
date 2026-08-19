#!/usr/bin/env python3
"""Generate French C2 Unit04: economics and complex systems."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

import generate_french_c2_unit01 as c2base

base = c2base.base
R = Path(__file__).resolve().parents[2]
C1 = R / 'reading/french/c1/passages.jsonl'
C2 = R / 'reading/french/c2/passages.jsonl'
SCHEMA = R / 'reading/schema/passage.schema.json'
LOCK = R / 'reading/audit/french_c2_unit03_frontier_lock.json'
PLAN = R / 'reading/audit/french_c2_unit04_plan.json'
SEL = R / 'reading/audit/french_c2_unit04_target_selection.json'

USE = {
    'entreprise': 'Une « entreprise » est ici un acteur qui combine travail, capital, information et contrats; son intérêt propre ne se confond pas automatiquement avec la performance du système auquel elle appartient.',
    'produire': '« Produire » signifie transformer des ressources en biens, services ou capacités utiles; mesurer seulement le volume produit peut masquer la qualité, les délais, les risques transférés et les coûts imposés ailleurs.',
    'frais': 'Les « frais » désignent les dépenses supportées par un acteur pour accomplir une activité; une baisse de frais privés peut déplacer un coût vers un fournisseur, un client ou une infrastructure commune.',
    'offre': 'L’« offre » représente la quantité ou la capacité qu’un acteur est disposé à proposer sous certaines conditions; elle dépend des prix attendus, des contraintes de production et des réactions anticipées des autres acteurs.',
    'partenaire': 'Un « partenaire » coopère dans une relation d’échange ou de production sans cesser d’avoir ses propres contraintes; la coopération peut donc contenir à la fois alignement, négociation et risque de dépendance.',

    'entrée': 'Une « entrée » est une ressource, une information ou un flux qui pénètre dans un processus; dans un système complexe, modifier une entrée peut changer plusieurs sorties par des voies indirectes.',
    'sortie': 'Une « sortie » est le résultat observable d’un processus, mais elle ne résume pas nécessairement son état interne; deux organisations peuvent afficher la même sortie tout en accumulant des fragilités différentes.',
    'pression': 'Une « pression » désigne une contrainte qui modifie les décisions, par exemple un délai, un prix, une pénurie ou une attente; sa force dépend de la capacité des acteurs à l’absorber ou à la transmettre.',
    'mouvement': 'Un « mouvement » décrit ici une variation collective de prix, de stocks ou de comportements; il peut résulter d’un choc commun ou de réactions qui se renforcent mutuellement.',
    'transformer': '« Transformer » un signal économique signifie modifier non seulement son niveau mais parfois sa fonction : une information utile individuellement peut devenir trompeuse lorsque tous les acteurs y réagissent de la même manière.',

    'énergie': 'L’« énergie » sert ici d’exemple de ressource dont la disponibilité traverse plusieurs secteurs; un changement local peut donc affecter transport, production, stockage et prix par plusieurs chaînes de dépendance.',
    'nombre': 'Le « nombre » d’acteurs ou de connexions ne suffit pas à décrire un réseau; leur distribution, leur concentration et la possibilité de substitution déterminent aussi la propagation d’un choc.',
    'déplacer': '« Déplacer » une activité ou un coût signifie le transférer vers un autre lieu, moment ou acteur; ce déplacement peut améliorer un indicateur local sans réduire la charge totale du système.',
    'perte': 'Une « perte » est une diminution de valeur, de capacité ou de ressources; dans un réseau, une perte initiale peut rester locale ou être amplifiée selon les dépendances et les mécanismes de compensation.',
    'crise': 'Une « crise » désigne une rupture assez forte pour rendre les règles ordinaires d’ajustement insuffisantes; l’analyse cherche le mécanisme de propagation plutôt que d’utiliser le mot comme simple synonyme de mauvais résultat.',

    'posséder': '« Posséder » un actif donne certains droits économiques mais n’implique pas que tous les risques soient supportés par son propriétaire; contrats, garanties et règles collectives peuvent redistribuer gains et pertes.',
    'privé': '« Privé » qualifie ici un intérêt, un coût ou un bénéfice supporté par un acteur particulier; l’opposition pertinente est avec les conséquences partagées ou transférées, non avec une valeur morale automatique.',
    'prêter': '« Prêter » crée une relation dans laquelle une ressource présente est échangée contre une promesse future; l’évaluation dépend donc de la probabilité de remboursement, du temps et des protections prévues.',
    'déposer': '« Déposer » des fonds signifie les confier à une institution selon des règles de disponibilité et de sécurité; le même acte peut devenir une source de financement pour d’autres activités économiques.',
    'responsabilité': 'La « responsabilité » précise qui doit répondre d’une décision ou d’une perte; si décision, bénéfice et responsabilité sont séparés, les incitations peuvent changer même lorsque les règles formelles restent identiques.',

    'remplacer': '« Remplacer » un mécanisme par un autre peut résoudre une contrainte tout en créant de nouvelles dépendances; une politique doit donc examiner ce qui se substitue réellement au comportement qu’elle modifie.',
    'interdire': '« Interdire » supprime une option légale ou institutionnelle, mais ne garantit pas que le besoin, l’incitation ou le flux associé disparaisse; des substitutions et contournements doivent être envisagés.',
    'puissant': 'Un acteur « puissant » peut modifier les conditions auxquelles les autres s’adaptent, par sa taille, son contrôle d’une ressource ou sa capacité à supporter des pertes; la puissance est donc relationnelle plutôt qu’un simple attribut.',
    'faveur': 'Une « faveur » est un avantage accordé de manière ciblée; dans l’analyse institutionnelle, sa conséquence dépend de la règle d’attribution et de la manière dont les autres acteurs anticipent cet avantage.',
    'faillir': '« Faillir » signifie ici ne plus pouvoir remplir une obligation ou soutenir un fonctionnement attendu; la faillite d’un acteur devient systémique seulement si ses liens rendent les substituts ou les absorptions insuffisants.',
}

# Paragraphs used only when a passage needs additional depth to reach the C2
# lower word bound. They add causal and counterfactual analysis, not filler.
EXTRA = [
    "Une autre lecture distingue équilibre apparent et stabilité. Un système peut revenir rapidement à son état habituel après de petits écarts tout en étant très vulnérable à une perturbation qui franchit un seuil. L’observation d’une période calme ne suffit donc pas à conclure que les mécanismes d’ajustement fonctionneront de la même façon lorsque les contraintes changent de régime.",
    "L’analyse ajoute un contre-exemple aux raisonnements purement agrégés. Deux scénarios peuvent avoir le même coût total et pourtant répartir ce coût entre des acteurs différents, à des moments différents. Cette différence modifie les réactions futures : épargne, investissement, sortie du marché ou recherche d’un substitut. La distribution fait ainsi partie du mécanisme, pas seulement du bilan final.",
    "Une objection demande si le modèle devient inutile dès qu’il ne prédit pas exactement chaque décision individuelle. La réponse distingue niveau micro et régularité collective. Un modèle peut rester informatif s’il explique quelles contraintes rendent certains mouvements plus probables, à condition d’annoncer les situations où l’hétérogénéité des acteurs change le résultat attendu.",
    "Une alternative consiste à tester des interventions contrefactuelles plutôt qu’à extrapoler une seule tendance. On modifie une règle, une capacité de substitution ou la concentration d’un réseau, puis on compare les chemins de propagation. Ce déplacement de la question permet de séparer une corrélation historique d’un mécanisme qui devrait continuer à agir lorsque l’environnement change.",
    "La portée de la conclusion reste volontairement limitée. Un mécanisme identifié dans un scénario fictif n’autorise pas à attribuer la même dynamique à toute économie réelle. Il sert à apprendre quelles observations permettraient de distinguer amplification, absorption et simple coïncidence lorsque des données empiriques seraient disponibles.",
    "Enfin, une révision du diagnostic est prévue dès le départ. Si une intervention supposée réduire un risque ne change pas les variables intermédiaires qui portaient l’explication, il faut réexaminer le mécanisme plutôt que protéger le récit initial. Une théorie de système complexe gagne en valeur lorsqu’elle indique aussi les observations qui la rendraient moins plausible.",
]


def h(path: Path) -> str:
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def fit(paragraphs, lo: int, hi: int):
    out = list(paragraphs)
    text = '\n\n'.join(out)
    i = 0
    while len(text.split()) < lo and i < len(EXTRA):
        out[-1] += ' ' + EXTRA[i]
        i += 1
        text = '\n\n'.join(out)
    if not lo <= len(text.split()) <= hi:
        raise AssertionError(f'C2 Unit04 word band {len(text.split())} not {lo}-{hi}')
    return out, text


def bridge(forms):
    return (
        'Révision interprétative : '
        + ', '.join(f'« {x} »' for x in forms)
        + '. Ces formes du passage précédent sont reprises ici pour relier choix de modèle, mesure, '
          'incertitude et limites d’inférence aux mécanismes économiques.'
    )


def qitems(spec, forms):
    core = [
        ('main_claim', spec['qclaim'], spec['aclaim'], [forms[0]]),
        ('ambiguity_resolution', spec['qamb'], spec['aamb'], [forms[1]]),
        ('assumption', spec['qassume'], spec['aassume'], [forms[2]]),
        ('rhetorical_function', spec['qrhet'], spec['arhet'], [forms[3]]),
        ('stance', spec['qstance'], spec['astance'], [forms[4]]),
    ]
    return core + [
        ('vocabulary_in_context', f'Quel rôle analytique joue « {form} » dans ce passage ?', USE[form], [form])
        for form in forms
    ]


def make_passage(spec, forms, reviews, prior, deck, lo, hi, theme):
    paragraphs = list(spec['paras'])
    paragraphs[1] += ' ' + ' '.join(USE[f] for f in forms)
    paragraphs[2] += ' ' + bridge(reviews)
    paragraphs, text = fit(paragraphs, lo, hi)
    previous = base.prior(prior)
    new = [c2base.nt(f, text, deck) for f in forms]
    review = [base.rev(f, previous) for f in reviews]
    ids = {t['form']: t['id'] for t in new + review}
    questions, answers = base.qa(qitems(spec, forms), ids)
    return {
        'id': spec['id'],
        'language': 'fr',
        'cefr': 'C2',
        'unit': 4,
        'sequence': spec['seq'],
        'revision': 1,
        'title': spec['title'],
        'passage_type': spec['ptype'],
        'genre': spec['genre'],
        'domains': ['educational', 'professional'],
        'topics': [theme] + spec['topics'],
        'text': text,
        'word_count': len(text.split()),
        'sentence_count': max(1, len(re.findall(r'[.!?](?:[»”\"])?', text))),
        'estimated_known_token_coverage': 0,
        'new_lexical_targets': new,
        'review_lexical_targets': review,
        'grammar_targets': [{
            'id': spec['id'] + '-g1',
            'role': 'integration',
            'description': 'integrate counterfactual conditionals, causal qualification and system-level scope',
        }],
        'discourse_targets': [{
            'id': spec['id'] + '-d1',
            'role': 'integration',
            'description': 'reconstruct actor incentives, feedback, propagation, alternatives and revision conditions',
        }],
        'questions': questions,
        'answer_key': answers,
        'speed_training': {
            'timed': False,
            'benchmark_eligible': False,
            'comprehension_gate': 0.8,
            'new_word_policy': 'controlled',
            'notes': 'C2 Unit04 economics and complex-systems reasoning.',
        },
        'quality': {
            'status': 'draft',
            'schema_check': 'pending',
            'linguistic_review': 'pending',
            'pedagogical_review': 'pending',
            'answer_key_check': 'pending',
            'coverage_check': 'pending',
            'fact_check': 'not_required',
            'notes': ['Fictional economic scenarios used to teach mechanisms; no invented empirical result is presented as a real-world fact.'],
        },
        'paired_text_group': None,
        'prerequisites': ['French C2 Unit03'],
        'difficulty_notes_internal': 'C2 feedback, incentives, propagation, distribution and counterfactual policy reasoning.',
        'reader_tags': ['unit_role:' + spec['ptype'], 'generation_batch', 'french_c2_u04'],
    }


def specs():
    return [
        {
            'id': 'fr-c2-u04-p01', 'seq': 19, 'ptype': 'instructional', 'genre': 'analytical essay',
            'topics': ['firm incentives', 'cost shifting', 'supply networks'],
            'title': 'Réduire un coût local peut augmenter le coût du système',
            'paras': [
                "Une entreprise fictive fabrique un composant utilisé par plusieurs ateliers. Pour réduire ses dépenses, elle concentre ses achats chez un fournisseur moins cher et diminue fortement son stock de réserve. Les comptes de l’entreprise s’améliorent immédiatement. Pourtant, le scénario demande si cette amélioration représente un gain collectif ou seulement un déplacement du risque vers les partenaires situés plus loin dans la chaîne.",
                "La première distinction oppose coût privé et coût du système. Un choix peut réduire la dépense enregistrée par l’acheteur tout en augmentant les délais, la fragilité ou les besoins de stockage chez d’autres acteurs. L’analyse ne condamne pas la recherche d’efficacité; elle exige simplement que la frontière du calcul corresponde à la question posée.",
                "Le mécanisme apparaît lorsqu’un retard fictif touche le fournisseur unique. L’entreprise économisait sur le stockage, mais plusieurs ateliers cessent alors leur activité faute de composant. Le coût évité en amont réapparaît sous forme d’interruptions ailleurs. Le contreargument affirme qu’un fournisseur spécialisé peut aussi être plus fiable; il faut donc comparer la probabilité du choc, la capacité de substitution et la valeur du stock de sécurité plutôt que supposer qu’une concentration est toujours mauvaise.",
                "Une alternative maintient deux fournisseurs mais attribue davantage de volume au plus efficace. Elle coûte un peu plus dans les périodes ordinaires et réduit cependant le temps nécessaire pour réorienter les commandes. Le résultat intéressant n’est pas qu’une solution domine universellement, mais que le prix de la redondance dépend du coût d’une interruption et de la vitesse de remplacement.",
                "La conclusion élargit la notion d’efficacité. Une décision est efficace relativement à un objectif, un horizon et une distribution de risques. Si l’évaluation ignore les conséquences transférées à d’autres acteurs, elle peut prendre une économie locale pour une amélioration globale. La portée du raisonnement reste conditionnelle : la concentration peut être rationnelle lorsque les substituts sont rapides, et fragile lorsqu’ils ne le sont pas.",
            ],
            'qclaim': 'Pourquoi la baisse des dépenses de l’entreprise ne suffit-elle pas à établir un gain collectif ?',
            'aclaim': 'Parce qu’une dépense réduite localement peut transférer délais, stockage et risque d’interruption à d’autres acteurs du système.',
            'qamb': 'Quelle ambiguïté de la notion de coût le passage résout-il ?',
            'aamb': 'Il distingue le coût enregistré par un acteur du coût total, distribué dans le temps et entre plusieurs acteurs.',
            'qassume': 'De quoi dépend l’intérêt réel de conserver plusieurs fournisseurs ?',
            'aassume': 'Du risque d’interruption, de la vitesse de substitution et de la valeur économique de la continuité.',
            'qrhet': 'Quel rôle joue le retard fictif du fournisseur unique ?',
            'arhet': 'Il montre comment une économie locale peut réapparaître comme coût indirect lorsqu’une dépendance devient active.',
            'qstance': 'Quelle position le texte adopte-t-il sur la concentration des achats ?',
            'astance': 'Il refuse une règle absolue et demande une comparaison conditionnelle entre efficacité ordinaire, redondance et coût des ruptures.',
        },
        {
            'id': 'fr-c2-u04-p02', 'seq': 20, 'ptype': 'reinforcement', 'genre': 'scenario analysis',
            'topics': ['feedback loops', 'expectations', 'inventory dynamics'],
            'title': 'Quand chacun suit le même signal, le signal change',
            'paras': [
                "Dans un marché fictif, plusieurs distributeurs utilisent le même indicateur de demande pour régler leurs commandes. Une hausse modeste des ventes conduit chacun à commander davantage. Les producteurs interprètent ces commandes comme une nouvelle information sur la demande finale et augmentent à leur tour leur activité. Le scénario montre pourquoi un signal n’est pas toujours extérieur au comportement qu’il déclenche.",
                "On distingue d’abord flux observé et état du système. Une commande reçue par un producteur peut refléter une vente réelle, une constitution de stock ou l’anticipation d’une pénurie. Si chaque niveau interprète le flux comme une demande finale, une petite variation peut être amplifiée à mesure qu’elle traverse la chaîne.",
                "Le contreargument propose une explication plus simple : la demande finale a peut-être réellement augmenté. Pour séparer les hypothèses, le scénario compare les ventes aux consommateurs, les stocks intermédiaires et les délais de livraison. Si les commandes montent beaucoup plus vite que les ventes tandis que les stocks s’accumulent, l’hypothèse d’une boucle de réaction devient plus plausible. Révision interprétative et comparaison de mécanismes évitent de traiter chaque mouvement comme une preuve autonome.",
                "Une alternative modifie la règle de décision : les distributeurs lissent leurs commandes sur plusieurs périodes ou partagent une partie de l’information de vente. Le modèle prédit alors une amplification moindre si le mécanisme initial venait bien des réactions successives. Cette intervention contrefactuelle est plus informative qu’une simple prolongation de la tendance observée.",
                "La conclusion généralise avec prudence. Dans un système où les acteurs réagissent aux mêmes signaux, l’information et l’action forment parfois une boucle. La portée de l’indicateur dépend alors de la manière dont il est produit. Comprendre une série économique exige donc de demander non seulement ce qu’elle mesure, mais aussi quelles décisions ont contribué à la créer.",
            ],
            'qclaim': 'Pourquoi une hausse des commandes ne mesure-t-elle pas nécessairement une hausse équivalente de la demande finale ?',
            'aclaim': 'Parce que les commandes peuvent contenir des réactions de stock et des anticipations qui s’amplifient entre niveaux de la chaîne.',
            'qamb': 'Quelle ambiguïté du signal économique est centrale ?',
            'aamb': 'Un même flux peut refléter une consommation finale ou une réaction intermédiaire à des attentes et contraintes.',
            'qassume': 'Que faudrait-il observer pour rendre l’hypothèse de boucle d’amplification plus plausible ?',
            'aassume': 'Des commandes qui augmentent davantage que les ventes finales tandis que les stocks ou délais changent selon la chaîne prévue.',
            'qrhet': 'Pourquoi le scénario introduit-il une règle de commande différente ?',
            'arhet': 'Pour créer un test contrefactuel : si l’amplification diminue, le mécanisme de réaction collective reçoit un soutien supplémentaire.',
            'qstance': 'Quelle conception des indicateurs défend le passage ?',
            'astance': 'Un indicateur doit être interprété avec son processus de production, surtout lorsque les acteurs modifient ce processus en y réagissant.',
        },
        {
            'id': 'fr-c2-u04-p03', 'seq': 21, 'ptype': 'contrast', 'genre': 'commentary',
            'topics': ['network propagation', 'resource constraints', 'systemic shocks'],
            'title': 'Un petit choc devient grand seulement si les connexions l’amplifient',
            'paras': [
                "Un réseau économique fictif relie des ateliers, des transporteurs et plusieurs sources d’énergie. Un incident réduit légèrement la capacité d’un nœud. Pris isolément, le manque paraît faible. Pourtant, certains ateliers dépendent de ce nœud à la même heure, reportent leur production, puis demandent davantage de transport lorsque la capacité revient. Le commentaire cherche le mécanisme qui transforme une perturbation locale en séquence plus large.",
                "La taille du choc initial n’est donc qu’une variable. Comptent aussi le nombre de dépendances simultanées, la concentration des alternatives, les stocks disponibles et le temps nécessaire pour déplacer l’activité. Un réseau très connecté peut absorber une panne grâce à plusieurs chemins de remplacement ou, au contraire, transmettre rapidement la même contrainte à de nombreux acteurs.",
                "Une objection attribue toute la séquence à la pénurie initiale. Le texte construit alors une alternative : deux réseaux reçoivent le même choc, mais l’un possède des capacités de substitution distribuées et l’autre dépend d’un petit nombre de nœuds critiques. Si leurs pertes divergent fortement, la structure des connexions fait partie de l’explication. Le terme crise n’est utilisé qu’une fois établi que les ajustements ordinaires deviennent insuffisants.",
                "Le scénario ajoute ensuite un délai. Les acteurs ne connaissent pas immédiatement l’état complet du réseau et prennent des décisions avec une information partielle. Certains réservent plus de capacité par précaution, ce qui peut accroître temporairement la rareté pour d’autres. La réaction au risque devient alors elle-même un canal de propagation.",
                "La conclusion sépare vulnérabilité et fatalité. Une dépendance ne produit pas toujours une cascade; elle devient importante lorsque les substituts, les réserves ou la coordination sont insuffisants au moment du choc. La portée du diagnostic est donc structurelle et conditionnelle. Une bonne analyse indique où une interruption peut être absorbée, où elle peut être amplifiée et quelle observation distinguerait ces deux possibilités.",
            ],
            'qclaim': 'Qu’est-ce qui transforme une petite perturbation en problème systémique dans le scénario ?',
            'aclaim': 'La structure des dépendances, les faibles possibilités de substitution, les délais et les réactions des acteurs peuvent amplifier le choc initial.',
            'qamb': 'Pourquoi le nombre de connexions n’est-il pas à lui seul une mesure de fragilité ?',
            'aamb': 'Parce que des connexions nombreuses peuvent fournir des substituts ou au contraire transmettre une contrainte commune selon leur organisation.',
            'qassume': 'Pourquoi comparer deux réseaux soumis au même choc est-il informatif ?',
            'aassume': 'Parce que maintenir le choc constant permet d’attribuer plus clairement une divergence de pertes à la structure du réseau.',
            'qrhet': 'Quel rôle joue la réservation préventive de capacité ?',
            'arhet': 'Elle montre qu’une réaction rationnelle localement peut devenir un canal supplémentaire de propagation collective.',
            'qstance': 'Quelle position le texte adopte-t-il sur les crises de réseau ?',
            'astance': 'Il refuse de les expliquer par la seule taille du choc et exige une analyse des dépendances, substituts, délais et réactions.',
        },
        {
            'id': 'fr-c2-u04-p04', 'seq': 22, 'ptype': 'analysis', 'genre': 'analytical essay',
            'topics': ['credit', 'ownership', 'risk allocation'],
            'title': 'Le risque change lorsque décision, gain et responsabilité se séparent',
            'paras': [
                "Une institution financière fictive reçoit des dépôts et prête une partie des fonds à plusieurs projets. Chaque projet appartient à un propriétaire privé, mais certaines pertes seraient partagées avec d’autres acteurs selon les contrats. L’essai ne cherche pas à juger cette architecture en bloc; il examine comment la répartition des gains et de la responsabilité peut modifier les décisions prises avant qu’une perte ne se réalise.",
                "Le point de départ est une relation temporelle. Prêter échange une ressource disponible aujourd’hui contre un remboursement futur incertain. Le prêteur évalue donc le rendement attendu, la qualité des garanties et sa propre capacité à supporter une erreur. Le déposant, de son côté, peut surtout se préoccuper de la disponibilité et de la sécurité de ses fonds. Plusieurs objectifs coexistent dans une même structure.",
                "Le contreargument affirme que les contrats suffisent à aligner les intérêts. Le passage accepte qu’ils puissent réduire de nombreux conflits, mais introduit une alternative où une partie importante d’une perte est transférée à un tiers. Si le décideur conserve une grande part du gain tout en supportant une petite part de la perte, son seuil de risque peut changer. La responsabilité économique pertinente ne se lit donc pas seulement dans le titre de propriété.",
                "Une seconde comparaison modifie les garanties. Lorsque le prêteur doit absorber davantage de perte, il peut demander plus d’information ou limiter certains projets; lorsqu’il est très protégé, il peut accepter davantage de risque. Mais une protection peut aussi éviter une réaction en chaîne coûteuse. L’analyse doit donc comparer l’incitation créée avant le choc et la stabilité recherchée après le choc.",
                "La conclusion refuse un choix binaire entre protection et discipline. Une règle peut améliorer la stabilité tout en modifiant les comportements qu’elle devait stabiliser. Sa portée doit être évaluée sur les deux moments du mécanisme. L’objectif est d’identifier qui décide, qui bénéficie, qui supporte la perte et comment chacun anticipe cette répartition avant d’agir.",
            ],
            'qclaim': 'Pourquoi la propriété formelle d’un projet ne suffit-elle pas à prévoir la prise de risque ?',
            'aclaim': 'Parce que contrats, garanties et transferts peuvent séparer le pouvoir de décision, le bénéfice attendu et la part de perte effectivement supportée.',
            'qamb': 'Quelle ambiguïté de la responsabilité le passage met-il en évidence ?',
            'aamb': 'Être propriétaire ou signataire ne signifie pas nécessairement supporter économiquement toute la conséquence d’une décision.',
            'qassume': 'Pourquoi une garantie peut-elle changer le comportement avant toute perte ?',
            'aassume': 'Parce qu’elle modifie la part de risque anticipée par le décideur et donc les projets qu’il juge acceptables.',
            'qrhet': 'Quel rôle joue la comparaison entre forte et faible absorption des pertes par le prêteur ?',
            'arhet': 'Elle rend visible le lien entre allocation du risque, demande d’information et choix de projets.',
            'qstance': 'Quelle position le texte adopte-t-il sur les protections financières ?',
            'astance': 'Il demande d’évaluer simultanément leur effet stabilisateur après un choc et leur effet sur les incitations avant le choc.',
        },
        {
            'id': 'fr-c2-u04-p05', 'seq': 23, 'ptype': 'integration', 'genre': 'scenario analysis',
            'topics': ['policy response', 'substitution', 'market power'],
            'title': 'Une règle change les comportements qui changent ensuite l’effet de la règle',
            'paras': [
                "Une autorité fictive veut réduire une pratique économique jugée trop risquée. Trois options sont comparées : interdire directement la pratique, augmenter son coût ou favoriser une technologie de remplacement. Le scénario ne suppose pas que les acteurs restent immobiles après la décision. Il demande comment consommateurs, entreprises dominantes, nouveaux entrants et fournisseurs adaptent leurs choix aux nouvelles contraintes.",
                "La première option paraît simple : supprimer l’activité visée. Pourtant, le besoin auquel elle répond peut persister. Les acteurs peuvent se déplacer vers un substitut légal, modifier la forme du contrat ou abandonner entièrement l’activité. L’efficacité de la règle dépend donc de ce qui remplace l’option supprimée et du coût relatif de ces alternatives.",
                "Un contreargument soutient qu’une politique plus souple évite ces contournements. Une alternative montre cependant qu’une entreprise puissante peut absorber un coût supplémentaire que de petits concurrents ne peuvent pas supporter. La même mesure réduit alors la pratique tout en augmentant la concentration. Si une faveur est accordée à certains acteurs pour faciliter la transition, les anticipations d’avantages futurs peuvent à leur tour modifier l’investissement.",
                "Le scénario examine aussi l’échec. Une entreprise peut faillir parce qu’elle était inefficace, parce qu’un choc commun a détruit sa marge ou parce qu’une règle a modifié brutalement ses possibilités d’adaptation. Ces mécanismes ont des implications différentes. Sauver systématiquement tout acteur éliminerait une partie de la discipline, mais laisser disparaître un nœud difficilement remplaçable peut transmettre une perte à tout le réseau.",
                "La conclusion propose une politique révisable. Avant l’intervention, on annonce les mécanismes attendus, les substitutions plausibles et les indicateurs qui signaleraient un effet contraire. Après l’intervention, on compare ces prédictions avec les changements observés. La portée de la règle dépend ainsi de la capacité à apprendre des réactions qu’elle provoque, plutôt que de supposer que son premier effet restera identique lorsque le système s’adapte.",
            ],
            'qclaim': 'Pourquoi l’effet d’une politique ne peut-il pas être déduit uniquement de sa règle formelle ?',
            'aclaim': 'Parce que les acteurs substituent, réorganisent et anticipent, de sorte que la règle modifie aussi le système qui détermine son effet.',
            'qamb': 'Quelle ambiguïté de la notion de remplacement est importante ?',
            'aamb': 'Supprimer une pratique ne dit pas si elle disparaît réellement, se déplace vers une autre forme ou est remplacée par une solution nouvelle.',
            'qassume': 'Pourquoi une hausse de coût peut-elle accroître la concentration ?',
            'aassume': 'Parce qu’un acteur puissant peut absorber le coût plus facilement que des concurrents fragiles, ce qui change la structure du marché.',
            'qrhet': 'Quel rôle joue la distinction entre plusieurs causes possibles de faillite ?',
            'arhet': 'Elle empêche de traiter tout échec comme la preuve du même mécanisme et relie la réponse politique à la cause réelle de la fragilité.',
            'qstance': 'Quelle forme de politique le passage privilégie-t-il ?',
            'astance': 'Une intervention accompagnée de prédictions explicites, d’indicateurs de substitution et d’une possibilité de révision lorsque les réactions diffèrent des attentes.',
        },
    ]


def checkpoint(groups, deck, lo, hi, theme, prior):
    forms = [f for key in ['p01', 'p02', 'p03', 'p04', 'p05'] for f in groups[key]]
    paragraphs = [
        "Le checkpoint rassemble cinq décisions dans une économie fictive : une entreprise réduit ses réserves, des distributeurs réagissent au même signal, un réseau subit une perturbation, une institution répartit un risque financier et une autorité modifie une règle. Le lecteur doit reconstruire les mécanismes sans supposer qu’un bon résultat local implique automatiquement un bon résultat collectif.",
        "La première tâche sépare acteurs, ressources, droits et contraintes. Pour chaque scénario, on indique qui décide, quelle information est disponible, quel coût est visible localement et quelle conséquence peut être transférée. Révision cumulative : " + '; '.join(f'« {f} »' for f in forms) + ". Les mêmes mots sont maintenant utilisés pour relier production, flux, financement et politique dans une carte de dépendances.",
        "La deuxième tâche identifie les boucles. Une décision modifie un prix, un stock ou une capacité; ce changement devient ensuite une information pour d’autres acteurs, dont la réaction revient affecter le premier groupe. Le lecteur distingue une simple chaîne causale d’une rétroaction et cherche une alternative où la boucle serait interrompue.",
        "La troisième tâche porte sur la propagation. Un choc identique est appliqué à deux structures qui diffèrent par leurs substituts, leurs réserves ou la concentration de leurs liens. Si les pertes divergent, la structure devient une partie de l’explication. Une objection pertinente doit proposer un autre mécanisme capable de produire la même divergence.",
        "Enfin, le checkpoint demande une décision révisable. Une politique ou un contrat est choisi avec des prédictions sur les réactions intermédiaires, puis l’analyse précise quelle observation obligerait à revoir le diagnostic. La portée d’une conclusion dépend de cette possibilité de correction : un modèle utile décrit non seulement ce qu’il prévoit, mais aussi la manière dont il pourrait échouer.",
    ]
    paragraphs, text = fit(paragraphs, lo, hi)
    previous = base.prior(prior)
    review = [base.rev(f, previous) for f in forms]
    ids = {t['form']: t['id'] for t in review}
    items = [
        ('main_claim', 'Quelle tâche générale organise le checkpoint ?', 'Relier décisions locales, transferts, rétroactions, propagation et révision afin d’expliquer les résultats du système plutôt que de juxtaposer des indicateurs.', [forms[0]]),
        ('ambiguity_resolution', 'Pourquoi un coût local et un coût collectif doivent-ils être séparés ?', 'Parce qu’une économie enregistrée par un acteur peut déplacer une charge vers un autre acteur, un autre moment ou une autre partie du réseau.', [forms[2]]),
        ('assumption', 'Quand une réaction individuelle devient-elle une boucle de rétroaction ?', 'Quand la réaction modifie le signal ou l’état auquel d’autres acteurs répondent, et que leurs réponses reviennent modifier la situation initiale.', [forms[7]]),
        ('rhetorical_function', 'Pourquoi appliquer le même choc à deux structures différentes ?', 'Pour isoler le rôle des connexions, substituts et réserves dans l’amplification ou l’absorption de la perturbation.', [forms[13]]),
        ('synthesis', 'Comment allocation du risque et politique publique se ressemblent-elles dans ce dossier ?', 'Toutes deux changent les incitations avant que le résultat final soit observé; leur effet dépend donc aussi des adaptations qu’elles provoquent.', [forms[18]]),
        ('vocabulary_in_context', f'Quel rôle joue « {forms[3]} » dans la première décision ?', USE[forms[3]], [forms[3]]),
        ('vocabulary_in_context', f'Quel rôle joue « {forms[8]} » dans l’analyse des boucles ?', USE[forms[8]], [forms[8]]),
        ('vocabulary_in_context', f'Quel rôle joue « {forms[14]} » dans l’analyse de propagation ?', USE[forms[14]], [forms[14]]),
        ('vocabulary_in_context', f'Quel rôle joue « {forms[17]} » dans la structure financière ?', USE[forms[17]], [forms[17]]),
        ('register_style', 'Pourquoi le mot « puissant » doit-il être relié à une relation précise plutôt qu’utilisé comme étiquette générale ?', 'Parce que la puissance pertinente dépend du contrôle d’une ressource, de la capacité d’absorber une perte ou d’influencer les conditions auxquelles les autres s’adaptent.', [forms[22]]),
    ]
    questions, answers = base.qa(items, ids)
    return {
        'id': 'fr-c2-u04-p06',
        'language': 'fr',
        'cefr': 'C2',
        'unit': 4,
        'sequence': 24,
        'revision': 1,
        'title': 'Checkpoint : suivre les rétroactions plutôt que seulement les résultats',
        'passage_type': 'checkpoint',
        'genre': 'commentary',
        'domains': ['educational', 'professional'],
        'topics': [theme, 'cumulative system reasoning'],
        'text': text,
        'word_count': len(text.split()),
        'sentence_count': max(1, len(re.findall(r'[.!?](?:[»”\"])?', text))),
        'estimated_known_token_coverage': 0,
        'new_lexical_targets': [],
        'review_lexical_targets': review,
        'grammar_targets': [{
            'id': 'fr-c2-u04-p06-g1',
            'role': 'integration',
            'description': 'integrate conditional, counterfactual and system-relative claims',
        }],
        'discourse_targets': [{
            'id': 'fr-c2-u04-p06-d1',
            'role': 'integration',
            'description': 'synthesize local incentives, feedback, propagation, risk allocation and policy adaptation',
        }],
        'questions': questions,
        'answer_key': answers,
        'speed_training': {
            'timed': True,
            'benchmark_eligible': True,
            'comprehension_gate': 0.8,
            'new_word_policy': 'none',
            'notes': 'C2 Unit04 zero-new checkpoint.',
        },
        'quality': {
            'status': 'draft',
            'schema_check': 'pending',
            'linguistic_review': 'pending',
            'pedagogical_review': 'pending',
            'answer_key_check': 'pending',
            'coverage_check': 'pending',
            'fact_check': 'not_required',
            'notes': ['Generic fictional economic-systems checkpoint.'],
        },
        'paired_text_group': None,
        'prerequisites': ['French C2 Unit04 P01-P05'],
        'difficulty_notes_internal': 'C2 cumulative economics and complex-systems reasoning.',
        'reader_tags': ['unit_role:checkpoint', 'generation_batch', 'french_c2_u04'],
    }


def main() -> None:
    raw = C2.read_text(encoding='utf-8')
    rows = [json.loads(x) for x in raw.splitlines() if x.strip()]
    lock = json.loads(LOCK.read_text(encoding='utf-8'))
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    selection = json.loads(SEL.read_text(encoding='utf-8'))
    c1 = h(C1)
    c2 = h(C2)

    if (
        len(rows) != 18
        or lock.get('status') != 'PASS'
        or lock.get('last_sequence') != 18
        or lock.get('c1_canonical_blob') != c1
        or lock.get('c2_canonical_blob') != c2
    ):
        raise AssertionError('C2 Unit04 source mismatch')
    if plan.get('c2_source_blob') != c2 or selection.get('c2_source_blob') != c2:
        raise AssertionError('C2 Unit04 plan/selection stale')

    groups = selection['passage_groups']
    previous_groups = lock['unit03_target_groups']
    reviews = {k: previous_groups[k] for k in ['p01', 'p02', 'p03', 'p04', 'p05']}
    deck = c2base.deck()
    lo, hi = selection['word_band']
    prior = (
        c2base.load(c2base.A1) + c2base.load(c2base.A2) + c2base.load(c2base.B1)
        + c2base.load(c2base.B2) + c2base.load(c2base.C1) + rows
    )
    unit = [
        make_passage(spec, groups[spec['id'][-3:]], reviews[spec['id'][-3:]], prior, deck, lo, hi, plan['theme'])
        for spec in specs()
    ]
    unit.append(checkpoint(groups, deck, lo, hi, plan['theme'], prior + unit))

    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    for row in unit:
        errors = sorted(validator.iter_errors(row), key=lambda e: list(e.path))
        if errors:
            raise AssertionError(f"{row['id']}: schema {[e.message for e in errors[:10]]}")

    C2.write_text(
        raw.rstrip('\n') + '\n' + ''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in unit),
        encoding='utf-8',
    )
    print(json.dumps({
        'status': 'PASS',
        'c2_passages': 24,
        'questions': 60,
        'answers': 60,
        'new_targets': 25,
        'word_counts': {x['id']: x['word_count'] for x in unit},
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
