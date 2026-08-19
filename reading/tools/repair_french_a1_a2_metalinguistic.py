import copy
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path('.')
FILES = {
    'A1': ROOT / 'reading/french/a1/passages.jsonl',
    'A2': ROOT / 'reading/french/a2/passages.jsonl',
}
INVENTORY = ROOT / 'reading/audit/french_a1_a2_metalinguistic_inventory_2026-08-19.json'
OUT = ROOT / 'reading/audit/french_a1_a2_metalinguistic_repair_2026-08-19.json'

EXPECTED_BEFORE = {
    'A1': '5f187a8bdce83812265b6c79bf505130f084f13f92bfc02b9d57df64efbdda42',
    'A2': '3c6dc3687fbacbd846c087d8041f2f0f58c0116b1dbf7008a64ad32611c4802a',
}

MANUAL = {
    ('fr-a2-u01-p01', 'q7'): {
        'type': 'cause_effect',
        'prompt': 'Pourquoi Camille suit-elle ce conseil ?',
        'answer': 'Parce qu’elle ne veut pas rester sans information.',
    },
    ('fr-a2-u02-p01', 'q7'): {
        'type': 'vocabulary_in_context',
        'prompt': 'Dans « la raison de ce changement », que signifie « raison » ?',
        'answer': 'La cause ou l’explication du changement.',
    },
    ('fr-a2-u02-p02', 'q7'): {
        'type': 'cloze_transfer',
        'prompt': 'Complète l’expression du texte : « avant de _____ une décision ».',
        'answer': '« prendre »',
    },
    ('fr-a2-u02-p03', 'q7'): {
        'type': 'cloze_transfer',
        'prompt': 'Complète l’expression du texte : « il est important de _____ ».',
        'answer': '« pratiquer »',
    },
}

FORMAL_PROMPT_MARKERS = [
    'quel type de mot', 'quelle catégorie grammaticale', 'classe grammaticale',
    'nature grammaticale', 'fonction grammaticale', 'rôle grammatical',
    'quel type de pronom', 'après une préposition', 'quelle forme suit',
    'quelle forme vient après', 'que complète',
]
FORMAL_ANSWER_MARKERS = [
    'un déterminant possessif', 'un pronom personnel', 'un infinitif',
    'un adjectif.', 'un verbe.', 'un nom.',
]


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def dump_jsonl(path, rows):
    path.write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + '\n', encoding='utf-8')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(s):
    return str(s).lower().replace('’', "'")


def classify(candidate):
    level = candidate['level']
    qtype = candidate['question_type']
    prompt = norm(candidate['prompt'])
    answer = norm(candidate['answer'])
    reasons = []
    if qtype == 'grammar_category':
        reasons.append('formal_grammar_category_retrieval')
    if qtype == 'grammar_function':
        reasons.append('low_level_function_label_task')
    if qtype == 'grammar_in_context' and (
        any(x in prompt for x in ('quelle forme suit', 'quelle forme vient après', 'que complète'))
        or any(x in answer for x in ('un infinitif', 'le nom «', 'le nom "'))
    ):
        reasons.append('formal_grammar_in_context_retrieval')
    if level == 'A1' and any(x in prompt for x in FORMAL_PROMPT_MARKERS):
        reasons.append('a1_explicit_metalinguistic_prompt')
    return sorted(set(reasons))


def find_target_form(rec, candidate):
    ids = candidate.get('target_ids') or []
    if not ids:
        return None
    targets = {}
    for t in rec.get('new_lexical_targets', []) + rec.get('review_lexical_targets', []):
        if t.get('id'):
            targets[t['id']] = t
    forms = [targets[x].get('form') for x in ids if x in targets and targets[x].get('form')]
    if not forms:
        forms = [x.get('form') for x in candidate.get('target_forms', []) if x.get('form')]
    # This repair class should have a single focal form. Fail closed rather than choose silently.
    unique = []
    for f in forms:
        if f not in unique:
            unique.append(f)
    if len(unique) != 1:
        raise AssertionError((rec['id'], candidate['question_id'], 'expected one focal target form', unique))
    return unique[0]


def sentence_cloze(text, form):
    # Exact lexical-form match with Unicode-aware word boundaries.
    pat = re.compile(r'(?<!\w)' + re.escape(form) + r'(?!\w)', re.IGNORECASE)
    m = pat.search(text)
    if not m:
        raise AssertionError(('target form not found in passage text', form))
    left_candidates = [text.rfind(ch, 0, m.start()) for ch in '.!?\n']
    left = max(left_candidates) + 1
    right_positions = []
    for ch in '.!?\n':
        pos = text.find(ch, m.end())
        if pos != -1:
            right_positions.append(pos)
    right = min(right_positions) + 1 if right_positions else len(text)
    sentence = text[left:right].strip()
    # Keep cloze readable if the source sentence is unusually long.
    local_match = pat.search(sentence)
    if not local_match:
        raise AssertionError(('target lost while extracting sentence', form, sentence))
    if len(sentence) > 220:
        a = max(0, local_match.start() - 85)
        b = min(len(sentence), local_match.end() + 105)
        fragment = sentence[a:b].strip()
        if a > 0:
            fragment = '… ' + fragment.lstrip(' ,;:')
        if b < len(sentence):
            fragment = fragment.rstrip(' ,;:') + ' …'
        sentence = fragment
        local_match = pat.search(sentence)
        if not local_match:
            raise AssertionError(('target lost in shortened cloze', form, sentence))
    surface = local_match.group(0)
    cloze = sentence[:local_match.start()] + '_____' + sentence[local_match.end():]
    return cloze, surface


before_hashes = {level: sha256(path) for level, path in FILES.items()}
assert before_hashes == EXPECTED_BEFORE, ('canonical drift', before_hashes, EXPECTED_BEFORE)

inventory = json.loads(INVENTORY.read_text(encoding='utf-8'))
assert inventory['canonical_sha256'] == EXPECTED_BEFORE
assert inventory['candidate_total'] == 88

corpora = {level: load_jsonl(path) for level, path in FILES.items()}
for level, rows in corpora.items():
    assert len(rows) == 60, (level, len(rows))
    assert [r['sequence'] for r in rows] == list(range(1, 61)), level

index = {r['id']: r for rows in corpora.values() for r in rows}
confirmed = []
false_positives = []
changed_records = set()
transformations = []

for cand in inventory['candidates']:
    reasons = classify(cand)
    if not reasons:
        false_positives.append({
            'level': cand['level'], 'passage_id': cand['passage_id'],
            'question_id': cand['question_id'], 'question_type': cand['question_type'],
            'prompt': cand['prompt'], 'decision': 'RETAIN',
            'rationale': 'Candidate does not require formal grammatical-category/function terminology under the adjudication rule; ordinary form-choice, comprehension, sequence, inference, or contextual-meaning tasks are retained.'
        })
        continue

    rec = index[cand['passage_id']]
    q = next(x for x in rec['questions'] if x['id'] == cand['question_id'])
    a = next(x for x in rec['answer_key'] if x['id'] == cand['answer_id'])
    assert q['prompt'] == cand['prompt'], (rec['id'], q['id'], 'prompt drift')
    assert a['answer'] == cand['answer'], (rec['id'], a['id'], 'answer drift')
    old = {'type': q['type'], 'prompt': q['prompt'], 'answer': a['answer'], 'target_ids': copy.deepcopy(q.get('target_ids', []))}

    manual = MANUAL.get((rec['id'], q['id']))
    if manual:
        q['type'] = manual['type']
        q['prompt'] = manual['prompt']
        a['answer'] = manual['answer']
    else:
        form = find_target_form(rec, cand)
        if not form:
            raise AssertionError((rec['id'], q['id'], 'confirmed defect lacks focal target and manual repair'))
        cloze, surface = sentence_cloze(rec['text'], form)
        q['type'] = 'cloze_transfer'
        q['prompt'] = f'Complète avec le mot du texte qui convient : « {cloze} »'
        a['answer'] = f'« {surface} »'

    # Preserve target linkage exactly; only task framing/answer changes.
    assert q.get('target_ids', []) == old['target_ids'], (rec['id'], q['id'], 'target linkage changed')
    changed_records.add(rec['id'])
    confirmed.append({
        'level': cand['level'], 'passage_id': rec['id'], 'question_id': q['id'],
        'decision': 'REPAIR', 'reasons': reasons
    })
    transformations.append({
        'level': cand['level'], 'passage_id': rec['id'], 'sequence': rec['sequence'],
        'question_id': q['id'], 'answer_id': a['id'], 'reasons': reasons,
        'before': old,
        'after': {'type': q['type'], 'prompt': q['prompt'], 'answer': a['answer'], 'target_ids': copy.deepcopy(q.get('target_ids', []))},
    })

for rec_id in changed_records:
    index[rec_id]['revision'] = int(index[rec_id].get('revision', 1)) + 1

# Whole-corpus structural and linkage checks after repair.
allowed_types = {
    'gist','literal_detail','sequence','cause_effect','reference_resolution','vocabulary_in_context',
    'single_word_definition','cloze_transfer','grammar_in_context','grammar_category','grammar_choice',
    'grammar_identification','grammar_function','person_form','contrast','paraphrase','inference','motive',
    'main_claim','argument_relation','stance','tone','rhetorical_function','assumption','ambiguity_resolution',
    'summary','synthesis','cross_text_synthesis','register_style'
}
for level, rows in corpora.items():
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)) == 60
    for rec in rows:
        assert rec['cefr'] == level
        assert len(rec['questions']) == 10, rec['id']
        assert len(rec['answer_key']) == 10, rec['id']
        qids = [q['id'] for q in rec['questions']]
        aids = [a['id'] for a in rec['answer_key']]
        assert len(qids) == len(set(qids)) == 10
        assert len(aids) == len(set(aids)) == 10
        assert {q['answer_id'] for q in rec['questions']} == set(aids), rec['id']
        assert {a['question_id'] for a in rec['answer_key']} == set(qids), rec['id']
        assert all(q['type'] in allowed_types for q in rec['questions'])

# Every inventory candidate is explicitly adjudicated.
assert len(confirmed) + len(false_positives) == 88

# Fail closed if the defined low-level formal-label class remains.
residue = []
for level, rows in corpora.items():
    for rec in rows:
        amap = {a['id']: a for a in rec['answer_key']}
        for q in rec['questions']:
            answer = amap[q['answer_id']]['answer']
            p = norm(q['prompt'])
            aa = norm(answer)
            formal = []
            if q['type'] in {'grammar_category', 'grammar_function'}:
                formal.append('formal_question_type')
            if q['type'] == 'grammar_in_context' and (
                any(x in p for x in ('quelle forme suit', 'quelle forme vient après', 'que complète'))
                or any(x in aa for x in ('un infinitif', 'le nom «', 'le nom "'))
            ):
                formal.append('formal_grammar_in_context')
            if level == 'A1' and any(x in p for x in FORMAL_PROMPT_MARKERS):
                formal.append('a1_explicit_metalinguistic_prompt')
            if formal:
                residue.append({'level': level, 'passage_id': rec['id'], 'question_id': q['id'], 'hits': formal, 'prompt': q['prompt'], 'answer': answer})
if residue:
    raise SystemExit('UNRESOLVED DEFINED DEFECT CLASS: ' + json.dumps(residue, ensure_ascii=False))

# Verify untouched passage/lexical content for changed records against a fresh source copy is implicit in
# this script's question-only mutations; assert target forms still occur where the new cloze relies on them.
for t in transformations:
    if t['after']['type'] == 'cloze_transfer' and t['after']['target_ids']:
        rec = index[t['passage_id']]
        answer_surface = t['after']['answer'].strip('«»')
        assert answer_surface.lower() in rec['text'].lower(), (t['passage_id'], t['question_id'], answer_surface)

for level, path in FILES.items():
    dump_jsonl(path, corpora[level])
after_hashes = {level: sha256(path) for level, path in FILES.items()}
assert after_hashes != before_hashes

OUT.write_text(json.dumps({
    'audit': 'French A1-A2 metalinguistic/CEFR pedagogy defect-class repair',
    'date': '2026-08-19',
    'status': 'REPAIRED_DEFINED_CLASS_STRUCTURAL_PASS_HUMAN_DIFF_REVIEW_REQUIRED',
    'scope': [str(FILES['A1']), str(FILES['A2'])],
    'before_sha256': before_hashes,
    'after_sha256': after_hashes,
    'inventory_candidate_total': 88,
    'confirmed_defect_count': len(confirmed),
    'false_positive_count': len(false_positives),
    'changed_passage_count': len(changed_records),
    'changed_passage_ids': sorted(changed_records),
    'adjudication_rule': {
        'repair': [
            'all grammar_category tasks in A1-A2',
            'all grammar_function tasks in A1-A2',
            'grammar_in_context tasks that explicitly require formal structural labels/forms',
            'A1 non-grammar-type candidates that explicitly require formal grammar terminology'
        ],
        'retain': [
            'ordinary form-choice recognition without terminology burden',
            'literal/sequence/inference/content questions that matched scanner text accidentally',
            'contextual meaning/order/purpose questions that do not require naming a grammar category'
        ]
    },
    'confirmed': confirmed,
    'false_positives': false_positives,
    'transformations': transformations,
    'validation': {
        'json_parse': 'PASS',
        '60_records_each_level': 'PASS',
        'sequence_continuity': 'PASS',
        'unique_record_ids': 'PASS',
        'ten_questions_ten_answers': 'PASS',
        'question_answer_linkage': 'PASS',
        'target_ids_preserved_on_repaired_questions': 'PASS',
        'defined_defect_class_residue': 0,
        'all_88_candidates_adjudicated': 'PASS'
    },
    'release_effect': 'French remains REOPEN_REQUIRED. Canonical A1/A2 hashes changed and all hash-bound educator/native/tool/model/human certification gates must use the repaired hashes.',
    'next_gate': 'Human semantic review of every transformed Q/A in passage context, followed by repaired-corpus deterministic and broader educator recertification.'
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(json.dumps({
    'confirmed': len(confirmed), 'false_positives': len(false_positives),
    'changed_passages': len(changed_records), 'before': before_hashes, 'after': after_hashes
}, ensure_ascii=False, indent=2))
