#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROTO = ROOT / "subjects/cissp/2024-outline/secx-prototype"
WORKFLOW = ROOT / ".github/workflows/secx-prototype-smoke.yml"
INDEX = PROTO / "index.html"
NEXT = PROTO / "next.html"
PREVIEW = PROTO / "serve-preview.py"
MANUAL_TESTING = PROTO / "MANUAL_TESTING.md"

EXPECTED_RUNTIME = [
    "../study-site/data-ai.js",
    "../study-site/data-precision.js",
    "learner-registry.js",
    "next-layer.js",
    "learner-state.js",
    "due-review.js",
    "study-lens.js",
    "source-lens.js",
    "coverage-lens.js",
    "projection-search.js",
    "released-relationships.js",
    "relationship-lens.js",
]
LOCAL_RUNTIME = {
    "learner-registry.js",
    "next-layer.js",
    "learner-state.js",
    "due-review.js",
    "study-lens.js",
    "source-lens.js",
    "coverage-lens.js",
    "projection-search.js",
    "released-relationships.js",
    "relationship-lens.js",
}
REVIEW_ONLY_MARKERS = (
    "RELATIONSHIP_REVIEW.json",
    "RELATIONSHIP_REVIEW.md",
    "CANDIDATE_HYGIENE.md",
    "CANDIDATE_COMPLETENESS.md",
    "BROWSER_FIXTURES.md",
    "RELEASE_BOUNDARY.md",
)
RESILIENCE_MARKERS = (
    "frame.dataset.secxExpandedState='loading'",
    "frame.dataset.secxExpandedState='error'",
    "frame.dataset.secxExpandedState='ready'",
    "loadStatus.id='secxExpandedStatus'",
    "loadStatus.setAttribute('role','alert')",
    "The conservative knowledge web remains available.",
    "doc.addEventListener('error'",
    "win.addEventListener('error'",
    "relationships.onload=readyExpanded",
    "if(frame.dataset.secxExpandedState==='error')return;",
    "Expanded review layer ready.",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL secx_candidate_completeness_audit: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def run(*args: str) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        fail(f"command {' '.join(args)} failed: {exc.output.strip()}")


def changed_files() -> list[str]:
    head = run("git", "rev-parse", "HEAD")
    base_name = os.environ.get("GITHUB_BASE_REF") or "main"
    base_ref = f"origin/{base_name}"
    try:
        subprocess.check_output(["git", "rev-parse", "--verify", base_ref], cwd=ROOT, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        fail(f"missing {base_ref}; exact-head workflow must checkout full history")
    merge_base = run("git", "merge-base", head, base_ref)
    return [p for p in run("git", "diff", "--name-only", f"{merge_base}..{head}").splitlines() if p]


def main() -> None:
    changed = changed_files()
    prefix = "subjects/cissp/2024-outline/secx-prototype/"
    workflow = WORKFLOW.read_text(encoding="utf-8")
    index_html = INDEX.read_text(encoding="utf-8")
    next_html = NEXT.read_text(encoding="utf-8")
    preview = PREVIEW.read_text(encoding="utf-8")
    manual_testing = MANUAL_TESTING.read_text(encoding="utf-8")

    require(next_html.count('src="index.html"') == 1, "next.html must embed conservative index.html exactly once")
    require("future stable junction for retrieval cards, scenarios, and typed relationships" not in index_html, "conservative subtopic copy reverted to stale future-junction wording")
    require("Retrieval cards and released scenarios are reached from the expanded objective hub; reviewed semantic links currently connect released objectives, not subtopics." in index_html, "conservative subtopic copy must describe current objective-hub practice routing and objective-level reviewed links")

    positions: list[int] = []
    for dependency in EXPECTED_RUNTIME:
        require(next_html.count(dependency) == 1, f"runtime dependency must appear exactly once in next.html: {dependency}")
        positions.append(next_html.index(dependency))
    require(positions == sorted(positions) and len(set(positions)) == len(positions), "expanded runtime dependency order drifted")

    for marker in RESILIENCE_MARKERS:
        require(marker in next_html, f"expanded runtime fail-visible readiness contract is missing: {marker}")

    for marker in REVIEW_ONLY_MARKERS:
        require(marker not in next_html, f"review-only artifact is learner-loaded or referenced by next.html: {marker}")
    require(re.search(r"(?:^|[\"'/])[^\"']*(?:-audit\.py|browser-smoke\.html|browser-smoke\.sh)", next_html) is None, "audit or browser-smoke artifact leaked into learner entrypoint")

    changed_js = {
        Path(path).name
        for path in changed
        if path.startswith(prefix) and path.endswith(".js")
    }
    require(changed_js == LOCAL_RUNTIME, f"local runtime JS set drifted or contains an orphan: expected={sorted(LOCAL_RUNTIME)} actual={sorted(changed_js)}")
    for name in LOCAL_RUNTIME:
        require((PROTO / name).is_file(), f"local runtime dependency is missing: {name}")

    require('SERVE_ROOT = PROTO.parent' in preview, "manual preview must serve from the 2024-outline root")
    require('("127.0.0.1", args.port)' in preview, "manual preview must bind to localhost only")
    require('0.0.0.0' not in preview, "manual preview must not expose a wildcard network bind")
    require('/secx-prototype/next.html' in preview, "manual preview must open the expanded review surface")
    require('webbrowser.open(url)' in preview, "manual preview must expose its exact test URL to the local browser")
    require('serve-preview.py' in workflow and 'python -m py_compile subjects/cissp/2024-outline/secx-prototype/serve-preview.py' in workflow, "manual preview launcher is not syntax-gated in exact-head CI")
    require('SecX manual preview launcher smoke' in workflow and 'http://127.0.0.1:8866/secx-prototype/next.html' in workflow, "manual preview launcher is not HTTP-smoke-gated in exact-head CI")
    require('python3 subjects/cissp/2024-outline/secx-prototype/serve-preview.py' in manual_testing, "manual testing doc is missing the one-command preview launcher")
    require('http://127.0.0.1:8000/secx-prototype/next.html' in manual_testing, "manual testing doc is missing the default localhost URL")
    require('file://' in manual_testing, "manual testing doc must warn against direct file loading")

    audit_paths = [
        path
        for path in changed
        if path.startswith(prefix)
        and (Path(path).name == "audit.py" or Path(path).name.endswith("-audit.py"))
    ]
    require(audit_paths, "no candidate audits found")
    for path in audit_paths:
        require(path in workflow, f"candidate audit is not wired into the exact-head workflow: {path}")

    smoke_shells = sorted(
        path for path in changed if path.startswith(prefix) and path.endswith("-smoke.sh")
    )
    smoke_html = sorted(
        path for path in changed if path.startswith(prefix) and path.endswith("-smoke.html")
    )
    require(smoke_shells, "no browser-smoke runners found")
    require(len(smoke_shells) == len(smoke_html), "browser-smoke runner/fixture count mismatch")

    for shell_path in smoke_shells:
        require(shell_path in workflow, f"browser-smoke runner is not wired into the exact-head workflow: {shell_path}")
        shell = ROOT / shell_path
        html = shell.with_suffix(".html")
        require(html.is_file(), f"browser-smoke runner has no HTML fixture: {shell_path}")
        shell_text = shell.read_text(encoding="utf-8")
        require(html.name in shell_text, f"browser-smoke runner does not reference its paired fixture: {shell_path} -> {html.name}")

    for html_path in smoke_html:
        shell = (ROOT / html_path).with_suffix(".sh")
        require(shell.is_file(), f"browser-smoke fixture has no paired runner: {html_path}")

    print(
        "PASS secx_candidate_completeness_audit "
        f"runtime_dependencies={len(EXPECTED_RUNTIME)} local_runtime_js={len(LOCAL_RUNTIME)} "
        f"candidate_audits={len(audit_paths)} browser_smokes={len(smoke_shells)} "
        "entrypoint=ordered+single-load+fail-visible reviewer_only=isolated "
        "conservative_copy=current-scope manual_preview=localhost-only+syntax-gated+http-smoked workflow=fully-wired"
    )


if __name__ == "__main__":
    main()
