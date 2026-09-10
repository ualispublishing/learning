#!/usr/bin/env python3
"""Post-filter public discovery output for a graduated/new-grad candidate.

Keeps junior, entry-level, associate and graduate opportunities while excluding
student-only internship/co-op roles. Public job metadata only.
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


def should_exclude(job: dict) -> bool:
    title = str(job.get("title") or "").lower()
    employment_type = str(job.get("employment_type") or "").lower()

    # Keep roles that explicitly invite graduates even if the title also says co-op.
    if any(term in title for term in GRADUATE_OVERRIDE_TERMS):
        return False

    if employment_type == "intern":
        return True

    return any(term in title for term in STUDENT_ONLY_TITLE_TERMS)


def main() -> int:
    payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", [])
    kept = [job for job in jobs if not should_exclude(job)]
    removed = len(jobs) - len(kept)

    payload["candidate_mode"] = "graduated_2026_new_grad_junior"
    payload["student_only_jobs_excluded"] = removed
    payload["jobs"] = kept
    payload["job_count"] = len(kept)
    payload["new_job_count"] = sum(1 for job in kept if job.get("new_this_run"))
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    status["candidate_mode"] = "graduated_2026_new_grad_junior"
    status["student_only_jobs_excluded"] = removed
    status["job_count"] = len(kept)
    status["new_job_count"] = payload["new_job_count"]
    STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"graduated filter: {len(kept)} kept; {removed} student-only jobs excluded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
