#!/usr/bin/env python3
"""Final Arabic review pass 08: cross-passage continuity, duplicates, and balance.

Exact duplicate texts are hard defects. Near-duplicate text, repeated titles, and
concentrated topic/genre patterns are review diagnostics rather than automatic
failures because deliberate recycling is part of the curriculum.
"""
from __future__ import annotations
import json,re,unicodedata
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass08_continuity_duplicate_balance.json'
DIAC=re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
WORD=re.compile(r'[\u0621-\u064A]{2,}')
STOP={'هذا','هذه','ذلك','تلك','الذي','التي','من','في','على','إلى','عن','مع','أن','إن','كان','كانت','هو','هي','ثم','لكن','لأن','بعد','قبل','كل','وقد','كما','عندما','إذا','ما','لم','لا','أو','حتى'}
def norm(s):
 s=unicodedata.normalize('NFKC',str(s or '')).replace('ـ','').replace('ٱ','ا');s=DIAC.sub('',s);return ' '.join(s.split())
def toks(s):return {w for w in WORD.findall(norm(s)) if w not in STOP}
def jacc(a,b):return len(a&b)/len(a|b) if a|b else 0.0

def main():
 rows=[]
 for level in LEVELS:
  p=ROOT/f'reading/arabic/{level}/passages.jsonl'
  for line in p.read_text(encoding='utf-8').splitlines():
   if line.strip():
    r=json.loads(line);r['_level']=level;r['_norm_text']=norm(r.get('text',''));r['_tokens']=toks(r.get('text',''));rows.append(r)
 hard=[];flags=[]
 text_groups=defaultdict(list);title_groups=defaultdict(list)
 for r in rows:
  text_groups[r['_norm_text']].append(r['id']);title_groups[norm(r.get('title',''))].append(r['id'])
 for text,ids in text_groups.items():
  if text and len(ids)>1:hard.append({'code':'exact_duplicate_passage_text','passage_ids':ids})
 for title,ids in title_groups.items():
  if title and len(ids)>1:flags.append({'code':'repeated_title','title':title,'passage_ids':ids})
 # Compare only pairs with roughly compatible lengths to reduce noisy overlap flags.
 near=[]
 for a,b in combinations(rows,2):
  la=len(a['_tokens']);lb=len(b['_tokens'])
  if min(la,lb)<20:continue
  ratio=min(la,lb)/max(la,lb)
  if ratio<0.65:continue
  score=jacc(a['_tokens'],b['_tokens'])
  if score>=0.72:
   near.append({'passage_a':a['id'],'passage_b':b['id'],'levels':[a['_level'],b['_level']],'token_jaccard':round(score,3),'length_ratio':round(ratio,3),'same_unit':a['_level']==b['_level'] and a.get('unit')==b.get('unit')})
 flags.extend({'code':'near_duplicate_passage_text',**x} for x in near)
 level_summary={}
 for level in LEVELS:
  rs=[r for r in rows if r['_level']==level];genres=Counter(str(r.get('genre','')) for r in rs);topics=Counter(t for r in rs for t in r.get('topics',[]) if t)
  top_genre=genres.most_common(1)[0] if genres else ('',0);top_topic=topics.most_common(1)[0] if topics else ('',0)
  level_summary[level]={'passages':len(rs),'unique_genres':len(genres),'unique_topics':len(topics),'top_genres':genres.most_common(10),'top_topics':topics.most_common(15),'dominant_genre_share':round(top_genre[1]/len(rs),3) if rs else 0,'dominant_topic_share':round(top_topic[1]/len(rs),3) if rs else 0}
  if rs and top_genre[1]/len(rs)>0.50:flags.append({'code':'genre_concentration','level':level,'genre':top_genre[0],'share':round(top_genre[1]/len(rs),3)})
  if rs and top_topic[1]/len(rs)>0.60:flags.append({'code':'topic_concentration','level':level,'topic':top_topic[0],'share':round(top_topic[1]/len(rs),3)})
 payload={'pass':8,'name':'cross_passage_continuity_duplicate_topic_genre_balance','scope':'Arabic A1-C2 canonical reading corpus','method':'exact normalized-text duplicate detection, conservative token-set near-duplicate screening, and per-level topic/genre concentration diagnostics','not_claimed':['semantic redundancy from lexical overlap alone','pedagogical harm from deliberate recycling'],'levels':level_summary,'totals':{'passages':len(rows),'hard_issues':len(hard),'review_flags':len(flags),'near_duplicate_pairs':len(near)},'hard_issues':hard,'flags':flags,'status':'FAIL' if hard else ('REVIEW_REQUIRED' if flags else 'PASS')}
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload['totals'],ensure_ascii=False));print('status='+payload['status'])
 if hard:raise SystemExit(1)
if __name__=='__main__':main()
