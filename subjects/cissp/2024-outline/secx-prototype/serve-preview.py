#!/usr/bin/env python3
"""Serve the SecX review prototype on localhost for manual testing."""
from __future__ import annotations

import argparse
import functools
import http.server
import subprocess
import threading
import webbrowser
from pathlib import Path

PROTO = Path(__file__).resolve().parent
SERVE_ROOT = PROTO.parent
REPO_ROOT = PROTO.parents[3]
DEFAULT_PORT = 8000
EXPECTED_BRANCH = "secx-web-prototype-20260901"


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def print_checkout_provenance() -> None:
    branch = git_value("rev-parse", "--abbrev-ref", "HEAD")
    head = git_value("rev-parse", "HEAD")
    status = git_value("status", "--porcelain")

    if head:
        print(f"Checkout: branch={branch or 'unknown'} head={head}", flush=True)
    else:
        print("Checkout: Git metadata unavailable — confirm the branch/SHA manually.", flush=True)

    if status is not None:
        if status:
            print("Status:   DIRTY — preview includes uncommitted or untracked changes.", flush=True)
        else:
            print("Status:   clean", flush=True)

    if branch and branch not in {EXPECTED_BRANCH, "HEAD"}:
        print(
            f"Warning: expected {EXPECTED_BRANCH} or a detached exact SHA; testing branch {branch}.",
            flush=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the SecX review prototype on localhost only.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"localhost port (default: {DEFAULT_PORT})")
    parser.add_argument("--no-browser", action="store_true", help="do not open the preview URL automatically")
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SERVE_ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    url = f"http://127.0.0.1:{args.port}/secx-prototype/next.html"

    print("SecX review prototype — localhost preview only", flush=True)
    print_checkout_provenance()
    print(f"Serving: {SERVE_ROOT}", flush=True)
    print(f"Open:    {url}", flush=True)
    print("Stop:    Ctrl-C", flush=True)

    if not args.no_browser:
        threading.Timer(0.35, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPreview stopped.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
