#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROTO = ROOT / "subjects/cissp/2024-outline/secx-prototype"
WORKFLOW = ROOT / ".github/workflows/secx-prototype-smoke.yml"
NEXT = PROTO / "next.html"
REL_REVIEW = PROTO / "RELATIONSHIP_REVIEW.json"
REL_RELEASE = PROTO / "RELEASED_RELATIONSHIPS.json"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL secx_release_boundary_audit: {message}")


def run(*args: str) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        fail(f"command {' '.join(args)} failed: {exc.output.strip()}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    head = run("git", "rev-parse", "HEAD")
    base_name = os.environ.get("GITHUB_BASE_REF") or "main"
    base_ref = f"origin/{base_name}"
    try:
        subprocess.check_output(["git", "rev-parse", "--verify", base_ref], cwd=ROOT, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        fail(f"missing {base_ref}; exact-head workflow must checkout full history")

    merge_base = run("git", "merge-base", head, base_ref)
    changed = [p for p in run("git", "diff", "--name-only", f"{merge_base}..{head}").splitlines() if p]
    require(changed, "candidate diff is unexpectedly empty")

    workflow_path = ".github/workflows/secx-prototype-smoke.yml"
    prototype_prefix = "subjects/cissp/2024-outline/secx-prototype/"
    forbidden = [p for p in changed if p != workflow_path and not p.startswith(prototype_prefix)]
    require(not forbidden, f"files escaped prototype boundary: {forbidden}")
    require(not any(p.startswith("subjects/cissp/2024-outline/study-site/") for p in changed), "production study-site file changed")

    next_html = NEXT.read_text(encoding="utf-8")
    require("Expanded Knowledge Web Review" in next_html, "next.html no longer identifies itself as review surface")
    require(re.search(r'<iframe[^>]+src=["\']index\.html["\']', next_html) is not None, "next.html no longer embeds conservative index.html")

    # Reviewer-only relationship state must never be learner-loaded.
    require("RELATIONSHIP_REVIEW" not in next_html, "reviewer relationship registry is learner-loaded by next.html")
    require("RELEASED_RELATIONSHIPS.json" not in next_html, "raw released relationship JSON is directly loaded by next.html")

    # The only allowed learner relationship publication channel is the audited JS runtime
    # followed by the dedicated relationship lens. Completeness audit separately enforces
    # full ordering/uniqueness for the entire expanded dependency chain.
    require(next_html.count("released-relationships.js") == 1, "expected released relationship runtime channel is missing or duplicated")
    require(next_html.count("relationship-lens.js") == 1, "expected relationship lens runtime is missing or duplicated")
    require(next_html.index("released-relationships.js") < next_html.index("relationship-lens.js"), "relationship lens loads before released relationship runtime")

    review = json.loads(REL_REVIEW.read_text(encoding="utf-8"))
    require(review.get("scope") == "reviewer-only", "relationship registry lost reviewer-only scope")
    require(review.get("learner_runtime_loaded") is False, "relationship registry claims learner runtime loading")
    require(review.get("publication_state") == "draft-only", "relationship registry is no longer draft-only")

    released = json.loads(REL_RELEASE.read_text(encoding="utf-8"))
    require(released.get("scope") == "secx-review-prototype", "released relationship artifact escaped prototype scope")
    require(released.get("publication_state") == "prototype-released", "released relationship artifact lost prototype release state")
    require(released.get("learner_runtime_loaded") is True, "released relationship artifact no longer declares learner runtime loading")
    require(released.get("review_registry") == "RELATIONSHIP_REVIEW.json", "released relationship artifact lost reviewer-registry provenance")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    require("permissions:\n  contents: read" in workflow, "workflow permissions are no longer read-only")
    require("ref: ${{ github.event.pull_request.head.sha || github.sha }}" in workflow, "workflow no longer pins exact PR head")
    require("test \"$ACTUAL_HEAD\" = \"$EXPECTED_HEAD\"" in workflow, "exact-head assertion missing")
    require("fetch-depth: 0" in workflow, "full history is required for merge-base release-boundary audit")
    require("release-boundary-audit.py" in workflow, "release-boundary audit is not wired into exact-head workflow")
    require("candidate-hygiene-audit.py" in workflow, "candidate hygiene audit is not wired into exact-head workflow")
    require("candidate-completeness-audit.py" in workflow, "candidate completeness audit is not wired into exact-head workflow")
    require("relationship-audit.py" in workflow, "relationship semantic audit is not wired into exact-head workflow")
    require("relationship-release-audit.py" in workflow, "relationship release audit is not wired into exact-head workflow")
    require("relationship-browser-smoke.sh" in workflow, "relationship browser smoke is not wired into exact-head workflow")

    forbidden_publish_markers = [
        "actions/deploy-pages",
        "peaceiris/actions-gh-pages",
        "firebase deploy",
        "vercel --prod",
        "npm publish",
        "docker push",
        "gh release create",
        "id-token: write",
        "pages: write",
        "packages: write",
        "deployments: write",
    ]
    hits = [m for m in forbidden_publish_markers if m in workflow]
    require(not hits, f"workflow contains publication/deployment capability: {hits}")

    print(
        "PASS secx_release_boundary_audit "
        f"head={head[:12]} merge_base={merge_base[:12]} changed_files={len(changed)} "
        "scope=prototype+dedicated-workflow production_study_site=UNCHANGED "
        "next=review-only relationships=reviewer-only-registry+audited-prototype-release-channel "
        "workflow=read-only+no-deploy+hygiene-gated+completeness-gated+relationship-gated"
    )


if __name__ == "__main__":
    main()
