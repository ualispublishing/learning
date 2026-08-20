import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import stanza

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
AUDIT = READING / "audit"
LEVELS = ["a1", "a2", "b1", "b2", "c1", "c2"]
LEVEL_LABEL = {x: x.upper() for x in LEVELS}
STAGES = ["R0", "R1", "R2", "R3", "R4", "R5", "long_term"]
FUNCTION_POS = {"AUX", "ADP", "CCONJ", "SCONJ", "DET", "PRON", "PART"}
TARGET_RE = re.compile(r"^fr-rank-(\d{4})$")
TOKEN_RE = re.compile(r"\w+(?:['’]\w+)?", re.UNICODE)
EXPECTED_HASHES = {
    "a1": "1cdb31ecb8b987c50051bb6f8fa5b2f7fda812cb3004c81ab8697f832fceacba",
    "a2": "8fcd71903e6a495a2abaac8d436232b4b7ee00ae5ac0bce4d273aa4a134b3c15",
    "b1": "7b1013fa606761bc7cc69fdaf67c66a0efcc9c91c478b1c8a5f8523458f9451b",
    "b2": "bfa64c472a93d572d65fbe0217283b9d53bbb0a8d88fee7ea3a3aef1c7993942",
    "c1": "dead8e5d6e6e60a7c6c5185996159670e6077ea2d5da31860de168674050b39a",
    "c2": "c161c4551a6ce0222850778c02ed0662e00bb60e5386d5dc0b4f31a92cb9f277",
}


def norm(s):
    s = unicodedata.normalize("NFC", s or "").replace("’", "'").replace("‘", "'").strip().casefold()
    return re.sub(r"^[^\w]+|[^\w]+$", "", s, flags=re.UNICODE)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def load_lexicon():
    rows = load_jsonl(READING / "lexicons" / "french.jsonl")
    by_id = {r["id"]: r for r in rows}
    by_form = {}
    for r in rows:
        for candidate in {r.get("form"), r.get("match_form")}:
            k = norm(candidate)
            if k:
                old = by_form.get(k)
                if old is None or r["rank"] < old["rank"]:
                    by_form[k] = r
    return rows, by_id, by_form


def load_support():
    data = json.loads((READING / "lexicons" / "french_a1_support.json").read_text(encoding="utf-8"))
    forms = {}
    for item in data.get("items", []):
        if not item.get("verified"):
            continue
        for form in [item.get("lemma"), *item.get("forms", [])]:
            k = norm(form)
            if k:
                forms[k] = item
    return data, forms


def rank_match(word, lex_by_form):
    candidates = [norm(word.lemma), norm(word.text)]
    matches = [lex_by_form[x] for x in candidates if x and x in lex_by_form]
    return min(matches, key=lambda r: r["rank"]) if matches else None


def target_keys(target, lex_by_id):
    keys = {norm(target.get("form")), norm(target.get("lemma"))}
    lex = lex_by_id.get(target.get("id"))
    if lex:
        keys |= {norm(lex.get("form")), norm(lex.get("match_form"))}
    return {x for x in keys if x}


def stage_max(a, b):
    if b not in STAGES:
        return a
    return b if STAGES.index(b) > STAGES.index(a) else a


def main():
    AUDIT.mkdir(parents=True, exist_ok=True)
    canonical_hashes = {}
    passages = []
    for level in LEVELS:
        path = READING / "french" / level / "passages.jsonl"
        got = sha256(path)
        canonical_hashes[level] = got
        if got != EXPECTED_HASHES[level]:
            raise SystemExit(f"canonical hash drift for {level}: expected {EXPECTED_HASHES[level]}, got {got}")
        rows = load_jsonl(path)
        if len(rows) != 60:
            raise SystemExit(f"{level}: expected 60 passages, got {len(rows)}")
        seqs = [r["sequence"] for r in rows]
        if seqs != list(range(1, 61)):
            raise SystemExit(f"{level}: non-contiguous sequence")
        passages.extend((level, r) for r in rows)

    lex_rows, lex_by_id, lex_by_form = load_lexicon()
    support_data, support_forms = load_support()
    if len(lex_rows) != 3000:
        raise SystemExit(f"French lexicon expected 3000 rows, got {len(lex_rows)}")

    # Pass 1: validate declared target chronology and construct planned exposure events.
    introduced = {}
    target_state = {}
    chronology_findings = []
    per_passage_pre_six_contact = {}
    global_index = 0

    def ensure_state(tid, target=None):
        if tid not in target_state:
            target_state[tid] = {
                "target_id": tid,
                "source_rank": None,
                "lemma": target.get("lemma") if target else None,
                "form": target.get("form") if target else None,
                "introduced_in": None,
                "introduced_global_index": None,
                "planned_meaningful_contacts": 0,
                "textual_introduction_exposures": 0,
                "review_events": 0,
                "question_target_contacts": 0,
                "highest_review_stage": "R0",
                "last_contact_passage": None,
                "review_history": [],
            }
        return target_state[tid]

    for level, p in passages:
        global_index += 1
        pid = p["id"]
        per_passage_pre_six_contact[pid] = {
            tid for tid, st in target_state.items()
            if st["introduced_in"] and st["planned_meaningful_contacts"] >= 6
        }
        for t in p.get("new_lexical_targets", []):
            tid = t.get("id")
            m = TARGET_RE.fullmatch(tid or "")
            if not m:
                chronology_findings.append({"severity": "major", "passage_id": pid, "kind": "invalid_new_target_id", "target_id": tid})
                continue
            rank = int(m.group(1))
            lex = lex_by_id.get(tid)
            if lex is None:
                chronology_findings.append({"severity": "major", "passage_id": pid, "kind": "new_target_missing_from_lexicon", "target_id": tid})
                continue
            if t.get("source_rank") != rank or lex.get("rank") != rank:
                chronology_findings.append({"severity": "major", "passage_id": pid, "kind": "new_target_rank_mismatch", "target_id": tid, "declared": t.get("source_rank"), "lexicon": lex.get("rank")})
            if tid in introduced:
                chronology_findings.append({"severity": "major", "passage_id": pid, "kind": "duplicate_first_introduction", "target_id": tid, "first": introduced[tid]})
            else:
                introduced[tid] = pid
            st = ensure_state(tid, t)
            st["source_rank"] = rank
            st["lemma"] = t.get("lemma")
            st["form"] = t.get("form")
            if st["introduced_in"] is None:
                st["introduced_in"] = pid
                st["introduced_global_index"] = global_index
            exp = max(1, int(t.get("exposures_in_text") or 1))
            st["textual_introduction_exposures"] += exp
            st["planned_meaningful_contacts"] += exp
            st["last_contact_passage"] = pid
        for r in p.get("review_lexical_targets", []):
            tid = r.get("id")
            st = ensure_state(tid, r)
            if tid not in introduced:
                chronology_findings.append({"severity": "major", "passage_id": pid, "kind": "review_before_declared_introduction", "target_id": tid, "review_stage": r.get("review_stage")})
            stage = r.get("review_stage")
            if stage not in STAGES:
                chronology_findings.append({"severity": "major", "passage_id": pid, "kind": "invalid_review_stage", "target_id": tid, "review_stage": stage})
            elif STAGES.index(stage) < STAGES.index(st["highest_review_stage"]):
                chronology_findings.append({"severity": "minor", "passage_id": pid, "kind": "review_stage_regression", "target_id": tid, "prior": st["highest_review_stage"], "current": stage})
            st["highest_review_stage"] = stage_max(st["highest_review_stage"], stage)
            st["review_events"] += 1
            st["planned_meaningful_contacts"] += 1
            st["last_contact_passage"] = pid
            st["review_history"].append({"passage_id": pid, "stage": stage, "representation": r.get("representation")})
        for q in p.get("questions", []):
            for tid in q.get("target_ids", []):
                st = ensure_state(tid)
                if tid not in introduced:
                    chronology_findings.append({"severity": "minor", "passage_id": pid, "kind": "question_target_before_declared_introduction", "target_id": tid, "question_id": q.get("id")})
                st["question_target_contacts"] += 1
                st["planned_meaningful_contacts"] += 1
                st["last_contact_passage"] = pid

    # NLP pass. Downloaded model is deterministic evidence tooling, not a release authority.
    stanza.download("fr", processors="tokenize,pos,lemma", verbose=False)
    nlp = stanza.Pipeline("fr", processors="tokenize,pos,lemma", use_gpu=False, verbose=False)

    per_passage = []
    unresolved_global = Counter()
    classification_global = Counter()
    support_hits = Counter()
    six_contact_token_hits = 0
    total_counted = 0
    thresholds = {
        "instructional": 0.03,
        "reinforcement": 0.03,
        "transfer": 0.03,
        "interleaved": 0.03,
        "integration": 0.03,
        "paired": 0.03,
        "stretch": 0.05,
        "checkpoint": 0.015,
        "fluency": 0.015,
    }

    # Map target IDs to all normalized keys once.
    tid_keys = {}
    for level, p in passages:
        for t in p.get("new_lexical_targets", []):
            tid_keys.setdefault(t["id"], set()).update(target_keys(t, lex_by_id))
        for r in p.get("review_lexical_targets", []):
            tid_keys.setdefault(r["id"], set()).add(norm(r.get("form")))

    for level, p in passages:
        pid = p["id"]
        current_new_ids = {x["id"] for x in p.get("new_lexical_targets", [])}
        current_review_ids = {x["id"] for x in p.get("review_lexical_targets", [])}
        pre_six_ids = per_passage_pre_six_contact[pid]
        new_keys = {k for tid in current_new_ids for k in tid_keys.get(tid, set()) if k}
        review_keys = {k for tid in current_review_ids for k in tid_keys.get(tid, set()) if k}
        stable_keys = {k for tid in pre_six_ids for k in tid_keys.get(tid, set()) if k}

        doc = nlp(p["text"])
        counts = Counter()
        unresolved = Counter()
        token_rows = []
        for sent in doc.sentences:
            for w in sent.words:
                if w.upos in {"PUNCT", "SYM", "X"}:
                    continue
                surface = norm(w.text)
                lemma = norm(w.lemma)
                if not surface:
                    continue
                keys = {surface, lemma} - {""}
                lex = rank_match(w, lex_by_form)
                if w.upos in {"PROPN", "NUM"}:
                    category = "situational_proper_or_number"
                elif w.upos in FUNCTION_POS:
                    category = "grammar_function_support"
                elif any(k in new_keys for k in keys):
                    category = "controlled_new_target"
                elif any(k in review_keys for k in keys):
                    category = "scheduled_review_target"
                elif any(k in stable_keys for k in keys):
                    category = "prior_six_contact_curriculum_proxy"
                    six_contact_token_hits += 1
                elif level == "a1" and any(k in support_forms for k in keys):
                    category = "verified_pedagogical_support"
                    for k in keys:
                        if k in support_forms:
                            support_hits[support_forms[k]["id"]] += 1
                            break
                elif lex is not None:
                    category = "ranked_backbone"
                else:
                    category = "uncontrolled_unknown_candidate"
                    unresolved[f"{w.text} | lemma={w.lemma} | upos={w.upos}"] += 1
                    unresolved_global[f"{lemma or surface} | upos={w.upos}"] += 1
                counts[category] += 1
                classification_global[category] += 1
                total_counted += 1
                token_rows.append({
                    "surface": w.text,
                    "lemma": w.lemma,
                    "upos": w.upos,
                    "category": category,
                    "rank": lex.get("rank") if lex else None,
                })
        n = sum(counts.values())
        ranked_inventory = sum(v for k, v in counts.items() if k != "uncontrolled_unknown_candidate") / n if n else 0
        supported = ranked_inventory
        uncontrolled = counts["uncontrolled_unknown_candidate"] / n if n else 0
        # Deliberately conservative proxy: this is NOT learner mastery. It counts only
        # grammar/function + situational names/numbers + targets with >=6 prior planned
        # contacts. It exists to expose the evidence gap, not to populate canonical data.
        conservative_proxy = (
            counts["grammar_function_support"]
            + counts["situational_proper_or_number"]
            + counts["prior_six_contact_curriculum_proxy"]
        ) / n if n else 0
        threshold = thresholds.get(p["passage_type"], 0.03)
        per_passage.append({
            "id": pid,
            "level": LEVEL_LABEL[level],
            "sequence": p["sequence"],
            "passage_type": p["passage_type"],
            "counted_tokens": n,
            "stored_estimated_known_token_coverage": p.get("estimated_known_token_coverage"),
            "classification_counts": dict(counts),
            "ranked_or_other_supported_coverage": round(ranked_inventory, 6),
            "supported_coverage": round(supported, 6),
            "uncontrolled_unknown_candidate_rate": round(uncontrolled, 6),
            "uncontrolled_unknown_candidate_threshold": threshold,
            "support_gate": "PASS" if uncontrolled <= threshold else "REVIEW_REQUIRED",
            "conservative_prior_six_contact_proxy": round(conservative_proxy, 6),
            "current_new_target_ids": sorted(current_new_ids),
            "current_review_target_ids": sorted(current_review_ids),
            "pre_passage_six_contact_target_count": len(pre_six_ids),
            "top_uncontrolled_unknown_candidates": unresolved.most_common(25),
        })

    target_rows = []
    for tid, st in sorted(target_state.items(), key=lambda kv: (kv[1].get("source_rank") or 999999, kv[0])):
        row = dict(st)
        row["six_planned_contacts_reached"] = st["planned_meaningful_contacts"] >= 6
        row["actual_success_evidence_available"] = False
        row["mastery_claim_allowed"] = False
        target_rows.append(row)

    # Summaries useful for manual follow-up and methodology decisions.
    level_summary = {}
    for level in LEVELS:
        rows = [x for x in per_passage if x["level"] == LEVEL_LABEL[level]]
        level_summary[LEVEL_LABEL[level]] = {
            "passages": len(rows),
            "mean_supported_coverage": round(sum(x["supported_coverage"] for x in rows) / len(rows), 6),
            "min_supported_coverage": min(x["supported_coverage"] for x in rows),
            "max_uncontrolled_unknown_candidate_rate": max(x["uncontrolled_unknown_candidate_rate"] for x in rows),
            "support_gate_passages": sum(x["support_gate"] == "PASS" for x in rows),
            "support_gate_review_required": sum(x["support_gate"] != "PASS" for x in rows),
            "mean_conservative_prior_six_contact_proxy": round(sum(x["conservative_prior_six_contact_proxy"] for x in rows) / len(rows), 6),
        }

    method = {
        "purpose": "Non-mutating French coverage evidence audit after educator repairs.",
        "canonical_field_policy": "Do not populate estimated_known_token_coverage from this audit alone.",
        "why": [
            "LEXICAL_COVERAGE_POLICY distinguishes curriculum support from actual individual learner mastery.",
            "READING_PASSAGE_STANDARD says stable curriculum knowledge normally requires at least six meaningful contacts and successful reinforcement evidence.",
            "The static corpus records planned review opportunities but contains no per-learner retrieval-success telemetry or validated starting-vocabulary profile.",
            "Therefore supported coverage and a six-contact curriculum proxy can be audited, but neither is proof of actual learner-known coverage."
        ],
        "nlp": "Stanza French tokenize,pos,lemma; standard GitHub-hosted runner; deterministic diagnostic only.",
        "classification_priority": [
            "situational_proper_or_number",
            "grammar_function_support",
            "controlled_new_target",
            "scheduled_review_target",
            "prior_six_contact_curriculum_proxy",
            "verified_pedagogical_support (A1 verified support lexicon only)",
            "ranked_backbone",
            "uncontrolled_unknown_candidate"
        ],
        "six_contact_proxy": "A target enters the prior-six-contact proxy only after >=6 declared/planned meaningful contacts before the passage. Question target references are retrieval opportunities, not assumed successes.",
        "support_gate": "Passage-type diagnostic based on uncontrolled unknown candidate rate; this is not educator release approval.",
        "known_coverage_field_population_decision": "BLOCKED_PENDING_SEMANTIC_DEFINITION_OR_TELEMETRY_BASELINE",
    }

    chronology_counts = Counter(x["kind"] for x in chronology_findings)
    evidence = {
        "schema_version": 1,
        "date": "2026-08-19",
        "language": "fr",
        "status": "EVIDENCE_ONLY_DO_NOT_AUTOPROMOTE",
        "bound_canonical_hashes": {LEVEL_LABEL[k]: v for k, v in canonical_hashes.items()},
        "method": method,
        "corpus": {
            "passages": len(passages),
            "questions": sum(len(p.get("questions", [])) for _, p in passages),
            "answers": sum(len(p.get("answer_key", [])) for _, p in passages),
            "counted_nlp_tokens": total_counted,
        },
        "target_ledger_summary": {
            "declared_target_ids_seen": len(target_rows),
            "targets_reaching_six_planned_contacts": sum(x["six_planned_contacts_reached"] for x in target_rows),
            "targets_with_actual_success_evidence": 0,
            "chronology_finding_count": len(chronology_findings),
            "chronology_finding_kinds": dict(chronology_counts),
        },
        "coverage_summary_by_level": level_summary,
        "classification_counts": dict(classification_global),
        "verified_a1_support_hits": dict(support_hits),
        "top_uncontrolled_unknown_candidates": unresolved_global.most_common(150),
        "chronology_findings": chronology_findings,
        "passages": per_passage,
        "decision": {
            "may_bulk_set_estimated_known_token_coverage": False,
            "may_bulk_set_quality_coverage_check_pass": False,
            "reason": "This run establishes support/chronology evidence but cannot infer actual learner mastery; unresolved token candidates and target chronology findings require adjudication before any coverage PASS.",
            "next_actions": [
                "adjudicate all target chronology findings",
                "adjudicate uncontrolled unknown candidates, beginning with highest-frequency types and passages exceeding the diagnostic threshold",
                "decide/document a pre-telemetry semantic contract for estimated_known_token_coverage or allow an explicit unavailable/null state",
                "rerun this audit after adjudication",
                "only then issue record-level coverage evidence and update quality.coverage_check where substantively justified"
            ]
        }
    }
    ledger = {
        "schema_version": 1,
        "date": "2026-08-19",
        "language": "fr",
        "learner_success_assumed": False,
        "mastery_claim_allowed": False,
        "bound_canonical_hashes": {LEVEL_LABEL[k]: v for k, v in canonical_hashes.items()},
        "targets": target_rows,
    }

    (AUDIT / "french_curriculum_exposure_ledger_2026-08-19.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (AUDIT / "french_coverage_evidence_2026-08-19.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": evidence["status"],
        "corpus": evidence["corpus"],
        "target_ledger_summary": evidence["target_ledger_summary"],
        "coverage_summary_by_level": level_summary,
        "top_uncontrolled_unknown_candidates": evidence["top_uncontrolled_unknown_candidates"][:25],
        "decision": evidence["decision"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
