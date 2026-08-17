#!/usr/bin/env python3
"""Advance durable state to B2 Unit05 only from the exact Unit04 lock."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit04_frontier_lock.json';STATUS=R/'reading/STATUS.json';TASKS=R/'reading/TASKS.md';HANDOFF=R/'reading/AGENT_HANDOFF.md'
U4=['coin','côté','arbre','air','voiture','proche','besoin','simple','construire','ouvrir','fermer','utiliser','haut','bas','monter','descendre','entrer','sortir','servir','nouveau']
THEME='climate and uncertainty';GENRES='evidence summary / news analysis / argument'
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=24 or blob!=lock.get('canonical_blob') or sorted(lock.get('unit04_target_forms',[]))!=sorted(U4):raise AssertionError('Unit04 lock mismatch')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=24 or rows[-1]['id']!='fr-b2-u04-p06':raise AssertionError('unexpected B2 frontier')
 wc=[r['word_count'] for r in rows[18:24]]
 s=json.loads(STATUS.read_text(encoding='utf-8'));b=s['french']['b2_generation']
 if b.get('last_sequence')!=18:raise AssertionError('STATUS not at pre-Unit04 sync frontier')
 s['phase']='Arabic A1-C2 is formally approved. French A1, A2, and B1 are generated and generation-integrity PASS. French B2 Units 01-04 are canonical; Unit 05 / sequences 25-30 is next.'
 fr=s['french'];fr['canonical_passages']=204;fr['questions']=2040;fr['answers']=2040;fr['levels']['b2']=24
 b['passages']=24;b['questions']=240;b['answers']=240;b['completed_units']=[1,2,3,4];b['last_sequence']=24;b['canonical_blob']=blob;b['unit04_theme']='cities and design';b['unit04_targets']=U4;b['unit04_word_counts']=wc;b['unit04_frontier_lock']='reading/audit/french_b2_unit04_frontier_lock.json'
 fr['next_target']=f'Generate French B2 Unit 05 / sequences 25-30 against B2 blob {blob}. Canonical topic-matrix theme: {THEME}; genres: {GENRES}. Use accepted default 4 fresh targets per P01-P05, P06 zero new, 350-550 words, 10 Q/A, explicit evidence/uncertainty reasoning, competing explanations, probability/limits, counterargument and synthesis, exact reviews, and freshness checks against all prior French targets.'
 s['next_actions']=['keep Arabic sealed unless canonical Arabic changes','do not broadly regenerate French A1/A2/B1','generate French B2 Unit05 against the locked Unit04 blob and canonical topic matrix','continue French generation-first through B2-C2 before final French multi-pass audit','keep Urdu unchanged while French is active unless explicitly reprioritized']
 if 'reading/audit/french_b2_unit04_frontier_lock.json' not in s['important_files']:s['important_files'].append('reading/audit/french_b2_unit04_frontier_lock.json')
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 t=TASKS.read_text(encoding='utf-8');start=t.index('#### Unit 04 — IMMEDIATE NEXT');end=t.index('\n## Urdu — QUEUED',start)
 block=f'''#### Unit 04 — COMPLETE\n- [x] Sequences 19–24 canonical.\n- [x] 6 passages / 60 Q / 60 A.\n- [x] 20 fresh source-backed targets, four in P01–P05; P06 zero new.\n- [x] Theme: `cities and design`; genres: report / proposal / critique.\n- [x] Canonical B2 blob after Unit04: `{blob}`.\n- [x] Frontier lock `reading/audit/french_b2_unit04_frontier_lock.json` = PASS.\n\nUnit 04 targets: `'''+'`, `'.join(U4)+f'''`.\n\n#### Unit 05 — IMMEDIATE NEXT\nCanonical topic-matrix theme: **{THEME}**. Genres: **{GENRES}**.\n\n- [ ] Generate sequences 25–30 against locked B2 blob `{blob}`.\n- [ ] Accepted default 4 fresh targets per P01–P05; P06 zero new.\n- [ ] Check every candidate against all prior deliberate French A1–B2 targets.\n- [ ] Preserve 350–550 words, 10 linked Q/A, source identity, exact reviews and local target declarations.\n- [ ] Require evidence-strength, uncertainty, competing explanations, probability/limitations, counterargument, author position and synthesis.\n- [ ] Fail closed on lock/source drift, collision, schema/linkage, word band or review visibility.\n\nRemaining after Unit04:\n- [ ] B2: 36 passages.\n- [ ] C1: 60 passages.\n- [ ] C2: 60 passages.\n'''
 t=t[:start]+block+t[end:]
 old=f'**Generate French B2 Unit 04 / sequences 19–24 for `cities and design` against blob `e97d0929a5ea7aa09a7306a82f9159194ff954da`. Keep Arabic sealed.**';new=f'**Generate French B2 Unit 05 / sequences 25–30 for `{THEME}` against blob `{blob}`. Keep Arabic sealed.**'
 if old not in t:raise AssertionError('TASKS anchor drift')
 TASKS.write_text(t.replace(old,new),encoding='utf-8')
 h=HANDOFF.read_text(encoding='utf-8');start=h.index('## 8. IMMEDIATE FRONTIER — B2 Unit 04');end=h.index('\n## 9. Urdu — QUEUED',start)
 block=f'''## 8. B2 Unit 04 — COMPLETE / CURRENT LOCK\n\nTheme: **cities and design**. Genres: report / proposal / critique. Sequences 19–24.\n\n- 6 passages / 60 questions / 60 answers;\n- 20 fresh targets, four in P01–P05; P06 zero new;\n- canonical B2 blob `{blob}`;\n- frontier lock `reading/audit/french_b2_unit04_frontier_lock.json` = PASS;\n- Unit04 targets: `'''+'`, `'.join(U4)+f'''`.\n\n## 9. IMMEDIATE FRONTIER — B2 Unit 05\n\nCanonical theme: **{THEME}**. Genres: **{GENRES}**. Generate sequences **25–30** against exact blob `{blob}`. Require the Unit04 lock; use four fresh targets by default in P01–P05 and zero new in P06; preserve source freshness/rank identity, exact reviews, 350–550 words, 10 linked Q/A, and explicit reasoning about evidence strength, uncertainty, competing explanations, limitations, counterargument and synthesis. Fail closed and repair instead of weakening guards.\n'''
 h=h[:start]+block+h[end:];h=h.replace('\n## 9. Urdu — QUEUED','\n## 10. Urdu — QUEUED').replace('\n## 10. Throughput / parallel rules','\n## 11. Throughput / parallel rules').replace('\n## 11. Core non-negotiables','\n## 12. Core non-negotiables')
 HANDOFF.write_text(h,encoding='utf-8');print(json.dumps({'status':'PASS','blob':blob,'next':'B2 Unit05','theme':THEME,'word_counts':wc},ensure_ascii=False))
if __name__=='__main__':main()
