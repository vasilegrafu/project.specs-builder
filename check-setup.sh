#!/bin/sh
# Checks this computer for specs-builder. It changes nothing.
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo
  echo "  MISSING  Python"
  echo "           Install it: see step 2 of GETTING-STARTED.md"
  echo
  exit 1
fi
exec python3 check_setup.py
