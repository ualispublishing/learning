#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[2]
C1 = R / 'reading/french/c1/passages.jsonl'
C2 = R / 'reading/french/c2/passages.jsonl'
LOCK = R / 'reading/audit/french_c2_unit03_frontier_lock.json'
PLAN = R / 'reading/audit/french_c2_unit04_plan.json'
PROBE = R / 'reading/audit/french_c2_unit04_target_probe.json'
OUT = R / 'reading/audit/french_c2_unit04_target_selection.json'

# Five semantically coherent targets per standard passage. The frequency list is
# only a candidate pool; selection is driven by the Unit04 economics/complex-
# systems discourse rather than by rank order alone.
SELECTION = [
    ('p01_firm', 'entreprise'), ('p01_produce', 'produire'),
    ('p01_costs', 'frais'), ('p01_supply', 'offre'),
    ('p01_partner', 'partenaire'),

    ('p02_input', 'entrée'), ('p02_output', 'sortie'),
    ('p02_pressure', 'pression'), ('p02_movement', 'mouvement'),
    ('p02_transform', 'transformer'),

    ('p03_energy', 'énergie'), ('p03_number', 'nombre'),
    ('p03_move', 'déplacer'), ('p03_loss', 'perte'),
    ('p03_crisis', 'crise'),

    ('p04_own', 'posséder'), ('p04_private', 'privé'),
    ('p04_lend', 'prêter'), ('p04_deposit', 'déposer'),
    ('p04_responsibility', 'responsabilité'),

    ('p05_replace', 'remplacer'), ('p05_forbid', 'interdire'),
    ('p05_powerful', 'puissant'), ('p05_favour', 'faveur'),
    ('p05_fail', 'faillir'),
]


def blob(path: Path) -> str:
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def main() -> None:
    lock = json.loads(LOCK.read_text(encoding='utf-8'))
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    probe = json.loads(PROBE.read_text(encoding='utf-8'))
    c1 = blob(C1)
    c2 = blob(C2)

    if (
        lock.get('status') != 'PASS'
        or lock.get('last_sequence') != 18
        or lock.get('c1_canonical_blob') != c1
        or lock.get('c2_canonical_blob') != c2
    ):
        raise AssertionError('C2 Unit03 lock/live mismatch')
    if (
        plan.get('status') != 'PASS'
        or plan.get('c2_source_blob') != c2
        or probe.get('status') != 'PASS'
        or probe.get('c2_source_blob') != c2
    ):
        raise AssertionError('C2 Unit04 plan/probe stale')

    fresh = {x['form']: x for x in probe['fresh']}
    selected = []
    seen = set()
    for slot, form in SELECTION:
        if form not in fresh:
            raise AssertionError(f'C2 Unit04 target not fresh/source-backed: {form}')
        item = fresh[form]
        if item.get('rank', 0) <= 1000 or item.get('source_lexicon') != 'french_top3000.csv':
            raise AssertionError(f'advanced source invalid: {form}')
        if form in seen:
            raise AssertionError(f'duplicate target: {form}')
        seen.add(form)
        out = dict(item)
        out.update({
            'slot': slot,
            'semantic_fallback': False,
            'pedagogical_content_word': True,
        })
        selected.append(out)

    groups = {
        key: [x['form'] for x in selected if x['slot'].startswith(key + '_')]
        for key in ['p01', 'p02', 'p03', 'p04', 'p05']
    }
    if len(selected) != 25 or any(len(v) != 5 for v in groups.values()):
        raise AssertionError(f'Unit04 target structure failure: {groups}')

    artifact = {
        'status': 'PASS',
        'scope': 'French C2 Unit04 pedagogical target selection',
        'c1_canonical_blob': c1,
        'c2_source_blob': c2,
        'theme': plan['theme'],
        'genres': plan['genres'],
        'word_band': [plan['c2_word_min'], plan['c2_word_max']],
        'new_targets_per_standard_passage': lock['accepted_c2_default_new_targets_per_standard_passage'],
        'default_is_hard_quota': False,
        'selected_count': 25,
        'selected': selected,
        'passage_groups': groups,
        'source_policy': 'validated french_top3000.csv continuation rank > 1000',
        'semantic_fallback_count': 0,
        'pedagogical_filter': (
            'firm production and costs; flow/feedback structure; resource shocks and '
            'systemic loss; ownership/finance/liability; policy adaptation and power'
        ),
    }
    OUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'selected_count': 25, 'groups': groups}, ensure_ascii=False))


if __name__ == '__main__':
    main()
