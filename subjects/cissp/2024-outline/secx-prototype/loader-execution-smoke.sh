#!/usr/bin/env bash
set -euo pipefail
PORT="${1:-8846}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
TARGET="$HERE/projection-search.js"
BACKUP="$HERE/projection-search.js.__secx_execution_smoke"
OUT="${TMPDIR:-/tmp}/secx-loader-execution-smoke.html"
LOG="${TMPDIR:-/tmp}/secx-loader-execution-server.log"
PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/secx-loader-execution-profile.XXXXXX")"
CHROME="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || command -v chromium-browser || true)"
SERVER_PID=""
cleanup(){
  if [[ -n "$SERVER_PID" ]]; then kill "$SERVER_PID" 2>/dev/null || true; fi
  if [[ -e "$BACKUP" ]]; then rm -f "$TARGET"; mv "$BACKUP" "$TARGET"; fi
  rm -rf "$PROFILE"
}
trap cleanup EXIT
if [[ -z "$CHROME" ]]; then echo "FAIL secx_loader_execution_smoke: Chrome/Chromium not found" >&2; exit 1; fi
if [[ ! -f "$TARGET" ]]; then echo "FAIL secx_loader_execution_smoke: expected dependency missing before test: $TARGET" >&2; exit 1; fi
if [[ -e "$BACKUP" ]]; then echo "FAIL secx_loader_execution_smoke: stale backup exists: $BACKUP" >&2; exit 1; fi
mv "$TARGET" "$BACKUP"
printf '%s\n' "throw new Error('SECX loader execution smoke');" > "$TARGET"
cd "$ROOT"
python -m http.server "$PORT" >"$LOG" 2>&1 & SERVER_PID=$!
sleep 1
if ! timeout 70s "$CHROME" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage --user-data-dir="$PROFILE" --virtual-time-budget=50000 --dump-dom "http://127.0.0.1:${PORT}/secx-prototype/loader-execution-smoke.html" >"$OUT"; then
  echo "FAIL secx_loader_execution_smoke: Chrome did not complete" >&2
  tail -n 100 "$LOG" >&2 || true
  exit 1
fi
if ! grep -Fq 'data-smoke="pass"' "$OUT"; then
  echo "FAIL secx_loader_execution_smoke: harness did not pass" >&2
  grep -o 'data-smoke="[^"]*"[^<]*>[^<]*' "$OUT" >&2 || true
  tail -n 120 "$OUT" >&2 || true
  exit 1
fi
grep -o 'PASS SecX loader execution smoke:[^<]*' "$OUT" | head -1 || echo 'PASS SecX loader execution smoke'
