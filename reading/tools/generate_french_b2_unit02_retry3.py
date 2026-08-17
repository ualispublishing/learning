#!/usr/bin/env python3
"""Fail-closed French B2 Unit 02 retry with corrected source-backed target pool.

The original Unit02 authoring accidentally selected six candidates that its own
source/freshness probe had rejected. This wrapper keeps the canonical source
frontier and all generator guards unchanged, swaps only those six targets for
probe-confirmed fresh entries, repairs question linkage, and adds exact visible
exposures for the replacements before invoking the original guarded main().
"""
from pathlib import Path

p = Path(__file__).with_name('generate_french_b2_unit02.py')
src = p.read_text(encoding='utf-8')
code = compile(src, str(p), 'exec')
ns = {'__name__': 'unit02_base', '__file__': str(p), '__package__': None}
exec(code, ns)

expected_old = (
    'promettre','avenir','attendre','confiance',
    'grave','calmer','solution','responsabilité',
    'partager','opinion','secret','surtout',
    'ordre','lieu','coût','préférer',
    'ramener','pareil','lumière','pousser'
)
if tuple(ns['FORMS']) != expected_old:
    raise AssertionError(f"unexpected original Unit02 pool: {ns['FORMS']}")

replace = {
    'avenir': 'décider',
    'solution': 'choisir',
    'responsabilité': 'problème',
    'partager': 'maintenir',
    'opinion': 'simplement',
    'coût': 'doute',
}
new_forms = tuple(replace.get(f, f) for f in expected_old)
if len(new_forms) != 20 or len(set(new_forms)) != 20:
    raise AssertionError('corrected Unit02 pool must contain 20 unique forms')
ns['FORMS'] = new_forms

specs = ns['SPECS']
if [s['id'] for s in specs] != [f'fr-b2-u02-p{i:02d}' for i in range(1, 6)]:
    raise AssertionError('unexpected Unit02 spec structure')

for s in specs:
    s['forms'] = [replace.get(f, f) for f in s['forms']]
    fixed = []
    for typ, prompt, answer, targets in s['items']:
        fixed.append((typ, prompt, answer, [replace.get(t, t) for t in targets]))
    s['items'] = fixed

# P01: décider replaces the rejected avenir target while preserving avenir as ordinary vocabulary.
p1 = specs[0]
p1['paragraphs'][0] += " Le comité doit donc décider à quel moment une date devient assez solide pour être annoncée comme engagement."
p1['paragraphs'][2] += " Avant de décider, il compare ce seuil avec les informations réellement disponibles."

# P02: choisir and problème replace solution/responsabilité as deliberate targets.
p2 = specs[1]
p2['paragraphs'][0] += " Le problème immédiat est donc de choisir une première réponse qui protège sans prétendre connaître déjà toute la cause."
p2['paragraphs'][2] += " Choisir cette étape locale permet de traiter le problème sans fermer les options suivantes."
fixed=[]
for typ,prompt,answer,targets in p2['items']:
    if prompt == 'Que signifie « responsabilité » dans l’analyse ?':
        prompt = 'Que signifie « problème » dans l’analyse ?'
        answer = 'La situation concrète à traiter malgré une connaissance encore incomplète de sa cause et de son étendue.'
        targets = ['problème']
    fixed.append((typ,prompt,answer,targets))
p2['items']=fixed

# P03: maintenir and simplement replace partager/opinion as deliberate targets.
p3 = specs[2]
p3['paragraphs'][0] += " Le but est de maintenir une distinction nette entre données provisoires, interprétation et confidentialité."
p3['paragraphs'][1] += " Maintenir cette limite ne consiste pas simplement à cacher des informations : il faut pouvoir en expliquer la raison."
p3['paragraphs'][2] += " Une expertise ne permet pas simplement de transformer une lecture plausible en résultat démontré."
fixed=[]
for typ,prompt,answer,targets in p3['items']:
    if prompt == 'Quelles informations l’équipe décide-t-elle de partager avec le journaliste ?':
        prompt = 'Quelle distinction l’équipe cherche-t-elle à maintenir dans sa réponse au journaliste ?'
        answer = 'Elle veut maintenir la différence entre données provisoires, interprétations des chercheurs et informations protégées.'
        targets = ['maintenir','secret']
    elif prompt == 'Que signifie « opinion » dans le texte ?':
        prompt = 'Que signifie « simplement » dans « ne permet pas simplement » ?'
        answer = 'L’adverbe indique qu’une étape ou une autorité, à elle seule, ne suffit pas à produire la conclusion annoncée.'
        targets = ['simplement']
    elif prompt == 'Pourquoi l’expertise ne suffit-elle pas à transformer une opinion en résultat ?':
        prompt = 'Pourquoi l’expertise ne permet-elle pas simplement de transformer une interprétation en résultat ?'
        answer = 'Parce qu’elle peut orienter l’interprétation, mais la conclusion doit encore être soutenue par les données et leur méthode.'
        targets = ['simplement','apporter']
    fixed.append((typ,prompt,answer,targets))
p3['items']=fixed

# P04: doute replaces the rejected coût target; coût remains normal B2 vocabulary.
p4 = specs[3]
p4['paragraphs'][0] += " Un doute demeure toutefois sur la participation finale, et ce doute doit rester visible dans le classement."
p4['paragraphs'][2] += " Le doute ne disparaît pas quand le comité classe les scénarios ; il devient une information à gérer."
fixed=[]
for typ,prompt,answer,targets in p4['items']:
    if prompt == 'Quels coûts le comité distingue-t-il ?':
        prompt = 'Quel doute principal le comité conserve-t-il malgré son tableau de comparaison ?'
        answer = 'Il conserve un doute sur le nombre final de participants et sur le scénario qui se réalisera.'
        targets = ['doute']
    fixed.append((typ,prompt,answer,targets))
p4['items']=fixed

# Checkpoint: remap Unit02 target tags, remove three stale Unit01-only tags, and
# make every corrected target exactly visible in the zero-new synthesis text.
cp = ns['CHECKPOINT']
cp['paragraphs'][-1] += (
    " Pour décider sans masquer le problème, le groupe peut choisir de maintenir une distinction explicite, "
    "simplement reconnaître le doute et réviser son action lorsque de nouvelles informations arrivent."
)
fixed=[]
allowed=set(new_forms)
for typ,prompt,answer,targets in cp['items']:
    mapped=[replace.get(t,t) for t in targets]
    mapped=[t for t in mapped if t in allowed]
    fixed.append((typ,prompt,answer,mapped))
cp['items']=fixed

ns['main']()
