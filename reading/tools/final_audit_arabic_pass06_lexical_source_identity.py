#!/usr/bin/env python3
"""Final Arabic review pass 06: lexical source identity and homograph precision.

Rank/source/surface-or-lemma identity and broad part-of-speech compatibility are
hard gates. Intended-sense wording remains a separate semantic review lens.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass06_lexical_source_identity.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
RANK_RE=re.compile(r'\bRank:\s*(\d+)')
POS_RE=re.compile(r'^Part of speech:\s*(.+)$',re.M|re.I)
MEANING_RE=re.compile(r'^Meaning:\s*(.+)$',re.M|re.I)
ID_RE=re.compile(r'^ar-r(\d+)$')
def norm(s):
    s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا')
    s=DIAC.sub('',s)
    return ''.join(s.split())
def pos_classes(s):
    s=str(s or '').lower();out=set()
    if any(x in s for x in ('verb','perfect','imperfect','imperative')):out.add('verb')
    if 'noun' in s:out.add('noun')
    if 'adjective' in s or re.search(r'\badj\b',s):out.add('adjective')
    if 'adverb' in s:out.add('adverb')
    if 'preposition' in s or re.search(r'\bprep\b',s):out.add('preposition')
    if 'pronoun' in s:out.add('pronoun')
    if 'conjunction' in s or re.search(r'\bconj\b',s):out.add('conjunction')
    if 'particle' in s:out.add('particle')
    if any(x in s for x in ('numeral','number')):out.add('numeral')
    if 'interjection' in s:out.add('interjection')
    if 'proper' in s:out.add('proper')
    return out
def read_ranked(name):
    idx={}
    with (ROOT/name).open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            back=row.get('Back','') or '';m=RANK_RE.search(back)
            if not m:continue
            rank=int(m.group(1));pm=POS_RE.search(back);mm=MEANING_RE.search(back)
            idx[rank]={'front':row.get('Front',''),'back':back,'source_file':name,'source_pos':pm.group(1).strip() if pm else '', 'source_meaning':mm.group(1).strip() if mm else ''}
    return idx
def add(bucket,code,**kw):bucket.append({'code':code,**kw})
def main():
    sources={**read_ranked('arabic_top1000.csv'),**read_ranked('arabic_top3000.csv')}
    assert len(sources)==3000,len(sources)
    hard=[];warnings=[];surfaces=defaultdict(list);new_count=0;ranked_count=0
    level_summary={level:Counter() for level in LEVELS};seen_ids={}
    for level in LEVELS:
        p=ROOT/f'reading/arabic/{level}/passages.jsonl'
        for line in p.read_text(encoding='utf-8').splitlines():
            if not line.strip():continue
            r=json.loads(line);pid=r['id']
            for t in r.get('new_lexical_targets',[]):
                if not isinstance(t,dict):continue
                new_count+=1;level_summary[level]['new_targets']+=1
                tid=str(t.get('id',''));form=t.get('form','');lemma=t.get('lemma','');sense=t.get('intended_sense','');pos=t.get('part_of_speech','')
                if tid in seen_ids:add(hard,'new_target_id_reused',level=level,passage_id=pid,target_id=tid,first_passage=seen_ids[tid])
                else:seen_ids[tid]=pid
                m=ID_RE.match(tid)
                if m:
                    ranked_count+=1;rank=int(m.group(1));level_summary[level]['ranked_targets']+=1
                    if t.get('source_rank')!=rank:add(hard,'source_rank_mismatch',level=level,passage_id=pid,target_id=tid,id_rank=rank,source_rank=t.get('source_rank'))
                    src=sources.get(rank)
                    if src is None:add(hard,'rank_missing_from_canonical_decks',level=level,passage_id=pid,target_id=tid,rank=rank);continue
                    expected_file='arabic_top1000.csv' if rank<=1000 else 'arabic_top3000.csv'
                    if t.get('source_lexicon')!=expected_file:add(hard,'source_lexicon_mismatch',level=level,passage_id=pid,target_id=tid,expected=expected_file,actual=t.get('source_lexicon'))
                    sf=norm(src['front']);nf=norm(form);nl=norm(lemma)
                    if sf not in {nf,nl}:
                        add(hard,'source_surface_or_lemma_mismatch',level=level,passage_id=pid,target_id=tid,source_front=src['front'],form=form,lemma=lemma,source_rank=rank)
                    sp=pos_classes(src['source_pos']);tp=pos_classes(pos)
                    if not sp:
                        add(warnings,'canonical_source_pos_unparsed',level=level,passage_id=pid,target_id=tid,source_pos=src['source_pos'])
                    elif not tp:
                        add(warnings,'reader_target_pos_unparsed',level=level,passage_id=pid,target_id=tid,target_pos=pos,source_pos=src['source_pos'])
                    elif not (sp&tp):
                        add(hard,'part_of_speech_incompatible_with_source',level=level,passage_id=pid,target_id=tid,form=form,lemma=lemma,target_pos=pos,target_pos_classes=sorted(tp),source_pos=src['source_pos'],source_pos_classes=sorted(sp),source_meaning=src['source_meaning'])
                else:
                    level_summary[level]['non_ranked_targets']+=1
                    if not t.get('beyond_base'):add(hard,'non_rank_id_not_marked_beyond_base',level=level,passage_id=pid,target_id=tid)
                if not str(sense).strip():add(hard,'missing_intended_sense',level=level,passage_id=pid,target_id=tid)
                if not str(pos).strip():add(hard,'missing_part_of_speech',level=level,passage_id=pid,target_id=tid)
                if t.get('first_introduced') is not True:add(warnings,'new_target_not_marked_first_introduced_true',level=level,passage_id=pid,target_id=tid,value=t.get('first_introduced'))
                surfaces[norm(form)].append({'target_id':tid,'passage_id':pid,'level':level,'form':form,'lemma':lemma,'intended_sense':sense,'part_of_speech':pos,'source_rank':t.get('source_rank')})
    multi={k:v for k,v in surfaces.items() if k and len({x['target_id'] for x in v})>1}
    for surface,entries in sorted(multi.items()):
        add(warnings,'normalized_surface_has_multiple_ranked_identities',normalized_surface=surface,entries=entries,same_part_of_speech=len({str(x['part_of_speech']) for x in entries})==1,same_intended_sense_text=len({str(x['intended_sense']) for x in entries})==1)
    payload={'pass':6,'name':'lexical_source_identity_and_homograph_precision','scope':'Arabic A1-C2 deliberate new lexical targets','method':'canonical ranked-CSV rank/source/surface-or-lemma/POS identity checks plus multiple-ID normalized-surface diagnostics','not_claimed':['full semantic equivalence of English glosses','CEFR placement'],'levels':{k:dict(v) for k,v in level_summary.items()},'totals':{'new_targets':new_count,'ranked_targets':ranked_count,'unique_new_target_ids':len(seen_ids),'hard_issues':len(hard),'warnings':len(warnings),'multi_id_normalized_surfaces':len(multi)},'hard_issues':hard,'warnings':warnings,'status':'PASS' if not hard else 'FAIL'}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload['totals'],ensure_ascii=False));print('status='+payload['status'])
    if hard:raise SystemExit(1)
if __name__=='__main__':main()
