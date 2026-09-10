#!/usr/bin/env python3
"""Post-filter public discovery output for a graduated/new-grad Canadian candidate.

Keeps junior, entry-level, associate and graduate opportunities, excludes
student-only internship/co-op roles, and rejects foreign-location false positives
where a description merely mentions Canada. Public job metadata only.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "discovered.json"
STATUS_PATH = ROOT / "discovery_status.json"

GRADUATE_OVERRIDE_TERMS = (
    "new grad",
    "new graduate",
    "recent grad",
    "recent graduate",
    "graduate program",
    "graduate rotational",
    "graduate recruitment",
)

STUDENT_ONLY_TITLE_TERMS = (
    "intern",
    "internship",
    "co-op",
    "co op",
    "coop",
    "student",
    "practicum",
)

CANADA_LOCATION_TERMS = (
    "canada", "canadian", "ontario", "toronto", "mississauga", "brampton",
    "waterloo", "kitchener", "ottawa", "hamilton", "guelph", "markham",
    "vaughan", "richmond hill", "oakville", "burlington", "london, on",
    "british columbia", "vancouver", "victoria", "alberta", "calgary",
    "edmonton", "quebec", "montréal", "montreal", "nova scotia", "halifax",
    "manitoba", "winnipeg", "saskatchewan", "regina", "saskatoon",
    "new brunswick", "fredericton", "newfoundland", "st. john's",
)


def is_student_only(job: dict) -> bool:
    title = str(job.get("title") or "").lower()
    employment_type = str(job.get("employment_type") or "").lower()

    # Keep roles that explicitly invite graduates even if the title also says co-op.
    if any(term in title for term in GRADUATE_OVERRIDE_TERMS):
        return False
    if employment_type == "intern":
        return True
    return any(term in title for term in STUDENT_ONLY_TITLE_TERMS)


def is_canada_location(job: dict) -> bool:
    location = str(job.get("location") or "").lower()
    if any(term in location for term in CANADA_LOCATION_TERMS):
        return True

    # Some providers label Canada-wide jobs simply as Remote. In that narrow case,
    # retain the role only if the upstream matcher found an explicit Canada signal.
    canada_signals = [str(x).lower() for x in (job.get("match") or {}).get("canada", [])]
    return "remote" in location and any(x in {"canada", "canadian"} for x in canada_signals)


def main() -> int:
    payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", [])

    after_student_filter = [job for job in jobs if not is_student_only(job)]
    student_removed = len(jobs) - len(after_student_filter)
    kept = [job for job in after_student_filter if is_canada_location(job)]
    location_removed = len(after_student_filter) - len(kept)

    payload["candidate_mode"] = "graduated_2026_new_grad_junior"
    payload["student_only_jobs_excluded"] = student_removed
    payload["non_canada_location_jobs_excluded"] = location_removed
    payload["jobs"] = kept
    payload["job_count"] = len(kept)
    payload["new_job_count"] = sum(1 for job in kept if job.get("new_this_run"))
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    status["candidate_mode"] = "graduated_2026_new_grad_junior"
    status["student_only_jobs_excluded"] = student_removed
    status["non_canada_location_jobs_excluded"] = location_removed
    status["job_count"] = len(kept)
    status["new_job_count"] = payload["new_job_count"]
    STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"graduated filter: {len(kept)} kept; {student_removed} student-only and "
        f"{location_removed} non-Canada-location jobs excluded"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
