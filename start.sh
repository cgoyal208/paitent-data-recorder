#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-5000}"

if command -v lsof >/dev/null 2>&1; then
  ports=$(lsof -ti ":$PORT" || true)
  if [[ -n "$ports" ]]; then
    echo "Port $PORT is already in use. Stopping stale server process..."
    kill $ports || true
  fi
elif command -v fuser >/dev/null 2>&1; then
  if fuser "$PORT/tcp" >/dev/null 2>&1; then
    echo "Port $PORT is already in use. Stopping stale server process..."
    fuser -k "$PORT/tcp" || true
  fi
else
  echo "No port-check utility found; continuing with startup."
fi

export PORT
exec python app.py
