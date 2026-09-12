#!/usr/bin/env python3
"""Plugin-free public job discovery for the job-automation project.

Reads public Greenhouse, Lever and Ashby job-board APIs listed in
discovery_sources.json, filters to Canada/remote-Canada early-career tech roles,
deduplicates them, and writes only public job metadata.

No candidate data, credentials, resume data, or application answers belong here.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES_PATH = ROOT / "discovery_sources.json"
OUTPUT_PATH = ROOT / "discovered.json"
STATUS_PATH = ROOT / "discovery_status.json"

USER_AGENT = "ualispublishing-job-discovery/1.0 (+https://github.com/ualispublishing/learning)"

CANADA_TERMS = (
    "canada", "canadian", "ontario", "toronto", "mississauga", "brampton",
    "waterloo", "kitchener", "ottawa", "hamilton", "guelph", "markham",
    "vaughan", "richmond hill", "oakville", "burlington", "london, on",
    "british columbia", "vancouver", "victoria", "alberta", "calgary",
    "edmonton", "quebec", "montréal", "montreal", "nova scotia", "halifax",
    "manitoba", "winnipeg", "saskatchewan", "regina", "saskatoon",
    "new brunswick", "fredericton", "newfoundland", "st. john's",
)

# When an ATS supplies an explicit location, trust that field over incidental
# country names in the description. Only fall back to body text for genuinely
# generic location labels such as Remote, North America, or Americas.
GENERIC_LOCATION_TERMS = (
    "remote", "hybrid", "on-site", "onsite", "anywhere", "global", "worldwide",
    "north america", "americas", "multiple locations", "various locations",
    "distributed",
)

TECH_TITLE_TERMS = (
    "software", "developer", "engineer", "data", "analytics", "analyst",
    "machine learning", "artificial intelligence", " ai ", "ai ", "qa",
    "quality assurance", "test", "testing", "cybersecurity", "security",
    "information technology", "it support", "technical support", "help desk",
    "helpdesk", "service desk", "implementation", "systems", "system analyst",
    "product support", "technical operations", "technology",
)

EARLY_TITLE_TERMS = (
    "junior", "jr.", "jr ", "entry", "new grad", "graduate", "intern",
    "internship", "co-op", "coop", "associate", "level 1", "level i",
    "engineer i", "developer i", "analyst i", "specialist i",
)

SENIOR_TITLE_TERMS = (
    "senior", "sr.", "staff ", "principal", "lead ", "manager", "director",
    "head of", "vice president", "vp ", "architect",
)

EARLY_BODY_PATTERNS = (
    re.compile(r"\b0\s*[-–]\s*2\s+years?\b", re.I),
    re.compile(r"\b0\s*[-–]\s*1\s+years?\b", re.I),
    re.compile(r"\b1\s*[-–]\s*2\s+years?\b", re.I),
    re.compile(r"\bup to 2 years?\b", re.I),
    re.compile(r"\bnew grads?\b", re.I),
    re.compile(r"\brecent graduates?\b", re.I),
    re.compile(r"\bearly[- ]career\b", re.I),
    re.compile(r"\bentry[- ]level\b", re.I),
)

# A generic non-senior title (for example "Support Engineer") should not enter
# the early-career queue when the posting itself clearly requires established
# mid-career tenure. Explicit junior/new-grad/associate titles still take
# precedence because some employers write aspirational experience ranges.
MID_CAREER_BODY_PATTERNS = (
    re.compile(r"\b3\s*[-–]\s*5\s+years?\b", re.I),
    re.compile(r"\b3\s*[-–]\s*4\s+years?\b", re.I),
    re.compile(r"\b3\+\s*years?\b", re.I),
    re.compile(r"\b4\+\s*years?\b", re.I),
    re.compile(r"\b5\+\s*years?\b", re.I),
    re.compile(r"\bminimum of 3 years?\b", re.I),
    re.compile(r"\bat least 3 years?\b", re.I),
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_json(url: str) -> dict | list:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def text_has_any(text: str, terms: tuple[str, ...]) -> list[str]:
    low = f" {text.lower()} "
    return [term.strip() for term in terms if term.lower() in low]


def is_canada_eligible(location: str, body: str) -> tuple[bool, list[str]]:
    location_low = (location or "").strip().lower()
    location_signals = [term for term in CANADA_TERMS if term in location_low]
    if location_signals:
        return True, location_signals[:5]

    # Strip work-mode/generic geography labels. If alphabetic location text is
    # still present, it is an explicit non-Canada place (e.g. "Remote (United
    # Kingdom)") and description boilerplate must not override it.
    remainder = location_low
    for term in GENERIC_LOCATION_TERMS:
        remainder = remainder.replace(term, " ")
    remainder = re.sub(r"[^a-z]+", " ", remainder).strip()
    if location_low and remainder:
        return False, []

    body_low = body[:8000].lower()
    body_signals = [term for term in CANADA_TERMS if term in body_low]
    if body_signals:
        return True, body_signals[:5]
    return False, []


def is_tech_role(title: str) -> tuple[bool, list[str]]:
    signals = text_has_any(title, TECH_TITLE_TERMS)
    return bool(signals), signals[:5]


def is_early_career(title: str, body: str, employment_type: str = "") -> tuple[bool, list[str]]:
    title_low = title.lower()
    senior = [term for term in SENIOR_TITLE_TERMS if term in title_low]
    if senior:
        return False, [f"seniority:{x.strip()}" for x in senior[:3]]

    title_signals = text_has_any(title, EARLY_TITLE_TERMS)
    explicit_early_title = bool(title_signals)
    signals = list(title_signals)
    if employment_type.lower() == "intern":
        signals.append("employment:intern")
        explicit_early_title = True

    if not explicit_early_title:
        for pattern in MID_CAREER_BODY_PATTERNS:
            match = pattern.search(body[:12000])
            if match:
                return False, [f"mid_career_requirement:{match.group(0)}"]

    for pattern in EARLY_BODY_PATTERNS:
        match = pattern.search(body[:12000])
        if match:
            signals.append(match.group(0))

    lower = title.lower()
    if not signals and any(x in lower for x in (
        "analyst", "support", "specialist", "technician", "coordinator"
    )):
        signals.append("non-senior analyst/support/specialist")

    return bool(signals), signals[:5]


def stable_id(provider: str, source_slug: str, job_key: str, url: str) -> str:
    material = f"{provider}|{source_slug}|{job_key}|{url}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def normalize_job(
    *,
    provider: str,
    source_name: str,
    source_slug: str,
    job_key: str,
    title: str,
    location: str,
    body: str,
    url: str,
    apply_url: str | None = None,
    published_at: str | None = None,
    employment_type: str | None = None,
    compensation: str | None = None,
) -> dict | None:
    if not title or not url:
        return None

    tech_ok, tech_signals = is_tech_role(title)
    canada_ok, location_signals = is_canada_eligible(location, body)
    early_ok, early_signals = is_early_career(title, body, employment_type or "")

    if not (tech_ok and canada_ok and early_ok):
        return None

    return {
        "id": stable_id(provider, source_slug, str(job_key), url),
        "provider": provider,
        "source": source_name,
        "source_slug": source_slug,
        "title": title.strip(),
        "location": (location or "").strip(),
        "employment_type": employment_type,
        "published_at": published_at,
        "url": url,
        "apply_url": apply_url or url,
        "compensation": compensation,
        "match": {
            "tech": tech_signals,
            "canada": location_signals,
            "early_career": early_signals,
        },
    }


def greenhouse_jobs(source: dict) -> list[dict]:
    slug = urllib.parse.quote(source["slug"], safe="")
    payload = fetch_json(
        f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    )
    results = []
    for job in payload.get("jobs", []):
        location = (job.get("location") or {}).get("name") or ""
        body = strip_html(job.get("content"))
        normalized = normalize_job(
            provider="greenhouse",
            source_name=source["name"],
            source_slug=source["slug"],
            job_key=str(job.get("id") or job.get("absolute_url") or ""),
            title=job.get("title") or "",
            location=location,
            body=body,
            url=job.get("absolute_url") or "",
            published_at=job.get("updated_at"),
        )
        if normalized:
            results.append(normalized)
    return results


def lever_jobs(source: dict) -> list[dict]:
    slug = urllib.parse.quote(source["slug"], safe="")
    payload = fetch_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    results = []
    for job in payload if isinstance(payload, list) else []:
        categories = job.get("categories") or {}
        location = categories.get("location") or ""
        body_parts = [
            job.get("descriptionPlain") or "",
            strip_html(job.get("description") or ""),
        ]
        for item in job.get("lists") or []:
            body_parts.append(strip_html(item.get("content") or ""))
        body = " ".join(body_parts)
        normalized = normalize_job(
            provider="lever",
            source_name=source["name"],
            source_slug=source["slug"],
            job_key=str(job.get("id") or job.get("hostedUrl") or ""),
            title=job.get("text") or "",
            location=location,
            body=body,
            url=job.get("hostedUrl") or "",
            apply_url=job.get("applyUrl"),
            published_at=str(job.get("createdAt") or "") or None,
        )
        if normalized:
            results.append(normalized)
    return results


def ashby_jobs(source: dict) -> list[dict]:
    slug = urllib.parse.quote(source["slug"], safe="")
    payload = fetch_json(
        f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true"
    )
    results = []
    for job in payload.get("jobs", []):
        if job.get("isListed") is False:
            continue
        locations = [job.get("location") or ""]
        for secondary in job.get("secondaryLocations") or []:
            if secondary.get("location"):
                locations.append(secondary["location"])
        location = " | ".join(x for x in locations if x)
        body = job.get("descriptionPlain") or strip_html(job.get("descriptionHtml"))
        compensation_obj = job.get("compensation") or {}
        compensation = (
            compensation_obj.get("compensationTierSummary")
            or compensation_obj.get("scrapeableCompensationSalarySummary")
        )
        normalized = normalize_job(
            provider="ashby",
            source_name=source["name"],
            source_slug=source["slug"],
            job_key=job.get("jobUrl") or job.get("applyUrl") or job.get("title") or "",
            title=job.get("title") or "",
            location=location,
            body=body,
            url=job.get("jobUrl") or "",
            apply_url=job.get("applyUrl"),
            published_at=job.get("publishedAt"),
            employment_type=job.get("employmentType"),
            compensation=compensation,
        )
        if normalized:
            results.append(normalized)
    return results


FETCHERS = {
    "greenhouse": greenhouse_jobs,
    "lever": lever_jobs,
    "ashby": ashby_jobs,
}


def load_previous() -> dict[str, dict]:
    if not OUTPUT_PATH.exists():
        return {}
    try:
        payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {job["id"]: job for job in payload.get("jobs", []) if job.get("id")}


def main() -> int:
    sources_doc = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    previous = load_previous()
    started = now_iso()
    all_jobs: list[dict] = []
    source_status = []

    for source in sources_doc.get("sources", []):
        provider = source.get("provider")
        fetcher = FETCHERS.get(provider)
        if not fetcher:
            source_status.append({
                "provider": provider,
                "source": source.get("name"),
                "status": "unsupported_provider",
                "jobs": 0,
            })
            continue
        try:
            jobs = fetcher(source)
            all_jobs.extend(jobs)
            source_status.append({
                "provider": provider,
                "source": source.get("name"),
                "slug": source.get("slug"),
                "status": "ok",
                "jobs": len(jobs),
            })
        except Exception as exc:
            source_status.append({
                "provider": provider,
                "source": source.get("name"),
                "slug": source.get("slug"),
                "status": "error",
                "jobs": 0,
                "error": f"{type(exc).__name__}: {exc}"[:300],
            })

    unique: dict[str, dict] = {}
    seen_urls: set[str] = set()
    for job in sorted(all_jobs, key=lambda item: (
        item.get("source", "").lower(),
        item.get("title", "").lower(),
        item.get("location", "").lower(),
    )):
        canonical_url = (job.get("url") or "").rstrip("/")
        if canonical_url in seen_urls:
            continue
        seen_urls.add(canonical_url)

        prior = previous.get(job["id"])
        job["first_seen_at"] = prior.get("first_seen_at") if prior else started
        job["last_seen_at"] = started
        job["new_this_run"] = prior is None
        unique[job["id"]] = job

    jobs = list(unique.values())
    jobs.sort(key=lambda item: (
        not item["new_this_run"],
        item.get("source", "").lower(),
        item.get("title", "").lower(),
    ))

    output = {
        "schema_version": 1,
        "generated_at": started,
        "privacy": "Public job metadata only. No candidate data or credentials.",
        "job_count": len(jobs),
        "new_job_count": sum(1 for job in jobs if job["new_this_run"]),
        "jobs": jobs,
    }
    status = {
        "schema_version": 1,
        "started_at": started,
        "completed_at": now_iso(),
        "source_count": len(source_status),
        "successful_sources": sum(1 for s in source_status if s["status"] == "ok"),
        "failed_sources": sum(1 for s in source_status if s["status"] == "error"),
        "job_count": len(jobs),
        "new_job_count": output["new_job_count"],
        "sources": source_status,
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    STATUS_PATH.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"discovery: {len(jobs)} matching jobs; "
        f"{output['new_job_count']} new; "
        f"{status['failed_sources']} source errors"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
