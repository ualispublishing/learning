import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reading" / "audit" / "arabic_a1_a2_metalinguistic_candidate_audit_2026-08-20.json"
LEVELS = ["a1", "a2"]
FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}
PROMPT_PATTERNS = [
    ("explicit_grammar_classification", re.compile(r"التصنيف\s+النحوي|التصنيف\s+الصرفي|ما\s+نوع\s+كلمة|ما\s+نوع\s+«|ما\s+نوع\s+\"")),
    ("explicit_grammar_function", re.compile(r"الوظيفة\s+النحوية|ما\s+وظيفة\s+كلمة|ما\s+وظيفة\s+«|ما\s+الدور\s+النحوي")),
    ("explicit_pos_term_request", re.compile(r"هل\s+هي\s+(اسم|فعل|صفة|ضمير|حرف)|أي\s+من\s+(الأسماء|الأفعال|الصفات|الضمائر|الحروف)")),
]
ANSWER_LABEL_RE = re.compile(r"\b(اسم|فعل|صفة|ضمير|حرف|ظرف|جار\s+ومجرور|مفعول|فاعل|مبتدأ|خبر|اسم\s+إشارة|اسم\s+موصول)\b")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    findings=[]
    type_counts=Counter()
    level_counts=defaultdict(Counter)
    hashes={}
    records=questions=answers=0
    for level in LEVELS:
        path=ROOT/"reading"/"arabic"/level/"passages.jsonl"
        hashes[level.upper()]=sha256(path)
        rows=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        records += len(rows)
        for p in rows:
            amap={a.get("id"):a for a in p.get("answer_key",[])}
            questions += len(p.get("questions",[])); answers += len(p.get("answer_key",[]))
            for q in p.get("questions",[]):
                qtype=q.get("type")
                type_counts[qtype]+=1; level_counts[level.upper()][qtype]+=1
                prompt=q.get("prompt") or ""
                ans=amap.get(q.get("answer_id"),{}).get("answer") or ""
                reasons=[]
                if qtype in FORMAL_TYPES:
                    reasons.append("formal_question_type")
                for name,pat in PROMPT_PATTERNS:
                    if pat.search(prompt): reasons.append(name)
                # POS terminology in the key matters only when prompt also asks for linguistic classification/function,
                # or the formal type itself already establishes a metalinguistic task.
                answer_has_label=bool(ANSWER_LABEL_RE.search(ans))
                if reasons and answer_has_label:
                    reasons.append("answer_requires_or_uses_grammar_label")
                if reasons:
                    findings.append({
                        "language":"ar","level":level.upper(),"passage_id":p["id"],"sequence":p["sequence"],
                        "question_id":q.get("id"),"question_type":qtype,"prompt":prompt,"answer":ans,
                        "reasons":sorted(set(reasons)),
                        "severity_candidate":"major" if (qtype in FORMAL_TYPES or any(r.startswith("explicit_") for r in reasons)) else "minor",
                        "status":"NEEDS_EDUCATOR_ADJUDICATION",
                        "note":"Candidate only. Communicative grammar-choice/use tasks are not flagged merely for testing grammar."
                    })
    by_level=Counter(f["level"] for f in findings)
    by_type=Counter(f["question_type"] for f in findings)
    by_reason=Counter(r for f in findings for r in f["reasons"])
    out={
        "schema_version":1,"date":"2026-08-20","language":"ar","levels":["A1","A2"],
        "status":"CANDIDATE_AUDIT_DO_NOT_AUTOREPAIR",
        "bound_canonical_hashes":hashes,
        "scope":{"records":records,"questions":questions,"answers":answers},
        "method":{
            "formal_types_flagged":sorted(FORMAL_TYPES),
            "prompt_pattern_classes":[x[0] for x in PROMPT_PATTERNS],
            "exclusion":"grammar_choice and other communicative use tasks are not flagged unless their wording independently matches explicit metalinguistic patterns",
            "purpose":"Find low-level assessment tasks that may test formal grammatical labeling rather than reading comprehension/use. Every candidate requires educator adjudication before repair."
        },
        "question_type_counts":dict(type_counts),
        "question_type_counts_by_level":{k:dict(v) for k,v in level_counts.items()},
        "candidate_summary":{"count":len(findings),"by_level":dict(by_level),"by_question_type":dict(by_type),"by_reason":dict(by_reason)},
        "findings":findings,
        "release_effect":"Arabic remains blocked. This artifact alone neither repairs nor approves any record."
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"scope":out["scope"],"candidate_summary":out["candidate_summary"]},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
