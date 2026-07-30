#!/usr/bin/env bash
set -euo pipefail

ROOT="${ASTRONEX_CHECKOUT:-/home/ubuntu/astronex-github-vnc-test}"
API_DIR="${ASTRONEX_API_DIR:-/home/ubuntu/astronex-mobile-api}"

export ASTRONEX_CHECKOUT="$ROOT"
export ASTRONEX_API_HOME="$API_DIR/runtime"
export ASTRONEX_API_KEY="${ASTRONEX_API_KEY:?Defina una clave antes de iniciar la API}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8088}"

exec "$API_DIR/.venv/bin/python" "$API_DIR/app.py"
