#!/usr/bin/env python3
"""Advance durable project state to B2 Unit09 from the exact Unit08 lock."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit08_frontier_lock.json';STATUS=R/'reading/STATUS.json';TASKS=R/'reading/TASKS.md';HANDOFF=R/'reading/AGENT_HANDOFF.md'
THEME='public policy and trade-offs';GENRES='briefing / argument / counterargument'
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=48 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit08 lock/live B2 mismatch')
 targets=lock.get('unit08_target_forms',[]);groups=lock.get('unit08_target_groups',{})
 if len(targets)!=20 or len(set(targets))!=20 or any(len(groups.get(k,[]))!=4 for k in ['p01','p02','p03','p04','p05']):raise AssertionError('Unit08 lock target metadata drift')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=48 or rows[-1]['id']!='fr-b2-u08-p06':raise AssertionError('unexpected B2 Unit08 frontier')
 s=json.loads(STATUS.read_text(encoding='utf-8'));b=s['french']['b2_generation']
 if b.get('last_sequence')!=42:raise AssertionError(f"STATUS not at expected pre-Unit08 sync frontier: {b.get('last_sequence')}")
 s['updated']='2026-08-17';s['phase']='Arabic A1-C2 is formally approved. French A1, A2, and B1 are generated and generation-integrity PASS. French B2 Units 01-08 are canonical; Unit 09 / sequences 49-54 is next.'
 fr=s['french'];fr['canonical_passages']=228;fr['questions']=2280;fr['answers']=2280;fr['levels']['b2']=48
 b['passages']=48;b['questions']=480;b['answers']=480;b['completed_units']=[1,2,3,4,5,6,7,8];b['last_sequence']=48;b['canonical_blob']=blob;b['unit08_theme']='history and explanation';b['unit08_targets']=targets;b['unit08_target_groups']=groups;b['unit08_word_counts']=lock['unit08_word_counts'];b['unit08_frontier_lock']='reading/audit/french_b2_unit08_frontier_lock.json'
 fr['next_target']=f'Generate French B2 Unit 09 / sequences 49-54 against B2 blob {blob}. Canonical topic-matrix theme: {THEME}; genres: {GENRES}. Use accepted default 4 fresh targets per P01-P05, P06 zero new, 350-550 words, 10 Q/A, policy goals, stakeholder trade-offs, distributional effects, implementation constraints, counterargument, rebuttal, author position and synthesis, exact reviews, and freshness checks against all prior French targets.'
 s['next_actions']=['keep Arabic sealed unless canonical Arabic changes','do not broadly regenerate French A1/A2/B1','generate French B2 Unit09 against the locked Unit08 blob and canonical topic matrix','continue French generation-first through B2-C2 before final French multi-pass audit','keep Urdu unchanged while French is active unless explicitly reprioritized']
 if 'reading/audit/french_b2_unit08_frontier_lock.json' not in s['important_files']:s['important_files'].append('reading/audit/french_b2_unit08_frontier_lock.json')
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 t=TASKS.read_text(encoding='utf-8');anchor='#### Unit 08 — IMMEDIATE NEXT'
 if anchor not in t:raise AssertionError('TASKS Unit08 frontier anchor missing')
 start=t.index(anchor);end=t.index('\n## Urdu — QUEUED',start)
 target_line='`, `'.join(targets)
 block=f'''#### Unit 08 — COMPLETE\n- [x] Sequences 43–48 canonical.\n- [x] 6 passages / 60 Q / 60 A.\n- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.\n- [x] Theme: `history and explanation`; genres: historical account / causal analysis / source comparison.\n- [x] Canonical B2 blob after Unit08: `{blob}`.\n- [x] Frontier lock `reading/audit/french_b2_unit08_frontier_lock.json` = PASS.\n\nUnit 08 targets: `{target_line}`.\n\n#### Unit 09 — IMMEDIATE NEXT\nCanonical topic-matrix theme: **{THEME}**. Genres: **{GENRES}**.\n\n- [ ] Generate sequences 49–54 against locked B2 blob `{blob}`.\n- [ ] Accepted default 4 fresh targets per P01–P05; P06 zero new.\n- [ ] Check every candidate against all prior deliberate French A1–B2 targets.\n- [ ] Preserve 350–550 words, 10 linked Q/A, source identity, exact reviews and local target declarations.\n- [ ] Require policy goals, stakeholder trade-offs, distributional effects, implementation constraints, counterargument/rebuttal, author position and synthesis.\n- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.\n\nRemaining after Unit08:\n- [ ] B2: 12 passages.\n- [ ] C1: 60 passages.\n- [ ] C2: 60 passages.\n'''
 t=t[:start]+block+t[end:]
 old='**Generate French B2 Unit 08 / sequences 43–48 for `history and explanation` against blob `5ff899452326f679b7c16b0ff33d8f38fa99719a`. Keep Arabic sealed.**';new=f'**Generate French B2 Unit 09 / sequences 49–54 for `{THEME}` against blob `{blob}`. Keep Arabic sealed.**'
 if old not in t:raise AssertionError('TASKS active-next anchor drift')
 TASKS.write_text(t.replace(old,new),encoding='utf-8')
 h=HANDOFF.read_text(encoding='utf-8');anchor='## 12. IMMEDIATE FRONTIER — B2 Unit 08'
 if anchor not in h:raise AssertionError('HANDOFF Unit08 frontier anchor missing')
 start=h.index(anchor);end=h.index('\n## 13. Urdu — QUEUED',start)
 block=f'''## 12. B2 Unit 08 — COMPLETE / CURRENT LOCK\n\nTheme: **history and explanation**. Genres: historical account / causal analysis / source comparison. Sequences 43–48.\n\n- 6 passages / 60 questions / 60 answers;\n- 20 fresh targets, four in P01–P05; P06 zero new;\n- canonical B2 blob `{blob}`;\n- frontier lock `reading/audit/french_b2_unit08_frontier_lock.json` = PASS;\n- Unit08 targets: `{target_line}`.\n\n## 13. IMMEDIATE FRONTIER — B2 Unit 09\n\nCanonical theme: **{THEME}**. Genres: **{GENRES}**. Generate sequences **49–54** against exact blob `{blob}`. Require the Unit08 lock; use four fresh targets by default in P01–P05 and zero new in P06; preserve source freshness/rank identity, exact reviews, 350–550 words, 10 linked Q/A, and B2 reasoning about policy goals, stakeholder trade-offs, distributional effects, implementation constraints, counterargument/rebuttal, position and synthesis. Fail closed and repair rather than weakening guards.\n'''
 h=h[:start]+block+h[end:];h=h.replace('\n## 13. Urdu — QUEUED','\n## 14. Urdu — QUEUED').replace('\n## 14. Throughput / parallel rules','\n## 15. Throughput / parallel rules').replace('\n## 15. Core non-negotiables','\n## 16. Core non-negotiables')
 HANDOFF.write_text(h,encoding='utf-8')
 print(json.dumps({'status':'PASS','b2_blob':blob,'b2_passages':48,'next':'B2 Unit09','theme':THEME,'targets':targets},ensure_ascii=False))
if __name__=='__main__':main()
