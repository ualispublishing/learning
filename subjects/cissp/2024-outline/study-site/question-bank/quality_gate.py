#!/usr/bin/env python3
"""CISSP Atlas future-question quality/originality gate.

Default: validate every question-bank/candidates/*.jsonl against the released bank.
This gate is deliberately stricter than JSON-schema shape validation: it also checks
source IDs, semantic-review status, difficulty calibration, and duplicate signals.
"""
from __future__ import annotations
import json, re, sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

QB = Path(__file__).resolve().parent
ROOT = QB.parent
CHUNK_FILES = [*(ROOT / f"data-d{i}.js" for i in range(1, 9)), ROOT / "data-ai.js", ROOT / "data-precision.js"]
SEQ_FAIL, SEQ_WARN = 0.90, 0.82
JACCARD_FAIL, JACCARD_WARN = 0.72, 0.60
ALLOWED_TIERS = {"F","E","S","B"}
TIER_RANGES = {"F":(35,49),"E":(50,69),"S":(70,84),"B":(85,100)}
REVIEW_PREFIX = "SEMANTIC_REVIEWED_"

def parse_chunk(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    pre, suf = "window.CISSP_CHUNKS.push(", ");"
    if not (raw.startswith(pre) and raw.endswith(suf)):
        raise ValueError(f"Invalid CISSP chunk wrapper: {path.name}")
    return json.loads(raw[len(pre):-len(suf)])

def load_current():
    chunks = [parse_chunk(p) for p in CHUNK_FILES]
    current = sum((c.get("questions",[]) for c in chunks), [])
    objectives = {o["id"] for c in chunks for o in c.get("objectives",[])}
    cover_raw = (ROOT/"coverage-detail.js").read_text(encoding="utf-8").strip()
    marker = ";\nwindow.CISSP_AI_COVERAGE="
    coverage = json.loads(cover_raw[len("window.CISSP_COVERAGE="):cover_raw.index(marker)])
    subtopics = {x for values in coverage.values() for x in values}
    meta_raw = (ROOT/"data-meta.js").read_text(encoding="utf-8").strip()
    end = meta_raw.index(";window.CISSP_CHUNKS=[];")
    meta = json.loads(meta_raw[len("window.CISSP_META="):end])
    sources = set(meta["sources"])
    return current, objectives, subtopics, sources

def norm(text: str) -> str:
    text = text.lower().replace("’", "'")
    text = re.sub(r"\b(?:mr|ms|mrs|dr)\.?\s+[a-z]+\b", " person ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", " number ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())

def shingles(text: str, n: int=3):
    toks = norm(text).split()
    return ({tuple(toks)} if toks else set()) if len(toks) < n else {tuple(toks[i:i+n]) for i in range(len(toks)-n+1)}

def jaccard(a:set,b:set)->float:
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a & b)/len(a | b)

def load_jsonl(path: Path):
    out=[]
    for lineno,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: obj=json.loads(line)
        except Exception as e: raise ValueError(f"{path}:{lineno}: invalid JSON: {e}") from e
        obj["_source_file"],obj["_source_line"]=str(path),lineno
        out.append(obj)
    return out

def question_text(q:dict)->str:
    if q.get("format","mcq")=="bellringer":
        return f"{q.get('stem','')} {' '.join(map(str,q.get('prompts',[])))}"
    return f"{q.get('stem','')} {' '.join(map(str,q.get('options',[])))}"

def structural_signature(q:dict):
    return (q.get("domain_primary"),tuple(sorted(q.get("objectives",[]))),q.get("scenario_family"),q.get("decision_point"),q.get("correct_rule_id"),tuple(sorted(q.get("misconceptions",[]))))

def validate_released_classification(current:list[dict], errors:list[str]):
    p=QB/"RELEASED_QUESTION_CLASSIFICATION.json"
    if not p.exists():
        errors.append("Released-question classification manifest missing"); return
    m=json.loads(p.read_text(encoding="utf-8")); items=m.get("items",{}); ids={q["id"] for q in current}
    if set(items)!=ids: errors.append("Released-question classification does not exactly cover released question IDs")
    dist=Counter(x.get("difficulty_tier") for x in items.values())
    if dict(m.get("distribution",{})) != {k:dist.get(k,0) for k in ("F","E","S","B")}: errors.append("Released-question classification distribution drift")
    for qid,x in items.items():
        tier=x.get("difficulty_tier"); score=x.get("difficulty_score")
        if tier not in ALLOWED_TIERS or not isinstance(score,int) or not (TIER_RANGES[tier][0] <= score <= TIER_RANGES[tier][1]): errors.append(f"{qid}: invalid released difficulty classification")

def validate_candidate(q, objectives, subtopics, sources, errors, warnings):
    qid=q.get("id","<missing-id>"); fmt=q.get("format","mcq")
    required=["id","format","stem","domain_primary","domains_secondary","objectives","subtopics","difficulty_tier","difficulty_score","scenario_family","decision_point","decision_verb","correct_rule_id","knowledge_atoms","misconceptions","source_ids","originality","review_status"]
    for k in required:
        if k not in q or q[k] in (None,""): errors.append(f"{qid}: missing required field {k}")
    if not isinstance(q.get("objectives"),list) or not q.get("objectives"): errors.append(f"{qid}: objectives must be a non-empty list")
    if not isinstance(q.get("knowledge_atoms"),list) or not q.get("knowledge_atoms"): errors.append(f"{qid}: knowledge_atoms must be a non-empty list")
    if q.get("domain_primary") not in range(1,9): errors.append(f"{qid}: domain_primary must be 1..8")
    bad_obj=[o for o in q.get("objectives",[]) if o not in objectives]
    if bad_obj: errors.append(f"{qid}: unknown objective(s): {bad_obj}")
    unknown_sub=[s for s in q.get("subtopics",[]) if s not in subtopics]
    if unknown_sub: errors.append(f"{qid}: unknown subtopic label(s): {unknown_sub}")
    bad_src=[s for s in q.get("source_ids",[]) if s not in sources]
    if bad_src: errors.append(f"{qid}: unknown source ID(s): {bad_src}")
    if not str(q.get("review_status","")).startswith(REVIEW_PREFIX): errors.append(f"{qid}: candidate lacks semantic-review status")
    tier=q.get("difficulty_tier"); score=q.get("difficulty_score")
    if tier not in ALLOWED_TIERS: errors.append(f"{qid}: invalid difficulty tier")
    elif not isinstance(score,int) or not TIER_RANGES[tier][0] <= score <= TIER_RANGES[tier][1]: errors.append(f"{qid}: difficulty score outside {tier} range")
    orig=q.get("originality",{})
    if orig.get("origin")!="original-from-public-scope" or orig.get("no_external_question_seed") is not True: errors.append(f"{qid}: invalid originality provenance")
    if "sibling_of" not in orig: errors.append(f"{qid}: originality.sibling_of must be explicit")
    if fmt=="mcq":
        opts=q.get("options",[]); rats=q.get("distractor_rationales",[])
        if len(opts)!=4: errors.append(f"{qid}: MCQ must have exactly four options")
        if not isinstance(q.get("answer"),int) or not 0 <= q.get("answer",-1) < 4: errors.append(f"{qid}: answer index must be 0..3")
        if len(rats)!=4 or any(not str(x).strip() for x in rats): errors.append(f"{qid}: four option rationales required")
        if not str(q.get("explanation","")).strip(): errors.append(f"{qid}: explanation required")
        if tier in {"E","S"} and len({norm(str(x)) for x in opts}) != 4: errors.append(f"{qid}: duplicate/near-identical option text")
    elif fmt=="bellringer":
        prompts=q.get("prompts",[])
        if tier!="B": errors.append(f"{qid}: bellringer must use B tier")
        if not 4 <= len(prompts) <= 8: errors.append(f"{qid}: bellringer must have 4..8 prompts")
        if len(set(q.get("domains_secondary",[])) | {q.get("domain_primary")}) < 3: errors.append(f"{qid}: bellringer must span >=3 domains")
        if len(q.get("knowledge_atoms",[])) < 8: errors.append(f"{qid}: bellringer needs >=8 knowledge atoms")
        if not q.get("rubric"): errors.append(f"{qid}: bellringer rubric required")
    else: errors.append(f"{qid}: unknown format {fmt}")

def main(argv:list[str])->int:
    current,objectives,subtopics,sources=load_current(); files=[Path(x) for x in argv[1:]]
    if not files:
        d=QB/"candidates"; files=sorted(d.glob("*.jsonl")) if d.exists() else []
    errors=[]; warnings=[]; validate_released_classification(current,errors)
    if not files:
        if errors: [print("FAIL",e) for e in errors]; return 1
        print(f"PASS baseline released_questions={len(current)} candidates=0"); return 0
    candidates=[q for f in files for q in load_jsonl(f)]; ids=[q.get("id") for q in candidates]
    if len(ids)!=len(set(ids)): errors.append("Candidate IDs duplicated within candidate set")
    for q in candidates: validate_candidate(q,objectives,subtopics,sources,errors,warnings)
    if len(candidates) >= 16:
        dist=Counter(q.get("difficulty_tier") for q in candidates)
        if dist["E"] / len(candidates) < 0.50: errors.append("Candidate set must keep Exam-calibrated items as the majority/center of gravity")
        if dist["B"] / len(candidates) > 0.10: errors.append("Bellringers exceed 10% of candidate set")
    existing=[{"id":q["id"],"text":question_text(q)} for q in current]; accepted=[]; structural_seen={}
    for q in candidates:
        qid=q.get("id","<missing-id>"); text=question_text(q); ntext=norm(text); qsh=shingles(text)
        for other in existing+accepted:
            onorm=norm(other["text"])
            if ntext==onorm: errors.append(f"{qid}: exact normalized duplicate of {other['id']}"); continue
            seq=SequenceMatcher(None,ntext,onorm).ratio(); jac=jaccard(qsh,shingles(other["text"]))
            if seq>=SEQ_FAIL or jac>=JACCARD_FAIL: errors.append(f"{qid}: near-duplicate of {other['id']} (sequence={seq:.3f}, jaccard={jac:.3f})")
            elif seq>=SEQ_WARN or jac>=JACCARD_WARN: warnings.append(f"{qid}: similarity review vs {other['id']} (sequence={seq:.3f}, jaccard={jac:.3f})")
        sig=structural_signature(q); sibling=q.get("originality",{}).get("sibling_of")
        if sig in structural_seen and sibling != structural_seen[sig]: errors.append(f"{qid}: structural duplicate of {structural_seen[sig]}")
        else: structural_seen.setdefault(sig,qid)
        accepted.append({"id":qid,"text":text})
    [print("WARN",w) for w in warnings]
    if errors: [print("FAIL",e) for e in errors]; return 1
    dist=Counter(q.get("difficulty_tier") for q in candidates)
    print(f"PASS released_questions={len(current)} candidates={len(candidates)} F={dist['F']} E={dist['E']} S={dist['S']} B={dist['B']} warnings={len(warnings)}")
    return 0

if __name__=="__main__":
    raise SystemExit(main(sys.argv))
