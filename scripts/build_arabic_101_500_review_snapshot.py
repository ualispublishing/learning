#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'arabic_top1000.csv'
MODERN=ROOT/'audit/arabic_top1000_modern_sense_review.json'
OUT=ROOT/'audit/arabic_101_500_second_pass_snapshot.json'
PRIORITY=ROOT/'audit/arabic_101_500_priority_review.json'
SUMMARY=ROOT/'audit/arabic_101_500_second_pass_summary.json'
MEAN=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$')
POS=re.compile(r'(?m)^Part of speech:\s*(.+?)\s*$')
RANK=re.compile(r'(?m)^Rank:\s*(\d+)\s*$')

def grab(rx,s):
    m=rx.search(s or '')
    return m.group(1).strip() if m else ''

def main():
    with TARGET.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    modern=[]
    if MODERN.exists():
        modern=json.loads(MODERN.read_text(encoding='utf-8'))
    modern_by_rank={int(x['rank']):x for x in modern if str(x.get('rank','')).isdigit()}
    out=[]; priority=[]
    for i,row in enumerate(rows,1):
        if not 101 <= i <= 500: continue
        back=row.get('Back','')
        rank=int(grab(RANK,back) or i)
        meaning=grab(MEAN,back); pos=grab(POS,back)
        flags=[]
        if rank in modern_by_rank: flags.append('modern_corpus_review_signal')
        if 'depending on vocalization' in meaning.lower(): flags.append('undiacritized_homograph_attention')
        if meaning.count(';') >= 3: flags.append('broad_or_multi_sense_meaning')
        if pos.lower() in {'other function word','other','unknown'}: flags.append('vague_pos_label')
        if pos.count('/') >= 2: flags.append('multi_pos_attention')
        if any(x in meaning.lower() for x in ['archaic','obsolete','rare','dialect']): flags.append('register_attention')
        item={
          'rank':rank,'front':row.get('Front',''),'meaning':meaning,'part_of_speech':pos,
          'priority_flags':flags,
        }
        if rank in modern_by_rank:
            item['corpus_signal']=modern_by_rank[rank].get('corpus_signal','')
        out.append(item)
        if flags: priority.append(item)
    counts={}
    for x in priority:
        for f in x['priority_flags']: counts[f]=counts.get(f,0)+1
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    PRIORITY.write_text(json.dumps(priority,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={
      'scope':'arabic_top1000.csv ranks 101-500',
      'rows':len(out),'priority_rows':len(priority),'flag_counts':counts,
      'policy':'Priority flags are review signals, not automatic errors. Educator clearance requires adjudication of every priority row plus manual inspection of the full block.'
    }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
