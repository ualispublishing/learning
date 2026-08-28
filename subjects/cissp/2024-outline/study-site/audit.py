#!/usr/bin/env python3
"""Deterministic release audit for CISSP Atlas."""
import json, re, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
QB=ROOT/"question-bank"
errors=[]
def check(ok,msg):
    if not ok: errors.append(msg)
def read(p): return p.read_text(encoding="utf-8").strip()
def jsonish(s,label):
    try: return json.loads(s)
    except json.JSONDecodeError as e1:
        fixed=re.sub(r"(?m)^(\s*)(\d+)\s*:",r'\1"\2":',s)
        if fixed==s: raise RuntimeError(f"{label} invalid JSON-compatible data: {e1}") from e1
        try: return json.loads(fixed)
        except json.JSONDecodeError as e2: raise RuntimeError(f"{label} invalid JSON-compatible JavaScript data: {e2}") from e2
def parse_meta():
    s=read(ROOT/"data-meta.js"); pre="window.CISSP_META="; marker=";window.CISSP_CHUNKS=[];"
    if not s.startswith(pre) or marker not in s: raise RuntimeError("data-meta.js wrapper invalid")
    return jsonish(s[len(pre):s.index(marker)],"data-meta.js")
def chunk(name):
    s=read(ROOT/name); pre="window.CISSP_CHUNKS.push("; suf=");"
    if not s.startswith(pre) or not s.endswith(suf): raise RuntimeError(f"Invalid CISSP chunk wrapper: {name}")
    return jsonish(s[len(pre):-len(suf)],name)
def parse_coverage():
    s=read(ROOT/"coverage-detail.js"); pre="window.CISSP_COVERAGE="; marker=";\nwindow.CISSP_AI_COVERAGE="
    if not s.startswith(pre) or marker not in s or not s.endswith(";"): raise RuntimeError("coverage-detail.js wrapper invalid")
    i=s.index(marker)
    return jsonish(s[len(pre):i],"CISSP coverage"),jsonish(s[i+len(marker):-1],"CISSP AI coverage")
def jsonl(p):
    out=[]
    for n,line in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: out.append(json.loads(line))
        except json.JSONDecodeError as e: raise RuntimeError(f"{p.relative_to(ROOT)}:{n} invalid JSONL: {e}") from e
    return out

try:
    M=parse_meta()
    chunks=[chunk(f"data-d{i}.js") for i in range(1,9)]+[chunk("data-ai.js"),chunk("data-precision.js")]
    coverage,ai=parse_coverage()
    release=json.loads(read(ROOT/"RELEASE_STATUS.json"))
    semantic_base=json.loads(read(ROOT/"SEMANTIC_ITEM_AUDIT.json"))
    additions_path=ROOT/"SEMANTIC_RELEASE_ADDITIONS.json"
    semantic_additions=json.loads(read(additions_path)) if additions_path.exists() else None
    manifest=json.loads(read(QB/"RELEASED_BATCHES.json"))
except (OSError,ValueError,RuntimeError,AssertionError) as e:
    print("FAIL"); print("-",f"Parse/setup error: {e}"); sys.exit(1)

objectives=sum((c["objectives"] for c in chunks),[])
high=sum((c["high"] for c in chunks),[])
base=sum((c["questions"] for c in chunks),[])
released=[]; seen_files=set()
for b in manifest.get("released_batches",[]):
    rows=[]
    for rel in b.get("files",[]):
        check(rel not in seen_files,f"Released file listed more than once: {rel}"); seen_files.add(rel)
        p=ROOT/rel; check(p.is_file(),f"Released file missing: {rel}")
        if p.is_file():
            try: rows+=jsonl(p)
            except RuntimeError as e: errors.append(str(e))
    for rel in b.get("review_files",[]):
        p=ROOT/rel; check(p.is_file(),f"Release review file missing: {rel}")
        if p.is_file():
            try:
                r=json.loads(read(p))
                check(str(r.get("status","")).startswith("SEMANTIC_REVIEWED_"),f"Release review not semantically reviewed: {rel}")
            except ValueError as e: errors.append(f"{rel} invalid JSON: {e}")
    released+=rows
    d=Counter(x.get("difficulty_tier") for x in rows); bid=b.get("batch_id")
    check(len(rows)==b.get("records"),f"{bid} record count drift")
    check(sum(x.get("format")=="mcq" for x in rows)==b.get("standard_mcq"),f"{bid} MCQ count drift")
    check(sum(x.get("format")=="bellringer" for x in rows)==b.get("bellringers"),f"{bid} Bellringer count drift")
    check({k:d.get(k,0) for k in ("F","E","S","B")}==b.get("difficulty"),f"{bid} difficulty drift")
    check(b.get("semantic_review")=="PASS",f"{bid} semantic release gate missing")
    check(b.get("originality_preflight")=="PASS",f"{bid} originality gate missing")

released_mcq=[x for x in released if x.get("format")=="mcq"]
bells=[x for x in released if x.get("format")=="bellringer"]
questions=base+released_mcq
obj_counts={1:12,2:6,3:10,4:3,5:6,6:5,7:15,8:5}
weights={1:16,2:10,3:13,4:13,5:13,6:12,7:13,8:10}
check(len(M["domains"])==8,"Expected 8 domains")
check(sum(d["weight"] for d in M["domains"])==100,"Weights !=100")
check({d["num"]:d["weight"] for d in M["domains"]}==weights,"Official weights drift")
for d,n in obj_counts.items(): check(sum(o["domain_num"]==d for o in objectives)==n,f"D{d} objective count wrong")
ids=[o["id"] for o in objectives]
check(len(ids)==62 and len(ids)==len(set(ids)),"Objective IDs incomplete/duplicate")
for d,n in obj_counts.items(): check(all(f"{d}.{i}" in ids for i in range(1,n+1)),f"D{d} missing objective ID")
check(set(coverage)==set(ids),"Subtopic coverage keys must exactly match objectives")
check(all(isinstance(v,list) and v and all(isinstance(x,str) and x.strip() for x in v) for v in coverage.values()),"Invalid subtopic coverage")
check(set(ai)=={str(i) for i in range(1,9)},"AI coverage must include all domains")
check(all(isinstance(v,list) and v for v in ai.values()),"Empty AI coverage domain")

for o in objectives:
    check(bool(o.get("direct","").strip()) and bool(o.get("trap","").strip()),f"Objective {o['id']} missing content")
    check(all(s in M["sources"] for s in o.get("source_ids",[])),f"Objective {o['id']} source invalid")
for h in high:
    check(h["objective"] in ids,f"Card {h['id']} objective invalid")
    check(bool(h.get("front","").strip()) and bool(h.get("direct","").strip()) and bool(h.get("trap","").strip()),f"Card {h['id']} missing content")
    check(all(s in M["sources"] for s in h.get("source_ids",[])),f"Card {h['id']} source invalid")
for q in base:
    check(q["objective"] in ids,f"Base question {q['id']} objective invalid")
    check(len(q["options"])==4 and isinstance(q["answer"],int) and 0<=q["answer"]<4,f"Base question {q['id']} answer/options invalid")
    check(bool(q.get("stem","").strip()) and bool(q.get("explanation","").strip()),f"Base question {q['id']} content missing")
for q in released:
    qid=q.get("id")
    check(all(o in ids for o in q.get("objectives",[])),f"Released record {qid} objective invalid")
    check(all(s in M["sources"] for s in q.get("source_ids",[])),f"Released record {qid} source invalid")
    check(str(q.get("review_status","")).startswith("SEMANTIC_REVIEWED_"),f"Released record {qid} not semantically reviewed")
    ori=q.get("originality",{})
    check(ori.get("origin")=="original-from-public-scope" and ori.get("no_external_question_seed") is True,f"Released record {qid} originality provenance invalid")
    if q.get("format")=="mcq":
        check(len(q.get("options",[]))==4 and isinstance(q.get("answer"),int) and 0<=q["answer"]<4 and len(q.get("distractor_rationales",[]))==4,f"Released MCQ {qid} invalid")
    elif q.get("format")=="bellringer":
        check(q.get("difficulty_tier")=="B" and 4<=len(q.get("prompts",[]))<=8 and bool(q.get("rubric")),f"Bellringer {qid} invalid")
    else: check(False,f"Released record {qid} format invalid")

check(len({h["id"] for h in high})==len(high),"Duplicate high-card ID")
check(len({q["id"] for q in questions})==len(questions),"Duplicate standard-question ID")
check(len({q["id"] for q in released})==len(released),"Duplicate released-batch ID")
cards=62+len(high); subtopics=sum(len(v) for v in coverage.values()); ai_areas=sum(len(v) for v in ai.values()); sources=len(M["sources"])
standard=len(questions); bell_count=len(bells); bank=standard+bell_count
base_sem_items=semantic_base.get("items",{}); add_sem_items=(semantic_additions or {}).get("items",{})
check(not(set(base_sem_items)&set(add_sem_items)),"Semantic base/additions contain duplicate item IDs")
sem_items={**base_sem_items,**add_sem_items}; sem_count=len(sem_items)
cal_raw=read(ROOT/"data-question-calibration.js")
cal=dict(re.findall(r'"(Q-\d{3})":\{tier:"([FES])"',cal_raw))
check(len(cal)==56 and all(f"Q-{i:03d}" in cal for i in range(1,57)),"Base difficulty calibration incomplete")
dist=Counter(cal.get(q["id"]) for q in base); dist.update(q.get("difficulty_tier") for q in released)

check(cards==140,"Runtime cards !=140"); check(len(base)==56,"Base question baseline !=56")
check(standard>=175,"Released standard MCQs fell below v1.5 floor"); check(bell_count>=1,"Released Bellringers fell below v1.5 floor"); check(bank>=176,"Question-bank records fell below v1.5 floor")
check(sources==20,"Source count !=20"); check(subtopics==344,"Subtopic count !=344"); check(ai_areas==33,"AI area count !=33")
for d in range(1,9):
    check(sum((q.get("domain_num") if "domain_num" in q else q.get("domain_primary"))==d for q in questions)>=9,f"D{d} standard-question coverage too low")
    check(sum(h["domain_num"]==d and h["id"].startswith("PX-") for h in high)==4,f"D{d} precision cards !=4")
    check(sum(h["domain_num"]==d and h["id"].startswith("AI-") for h in high)==1,f"D{d} AI cards !=1")

mm=M["meta"]; version=release.get("release")
semantic_release=(semantic_additions or semantic_base).get("release")
release_audit_date=release.get("last_semantic_audit") or release.get("prepared_on")
check(version==mm.get("version")==semantic_release,"Release version drift across ledgers")
check(bool(release_audit_date) and mm.get("audited_on")==release_audit_date,"Metadata audit date drift")
check(mm.get("objective_count")==62 and mm.get("subtopic_checks")==subtopics and mm.get("ai_coverage_areas")==ai_areas and mm.get("card_count")==cards,"Metadata knowledge counts drift")
check(mm.get("question_count")==standard and mm.get("bellringer_count")==bell_count and mm.get("question_bank_records")==bank and mm.get("semantic_items_reviewed")==sem_count,"Metadata bank counts drift")
check(mm.get("source_count")==sources and mm.get("domain_weight_total")==100,"Metadata source/weight drift")
rs=release.get("scope",{})
check(release.get("project_id")=="CISSP-ATLAS" and release.get("status")=="READY_FOR_STUDY","Release identity/state drift")
check(rs.get("domains")==8 and rs.get("numbered_objectives")==62 and rs.get("subtopic_checks")==subtopics and rs.get("ai_coverage_areas")==ai_areas and rs.get("layered_cards")==cards and rs.get("standard_scenario_questions")==standard and rs.get("bellringers")==bell_count and rs.get("question_bank_records")==bank and rs.get("semantic_items_reviewed")==sem_count and rs.get("sources")==sources and rs.get("official_weight_total_percent")==100,"Release scope drift")
check(rs.get("released_difficulty_distribution")=={k:dist.get(k,0) for k in ("F","E","S","B")},"Release difficulty distribution drift")

# Learner-facing documentation and continuation routing must not lag the release ledger.
try:
    readme=read(ROOT/"README.md")
    tomorrow=read(ROOT/"TOMORROW_START.md")
    precision=read(ROOT/"PRECISION_AUDIT.md")
    tracks=json.loads(read(ROOT.parents[3]/"PROJECT_TRACKS.json"))
except (OSError,ValueError) as e:
    errors.append(f"Release documentation freshness setup error: {e}")
else:
    doc_markers={
        "README.md":[f"v{version}",f"{standard} released standard scenario questions + {bell_count} Bellringer = {bank} released bank records",f"{sem_count} learner-facing item IDs"],
        "TOMORROW_START.md":[f"v{version}",f"{standard} released standard scenario questions + {bell_count} Bellringer = {bank} question-bank records",f"{sem_count} semantically reviewed learner-facing item IDs"],
        "PRECISION_AUDIT.md":[f"v{version}",f"{standard} released standard scenario questions",f"{bank} total released question-bank records",f"{sem_count} learner-facing item IDs"],
    }
    for name,text in (("README.md",readme),("TOMORROW_START.md",tomorrow),("PRECISION_AUDIT.md",precision)):
        for marker in doc_markers[name]: check(marker in text,f"{name} release marker stale/missing: {marker}")
    cscope=tracks.get("tracks",{}).get("CISSP-ATLAS",{}).get("current_scope",{})
    check(cscope.get("version")==version,"PROJECT_TRACKS CISSP version drift")
    check(cscope.get("domains")==8 and cscope.get("objectives")==62 and cscope.get("subtopic_checks")==subtopics and cscope.get("ai_coverage_areas")==ai_areas and cscope.get("layered_cards")==cards,"PROJECT_TRACKS CISSP knowledge-count drift")
    check(cscope.get("released_standard_questions")==standard and cscope.get("released_bellringers")==bell_count and cscope.get("released_bank_records")==bank and cscope.get("semantic_items_reviewed")==sem_count,"PROJECT_TRACKS CISSP release-count drift")
    check(cscope.get("released_question_difficulty")=={k:dist.get(k,0) for k in ("F","E","S","B")},"PROJECT_TRACKS CISSP difficulty drift")

expected_semantic={*(f"OBJ-{o['id']}" for o in objectives),*(h["id"] for h in high),*(q["id"] for q in base),*(q["id"] for q in released)}
allowed={"VERIFIED","VERIFIED_AFTER_CORRECTION","VERIFIED_WITH_SOURCE_SCOPE_NOTE"}
check(semantic_base.get("audit_date")=="2026-08-24","Semantic base audit date drift")
check(semantic_base.get("scope",{}).get("total_items")==len(base_sem_items),"Semantic base scope drift")
if semantic_additions:
    check(semantic_additions.get("audit_date")==release_audit_date,"Semantic additions audit date drift")
    check(semantic_additions.get("base_items")==len(base_sem_items),"Semantic additions base count drift")
    check(semantic_additions.get("added_items")==len(add_sem_items),"Semantic additions count drift")
    check(semantic_additions.get("total_items")==sem_count,"Semantic additions total count drift")
check(set(sem_items)==expected_semantic,f"Semantic coverage mismatch expected {len(expected_semantic)} got {len(sem_items)}")
check(len(expected_semantic)>=316,"Semantic item count fell below v1.5 floor")
check(all(v.get("status") in allowed for v in sem_items.values()),"Semantic audit contains unreviewed status")
base_summary=semantic_base.get("summary",{}); add_summary=(semantic_additions or {}).get("summary",{})
reviewed_total=sum(base_summary.get(k,0)+add_summary.get(k,0) for k in ("verified","verified_after_correction","verified_with_source_scope_note"))
check(reviewed_total==sem_count,"Semantic summary count drift")
check(base_summary.get("answer_key_reversals",0)+add_summary.get("answer_key_reversals",0)==0,"Semantic summary reports answer-key reversal")
check(base_summary.get("material_factual_errors_remaining",0)+add_summary.get("material_factual_errors_remaining",0)==0,"Semantic summary reports unresolved factual error")

html=read(ROOT/"index.html"); label=".".join(str(version).split(".")[:2])
required=["data-meta.js",*[f"data-d{i}.js" for i in range(1,9)],"data-ai.js","data-precision.js","coverage-detail.js","data-question-calibration.js","bootstrap.js","styles.css","mobile-fix.css","enhancements.css",'id="today"','id="learn"','id="practice"','id="blueprint"','id="progress"','id="sources"','id="quizDifficulty"','id="startBellringer"','value="999999">All available</option>',f"RELEASE v{label}"]
check(all(x in html for x in required),"HTML shell/assets/release controls incomplete"); check("Weighted mixed domains" not in html,"Misleading weighted-mix wording present")
bootstrap=read(ROOT/"bootstrap.js"); app=read(ROOT/"app.js"); enh=read(ROOT/"enhancements.js")
check("RELEASED_BATCHES.json" in bootstrap and "CISSP_BELLRINGERS" in bootstrap and "import('./app.js')" in bootstrap,"Bootstrap release loading incomplete")
check("cisspStandardQuestions" in bootstrap and "cisspReleasedRecords" in bootstrap,"Bootstrap bank-count health markers missing")
check("CISSP_CHUNKS.flatMap" in app and "D.cards=" in app,"App runtime assembly missing")
check("startCalibratedQuiz" in enh and "startBellringer" in enh and "data-conf" in enh and "distractor_rationales" in enh and "addSubtopicSearch" in enh,"Enhanced practice workflow incomplete")
check((QB/"quality_gate.py").exists() and (QB/"QUESTION_BANK_EXPANSION_PLAN.md").exists(),"Question-bank quality system incomplete")

if errors:
    print("FAIL")
    for e in errors: print("-",e)
    sys.exit(1)
print("PASS")
print(f"release={version} status=READY_FOR_STUDY domains=8 objectives=62 subtopic_checks={subtopics} ai_areas={ai_areas} cards={cards} standard_questions={standard} bellringers={bell_count} bank_records={bank} sources={sources} semantic_items={sem_count} released_difficulty={dict(sorted(dist.items()))} weights=100%")
