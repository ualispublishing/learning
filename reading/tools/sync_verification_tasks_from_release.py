#!/usr/bin/env python3
"""Keep the concise Arabic verification summary aligned with RELEASE_STATUS evidence."""
from __future__ import annotations
import re
from datetime import date
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; RELEASE=READING/'RELEASE_STATUS.json'; TASKS=READING/'VERIFICATION_TASKS.md'
def sub_once(text:str,pattern:str,replacement:str,label:str)->str:
 out,n=re.subn(pattern,replacement,text,count=1,flags=re.MULTILINE)
 if n!=1: raise SystemExit(f'{label}: expected exactly one match, found {n}')
 return out
def main():
 release=json.loads(RELEASE.read_text(encoding='utf-8')); arabic=release.get('languages',{}).get('arabic',{}); gate=arabic.get('latest_deterministic_gate',{})
 status=gate.get('status'); findings=gate.get('open_findings')
 if status!='FAIL' or not isinstance(findings,int) or findings<0: raise SystemExit('unexpected Arabic deterministic gate state')
 if arabic.get('educator_release_ready') is not False: raise SystemExit('refusing verification sync while Arabic educator_release_ready is not false')
 text=TASKS.read_text(encoding='utf-8')
 text=sub_once(text,r'^Updated: \d{4}-\d{2}-\d{2}$',f'Updated: {date.today().isoformat()}','updated date')
 text=sub_once(text,r'Current release position: fresh deterministic revalidation is \*\*FAIL\*\* with \*\*[0-9,]+\*\* open evidence findings;',f'Current release position: fresh deterministic revalidation is **FAIL** with **{findings}** open evidence findings;','current release position')
 text=sub_once(text,r'(Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30\.json` — 360 records, 3,600 questions, 3,600 answers; status \*\*FAIL\*\*; open findings )\*\*[0-9,]+\*\*\.',rf'\g<1>**{findings}**.','fresh evidence summary')
 TASKS.write_text(text,encoding='utf-8')
 print(json.dumps({'verification_tasks_synced':True,'arabic_status':status,'arabic_open_findings':findings,'educator_release_ready':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
