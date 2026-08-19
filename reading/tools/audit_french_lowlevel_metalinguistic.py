import json, re, pathlib, hashlib

ROOT = pathlib.Path('.')
FILES = {
    'A1': ROOT / 'reading/french/a1/passages.jsonl',
    'A2': ROOT / 'reading/french/a2/passages.jsonl',
}
OUT = ROOT / 'reading/audit/french_a1_a2_metalinguistic_inventory_2026-08-19.json'

HIGH_PATTERNS = [
    r'cat[ée]gorie grammaticale', r'classe grammaticale', r'nature grammaticale',
    r'fonction grammaticale', r'r[oô]le grammatical', r'gramma(?:ire|tical)',
    r'quel(?:le)? (?:r[oô]le|fonction) joue', r'quel(?:le)? est (?:le|la) (?:r[oô]le|fonction)',
    r'quel temps', r'quel mode', r'conjug', r'accord', r'subordonn',
    r'groupe nominal', r'sujet grammatical', r'compl[ée]ment d[’\']objet',
]
META_TERMS = [
    'adverbe','adjectif','nom commun','nom propre','pronom','préposition','conjonction',
    'déterminant','article défini','article indéfini','infinitif','participe','auxiliaire',
    'sujet','complément','COD','COI','attribut','impératif','indicatif','conditionnel',
    'subjonctif','passé composé','imparfait','futur simple','présent de l’indicatif',
]


def load(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalize(s):
    return s.lower().replace('’', "'")

def target_forms(rec, q):
    by_id = {}
    for t in rec.get('new_lexical_targets', []) + rec.get('review_lexical_targets', []):
        by_id[t.get('id')] = t
    return [by_id[x] for x in q.get('target_ids', []) if x in by_id]

def context_window(text, forms):
    parts = re.split(r'(?<=[.!?])\s+', text.replace('\n', ' '))
    lows = [f.get('form','').lower() for f in forms if f.get('form')]
    hits=[]
    for s in parts:
        ls=s.lower()
        if any(f and f in ls for f in lows):
            hits.append(s.strip())
        if len(hits)>=2:
            break
    return ' '.join(hits)[:900]

rows=[]
counts={}
for level, path in FILES.items():
    records=load(path)
    assert len(records)==60, (level, len(records))
    assert [r['sequence'] for r in records] == list(range(1,61)), level
    level_count=0
    for rec in records:
        amap={a['id']:a for a in rec.get('answer_key',[])}
        for q in rec.get('questions',[]):
            prompt=q.get('prompt','')
            answer=amap.get(q.get('answer_id'),{}).get('answer','')
            qtype=str(q.get('type',''))
            hay=normalize(prompt+' '+answer+' '+qtype)
            reasons=[]
            for pat in HIGH_PATTERNS:
                if re.search(pat, hay, re.I): reasons.append('pattern:'+pat)
            if any(term.lower() in hay for term in META_TERMS):
                reasons.append('metalinguistic_terminology')
            if 'grammar' in qtype.lower() or 'morph' in qtype.lower() or 'syntax' in qtype.lower():
                reasons.append('question_type:'+qtype)
            if not reasons:
                continue
            forms=target_forms(rec,q)
            rows.append({
                'level':level,
                'passage_id':rec['id'],
                'sequence':rec['sequence'],
                'unit':rec.get('unit'),
                'title':rec.get('title'),
                'question_id':q.get('id'),
                'answer_id':q.get('answer_id'),
                'question_type':qtype,
                'prompt':prompt,
                'answer':answer,
                'target_ids':q.get('target_ids',[]),
                'target_forms':[{'id':t.get('id'),'form':t.get('form'),'lemma':t.get('lemma'),'role':'new' if t in rec.get('new_lexical_targets',[]) else 'review'} for t in forms],
                'context':context_window(rec.get('text',''),forms),
                'candidate_reasons':sorted(set(reasons)),
            })
            level_count+=1
    counts[level]=level_count

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    'audit':'French A1-A2 low-level metalinguistic/CEFR candidate inventory',
    'date':'2026-08-19',
    'scope':[str(p) for p in FILES.values()],
    'canonical_sha256':{k:file_hash(v) for k,v in FILES.items()},
    'status':'CANDIDATES_REQUIRE_SEMANTIC_ADJUDICATION',
    'candidate_counts':counts,
    'candidate_total':len(rows),
    'method':'High-recall candidate scan only; keyword/type hits are not automatically defects. Every candidate requires semantic CEFR/pedagogical adjudication before repair.',
    'candidates':rows,
}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'candidate_counts':counts,'candidate_total':len(rows)},ensure_ascii=False))
