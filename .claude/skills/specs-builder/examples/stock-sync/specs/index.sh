#!/bin/sh
# Opens this specification: starts its application and the browser on it. Ctrl+C stops it.
cd "$(dirname "$0")" && exec python3 app/serve.py --open "$@"
