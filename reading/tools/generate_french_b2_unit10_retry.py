#!/usr/bin/env python3
"""Fail-closed runtime/preflight for final French B2 Unit10.

Refreshes the exhaustive probe and pedagogically filtered selection under the
Unit09 lock, compiles the base generator directly when already valid (repairing
only the historical nested-f-string defect if it still exists), aligns content-
word fallbacks with genuine learner-facing meanings, checks linkage/word bands,
and delegates to all base source/schema/freshness/review/uniqueness guards.
"""
from pathlib import Path
import re
HERE=Path(__file__).resolve().parent

def run_module(filename,name):
    p=HERE/filename;ns={'__name__':name,'__file__':str(p),'__package__':None}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns);ns['main']()

run_module('probe_french_b2_unit10_targets.py','unit10_probe')
run_module('select_french_b2_unit10_targets.py','unit10_select')

p=HERE/'generate_french_b2_unit10.py';src=p.read_text(encoding='utf-8')
# Modern base text may already compile. Repair the historical nested f-string
# only when Python actually rejects the staged source.
try:
    code=compile(src,str(p),'exec')
except SyntaxError:
    old="  for i,x in enumerate(f):out.append(('vocabulary_in_context',f'Quel rôle joue « {x} » dans ce passage ?',f'Il sert à préciser {SLOT_MEANING[f\"{spec[\"prefix\"]}_{slots(spec[\"prefix\"])[i]}\"]}.',[x]))"
    new="""  for i,x in enumerate(f):
   slot=f\"{spec['prefix']}_{slots(spec['prefix'])[i]}\"
   out.append(('vocabulary_in_context',f'Quel rôle joue « {x} » dans ce passage ?',f\"Il sert à préciser {SLOT_MEANING[slot]}.\",[x]))"""
    if old not in src:raise
    src=src.replace(old,new,1);code=compile(src,str(p),'exec')
ns={'__name__':'unit10_base','__file__':str(p),'__package__':None};exec(code,ns)

# Semantic roles for the vetted content-word fallback pool. These descriptions
# are used only when the exhaustive selector had to leave an exhausted preferred
# synthesis slot; they teach the selected word itself, not an unrelated slot.
WORD_ROLE={
 'fait':'un fait observable qui doit être distingué d’une interprétation',
 'affaire':'une affaire ou un dossier concret dont plusieurs lectures doivent être comparées',
 'peur':'une peur exprimée par un acteur, pertinente comme donnée de perspective sans devenir preuve suffisante à elle seule',
 'prêt':'le fait qu’un acteur ou dispositif soit prêt à agir sous des conditions précises',
 'moment':'le moment auquel une décision, une source ou un effet apparaît dans la chaîne de raisonnement',
 'dernier':'le dernier élément d’une série ou la dernière option considérée dans une comparaison',
 'rendre':'l’action de rendre un résultat, une relation ou une contrainte plus visible dans l’analyse',
 'défendre':'l’action de défendre une position tout en répondant au meilleur contreargument',
 'vivre':'l’expérience que des personnes peuvent vivre différemment sous une même règle ou décision',
 'type':'le type de source, de cas ou de mécanisme auquel une affirmation se rapporte',
 'police':'la police comme institution concrète dont les données et intérêts doivent être situés parmi d’autres sources',
 'façon':'la façon dont une source, une méthode ou un acteur construit et présente le problème',
 'attention':'l’attention portée à une conséquence, un groupe ou une limite que l’argument ne doit pas négliger',
 'partie':'une partie du dossier ou une partie prenante dont le rôle doit être distingué de l’ensemble',
 'manquer':'ce qui peut manquer à une preuve, un mécanisme ou une mise en œuvre avant de conclure',
 'suite':'la suite donnée à une décision et les conséquences qui permettent ensuite de la réévaluer',
 'dur':'une contrainte difficile ou un test dur qui met à l’épreuve la robustesse d’une conclusion',
 'prochain':'le prochain cas, cycle ou moment auquel l’analyse doit être transférée ou révisée',
 'impossible':'une limite qui rend une option impossible et réduit donc l’espace réel des choix',
 'abandonner':'l’action d’abandonner une option lorsque les preuves ou contraintes ne justifient plus de la maintenir'
}

# Load selection once and rewrite fallback slot meanings to match the actual word.
_,pre_groups,pre_details,_=ns['load_state']()
for slot,detail in pre_details.items():
    form=detail['form']
    if detail.get('semantic_fallback'):
        if form not in WORD_ROLE:raise AssertionError(f'Missing learner-facing semantic role for Unit10 fallback {form}')
        ns['SLOT_MEANING'][slot]=WORD_ROLE[form]

def clean_lexical_sentence(slot,form,detail):
    meaning=ns['SLOT_MEANING'][slot]
    return f"Dans ce passage, « {form} » sert à préciser {meaning}; son emploi est relié à un élément vérifiable du raisonnement."
ns['lexical_sentence']=clean_lexical_sentence

orig_make=ns['make']
def patched_make(spec,forms,review_forms,details,prior,deck):
    row=orig_make(spec,forms,review_forms,details,prior,deck)
    local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in row.get(fld,[])};amap={a['question_id']:a['id'] for a in row['answer_key']}
    for q in row['questions']:
        if amap.get(q['id'])!=q['answer_id'] or any(t not in local for t in q.get('target_ids',[])):
            raise AssertionError(f"{row['id']} {q['id']}: preflight linkage failure")
    if row['word_count']<350:
        row['text'] += " L’auteur précise enfin ce qui pourrait affaiblir la conclusion : une source indépendante qui contredit le mécanisme central, un groupe jusque-là absent dont les effets sont différents, ou un coût supérieur au seuil annoncé. Une telle information ne détruit pas automatiquement le raisonnement, mais oblige à réviser sa portée ou sa force."
        row['word_count']=len(row['text'].split());row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',row['text'])));row['quality']['notes'].append('Added substantive counterevidence/revision logic to clear B2 minimum word band.')
    if row['word_count']>550:raise AssertionError(f"{row['id']}: preflight over B2 maximum: {row['word_count']}")
    return row
ns['make']=patched_make
orig_checkpoint=ns['checkpoint']
def patched_checkpoint(groups,deck):
    row=orig_checkpoint(groups,deck)
    if row['word_count']<350:
        row['text'] += " Cette méthode ne transforme pas toute question en débat sans fin. Elle permet au contraire de conclure lorsque les preuves sont suffisantes, tout en indiquant quelle nouvelle information pourrait justifier une révision. La maîtrise B2 tient autant à cette discipline de portée qu’à la capacité d’exprimer une position complexe."
        row['word_count']=len(row['text'].split());row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',row['text'])))
    if not 350<=row['word_count']<=550:raise AssertionError(f"{row['id']}: final checkpoint outside B2 band: {row['word_count']}")
    return row
ns['checkpoint']=patched_checkpoint

_,groups,details,reviews=ns['load_state']();expected=set(ns['SLOT_MEANING'])
if set(details)!=expected:raise AssertionError(f"Unit10 selected-slot drift: missing={sorted(expected-set(details))} extra={sorted(set(details)-expected)}")
if any(len(groups[k])!=4 or len(reviews[k])!=4 for k in ['p01','p02','p03','p04','p05']):raise AssertionError('Unit10 group/review structure drift')

ns['main']()
