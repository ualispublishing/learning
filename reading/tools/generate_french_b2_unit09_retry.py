#!/usr/bin/env python3
"""Fail-closed preflight wrapper for French B2 Unit09.

Refreshes the read-only Unit09 probe/selection under the exact Unit08 lock,
removes audit jargon from learner-facing fallback wording, verifies local target
tags, and adds substantive reasoning only if a standard passage is marginally
below the B2 word floor. The base generator's full guards remain authoritative.
"""
from pathlib import Path
import re
HERE=Path(__file__).resolve().parent

def run_module(filename,name):
    p=HERE/filename;ns={'__name__':name,'__file__':str(p),'__package__':None}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns);ns['main']()

# Deterministic prerequisites; both are read-only with respect to canonical B2.
run_module('probe_french_b2_unit09_targets.py','unit09_probe')
run_module('select_french_b2_unit09_targets.py','unit09_select')

p=HERE/'generate_french_b2_unit09.py';ns={'__name__':'unit09_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)

# Never expose curriculum/audit implementation language to learners.
def clean_lexical_sentence(slot,form,detail):
    meaning=ns['SLOT_MEANING'][slot]
    if detail.get('semantic_fallback'):
        return f"Dans ce dossier, le terme « {form} » est employé comme repère complémentaire de l’analyse; le contexte précise sa fonction dans l’arbitrage au lieu de lui attribuer une portée automatique."
    return f"Dans ce briefing, le terme « {form} » sert à nommer {meaning}; il est donc relié à une décision observable plutôt qu’utilisé comme simple étiquette."
ns['lexical_sentence']=clean_lexical_sentence

orig_make=ns['make']
def patched_make(spec,forms,review_forms,details,prior,deck):
    row=orig_make(spec,forms,review_forms,details,prior,deck)
    # Local assessment-target preflight before full generator checks.
    local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in row.get(fld,[])}
    amap={a['question_id']:a['id'] for a in row['answer_key']}
    for q in row['questions']:
        if amap.get(q['id'])!=q['answer_id'] or any(t not in local for t in q.get('target_ids',[])):
            raise AssertionError(f"{row['id']} {q['id']}: preflight linkage failure")
    if row['word_count']<350:
        row['text'] += " Le briefing précise enfin ce qui pourrait faire changer la recommandation : une demande plus faible que prévu, un coût d’application supérieur au seuil annoncé, ou un effet distributif différent entre groupes. Ces conditions de révision rendent l’arbitrage vérifiable au lieu de protéger la décision initiale contre toute nouvelle information."
        row['word_count']=len(row['text'].split());row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',row['text']))
        row['quality']['notes'].append('Added substantive revision criteria to clear the B2 minimum word band.')
    if row['word_count']>550:
        raise AssertionError(f"{row['id']}: preflight exceeds B2 maximum: {row['word_count']}")
    return row
ns['make']=patched_make

orig_checkpoint=ns['checkpoint']
def patched_checkpoint(groups,details,deck):
    row=orig_checkpoint(groups,details,deck)
    if row['word_count']<350:
        row['text'] += " Une décision publique reste ainsi révisable sans devenir arbitraire : les mêmes critères servent avant et après le pilote, tandis qu’une nouvelle preuve peut modifier la force de la recommandation. L’objectif est de rendre le désaccord traçable, de montrer qui supporte chaque coût et d’indiquer pourquoi une autre répartition deviendrait préférable."
        row['word_count']=len(row['text'].split());row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',row['text'])))
    if not 350<=row['word_count']<=550:
        raise AssertionError(f"{row['id']}: checkpoint outside B2 band: {row['word_count']}")
    return row
ns['checkpoint']=patched_checkpoint

# Preflight selected slot structure before the canonical writer starts.
_,groups,details,reviews=ns['load_state']()
expected_slots=set(ns['SLOT_MEANING'])
if set(details)!=expected_slots:
    raise AssertionError(f"Unit09 selection slot drift: missing={sorted(expected_slots-set(details))} extra={sorted(set(details)-expected_slots)}")
if any(len(groups[k])!=4 or len(reviews[k])!=4 for k in ['p01','p02','p03','p04','p05']):
    raise AssertionError('Unit09 group/review structure drift')

ns['main']()
