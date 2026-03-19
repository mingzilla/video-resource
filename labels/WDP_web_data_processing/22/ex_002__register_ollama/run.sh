#!/bin/bash
set -e
RUNTIME_ENV="${RUNTIME_ENV:-DEV}"
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${CURRENT_DIR}/../.." && pwd)"
CONFIG_ROOT="${CONFIG_ROOT:-${CURRENT_DIR}}"
CONFIG_FILE="${CONFIG_FILE:-run.json}"

export RUNTIME_ENV
export CONFIG_ROOT
export CONFIG_FILE

cd "${PROJECT_ROOT}"
uv run python src/ex_002__register_ollama/main.py
