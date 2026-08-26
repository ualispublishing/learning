#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/audit/arabic_a1_a2_remaining_23_2026-08-23.json'
OUT=ROOT/'reading/audit/arabic_a1_a2_remaining_23_summary_2026-08-23.md'
def main():
 d=json.loads(SRC.read_text(encoding='utf-8'))
 lines=['# Arabic A1/A2 remaining 23 — concise review sheet','', '| # | kind | passage | target | lemma | declared | supported | surface hits |','|---:|---|---|---|---|---:|---:|---|']
 for it in d['items']:
  b=it['source_blocker'];tr=it.get('target_record') or {};hits=b.get('hits') or []
  toks=[]
  for h in hits:
   tok=h.get('token','')
   if tok not in toks:toks.append(tok)
  lines.append(f"| {it['blocker_id']} | {it['kind']} | {it['passage_id']} | {tr.get('form','')} | {tr.get('lemma','')} | {b.get('declared','')} | {b.get('supported_count','')} | {'، '.join(toks)} |")
 OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print('\n'.join(lines))
if __name__=='__main__':main()
