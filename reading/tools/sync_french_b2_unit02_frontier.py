#!/usr/bin/env python3
"""Advance durable project state to B2 Unit03 only from the exact Unit02 lock."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
B2=REPO/'reading/french/b2/passages.jsonl';LOCK=REPO/'reading/audit/french_b2_unit02_frontier_lock.json';STATUS=REPO/'reading/STATUS.json';TASKS=REPO/'reading/TASKS.md';HANDOFF=REPO/'reading/AGENT_HANDOFF.md'
U2=['promettre','décider','attendre','confiance','grave','calmer','choisir','problème','maintenir','simplement','secret','surtout','ordre','lieu','doute','préférer','ramener','pareil','lumière','pousser']
U3_THEME='ethics and competing values'
U3_GENRES='argument / case / response'

def main():
 if not LOCK.exists(): raise AssertionError('Unit02 frontier lock missing; durable handoff not advanced')
 lock=json.loads(LOCK.read_text(encoding='utf-8'))
 current=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=12 or current!=lock.get('canonical_blob'): raise AssertionError('Unit02 frontier lock does not match live B2')
 if sorted(lock.get('unit02_target_forms',[]))!=sorted(U2): raise AssertionError('Unit02 lock target set drift')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=12 or rows[-1]['id']!='fr-b2-u02-p06' or [r['sequence'] for r in rows]!=list(range(1,13)): raise AssertionError('unexpected B2 canonical frontier')
 wc=[r['word_count'] for r in rows[6:12]]

 s=json.loads(STATUS.read_text(encoding='utf-8'))
 if 'Unit 02 / sequences 7-12 is next' not in s.get('phase',''): raise AssertionError('STATUS no longer at expected Unit02 frontier')
 s['updated']='2026-08-17'
 s['phase']='Arabic A1-C2 is formally approved. French A1, A2, and B1 are generated and generation-integrity PASS. French B2 Units 01-02 are canonical; Unit 03 / sequences 13-18 is next.'
 fr=s['french']; fr['canonical_passages']=192; fr['questions']=1920; fr['answers']=1920; fr['levels']['b2']=12
 b2=fr['b2_generation']; b2['state']='ACTIVE'; b2['passages']=12; b2['questions']=120; b2['answers']=120; b2['completed_units']=[1,2]; b2['last_sequence']=12; b2['canonical_blob']=current; b2['unit02_theme']='decision under uncertainty'; b2['unit02_targets']=U2; b2['unit02_word_counts']=wc; b2['unit02_frontier_lock']='reading/audit/french_b2_unit02_frontier_lock.json'
 fr['next_target']=f'Generate French B2 Unit 03 / sequences 13-18 against B2 blob {current}. Roadmap theme: {U3_THEME}; genres: {U3_GENRES}. Use accepted default 4 fresh targets per P01-P05, P06 zero new, 350-550 words, 10 Q/A, competing-value reasoning, stakeholder claims, scope/exceptions, counterargument and author-position demand, exact reviews, and freshness checks against all prior French targets.'
 s['next_actions']=['keep Arabic sealed unless canonical Arabic changes','do not broadly regenerate French A1/A2/B1','generate French B2 Unit03 against the locked Unit02 blob and canonical topic matrix','continue French generation-first through B2-C2 before final French multi-pass audit','keep Urdu unchanged while French is active unless explicitly reprioritized']
 if 'reading/audit/french_b2_unit02_frontier_lock.json' not in s['important_files']: s['important_files'].append('reading/audit/french_b2_unit02_frontier_lock.json')
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

 t=TASKS.read_text(encoding='utf-8')
 start_marker='#### Unit 02 — IMMEDIATE NEXT'
 if start_marker not in t: raise AssertionError('TASKS no longer at expected Unit02 frontier')
 start=t.index(start_marker); end=t.index('\n## Urdu — QUEUED',start)
 replacement=f'''#### Unit 02 — COMPLETE\n- [x] Sequences 7–12 canonical.\n- [x] 6 passages / 60 Q / 60 A.\n- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.\n- [x] Theme used: `decision under uncertainty`.\n- [x] Canonical B2 blob after Unit02: `{current}`.\n- [x] Frontier lock `reading/audit/french_b2_unit02_frontier_lock.json` = PASS.\n\nUnit 02 targets: `'''+'`, `'.join(U2)+f'''`.\n\n#### Unit 03 — IMMEDIATE NEXT\nRoadmap theme: **{U3_THEME}**. Genres: **{U3_GENRES}**.\n\n- [ ] Generate sequences 13–18 against locked B2 blob `{current}`.\n- [ ] Use accepted default 4 fresh targets per P01–P05; P06 zero new.\n- [ ] Check every candidate against all prior deliberate French A1+A2+B1+B2 targets.\n- [ ] Preserve 350–550 words, 10 linked Q/A, exact review visibility, source rank/ID identity and local target declarations.\n- [ ] Require competing-value analysis, stakeholder claims, scope and exceptions, justified counterargument, author position, inference/reference and synthesis.\n- [ ] Vary argument, case and response genres according to the canonical topic matrix.\n- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.\n\nRemaining after Unit02:\n- [ ] B2: 48 passages.\n- [ ] C1: 60 passages.\n- [ ] C2: 60 passages.\n'''
 t=t[:start]+replacement+t[end:]
 old='**Generate French B2 Unit 02 / sequences 7–12 for `decision under uncertainty` against blob `1ba43c900ad64ff9359264e743470138ce25a9c5`. Keep Arabic sealed.**'
 new=f'**Generate French B2 Unit 03 / sequences 13–18 for `{U3_THEME}` against blob `{current}`. Keep Arabic sealed.**'
 if old not in t: raise AssertionError('TASKS immediate-next anchor drift')
 t=t.replace(old,new)
 TASKS.write_text(t,encoding='utf-8')

 h=HANDOFF.read_text(encoding='utf-8')
 marker='## 6. IMMEDIATE FRONTIER — B2 Unit 02'
 if marker not in h: raise AssertionError('HANDOFF no longer at expected Unit02 frontier')
 start=h.index(marker); end=h.index('\n## 7. Urdu — QUEUED',start)
 block=f'''## 6. B2 Unit 02 — COMPLETE / CURRENT LOCK\n\nTheme used: **decision under uncertainty**. Sequences 7–12.\n\n- 6 passages / 60 questions / 60 answers;\n- 20 fresh deliberate targets, four in P01–P05; P06 zero new;\n- canonical B2 blob after Unit02: `{current}`;\n- frontier lock artifact: `reading/audit/french_b2_unit02_frontier_lock.json` = PASS;\n- Unit02 targets: `'''+'`, `'.join(U2)+f'''`.\n\nGuard repairs preserved rather than weakened freshness, local-linkage and exact-form checks.\n\n## 7. IMMEDIATE FRONTIER — B2 Unit 03\n\nCanonical topic-matrix theme: **{U3_THEME}**. Genres: **{U3_GENRES}**.\n\nGenerate **sequences 13–18** against exact B2 blob `{current}`.\n\nRequirements:\n1. require the Unit02 frontier lock and verify the live B2 blob before target selection or append;\n2. use accepted default 4 fresh targets per P01–P05 unless discourse load clearly justifies another value within 4–8; P06 zero new;\n3. check every candidate against all deliberate French A1+A2+B1+B2 Units01–02 targets;\n4. preserve source rank/ID/intended sense and exact target/review exposure;\n5. build natural argument/case/response passages around competing values, stakeholder claims, scope, exceptions, fairness/obligation trade-offs and counterarguments;\n6. preserve 350–550 words, 10 linked Q/A, B2 author-position/argument/inference/reference/synthesis demand;\n7. fail closed and repair instead of weakening guards.\n'''
 h=h[:start]+block+h[end:]
 h=h.replace('\n## 7. Urdu — QUEUED','\n## 8. Urdu — QUEUED').replace('\n## 8. Throughput / parallel rules','\n## 9. Throughput / parallel rules').replace('\n## 9. Core non-negotiables','\n## 10. Core non-negotiables')
 HANDOFF.write_text(h,encoding='utf-8')
 print(json.dumps({'status':'PASS','b2_blob':current,'b2_passages':12,'next':'B2 Unit03','theme':U3_THEME,'word_counts':wc},ensure_ascii=False))
if __name__=='__main__':main()
