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
  --virtual-time-budget=7000 \
  --dump-dom \
  "http://127.0.0.1:${PORT}/" >"$OUT"

require(){
  local pattern="$1" label="$2"
  if ! grep -Fq "$pattern" "$OUT"; then
    echo "FAIL browser_smoke: missing $label ($pattern)" >&2
    tail -n 80 "$OUT" >&2 || true
    exit 1
  fi
}

forbid(){
  local pattern="$1" label="$2"
  if grep -Fq "$pattern" "$OUT"; then
    echo "FAIL browser_smoke: unexpected $label ($pattern)" >&2
    tail -n 80 "$OUT" >&2 || true
    exit 1
  fi
}

require 'data-cissp-core="ready"' 'core-ready marker'
require 'data-cissp-bank="ready"' 'released-bank marker'
require 'data-cissp-ready="true"' 'full-ready marker'
require 'Study what matters.' 'product-polish copy'
require '>Mastery<' 'readiness polish'
require 'Run baseline diagnostic' 'first-run diagnostic CTA'
require 'workflow-clarity.css?v=1' 'workflow clarity stylesheet'
require '79' 'released standard-question count'
forbid 'id="startupIssue"' 'startup error banner'

printf 'PASS browser_smoke core=ready bank=ready ui=ready\n'
