#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROTO = ROOT / "subjects/cissp/2024-outline/secx-prototype"
WORKFLOW_PATH = ".github/workflows/secx-prototype-smoke.yml"
PROTO_PREFIX = "subjects/cissp/2024-outline/secx-prototype/"

TEXT_SUFFIXES = {".html", ".js", ".json", ".md", ".py", ".sh", ".yml", ".yaml"}
RUNTIME_FILES = {
    "index.html",
    "next.html",
    "learner-registry.js",
    "next-layer.js",
    "learner-state.js",
    "due-review.js",
    "study-lens.js",
    "source-lens.js",
    "coverage-lens.js",
    "projection-search.js",
}
SMOKE_QUERY_TOKENS = (
    "browser-smoke=",
    "continue-smoke=",
    "source-smoke=",
    "coverage-smoke=",
    "projection-search-smoke=",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL secx_candidate_hygiene_audit: {message}")


def run(*args: str) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        fail(f"command {' '.join(args)} failed: {exc.output.strip()}")


def candidate_paths() -> list[str]:
    head = run("git", "rev-parse", "HEAD")
    base_name = os.environ.get("GITHUB_BASE_REF") or "main"
    base_ref = f"origin/{base_name}"
    try:
        subprocess.check_output(["git", "rev-parse", "--verify", base_ref], cwd=ROOT, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        fail(f"missing {base_ref}; hygiene audit requires full-history checkout")
    merge_base = run("git", "merge-base", head, base_ref)
    return [p for p in run("git", "diff", "--name-only", f"{merge_base}..{head}").splitlines() if p]


def main() -> None:
    changed = candidate_paths()
    if not changed:
        fail("candidate diff is unexpectedly empty")

    escaped = [p for p in changed if p != WORKFLOW_PATH and not p.startswith(PROTO_PREFIX)]
    if escaped:
        fail(f"candidate files escaped hygiene scope: {escaped}")

    text_paths: list[Path] = []
    for rel in changed:
        path = ROOT / rel
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text_paths.append(path)

    errors: list[str] = []
    for path in text_paths:
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{rel}: candidate text file is not UTF-8")
            continue
        if not raw.endswith(b"\n"):
            errors.append(f"{rel}: missing final newline")
        if b"\r\n" in raw:
            errors.append(f"{rel}: CRLF line endings are not allowed in candidate text")
        if re.search(r"^(?:<<<<<<< .+|=======|>>>>>>> .+)$", text, re.MULTILINE):
            errors.append(f"{rel}: unresolved merge-conflict marker")

    for name in sorted(RUNTIME_FILES):
        path = PROTO / name
        if not path.is_file():
            errors.append(f"runtime file missing: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"\b(?:TODO|FIXME|HACK|XXX)\b", text, re.IGNORECASE):
            errors.append(f"{name}: unresolved developer marker in learner runtime")
        if re.search(r"\bdebugger\s*;?", text):
            errors.append(f"{name}: debugger statement in learner runtime")
        if re.search(r"\bconsole\.(?:log|debug|trace)\s*\(", text):
            errors.append(f"{name}: stray console logging in learner runtime")
        leaked = [token for token in SMOKE_QUERY_TOKENS if token in text]
        if leaked:
            errors.append(f"{name}: browser-smoke query token leaked into learner runtime: {leaked}")
        if "data-smoke=" in text:
            errors.append(f"{name}: smoke result marker leaked into learner runtime")

    if errors:
        print("FAIL secx_candidate_hygiene_audit")
        for error in errors:
            print("-", error)
        raise SystemExit(1)

    print(
        "PASS secx_candidate_hygiene_audit "
        f"candidate_text_files={len(text_paths)} runtime_files={len(RUNTIME_FILES)} "
        "utf8=yes final_newlines=yes crlf=no conflicts=no dev_markers=no "
        "debugger=no stray_console=no smoke_query_leakage=no"
    )


if __name__ == "__main__":
    main()
