#!/usr/bin/env python3
"""Keep the Arabic global release-blocker summary aligned with authoritative gate evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/RELEASE_STATUS.json'
PREFIX='Arabic fresh deterministic release revalidation remains '

def main():
 release=json.loads(PATH.read_text(encoding='utf-8'))
 arabic=release.get('languages',{}).get('arabic',{})
 gate=arabic.get('latest_deterministic_gate',{})
 status=gate.get('status'); findings=gate.get('open_findings')
 if not isinstance(status,str) or not isinstance(findings,int):
  raise SystemExit('Arabic latest deterministic gate is incomplete')
 if arabic.get('educator_release_ready') is not False:
  raise SystemExit('refusing blocker sync while educator_release_ready is not false')
 blockers=release.get('global_release_blockers')
 if not isinstance(blockers,list): raise SystemExit('global_release_blockers is not a list')
 matches=[i for i,b in enumerate(blockers) if isinstance(b,str) and b.startswith(PREFIX)]
 if len(matches)!=1: raise SystemExit(f'expected exactly one Arabic global blocker, found {len(matches)}')
 i=matches[0]; current=blockers[i]
 suffix=''
 if ';' in current: suffix=';'+current.split(';',1)[1]
 blockers[i]=f'{PREFIX}{status} with {findings} open release-evidence findings{suffix}'
 release['updated']='2026-08-31'
 PATH.write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'arabic_status':status,'arabic_open_findings':findings,'global_blocker_synced':True,'educator_release_ready':False},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
