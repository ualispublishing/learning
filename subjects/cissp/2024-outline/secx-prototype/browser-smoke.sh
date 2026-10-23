#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8776}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
OUT="${TMPDIR:-/tmp}/secx-expanded-browser-smoke.html"
LOG="${TMPDIR:-/tmp}/secx-expanded-browser-smoke-server.log"
PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/secx-chrome-profile.XXXXXX")"

CHROME="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser || true)"
if [[ -z "$CHROME" ]]; then
  echo "FAIL secx_browser_smoke: Chrome/Chromium not found" >&2
  rm -rf "$PROFILE"
  exit 1
fi

cd "$ROOT"
python -m http.server "$PORT" >"$LOG" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true; rm -rf "$PROFILE"' EXIT
sleep 1

if ! timeout 120s "$CHROME" \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --user-data-dir="$PROFILE" \
  --virtual-time-budget=100000 \
  --dump-dom \
  "http://127.0.0.1:${PORT}/secx-prototype/browser-smoke.html" >"$OUT"; then
  echo "FAIL secx_browser_smoke: Chrome did not complete successfully" >&2
  tail -n 120 "$LOG" >&2 || true
  exit 1
fi

if ! grep -Fq 'data-smoke="pass"' "$OUT"; then
  echo "FAIL secx_browser_smoke: interactive harness did not pass" >&2
  grep -o 'data-smoke="[^"]*"[^<]*>[^<]*' "$OUT" >&2 || true
  tail -n 140 "$OUT" >&2 || true
  echo "--- server log ---" >&2
  tail -n 140 "$LOG" >&2 || true
  exit 1
fi

if grep -Fq 'data-smoke="fail"' "$OUT"; then
  echo "FAIL secx_browser_smoke: harness reported failure" >&2
  tail -n 140 "$OUT" >&2 || true
  exit 1
fi

RESULT="$(grep -o 'PASS SecX expanded browser smoke:[^<]*' "$OUT" | head -1 || true)"
printf '%s\n' "${RESULT:-PASS SecX expanded browser smoke}"
