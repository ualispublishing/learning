import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "french" / "a1" / "passages.jsonl"
LEX = ROOT / "reading" / "lexicons" / "french.jsonl"
OUT = ROOT / "reading" / "audit" / "french_a1_review_integrity_postrepair_2026-08-20.json"
EXPECTED_SHA256 = "714cf8d41df917d2deb745f1cd9e82586a75f59cdaa4bff2eb494144a5345037"
STAGE_ORDER = {"R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "long_term": 6}


def norm(s):
    s = unicodedata.normalize("NFC", str(s or "")).replace("’", "'").replace("‘", "'").casefold().strip()
    return re.sub(r"^[^\w]+|[^\w]+$", "", s, flags=re.UNICODE)


def main():
    bound = hashlib.sha256(PATH.read_bytes()).hexdigest()
    if bound != EXPECTED_SHA256:
        raise SystemExit(f"French A1 hash drift: expected {EXPECTED_SHA256}, got {bound}")
    rows = [json.loads(x) for x in PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    lex = {r["id"]: r for r in [json.loads(x) for x in LEX.read_text(encoding="utf-8").splitlines() if x.strip()]}
    if len(rows) != 60 or [r.get("sequence") for r in rows] != list(range(1, 61)):
        raise SystemExit("French A1 structural precondition failed")

    visibility = []
    histories = {}
    for p in rows:
        text = norm(p.get("text"))
        qtargets = {tid for q in p.get("questions", []) for tid in q.get("target_ids", [])}
        for r in p.get("review_lexical_targets", []):
            tid = r.get("id")
            lr = lex.get(tid, {})
            keys = {norm(r.get("form")), norm(lr.get("form")), norm(lr.get("match_form")), norm(lr.get("lemma"))} - {""}
            token_visible = any(re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", text) for k in keys)
            task_visible = tid in qtargets
            visible = token_visible or task_visible
            if not visible:
                visibility.append({
                    "passage_id": p["id"],
                    "sequence": p["sequence"],
                    "target_id": tid,
                    "form": r.get("form"),
                    "stage": r.get("review_stage"),
                    "representation": r.get("representation"),
                    "kind": "review_not_visible_after_repair",
                    "severity": "major",
                })
            histories.setdefault(tid, []).append({
                "sequence": p["sequence"],
                "stage": r.get("review_stage"),
                "visible": visible,
                "passage_id": p["id"],
            })

    regressions = []
    for tid, hist in histories.items():
        highest = 0
        for e in sorted(hist, key=lambda x: x["sequence"]):
            cur = STAGE_ORDER.get(e.get("stage"), 0)
            if cur < highest:
                regressions.append({"target_id": tid, **e, "kind": "review_stage_regression"})
            highest = max(highest, cur)

    out = {
        "schema_version": 1,
        "date": "2026-08-20",
        "language": "fr",
        "level": "A1",
        "bound_sha256": bound,
        "scope": {"records": 60, "questions": 600, "answers": 600},
        "review_visibility_finding_count": len(visibility),
        "review_visibility_findings": visibility,
        "stage_regression_count": len(regressions),
        "stage_regressions": regressions,
        "deterministic_status": "PASS" if not visibility and not regressions else "FAIL",
        "known_unresolved_spacing_item": {
            "target_id": "fr-rank-0047",
            "lemma": "venir",
            "kind": "missing_later_R3_opportunity",
            "status": "UNRESOLVED_REQUIRES_PEDAGOGICAL_ADJUDICATION_OR_NATURAL_REVIEW_OPPORTUNITY",
        },
        "limitations": "Surface/token visibility and monotonic stage chronology only. This does not establish semantic review quality, spacing adequacy, coverage, naturalness, or educator release readiness.",
        "release_effect": "French remains REOPEN_REQUIRED."
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"deterministic_status": out["deterministic_status"], "visibility": len(visibility), "regressions": len(regressions)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
