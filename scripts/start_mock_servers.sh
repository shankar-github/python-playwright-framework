#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python tests/mocks/mock_api_server.py &
API_PID=$!
python tests/mocks/mock_web_server.py &
WEB_PID=$!

cleanup() {
  kill "$API_PID" "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT

python scripts/wait_for_mocks.py
echo "Mock servers ready. Press Ctrl+C to stop."
wait
