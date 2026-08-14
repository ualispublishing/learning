#!/usr/bin/env python3
"""Final Arabic review pass 10: lexical intended-sense/register alignment.

Compares each deliberate ranked target's intended English sense with the cleared
canonical source meaning. Zero lexical overlap is a REVIEW flag, not automatic
semantic rejection, because legitimate synonyms/paraphrases exist. The artifact
is designed for targeted human-grade adjudication.
"""
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass10_lexical_sense_alignment.json'
RANK_RE=re.compile(r'\bRank:\s*(\d+)');MEAN_RE=re.compile(r'^Meaning:\s*(.+)$',re.M|re.I);POS_RE=re.compile(r'^Part of speech:\s*(.+)$',re.M|re.I)
WORD=re.compile(r'[A-Za-z]+')
STOP={'the','a','an','to','of','or','and','be','is','are','in','on','at','for','with','as','by','from','into','that','this','one','someone','something','etc','context','dependent'}
SYN_GROUPS=[
 {'show','display','demonstrate','manifest','reveal','indicate'},
 {'main','principal','primary','chief','major'},
 {'expect','anticipate','forecast','predict'},
 {'transport','transfer','move','movement','transmission'},
 {'event','activity','occasion'},
 {'effectiveness','efficiency','efficacy'},
 {'begin','start','commence'},
 {'end','finish','conclude'},
 {'help','assist','aid'},
 {'buy','purchase'}, {'job','work','employment'}, {'place','location','site'},
 {'answer','reply','response'}, {'result','outcome'}, {'reason','cause'},
 {'idea','concept','notion'}, {'change','modify','alter'}, {'important','significant'},
 {'big','large','great'}, {'small','little'}, {'fast','quick','rapid'}, {'slow','gradual'},
 {'possible','possible','potential'}, {'clear','obvious','evident'}, {'use','usage','utilize'},
]
SYN={w:g for g in SYN_GROUPS for w in g}
def stem(w):
 w=w.lower()
 for suf in ('ies','ing','ed','es','s'):
  if len(w)>len(suf)+3 and w.endswith(suf):w=w[:-len(suf)];break
 return w
def terms(s):return {stem(x) for x in WORD.findall(str(s or '')) if x.lower() not in STOP and len(x)>2}
def expanded(ts):
 out=set(ts)
 for t in list(ts):
  if t in SYN:out|={stem(x) for x in SYN[t]}
 return out
def read_sources():
 src={}
 for name in ('arabic_top1000.csv','arabic_top3000.csv'):
  with (ROOT/name).open(encoding='utf-8',newline='') as f:
   for row in csv.DictReader(f):
    back=row.get('Back','') or '';m=RANK_RE.search(back)
    if not m:continue
    rank=int(m.group(1));mm=MEAN_RE.search(back);pm=POS_RE.search(back)
    src[rank]={'front':row.get('Front',''),'meaning':mm.group(1).strip() if mm else '','pos':pm.group(1).strip() if pm else '','source_file':name}
 return src
def main():
 src=read_sources();assert len(src)==3000
 flags=[];summary={};checked=0
 for level in LEVELS:
  rows=[json.loads(x) for x in (ROOT/f'reading/arabic/{level}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
  c=Counter();flagged=set()
  for r in rows:
   for t in r.get('new_lexical_targets',[]):
    if not isinstance(t,dict) or not str(t.get('id','')).startswith('ar-r'):continue
    checked+=1;rank=int(str(t['id']).split('ar-r',1)[1]);s=src[rank];it=str(t.get('intended_sense',''))
    a=expanded(terms(it));b=expanded(terms(s['meaning']));overlap=sorted(a&b)
    if not overlap:
     flags.append({'code':'intended_sense_zero_keyword_overlap_with_source','level':level,'passage_id':r['id'],'target_id':t['id'],'form':t.get('form'),'lemma':t.get('lemma'),'target_pos':t.get('part_of_speech'),'intended_sense':it,'source_front':s['front'],'source_pos':s['pos'],'source_meaning':s['meaning'],'source_rank':rank,'source_file':s['source_file']});c['zero_overlap']+=1;flagged.add(r['id'])
  summary[level]={'passages':len(rows),'ranked_targets_checked':sum(1 for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict) and str(t.get('id','')).startswith('ar-r')),'flagged_passages':len(flagged),'zero_overlap_flags':c['zero_overlap']}
 payload={'pass':10,'name':'lexical_intended_sense_register_alignment','scope':'Arabic A1-C2 deliberate ranked lexical targets','method':'source-aware English intended-sense keyword/synonym overlap diagnostic against educator-cleared canonical source meanings','interpretation':'zero-overlap items require human/source adjudication; nonzero overlap is not by itself proof of semantic correctness','levels':summary,'totals':{'ranked_targets_checked':checked,'review_flags':len(flags)},'flags':flags,'status':'PASS' if not flags else 'REVIEW_REQUIRED'}
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload['totals'],ensure_ascii=False));print('status='+payload['status'])
if __name__=='__main__':main()
