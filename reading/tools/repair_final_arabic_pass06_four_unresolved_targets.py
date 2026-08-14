#!/usr/bin/env python3
"""Resolve the final four source-identity mismatches from Pass 06.

Policy:
- انتقال remains natural support vocabulary; deliberate ranked target becomes
  نقل/ar-r316 in A2 U06 P03, with lexical questions rewritten accordingly.
- أظهرت is a transparent surface form of lemma أظهر/ar-r1128.
- رئيسية is feminine of adjective رئيسي/ar-r905.
- noun توقعات is not falsely mapped to the verb row. The ranked verb
  توقع/ar-r1349 is introduced in A2 U07 P04 (where it already occurs naturally)
  and reviewed in P05; noun توقعات remains support vocabulary elsewhere.
All stale wrong IDs ar-r800/ar-r913/ar-r998/ar-r986 are removed corpus-wide.
"""
from __future__ import annotations
import json,re,unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OLD_IDS=('ar-r800','ar-r913','ar-r998','ar-r986')
NEW_IDS=('ar-r316','ar-r1128','ar-r905','ar-r1349')

loaded={}
for level in LEVELS:
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    loaded[level]=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
by={r['id']:r for rows in loaded.values() for r in rows}

# Guard exact pre-repair usage counts from the persisted audit inventory.
counts={tid:Counter() for tid in OLD_IDS}
for rows in loaded.values():
    for r in rows:
        for t in r.get('new_lexical_targets',[]):
            if isinstance(t,dict) and t.get('id') in counts: counts[t['id']]['new']+=1
        for t in r.get('review_lexical_targets',[]):
            if isinstance(t,dict) and t.get('id') in counts: counts[t['id']]['review']+=1
        for q in r.get('questions',[]):
            if isinstance(q,dict):
                for tid in q.get('target_ids',[]) if isinstance(q.get('target_ids'),list) else []:
                    if tid in counts: counts[tid]['questions']+=1
expected={
 'ar-r800':Counter(new=1,review=4,questions=5),
 'ar-r913':Counter(new=1,review=4,questions=4),
 'ar-r998':Counter(new=1,review=2,questions=4),
 'ar-r986':Counter(new=1,review=6,questions=7),
}
assert counts==expected,(counts,expected)

# New candidate IDs must not already be deliberate introductions.
for nid in NEW_IDS:
    intro=[]
    for rows in loaded.values():
        for r in rows:
            intro += [(r['id'],t.get('form')) for t in r.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==nid]
    assert not intro,(nid,intro)

# 1) U06 P03: replace false انتقال rank target with genuine نقل/ar-r316.
r=by['ar-a2-u06-p03']
hits=[t for t in r['new_lexical_targets'] if t.get('id')=='ar-r800']
assert len(hits)==1 and hits[0].get('form')=='انتقال',hits
t=hits[0]
t.update({
 'form':'نقل','lemma':'نقل','id':'ar-r316','intended_sense':'transport; transfer',
 'part_of_speech':'noun','source_rank':316,'source_lexicon':'arabic_top1000.csv',
 'exposures_in_text':2,
})
old1='قارنت عدة وسائل للوصول؛'
new1='قارنت عدة وسائل نقل للوصول؛'
old2='عندما تستخدم أكثر من وسيلة في رحلة واحدة،'
new2='عندما تستخدم أكثر من وسيلة نقل في رحلة واحدة،'
assert r['text'].count(old1)==1 and r['text'].count(old2)==1
r['text']=r['text'].replace(old1,new1).replace(old2,new2)
q={x['id']:x for x in r['questions']};a={x['question_id']:x for x in r['answer_key']}
assert q['q3']['target_ids']==['ar-r800'] and q['q6']['target_ids']==['ar-r800'] and q['q9']['target_ids']==['ar-r800']
q['q3']['prompt']='ماذا يعني «نقل» في «وسائل نقل»؟';q['q3']['target_ids']=['ar-r316'];a['q3']['answer']='وسائل تُستخدم للانتقال من مكان إلى آخر.'
q['q6']['prompt']='ما معنى «نقل» في هذا السياق؟';q['q6']['target_ids']=['ar-r316'];a['q6']['answer']='تحريك الأشخاص أو الأشياء من مكان إلى آخر.'
q['q9']['prompt']='أكمل: القطار والحافلة من وسائل _____ داخل المدينة.';q['q9']['target_ids']=['ar-r316'];a['q9']['answer']='النقل'

# Remove all later false ar-r800 review bookkeeping and nonlexical target refs.
for rows in loaded.values():
    for row in rows:
        row['review_lexical_targets']=[x for x in row.get('review_lexical_targets',[]) if not (isinstance(x,dict) and x.get('id')=='ar-r800')]
        if row['id']!='ar-a2-u06-p03':
            for qq in row.get('questions',[]):
                if isinstance(qq,dict) and isinstance(qq.get('target_ids'),list):
                    qq['target_ids']=[tid for tid in qq['target_ids'] if tid!='ar-r800']

# 2) U07 P04: correct أظهرت to lemma أظهر/ar-r1128 and introduce توقع/ar-r1349.
r4=by['ar-a2-u07-p04']
h=[t for t in r4['new_lexical_targets'] if t.get('id')=='ar-r913']
assert len(h)==1 and h[0].get('form')=='أظهرت',h
h[0].update({'id':'ar-r1128','lemma':'أظهر','part_of_speech':'verb','source_rank':1128,'source_lexicon':'arabic_top3000.csv','intended_sense':'show; demonstrate'})
# Update all old أظهرت references to the corrected ID.
for rows in loaded.values():
    for row in rows:
        for tt in row.get('review_lexical_targets',[]):
            if isinstance(tt,dict) and tt.get('id')=='ar-r913':
                assert tt.get('form')=='أظهرت',(row['id'],tt)
                tt['id']='ar-r1128'
        for qq in row.get('questions',[]):
            if isinstance(qq,dict) and isinstance(qq.get('target_ids'),list):
                qq['target_ids']=['ar-r1128' if tid=='ar-r913' else tid for tid in qq['target_ids']]
# The verb already occurs naturally twice in P04 (توقع / توقعوا); introduce its lemma.
assert 'توقع المنظمون' in r4['text'] and 'توقعوا' in r4['text']
r4['new_lexical_targets'].append({
 'beyond_base':False,'context_strategy':['cause_consequence'],'exposures_in_text':2,
 'first_introduced':True,'form':'توقع','id':'ar-r1349','intended_sense':'expect; anticipate',
 'lemma':'توقع','part_of_speech':'verb','register':'contemporary standard',
 'source_lexicon':'arabic_top3000.csv','source_rank':1349,'variety':'MSA'
})

# 3) U07 P05: correct رئيسية to رئيسي/ar-r905; توقع becomes review, not noun target.
r5=by['ar-a2-u07-p05']
h=[t for t in r5['new_lexical_targets'] if t.get('id')=='ar-r998']
assert len(h)==1 and h[0].get('form')=='رئيسية',h
h[0].update({'id':'ar-r905','lemma':'رئيسي','part_of_speech':'adjective','source_rank':905,'source_lexicon':'arabic_top1000.csv','intended_sense':'main; principal'})
# Update all رئيسية reviews/questions globally.
for rows in loaded.values():
    for row in rows:
        for tt in row.get('review_lexical_targets',[]):
            if isinstance(tt,dict) and tt.get('id')=='ar-r998':
                assert tt.get('form')=='رئيسية',(row['id'],tt)
                tt['id']='ar-r905'
        for qq in row.get('questions',[]):
            if isinstance(qq,dict) and isinstance(qq.get('target_ids'),list):
                qq['target_ids']=['ar-r905' if tid=='ar-r998' else tid for tid in qq['target_ids']]
# Remove the false noun توقعات introduction.
false=[t for t in r5['new_lexical_targets'] if t.get('id')=='ar-r986']
assert len(false)==1 and false[0].get('form')=='توقعات',false
r5['new_lexical_targets']=[t for t in r5['new_lexical_targets'] if t is not false[0]]
# Add a legitimate review target for the verb introduced in P04; the text has يتوقعون.
assert 'يتوقعون' in r5['text']
r5.setdefault('review_lexical_targets',[]).append({'form':'يتوقعون','id':'ar-r1349','representation':'running_text','review_stage':'R1'})
# Rewrite only the three noun-target assessment items to test the ranked verb.
q={x['id']:x for x in r5['questions']};a={x['question_id']:x for x in r5['answer_key']}
assert q['q4']['target_ids']==['ar-r986'] and q['q7']['target_ids']==['ar-r986'] and q['q10']['target_ids']==['ar-r986']
q['q4']['prompt']='ماذا يعني «يتوقعون» في قول المعلمة إن المنظمين يتوقعون هذا العدد؟';q['q4']['target_ids']=['ar-r1349'];a['q4']['answer']='يعتقدون أن هذا العدد قد يحضر مستقبلًا، من دون تأكيد.'
q['q7']['prompt']='ما معنى «يتوقع»؟';q['q7']['target_ids']=['ar-r1349'];a['q7']['answer']='يظن أن شيئًا سيحدث مستقبلًا بناءً على معلومات أو تقدير.'
q['q10']['prompt']='أكمل: _____ المنظمون حضور عدد كبير إذا كان الطقس مناسبًا.';q['q10']['target_ids']=['ar-r1349'];a['q10']['answer']='يتوقع'
# Align grammar-target wording to the ranked verb.
for gt in r5.get('grammar_targets',[]):
    if gt.get('id')=='ar-a2-expectations':gt['description']='يتوقع أن... / يتوقعون...'

# Remove every remaining false ar-r986 review and target reference elsewhere.
for rows in loaded.values():
    for row in rows:
        row['review_lexical_targets']=[x for x in row.get('review_lexical_targets',[]) if not (isinstance(x,dict) and x.get('id')=='ar-r986')]
        if row['id']!='ar-a2-u07-p05':
            for qq in row.get('questions',[]):
                if isinstance(qq,dict) and isinstance(qq.get('target_ids'),list):
                    qq['target_ids']=[tid for tid in qq['target_ids'] if tid!='ar-r986']

# Annotate/recount all passages changed by any old/new ID reference or direct text/question edits.
changed_ids=set()
# Determine changed rows conservatively from known usages and core edited passages.
changed_ids.update(['ar-a2-u06-p03','ar-a2-u06-p04','ar-a2-u06-p06','ar-a2-u10-p03','ar-a2-u10-p06',
                    'ar-a2-u07-p04','ar-a2-u07-p05','ar-a2-u07-p06','ar-a2-u08-p03','ar-a2-u10-p04',
                    'ar-b1-u08-p01','ar-a2-u10-p05','ar-b1-u02-p05'])
for pid in changed_ids:
    row=by[pid]
    row['word_count']=len(str(row.get('text','')).split())
    row['revision']=int(row.get('revision',1))+1
    notes=row.setdefault('quality',{}).setdefault('notes',[])
    note='Final audit Pass 06 repair: resolved remaining source-identity mismatches using source-supported ranked lemmas; unsupported noun surfaces remain ordinary support vocabulary rather than false ranked targets.'
    if note not in notes:notes.append(note)

# Hard postconditions: old wrong IDs disappear entirely.
remaining=[]
new_intro={nid:[] for nid in NEW_IDS}
for rows in loaded.values():
    for row in rows:
        for t in row.get('new_lexical_targets',[]):
            if isinstance(t,dict):
                if t.get('id') in OLD_IDS:remaining.append((row['id'],'new',t.get('id'),t.get('form')))
                if t.get('id') in new_intro:new_intro[t['id']].append((row['id'],t.get('form'),t.get('lemma'),t.get('part_of_speech')))
        for t in row.get('review_lexical_targets',[]):
            if isinstance(t,dict) and t.get('id') in OLD_IDS:remaining.append((row['id'],'review',t.get('id'),t.get('form')))
        for qq in row.get('questions',[]):
            for tid in qq.get('target_ids',[]) if isinstance(qq,dict) and isinstance(qq.get('target_ids'),list) else []:
                if tid in OLD_IDS:remaining.append((row['id'],'question',tid,qq.get('id')))
assert not remaining,remaining
assert all(len(v)==1 for v in new_intro.values()),new_intro
assert new_intro['ar-r316'][0][1:]==('نقل','نقل','noun')
assert new_intro['ar-r1128'][0][1:]==('أظهرت','أظهر','verb')
assert new_intro['ar-r905'][0][1:]==('رئيسية','رئيسي','adjective')
assert new_intro['ar-r1349'][0][1:]==('توقع','توقع','verb')

for level,rows in loaded.items():
    if any(r['id'] in changed_ids for r in rows):
        p=ROOT/f'reading/arabic/{level}/passages.jsonl'
        p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'resolved_old_ids':OLD_IDS,'new_introductions':new_intro,'changed_passages':len(changed_ids)},ensure_ascii=False))
