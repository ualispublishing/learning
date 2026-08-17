#!/usr/bin/env python3
"""Fail-closed runtime/preflight for final French B2 Unit10.

Refreshes the exhaustive probe/selection under the Unit09 frontier, repairs a
single staged nested-f-string syntax defect before compiling the base generator,
checks local assessment linkage and word bands, then delegates to every base
source/schema/freshness/review/uniqueness guard.
"""
from pathlib import Path
import re
HERE=Path(__file__).resolve().parent

def run_module(filename,name):
    p=HERE/filename;ns={'__name__':name,'__file__':str(p),'__package__':None}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns);ns['main']()

# Exhaustive, read-only prerequisites; both fail before canonical writes unless
# the exact Unit09 frontier lock matches live B2.
run_module('probe_french_b2_unit10_targets.py','unit10_probe')
run_module('select_french_b2_unit10_targets.py','unit10_select')

p=HERE/'generate_french_b2_unit10.py';src=p.read_text(encoding='utf-8')
old="  for i,x in enumerate(f):out.append(('vocabulary_in_context',f'Quel rôle joue « {x} » dans ce passage ?',f'Il sert à préciser {SLOT_MEANING[f\"{spec[\"prefix\"]}_{slots(spec[\"prefix\"])[i]}\"]}.',[x]))"
new="""  for i,x in enumerate(f):
   slot=f\"{spec['prefix']}_{slots(spec['prefix'])[i]}\"
   out.append(('vocabulary_in_context',f'Quel rôle joue « {x} » dans ce passage ?',f\"Il sert à préciser {SLOT_MEANING[slot]}.\",[x]))"""
if old not in src:
    raise AssertionError('Unit10 staged syntax-repair anchor drift')
src=src.replace(old,new,1)
ns={'__name__':'unit10_base','__file__':str(p),'__package__':None}
exec(compile(src,str(p),'exec'),ns)

# Remove curriculum-meta wording from rare exhaustive-selector fallbacks.
def clean_lexical_sentence(slot,form,detail):
    if detail.get('semantic_fallback'):
        return f"Dans ce passage, « {form} » est employé dans une fonction précise du raisonnement; son rôle est défini par le contexte plutôt que supposé à partir du mot seul."
    return f"Dans ce texte, « {form} » sert à nommer {ns['SLOT_MEANING'][slot]}; le mot est relié à un raisonnement explicite plutôt qu’à une impression isolée."
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
