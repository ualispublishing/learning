#!/usr/bin/env python3
"""Serve the SecX review prototype on localhost for manual testing."""
from __future__ import annotations

import argparse
import functools
import http.server
import threading
import webbrowser
from pathlib import Path

PROTO = Path(__file__).resolve().parent
SERVE_ROOT = PROTO.parent
DEFAULT_PORT = 8000


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
