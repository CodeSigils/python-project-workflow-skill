#!/usr/bin/env bash
set -euo pipefail

python3 -m pytest tests -q
python3 -m compileall -q scripts tests
