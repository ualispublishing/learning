#!/usr/bin/env python3
"""Build a privacy-safe early-career review queue from discovered public jobs.

This script uses only public job metadata already present in discovered.json.
It does not contain candidate PII, credentials, resumes, application answers, or
submission logic. The output is triage data for the private application workflow.
"""

from __future__ import annotations

import json
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

GOOD_LOCATION = (
    "toronto", "markham", "mississauga", "brampton", "vaughan",
    "richmond hill", "oakville", "burlington", "ontario", "remote",
)


def score_job(job: dict) -> tuple[int, list[str]]:
    title = str(job.get("title") or "").lower()
    location = str(job.get("location") or "").lower()
    reasons: list[str] = []
    score = 50

    if job.get("new_this_run"):
        score += 25
        reasons.append("new_this_run")

    if any(term in title for term in STRONG_EARLY):
        score += 25
        reasons.append("explicit_early_career_title")

    role_hits = [term.strip() for term in GOOD_ROLE if term in title]
    if role_hits:
        score += min(20, 6 + (len(role_hits) * 3))
        reasons.append("technical_role_family")

    if any(term in location for term in GOOD_LOCATION):
        score += 8
        reasons.append("preferred_canada_location")

    if any(term in title for term in SENIOR_TITLE):
        score -= 60
        reasons.append("senior_title_penalty")

    if "intern" in title or "co-op" in title or "co op" in title:
        score -= 50
        reasons.append("student_role_penalty")

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
            "high" if score >= 80 else "medium" if score >= 60 else "low"
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
        "schema_version": 1,
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
