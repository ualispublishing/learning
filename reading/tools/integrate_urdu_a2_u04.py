#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, urllib.parse, subprocess

ROOT=Path(".")
A2=ROOT/"reading/urdu/a2/passages.jsonl"
A1=ROOT/"reading/urdu/a1/passages.jsonl"
STATUS=ROOT/"reading/STATUS.json"
CONT=ROOT/"reading/CONTINUATION.json"
TASKS=ROOT/"reading/TASKS.md"
HANDOFF=ROOT/"reading/AGENT_HANDOFF_V2.md"
LEX=ROOT/"reading/audit/urdu_a2_u04_lexical_sense_check_2026-08-24.json"
QUAL=ROOT/"reading/audit/urdu_a2_u04_quality_pass_2026-08-24.json"

SOURCE_BLOB="be63df201db20cd4969e845793c122844bc18bb7"
PACKET_SHA="a7a51785008542503f4af78caa47b83ce77939af98b92316a9984342489ede65"
PARTS=[
("reading/staging/u04_exact_p01.tmp","6e14edff0c58d2d90f599424f9f0b315024d5b68"),
("reading/staging/u04_exact_p02.tmp","284e9936e86a6e50755ee5da0440f33817008cc7"),
("reading/staging/u04_exact_p03.tmp","5bb39d50951e5dd8ed28f3c3a9b2e69925a75d90"),
("reading/staging/u04_exact_p04.tmp","5157b6c7a92e3d61846ddd449f08731689533666"),
("reading/staging/u04_exact_p05.tmp","eaa5a9eea4d450a8e401ab3e4aa13cd891fcc833"),
("reading/staging/u04_exact_p06.tmp","f02a3a6c4d5d7e6d97e01e55c2c7e2ebac1d19e8"),
]
TARGETS={
"ur-a2-u04-p01":["ur-rank-0690","ur-rank-0769"],
"ur-a2-u04-p02":["ur-rank-0765","ur-rank-0715"],
"ur-a2-u04-p03":["ur-rank-0800","ur-rank-0803"],
"ur-a2-u04-p04":["ur-rank-0832","ur-rank-0955"],
"ur-a2-u04-p05":[],
"ur-a2-u04-p06":[],
}
WCS=[202,207,199,203,211,195]
ROLES=["instructional","reinforcement","interleaved","transfer","integration","fluency"]
GENRES={"review","problem-solution narrative","notice"}

def git_blob(b):
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()
def sha256(b): return hashlib.sha256(b).hexdigest()
def rows(b): return [json.loads(x) for x in b.splitlines()]
def fail(s): raise SystemExit(s)

src=A2.read_bytes()
if git_blob(src)!=SOURCE_BLOB: fail("A2 source blob drift")
old=rows(src)
if len(old)!=18 or [x["sequence"] for x in old]!=list(range(1,19)): fail("A2 source sequence/count drift")
st=json.loads(STATUS.read_text())
co=json.loads(CONT.read_text())
if st["current"]["canonical_passages"]!=798 or st["languages"]["urdu"]["canonical_passages"]!=78: fail("STATUS frontier drift")
if co["production"]["canonical_passages"]!=798 or co["production"]["urdu"]["canonical_passages"]!=78: fail("CONTINUATION count drift")
if "Unit 4 / sequence 19" not in co["active_frontier"]["production"]["action"]: fail("CONTINUATION frontier drift")

ps=[]
for path, expected in PARTS:
    b=(ROOT/path).read_bytes()
    if git_blob(b)!=expected: fail(f"staged byte drift: {path}")
    ps.append(b)
packet=b"\n".join(ps)+b"\n"
if len(packet)!=51180 or sha256(packet)!=PACKET_SHA: fail("reviewed packet hash/size drift")
recs=rows(packet)
if len(recs)!=6: fail("packet count")

introduced=set()
for p in [A1,A2]:
    for r in rows(p.read_bytes()):
        introduced |= {t["id"] for t in r.get("new_lexical_targets",[])}

questions=answers=0
exposures={}
for i,r in enumerate(recs):
    rid=f"ur-a2-u04-p{i+1:02d}"
    if (r.get("id"),r.get("sequence"),r.get("unit"),r.get("language"),r.get("cefr"))!=(rid,19+i,4,"ur","A2"): fail(f"{rid}: identity")
    if r.get("passage_type")!=ROLES[i] or r.get("genre") not in GENRES: fail(f"{rid}: roadmap")
    wc=len(r["text"].split())
    if wc!=r.get("word_count") or wc!=WCS[i] or not 140<=wc<=220: fail(f"{rid}: word count")
    qs,ans=r["questions"],r["answer_key"]
    if len(qs)!=10 or len(ans)!=10: fail(f"{rid}: q/a count")
    questions+=10; answers+=10
    for n,(q,a) in enumerate(zip(qs,ans),1):
        if q.get("id")!=f"q{n}" or q.get("answer_id")!=f"a{n}" or a.get("id")!=f"a{n}" or a.get("question_id")!=f"q{n}" or not a.get("answer","").strip():
            fail(f"{rid}: q/a link")
    nts=r.get("new_lexical_targets",[])
    ids=[t["id"] for t in nts]
    if ids!=TARGETS[rid]: fail(f"{rid}: target set")
    exposures[rid]={}
    for t in nts:
        if t["id"] in introduced: fail(f"{rid}: target not fresh")
        c=r["text"].count(t["form"])
        if c!=t["exposures_in_text"] or c<2: fail(f"{rid}: target exposure")
        if not any(t["id"] in q.get("target_ids",[]) for q in qs): fail(f"{rid}: target unassessed")
        exposures[rid][t["id"]]=c
if sum(len(v) for v in TARGETS.values())!=8: fail("target total")
if recs[4]["new_lexical_targets"] or recs[5]["new_lexical_targets"]: fail("P5/P6 new-target policy")
if recs[5]["speed_training"].get("new_word_policy")!="none" or not recs[5]["speed_training"].get("timed"): fail("P6 fluency policy")

result=src+packet
if len(rows(result))!=24: fail("result count")
A2.write_bytes(result)
result_blob=git_blob(result)

target_rows=[]
for r in recs[:4]:
    for t in r["new_lexical_targets"]:
        target_rows.append({
            "id":t["id"],"form":t["form"],"source_rank":t["source_rank"],
            "accepted_sense":t["intended_sense"],"dictionary":"Rekhta Dictionary",
            "url":"https://www.rekhta.org/urdudictionary?keyword="+urllib.parse.quote(t["form"])
        })
LEX.write_text(json.dumps({
    "schema_version":1,"project_id":"LANG-A1C2","language":"ur","cefr":"A2","unit":4,"date":"2026-08-24",
    "status":"PASS_FOR_GENERATION_TARGET_SENSES",
    "scope":"Deliberate learner-facing senses only. This does not validate whole-passage linguistic/pedagogical quality or educator/publication release readiness.",
    "source_lexicon":"reading/lexicons/urdu.jsonl",
    "canonical_freshness_method":"All eight candidate IDs were checked against live canonical Urdu A1 and A2 new_lexical_targets and were absent before Unit 4.",
    "targets":target_rows,
    "generation_policy":{"P1_P4_new_targets_per_passage":2,"P5_new_targets":0,"P6_new_targets":0,"P6_new_word_policy":"none"},
    "quality_promotion":False
},ensure_ascii=False,indent=2)+"\n")

QUAL.write_text(json.dumps({
    "schema_version":1,"project_id":"LANG-A1C2","language":"ur","cefr":"A2","unit":4,"date":"2026-08-24",
    "status":"PASS_AFTER_PRECANONICAL_READER_PASS",
    "scope":"Bounded generation-stage reader-first pass for Unit 4 only: naturalness, target-sense clarity, answer grounding/linkage, operational A2 grammar, word-band checks, roadmap role/genre checks, and fluency new-word policy. Formal corpus-wide linguistic, pedagogical, CEFR/coverage, independent/native, and educator-release gates remain pending.",
    "source_canonical_git_blob":SOURCE_BLOB,"source_a2_passages":18,"packet_sha256":PACKET_SHA,
    "result_canonical_git_blob":result_blob,"result_a2_passages":24,"project_passages_after":804,"urdu_passages_after":84,
    "unit_sequences":list(range(19,25)),"passages":6,"questions":questions,"answers":answers,
    "word_counts":{r["id"]:r["word_count"] for r in recs},
    "new_target_ids_by_passage":TARGETS,"new_target_exposures":exposures,
    "lexical_sense_evidence":"reading/audit/urdu_a2_u04_lexical_sense_check_2026-08-24.json",
    "checks":{"source_blob_guard":True,"packet_hash_guard":True,"six_component_blob_guards":True,"fresh_target_ids_against_live_urdu_a1_a2":True,
              "six_passage_role_order":True,"roadmap_genres_only":True,"word_band_140_220":True,
              "exactly_10_questions_and_10_answers_each":True,"bidirectional_q_a_links":True,"each_new_target_assessed":True,
              "target_exposure_metadata_recounted":True,"p5_has_no_new_deliberate_targets":True,"p6_has_no_new_deliberate_targets":True,
              "p6_new_word_policy_none":True,"post_write_project_and_urdu_counts":True},
    "quality_promotion":False,"educator_release_ready":False
},ensure_ascii=False,indent=2)+"\n")

st["current"]["canonical_passages"]=804; st["current"]["remaining_generation_passages"]=276
st["languages"]["urdu"]["canonical_passages"]=84; st["languages"]["urdu"]["remaining_generation_passages"]=276
STATUS.write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n")

co["production"]["canonical_passages"]=804; co["production"]["urdu"]["canonical_passages"]=84
co["active_frontier"]["production"]["action"]="Continue generation-first production from Urdu A2 Unit 5 / sequence 25 using the canonical roadmap and ten-question contract. Do not reopen Urdu A1 generation unless fresh evidence identifies a concrete defect."
co["exact_next_actions"]=[x.replace("Unit 4 batch at sequence 19","Unit 5 batch at sequence 25") for x in co["exact_next_actions"]]
CONT.write_text(json.dumps(co,ensure_ascii=False,indent=2)+"\n")

def rep(path, old,new):
    s=path.read_text()
    if old not in s: fail(f"{path}: missing expected live text")
    path.write_text(s.replace(old,new))
rep(TASKS,"Canonical production frontier: **Urdu A2, Unit 4, sequence 19**.","Canonical production frontier: **Urdu A2, Unit 5, sequence 25**.")
rep(TASKS,"- Urdu: 78/360 generated; A1 complete, A2 in progress.","- Urdu: 84/360 generated; A1 complete, A2 in progress.")
rep(TASKS,"- Project: 798/1080 generated.","- Project: 804/1080 generated.")
rep(HANDOFF,"- Canonical generated total: **798**.","- Canonical generated total: **804**.")
rep(HANDOFF,"- Urdu: **78/360**; A1 generation complete and A2 generation in progress.","- Urdu: **84/360**; A1 generation complete and A2 generation in progress.")
rep(HANDOFF,"- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-3 currently contain sequences 1-18.","- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-4 currently contain sequences 1-24.")
rep(HANDOFF,"Continue **Urdu A2**, starting from Unit 4 / sequence 19, under:","Continue **Urdu A2**, starting from Unit 5 / sequence 25, under:")
rep(HANDOFF,"Unit 4 uses the roadmap theme **shopping, comparison, and problems** with `review`, `problem-solution narrative`, and `notice` genres.","Unit 5 uses the roadmap theme **hobbies and learning skills** with `profile`, `how-to`, and `short article` genres.")
rep(HANDOFF,"Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu A2 Unit 4 / sequence 19** using the Unit 4 roadmap theme `shopping, comparison, and problems`.","Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu A2 Unit 5 / sequence 25** using the Unit 5 roadmap theme `hobbies and learning skills`.")

subprocess.run(["python","reading/tools/extract_active_generation_plan.py"],check=True)
subprocess.run(["python","reading/tools/refresh_state_manifest.py"],check=True)
subprocess.run(["python","reading/tools/validate_continuation_state.py"],check=True)
print(json.dumps({"status":"PASS","source_blob":SOURCE_BLOB,"packet_sha256":PACKET_SHA,"result_blob":result_blob,
                  "project_after":804,"urdu_after":84,"next_unit":5,"next_sequence":25}))
