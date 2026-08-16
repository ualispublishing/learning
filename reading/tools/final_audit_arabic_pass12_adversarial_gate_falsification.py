#!/usr/bin/env python3
"""Final Arabic review pass 12: adversarial cross-gate falsification.

Pass 12 is the final fail-closed approval gate. It runs only after the upstream
suite has been freshly regenerated. It distrusts status strings enough to
recheck high-value corpus invariants directly and derives blockers from current
artifacts rather than historical prose.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
OUT = ROOT / "reading/audit/final_arabic_pass12_adversarial_gate_falsification.json"
ART = {
    "pass01": "reading/audit/final_arabic_pass01_data_integrity.json",
    "pass02": "reading/audit/final_arabic_pass02_lexical_exposure_integrity.json",
    "pass03": "reading/audit/final_arabic_pass03_question_composition.json",
    "pass04": "reading/audit/final_arabic_pass04_answer_evidence_alignment.json",
    "pass05": "reading/audit/final_arabic_pass05_script_orthography_hygiene.json",
    "pass06": "reading/audit/final_arabic_pass06_lexical_source_identity.json",
    "pass07": "reading/audit/final_arabic_pass07_cefr_difficulty_calibration.json",
    "pass08": "reading/audit/final_arabic_pass08_continuity_duplicate_balance.json",
    "pass09": "reading/audit/final_arabic_pass09_fluency_checkpoint.json",
    "pass10_raw": "reading/audit/final_arabic_pass10_lexical_sense_alignment.json",
    "pass10_adjudication": "reading/audit/final_arabic_pass10_adjudication.json",
    "pass11": "reading/audit/final_arabic_pass11_naturalness_review.json",
}
LATIN = re.compile(r"[A-Za-z]")
BANNED_IDS = {"ar-r800", "ar-r913", "ar-r998", "ar-r986", "ar-r2063"}
BANDS = {
    "a1": (90, 140),
    "a2": (140, 220),
    "b1": (220, 350),
    "b2": (350, 550),
    "c1": (500, 800),
    "c2": (700, 1200),
}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def word_count(text: object) -> int:
    return len(str(text or "").split())


def declared_target_ids(row: dict) -> set[str]:
    out: set[str] = set()
    for field in ("new_lexical_targets", "review_lexical_targets"):
        for item in row.get(field, []):
            if isinstance(item, dict) and item.get("id"):
                out.add(str(item["id"]))
    return out


def add(items: list[dict], code: str, **fields: object) -> None:
    items.append({"code": code, **fields})


def main() -> None:
    hard: list[dict] = []
    blockers: list[dict] = []
    evidence = {key: load(path) for key, path in ART.items()}

    # Upstream artifact contract. Pass 10 is handled separately because its raw
    # detector intentionally leaves source-gloss candidates for adjudication.
    for key in ("pass01", "pass02", "pass03", "pass04", "pass05", "pass06", "pass07", "pass08", "pass09"):
        actual = evidence[key].get("status")
        if actual != "PASS":
            add(blockers, "upstream_gate_not_pass", gate=key, status=actual, totals=evidence[key].get("totals"))

    p2 = evidence["pass02"]
    undeclared_warning_hits = [
        warning for warning in p2.get("warnings", [])
        if isinstance(warning, dict) and warning.get("code") == "question_target_not_declared_in_passage_targets"
    ]
    if undeclared_warning_hits:
        add(hard, "pass02_undeclared_question_targets_reappeared", hits=undeclared_warning_hits)

    p4 = evidence["pass04"]
    p4tot = p4.get("totals", {})
    if p4tot.get("review_flags") != 0 or p4tot.get("unresolved_review_flags") != 0:
        add(blockers, "pass04_unresolved_answer_evidence_candidates", totals=p4tot)
    if p4tot.get("stale_adjudications") != 0:
        add(hard, "pass04_stale_adjudications", keys=p4.get("stale_adjudication_keys", []), totals=p4tot)

    p7 = evidence["pass07"]
    if p7.get("totals", {}).get("review_flags") != 0:
        add(blockers, "pass07_actionable_flags_remain", totals=p7.get("totals"))

    # Pass 10: all current raw candidates must be exactly covered by current
    # source adjudications; the one historically repaired item must stay absent.
    raw10 = evidence["pass10_raw"]
    adj10 = evidence["pass10_adjudication"]
    if adj10.get("status") != "PASS_WITH_SOURCE_ADJUDICATION" or adj10.get("unresolved"):
        add(blockers, "pass10_adjudication_not_closed", status=adj10.get("status"), unresolved=adj10.get("unresolved"))
    raw10_keys = {
        (str(item.get("passage_id")), str(item.get("target_id")))
        for item in raw10.get("flags", []) if isinstance(item, dict)
    }
    active_adj = adj10.get("current_raw_adjudications", [])
    adj10_keys = {
        (str(item.get("passage_id")), str(item.get("target_id")))
        for item in active_adj if isinstance(item, dict)
    }
    if raw10_keys != adj10_keys:
        add(hard, "pass10_raw_adjudication_key_drift", raw_only=sorted(raw10_keys - adj10_keys), adjudication_only=sorted(adj10_keys - raw10_keys))
    if raw10.get("totals", {}).get("review_flags") != len(raw10_keys) or adj10.get("current_raw_flag_count") != len(raw10_keys):
        add(hard, "pass10_raw_adjudication_count_drift", raw_totals=raw10.get("totals"), ledger_count=adj10.get("current_raw_flag_count"), unique_keys=len(raw10_keys))
    historical10 = adj10.get("historical_resolved_after_canonical_repair", [])
    if len(historical10) != 1:
        add(hard, "pass10_historical_repair_ledger_drift", historical=historical10)
    else:
        item = historical10[0]
        hist_key = (str(item.get("passage_id")), str(item.get("target_id")))
        if item.get("decision") != "ACCEPT_AFTER_CANONICAL_REPAIR" or item.get("current_raw_detector_state") != "NO_LONGER_FLAGGED":
            add(hard, "pass10_historical_repair_state_invalid", entry=item)
        if hist_key in raw10_keys:
            add(hard, "pass10_repaired_item_reappeared", key=hist_key)

    # Pass 11 uses COMPLETE as the documented manual-review completion state.
    p11 = evidence["pass11"]
    t11 = p11.get("totals", {})
    reviewed11 = t11.get("passages_fully_reviewed_in_completed_levels", t11.get("passages_fully_reviewed"))
    if p11.get("status") not in {"PASS", "COMPLETE"} or t11.get("levels_pending") != 0 or t11.get("levels_complete") != 6 or reviewed11 != 360:
        add(blockers, "pass11_manual_naturalness_incomplete", status=p11.get("status"), totals=t11, reviewed=reviewed11)

    # Direct corpus falsification.
    rows: list[dict] = []
    seen_ids: set[str] = set()
    level_direct: dict[str, dict] = {}
    latin_hits: list[dict] = []
    banned_hits: list[dict] = []
    p6_bad: list[dict] = []
    linkage_bad: list[dict] = []
    question_target_bad: list[dict] = []
    word_band_bad: list[dict] = []
    stored_word_count_bad: list[dict] = []

    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        level_rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows.extend(level_rows)
        sequences = [int(row.get("sequence", -1)) for row in level_rows]
        lo, hi = BANDS[level]

        if len(level_rows) != 60:
            add(hard, "direct_level_count_changed", level=level, actual=len(level_rows), expected=60)
        if sorted(sequences) != list(range(1, 61)):
            add(hard, "direct_level_sequence_set_changed", level=level, sequences=sorted(sequences))

        level_direct[level] = {
            "passages": len(level_rows),
            "sequence_min": min(sequences) if sequences else None,
            "sequence_max": max(sequences) if sequences else None,
            "word_band": [lo, hi],
            "min_actual_words": min((word_count(r.get("text")) for r in level_rows), default=None),
            "max_actual_words": max((word_count(r.get("text")) for r in level_rows), default=None),
        }

        for row in level_rows:
            pid = str(row.get("id"))
            if pid in seen_ids:
                add(hard, "direct_duplicate_id", passage_id=pid)
            seen_ids.add(pid)

            actual_wc = word_count(row.get("text"))
            if not lo <= actual_wc <= hi:
                word_band_bad.append({"passage_id": pid, "level": level, "actual": actual_wc, "band": [lo, hi]})
            if row.get("word_count") != actual_wc:
                stored_word_count_bad.append({"passage_id": pid, "stored": row.get("word_count"), "actual": actual_wc})

            reader_fields = [("title", row.get("title", "")), ("text", row.get("text", ""))]
            reader_fields += [(f"question:{q.get('id')}", q.get("prompt", "")) for q in row.get("questions", []) if isinstance(q, dict)]
            reader_fields += [(f"answer:{a.get('question_id')}", a.get("answer", "")) for a in row.get("answer_key", []) if isinstance(a, dict)]
            for where, value in reader_fields:
                if LATIN.search(str(value or "")):
                    latin_hits.append({"passage_id": pid, "where": where})

            questions = [q for q in row.get("questions", []) if isinstance(q, dict)]
            answers = [a for a in row.get("answer_key", []) if isinstance(a, dict)]
            qids = [str(q.get("id")) for q in questions]
            answer_qids = [str(a.get("question_id")) for a in answers]
            if len(questions) != 10 or len(answers) != 10 or len(set(qids)) != 10 or len(set(answer_qids)) != 10 or set(qids) != set(answer_qids):
                linkage_bad.append({
                    "passage_id": pid,
                    "questions": len(questions),
                    "answers": len(answers),
                    "unique_question_ids": len(set(qids)),
                    "unique_answer_question_ids": len(set(answer_qids)),
                    "question_only": sorted(set(qids) - set(answer_qids)),
                    "answer_only": sorted(set(answer_qids) - set(qids)),
                })

            local_targets = declared_target_ids(row)
            for q in questions:
                for tid in q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []:
                    tid = str(tid)
                    if tid and tid not in local_targets:
                        question_target_bad.append({"passage_id": pid, "question_id": q.get("id"), "target_id": tid})
                    if tid in BANNED_IDS:
                        banned_hits.append({"passage_id": pid, "where": "question", "question_id": q.get("id"), "target_id": tid})

            for target in [*row.get("new_lexical_targets", []), *row.get("review_lexical_targets", [])]:
                if isinstance(target, dict) and str(target.get("id")) in BANNED_IDS:
                    banned_hits.append({"passage_id": pid, "where": "lexical", "target_id": target.get("id")})

            if pid.endswith("-p06") and row.get("new_lexical_targets"):
                p6_bad.append({"passage_id": pid, "target_ids": [t.get("id") for t in row.get("new_lexical_targets", []) if isinstance(t, dict)]})

    if len(rows) != 360:
        add(hard, "direct_total_passage_count_changed", actual=len(rows), expected=360)
    if len(seen_ids) != 360:
        add(hard, "direct_unique_id_count_changed", actual=len(seen_ids), expected=360)
    if latin_hits:
        add(hard, "latin_reader_content_reappeared", hits=latin_hits)
    if banned_hits:
        add(hard, "known_bad_lexical_ids_reappeared", hits=banned_hits)
    if p6_bad:
        add(hard, "p6_new_targets_reappeared", hits=p6_bad)
    if linkage_bad:
        add(hard, "question_answer_linkage_regression", hits=linkage_bad)
    if question_target_bad:
        add(hard, "question_target_not_locally_declared", hits=question_target_bad)
    if word_band_bad:
        add(hard, "direct_word_band_regression", hits=word_band_bad)
    if stored_word_count_bad:
        add(hard, "stored_word_count_drift", hits=stored_word_count_bad)

    hard_codes = Counter(str(item.get("code")) for item in hard)
    blocker_codes = Counter(str(item.get("code")) for item in blockers)
    status = "FAIL_REGRESSION" if hard else ("BLOCKED" if blockers else "PASS")
    final_approval = status == "PASS"

    payload = {
        "pass": 12,
        "name": "adversarial_cross_gate_falsification",
        "scope": "Arabic A1-C2 canonical reading corpus",
        "method": "fresh upstream artifact validation plus independent direct corpus rechecks; approval is denied on any hard regression or unresolved substantive gate",
        "upstream_statuses": {key: value.get("status") for key, value in evidence.items()},
        "direct_checks": {
            "passages": len(rows),
            "unique_ids": len(seen_ids),
            "levels": level_direct,
            "latin_reader_hits": len(latin_hits),
            "known_bad_id_hits": len(banned_hits),
            "p6_with_new_targets": len(p6_bad),
            "question_answer_linkage_failures": len(linkage_bad),
            "undeclared_question_target_hits": len(question_target_bad),
            "word_band_failures": len(word_band_bad),
            "stored_word_count_failures": len(stored_word_count_bad),
        },
        "pass04_adjudication": {
            "manual_adjudications_applied": p4tot.get("manual_adjudications_applied"),
            "stale_adjudications": p4tot.get("stale_adjudications"),
            "unresolved_review_flags": p4tot.get("unresolved_review_flags"),
        },
        "pass10_adjudication": {
            "raw_flag_count": len(raw10_keys),
            "current_adjudication_count": len(adj10_keys),
            "historical_repaired_count": len(historical10),
            "status": adj10.get("status"),
        },
        "pass11_manual_review": {
            "status": p11.get("status"),
            "levels_complete": t11.get("levels_complete"),
            "levels_pending": t11.get("levels_pending"),
            "passages_reviewed": reviewed11,
        },
        "coverage_note": {
            "status": "UNMEASURED_NOT_FAILURE",
            "interpretation": "estimated_known_token_coverage zeros are unmeasured placeholders; Pass 12 does not fabricate coverage percentages or interpret them as measured 0%",
        },
        "hard_regression_counts": dict(hard_codes),
        "blocker_counts": dict(blocker_codes),
        "hard_regressions": hard,
        "final_approval_blockers": blockers,
        "status": status,
        "final_approval": final_approval,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "hard_regressions": len(hard),
        "blockers": len(blockers),
        "status": status,
        "final_approval": final_approval,
    }, ensure_ascii=False))
    print("status=" + status)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
