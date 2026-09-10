#!/usr/bin/env python3
"""Build a privacy-safe early-career review queue from discovered public jobs.

This script uses only public job metadata already present in discovered.json.
It does not contain candidate PII, credentials, resumes, application answers, or
submission logic. The output is triage data for the private application workflow.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DISCOVERED = ROOT / "discovered.json"
OUTPUT = ROOT / "actionable.json"

STRONG_EARLY = (
    "junior", "new grad", "new graduate", "graduate", "entry level",
    "entry-level", "associate", "early career", "early-career",
)

GOOD_ROLE = (
    "software", "developer", "engineer", "data", "analyst", "support",
    "quality", "qa", "security", "cyber", "implementation", "technical",
    "automation", "ai", "machine learning", "systems", "it ",
)

SENIOR_TITLE = (
    "senior", "sr.", "sr ", "staff", "principal", "lead", "manager",
    "director", "architect", "head of", "vp ", "vice president",
)

MID_LEVEL_TITLE = (
    "intermediate", "level 2", "level ii", "engineer ii", "developer ii",
    "analyst ii", "specialist ii", "sdet ii",
)

ADVANCED_LEVEL_TITLE = (
    "level 3", "level iii", "engineer iii", "developer iii", "analyst iii",
    "specialist iii", "sdet iii", "engineer iv", "developer iv", "sdet iv",
)

GOOD_LOCATION = (
    "toronto", "markham", "mississauga", "brampton", "vaughan",
    "richmond hill", "oakville", "burlington", "ontario", "remote",
)


def has_level_token(title: str, roman: str) -> bool:
    return bool(re.search(rf"\b{roman}\b", title, flags=re.IGNORECASE))


def score_job(job: dict) -> tuple[int, list[str]]:
    title = str(job.get("title") or "").lower()
    location = str(job.get("location") or "").lower()
    reasons: list[str] = []
    score = 50

    # Freshness helps ordering, but cannot by itself make a role high priority.
    if job.get("new_this_run"):
        score += 10
        reasons.append("new_this_run")

    explicit_early = any(term in title for term in STRONG_EARLY)
    if explicit_early:
        score += 25
        reasons.append("explicit_early_career_title")

    role_hits = [term.strip() for term in GOOD_ROLE if term in title]
    if role_hits:
        score += min(15, 5 + (len(set(role_hits)) * 2))
        reasons.append("technical_role_family")

    if any(term in location for term in GOOD_LOCATION):
        score += 8
        reasons.append("preferred_canada_location")

    if any(term in title for term in SENIOR_TITLE):
        score -= 60
        reasons.append("senior_title_penalty")

    if any(term in title for term in ADVANCED_LEVEL_TITLE) or (
        any(k in title for k in ("engineer", "developer", "analyst", "sdet", "specialist"))
        and (has_level_token(title, "iii") or has_level_token(title, "iv"))
    ):
        score -= 35
        reasons.append("advanced_level_title_penalty")
    elif any(term in title for term in MID_LEVEL_TITLE) or (
        any(k in title for k in ("engineer", "developer", "analyst", "sdet", "specialist"))
        and has_level_token(title, "ii")
    ):
        score -= 20
        reasons.append("mid_level_title_penalty")

    if "intern" in title or "co-op" in title or "co op" in title:
        score -= 50
        reasons.append("student_role_penalty")

    # High means the title itself gives affirmative early-career evidence.
    # Fresh non-senior technical roles remain medium until private screening.
    if not explicit_early and score >= 85:
        score = 84
        reasons.append("high_band_capped_without_early_career_evidence")

    return max(0, min(100, score)), reasons


def main() -> int:
    payload = json.loads(DISCOVERED.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", [])

    ranked = []
    for job in jobs:
        score, reasons = score_job(job)
        item = dict(job)
        item["priority_score"] = score
        item["priority_reasons"] = reasons
        item["review_band"] = (
            "high" if score >= 85 else "medium" if score >= 60 else "low"
        )
        ranked.append(item)

    ranked.sort(
        key=lambda j: (
            j.get("priority_score", 0),
            bool(j.get("new_this_run")),
            str(j.get("published_at") or ""),
        ),
        reverse=True,
    )

    actionable = [j for j in ranked if j["review_band"] != "low"]
    output = {
        "schema_version": 2,
        "generated_at": payload.get("generated_at"),
        "privacy": "Public job metadata only. No candidate data, credentials, or application answers.",
        "purpose": "Prioritized review queue only; not submission authorization.",
        "candidate_mode": payload.get("candidate_mode", "graduated_2026_new_grad_junior"),
        "source_job_count": len(jobs),
        "actionable_job_count": len(actionable),
        "high_priority_count": sum(1 for j in actionable if j["review_band"] == "high"),
        "medium_priority_count": sum(1 for j in actionable if j["review_band"] == "medium"),
        "suppressed_low_priority_count": len(jobs) - len(actionable),
        "jobs": actionable,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"priority queue: {len(actionable)} actionable from {len(jobs)} jobs; "
        f"{output['high_priority_count']} high, {output['medium_priority_count']} medium, "
        f"{output['suppressed_low_priority_count']} low suppressed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
