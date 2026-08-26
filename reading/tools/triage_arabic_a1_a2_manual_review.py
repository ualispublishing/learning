#!/usr/bin/env python3
import json
import re
import subprocess
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "reading" / "audit" / "arabic_a1_a2_manual_review_evidence_2026-08-23.json"
OUTPUT = ROOT / "reading" / "audit" / "arabic_a1_a2_manual_review_triage_2026-08-23.json"
A1 = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
A2 = ROOT / "reading" / "arabic" / "a2" / "passages.jsonl"
EXPECTED = {"a1":"4723cb4c9974a9a9c84b6c030d9c1a30c0820500","a2":"d6a10dddde14628c8e4a7ddb4db7781604852210"}

DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
WORD_RE = re.compile(r"[\u0621-\u064A]+")
PROCLITICS = ("و","ف","ب","ك","ل")
NOMINAL_SUFFIXES = ("هما","هم","هن","كما","كم","كن","نا","ها","ه","ك","ي","ات","ون","ين","ان")
VERB_PREFIXES = ("أ","ن","ي","ت")
VERB_SUFFIXES = ("ون","ين","ان","وا","نا","تم","تن","ن","ت")


def blob(p): return subprocess.check_output(["git","hash-object",str(p)],text=True).strip()
def norm(s):
    s=unicodedata.normalize("NFKC",str(s or "")).replace("ـ","")
    s=DIACRITICS.sub("",s).replace("ٱ","ا")
    return s

def toks(s): return WORD_RE.findall(norm(s))

def nominal_forms(tok):
    out={tok}
    frontier={tok}
    for _ in range(2):
        nxt=set()
        for x in frontier:
            for p in PROCLITICS:
                if x.startswith(p) and len(x)-1>=2: nxt.add(x[1:])
            if x.startswith("ال") and len(x)>4: nxt.add(x[2:])
        out |= nxt; frontier=nxt
    expanded=set(out)
    for x in list(out):
        for suf in NOMINAL_SUFFIXES:
            if x.endswith(suf) and len(x)-len(suf)>=2: expanded.add(x[:-len(suf)])
        # adverbial accusative/orthographic final alif: أولًا -> أولا -> أول
        if x.endswith("ا") and len(x)>3: expanded.add(x[:-1])
    return expanded

def verb_cores(tok):
    base=set(nominal_forms(tok))
    out=set(base)
    for x in list(base):
        if len(x)>=4 and x[0] in VERB_PREFIXES: out.add(x[1:])
    for x in list(out):
        for suf in VERB_SUFFIXES:
            if x.endswith(suf) and len(x)-len(suf)>=3: out.add(x[:-len(suf)])
    return {x for x in out if len(x)>=3}

def nominal_equiv(a,b): return bool(nominal_forms(a)&nominal_forms(b))
def verb_equiv(a,b): return bool(verb_cores(a)&verb_cores(b))

def counts(text, form, is_verb):
    fs=norm(form); exact=nominal=verb=0; matched=[]
    for t in toks(text):
        if t==fs:
            exact+=1; matched.append({"token":t,"kind":"exact"})
        elif nominal_equiv(t,fs):
            nominal+=1; matched.append({"token":t,"kind":"nominal_or_orthographic"})
        elif is_verb and verb_equiv(t,fs):
            verb+=1; matched.append({"token":t,"kind":"verbal_inflection"})
    return {"exact":exact,"nominal_or_orthographic":nominal,"verbal_inflection":verb,"total_supported":exact+nominal+verb,"matched":matched}

def main():
    actual={"a1":blob(A1),"a2":blob(A2)}
    if actual!=EXPECTED: raise SystemExit(f"unexpected blobs {actual}")
    src=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if src.get("packet_count")!=107: raise SystemExit("expected 107 evidence items")
    decisions=[]; classes=Counter(); manual=[]; repairs=[]
    for item in src["items"]:
        pos=str((item.get("target_metadata") or {}).get("part_of_speech") or "").lower()
        is_verb="verb" in pos
        ev=counts(item.get("full_text", ""), item.get("target_form", ""), is_verb)
        code=item.get("warning_code")
        declared=(item.get("target_metadata") or {}).get("declared_exposures_in_text")
        decision={"review_id":item.get("review_id"),"passage_id":item.get("passage_id"),"target_id":item.get("target_id"),"target_form":item.get("target_form"),"part_of_speech":pos,"warning_code":code,"evidence":ev,"declared_exposures":declared}
        if code=="new_target_form_not_exactly_found_in_text":
            if ev["total_supported"]>0 and (not isinstance(declared,int) or ev["total_supported"]==declared):
                decision["decision"]="RESOLVE_VALID_INFLECTION_OR_ORTHOGRAPHY"
                decision["reason"]="Every scheduled new-target exposure is recoverable through exact, conservative orthographic/nominal, or POS-confirmed verbal inflectional realization."
            elif ev["total_supported"]>0:
                decision["decision"]="MANUAL_EXPOSURE_COUNT_CHECK"
                decision["reason"]="A valid realization is present, but the supported count does not equal declared exposures."
                manual.append(decision)
            else:
                decision["decision"]="REPAIR_NEW_TARGET_REALIZATION"
                decision["reason"]="No exact or conservative POS-supported realization of the new target was found."
                manual.append(decision); repairs.append(decision)
        elif code=="running_text_review_target_no_exact_surface":
            if ev["total_supported"]>0:
                decision["decision"]="RESOLVE_VALID_REVIEW_INFLECTION_OR_ORTHOGRAPHY"
                decision["reason"]="The review target is present through an exact/conservative/POS-confirmed inflectional surface realization."
            else:
                decision["decision"]="REPAIR_FALSE_RUNNING_TEXT_REVIEW_METADATA"
                decision["reason"]="The passage declares a running-text review but contains no supported realization of that target. Remove the false declaration first; later review-spacing audit may reschedule it naturally."
                repairs.append(decision)
        elif code=="declared_exposure_count_differs_from_exact_surface_count":
            if isinstance(declared,int) and ev["total_supported"]==declared:
                decision["decision"]="RESOLVE_DECLARED_COUNT_BY_VALID_VARIANTS"
                decision["reason"]="Declared count is exactly recovered by supported surface variants."
            else:
                decision["decision"]="MANUAL_EXPOSURE_COUNT_CHECK"
                decision["reason"]="Supported surface count does not reproduce the declared exposure count."
                manual.append(decision)
        else:
            decision["decision"]="MANUAL_UNKNOWN_WARNING"
            manual.append(decision)
        classes[decision["decision"]]+=1
        decisions.append(decision)
    out={
        "schema_version":1,"date":"2026-08-23","scope":"Arabic A1+A2 conservative manual-review triage","input_blobs":actual,
        "source_count":len(decisions),"decision_counts":dict(classes),"auto_resolved_count":sum(n for k,n in classes.items() if k.startswith("RESOLVE_")),
        "repair_candidate_count":len(repairs),"manual_check_count":len(manual),"repair_candidates":repairs,"manual_checks":manual,"decisions":decisions,
        "guardrail":"No learner-facing text or metadata is changed by this triage. POS-confirmed verbal inflection is only used when part_of_speech explicitly contains verb; all remaining mismatches stay open."
    }
    OUTPUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("source_count","decision_counts","auto_resolved_count","repair_candidate_count","manual_check_count")},ensure_ascii=False))
if __name__=="__main__": main()
