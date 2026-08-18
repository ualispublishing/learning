#!/usr/bin/env python3
"""Resolve exact canonical French C2 plan node for C2_UNIT=2..10 from the sealed previous frontier."""
from __future__ import annotations
import json,os,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';STD=R/'docs/READING_PASSAGE_STANDARD.md';MATRIX=R/'reading/planning/topic_genre_matrix.json';AUD=R/'reading/audit'
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def main():
 u=int(os.environ.get('C2_UNIT','0'))
 if not 2<=u<=10:raise AssertionError('C2_UNIT must be 2..10')
 prev=u-1;lock=json.loads((AUD/f'french_c2_unit{prev:02d}_frontier_lock.json').read_text());rows=[json.loads(x) for x in C2.read_text().splitlines() if x.strip()];c2=h(C2);c1=h(C1)
 if len(rows)!=(prev*6) or rows[-1]['sequence']!=prev*6 or lock.get('status')!='PASS' or lock.get('last_sequence')!=prev*6 or lock.get('c2_canonical_blob')!=c2 or lock.get('c1_canonical_blob')!=c1:raise AssertionError(f'C2 Unit{prev:02d} lock/live mismatch')
 text=STD.read_text();m=re.search(r'\|\s*C2\s*\|\s*([\d,]+)\s*[–-]\s*([\d,]+)\s*\|',text);lex=re.search(r'C2:\s*(\d+)\s*[–-]\s*(\d+)',text)
 if not m or not lex:raise AssertionError('cannot resolve C2 durable standard')
 lo,hi=[int(x.replace(',','')) for x in m.groups()];lexband=list(map(int,lex.groups()));nodes=json.loads(MATRIX.read_text()).get('levels',{}).get('C2',[]);matches=[(i,x) for i,x in enumerate(nodes) if isinstance(x,dict) and int(x.get('unit',-1))==u]
 if len(matches)!=1:raise AssertionError(f'expected one levels.C2 Unit{u:02d} node, found {len(matches)}')
 idx,node=matches[0];out={'status':'PASS','scope':f'French C2 Unit{u:02d} canonical planning resolution','c1_canonical_blob':c1,'c2_source_blob':c2,'previous_frontier_lock':f'reading/audit/french_c2_unit{prev:02d}_frontier_lock.json','c2_word_min':lo,'c2_word_max':hi,'c2_lexical_planning_band':lexband,'lexical_band_is_maximum_not_quota':True,'accepted_c2_default_new_targets_per_standard_passage':lock.get('accepted_c2_default_new_targets_per_standard_passage',5),'accepted_default_is_hard_quota':False,'matrix_path':f'$.levels.C2[{idx}]','theme':node.get('theme'),'genres':node.get('genres'),'canonical_node':node}
 if not out['theme'] or not out['genres']:raise AssertionError('C2 plan node incomplete')
 (AUD/f'french_c2_unit{u:02d}_plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','unit':u,'theme':out['theme'],'genres':out['genres']},ensure_ascii=False))
if __name__=='__main__':main()
