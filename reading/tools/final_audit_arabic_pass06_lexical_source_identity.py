#!/usr/bin/env python3
"""Final Arabic review pass 06: lexical source identity and homograph diagnostics."""
from __future__ import annotations
import csv,io,json,re,unicodedata
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass06_lexical_source_identity.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
RANK_RE=re.compile(r'\bRank:\s*(\d+)')
ID_RE=re.compile(r'^ar-r(\d+)$')
def norm(s):
    s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا')
    s=DIAC.sub('',s)
    return ''.join(s.split())
def read_ranked(name):
    idx={}
    with (ROOT/name).open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            m=RANK_RE.search(row.get('Back','') or '')
            if not m: continue
            rank=int(m.group(1)); idx[rank]={'front':row.get('Front',''),'back':row.get('Back',''),'source_file':name}
    return idx

def add(bucket,code,**kw):bucket.append({'code':code,**kw})
def main():
    sources={**read_ranked('arabic_top1000.csv'),**read_ranked('arabic_top3000.csv')}
    assert len(sources)==3000,len(sources)
    hard=[];warnings=[];surfaces=defaultdict(list);new_count=0;ranked_count=0
    level_summary={level:Counter() for level in LEVELS}
    seen_ids={}
    for level in LEVELS:
        p=ROOT/f'reading/arabic/{level}/passages.jsonl'
        for line in p.read_text(encoding='utf-8').splitlines():
            if not line.strip():continue
            r=json.loads(line);pid=r['id']
            for t in r.get('new_lexical_targets',[]):
                if not isinstance(t,dict):continue
                new_count+=1;level_summary[level]['new_targets']+=1
                tid=str(t.get('id',''));form=t.get('form','');lemma=t.get('lemma','');sense=t.get('intended_sense','');pos=t.get('part_of_speech','')
                if tid in seen_ids:
                    add(hard,'new_target_id_reused',level=level,passage_id=pid,target_id=tid,first_passage=seen_ids[tid])
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
                        add(warnings,'target_form_lemma_not_exactly_source_front',level=level,passage_id=pid,target_id=tid,source_front=src['front'],form=form,lemma=lemma,source_rank=rank)
                else:
                    level_summary[level]['non_ranked_targets']+=1
                    if not t.get('beyond_base'):
                        add(warnings,'non_rank_id_not_marked_beyond_base',level=level,passage_id=pid,target_id=tid)
                if not str(sense).strip():add(hard,'missing_intended_sense',level=level,passage_id=pid,target_id=tid)
                if not str(pos).strip():add(hard,'missing_part_of_speech',level=level,passage_id=pid,target_id=tid)
                if t.get('first_introduced') is not True:add(warnings,'new_target_not_marked_first_introduced_true',level=level,passage_id=pid,target_id=tid,value=t.get('first_introduced'))
                surfaces[norm(form)].append({'target_id':tid,'passage_id':pid,'level':level,'form':form,'lemma':lemma,'intended_sense':sense,'part_of_speech':pos,'source_rank':t.get('source_rank')})
    multi={k:v for k,v in surfaces.items() if k and len({x['target_id'] for x in v})>1}
    for surface,entries in sorted(multi.items()):
        same_pos=len({str(x['part_of_speech']) for x in entries})==1
        same_sense=len({str(x['intended_sense']) for x in entries})==1
        add(warnings,'normalized_surface_has_multiple_ranked_identities',normalized_surface=surface,entries=entries,same_part_of_speech=same_pos,same_intended_sense_text=same_sense)
    payload={'pass':6,'name':'lexical_source_identity_and_homograph_precision','scope':'Arabic A1-C2 deliberate new lexical targets','method':'canonical ranked-CSV rank/source/form identity checks plus multiple-ID normalized-surface diagnostics','levels':{k:dict(v) for k,v in level_summary.items()},'totals':{'new_targets':new_count,'ranked_targets':ranked_count,'unique_new_target_ids':len(seen_ids),'hard_issues':len(hard),'warnings':len(warnings),'multi_id_normalized_surfaces':len(multi)},'hard_issues':hard,'warnings':warnings,'status':'PASS' if not hard else 'FAIL'}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(payload['totals'],ensure_ascii=False));print('status='+payload['status'])
    if hard:raise SystemExit(1)
if __name__=='__main__':main()
