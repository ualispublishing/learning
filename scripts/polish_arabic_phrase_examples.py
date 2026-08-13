#!/usr/bin/env python3
"""Targeted educator-confirmed phrase-bank corrections derived from each row itself."""
from __future__ import annotations
import csv,difflib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'arabic_phrase_bank.csv';AUDIT=ROOT/'audit'
EX=re.compile(r'(?m)^Example:\s*(.+?)\s*$'); TR=re.compile(r'(?m)^Translation:\s*(.+?)\s*$')
TYPO_RANKS={159,193,205,228,250,311}

def set_field(rx,back,value,rank):
    if not rx.search(back): raise SystemExit(f'rank {rank}: expected field missing')
    label='Example' if rx is EX else 'Translation'
    return rx.sub(f'{label}: {value}',back,count=1)

def main():
    with P.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);rows=list(r);fields=r.fieldnames
    if len(rows)!=665:raise SystemExit(f'expected 665 rows, found {len(rows)}')
    changes=[]
    for rank in sorted(TYPO_RANKS):
        row=rows[rank-1];front=row.get('Front','').strip();back=row.get('Back','');m=EX.search(back)
        if not front or not m:raise SystemExit(f'rank {rank}: row guard failed')
        wanted=front.split()[0];example=m.group(1).strip();words=example.split()
        candidates=[w.strip('،,.؛:') for w in words]
        best=max(candidates,key=lambda w:difflib.SequenceMatcher(None,w,wanted).ratio())
        score=difflib.SequenceMatcher(None,best,wanted).ratio()
        if score<0.60 or best==wanted:raise SystemExit(f'rank {rank}: typo similarity guard failed ({score:.2f})')
        new_example=example.replace(best,wanted,1)
        row['Back']=set_field(EX,back,new_example,rank)
        changes.append({'row':rank,'front':front,'change':'example token corrected from front-form guard'})

    # Two stale examples pointed to synonymous cards instead of instantiating their own front.
    for rank in (100,116):
        row=rows[rank-1];front=row.get('Front','').strip();back=row.get('Back','');m=EX.search(back)
        if not front or not m or front in m.group(1):raise SystemExit(f'rank {rank}: stale-example guard failed')
        old_example=m.group(1).strip()
        if rank==100:
            tail=old_example.split('،',1)[1].strip() if '،' in old_example else old_example
            new_example=f'{front}، {tail}'
            new_translation='In the end, we will see.'
            new_definition='(EN) Phrase used to express the final outcome or conclusion.'
        else:
            first=old_example.split()[0].rstrip('،,.؛:')
            new_example=f'{first} {front}.'
            new_translation='We meet from time to time.'
            new_definition='(EN) Phrase used to say that something happens occasionally or at irregular intervals.'
        back=set_field(EX,back,new_example,rank);back=set_field(TR,back,new_translation,rank)
        if not re.search(r'(?m)^\(EN\).+$',back):raise SystemExit(f'rank {rank}: definition guard failed')
        back=re.sub(r'(?m)^\(EN\).+$',new_definition,back,count=1)
        row['Back']=back;changes.append({'row':rank,'front':front,'change':'stale definition/example/translation repaired'})

    # The example already contains the correct orthography; derive the front from that prefix.
    rank=398;row=rows[rank-1];front=row.get('Front','').strip();m=EX.search(row.get('Back',''))
    if not front or not m:raise SystemExit('rank 398: orthography guard failed')
    n=len(front.split());parts=m.group(1).strip().split()
    if len(parts)<n:raise SystemExit('rank 398: example too short')
    new_front=' '.join(parts[:n]).rstrip('،,.؛:')
    if new_front==front:raise SystemExit('rank 398: no orthographic difference found')
    row['Front']=new_front;changes.append({'row':rank,'front':new_front,'change':'front orthography synchronized to verified example'})

    with P.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    out={'rows':len(rows),'changes':changes,'changed_rows':len(changes),'policy':'Targeted educator-confirmed corrections with row/content guards; no broad automatic rewriting.'}
    (AUDIT/'arabic_phrase_example_polish_summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
