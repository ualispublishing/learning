#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/audit/arabic_b1_c2_lexical_diagnostic_adjudication_2026-08-23.json'
OUT=ROOT/'reading/audit/arabic_b1_c2_lexical_remainder_summary_2026-08-23.md'
LEVELS=('b1','b2','c1','c2')
def load(l):return [json.loads(x) for x in (ROOT/f'reading/arabic/{l}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 d=json.loads(SRC.read_text(encoding='utf-8'));idx={l:{r['id']:r for r in load(l)} for l in LEVELS};false=[];new=[]
 for x in d.get('unresolved',[]):
  dec=x.get('decision');diag=x.get('diagnostic',{});pid=diag.get('passage_id');level=pid.split('-')[1];row=idx[level][pid];tid=diag.get('target_id');refs=[q.get('id') for q in row.get('questions',[]) if tid in (q.get('target_ids') or [])]
  item={'decision':dec,'passage_id':pid,'target_id':tid,'form':diag.get('form'),'question_refs':refs,'text':row.get('text'),'target_metadata':x.get('target_metadata'),'supported_hits':x.get('supported_hits')}
  if dec=='UNRESOLVED_FALSE_RUNNING_TEXT_REVIEW':false.append(item)
  else:new.append(item)
 linked=[x for x in false if x['question_refs']];unlinked=[x for x in false if not x['question_refs']]
 lines=['# Arabic B1-C2 lexical remainder','',f"False `running_text` review declarations: **{len(false)}** — question-linked: **{len(linked)}**, unlinked: **{len(unlinked)}**",f"Unresolved new-target diagnostics: **{len(new)}**",'','## New-target diagnostics']
 for x in new:
  lines += ['',f"### {x['passage_id']} · {x['target_id']} · {x['form']}",f"Decision: `{x['decision']}`",f"Target metadata: `{json.dumps(x['target_metadata'],ensure_ascii=False)}`",f"Supported hits: `{json.dumps(x['supported_hits'],ensure_ascii=False)}`",'',x['text']]
 lines += ['','## Question-linked false running-text reviews','', '| Passage | Target | Form | Question refs |','|---|---|---|---|']
 for x in linked:lines.append(f"| {x['passage_id']} | {x['target_id']} | {x['form']} | {', '.join(x['question_refs'])} |")
 lines += ['','## Unlinked false running-text reviews','', '| Passage | Target | Form |','|---|---|---|']
 for x in unlinked:lines.append(f"| {x['passage_id']} | {x['target_id']} | {x['form']} |")
 OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps({'false_running_text':len(false),'question_linked':len(linked),'unlinked':len(unlinked),'new_target':len(new)},ensure_ascii=False))
if __name__=='__main__':main()
