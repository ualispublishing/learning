#!/usr/bin/env python3
"""Advance durable state to B2 Unit04 only from the exact Unit03 lock."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
B2=REPO/'reading/french/b2/passages.jsonl'; LOCK=REPO/'reading/audit/french_b2_unit03_frontier_lock.json'; STATUS=REPO/'reading/STATUS.json'; TASKS=REPO/'reading/TASKS.md'; HANDOFF=REPO/'reading/AGENT_HANDOFF.md'
U3=['juste','chance','groupe','réussir','permettre','refuser','accord','obliger','vérité','vrai','faux','mentir','victime','dommage','aider','difficile','garder','donner','loi','guerre']
NEXT_THEME='cities and design'; NEXT_GENRES='report / proposal / critique'

def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'))
 current=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=18 or current!=lock.get('canonical_blob'): raise AssertionError('Unit03 lock does not match live B2')
 if sorted(lock.get('unit03_target_forms',[]))!=sorted(U3): raise AssertionError('Unit03 target lock drift')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=18 or rows[-1]['id']!='fr-b2-u03-p06': raise AssertionError('unexpected B2 Unit03 frontier')
 wc=[r['word_count'] for r in rows[12:18]]
 s=json.loads(STATUS.read_text(encoding='utf-8'))
 if s['french']['b2_generation'].get('last_sequence')!=12: raise AssertionError('STATUS not at expected pre-sync frontier')
 s['updated']='2026-08-17'
 s['phase']='Arabic A1-C2 is formally approved. French A1, A2, and B1 are generated and generation-integrity PASS. French B2 Units 01-03 are canonical; Unit 04 / sequences 19-24 is next.'
 fr=s['french'];fr['canonical_passages']=198;fr['questions']=1980;fr['answers']=1980;fr['levels']['b2']=18
 b=fr['b2_generation'];b['passages']=18;b['questions']=180;b['answers']=180;b['completed_units']=[1,2,3];b['last_sequence']=18;b['canonical_blob']=current;b['unit03_theme']='ethics and competing values';b['unit03_targets']=U3;b['unit03_word_counts']=wc;b['unit03_frontier_lock']='reading/audit/french_b2_unit03_frontier_lock.json'
 fr['next_target']=f'Generate French B2 Unit 04 / sequences 19-24 against B2 blob {current}. Canonical topic-matrix theme: {NEXT_THEME}; genres: {NEXT_GENRES}. Use accepted default 4 fresh targets per P01-P05, P06 zero new, 350-550 words, 10 Q/A, report/proposal/critique reasoning, design trade-offs, stakeholder impacts, counterargument, author position and synthesis, exact reviews, and freshness checks against all prior French targets.'
 s['next_actions']=['keep Arabic sealed unless canonical Arabic changes','do not broadly regenerate French A1/A2/B1','generate French B2 Unit04 against the locked Unit03 blob and canonical topic matrix','continue French generation-first through B2-C2 before final French multi-pass audit','keep Urdu unchanged while French is active unless explicitly reprioritized']
 if 'reading/audit/french_b2_unit03_frontier_lock.json' not in s['important_files']:s['important_files'].append('reading/audit/french_b2_unit03_frontier_lock.json')
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

 t=TASKS.read_text(encoding='utf-8');start=t.index('#### Unit 03 — IMMEDIATE NEXT');end=t.index('\n## Urdu — QUEUED',start)
 block=f'''#### Unit 03 — COMPLETE\n- [x] Sequences 13–18 canonical.\n- [x] 6 passages / 60 Q / 60 A.\n- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.\n- [x] Theme: `ethics and competing values`; genres: argument / case / response.\n- [x] Canonical B2 blob after Unit03: `{current}`.\n- [x] Frontier lock `reading/audit/french_b2_unit03_frontier_lock.json` = PASS.\n\nUnit 03 targets: `'''+'`, `'.join(U3)+f'''`.\n\n#### Unit 04 — IMMEDIATE NEXT\nCanonical topic-matrix theme: **{NEXT_THEME}**. Genres: **{NEXT_GENRES}**.\n\n- [ ] Generate sequences 19–24 against locked B2 blob `{current}`.\n- [ ] Use accepted default 4 fresh targets per P01–P05; P06 zero new.\n- [ ] Check candidates against every deliberate French target across A1–B2 Unit03.\n- [ ] Keep 350–550 words, 10 linked Q/A, exact reviews, source rank/ID identity and local target declarations.\n- [ ] Require urban-design trade-offs, stakeholder impacts, evidence/assumptions, counterargument, author position, critique and synthesis.\n- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.\n\nRemaining after Unit03:\n- [ ] B2: 42 passages.\n- [ ] C1: 60 passages.\n- [ ] C2: 60 passages.\n'''
 t=t[:start]+block+t[end:]
 old='**Generate French B2 Unit 03 / sequences 13–18 for `ethics and competing values` against blob `ff94113359f90b68032b2e2f92aaa1bf2b3ea923`. Keep Arabic sealed.**'
 new=f'**Generate French B2 Unit 04 / sequences 19–24 for `{NEXT_THEME}` against blob `{current}`. Keep Arabic sealed.**'
 if old not in t: raise AssertionError('TASKS immediate-next anchor drift')
 TASKS.write_text(t.replace(old,new),encoding='utf-8')

 h=HANDOFF.read_text(encoding='utf-8');start=h.index('## 7. IMMEDIATE FRONTIER — B2 Unit 03');end=h.index('\n## 8. Urdu — QUEUED',start)
 block=f'''## 7. B2 Unit 03 — COMPLETE / CURRENT LOCK\n\nTheme: **ethics and competing values**. Genres: argument / case / response. Sequences 13–18.\n\n- 6 passages / 60 questions / 60 answers;\n- 20 fresh deliberate targets, four in P01–P05; P06 zero new;\n- canonical B2 blob after Unit03: `{current}`;\n- frontier lock: `reading/audit/french_b2_unit03_frontier_lock.json` = PASS;\n- Unit03 targets: `'''+'`, `'.join(U3)+f'''`.\n\n## 8. IMMEDIATE FRONTIER — B2 Unit 04\n\nCanonical topic-matrix theme: **{NEXT_THEME}**. Genres: **{NEXT_GENRES}**.\n\nGenerate sequences **19–24** against exact B2 blob `{current}`. Require the Unit03 lock before target selection or append; use the accepted four-target default in P01–P05 and zero new in P06; preserve source freshness/rank identity, exact reviews, 350–550 words, 10 linked Q/A, and B2 report/proposal/critique reasoning with urban-design trade-offs, stakeholders, assumptions, counterargument, position and synthesis. Fail closed and repair rather than weaken guards.\n'''
 h=h[:start]+block+h[end:]
 h=h.replace('\n## 8. Urdu — QUEUED','\n## 9. Urdu — QUEUED').replace('\n## 9. Throughput / parallel rules','\n## 10. Throughput / parallel rules').replace('\n## 10. Core non-negotiables','\n## 11. Core non-negotiables')
 HANDOFF.write_text(h,encoding='utf-8')
 print(json.dumps({'status':'PASS','b2_blob':current,'b2_passages':18,'next':'B2 Unit04','theme':NEXT_THEME,'word_counts':wc},ensure_ascii=False))
if __name__=='__main__':main()
