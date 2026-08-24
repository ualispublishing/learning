#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8766}"
OUT="${TMPDIR:-/tmp}/cissp-browser-smoke.html"
LOG="${TMPDIR:-/tmp}/cissp-browser-smoke-server.log"

CHROME="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser || true)"
if [[ -z "$CHROME" ]]; then
  echo "FAIL browser_smoke: Chrome/Chromium not found" >&2
  exit 1
fi

python -m http.server "$PORT" >"$LOG" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 1

"$CHROME" \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=12000 \
  --dump-dom \
  "http://127.0.0.1:${PORT}/browser-smoke.html" >"$OUT"

if ! grep -Fq 'data-smoke="pass"' "$OUT"; then
  echo "FAIL browser_smoke: interactive harness did not pass" >&2
  grep -o 'data-smoke="[^"]*"[^<]*>[^<]*' "$OUT" >&2 || true
  tail -n 100 "$OUT" >&2 || true
  echo "--- server log ---" >&2
  tail -n 100 "$LOG" >&2 || true
  exit 1
fi

if grep -Fq 'data-smoke="fail"' "$OUT"; then
  echo "FAIL browser_smoke: harness reported failure" >&2
  tail -n 100 "$OUT" >&2 || true
  exit 1
fi

printf 'PASS browser_smoke interactive=startup,review,practice,progress,sources,navigation\n'
