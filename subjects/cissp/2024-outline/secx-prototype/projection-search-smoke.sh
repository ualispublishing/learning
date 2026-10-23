#!/usr/bin/env bash
set -euo pipefail
PORT="${1:-8806}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
OUT="${TMPDIR:-/tmp}/secx-projection-search-smoke.html"
LOG="${TMPDIR:-/tmp}/secx-projection-search-server.log"
PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/secx-projection-search-profile.XXXXXX")"
CHROME="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser || true)"
if [[ -z "$CHROME" ]]; then echo "FAIL secx_projection_search_smoke: Chrome/Chromium not found" >&2; rm -rf "$PROFILE"; exit 1; fi
cd "$ROOT"
python -m http.server "$PORT" >"$LOG" 2>&1 & SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true; rm -rf "$PROFILE"' EXIT
sleep 1
if ! timeout 70s "$CHROME" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage --user-data-dir="$PROFILE" --virtual-time-budget=50000 --dump-dom "http://127.0.0.1:${PORT}/secx-prototype/projection-search-smoke.html" >"$OUT"; then
 echo "FAIL secx_projection_search_smoke: Chrome did not complete" >&2; tail -n 100 "$LOG" >&2 || true; exit 1
fi
if ! grep -Fq 'data-smoke="pass"' "$OUT"; then
 echo "FAIL secx_projection_search_smoke: harness did not pass" >&2; grep -o 'data-smoke="[^"]*"[^<]*>[^<]*' "$OUT" >&2 || true; tail -n 120 "$OUT" >&2 || true; exit 1
fi
grep -o 'PASS SecX projection search smoke:[^<]*' "$OUT" | head -1 || echo 'PASS SecX projection search smoke'
