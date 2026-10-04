#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export SNOW_RESEARCH_STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv sync --frozen
uv run --frozen python -u pipeline.py prepare
uv run --frozen python -c 'from pipeline import catalog; catalog()'
uv run --frozen python -u audit_radiometry.py
uv run --frozen python -u pipeline.py imagery
uv run --frozen python -u analyze.py
uv run --frozen python -m unittest discover -p 'test_*.py' 2>&1 | tee results/tests.log
uv run --frozen python record_run.py
