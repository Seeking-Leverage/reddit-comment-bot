#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

source .venv/bin/activate

echo "Starting API on http://127.0.0.1:8000"
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload &
API_PID=$!

echo "Starting web console on http://localhost:5173"
cd web
npm run dev &
WEB_PID=$!

trap 'kill $API_PID $WEB_PID 2>/dev/null' EXIT

echo ""
echo "Open http://localhost:5173"
wait