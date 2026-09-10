#!/usr/bin/env python3
"""Post-filter public discovery output for a graduated/new-grad search lane.

This contains no candidate PII. It suppresses roles whose title/body metadata clearly
indicates they are student-only internship/co-op/PEY opportunities, while preserving
junior, entry-level, associate, new-grad and recent-graduate roles.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "discovered.json"
STATUS_PATH = ROOT / "discovery_status.json"

STUDENT_TITLE = re.compile(r"\b(intern(?:ship)?|co[- ]?op|student|pey)\b", re.I)
GRAD_SIGNAL = re.compile(r"\b(new grad(?:uate)?|recent grad(?:uate)?|graduate program|entry[- ]level|junior|jr\.?|associate)\b", re.I)


def main() -> int:
    if not OUTPUT_PATH.exists():
        return 0
    doc = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    original = list(doc.get("jobs", []))
    kept = []
    suppressed = []
    for job in original:
        title = str(job.get("title") or "")
        if STUDENT_TITLE.search(title) and not GRAD_SIGNAL.search(title):
            suppressed.append({
                "id": job.get("id"),
                "source": job.get("source"),
                "title": title,
                "reason": "student_only_title_in_graduated_mode",
            })
            continue
        kept.append(job)

    doc["search_lane"] = "graduated_new_grad"
    doc["pre_filter_job_count"] = len(original)
    doc["student_only_suppressed_count"] = len(suppressed)
    doc["job_count"] = len(kept)
    doc["new_job_count"] = sum(1 for j in kept if j.get("new_this_run"))
    doc["jobs"] = kept
    OUTPUT_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if STATUS_PATH.exists():
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        status["search_lane"] = "graduated_new_grad"
        status["pre_filter_job_count"] = len(original)
        status["student_only_suppressed_count"] = len(suppressed)
        status["job_count"] = len(kept)
        status["new_job_count"] = doc["new_job_count"]
        status["student_only_suppressed"] = suppressed[:100]
        STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"graduated filter: kept {len(kept)}; suppressed {len(suppressed)} student-only roles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
