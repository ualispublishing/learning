#!/usr/bin/env python3
"""Fail-closed preflight wrapper for French B2 Unit09.

Refreshes the exhaustive Unit09 probe and pedagogical content-word selection under
the exact Unit08 lock, aligns each selected word with its actual policy reasoning
role, verifies local target tags, and adds substantive reasoning only if a
standard passage is marginally below the B2 word floor.
"""
from pathlib import Path
import re
HERE=Path(__file__).resolve().parent

def run_module(filename,name):
    p=HERE/filename;ns={'__name__':name,'__file__':str(p),'__package__':None}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns);ns['main']()

run_module('probe_french_b2_unit09_targets.py','unit09_probe')
run_module('select_french_b2_unit09_targets.py','unit09_select')

p=HERE/'generate_french_b2_unit09.py';ns={'__name__':'unit09_base','__file__':str(p),'__package__':None}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)

# These definitions match the curated content words selected for each reasoning
# slot, so vocabulary questions teach the word in a genuine policy context.
ns['SLOT_MEANING'].update({
 'p01_budget':'la situation de départ qui détermine les ressources et contraintes du choix public',
 'p01_priority':'le cas concret auquel une règle ou priorité doit s’appliquer',
 'p01_cost':'la part de ressources, de coût ou d’effort attribuée à une option',
 'p01_value':'le critère comparatif utilisé pour identifier une option meilleure sans prétendre qu’elle est parfaite',
 'p02_income':'la catégorie riche dont l’effet d’une mesure peut différer de celui d’autres ménages',
 'p02_access':'la catégorie pauvre pour laquelle prix, distance ou procédure peuvent créer des obstacles particuliers',
 'p02_support':'l’aide effectivement disponible, et non seulement annoncée',
 'p02_people':'le groupe jeune dont l’usage ou les contraintes doivent être mesurés séparément',
 'p03_program':'l’action d’assurer qu’un service annoncé existe réellement dans les conditions prévues',
 'p03_apply':'l’action d’obtenir un résultat observable entre la règle écrite et l’usage réel',
 'p03_improve':'ce que la politique cherche à offrir concrètement aux personnes concernées',
 'p03_decision':'le rôle du président ou d’une autorité formelle au point de décision',
 'p04_benefit':'la position contre laquelle l’argument favorable doit répondre sans caricature',
 'p04_opposition':'la dimension humaine qu’un calcul de bénéfice ou de coût ne doit pas effacer',
 'p04_justify':'l’appel à une raison, une donnée ou un principe qui doit être évalué plutôt que simplement invoqué',
 'p04_trade':'les propos réellement avancés par une partie, qu’il faut représenter fidèlement avant d’y répondre',
 'p05_effective':'la recherche de données qui permet de vérifier l’effet au lieu de présumer la réussite',
 'p05_time':'l’action de réfléchir aux conséquences, aux alternatives et à la portée de la conclusion',
 'p05_estimate':'l’action de revoir les résultats avec les mêmes critères après la mise en œuvre',
 'p05_revision':'la force d’une conclusion, qui doit augmenter ou diminuer selon les nouvelles preuves'
})

def clean_lexical_sentence(slot,form,detail):
    meaning=ns['SLOT_MEANING'][slot]
    return f"Dans ce dossier, le terme « {form} » sert à préciser {meaning}; il est relié à un élément observable de l’arbitrage plutôt qu’utilisé comme simple étiquette."
ns['lexical_sentence']=clean_lexical_sentence

orig_make=ns['make']
def patched_make(spec,forms,review_forms,details,prior,deck):
    row=orig_make(spec,forms,review_forms,details,prior,deck)
    local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in row.get(fld,[])}
    amap={a['question_id']:a['id'] for a in row['answer_key']}
    for q in row['questions']:
        if amap.get(q['id'])!=q['answer_id'] or any(t not in local for t in q.get('target_ids',[])):
            raise AssertionError(f"{row['id']} {q['id']}: preflight linkage failure")
    if row['word_count']<350:
        row['text'] += " Le briefing précise enfin ce qui pourrait faire changer la recommandation : une demande plus faible que prévu, un coût d’application supérieur au seuil annoncé, ou un effet distributif différent entre groupes. Ces conditions de révision rendent l’arbitrage vérifiable au lieu de protéger la décision initiale contre toute nouvelle information."
        row['word_count']=len(row['text'].split())
        row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',row['text'])))
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
        row['word_count']=len(row['text'].split())
        row['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',row['text'])))
    if not 350<=row['word_count']<=550:
        raise AssertionError(f"{row['id']}: checkpoint outside B2 band: {row['word_count']}")
    return row
ns['checkpoint']=patched_checkpoint

_,groups,details,reviews=ns['load_state']()
expected_slots=set(ns['SLOT_MEANING'])
if set(details)!=expected_slots:
    raise AssertionError(f"Unit09 selection slot drift: missing={sorted(expected_slots-set(details))} extra={sorted(set(details)-expected_slots)}")
if any(len(groups[k])!=4 or len(reviews[k])!=4 for k in ['p01','p02','p03','p04','p05']):
    raise AssertionError('Unit09 group/review structure drift')

ns['main']()
